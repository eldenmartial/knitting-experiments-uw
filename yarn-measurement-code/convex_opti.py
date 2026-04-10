import numpy as np
from gekko import GEKKO

import atexit

def exitHandler(gk):
    gk.cleanup()
    print("gekko temp file cleanup complete.")


GAUGE = 15

# https://www.shimaseiki.com/ire/company/vocabulary.html
# 15 gauge means 15 needles per/inch aka 15/2.54 cm # 25.4 mm

def grams2cm(weight_grams, grams_per_cm=0.0007283464567):
    return weight_grams/grams_per_cm 


def solve(A_train, b_train, labels, bounds=[0, 1], rtol=1e-4, otol=1e-8, machine_cons=True, geometric_cons=True, grams_per_cm=0.0007283464567, fixed_vals={}):
    d1_idx = labels.index('d1') if 'd1' in labels else None
    if not np.sum(A_train[:,d1_idx]): d1_idx = None

    g_idx = labels.index('gap') if 'gap' in labels else None
    if not np.sum(A_train[:,g_idx]): g_idx = None

    d2_idx = labels.index('d2') if 'd2' in labels else None
    if not np.sum(A_train[:,d2_idx]): d2_idx = None

    xl_idx = labels.index('xladder') if 'xladder' in labels else None
    if not np.sum(A_train[:,xl_idx]): xl_idx = None

    l_idx = labels.index('ladder') if 'ladder' in labels else None
    if not np.sum(A_train[:,l_idx]): l_idx = None

    m_idx = labels.index('miss') if 'miss' in labels else None
    if not np.sum(A_train[:,m_idx]): m_idx = None

    t_idx = labels.index('tuck') if 'tuck' in labels else None
    if not np.sum(A_train[:,t_idx]): t_idx = None

    k_idx = labels.index('knit') if 'knit' in labels else None
    bk_idx = labels.index('backknit') if 'backknit' in labels else None

    e_k_idx = labels.index('edge-knit') if 'edge-knit' in labels else None
    e_bk_idx = labels.index('edge-backknit') if 'edge-backknit' in labels else None

    gk = GEKKO(remote=False)

    atexit.register(exitHandler, gk)

    gk.options.IMODE = 2

    gk.options.RTOL = rtol # equation residual tolerance
    gk.options.OTOL = otol # objective tolerance
    # m.cleanup()

    gk.options.SOLVER = 1

    m, n = A_train.shape

    b = np.copy(b_train)

    x = gk.Array(gk.Var, n)

    A = np.copy(A_train)

    for i in range(n):
        if i == l_idx: x[i].lower = -3e-4
        elif i == k_idx or i == t_idx or i == e_k_idx: x[i].lower = 1e-4
        else: x[i].lower = bounds[0]
        x[i].upper = bounds[1]
    eqn = np.dot(A, x)

    cons_slk = []

    if machine_cons:
        if bk_idx is not None:
            slk_k_bk = gk.Var(name=f'slk_k_bk', lb=-rtol*5, ub=rtol*5)
            gk.Equation(abs(x[k_idx]-x[bk_idx]) + slk_k_bk == abs(x[e_k_idx]-x[e_bk_idx]))

        if m_idx is not None:

            if g_idx is not None:
                gauge_tol = 1e-1 # +/- 1 mm/0.1cm
                slk_gauge = gk.Var(name='slk_gauge', lb=-gauge_tol, ub=gauge_tol)
                cons_slk.append(slk_gauge)
                gk.Equation(GAUGE*(x[m_idx]/grams_per_cm) + (GAUGE-1)*(x[g_idx]/grams_per_cm) + slk_gauge == 2.54)
            else:
                gauge_tol = 1e-1
                slk_gauge = gk.Var(name='slk_gauge', lb=-gauge_tol, ub=gauge_tol)
                cons_slk.append(slk_gauge)
                gk.Equation((GAUGE)*(x[m_idx]/grams_per_cm) + slk_gauge == 2.54)

    if geometric_cons:  
        if d1_idx is not None and d2_idx is not None:
            if g_idx is not None:
                # law of cosines:
                slk_cos = gk.Var(name='slk_cos', lb=-rtol, ub=rtol)
                cons_slk.append(slk_cos)
                gk.Equation((2*x[g_idx]+x[m_idx])**2 + x[d1_idx]**2 - (2*(2*x[g_idx]+x[m_idx])*x[d1_idx]*gk.cos((135*np.pi)/180)) + slk_cos == x[d2_idx]**2)
            else:
                # law of cosines:
                slk_cos = gk.Var(name='slk_cos', lb=-rtol, ub=rtol)
                cons_slk.append(slk_cos)
                gk.Equation(x[m_idx]**2 + x[d1_idx]**2 - (2*x[m_idx]*x[d1_idx]*gk.cos((135*np.pi)/180)) + slk_cos == x[d2_idx]**2)

        obj_funcs = []
        for i in range(m):
            obj_funcs.append(gk.Intermediate((eqn[i]-b[i])**2))

        gk.Minimize(gk.sum(obj_funcs))
    else:
        obj_funcs = []
        for i in range(m):
            obj_funcs.append(gk.Intermediate((eqn[i]-b[i])**2))

        gk.Minimize(gk.sum(obj_funcs))

    # solve system:
    gk.solve(disp=False)

    # predicted values:
    x_p = np.array([x[i].value[0] for i in range(n)])

    return x_p
