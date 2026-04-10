import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def save(idx, desc, op_names):
    dataframe = pd.read_csv('./combinations/dataframe' + str(idx) + '.csv',)

    # max() or min () is called twice because the first call
    # the max/min of each row, the second finds the max/min
    # of that list of those row max/min
    max_error = dataframe[op_names].max().max()
    min_error = dataframe[op_names].min().min()

    print(min_error)
    print(max_error)

    for op in op_names:
        n,x = np.histogram(dataframe[op], 20, (min_error-0.1, max_error+0.1))
        
        # from stackOverflow
        bin_centers = 0.5*(x[1:]+x[:-1])
        plt.plot(bin_centers,n,label=op) ## using bin_centers rather than edges
        plt.fill_between(bin_centers,n,alpha=0.3)

    plt.ylim(ymin=0.0)
    plt.title('Error of Simulated Knitting Experiment Severity vs Frequency')
    plt.xlabel('Error of Knit Values (true-estimated)')
    plt.ylabel('Frequency of Error Value')
    print(desc)
    plt.annotate(desc, (0, 1), (0,30), xycoords='axes fraction', textcoords='offset points', va='top', fontsize=8)
    plt.legend()
    plt.savefig('./histograms/histogram' + str(idx) + '.png')
    plt.clf()

def display_all():
    op_names = np.loadtxt("op_names.csv", dtype=str)
    combination_names = np.loadtxt("combination_names.csv", dtype=str, delimiter="~")
    idx = 0
    for desc in combination_names:
        save(idx, desc, op_names)
        idx += 1


display_all()