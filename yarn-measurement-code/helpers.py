import numpy as np
import pandas as pd
import sympy as sp

import regex
import json
import os
import zipfile

from sklearn.linear_model import LinearRegression
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec


# ---
MAIN_ST = 63

STITCH_TABLE = {
    20: 20, # 20 with leading 25 (was 120)
    77: 25, # 25 with leading 25
    63: 30, # 30 with leading 25
    64: 40, # 40 with leading 25
    94: 35, # 35 with leading 25,

    110: 30, # 30 with leading 25
    105: 25, # 25 with leading 20
    113: 33, # 33 with leading 26
    114: 34, # 34 with leading 21 
    115: 35, # 35 with leading 24
    120: 40
}


def reportErrors(preds, actual, errs, mean_err, train_instances):
    high_errs = np.where(errs > mean_err)
    print(f'\nAbove-average errors: ({len(high_errs[0])}/{len(errs)})')
    print('----------------------------')
    print(pd.DataFrame({'predicted': np.array(preds)[high_errs], 'actual': actual[high_errs],'train % error': errs[high_errs]*100}, index=train_instances[high_errs]).sort_values(by='train % error', ascending=False).round(3).to_markdown())


def combineLinearlyDependent(data, masses, instances):
    li_data = np.copy(data)
    li_masses = np.copy(masses)
    li_instances = np.copy(instances)

    # combine linearly dependent data
    unq, count = np.unique(data, axis=0, return_counts=True)
    repeated_groups = unq[count > 1]

    for repeated_group in repeated_groups:
        repeated_idx = np.argwhere(np.all(li_data == repeated_group, axis=1)).ravel()
        li_data = np.delete(li_data, repeated_idx[1:], axis=0)
        avg_mass = np.mean(li_masses[repeated_idx])
        li_masses[repeated_idx[0]] = avg_mass
        li_masses = np.delete(li_masses, repeated_idx[1:])
        if len(li_instances): li_instances = np.delete(li_instances, repeated_idx[1:])
    
    return li_data, li_masses, li_instances


def getStitchData(data, masses, instances, lindensities, lindensity_idx=None, main_stitch_size=30):
    stitchNumber_data = None
    stitchNumber_idxs = np.where(['stitchNumber' in el for el in instances])[0]

    del_st_idxs = np.empty(0, dtype=int)

    if len(stitchNumber_idxs):
        stitchNumber_data = {}
        extensions = [json.loads(el[el.index('{'):el.index('}')+1]) for el in instances[stitchNumber_idxs]]

        stitchNumbers = [STITCH_TABLE[ext["stitchNumber"]] for ext in extensions]
        stitchNumber_labels = np.unique(stitchNumbers)
        for st in stitchNumber_labels:
            st_idxs = stitchNumber_idxs[np.where(stitchNumbers == st)]

            st_data, st_masses, st_instances = data[st_idxs], masses[st_idxs], instances[st_idxs]

            # combine linearly dependent data
            st_data, st_masses, st_instances = combineLinearlyDependent(st_data, st_masses, st_instances)
            
            if lindensity_idx is not None:
                lindensities['stitchNumber'][st] = st_data[:,lindensity_idx]
                st_data = np.delete(st_data, lindensity_idx, axis=1)

            stitchNumber_data[st] = [st_data.astype(int), st_masses, st_instances]
            if st == main_stitch_size: del_st_idxs = np.append(del_st_idxs, np.where(stitchNumbers == st)[0])

        stitchNumber_idxs = np.delete(stitchNumber_idxs, del_st_idxs) #we want to keep this in the main/training data
        return stitchNumber_data, lindensities, stitchNumber_idxs
    else: return None, lindensities, stitchNumber_idxs


