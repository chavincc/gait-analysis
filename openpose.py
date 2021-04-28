import subprocess
import os
import json
import glob


def run_openpose(video_source_foldername, video_file_name, video_file_extension, output_foldername):
    if not os.path.exists(output_foldername):
        os.makedirs(output_foldername)
    if not os.path.exists(f"{output_foldername}/{video_file_name}"):
        os.makedirs(f"{output_foldername}/{video_file_name}")
        
    shell_command = f"bin\OpenPoseDemo.exe --video {video_source_foldername}/{video_file_name}.{video_file_extension} --write_video {output_foldername}/{video_file_name}/out.avi --write_json {output_foldername}/{video_file_name}"
    subprocess.call(shell_command, shell=True)


def load_frame(foldername):
    frames = []
    for file in glob.glob(f"result/{foldername}/*.json"):
        with open(file) as f:
            frame = json.load(f)
            frames.append(frame)
    return frames


def load_keypoints(frames, kp_index):
    x = []
    y = []
    for i in range(len(frames)):
        if len(frames[i]['people']) != 0:
            x.append(frames[i]['people'][0]['pose_keypoints_2d'][3*kp_index])
            y.append(frames[i]['people'][0]['pose_keypoints_2d'][3*kp_index + 1])
    return x, y