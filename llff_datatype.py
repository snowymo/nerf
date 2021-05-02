import numpy as np
import json
import math

def fov2length(angle):
    return math.tan(math.radians(angle) / 2) * 2

def _convert_camera_params(input_camera_params,
                           view_res):
    """
    Check and convert camera parameters in config file to pixel-space

    :param cam_params: { ["fx", "fy" | "fov"], "cx", "cy", ["normalized"] },
        the parameters of camera
    :return: camera parameters
    """
    input_is_normalized = bool(input_camera_params.get('normalized'))
    camera_params = {}
    if 'fov' in input_camera_params:
        if input_is_normalized:
            camera_params['fy'] = 1 / fov2length(input_camera_params['fov'])
            camera_params['fx'] = camera_params['fy'] / view_res["y"] * view_res["x"]
        else:
            camera_params['fx'] = camera_params['fy'] = view_res["x"] / \
                                                        fov2length(input_camera_params['fov'])
        camera_params['fy'] *= -1
    else:
        camera_params['fx'] = input_camera_params['fx']
        camera_params['fy'] = input_camera_params['fy']
    camera_params['cx'] = input_camera_params['cx']
    camera_params['cy'] = input_camera_params['cy']
    if input_is_normalized:
        camera_params['fx'] *= view_res["y"]
        camera_params['fy'] *= view_res["x"]
        camera_params['cx'] *= view_res["y"]
        camera_params['cy'] *= view_res["x"]
    return camera_params

def load_pose_json(filename,near,far):
    info = None
    with open(filename, encoding='utf-8') as file:
        info = json.loads(file.read())
    poses = []
    for i in range(len(info["view_centers"])):
        pose = np.zeros((3, 5), dtype=np.float32)
        Rt = np.eye(4, dtype=np.float32)
        if len(info["view_rots"][i]) == 9:
            for j in range(9):
                Rt[j // 3, j % 3] = info["view_rots"][i][j]
        #     right up backward -> down right backward
            temp = Rt[:,0]
            Rt[:,0] = Rt[:,1]
            Rt[:,1] = temp
            Rt[1,0] *= -1
        elif len(info["view_rots"][i]) == 2:
            Rt[1, 1] = math.cos(math.radians(info["view_rots"][i][0]))
            Rt[2, 1] = math.sin(math.radians(info["view_rots"][i][0]))
            Rt[1, 2] = -Rt[2,1]
            Rt[2, 2] = Rt[1,1]
            #     flip rots row3 and col3
            Rt[2] *= -1
            Rt[:, 2] *= -1
        for j in range(3):
            Rt[j, 3] = info["view_centers"][i][j]
        # Rt = np.linalg.inv(Rt)
        Rt = Rt[:3,:4]
        Rt = np.concatenate([-Rt[:, 1:2], Rt[:, 0:1], -Rt[:, 2:3], Rt[:,3:4]],1)

        # OGL to DX coordinate
        if len(info["view_rots"][i]) == 2:
            #     flip fy
            # cam_par["fy"] *= -1
            #     flip view center z
            Rt[2, 3] *= -1

        pose[0,:4] = Rt[0]
        pose[1,:4] = Rt[2]
        pose[2,:4] = Rt[1]
        
        pose[0, 4] = info["view_res"]["x"]
        pose[1, 4] = info["view_res"]["y"]
        # print(info["view_res"])
        if "fx" in info["cam_params"]:
            pose[2, 4] = info["cam_params"]["fx"]
        else:
            cam_par = _convert_camera_params(info["cam_params"],info["view_res"])
            # print("cam_par", cam_par)
            pose[2,4] = cam_par["fx"]
        # OGL to DX coordinate
        if len(info["view_rots"][i]) == 2:
            #     flip fy
            cam_par["fy"] *= -1
        pose = pose.flatten()
        pose = np.concatenate((pose, [near,far])) 
        ## better to know the near and far plane from Unity-DengNianchen. 
        ## Hard to understand the exact meaning (the depth bound of scene geometry as I can see)
        # print(pose.shape)
        poses.append(pose) 
    poses = np.stack(poses)
    
    print(poses.shape)
    return poses

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('train_json', type=str,
                    help='input training set info')
parser.add_argument('near', type=float,
                    help='scene depth range near')
parser.add_argument('far', type=float,
                    help='scene depth range far')
args = parser.parse_args()

if __name__ == "__main__":
    jsonfile = args.train_json
    near = args.near
    far = args.far
    poses = load_pose_json(jsonfile,near,far)
    np.save(args.train_json+"poses_bounds.npy", poses)