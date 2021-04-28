from copy import deepcopy
import numpy as np


def trim_zero(xL, xR, yL, yR, xL_toe, xR_toe, yL_toe, yR_toe):
    xLfilter = deepcopy(xL)
    xRfilter = deepcopy(xR)
    yLfilter = deepcopy(yL)
    yRfilter = deepcopy(yR)
    xLfilter_toe = deepcopy(xL_toe)
    xRfilter_toe = deepcopy(xR_toe)
    yLfilter_toe = deepcopy(yL_toe)
    yRfilter_toe = deepcopy(yR_toe)
    bulk = [xLfilter, xRfilter, yLfilter, yRfilter, xLfilter_toe, xRfilter_toe, yLfilter_toe, yRfilter_toe]
    
    while xLfilter[0] == 0 or xLfilter_toe[0] == 0 or xRfilter[0] == 0 or xRfilter_toe[0] == 0:
        for frames in bulk:
            frames.pop(0)
    while xLfilter[-1] == 0 or xLfilter_toe[-1] == 0 or xRfilter[-1] == 0 or xRfilter_toe[-1] == 0:
        for frames in bulk:
            frames.pop(-1)
        
    return xLfilter, xRfilter, yLfilter, yRfilter, xLfilter_toe, xRfilter_toe, yLfilter_toe, yRfilter_toe


def interpolate_zero(xL, xR, yL, yR):
    xLfilter = deepcopy(xL)
    xRfilter = deepcopy(xR)
    yLfilter = deepcopy(yL)
    yRfilter = deepcopy(yR)
    pair = [(xLfilter, yLfilter), (yLfilter, xLfilter), (xRfilter, yRfilter), (yRfilter, xRfilter)]
    
    for (f0, f1) in pair:
        for i in range(len(f0)-2):
            nextisnot0 = False
            if f0[i+1] == 0:
                n_zero = 0
                for j in range(i+1,len(f0)):
                    if f0[j] == 0:
                        n_zero += 1
                    else:
                        nextisnot0 = True
                        n_region = n_zero+1
                        break
            if nextisnot0:
                stepx = (f0[i+n_region]-f0[i])/n_region
                stepy = (f1[i+n_region]-f1[i])/n_region
                for j in range(n_zero):
                    f0[i+j+1] = f0[i]+(j+1)*stepx
                    f1[i+j+1] = f1[i]+(j+1)*stepy

    tfilter = [i for i in range(len(xLfilter))]

    return xLfilter, xRfilter, yLfilter, yRfilter, tfilter


def median5mean3Filter(x, y):
    x = np.array(x)
    y = np.array(y)
    x_med_arr = np.zeros(x.shape)
    for i in range(len(x)):
        L = max(0, i-2)
        R = min(len(x), i+3)
        xmed = np.median(x[L:R])
        x_med_arr[i] = xmed
        
    x_medmean_arr = np.zeros(x.shape)
    y_medmean_arr = np.zeros(y.shape)
    for i in range(len(x)):
        if (x_med_arr[i] != x[i]):
            L = max(0, i-1)
            R = min(len(x), i+2)
            xmean = np.mean(x_med_arr[L:R])
            ymean = np.mean(y[L:R])
            x_medmean_arr[i] = xmean
            y_medmean_arr[i] = ymean
        else:
            x_medmean_arr[i] = x_med_arr[i]
            y_medmean_arr[i] = y[i]
    
    return x_medmean_arr, y_medmean_arr