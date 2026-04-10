import os
import json
import regex
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from sklearn.linear_model import LinearRegression

import helpers
import convex_opti


MAIN_ST = helpers.MAIN_ST

STITCH_TABLE = helpers.STITCH_TABLE

class YarnModel:
    def __init__(self, labels, A_train=np.empty(0), b_train=np.empty(0), train_instances=np.empty(0), A_valid=np.empty(0), b_valid=np.empty(0), valid_instances=np.empty(0), lindensities={'train': np.empty(0), 'valid': np.empty(0)}, norm_density=1):
        self.labels = labels

        self.A_train = A_train
        self.b_train = b_train
        self.train_instances = train_instances # comments naming the instances
        self.A_valid = A_valid
        self.b_valid = b_valid
        self.valid_instances = valid_instances

        self.train_lindensities = lindensities.get('train', np.empty(0))
        self.valid_lindensities = lindensities.get('valid', np.empty(0))

        self.norm_density = norm_density

        self.x = None
    
    def train(self, method, **kwargs):
        if method.lower() == 'gekko' or 'lp' in method.lower() or 'constrained' in method.lower():
            kwargs = {k:v for k,v in kwargs.items() if k in ['bounds', 'rtol', 'otol', 'machine_cons', 'geometric_cons', 'grams_per_cm', 'fixed_vals']}
            try:
                self.x = convex_opti.solve(self.A_train, self.b_train, self.labels)
            except Exception as e:
                if 'rtol' in kwargs: kwargs['rtol'] *= 1e1 # increase rtol
                else: kwargs['rtol'] = 1e-2

                self.x = convex_opti.solve(self.A_train, self.b_train, self.labels, **kwargs)
        else:
            kwargs = {k:v for k,v in kwargs.items() if k in ['fit_intercept', 'normalize', 'copy_X', 'n_jobs', 'positive']}
            kwargs = {k:v for k,v in kwargs.items() if k in ['fit_intercept', 'normalize', 'copy_X', 'n_jobs', 'positive']}

            if not len(kwargs): kwargs = {'fit_intercept': False}

            if 'positive' in method.lower() or 'nonnegative' in method.lower() or 'non-negative' in method.lower():
                method = 'Linear Regression'
                kwargs['positive'] = True

            kwargs['fit_intercept'] = False # always do this, since it works better consistently

            reg_model = LinearRegression(**kwargs)
            reg_model.fit(self.A_train, self.b_train)
            self.x = reg_model.coef_

        return self.x
    
    def results(self):
        if self.x is not None:
            print(f"\n--- Operation Predictions ---\n")
            res = {'feature': self.labels, 'mass (mg)': self.x*1000}
            print(pd.DataFrame(res).set_index(['feature']).round(3).to_markdown())

    def predict(self, A=None, b=None, instances=np.empty(0), lindensities=np.empty(0), x=None, return_stats=False, verbose=True):
        if x is None: x = np.copy(self.x)
        if A is None:
            if len(self.b_valid):
                b_pred = self.A_valid @ x
                instances = np.copy(self.valid_instances)
                lindensities = np.copy(self.valid_lindensities)
            else:
                b_pred = self.A_train @ x
                instances = np.copy(self.train_instances)
                lindensities = np.copy(self.train_lindensities)
            b = np.copy(self.b)
        else: b_pred = A @ x

        mae, std = None, None
        if b is not None and len(instances):
            b_true = np.copy(b)
            if len(lindensities): #normalize
                b_pred = (b_pred/self.norm_density)*lindensities
                b_true = (b_true/self.norm_density)*lindensities
            
            errs = np.abs(b_pred-b_true)/b_true

            mae = np.mean(errs)
            std = np.std(errs)
            if verbose:
                res = {'predicted': b_pred, 'true': b_true, '% error': errs*100}
                print(f"\nmean error: {mae*100:.3f}%, std: {std*100:.3f}%\n")
                print(pd.DataFrame(res, index=instances).sort_values(by='% error', ascending=False).round(3).to_markdown())

        if return_stats: return b_pred, mae, std
        else: return b_pred
    

    def mae(self, A=None, b=None, lindensities=np.empty(0), x=None):
        if x is None: x = np.copy(self.x)
        if A is None:
            if len(self.b_valid):
                b_pred = self.A_valid @ x
                lindensities = np.copy(self.valid_lindensities)
            else:
                b_pred = self.A_train @ x
                lindensities = np.copy(self.train_lindensities)
            b = np.copy(self.b)
        else: b_pred = A @ x

        b_true = np.copy(b)
        if len(lindensities):
            b_pred = (b_pred/self.norm_density)*lindensities
            b_true = (b_true/self.norm_density)*lindensities
        
        errs = np.abs(b_pred-b_true)/b_true

        mae = np.mean(errs)
        return mae
    
    def std(self, A=None, b=None, lindensities=np.empty(0), x=None):
        if x is None: x = np.copy(self.x)
        if A is None:
            if len(self.b_valid):
                b_pred = self.A_valid @ x
                lindensities = np.copy(self.valid_lindensities)
            else:
                b_pred = self.A_train @ x
                lindensities = np.copy(self.train_lindensities)
            b = np.copy(self.b)
        else: b_pred = A @ x

        b_true = np.copy(b)
        if len(lindensities):
            b_pred = (b_pred/self.norm_density)*lindensities
            b_true = (b_true/self.norm_density)*lindensities
        
        errs = np.abs(b_pred-b_true)/b_true

        return np.std(errs)

    def stitchNumber_predict(self, steps, vfunc=None, coeff=1.15, A=None, b=None, instances=np.empty(0), lindensities=np.empty(0), verbose=True):
        st_x = np.copy(self.x)
        idxs = np.where(np.isin(self.labels, ['knit', 'tuck', 'edge-knit', 'xknit']))

        if vfunc is None:
            if steps > 0: st_x[idxs] *= steps*coeff
            else: st_x[idxs] /= abs(steps)*coeff
        else:
            if type(vfunc) == dict:
                for (label,func) in vfunc.items():
                    if label == 'knit': idx = np.append(np.where(np.array(self.labels) == label)[0], np.where(np.isin(self.labels, [l for l in ['tuck', 'xknit'] if l not in vfunc.keys()]))[0])
                    else: idx = np.where(np.array(self.labels) == label)
                    st_x[idx] = func(st_x[idx], steps)
            else: st_x[idxs] = vfunc(st_x[idxs], steps)

        return st_x, self.predict(A=A, b=b, instances=instances, lindensities=lindensities, x=st_x, verbose=verbose)


