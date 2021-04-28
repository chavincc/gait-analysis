import cv2
import pandas as pd
import numpy as np


def extract_phase_transition(x_arr, y_arr, label, leg, joint):
    out = []
    for i in range(1, len(label)):
        if label[i-1] != label[i]:
            phase = 'place' if label[i] == 0 else 'lift'
            out.append({
                'frame': i,
                'leg': leg,
                'phase': phase,
                'Ximage': x_arr[i],
                'Yimage': y_arr[i],
                'joint': joint
            })
    return out


def detect_chessboard(filename, MATLAB, square_size):
    cap = cv2.VideoCapture(f'result/{filename}/out.avi')
    _, background = cap.read()
    gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('temp/detection.jpg', gray)
    result = MATLAB.detectChessBoard(square_size, 'temp/detection.jpg')
    return result


def get_line(x1, y1, x2, y2):
    m = (y2-y1)/(x2-x1)
    c1 = y1 - m*x1
    c2 = y2 - m*x2
    c = np.mean([c1, c2])
    return m, c


def line_point_compare(x, y, m, c):
    # 0  => point intersect with line
    # -1 => point on the left region of line (image-vise)
    # 1  => point on the right region of line (image-vise)
    if y == m*x + c:
        return 0
    elif y < m*x + c:
        if m > 0:
            return 1
        else:
            return -1
    else:
        if m > 0:
            return -1
        else:
            return 1


def get_chessboard_corner(square_size):
    board_size = pd.read_csv('temp/boardSize.csv')
    ax1 = int(board_size['x'][0]) - 1
    ax2 = int(board_size['y'][0]) - 1

    ip = pd.read_csv('temp/ip.csv')
    xl = list(ip['x'])
    yl = list(ip['y'])

    corners = [
        (xl[0], yl[0]),
        (xl[ax1-1], yl[ax1-1]),
        (xl[ax1*(ax2-1)], yl[ax1*(ax2-1)]),
        (xl[ax1*ax2 - 1], yl[ax1*ax2 - 1])
    ]
    corners.sort(key = lambda x : x[0])
    
    walkway_distance = square_size*(max(ax1, ax2)-1)

    return corners, walkway_distance


def get_left_right_line(corners):
    left_line = get_line(corners[0][0], corners[0][1], corners[1][0], corners[1][1])
    right_line = get_line(corners[2][0], corners[2][1], corners[3][0], corners[3][1])  
    return left_line, right_line


def trim_phase_transition(phase_transition, start_line, finish_line, near_foot):
    start_frame = phase_transition[0]['frame']
    finish_frame = phase_transition[-1]['frame']

    for pt in phase_transition:
        x = pt['Ximage']
        y = pt['Yimage']
        if near_foot == 'R':
            cross_start = line_point_compare(x, y, start_line[0], start_line[1]) >= 0
        elif near_foot == 'L':
            cross_start = line_point_compare(x, y, start_line[0], start_line[1]) <= 0
        if cross_start:
            start_frame = pt['frame']
            break
    
    for pt in phase_transition:
        x = pt['Ximage']
        y = pt['Yimage']
        if near_foot == 'R':
            cross_finish = line_point_compare(x, y, finish_line[0], finish_line[1]) >= 0
        elif near_foot == 'L':
            cross_finish = line_point_compare(x, y, finish_line[0], finish_line[1]) <= 0
        if cross_finish:
            finish_frame = pt['frame']
            break

    phase_transition = list(filter(lambda x : start_frame <= x['frame'] <= finish_frame, phase_transition))
    return phase_transition


def get_direction_calibration(phase_transition, MATLAB):
    x1 = int(phase_transition[0]['Ximage'])
    y1 = int(phase_transition[0]['Yimage'])
    x2 = int(phase_transition[-1]['Ximage'])
    y2 = int(phase_transition[-1]['Yimage'])
    distance = get_distance(x1, y1, x2, y2, MATLAB, option='x')
    if distance >= 0:
        multiplier = 1
    else:
        multiplier = -1
        
    return multiplier


def getfps(filename):
    cap=cv2.VideoCapture(f"result/{filename}/out.avi")
    fps = cap.get(cv2.CAP_PROP_FPS)
    return fps


