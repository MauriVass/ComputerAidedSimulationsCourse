import matplotlib.pyplot as plt
import csv

def plot_graph(input_filename,output_filename):

    n = []
    ave = []
    lower_bound=[]
    upper_bound=[]
    ci1=[]
    ci2=[]

    with open(input_filename,'r') as csvfile:
        plots = csv.reader(csvfile, delimiter='\t')
        first_line=True
        for row in plots:
            if first_line:
                first_line=False
            else:
                n.append(float(row[0]))
                lower_bound.append(float(row[1]))
                upper_bound.append(float(row[2]))
                ci1.append(float(row[3]))
                ave.append(float(row[4]))
                ci2.append(float(row[5]))
    plt.plot(n, upper_bound, label='Upper bound', linestyle='dotted')
    plt.plot(n,ave, label='Simulation',marker='o')
    plt.plot(n,lower_bound, label='Lower bound',linestyle='dotted')

    plt.xscale("log")
    plt.fill_between(n, ci1,ci2, color='b', alpha=.1)
    plt.xlabel('Bins')
    plt.ylabel('Max bin occupancy')
    plt.ylim(bottom=0)
    # plt.title('Simulation')
    plt.legend()
    # plt.show()
    plt.savefig(output_filename)
    plt.clf()
plot_graph('binsballs-5runs.dat','graph-5runs.pdf')
plot_graph('binsballs-10runs.dat','graph-10runs.pdf')
plot_graph('binsballs-40runs.dat','graph-40runs.pdf')