def estimateNoise(data_paths=['data-auto'], masses_paths=['masses-auto'], exclude_instances=[lambda x: 'rayon' in x], exclude_lindensities=['rayon'], main_stitch_size=30, verbose=True):
    exclude_test_funcs = [x for x in exclude_instances if callable(x)]

    scale_noise = []
    
    for masses_path in masses_paths:
        for fn in os.listdir(masses_path):
            if 'lindensity' in fn: continue
            with open(os.path.join(masses_path, fn), 'r+') as f:
                content = [ln.split(',') for ln in f.read().splitlines()[1:]]
            
            df = pd.DataFrame(content, dtype=float, columns=range(max(len(row) for row in content)))
            masses_mean = df.mean(axis=1, skipna=True)
            masses_std = df.std(axis=1, skipna=True)
            perc_deviation = masses_std/masses_mean
            scale_noise.extend(perc_deviation.dropna().values) # for percent deviation (decimal form)
    
    est_scale_noise = np.mean(scale_noise)
    
    est_yarn_noise = None
    if os.path.exists(f'{masses_path}/lindensity.csv'): # grams/cm
        cone_densities = pd.read_csv(f'{masses_path}/lindensity.csv', sep=',', header=None, index_col=0).dropna()
        cone_densities.drop(exclude_lindensities, inplace=True)
        std = np.std(cone_densities.values)
        est_yarn_noise = std/np.mean(cone_densities.values) # use this is a metric of how much deviation we can expect just from variation in linear density of yarn
    
    est_machine_noise = None
    data = []
    masses = []
    instances = np.empty(0)

    for data_path in data_paths:
        for fn in os.listdir(data_path):
            instance = ""
            try:
                df = pd.read_csv(os.path.join(data_path, fn), sep=',', header=0)
            except Exception:
                print(f'invalid or empty file: {fn} (skipping)') #debug
                continue
            
            df.dropna(axis=1, inplace=True) #drop columns with nan or None values

            if 'comment' in df.columns:
                instance = df['comment'].values[0]
                if instance in exclude_instances or any(f(instance) for f in exclude_test_funcs):
                    if verbose: print(f"skipping file {fn} (excluded instance)") #debug
                    continue

            if 'stitchNumber' in instance: #TODO: add option to get noise for each stitch number
                extensions = json.loads(instance[instance.index('{'):instance.index('}')+1])
                st = STITCH_TABLE[extensions['stitchNumber']]
                if st != main_stitch_size:
                    if verbose: print(f"skipping file {fn} with stitchNumber {st}") #debug
                    continue
            
            df.drop(['comment', 'carrier', 'lindensity'], axis=1, inplace=True, errors='ignore') 

            mass_headers = [h for h in list(df.columns) if 'mass' in h]

            masses.append(df[mass_headers].values.ravel())
            instances = np.append(instances, instance)

            avg_mass = df[mass_headers].mean(axis=1, skipna=True)
            df.drop(mass_headers, axis=1, inplace=True)
            df['mass'] = avg_mass
            data.append(df)
    
    data_df = pd.concat(data).fillna(0)

    A_df = data_df.drop('mass', axis=1)

    A = A_df.values

    # combine linearly dependent data
    unq, count = np.unique(A, axis=0, return_counts=True)
    repeated_groups = unq[count > 1]

    delete_idxs = np.empty(0, dtype=int)

    li_masses = np.array(masses, dtype=object)

    for repeated_group in repeated_groups:
        repeated_idxs = np.argwhere(np.all(A == repeated_group, axis=1)).ravel()

        delete_idxs = np.append(delete_idxs, repeated_idxs[1:])
        li_masses[repeated_idxs[0]] = np.concatenate(li_masses[repeated_idxs]).ravel()

    li_instances = np.delete(instances, delete_idxs)
    machine_noise = np.array([np.std(m_arr)/np.mean(m_arr) for m_arr in np.delete(li_masses, delete_idxs)])

    if len(machine_noise):
        est_machine_noise = np.mean(machine_noise)

        if verbose: print(pd.DataFrame({'% deviation': machine_noise*100}, index=li_instances).sort_values(by='% deviation', ascending=False).round(3).to_markdown())

    if verbose:
        print(f"Scale noise (as mean percent deviation): {est_scale_noise*100:.3f}%", "\n")
        if est_yarn_noise is not None: print(f"Noise from variation in yarn linear density (as mean percent deviation): {est_yarn_noise*100:.3f}%", "\n")
        if est_machine_noise is not None: print(f"Noise from machine repeatability (as mean percent deviation): {est_machine_noise*100:.3f}%", "\n")

    return {'scale': est_scale_noise, 'yarn': est_yarn_noise, 'machine': est_machine_noise}


