import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
import pandas as pd
import itertools

# - MAE
# - Additive vs multiplicative

scale_noise = 0.00398
machine_noise = 0.02575
linear_density_noise = 0.05908
def experiment(samples, knit, measure):
    sample_measurements = []
    for sample in samples:
        knitted = knit(sample)
        measured = measure(knitted)
        sample_measurements.append(measured)

    # optimize
    sorted_samples = [[sample[i] for i in sorted(sample.keys())] for sample in samples]
    matrix = np.array(sorted_samples)
    # intercept: false, positive: true
    reg = linear_model.LinearRegression(fit_intercept=False, positive=True)
    reg.fit(matrix, sample_measurements)
    measurements = reg.coef_

    # estimated operation lengths
    return measurements
     
     

def run_experiments(idx, combine_machine, combine_density, combine_scale):
    op_names = np.array(['d1', 'd2', 'edge-knit', 'knit', 'miss', 'tuck', 'xknit'])

    A = np.array([[ 9480, 0, 118, 9422, 0, 0, 0],
    [ 0, 0, 0, 14842, 0, 0, 2119],
    [ 0, 4740, 118, 4682, 4740, 0, 0],
    [ 0, 0, 118, 4712, 0, 4710, 0],
    [ 0, 0, 1058, 8482, 0, 0, 0],
    [ 0, 0, 118, 9422, 0, 0, 0],
    [ 0, 0, 118, 4682, 4740, 0, 0]])

    b = np.array([4.71566667, 7.576, 2.69166667, 3.90466667, 3.7565, 3.812,
    2.559 ])

    # fill n w/ actual data
    samples = []

    for sample in A:
        cts = {}
        for i, label in enumerate(op_names):
            cts[label] = sample[i]
        samples.append(cts)

            
    op_measurements = dict(zip(op_names, b))

    def knit(op_nums):
        """
        knit takes in a dictionary of operations and returns a KnittedItem object, 
        which models the object that would be created by the knitting machine.

        :param op_dict: dictionary that maps operation type to knit
        :return: a KnittedItem with a yarn length and true weight based on the count of each operation
        """
        total_yarn_weight = 0.0
        for op in op_nums.keys():
            total_yarn_weight += op_nums[op] * op_measurements[op]

        # add machine noise, linear density noise
        total_yarn_weight = combine_machine(total_yarn_weight, machine_noise)

        total_yarn_weight = combine_density(total_yarn_weight, linear_density_noise)

        return total_yarn_weight


    def measure(total_yarn_weight):
        """
        measure takes in the total length produced by the knit function and models that item being
        measured with noise.

        :param total_yarn_length: the total
        :return: a float returning the measured quantity with noise
        """


        # weigh with scale noise
        measured_weight = combine_scale(total_yarn_weight, scale_noise)


        # computer noised length from weight and linear density
        return measured_weight
    
    all_error = []
    experiment_names = []

    # optimize
    sorted_measurement = [op_measurements[i] for i in sorted(op_measurements.keys())]

    true_measurements = np.array(sorted_measurement)
    for x in range (10000):
        experiment_measurements = experiment(samples, knit, measure)

        error = np.subtract(true_measurements, experiment_measurements)
        # np.abs(experiment_measurements-true_measurements)/true_measurements
        all_error.append(error)
        experiment_names.append("experiment_" + str(x))

    dataframe = pd.DataFrame(all_error, columns = op_names, index = experiment_names)
    np.savetxt("op_names.csv", op_names, fmt="%s")
    dataframe.to_csv("./combinations/dataframe" + str(idx) + ".csv")

def run_all_combinations():
    multiplicative = ("mult", lambda weight, noise : weight * np.random.normal(1, noise))
    additive = ("add", lambda weight, noise : weight + np.random.normal(0, noise*weight))
    functions = [multiplicative, additive]

    all_combinations = itertools.product(functions, functions, functions)

    idx = 0
    combination_names = []
    for noises in all_combinations:
        run_experiments(idx, noises[0][1], noises[1][1], noises[2][1])
        description = "Machine Noise: " + noises[0][0] + ", Density Noise: " + noises[1][0] + ", Scale Noise: " + noises[2][0]
        combination_names.append(description)
        idx += 1

    np.savetxt("combination_names.csv", np.array(combination_names), fmt="%s")
    



run_all_combinations()
    
# put everything in csv from pandas
    
