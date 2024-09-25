import yaml
import os
import shutil
import configparser
import sys
import json
import numpy as np
import torch

from Data.Models.ultralytics.ultralytics import YOLO
from Resources.Consts import *
from Modules.DataLoader import PathLoader


def PredictYolo(config, predict_name):
    model_name = config["SELECTED"]["yolo_model"]
    if model_name == "":
        return
    model = YOLO(YOLO_MODELS_PATH + model_name)

    with open(YOLO_CONFIG_PATH) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)

    with open(YOLO_DATA_CONFIG_PATH) as f:
        data_cfg = yaml.load(f, Loader=yaml.FullLoader)

    data_cfg["path"] = os.getcwd() + DATASETS_PATH + config["SELECTED"]["dataset"]
    cfg["iou"] = float(config["YOLO"]["iou"])
    cfg["conf"] = float(config["YOLO"]["conf"])
    cfg["max_det"] = float(config["YOLO"]["max_det"])
    # save
    with open(YOLO_DATA_CONFIG_PATH, "w") as f:
        yaml.dump(data_cfg, f)

    # Save all images to yolo.txt
    all_image_paths = []
    for root, dirs, files in os.walk(data_cfg["path"]):
        for file in files:
            all_image_paths.append(os.path.join(IMAGE_FOLDER, file))

    with open(data_cfg["path"] + "/" + TXT_ANNOTATIONS_FILE, "w") as f:
        for image_path in all_image_paths:
            f.write("./" + image_path + "\n")
    model.val(cfg=cfg, data=YOLO_DATA_CONFIG_PATH, save_json=True, device="0" if torch.cuda.is_available() else "cpu")
    MovePredsFile(PathLoader.GetAllPredictionsPath(config) + predict_name + ".json")


def MovePredsFile(newPath):
    # get predsPathVal file frin \runs\pose\ newest folder
    predsPathVal = "predictions.json"
    dirs = os.listdir("runs/pose")
    # sort by date
    dirs.sort(key=lambda x: os.path.getmtime("runs/pose/" + x))
    newestDir = dirs[-1]
    file = "runs/pose/" + newestDir + "/" + predsPathVal

    if not os.path.exists(os.path.dirname(newPath)):
        os.makedirs(os.path.dirname(newPath))

    # remove old file if exists
    if os.path.exists(newPath):
        os.remove(newPath)
    os.rename(file, newPath)

    # remove runs/pose folder
    shutil.rmtree("runs/pose")


def PredictOpenPose(config, predict_name):
    # run openpose
    currPath = os.getcwd()
    os.chdir(currPath + OPENPOSE_MODEL_PATH)
    os.system(
        currPath
        + OPENPOSE_MODEL_PATH
        + "bin/OpenPoseDemo.exe --image_dir ../../."
        + PathLoader.GetImagesPath(config)
        + " --net_resolution "
        + config["OPENPOSE"]["net_resolution"]
        + " --scale_number "
        + config["OPENPOSE"]["scale_number"]
        + " --scale_gap "
        + config["OPENPOSE"]["scale_gap"]
        + " --write_json output_jsons/ --display 0 --render_pose 0"
    )
    os.chdir(currPath)
    OpenPoseNormalizeAndSave(
        PathLoader.GetAllPredictionsPath(config) + predict_name + ".json"
    )
    FixCocoPredsOpenPose(
        PathLoader.GetAllPredictionsPath(config) + predict_name + ".json"
    )


def OpenPoseNormalizeKeypoints():
    all_keypoints = []
    outputTempPath = OPENPOSE_MODEL_PATH + "output_jsons/"

    for file in os.listdir(outputTempPath):
        with open(outputTempPath + file) as f:
            data = json.load(f)

        for person in data["people"]:
            keypoints = np.reshape(person["pose_keypoints_2d"], (-1, 3))
            reordered_keypoints = []
            for i in OPENPOSE_KEY_REORDER:
                reordered_keypoints.append(keypoints[i])
            all_keypoints.append(
                {
                    "filename": file.replace("_keypoints.json", ""),
                    "keypoints": reordered_keypoints,
                }
            )

    return all_keypoints


def OpenPoseNormalizeAndSave(path):
    all_keypoints = OpenPoseNormalizeKeypoints()
    # make json serializable
    for keypoints in all_keypoints:
        for i in range(len(keypoints["keypoints"])):
            keypoints["keypoints"][i] = keypoints["keypoints"][i].tolist()
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    with open(path, "w") as f:
        json.dump(all_keypoints, f)