def train(data_paths=['data-auto/'], exclude_instances=[lambda x: 'rayon' in x], train_instances=[], valid_instances=[], labels_to_drop=[], main_stitch_size=30, carriers=[], method='Linear Regression', normalize_lindensity=False, x_vals=None, lindensities=None, plot=False, title=None, verbose=True, print_matrix=False, **train_args):
    if lindensities is not None: lindensities_ = lindensities.copy()
    else: lindensities_ = None

    labels, A_train, b_train, train_instances, A_valid, b_valid, valid_instances, stitchNumber_data, lindensities = helpers.getData(data_paths, exclude_instances=exclude_instances, train_instances=train_instances, valid_instances=valid_instances, labels_to_drop=labels_to_drop, carriers=carriers, main_stitch_size=main_stitch_size)

    if lindensities_ is not None:
        for (k,v) in lindensities_.items():
            lindensities[k] = v

    if print_matrix: #debug
        import sympy as sp
        print("labels = np.array(['" + "', '".join(labels) + "'])")

        print("A_train = np.array([")
        for row in A_train:
            print("  [" + ", ".join(row.astype(str)) + "],")
        print("])")

        print("b_train = np.array([" + ", ".join(b_train.astype(str)) + "])")
        print("sample_names = np.array(['" + "', '".join(train_instances) + "'])")
        print()

        sp.pprint(sp.Matrix(np.vstack([labels, A_train]))) #debug

        print(sp.latex(sp.Matrix(np.hstack([np.append([sp.Symbol(r'\text{feature}')], [sp.Symbol(r'\textbf{' + inst.replace('_', '').replace('{"', '').replace('":', ':').replace('}', '') + '}') for inst in train_instances]).reshape((-1, 1)), np.vstack([[sp.Symbol(r'\mathbf{'+label+'}') for label in labels], A_train])])))) # formatted latex

    if normalize_lindensity:
        norm_density = np.mean(lindensities['train'])
        norm_b_train = helpers.normalizeMass(b_train, lindensities['train'], norm_density)
        norm_b_valid = helpers.normalizeMass(b_valid, lindensities['valid'], norm_density)

        m = YarnModel(labels, A_train, norm_b_train, train_instances, A_valid=A_valid, b_valid=norm_b_valid, valid_instances=valid_instances, lindensities=lindensities, norm_density=norm_density)
    else:
        m = YarnModel(labels, A_train, b_train, train_instances, A_valid, b_valid, valid_instances)

    if x_vals is not None:
        x = np.array(x_vals)
        m.x = x

    method_name = method

    if method == 'gekko' or 'constrained' in method.lower():
        if not len(train_args):
            train_args['machine_cons'] = True
            train_args['geometric_cons'] = False
            train_args['otol'] = 1e-8

        if train_args.get('geometric_cons', False):
            train_args['bounds'] = [1e-8,1]
            train_args['rtol'] = 1e-5
    else:
        if 'fit_intercept' not in train_args: train_args['fit_intercept'] = False #default
        if train_args.get('positive', False): method_name = f'Nonnegative {method}'

    if x_vals is None: x = m.train(method, **train_args)
    else: x = x_vals

    if verbose:
        m.results()
        print(f"\n--- Train predictions for {method_name} ---")
    if normalize_lindensity: b_train_pred, train_mae, train_std = m.predict(A_train, norm_b_train, train_instances, lindensities=lindensities['train'], return_stats=True, verbose=verbose)
    else: b_train_pred, train_mae, train_std = m.predict(A_train, b_train, train_instances, return_stats=True, verbose=verbose)

    if verbose: print(f"\n--- Validation predictions for {method_name} ---")
    if normalize_lindensity: b_valid_pred, valid_mae, valid_std = m.predict(A_valid, norm_b_valid, valid_instances, lindensities=lindensities['valid'], return_stats=True, verbose=verbose)
    else: b_valid_pred, valid_mae, valid_std = m.predict(A_valid, b_valid, valid_instances, return_stats=True, verbose=verbose)

    A = np.vstack([A_train, A_valid])
    b = np.append(b_train, b_valid)
    b_pred = np.append(b_train_pred, b_valid_pred)

    instances = np.append(train_instances, valid_instances)

    if plot:
        if title is None:
            title = ""
            save_as_pre = ""
        else: save_as_pre = f"{title.lower().replace(' ', '_')}_"
        helpers.plotErrors(train_instances, b_train, b_train_pred, title=f'{title+": " if len(title) else ""}Train Error', save_as=f'figures/plots/{save_as_pre}train_err.pdf', graph='bar')
        helpers.plotErrors(valid_instances, b_valid, b_valid_pred, title=f'{title+": " if len(title) else ""}Validation Error', save_as=f'figures/plots/{save_as_pre}valid_err.pdf', graph='bar')
 
    return m, {'train_mae': train_mae, 'train_std': train_std, 'valid_mae': valid_mae, 'valid_std': valid_std}