def processData(dfs, masses, labels, instances=[], valid_instances=[], main_stitch_size=30):
    valid_test_funcs = [x for x in valid_instances if callable(x)]

    instances = np.array(instances)

    valid_idxs = np.empty((0,), dtype=np.int64)

    sorted_labels = sorted(labels)

    data = np.empty((0,len(sorted_labels)), dtype=np.int64)

    lindensities = {'train': [], 'valid': [], 'stitchNumber': {}}

    if 'lindensity' in sorted_labels: lindensity_idx = sorted_labels.index('lindensity')
    else: lindensity_idx = None

    for df in dfs:
        df_copy = df.copy()
        df_copy = df_copy.reindex(columns=sorted_labels, fill_value=0)
        data = np.append(data, df_copy.values, axis=0)

    stitchNumber_data, lindensities, stitchNumber_idxs = getStitchData(data, masses, instances, lindensities, lindensity_idx, main_stitch_size)

    swatch_labels = np.unique([el[:el.index('{')].strip() for el in instances[stitchNumber_idxs]])

    data = np.delete(data, stitchNumber_idxs, axis=0)
    masses = np.delete(masses, stitchNumber_idxs)
    instances = np.delete(instances, stitchNumber_idxs)
    
    # combine linearly dependent data
    data, masses, instances = combineLinearlyDependent(data, masses, instances)

    if len(instances): valid_idxs = np.where([el in valid_instances or any(f(el) for f in valid_test_funcs) for el in instances])[0]

    A_train, b_train = np.delete(data, valid_idxs, axis=0), np.delete(masses, valid_idxs)

    A_valid, b_valid = data[valid_idxs], masses[valid_idxs]
    train_instances, valid_instances = np.delete(np.array(instances), valid_idxs), np.array(instances)[valid_idxs]

    if lindensity_idx is not None:
        sorted_labels.remove('lindensity')

        lindensities['train'] = A_train[:,lindensity_idx]
        lindensities['valid'] = A_valid[:,lindensity_idx]
        A_train = np.delete(A_train, lindensity_idx, axis=1)
        A_valid = np.delete(A_valid, lindensity_idx, axis=1)

    if stitchNumber_data is not None:
        main_st_idxs = np.nonzero(np.in1d(instances, np.unique(swatch_labels)))[0]

        if len(main_st_idxs):
            main_st_data = np.copy(data)[main_st_idxs]
            if lindensity_idx is not None:
                if main_stitch_size in lindensities['stitchNumber']: lindensities['stitchNumber'][main_stitch_size] = np.append(lindensities['stitchNumber'][main_stitch_size], main_st_data[:,lindensity_idx])
                else: lindensities['stitchNumber'][main_stitch_size] = main_st_data[:,lindensity_idx]
                main_st_data = np.delete(main_st_data, lindensity_idx, axis=1)

            if main_stitch_size in stitchNumber_data:
                stitchNumber_data[main_stitch_size][0] = np.vstack([stitchNumber_data[main_stitch_size][0], main_st_data.astype(int)])
                stitchNumber_data[main_stitch_size][1] = np.append(stitchNumber_data[main_stitch_size][1], masses[main_st_idxs])
                stitchNumber_data[main_stitch_size][2] = np.append(stitchNumber_data[main_stitch_size][2], instances[main_st_idxs])
            else:
                stitchNumber_data[main_stitch_size] = [main_st_data.astype(int), masses[main_st_idxs], instances[main_st_idxs]]

    return sorted_labels, A_train.astype(int), b_train, train_instances, A_valid.astype(int), b_valid, valid_instances, stitchNumber_data, lindensities