def PredictHRNet(config, predict_name):
    # check if pred file exists
    currPath = os.getcwd()
    if not os.path.exists(currPath + ALPHAPOSE_MODEL_PATH + "demo_inference.py"):\
        # move it up from scripts/demo_inference.py
        shutil.move(currPath + ALPHAPOSE_MODEL_PATH + "scripts/demo_inference.py", currPath + ALPHAPOSE_MODEL_PATH)
    # update conf
    with open(ALPHAPOSE_FULL_CONFIG_PATH) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
        cfg["DETECTOR"]["NMS_THRES"] = config["ALPHAPOSE"]["nms_thres"]
        cfg["DETECTOR"]["CONFIDENCE"] = config["ALPHAPOSE"]["confidence"]

    with open(ALPHAPOSE_FULL_CONFIG_PATH, "w") as f:
        yaml.dump(cfg, f)

    os.chdir(currPath + ALPHAPOSE_MODEL_PATH)
    os.system(
        "python demo_inference.py --cfg "
        + ALPHAPOSE_CONFIG_PATH
        + " --checkpoint ./pretrained_models/"
        + config["SELECTED"]["alphapose_model"]
        + " --indir  ../../."
        + PathLoader.GetImagesPath(config)
        + " --outdir ./out"
    )
    os.chdir(currPath)
    os.rename(
        ALPHAPOSE_MODEL_PATH + "out/alphapose-results.json",
        PathLoader.GetAllPredictionsPath(config) + predict_name + ".json",
    )
    FixCocoPredsHRNet(PathLoader.GetAllPredictionsPath(config) + predict_name + ".json")


def FixCocoPredsHRNet(predsPath):  # hrnet
    with open(predsPath) as json_file:
        preds = json.load(json_file)
    # add image_id
    for i in range(len(preds)):
        preds[i]["image_id"] = preds[i]["image_id"].split(".")[0].lstrip("0")
        # convert to int
        preds[i]["image_id"] = int(preds[i]["image_id"])
        preds[i]["category_id"] = 0
    # save
    with open(predsPath, "w") as outfile:
        json.dump(preds, outfile)


def FixCocoPredsOpenPose(predsPath):  # yolo and openpose
    with open(predsPath) as json_file:
        preds = json.load(json_file)
    # add image_id
    newPreds = []
    for i in range(len(preds)):
        preds[i]["image_id"] = preds[i]["filename"].split(".")[0].lstrip("0")
        # convert to int
        preds[i]["image_id"] = int(preds[i]["image_id"])
        # category
        preds[i]["category_id"] = 0
        # score
        if "score" not in preds[i]:
            # set score to average of scrore from all points
            score = 0
            nonzeroScore = 0
            for j in range(len(preds[i]["keypoints"])):
                if preds[i]["keypoints"][j][2] < 0.1:
                    preds[i]["keypoints"][j] = [0, 0, 0]
                if preds[i]["keypoints"][j][2] > 0:
                    nonzeroScore += 1
                score += preds[i]["keypoints"][j][2]

            # fill keypoints to size 3
            for j in range(len(preds[i]["keypoints"])):
                if len(preds[i]["keypoints"][j]) == 2:
                    preds[i]["keypoints"][j].append(0)

            # reshape to lists with 51x1 elements
            preds[i]["keypoints"] = np.reshape(preds[i]["keypoints"], (-1, 51)).tolist()

            # for each keypoint add a copy to newPreds
            # predEntry = []
            for j in range(len(preds[i]["keypoints"])):
                # if it's not all 0s
                if np.sum(preds[i]["keypoints"][j]) > 0:
                    newPreds.append(preds[i].copy())
                    newPreds[-1]["keypoints"] = preds[i]["keypoints"][j]
                    newPreds[-1]["id"] = i * 100 + j
            # if nonzeroScore > 0:
            score /= 17
            newPreds[-1]["score"] = score
            # remove is score is 0
            if score == 0:
                newPreds.pop()

    # save
    with open(predsPath, "w") as outfile:
        json.dump(newPreds, outfile)


def Reindex(keypoints):
    reindex = [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15]
    # reindex = [16, 15, 14, 13, 12, 11, 10, 9, 8, 7 ,6, 5, 4, 3, 2, 1, 0]
    newKeypoints = []
    for k in reindex:
        newKeypoints.append(keypoints[k])
    return newKeypoints


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(SAVE_PATH)

    model_type = config["SELECTED"]["model_type"]
    if model_type == MODEL_TYPES[0]:
        PredictYolo(config, str(sys.argv[1]))
    elif model_type == MODEL_TYPES[1]:
        PredictOpenPose(config, str(sys.argv[1]))
    elif model_type == MODEL_TYPES[2]:
        PredictHRNet(config, str(sys.argv[1]))