def stitchNumberTrain(data_paths=['data-auto/'], train_instances=[], valid_instances=[], exclude_instances=[lambda x: 'rayon' in x], labels_to_drop=[], main_stitch_size=30, carriers=[], method='Linear Regression', fit_label='knit', fit_funcs=['linear', 'poly'], all_data_train=False, add_fixed_vals=True, exclude_outliers=True, plot=True, title="Curve Fits for Stitch-Size-Dependent Feature Data", **train_args):
    labels, A_train, b_train, train_instances, A_valid, b_valid, valid_instances, st_data, lindensities = helpers.getData(data_paths, exclude_instances=exclude_instances, train_instances=train_instances, valid_instances=valid_instances, labels_to_drop=labels_to_drop, carriers=carriers, main_stitch_size=main_stitch_size)

    norm_density = np.mean(lindensities['train'])

    if all_data_train: train_data = [A_train.copy(), b_train.copy(), train_instances.copy()]
    else: train_data = None

    solutions = {}
    
    if train_data is None: A, b, instances = st_data[main_stitch_size]
    else: A, b, instances = train_data

    main_model = YarnModel(labels, A, b, instances)

    if method == 'gekko' or 'constrained' in method.lower():
        if not len(train_args):
            train_args['machine_cons'] = True
            train_args['geometric_cons'] = False
            train_args['otol'] = 1e-8

        if train_args['geometric_cons']:
            train_args['bounds'] = [1e-8,1]
            train_args['rtol'] = 1e-5
        else:
            train_args['bounds'] = [0,1]
            train_args['rtol'] = 1e-5

    train_args['grams_per_cm'] = norm_density

    x = main_model.train(method, **train_args)
    
    print(f"\n--- Train predictions (main stitch size {main_stitch_size}): ---")
    main_model.predict(A, b, instances, verbose=True)
    
    main_model.results()

    if type(fit_label) == list:
        fit_labels = np.array(fit_label)
        # get the indices where the particular value occurs
        idxs = np.where(np.char.find(fit_labels, '(') != -1)
        fit_samples = fit_labels[idxs].tolist()
        fit_label = np.delete(fit_labels, idxs).tolist()
    else: fit_samples = []

    fit_samples_ydata = {el:{} for el in fit_samples}
 
    solutions[main_stitch_size] = x.copy()

    if add_fixed_vals:
        d1_idx = labels.index('d1') if 'd1' in labels else None
        g_idx = labels.index('gap') if 'gap' in labels else None
        d2_idx = labels.index('d2') if 'd2' in labels else None
        xl_idx = labels.index('xladder') if 'xladder' in labels else None
        m_idx = labels.index('miss') if 'miss' in labels else None

        train_args['fixed_vals'] = {d1_idx: x[d1_idx], d2_idx: x[d2_idx], g_idx: x[g_idx], xl_idx: x[xl_idx], m_idx: x[m_idx]}

    
    for st, (A, b, instances) in st_data.items():
        if len(fit_samples):
            for fit_sample in fit_samples:
                sample_idx = np.where(np.char.find(instances, fit_sample) == 0)
                fit_samples_ydata[fit_sample][st] = b[sample_idx][0]
            
        if st == main_stitch_size: continue
        
        st_model = YarnModel(labels, A, b, instances)
        x = st_model.train(method, **train_args)

        solutions[st] = x.copy()

        print(f"\n--- Predictions for stitch size {st}: ---")
        st_model.predict(A, b, instances, verbose=True)

        st_model.results()

    res_df = pd.DataFrame(solutions, labels).sort_index(axis=1)

    stitch_sizes = res_df.columns.values

    print(res_df.apply(lambda v: v*100).round(3).to_markdown()) #to mg

    if fit_label == 'all': fit_label == ['knit', 'edge-knit', 'tuck', 'xknit']
    if type(fit_label) == list:
        fit_func = {}
        eqns = {}
        r2_vals = {}
        y_fits = {}
        labels_y = {}
        for label in fit_label:
            if label in labels:
                ydata = res_df.loc[label].values
                labels_y[label] = ydata
                fit_func[label], r2_vals[label], y_fits[label], eqns[label] = helpers.curveFitter(ydata=ydata, stitch_sizes=stitch_sizes, main_stitch_size=main_stitch_size, op=label, exclude_outliers=(label in exclude_outliers if type(exclude_outliers) == list else exclude_outliers), return_all=False, fit_funcs=fit_funcs)
        
        if len(fit_samples):
            for fit_sample in fit_samples:
                ydata = np.array(sorted(fit_samples_ydata[fit_sample].items()))[:,1]
                labels_y[fit_sample] = ydata
                _, r2_vals[fit_sample], y_fits[fit_sample], eqns[fit_sample] = helpers.curveFitter(ydata=ydata, stitch_sizes=stitch_sizes, main_stitch_size=main_stitch_size, op=fit_sample, exclude_outliers=(fit_sample in exclude_outliers if type(exclude_outliers) == list else exclude_outliers), return_all=False, fit_funcs=['linear'], show=plot, save_as=f"figures/plots/{fit_sample}_fit.pdf")

        if plot: helpers.plotFits(ydata=labels_y, stitch_sizes=stitch_sizes, main_stitch_size=main_stitch_size, exclude_outliers=exclude_outliers, r2_vals=r2_vals, y_fits=y_fits, eqns=eqns, title=title, save_as="figures/plots/feature_curve_fits.pdf")
    else:
        ydata = res_df.loc[fit_label].values
        fit_func, _, _, _ = helpers.curveFitter(ydata=ydata, stitch_sizes=stitch_sizes, main_stitch_size=main_stitch_size, exclude_outliers=exclude_outliers, op=fit_label, return_all=False, fit_funcs=fit_funcs, show=plot, save_as=f"figures/plots/{fit_label}_fit.pdf")

    print("--------------------------")
    print("When trained on main data:")
    print("--------------------------")
    for st, (A, b, instances) in st_data.items():
        if st == main_stitch_size: continue

        steps = (st-main_stitch_size)/5
        print(f"\n--- Predictions for stitch size {st}: ---")
        main_model.stitchNumber_predict(steps=steps, vfunc=fit_func, A=A, b=b, instances=instances, verbose=True)