def getData(data_paths=['data-auto/'], exclude_instances=[], train_instances=[], valid_instances=[], labels_to_drop=[], labels_to_combine=[], carriers=[], main_stitch_size=30, verbose=False):
    if not hasattr(data_paths, '__iter__') or isinstance(data_paths, str): data_paths = [data_paths]
    valid_test_funcs = [el for el in valid_instances if callable(el)]
    valid_instances = [el for el in valid_instances if el not in valid_test_funcs]
    valid_paths = [el for el in valid_instances if os.path.isdir(el)]
    
    exclude_test_funcs = [x for x in exclude_instances if callable(x)]

    files = []
    for p in data_paths:
        name, ext = os.path.splitext(p)
        if ext == '.zip':
            os.rmdir(name)
            with zipfile.ZipFile(p, 'r') as zip_ref:
                zip_ref.extractall(name)

        
        files.extend([[name, f] for f in os.listdir(name) if os.path.isfile(os.path.join(name, f))])

    # ------
    train_dfs = []
    masses = [] #masses (average of all iterations for a given sample)

    scale_noise = []
    instances = []

    train_dfs_labels = []

    if len(files):
        for (p, fn) in files:
            try:
                df = pd.read_csv(os.path.join(p, fn), sep=',', header=0)
            except Exception:
                if verbose: print(f'invalid or empty file: {fn} (skipping)')
                continue
            
            df.dropna(axis=1, inplace=True) #drop columns with nan or None values

            if len(labels_to_drop): df.drop(labels_to_drop, axis=1, inplace=True, errors='ignore')

            if len(labels_to_combine):
                for comb in labels_to_combine:
                    feat_sum = df[[l for l in comb if l in df.columns]].sum(axis=1) #.values
                    df.drop(comb, axis=1, inplace=True, errors='ignore')
                    df['+'.join(comb)] = feat_sum

            comment = ''
            if 'comment' in df.columns:
                if df['comment'].values[0] in exclude_instances or any(f(df['comment'].values[0]) for f in exclude_test_funcs):
                    if verbose: print(f"skipping file {fn} (excluded instance)") #debug
                    continue
                comment = df['comment'].values[0]
                df.drop('comment', axis=1, inplace=True)
            
            if p in valid_paths and comment not in valid_instances: valid_instances.append(comment)

            if len(carriers): df = df[df['carrier'].isin(carriers)]
            sum_df = df.drop('carrier', axis=1).sum().to_frame().transpose()

            sum_df = sum_df.loc[:, (sum_df != 0).any(axis=0)] # drop columns without any counts

            mass_headers_df = [h for h in list(df.columns) if 'mass' in h]

            if not len(mass_headers_df):
                if verbose: print(f"skipping file {fn} since no mass") #debug
                continue #don't store data without mass values

            mass_headers = [h for h in list(sum_df.columns) if 'mass' in h]
            mass_vals = sum_df[mass_headers].values
            avg_mass = np.mean(mass_vals)
            
            std_mass = np.std(mass_vals)
            scale_noise.append(std_mass/avg_mass) # for percent deviation

            masses.append(avg_mass)

            instances.append(comment)

            sum_df = sum_df.drop(mass_headers, axis=1)

            train_dfs.append(sum_df)
            train_dfs_labels += list(sum_df.columns)

        train_dfs_labels = list(set(train_dfs_labels))
        masses = np.array(masses)

    if len(valid_test_funcs):
        for func in valid_test_funcs:
            valid_instances.extend([el for el in instances if func(el)])

    train_test_funcs = [x for x in train_instances if callable(x)]
    if len(train_test_funcs):
        train_instances = [x for x in train_instances if x not in train_test_funcs]
        for func in train_test_funcs:
            train_instances.extend([x for x in instances if func(x)])

    if len(train_instances): valid_instances = np.delete(instances, np.where(np.in1d(instances, train_instances))[0])

    labels, A_train, b_train, train_instances, A_valid, b_valid, valid_instances, stitchNumber_data, lindensities = processData(train_dfs, masses, train_dfs_labels, instances, valid_instances, main_stitch_size)

    return labels, A_train, b_train, train_instances, A_valid, b_valid, valid_instances, stitchNumber_data, lindensities


