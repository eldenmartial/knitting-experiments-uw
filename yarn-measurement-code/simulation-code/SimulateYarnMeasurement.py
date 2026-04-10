import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
import pandas as pd

#will model variation in machine operation, yarn density, and weight returned by the scale
# as multiplicative noise with mean 1 and standard deviations as follows:

#older estimates -- may not have been proper measurement:
#scale_noise_stddev = 0.00398
#machine_noise_stddev = 0.02575
#yarn_density_noise_stddev = 0.05908

#standard deviation of measured_weight / real_weight:
scale_noise_stddev = 0.001

#standard deviation of fabricated sample weight / "ideal" weight:
# (bakes in both machine and yarn variation)
machine_and_yarn_noise_stddev = 0.02

#^^^ the above were estimated from 28 samples knit with stitch 30 / leading 25 from Tamm Petit; basically every sample we knit of our seven test swatches that didn't fail.

def experiment(samples, knit, weigh):
    #do samples in order by name:
    sorted_samples = [samples[i] for i in sorted(samples.keys())]

    #operation counts and measurements for all knitted + weighted samples:
    sample_counts = []
    sample_weights = []
    for sample in sorted_samples:
        for knittings in range(3): #each sample was knitted three times
            knitted = knit(sample)
            for weightings in range(3): #each knit sample was weighed three times
                weight = weigh(knitted)
                sample_counts.append(sample)
                sample_weights.append(weight)

    # fit per-operation weights
    reg = linear_model.LinearRegression(fit_intercept=False, positive=True)
    reg.fit(np.array(sample_counts), np.array(sample_weights))
    measurements = reg.coef_

    # estimated operation lengths
    return measurements
     
     

def run_experiments():
    #name and weight (mg) for each operation:
    #taken from the estimates in Full-data condition of the Feature Weights table
    ops = {
        'd1': 0.10,
        'd2': 0.17,
        'edge-knit': 0.49,
        'knit': 0.39,
        'miss': 0.14,
        'tuck': 0.41,
        'x-knit': 0.84,
    }
    op_names = [
        'd1', 'd2', 'edge-knit', 'knit', 'miss', 'tuck', 'x-knit'
    ]
    assert(op_names == sorted(ops.keys()))
    op_weights = []
    #NOTE: randomizing op_weights per trial below!
    print("WARNING: randomizing op_weights per trial. Make sure this is what you want.")

    #sample counts for each sample (counts in the same order as op_names):
    samples = {
        'rib-fb (159 x 60)':            [ 9480, 0, 118, 9422, 0, 0, 0],
        'half-gauge rib-fb (159 x 60)': [ 0, 4740, 118, 4682, 0, 0, 0],
        'jersey (18 x 530)':            [ 0, 0, 1058, 8482, 0, 0, 0],
        'jersey (159 x 60)':            [ 0, 0, 118, 9422, 0, 0, 0],
        'half-gauge jersey (159 x 60)': [ 0, 0, 118, 4682, 4740, 0, 0],
        'tuck-stitch (159 x 60)':       [ 0, 0, 118, 4712, 0, 4710, 0],
        'jersey tube (9 x 1060)':       [ 0, 0, 0, 14842, 0, 0, 2119],
    }

    # true_linear_density = 0.0007292708883
    #(linear density is unused)

    def knit(op_counts):
        """
        knit takes in a list of operation counts and returns an opaque value,
        which models the object that would be created by the knitting machine.

        :param op_dict: dictionary that maps operation type to knit
        :return: a KnittedItem with a yarn length and true weight based on the count of each operation
        """
        assert(len(op_counts) == len(op_weights))
        total_yarn_weight = 0.0
        for i in range(len(op_counts)):
            total_yarn_weight += op_counts[i] * op_weights[i]

        # add machine noise, linear density noise
        total_yarn_weight *= np.random.normal(1, machine_and_yarn_noise_stddev)

        knit_object = {'total_yarn_weight':total_yarn_weight}

        return knit_object


    def weigh(knit_object):
        """
        weigh takes in the opaque value produced by the knit function and returns the
        item's weight (with scale noise).

        :param total_yarn_length: the total
        :return: a float returning the measured quantity with noise
        """


        # weigh with scale noise
        measured_weight = knit_object['total_yarn_weight']

        #scale noise:
        measured_weight *= np.random.normal(1, scale_noise_stddev)

        # computer noised length from weight and linear density
        return measured_weight
    
    all_error = []
    experiment_names = []

    #true_weights = np.array(op_weights)
    #print("true weights: ", true_weights)
    for x in range(10000):
        op_weights = np.array([ops[n] * np.random.uniform(0.9,1.1) for n in op_names])
        experiment_weights = experiment(samples, knit, weigh)
        if (x == 0):
            print(f"experiment_weights[{x}]", experiment_weights)

        error = (experiment_weights-op_weights)/op_weights
        all_error.append(error)
        experiment_names.append("experiment_" + str(x))

    dataframe = pd.DataFrame(all_error, columns = op_names, index = experiment_names)
    np.savetxt("op_names.csv", op_names, fmt="%s")
    dataframe.to_csv("dataframe.csv")
    
run_experiments()
# put everything in csv from pandas
    