def lindensityTrain(data_paths=['data-auto/'], exclude_instances=[lambda x: 'rayon' in x], train_instances=[], valid_instances=[], labels_to_drop=[], main_stitch_size=30, carriers=[], method='Linear Regression', plot=False, x_vals=None, find_stretch=False, stretch_range=[0.3, 0.5], stretch_step_size=0.01, verbose=True, **train_args):
    m, stats = train(data_paths=data_paths, exclude_instances=exclude_instances, train_instances=train_instances, valid_instances=valid_instances, labels_to_drop=labels_to_drop, main_stitch_size=main_stitch_size, carriers=carriers, method=method, normalize_lindensity=True, x_vals=x_vals, plot=plot, verbose=verbose, **train_args)

    valid_lindensities = m.valid_lindensities

    x_ld = (m.x/m.norm_density)*np.mean(valid_lindensities)
    print(f"\n--- Operation Predictions (scaled by LD) ---\n")
    res = {'feature': m.labels, 'mass (mg)': x_ld*1000}
    print(pd.DataFrame(res).set_index(['feature']).round(3).to_markdown())
    
    if find_stretch:
        res = {}
        for n in np.arange(*stretch_range, stretch_step_size): #this can be adjusted 
            if verbose: print(f"stretch factor: {n}") #debug
            m, stats = train(data_paths=data_paths, exclude_instances=exclude_instances, train_instances=train_instances, valid_instances=valid_instances, labels_to_drop=labels_to_drop, main_stitch_size=main_stitch_size, carriers=carriers, method=method, normalize_lindensity=True, x_vals=x_vals, lindensities={'valid': n*valid_lindensities}, plot=plot, verbose=verbose, **train_args)

            res[n] = stats.copy()
        
        stretch_factor = min(res, key=lambda x: res[x]['valid_mae'])

        x_ld = (m.x/m.norm_density)*(stretch_factor*np.mean(valid_lindensities))
        print(f"\n--- Operation Predictions (scaled by {round(stretch_factor*100,3)}% of LD) ---\n")
        pred_res = {'feature': m.labels, 'mass (mg)': x_ld*1000}
        print(pd.DataFrame(pred_res).set_index(['feature']).round(3).to_markdown())

        print(f"Predicted stretch factor: {stretch_factor}")
        print(f"Scaled avg linear density: {np.format_float_scientific(np.mean(valid_lindensities)*stretch_factor, precision=2)} g/cm")
        print(f"Stats: {res[stretch_factor]}")