def get_distance(x1, y1, x2, y2, MATLAB, option='default'):
    if option == 'default':
        option = 0
    elif option == 'x':
        option = 1
    elif option == 'y':
        option = 2
    else:
        raise Exception('invalid option')
    distance = MATLAB.measure(x1, y1, x2, y2, option)
    return distance


def get_walking_speed(phase_transition, fps, walkway_distance):
    start_frame = phase_transition[0]['frame']
    finish_frame = phase_transition[-1]['frame']
    speed = (walkway_distance/1000)/((finish_frame - start_frame)/fps)
    return speed


def get_cadence(phase_transition, fps):
    step = []
    for item in phase_transition:
        if item['phase'] == 'place' and item['joint'] == 'heel':
            step.append(item)
    
    n_step = len(step) - 1
    total_time = (step[-1]['frame'] - step[0]['frame'])/fps
    cadence = n_step*60/total_time
    
    return cadence


def get_step_info(phase_transition, fps, MATLAB):
    step = []
    for item in phase_transition:
        if item['phase'] == 'place' and item['joint'] == 'heel':
            step.append(item)
    
    direction_multiplier = get_direction_calibration(phase_transition, MATLAB)

    L_step_length = []
    L_step_time = []
    R_step_length = []
    R_step_time = []
    for i in range(len(step) - 1):
        x1 = int(step[i]['Ximage'])
        y1 = int(step[i]['Yimage'])
        x2 = int(step[i+1]['Ximage'])
        y2 = int(step[i+1]['Yimage'])
        distance = get_distance(x1, y1, x2, y2, MATLAB, option='x') * direction_multiplier
        time = (step[i+1]['frame'] - step[i]['frame'])/fps
        if step[i+1]['leg'] == 'L' and step[i]['leg'] == 'R':
            L_step_length.append(distance)
            L_step_time.append(time)
        elif step[i+1]['leg'] == 'R' and step[i]['leg'] == 'L':
            R_step_length.append(distance)
            R_step_time.append(time)
            
    L_mean = np.mean(L_step_length)/10
    R_mean = np.mean(R_step_length)/10
    L_mean_time = np.mean(L_step_time)
    R_mean_time = np.mean(R_step_time)
    
    return L_mean, R_mean, L_mean_time, R_mean_time


def get_stride_info(phase_transition, fps, MATLAB):
    L_step = []
    R_step = []
    for item in phase_transition:
        if item['phase'] == 'place' and item['joint'] == 'heel':
            if item['leg'] == 'L':
                L_step.append(item)
            if item['leg'] == 'R':
                R_step.append(item)
    
    L_stride_length = []
    R_stride_length = []
    L_stride_time = []
    R_stride_time = []
    for i in range(len(L_step) - 1):
        x1 = int(L_step[i]['Ximage'])
        y1 = int(L_step[i]['Yimage'])
        x2 = int(L_step[i+1]['Ximage'])
        y2 = int(L_step[i+1]['Yimage'])
        distance = get_distance(x1, y1, x2, y2, MATLAB, option='default')
        time = (L_step[i+1]['frame'] - L_step[i]['frame'])/fps
        L_stride_length.append(distance)
        L_stride_time.append(time)
    for i in range(len(R_step) - 1):
        x1 = int(R_step[i]['Ximage'])
        y1 = int(R_step[i]['Yimage'])
        x2 = int(R_step[i+1]['Ximage'])
        y2 = int(R_step[i+1]['Yimage'])
        distance = get_distance(x1, y1, x2, y2, MATLAB, option='default')
        time = (R_step[i+1]['frame'] - R_step[i]['frame'])/fps
        R_stride_length.append(distance)
        R_stride_time.append(time)
        
    L_mean = np.mean(L_stride_length)/10
    R_mean = np.mean(R_stride_length)/10
    L_mean_time = np.mean(L_stride_time)
    R_mean_time = np.mean(R_stride_time)
    
    return L_mean, R_mean, L_mean_time, R_mean_time


def get_step_width(phase_transition, MATLAB):
    step = []
    for item in phase_transition:
        if item['phase'] == 'place' and item['joint'] == 'heel':
            step.append(item)
    
    step_width = []
    for i in range(len(step) - 1):
        x1 = int(step[i]['Ximage'])
        y1 = int(step[i]['Yimage'])
        x2 = int(step[i+1]['Ximage'])
        y2 = int(step[i+1]['Yimage'])
        distance = get_distance(x1, y1, x2, y2, MATLAB, option='y')
        step_width.append(distance)
            
    width_mean = np.mean(np.abs(step_width))/10
    
    return width_mean


