import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# def gen_slope(x):
#     slope = []
#     slope.append(abs(x[0] - x[1]))
#     for i in range(1, len(x)-1):
#         slope.append((abs(x[i-1] - x[i]) + abs(x[i] - x[i+1]))/2)
#     slope.append(abs(x[len(x)-1] - x[len(x)-2]))
#     return np.array(slope)
def gen_slope(x, window_size=2):
    slope = []
    for i in range(len(x)):
        l_bound = max(0, i-window_size)
        r_bound = min(len(x)-1, i+window_size)
        neighbor = x[l_bound:r_bound+1]
        s = sum(np.abs(neighbor - x[i]))/(len(neighbor) - 1)
        slope.append(s)
    return np.array(slope)


def cluster(graph, plot=False):
    slope = gen_slope(graph)
    X = np.zeros((len(slope), 2))
    X[:, 0] = slope
    n_clusters=2
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(X)
    if plot:
        t = np.arange(len(graph))
        color = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink']
        for i in range(len(kmeans.labels_)):
            plt.scatter([t[i]], [graph[i]], c=color[kmeans.labels_[i]])
        plt.show()
    return kmeans.labels_