from sklearn.model_selection import KFold

def batchTrain(data_path='data-auto/', exclude_instances=[lambda x: 'rayon' in x], carriers=[], n_splits=10, verbose=True):
    labels, A, b, instances, _, _, _, stitchNumber_data, _ = helpers.getData(data_path, exclude_instances=exclude_instances, carriers=carriers)

    kf = KFold(n_splits=n_splits)

    train_std = {'Linear Regression': [], 'Positive Linear Regression': [], 'Constrained LP': []}
    valid_std = {'Linear Regression': [], 'Positive Linear Regression': [], 'Constrained LP': []}
    train_errs = {'Linear Regression': [], 'Positive Linear Regression': [], 'Constrained LP': []}
    valid_errs = {'Linear Regression': [], 'Positive Linear Regression': [], 'Constrained LP': []}

    for i, (train_idxs, test_idxs) in enumerate(kf.split(A)):
        A_train, b_train, train_instances = A[train_idxs], b[train_idxs], instances[train_idxs]

        A_valid, b_valid, valid_instances = A[test_idxs], b[test_idxs], instances[test_idxs]

        method = 'Linear Regression'
        train_args = {'positive': False, 'fit_intercept': False}
        m = YarnModel(labels, A_train, b_train, train_instances, A_valid, b_valid, valid_instances)
        m.train(method, **train_args)

        if verbose:
            print(f"\n--- Predictions for {method} ({train_args}) ---")
            m.predict(A_valid, b_valid, valid_instances, verbose=True)
            m.results()

        train_errs['Linear Regression'].append(m.mae(A_train, b_train))
        train_std['Linear Regression'].append(m.std(A_train, b_train))
        valid_errs['Linear Regression'].append(m.mae(A_valid, b_valid))
        valid_std['Linear Regression'].append(m.std(A_valid, b_valid))

        method = 'Linear Regression'
        train_args = {'positive': True, 'fit_intercept': False}
        m = YarnModel(labels, A_train, b_train, train_instances, A_valid, b_valid, valid_instances)
        m.train(method, **train_args)

        if verbose:
            print(f"\n--- Predictions for {method} ({train_args}) ---")
            m.predict(A_valid, b_valid, valid_instances, verbose=True)
            m.results()

        train_errs['Positive Linear Regression'].append(m.mae(A_train, b_train))
        train_std['Positive Linear Regression'].append(m.std(A_train, b_train))
        valid_errs['Positive Linear Regression'].append(m.mae(A_valid, b_valid))
        valid_std['Positive Linear Regression'].append(m.std(A_valid, b_valid))

        method = 'gekko'
        train_args = {'machine_cons': True, 'geometric_cons': False}
        m = YarnModel(labels, A_train, b_train, train_instances, A_valid, b_valid, valid_instances)
        m.train(method, **train_args)

        if verbose:
            print(f"\n--- Predictions for {method} ({train_args}) ---")
            m.predict(A_valid, b_valid, valid_instances, verbose=True)
            m.results()

        train_errs['Constrained LP'].append(m.mae(A_train, b_train))
        train_std['Constrained LP'].append(m.std(A_train, b_train))
        valid_errs['Constrained LP'].append(m.mae(A_valid, b_valid))
        valid_std['Constrained LP'].append(m.std(A_valid, b_valid))


    avg_train_errs = {k: np.mean(v) for k,v in train_errs.items()}
    avg_train_std = {k: np.mean(v) for k,v in train_std.items()}
    avg_valid_errs = {k: np.mean(v) for k,v in valid_errs.items()}
    avg_valid_std = {k: np.mean(v) for k,v in valid_std.items()}

    print("avg_train_errs:", avg_train_errs)
    print("avg_train_std:", avg_train_std)
    print("avg_valid_errs:", avg_valid_errs)
    print("avg_valid_std:", avg_valid_std)



