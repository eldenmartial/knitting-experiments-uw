import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def display():
    dataframe = pd.read_csv('dataframe.csv',)
    op_names = np.loadtxt("op_names.csv", dtype=str)

    # max() or min () is called twice because the first call
    # the max/min of each row, the second finds the max/min
    # of that list of those row max/min
    max_error = dataframe[op_names].max().max()
    min_error = dataframe[op_names].min().min()

    print(f"Error is in range [{min_error},{max_error}]")

    plt.figure(figsize=(10,3))
    #plt.margins(0,0)
    for op in op_names:
        n,x = np.histogram(100 * dataframe[op], 60, (-50, 50))
        
        # from stackOverflow
        bin_centers = 0.5*(x[1:]+x[:-1])
        plt.plot(bin_centers,n,label=op) ## using bin_centers rather than edges
        plt.fill_between(bin_centers,n,alpha=0.3)

    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": [],                   # use latex default serif font
        "font.sans-serif": ["DejaVu Sans"], # use a specific sans-serif font
        })
    plt.ylim(ymin=0.0)
    plt.title('Error of Simulated Knitting Experiments')
    plt.xlabel('Relative Operation Error (\\%)')
    plt.ylabel('Frequency of Error Value (in \\# of trials)')
    plt.legend()
    plt.savefig('figure.pdf', backend='pgf', bbox_inches='tight')

display()