def get_phase_duration(phase_transition, fps):
    L_step = []
    R_step = []
    for item in phase_transition:
        if (item['joint'] == 'toe' and item['phase'] == 'lift') or (item['joint'] == 'heel' and item['phase'] == 'place'):
            if item['leg'] == 'L':
                L_step.append(item)
            if item['leg'] == 'R':
                R_step.append(item)
                
    L_stance = []
    L_swing = []
    R_stance = []
    R_swing = []
    for i in range(len(L_step)-1):
        if L_step[i]['phase'] == 'lift' and L_step[i+1]['phase'] == 'place':
            time = (L_step[i+1]['frame'] - L_step[i]['frame'])/fps
            L_swing.append(time)
        elif L_step[i]['phase'] == 'place' and L_step[i+1]['phase'] == 'lift':
            time = (L_step[i+1]['frame'] - L_step[i]['frame'])/fps
            L_stance.append(time)      
    for i in range(len(R_step)-1):
        if R_step[i]['phase'] == 'lift' and R_step[i+1]['phase'] == 'place':
            time = (R_step[i+1]['frame'] - R_step[i]['frame'])/fps
            R_swing.append(time)
        elif R_step[i]['phase'] == 'place' and R_step[i+1]['phase'] == 'lift':
            time = (R_step[i+1]['frame'] - R_step[i]['frame'])/fps
            R_stance.append(time)
    
    L_stance_mean = np.mean(L_stance)
    L_swing_mean = np.mean(L_swing)
    R_stance_mean = np.mean(R_stance)
    R_swing_mean = np.mean(R_swing)
    
    L_cycle_duration = L_stance_mean + L_swing_mean
    R_cycle_duration = R_stance_mean + R_swing_mean
    cycle_duration = (L_cycle_duration + R_cycle_duration)/2
    L_stance_percentage = L_stance_mean*100/L_cycle_duration
    L_swing_percentage = 100 - L_stance_percentage
    R_stance_percentage = R_stance_mean*100/R_cycle_duration
    R_swing_percentage = 100 - R_stance_percentage
    
    return cycle_duration, L_stance_mean, L_swing_mean, L_cycle_duration, L_stance_percentage, L_swing_percentage,\
            R_stance_mean, R_swing_mean, R_cycle_duration, R_stance_percentage, R_swing_percentage


def get_support_duration(phase_transition, fps):
    step = []
    for item in phase_transition:
        if (item['joint'] == 'toe' and item['phase'] == 'lift') or (item['joint'] == 'heel' and item['phase'] == 'place'):
            step.append(item)
            
    while step[0]['phase'] == 'lift':
        step.pop(0)
    while step[-1]['phase'] == 'place':
        step.pop(-1)
        
    L_double_initial = []
    R_double_initial = []
    L_single = []
    R_single = []
    for i in range(len(step)-1):
        time = (step[i+1]['frame'] - step[i]['frame'])/fps
        if step[i]['phase'] == 'place' and step[i+1]['phase'] == 'lift':
            if step[i]['leg'] == 'L':
                L_double_initial.append(time)
            else:
                R_double_initial.append(time)
        elif step[i]['phase'] == 'lift' and step[i+1]['phase'] == 'place':
            if step[i]['leg'] == 'L':
                R_single.append(time)
            else:
                L_single.append(time)
    
    L_double_initial_mean = np.mean(L_double_initial)
    R_double_initial_mean = np.mean(R_double_initial)
    L_single_mean = np.mean(L_single)
    R_single_mean = np.mean(R_single)
    
    cycle_time = sum([L_double_initial_mean, R_double_initial_mean, L_single_mean, R_single_mean])
    L_double_initial_percentage = L_double_initial_mean * 100 / cycle_time
    R_double_initial_percentage = R_double_initial_mean * 100 / cycle_time
    L_single_percentage = L_single_mean * 100 / cycle_time
    R_single_percentage = R_single_mean * 100 / cycle_time
    
    return L_double_initial_mean, L_single_mean, L_double_initial_percentage, L_single_percentage, R_double_initial_mean,\
            R_single_mean, R_double_initial_percentage, R_single_percentage