def curveFitter(ydata=np.array([0.000242, 0.000267, 0.000386, 0.000486, 0.000552]), stitch_sizes=[20, 25, 30, 35, 40], main_stitch_size=30, op='knit', fit_funcs=['linear', 'poly'], exclude_outliers=True, return_all=False, show=False, save_as=None):
    assert np.all(np.diff(stitch_sizes) > 0), "Stitch sizes should be in ascending order."

    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": [],                   # use latex default serif font
        "font.sans-serif": ["DejaVu Sans"], # use a specific sans-serif font
    })

    fig = plt.figure()
    ax = fig.add_subplot(111)

    xdata = (stitch_sizes-main_stitch_size)/5
    main_idx = np.where(stitch_sizes == main_stitch_size)[0][0]
    y0 = ydata[main_idx]

    if exclude_outliers:
        while not np.all(np.diff(ydata) >= 0):
            valid_idxs = np.hstack([np.where(np.diff(ydata[:main_idx+1]) >= 0)[0], [main_idx], np.where(np.diff(ydata[main_idx:]) >= 0)[0]+main_idx+1])

            xdata = xdata[valid_idxs]
            ydata = ydata[valid_idxs]
            stitch_sizes = np.array(stitch_sizes)[valid_idxs]
    else:
        valid_idxs = np.where(ydata != 0)

        xdata = xdata[valid_idxs]
        ydata = ydata[valid_idxs]
        stitch_sizes = np.array(stitch_sizes)[valid_idxs]

    x_cont = np.linspace(xdata[0], xdata[-1], 1000)

    def getR2(f, popt):
        residuals = ydata - f(xdata, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((ydata-np.mean(ydata))**2)
        r_squared = 1 - (ss_res / ss_tot)
        return r_squared

    def atan_f(x, k, w, x0):
        return k * np.arctan(w*(x-x0)) + y0
    
    def poly_f(x, a, b, c):
        return y0*(a*x**2 + b*x + c)
    
    def lin_f(x, a, b):
        return y0*(a*x + b)
    
    x_, s_ = sp.symbols(f'x s')

    eqns = []
    func_vals = []
    r2_vals = []
    y_fits = []

    if 'atan' in fit_funcs:
        try:
            atan_popt, tan_pcov = curve_fit(atan_f, xdata, ydata)
            atan_r2 = getR2(atan_f, atan_popt)

            def atan_func(y0, x):
                return atan_popt[0] * np.arctan(atan_popt[1]*(x-atan_popt[2])) + y0

            atan_eqn = '$' + sp.latex(sp.Float(atan_popt[0],3) * sp.atan(sp.Float(atan_popt[1],3) * (x_ - sp.Float(atan_popt[2],3))) + sp.Float(y0,3), full_prec=False, min=-3, max=3) + '$'

            atan_y = atan_f(x_cont, *atan_popt)
            ax.plot(x_cont, atan_y, label=f'atan:   {atan_eqn}\n            $R^2 = {round(atan_r2, 3)}$', color='green')

            func_vals.append(atan_func)
            r2_vals.append(atan_r2)
            y_fits.append(atan_y)
            eqns.append(atan_eqn)
        except Exception:
            atan_popt = np.zeros(3)
            atan_r2 = 0    
    
    if 'poly' in fit_funcs:
        try:
            poly_popt, poly_pcov = curve_fit(poly_f, xdata, ydata)
            poly_r2 = getR2(poly_f, poly_popt)

            def poly_func(y0, x):
                return y0*(poly_popt[0]*x**2 + poly_popt[1]*x + poly_popt[2])

            poly_eqn = '$' + sp.latex(sp.Mul(x_, sp.Float(poly_popt[0],3)*s_**2 + sp.Float(poly_popt[1],3)*s_ + sp.Float(poly_popt[2],3), evaluate=False), full_prec=False, min=-3, max=3) + '$'

            poly_y = poly_f(x_cont, *poly_popt)

            ax.plot(x_cont, poly_y, label=f'poly:   {poly_eqn}\n            $R^2 = {round(poly_r2, 3)}$', color='darkorange')

            func_vals.append(poly_func)
            r2_vals.append(poly_r2)
            y_fits.append(poly_y)
            eqns.append(poly_eqn)
        except Exception:
            poly_popt = np.zeros(2)
            poly_r2 = 0

    if 'linear' in fit_funcs:
        try:
            lin_popt, lin_pcov = curve_fit(lin_f, xdata, ydata)
            lin_r2 = getR2(lin_f, lin_popt)

            def lin_func(y0, x):
                return y0*(lin_popt[0]*x + lin_popt[1])
            
            lin_eqn = '$' + sp.latex(sp.Mul(x_, sp.Add(sp.Float(lin_popt[0],3)*s_, sp.Float(lin_popt[1],3), evaluate=False), evaluate=False), full_prec=False, min=-3, max=3, order='none') + '$'

            lin_y = lin_f(x_cont, *lin_popt)
            ax.plot(x_cont, lin_y, label=f'linear: {lin_eqn}\n            $R^2 = {round(lin_r2, 3)}$', color='blue')

            func_vals.append(lin_func)
            r2_vals.append(lin_r2)
            y_fits.append(lin_y)
            eqns.append(lin_eqn)
        except Exception:
            lin_popt = np.zeros(1)
            lin_r2 = 0

    ax2 = ax.twiny()
    ax.plot(xdata, ydata, 'o', label='data', color='red')
    plt.xticks(xdata)

    ax.set_xticks(xdata)
    ax2.set_xticks(xdata)
    ax2.set_xbound(ax.get_xbound())
    ax.set_xticklabels(stitch_sizes)

    ax.legend(title=f'$x$ := feature weight for stitch size {main_stitch_size}, $s$ := step from stitch size {main_stitch_size}')

    plt.title(r'\textbf{'+f'Curve fits for {op} data'+'}', fontweight="bold")
    
    ax.set_ylabel('mass (g)')
    
    ax.set_xlabel('stitch size')
    ax2.set_xlabel('steps from main stitch size')
    
    fig = plt.gcf()
    fig.set_dpi(300)

    plt.tight_layout()

    if show: plt.show()

    if save_as is not None:
        fig.savefig(save_as, bbox_inches="tight", backend='pgf')

    if return_all: return func_vals, r2_vals, y_fits, eqns
    else:
        best_idx = np.argmax(np.array([r2_vals]))
        return np.vectorize(func_vals[best_idx]), r2_vals[best_idx], y_fits[best_idx], eqns[best_idx]
    

def plotFits(ydata, stitch_sizes, main_stitch_size=30, exclude_outliers=False, r2_vals={}, y_fits={}, eqns={}, title="Curve Fits for Stitch-Size-Dependent Feature Data", save_as="figures/plots/feature_curve_fits.pdf"):
    assert np.all(np.diff(stitch_sizes) > 0), "Stitch sizes should be in ascending order."

    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": [],                   # use latex default serif font
        "font.sans-serif": ["DejaVu Sans"], # use a specific sans-serif font
    })

    fig = plt.figure(figsize=(16, 10), dpi=300)

    labels = np.array(list(ydata.keys()))
    diff_vals = np.diff(np.mean(np.array((list(ydata.values()))), axis=1))
    
    break_pts = np.append(-1, np.where(diff_vals > np.mean(diff_vals))[0])
    n_ax = len(break_pts) 

    ax_locs = {}

    for i, label in enumerate(labels):
        ax_locs[label] = n_ax-np.where(break_pts < i)[0][-1]-1
    
    gs = GridSpec(n_ax, 1, figure=fig, height_ratios=[1]*(n_ax-1)+[2])
    axes = []
    for n in range(n_ax):
        if n > 0: axes.append(fig.add_subplot(gs[n]))
        else: axes.append(fig.add_subplot(gs[n]))

    d = .01  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=axes[0].transAxes, color='k', clip_on=False)
    if len(axes) > 1:
        for i, ax in enumerate(axes):
            if i > 0:
                kwargs.update(transform=ax.transAxes)
                ax.spines['top'].set_visible(False)

                ax.plot((-d, +d), (1-d, 1+d), **kwargs) # bottom-left diagonal
                ax.plot((1-d, 1+d), (1-d, 1+d), **kwargs) # bottom-right diagonal
                
            if i < n_ax-1:
                if i == 0: # for second axis on top
                    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
                    ax.xaxis.set_label_position('top')
                else:
                    ax.get_xaxis().set_visible(False)

                ax.spines['bottom'].set_visible(False)

                ax.plot((-d, +d), (-d, +d), **kwargs) # top-left diagonal
                ax.plot((1 - d, 1+d), (-d, +d), **kwargs) # top-right diagonal

    # ---
    xdata = (stitch_sizes-main_stitch_size)/5
    main_idx = np.where(stitch_sizes == main_stitch_size)[0][0]

    x_cont = np.linspace(xdata[0], xdata[-1], 1000)

    colors = ["#ff54b2","#0edca7","#8900ff","#ffa948","#3772FF","#76ff00","#ff3833","#effe60","#00ff89"]
    for i,(label, y) in enumerate(ydata.items()):
        if type(exclude_outliers) == list: exclude_outliers_ = label in exclude_outliers
        else: exclude_outliers_ = exclude_outliers

        if exclude_outliers_:
            while not np.all(np.diff(y) >= 0):
                valid_idxs = np.hstack([np.where(np.diff(y[:main_idx+1]) >= 0)[0], [main_idx], np.where(np.diff(y[main_idx:]) >= 0)[0]+main_idx+1])

                x = xdata[valid_idxs]
                y = y[valid_idxs]
        else:
            valid_idxs = np.where(y != 0)

            x = xdata[valid_idxs]
            y = y[valid_idxs]

        axes[ax_locs[label]].plot(x, y, 'o', label='data', color=colors[i])

        axes[ax_locs[label]].plot(x_cont, y_fits[label], label=r'\textbf{'+label+':} '+f'$f(x,s)=$ {eqns[label]}\n            $R^2 = {round(r2_vals[label], 3)}$', color=colors[i])
    
    plt.yticks(fontsize=12)
    plt.xticks(xdata)
    if len(axes) == 1:
        ax2 = axes[0].twiny()
        axes[0].set_xticks(xdata)
        ax2.set_xticks(xdata)
        axes[0].set_xticklabels(stitch_sizes)

        axes[0].set_xlabel('stitch size', size=12)
        ax2.set_xlabel('steps from main stitch size', size=12)
    else:
        for i,ax in enumerate(axes):
            ax.set_xticks(xdata)
            ax.tick_params(axis='y', labelsize=12)
            if i == 0:
                axes[i].set_xticklabels(xdata, fontsize=12)
            else:
                axes[i].set_xticklabels(stitch_sizes, fontsize=12)
        
        axes[-1].set_xlabel('stitch size', size=12)
        axes[0].set_xlabel('steps from main stitch size', size=12)

    from matplotlib.legend_handler import HandlerTuple

    handles, labels = [], []
    handles_, labels_ = [], []
    for ax in axes:
        ax_handles, ax_labels = ax.get_legend_handles_labels()
        handles.extend(ax_handles)
        labels.extend(ax_labels)

    for (h, l) in zip(handles, labels):
        if l in labels_:
            i = labels.index(l)
            handles_.append(None)
            if type(handles_[i]) == list: handles_[i].append(h)
            else: handles_[i] = [handles_[i], h]
        else:
            labels_.append(l)
            handles_.append(h)
    
    handles_ = [h for h in handles_ if h is not None]
    handles_ = [tuple(h) if type(h) == list else h for h in handles_]

    # # Shrink current axis by 20%
    for ax in axes:
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width*0.8, box.height])

    lgd = plt.legend(handles=handles_, labels=labels_, loc='center left', bbox_to_anchor=(1, 0.5), title=f'$x$ := feature weight for stitch size {main_stitch_size}, $s$ := step from stitch size {main_stitch_size}', prop={'size': 12}, handler_map={tuple: HandlerTuple(ndivide=None)})
    
    lgd.get_title().set_fontsize('12') #legend 'Title' fontsize

    axes[0].set_title(r"\textbf{" + title + "}", fontweight="bold")
    axes[-1].set_ylabel('mass (g)', size=12)

    plt.tight_layout()
    fig.tight_layout()

    plt.show()

    if save_as is not None: fig.savefig(save_as, bbox_inches="tight", backend="pgf")