from itertools import combinations
from math import factorial
import random
import time

def randomSampleTrain(data_paths=['data-auto/'], exclude_instances=[lambda x: 'rayon' in x], labels_to_drop=[], main_stitch_size=30, carriers=[], methods=[('Linear Regression', {'positive': False}), ('Nonnegative Linear Regression', {'positive': True}), ('Constrained Convex Opti', {'machine_cons': True, 'geometric_cons': True, 'rtol': 1e-4, 'otol': 1e-8})], random_sample=True, must_include=None, min_bs=6, max_bs=np.inf, iters_per_bs=np.inf, ensure_independence=False, verbose=True, only_print_best=True, print_delay=3):
    labels, A, b, instances, _, _, _, _, _ = helpers.getData(data_paths, exclude_instances=exclude_instances, labels_to_drop=labels_to_drop, main_stitch_size=main_stitch_size, carriers=carriers)

    if must_include is not None:
        must_include_funcs = [np.vectorize(v) for v in must_include if callable(v)]
        must_include = [v for v in must_include if not callable(v)]

        for func in must_include_funcs:
            must_include.extend(list(instances[np.where(func(instances))]))

        if not len(must_include): must_include = None
    else: must_include_funcs = []

    for i, method in enumerate(methods):
        if type(method) == str: method[i] = (method, {})

    stats = []

    n = len(b) # num samples
    idxs = list(range(n))

    lowest_err = np.inf
    
    if must_include is not None:
        must_include_idxs = np.where(np.in1d(instances, must_include))[0]
        idxs = list(np.delete(np.array(idxs), must_include_idxs))

    class RandomSampler:
        def __init__(self, k):
            self.k = k
            self.condition = lambda i: np.all(np.sum(A[i], axis=0))

        def __iter__(self):
            return self

        def __next__(self):
            if must_include is not None:
                np_idxs = np.array(random.sample(idxs, self.k-len(must_include)))

                while not self.condition(np.append(must_include_idxs, np_idxs)):
                    np_idxs = np.array(random.sample(idxs, self.k-len(must_include)))

                np_idxs = np.append(must_include_idxs, np_idxs)
            else:
                np_idxs = np.array(random.sample(idxs, self.k))
                while not self.condition(np_idxs):
                    np_idxs = np.array(random.sample(idxs, self.k))

            return np_idxs

    for k in range(min_bs, n+1):
        if k > max_bs: break

        if must_include is None: select_k = k
        else: select_k = k-len(must_include)

        k_stats = [[[],[],[],[]] for _ in range(len(methods))]
        
        NUM_COMBS = int(factorial(n)/(factorial(select_k)*factorial(n-select_k))) # binomial coefficient
        num_combs = NUM_COMBS
        if verbose: print(f"num combs (k = {k}):", num_combs)
        else: print(f"k: {k}/{max_bs}")

        random.shuffle(idxs) # so we aren't getting too many from the same batch when we use low k numbers

        if random_sample:
            # create an object
            combs = RandomSampler(k)
        else:
            if must_include is None: combs = filter(lambda i: np.all(np.sum(A[np.array(i)], axis=0)), combinations(idxs, k)) # ensure that there is at least one of each operation
            else:
                combs = filter(lambda i: np.all(np.sum(A[np.append(must_include_idxs, np.array(i))], axis=0)), combinations(idxs, k-len(must_include)))

        i = 0

        for batch_idxs in combs:
            np_idxs = np.array(batch_idxs)

            if must_include is not None and not random_sample: np_idxs = np.append(must_include_idxs, np_idxs)

            if verbose:
                if i % 1000 == 0: print(f"({i+1}/{min(iters_per_bs, NUM_COMBS)})")

            if ensure_independence: np_idxs = helpers.linearlyIndependent(A[np_idxs])

            A_train, b_train, train_instances = A[np_idxs], b[np_idxs], instances[np_idxs]
            
            A_valid, b_valid, valid_instances = np.delete(A, np_idxs, axis=0), np.delete(b, np_idxs), np.delete(instances, np_idxs)

            for m_idx, (method, kwargs) in enumerate(methods):
                model = YarnModel(labels=labels, A_train=A_train, b_train=b_train, train_instances=train_instances, A_valid=A_valid, b_valid=b_valid, valid_instances=valid_instances)

                method_name = str((method, kwargs))
                try:
                    model.train(method=method, **kwargs)

                    if len(b_valid):
                        _, valid_mae, valid_std = model.predict(A=A_valid, b=b_valid, instances=valid_instances, return_stats=True, verbose=False)

                        k_stats[m_idx][0].append(valid_mae)
                        k_stats[m_idx][1].append(valid_std)

                        if verbose or (only_print_best and valid_mae < lowest_err):
                            print(f"\n--- Predictions for {method_name} ---")

                            print(f'{k} samples ["' + '", "'.join(instances[np_idxs]) + '"]')

                            if verbose:
                                model.predict(A=A_valid, b=b_valid, instances=valid_instances, return_stats=True, verbose=True)
                            
                                model.results()
                            else: print(f"\nmean error: {valid_mae*100:.3f}%, std: {valid_std*100:.3f}%\n")
                            
                            lowest_err = valid_mae

                    k_stats[m_idx][2].append(model.mae(A_train, b_train))
                    k_stats[m_idx][3].append(model.std(A_train, b_train))
                except Exception as e: # for when we get Exception: @error: Solution Not Found
                    if verbose: print(e)
                    continue

            if i >= iters_per_bs: break
            else: i += 1

            if verbose: time.sleep(print_delay)

        mean_k_stats = []
        for m_idx in range(len(k_stats)):
            if len(k_stats[m_idx][0]): mean_k_stats.append([np.mean(k_stats[m_idx][0])*100, np.mean(k_stats[m_idx][1])*100])
            else: mean_k_stats.append([None, None])

            if len(k_stats[m_idx][2]):  mean_k_stats.append([np.mean(k_stats[m_idx][2])*100, np.mean(k_stats[m_idx][3])*100])
            else: mean_k_stats.append([None, None])

        stats.append(mean_k_stats)

    return np.array(stats, dtype=float)


