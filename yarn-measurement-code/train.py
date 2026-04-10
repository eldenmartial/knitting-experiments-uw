import model

import argparse

parser = argparse.ArgumentParser()


parser.add_argument('-d', '--data_paths', nargs='+', help='path to folders containing data', default=['data-auto/', 'data-st/'])

parser.add_argument('-t', '--train_instances', nargs='+', default=[])


parser.add_argument('-v', '--valid_instances', nargs='+', default=['data-auto/'])

parser.add_argument('-e', '--exclude_instances', nargs='+', default=[lambda x: 'rayon' in x, lambda x: 'elastomer' in x, lambda x: '"stitchNumber": 64}' in x or '"stitchNumber": 94}' in x or '"stitchNumber": 77}' in x or '"stitchNumber": 20}' in x])

parser.add_argument('-s','--main_stitch_size', help='main stitch size (used in training)', default=30)

parser.add_argument('-c','--carriers', nargs='+', help='carriers to parse knitout for', default=[]) #[] means parse for all


parser.add_argument('-m', '--method', type=str, help='modeling method', default='Linear Regression')

parser.add_argument('-p', '--positive', action='store_true')

parser.add_argument('--plot', action='store_true')

parser.add_argument('-l','--labels_to_drop', nargs='+', help='', default=['gap'])

parser.add_argument('-n', '--normalize_lindensity', help='whether to normalize for linear density', action='store_true')


args = parser.parse_args()

# ============================= TRAIN ON BASIC SET =============================
model.train(data_paths=args.data_paths, exclude_instances=args.exclude_instances, train_instances=args.train_instances, valid_instances=['data-auto/'], labels_to_drop=args.labels_to_drop, main_stitch_size=args.main_stitch_size, carriers=args.carriers, method=args.method, normalize_lindensity=args.normalize_lindensity, positive=args.positive, fit_intercept=False, plot=args.plot, title=None)
# ==============================================================================

# ========================== TRAIN ON VALIDATION SET ===========================
# model.train(data_paths=args.data_paths, exclude_instances=args.exclude_instances, train_instances=args.train_instances, valid_instances=args.valid_instances, labels_to_drop=args.labels_to_drop, main_stitch_size=args.main_stitch_size, carriers=args.carriers, method=args.method, normalize_lindensity=args.normalize_lindensity, positive=args.positive, fit_intercept=False, plot=args.plot, title='Validation Set')
# ==============================================================================


# ================================ ELASTOMERIC =================================
# model.lindensityTrain(data_paths=args.data_paths, exclude_instances=[lambda x: 'rayon' in x], train_instances=[], valid_instances=[lambda x: 'elastomer' in x], labels_to_drop=args.labels_to_drop, main_stitch_size=args.main_stitch_size, carriers=args.carriers, method=args.method, positive=args.positive, fit_intercept=False, find_stretch=True, verbose=False, plot=False)
# ==============================================================================


# =================================== RAYON ====================================
# model.lindensityTrain(data_paths=args.data_paths, exclude_instances=[lambda x: 'elastomer' in x], train_instances=[], valid_instances=[lambda x: 'rayon' in x], labels_to_drop=args.labels_to_drop, main_stitch_size=args.main_stitch_size, carriers=args.carriers, method=args.method, positive=args.positive, fit_intercept=False, find_stretch=False, verbose=True, plot=False)
# ==============================================================================


# =============================== STITCH NUMBER ================================
# model.stitchNumberTrain(data_paths=args.data_paths, exclude_instances=args.exclude_instances, train_instances=args.train_instances, valid_instances=args.valid_instances, labels_to_drop=args.labels_to_drop, main_stitch_size=args.main_stitch_size, carriers=args.carriers, method=args.method, min_labels=False, fit_label=['knit', 'tuck', 'edge-knit', 'xknit', 'jersey (159x60)'], exclude_outliers=['edge-knit', 'xknit'], fit_funcs=['linear'], positive=args.positive)
# ==============================================================================


# ================================= EVALUATION =================================
# --- noise ---
# model.estimateNoise(data_paths=['data-st/'], masses_paths=['masses-st/'], exclude_instances=args.exclude_instances)
# # model.estimateNoise(data_paths=args.data_paths, masses_paths=['masses-st/', 'masses-auto/'], exclude_instances=args.exclude_instances)

# --- method comparison ---
# model.plotModelPerformance(data_paths=['data-auto/', 'data-st/'], exclude_instances=args.exclude_instances, labels_to_drop=['gap'], iters_per_bs=100, methods=[('Linear Regression', {'positive': False}), ('Nonnegative Linear Regression', {'positive': True}), ('Constrained Convex Optimization', {'machine_cons': True, 'geometric_cons': True, 'rtol': 1e-2, 'otol': 1e-8})])
# ==============================================================================