def sigFigs(v, precision=3):
    return float(np.format_float_positional(v, precision=precision, unique=False, fractional=False, trim='k'))


def plotResults(instances, b_true, b_pred, title=None, save_as=None):
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": [],                   # use latex default serif font
        "font.sans-serif": ["DejaVu Sans"], # use a specific sans-serif font
    })

    n_samples = len(instances)

    steps = np.arange(n_samples)
    
    sorted_true = np.sort(b_true)
    sorted_pred = np.sort(b_pred)

    diff_vals = np.diff(sorted_true)
    tol = (sorted_true[-1]-sorted_true[0])/10
    break_pts = np.where(diff_vals > tol)[0][::-1]
    n_ax = len(break_pts)

    fig, axes = plt.subplots(n_ax+1, 1, sharex=True)

    if title is not None: axes[0].set_title(r'\textbf{'+title+'}', fontweight='bold')

    axes[0].spines['bottom'].set_visible(False)
    axes[0].xaxis.tick_top()

    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=axes[0].transAxes, color='k', clip_on=False)
    axes[0].plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
    axes[0].plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal
    s = 60
    for i in range(n_ax+1):
        axes[i].scatter(s=s, x=steps, y=b_true, color="blue", alpha=0.4, label=("Expected" if i == 0 else None), clip_on=False)
        axes[i].scatter(s=s, x=steps, y=b_pred, color="red", alpha=0.4, label=("Predicted" if i == 0 else None), clip_on=False)

        if i > 0:
            kwargs.update(transform=axes[i].transAxes)  # switch to this axes
            axes[i].plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
            axes[i].plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal
            axes[i].spines['top'].set_visible(False)

            if i == n_ax:
                ylim_bot = 0
                ylim_top = max(sorted_true[break_pts[-1]-1], sorted_pred[break_pts[-1]-1])
            else:
                axes[i].spines['bottom'].set_visible(False)
                axes[i].plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
                axes[i].plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

                ylim_bot = min(sorted_true[break_pts[i]+1], sorted_pred[break_pts[i]+1])
                ylim_top = max(sorted_true[break_pts[i-1]], sorted_pred[break_pts[i-1]])
        else:
            ylim_bot = min(sorted_true[break_pts[i]+1], sorted_pred[break_pts[i]+1])
            ylim_top = max(sorted_true[-1], sorted_pred[-1])

        axes[i].set_ylim(sigFigs(ylim_bot), sigFigs(ylim_top))

    axes[-1].tick_params(labeltop=False)  # don't put tick labels at the top

    axes[-1].xaxis.tick_bottom()

    fig.legend(loc=(0.9, 0.9))
    plt.xlabel("sample number")
    fig.text(0.06, 0.5, "weight (g)", ha='center', va='center', rotation='vertical') # y label

    fig.set_size_inches(18.5, 10.5, forward=True)
    fig.set_dpi(300)

    plt.show()

    if save_as is not None: fig.savefig(save_as, bbox_inches="tight", backend='pgf')  


