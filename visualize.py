import numpy as np
import matplotlib.pyplot as plt
import cv2


def plot_cluster(kp, label):
    color = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:cyan']
    t = np.arange(len(kp))
    for i in range(len(label)):
        plt.scatter([t[i]], [kp[i]], c=color[label[i]])
    plt.show()

    
def plot_multi_cluster(kp_label_arr):
    color = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:cyan']
    for n, (kp, label) in enumerate(kp_label_arr):
        t = np.arange(len(kp))
        label = np.array(label)
        label += 2*n
        for i in range(len(label)):
            plt.scatter([t[i]], [kp[i]], c=color[label[i]])
    plt.show()


def plot_left_right_line(filename, leftline, rightline):
    # x = (y-c)/m
    cap = cv2.VideoCapture(f'result/{filename}/out.avi')
    _, background = cap.read()
    ceil = background.shape[0]
    plt.imshow(cv2.cvtColor(background, cv2.COLOR_BGR2RGB))

    plt.plot([(ceil-leftline[1])/leftline[0] ,-leftline[1]/leftline[0]], [ceil, 0], c='r')
    plt.plot([(ceil-rightline[1])/rightline[0] ,-rightline[1]/rightline[0]], [ceil, 0], c='r')
    plt.show()