def plotModelPerformance(data_paths, exclude_instances=[], labels_to_drop=[], min_bs=7, max_bs=np.inf, iters_per_bs=50, methods=[('Linear Regression', {'positive': False}), ('Nonnegative Linear Regression', {'positive': True}), ('Constrained Convex Optimization', {'machine_cons': True, 'geometric_cons': True, 'rtol': 1e-2, 'otol': 1e-8})], plot_std=False):
    stats = randomSampleTrain(data_paths=data_paths, carriers=[], exclude_instances=exclude_instances, labels_to_drop=labels_to_drop, methods=methods, random_sample=True, must_include=None, min_bs=min_bs, max_bs=max_bs, iters_per_bs=iters_per_bs, ensure_independence=False, verbose=False, print_delay=0).T

    if max_bs == np.inf: max_bs = stats.shape[-1]+min_bs-1

    helpers.plotMetric(stats, 'MAE', min_bs, max_bs, iters_per_bs, methods, save_as='figures/plots/model_performance_mae.png')

    if plot_std: helpers.plotMetric(stats, 'STD', min_bs, max_bs, iters_per_bs, methods, save_as='figures/plots/model_performance_std.png')

    stats_strs = [['N/A' if np.isnan(info[0]) else f"{info[0]:.2f}" + r' \% $\pm$ ' + f"{info[1]:.2f}" for info in k_stats] for k_stats in stats.T]

    df = pd.DataFrame(np.array(stats_strs), index=range(min_bs, max_bs+1), columns=pd.MultiIndex.from_product([[method[0] for method in methods], [r'Validation', r'Train']], names=[r'\underline{Method:}', r'\underline{Set:}']))
    df.index.name = r'$\mathbf{n}$ \textbf{Samples}'

    with open('random_sample_table.tex', 'w+') as f:
        f.write('\n'.join([r'\documentclass[8pt,letterpaper]{article}', r'\usepackage[letterpaper,margin=0.5in]{geometry}', r'\usepackage{booktabs}', r'\begin{document}',  df.round(3).to_latex(bold_rows=True, escape=False), r'\end{document}']))