def plotErrors(instances, b_true, b_pred, title=None, save_as=None, graph='bar'):
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": [],                   # use latex default serif font
        "font.sans-serif": ["DejaVu Sans"], # use a specific sans-serif font
    })

    plt.rc('xtick', labelsize=12)

    def fmtInstance(instance):
        new_val = regex.sub(r"tuckStitch |tuck ", "tuck-stitch ", regex.sub(r' {"stitchNumber": \d+}', "", instance))

        seq_match = regex.search(r"_f[fb]+", new_val)
        if seq_match is not None:
            seq = new_val[seq_match.start():seq_match.end()]
            fmt_seq = f"{seq.count('f')}x{seq.count('b')} "
            new_val = fmt_seq + new_val[:seq_match.start()] + new_val[seq_match.end():]

        return new_val
    
    vfunc = np.vectorize(fmtInstance)
    fmt_instances = vfunc(instances)

    figsize = (max(10, len(instances)//2), 10)

    fig, ax = plt.subplots(figsize=figsize, dpi=300)

    plt.rcParams['axes.formatter.min_exponent'] = 2

    from matplotlib import ticker
    
    ax.yaxis.set_major_formatter(ticker.LogFormatterSciNotation(base=10, minor_thresholds=(np.inf,np.inf)))

    if title is not None: ax.set_title(r'\textbf{'+title+'}', fontweight='bold')

    perc_errs = (np.abs(b_pred-b_true)/b_true)*100

    sort_idxs = np.argsort(perc_errs)

    ax.bar(fmt_instances[sort_idxs], perc_errs[sort_idxs], color='#461b97')
    plt.xlim([-1,instances.size])

    plt.xticks(rotation='vertical')
    # Pad margins so that markers don't get clipped by the axes
    plt.margins(0.2)
    # Tweak spacing to prevent clipping of tick-labels
    plt.subplots_adjust(bottom=0.15)

    plt.xlabel("swatch")
    plt.ylabel("\% MAE")
    
    plt.tight_layout()

    plt.show()

    if save_as is not None: fig.savefig(save_as, bbox_inches="tight", backend='pgf')
    

def sampleInfo(instances, stitchNumber_data=None):
    print(f'total number of swatches: {len(instances)}')

    min_area, max_area = np.inf, -np.inf
    min_area_sample, max_area_sample = None, None
    for instance in instances:
        dims = instance[instance.index('(')+1:instance.index(')')].split('x')
        area = int(dims[0])*int(dims[1])

        if area < min_area:
            min_area = area
            min_area_sample = instance
        
        if area > max_area:
            max_area = area
            max_area_sample = instance
    
    print('min:', min_area, min_area_sample)
    print('max:', max_area, max_area_sample)

    if stitchNumber_data is not None:
        for st, st_data in stitchNumber_data.items():
            print(st, len(st_data[1]))


# grams/cm
def normalizeMass(mass, lindensity, norm_density=1):
	return (mass/lindensity)*norm_density


def linearlyIndependent(A):
    _, indep_idxs = sp.Matrix(A).T.rref()
    return np.array(indep_idxs)


def plotMetric(stats, metric='MAE', min_bs=8, max_bs=55, iters_per_bs=50, methods=[('Linear Regression', {'positive': False}), ('Nonnegative Linear Regression', {'positive': True}), ('Constrained Convex Optimization', {'machine_cons': True, 'geometric_cons': False, 'rtol': 1e-2, 'otol': 1e-8})], plot_std=False, save_as=None):
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "Helvetica"
    })

    if metric.upper() == 'MAE':
        vals = stats[0]
        valid_vals = np.sort(np.ravel(vals[::2]))
    else:
        vals = stats[1]
        valid_vals = np.sort(np.ravel(vals[::2]))

    diff_vals = np.diff(valid_vals) # just validation
    
    thresh = 5
    break_pts = np.where(diff_vals > thresh)[0]

    break_vals = valid_vals[break_pts][::-1]

    n_ax = len(break_pts)+1 #+1

    fig = plt.figure(figsize=(16, 10), dpi=300)

    gs = GridSpec(n_ax+1, 1, figure=fig, height_ratios=[1]*(n_ax-1)+[8,8+n_ax-1])
    axes = []
    for n in range(n_ax):
        if n > 0: axes.append(fig.add_subplot(gs[n], sharex=axes[0]))
        else: axes.append(fig.add_subplot(gs[n]))

    train_ax = fig.add_subplot(gs[-1])


    axes[0].set_title('Validation Set', size=12)
    axes[-1].set_ylabel(f'Avg \% {metric}', size=10)


    train_ax.set_title('Train Set', size=12)
    train_ax.set_xlabel('$n$ samples', size=10)
    train_ax.set_ylabel(f'Avg \% {metric}', size=10)

    train_ax.tick_params(axis='y', labelsize=5)
    train_ax.tick_params(axis='x', labelsize=10)
    for i,ax in enumerate(axes):
        ax.title.set_fontsize(12)
        ax.xaxis.label.set_size(10)
        ax.yaxis.label.set_size(10)
        ax.tick_params(axis='x', labelsize=10)
        if i == len(axes)-1: ax.tick_params(axis='y', labelsize=5)
        else: ax.tick_params(axis='y', labelsize=4)
    

    d = .002 # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=axes[0].transAxes, color='k', clip_on=False)
    if len(axes) > 1:
        for i, ax in enumerate(axes):
            if i > 0:
                kwargs.update(transform=ax.transAxes)
                ax.spines['top'].set_visible(False)

                ax.plot((-d, +d), (1-d, 1+d), **kwargs)  # bottom-left diagonal
                ax.plot((1-d, 1+d), (1-d, 1+d), **kwargs)  # bottom-right diagonal
                
            if i < n_ax-1:
                ax.get_xaxis().set_visible(False)

                ax.spines['bottom'].set_visible(False)

                ax.plot((-d, +d), (-d, +d), **kwargs)      # top-left diagonal
                ax.plot((1 - d, 1+d), (-d, +d), **kwargs)  # top-right diagonal

    x = np.array(range(min_bs, max_bs+1))

    for i, method_vals in enumerate(vals):
        if i % 2 == 0:
            if len(break_vals):
                for j, val in enumerate(break_vals):
                    if j == 0: idxs = np.where(method_vals > val)[0]
                    else: idxs = np.where((method_vals <= break_vals[j-1]) & (method_vals > val))[0]
                    if len(idxs):
                        axes[j].scatter(x[idxs], method_vals[idxs], s=10)
                        axes[j].margins(y=0.4)
                
                idxs = np.where(method_vals <= break_vals[-1])[0]
                if len(idxs):
                    axes[-1].scatter(x[idxs], method_vals[idxs], s=10)
            else: axes[0].scatter(x, method_vals, s=10)
        else:
            train_ax.scatter(x, method_vals, label=methods[i//2][0], s=10)
        
    fig.legend(loc=1, fancybox=True, numpoints=1, ncol=min(len(methods),2), prop={'size': 8})

    plt.tight_layout()

    if save_as is not None: fig.savefig(save_as, bbox_inches="tight", dpi=400)

    plt.show()
