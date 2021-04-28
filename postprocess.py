import numpy as np
import copy


def dilate(arr, width):
    dilatedArr = np.copy(arr)
    
    found_texture = False
    for i in range(len(arr)):
        if arr[i] == 1:
            found_texture = True
        elif arr[i] == 0 and found_texture:
            found_texture = False
            R = min(i+width, len(arr))
            dilatedArr[i:R] = 1
            
    found_texture = False
    for i in range(len(arr)-1, -1, -1):
        if arr[i] == 1:
            found_texture = True
        elif arr[i] == 0 and found_texture:
            found_texture = False
            L = max(0, i-width+1)
            dilatedArr[L: i+1] = 1
            
    return dilatedArr


def erode(arr, width):
    erotedArr = np.copy(arr)
    
    found_texture = False
    for i in range(len(arr)):
        if arr[i] == 0:
            found_texture = True
        elif arr[i] == 1 and found_texture:
            found_texture = False
            R = min(i+width, len(arr))
            erotedArr[i:R] = 0
            
    found_texture = False
    for i in range(len(arr)-1, -1, -1):
        if arr[i] == 0:
            found_texture = True
        elif arr[i] == 1 and found_texture:
            found_texture = False
            L = max(0, i-width+1)
            erotedArr[L: i+1] = 0
            
    return erotedArr


def structure_close(arr, width):
    out = dilate(arr, width)
    out = erode(out, width)
    return out


def structure_open(arr, width):
    out = erode(arr, width)
    out = dilate(out, width)
    return out


def is_multiclass(arr):
    return len(np.unique(np.array(arr))) > 1


def get_stop_phase_label(x_arr, label_arr):
    class_speed = {
        0: [],
        1: []
    }
    for i in range(1, len(label_arr)):
        if label_arr[i] == label_arr[i-1]:
            speed = abs(x_arr[i] - x_arr[i-1])
            class_speed[label_arr[i]].append(speed)
            
    for key in class_speed:
        class_speed[key] = sum(class_speed[key])/len(class_speed[key])
    class_rank = list(class_speed.items())
    class_rank.sort(key = lambda x : x[1])
    
    return class_rank[0][0]


def evaluate_clustering(x_arr, label):
    stop_phase_label = get_stop_phase_label(x_arr, label)
    class_speed = []
    for i in range(len(label)):
        if label[i] == stop_phase_label:
            if i == 0:
                speed = abs(x_arr[i] - x_arr[i+1])
            elif i == len(label) - 1:
                speed = abs(x_arr[i] - x_arr[i-1])
            else:
                speed = abs(x_arr[i] - x_arr[i+1])/2 + abs(x_arr[i] - x_arr[i+1])/2
            class_speed.append(speed)
    
    std = np.std(class_speed)
    return std


def swap_label(x_arr, label, stop_phase_label = 0):
    new_label = copy.deepcopy(label)
    if get_stop_phase_label(x_arr, label) != stop_phase_label:
        for i in range(len(new_label)):
            new_label[i] = int(not bool(new_label[i]))
    return new_label


def pick_clustering(x_arr, label_arr):
    min_score = float('inf')
    min_label = None
    
    for label in label_arr:
        if not is_multiclass(label):
            continue
        score = evaluate_clustering(x_arr, label)
        if score < min_score:
            min_score = score
            min_label = label
    
    return min_label


def get_near_foot(x):
    slope = []
    for i in range(1, len(x)):
        slope.append(x[i] - x[i-1])
    mean_slope = np.mean(slope)
    if mean_slope > 0:
        return 'R'
    else:
        return 'L'


def correct_foot_side(yl, yr, l_bulk, r_bulk, near_foot='R'):
    mean_yl = sum(yl)*-1/len(yl)
    mean_yr = sum(yr)*-1/len(yr)
    if (near_foot == 'R' and mean_yr > mean_yl) or (near_foot == 'L' and mean_yl > mean_yr):
        yl, yr = yr, yl
        l_bulk, r_bulk = r_bulk, l_bulk
    return yl, yr, l_bulk, r_bulk