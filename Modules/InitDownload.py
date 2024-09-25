import os
import zipfile
import urllib.request
import patoolib
import gdown
import pandas as pd
import shutil
from PIL import Image

import configparser
from Resources.Consts import SAVE_PATH


# Coco API
# try:
#     os.system('pip install git+https://github.com/philferriere/cocoapi.git#subdirectory=PythonAPI')
# except Exception as e:
#     print('Error downloading COCO API:', e)


# HRNet from https://github.com/MVIG-SJTU/AlphaPose.git
try:
    if not os.path.exists("Data/Models/HRNet"):
        print("Downloading HRNet...")
        os.system(
            "git clone https://github.com/MVIG-SJTU/AlphaPose.git Data/Models/HRNet"
        )
        print("Done.")
except Exception as e:
    print("Error downloading HRNet:", e)

# get trained model
try:
    if not os.path.exists("Data/Models/HRNet/hrnet_w32_256x192.pth"):
        print("Downloading HRNet model...")
        basePath = os.getcwd()
        os.chdir(basePath + "/Data/Models/HRNet")
        # gdown.download('https://drive.google.com/file/d/1i63BPlOnp2vSjIZ7ni4Yp3RCPQwqe922', 'hrnet_w32_256x192.pth', quiet=False)
        id = "1i63BPlOnp2vSjIZ7ni4Yp3RCPQwqe922"
        gdown.download(id=id, output="pretrained_models/hrnet_w32_256x192.pth")
        os.chdir(basePath)
        print("Done.")
except Exception as e:
    print("Error downloading HRNet model:", e)

# openpose from https://github.com/CMU-Perceptual-Computing-Lab/openpose/releases/download/v1.7.0/openpose-1.7.0-binaries-win64-gpu-python3.7-flir-3d_recommended.zip
try:
    if not os.path.exists("Data/Models/openpose/"):
        print("Downloading OpenPose...")
        os.system(
            "curl -L https://github.com/CMU-Perceptual-Computing-Lab/openpose/releases/download/v1.7.0/openpose-1.7.0-binaries-win64-gpu-python3.7-flir-3d_recommended.zip --output openpose.zip"
        )
        print("Extracting OpenPose...")
        with zipfile.ZipFile("openpose.zip", "r") as zip_ref:
            zip_ref.extractall("./Data/Models/")

        os.remove("openpose.zip")
        os.system(".\Data\Models\openpose\models\getBaseModels.bat")
        print("Done.")
except Exception as e:
    print("Error downloading OpenPose:", e)

# Ultralytics
try:
    if not os.path.exists("Data/Models/ultralytics/"):
        print("Downloading Ultralytics...")
        path = os.getcwd()
        os.system(
            "pip install --target "
            + path
            + "/Data/Models/ultralytics/ ultralytics --no-user --no-deps"
        )
        # add it to path
        os.system("set PYTHONPATH=%PYTHONPATH%;" + path + "/Data/Models/ultralytics/")
        os.system(
            "set PYTHONPATH=%PYTHONPATH%;" + path + "/Data/Models/ultralytics/utils/"
        )
        print("Done.")

        if not os.path.exists("Data/Models/ultralytics/pretrained_models/"):
            os.makedirs("Data/Models/ultralytics/pretrained_models/")

        if not os.path.exists(
            "Data/Models/ultralytics/pretrained_models/yolov8n-pose.pt"
        ):
            print("Downloading Ultralytics model...")
            os.system(
                "curl -L https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n-pose.pt --output Data/Models/ultralytics/pretrained_models/yolov8n-pose.pt"
            )
            os.system(
                "curl -L https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8x-pose-p6.pt --output Data/Models/ultralytics/pretrained_models/yolov8x-pose-p6.pt"
            )
            print("Done.")

except Exception as e:
    print("Error downloading Ultralytics:", e)


# Download coco dataset
cocoPath = "./Data/Datasets/coco-pose/images/"
try:
    if not os.path.exists(cocoPath):
        os.makedirs(cocoPath)
        print("Downloading COCO dataset...")
        urllib.request.urlretrieve(
            "http://images.cocodataset.org/zips/val2017.zip", "val2017.zip"
        )
        print("Extracting COCO dataset...")
        with zipfile.ZipFile("val2017.zip", "r") as zip_ref:
            zip_ref.extractall(cocoPath)
        os.remove("val2017.zip")

        print("Done.")
    else:
        print("COCO dataset already downloaded.")
except Exception as e:
    print("Error downloading COCO dataset:", e)

# move all images from any subdirectories to the root directory
try:
    for root, dirs, files in os.walk(cocoPath):
        for file in files:
            os.rename(os.path.join(root, file), os.path.join(cocoPath, file))
    # remove all subdirectories
    for root, dirs, files in os.walk(cocoPath):
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
except Exception as e:
    print("Error downloading COCO dataset:", e)

# Coco labels
labelsPath = "./Data/Datasets/coco-pose/"
try:
    if not os.path.exists(labelsPath):
        os.makedirs(labelsPath)
        print("Downloading COCO labels...")
        urllib.request.urlretrieve(
            "http://images.cocodataset.org/annotations/annotations_trainval2017.zip",
            "coco2017labels.zip",
        )
        print("Extracting COCO labels...")
        with zipfile.ZipFile("coco2017labels.zip", "r") as zip_ref:
            zip_ref.extractall(labelsPath)
        os.remove("coco2017labels.zip")
        print("Done.")
    else:
        print("COCO labels already downloaded.")
except Exception as e:
    print("Error downloading COCO dataset:", e)

# leave only person_keypoints_val2017.json
try:
    labelsPath += "annotations/"
    for file in os.listdir(labelsPath):
        if file != "person_keypoints_val2017.json":
            os.remove(os.path.join(labelsPath, file))
except Exception as e:
    print("Error downloading COCO dataset:", e)


try:
    # MPII_Leeds images https://datasets.d2.mpi-inf.mpg.de/andriluka14cvpr/mpii_human_pose_v1.tar.gz
    if not os.path.exists("./Data/Datasets/mpii_leeds/images"):
        print("Downloading MPII_Leeds dataset...")
        id = "1_Dk2xqRyJ51OseMSIcG5f4BEnCsNt-fI"
        gdown.download(id=id, output="Human Body Image.rar")
        try:
            patoolib.extract_archive(
                "Human Body Image.rar", outdir="./Data/Datasets/mpii_leeds/images"
            )
        except Exception as e:
            print("Extract failed:", e)
        # move all images to main folder
        for root, dirs, files in os.walk("./Data/Datasets/mpii_leeds/images"):
            for file in files:
                os.rename(
                    os.path.join(root, file),
                    os.path.join("./Data/Datasets/mpii_leeds/images/", file),
                )
        os.remove("Human Body Image.rar")
        # remove all subdirectories
        for root, dirs, files in os.walk("./Data/Datasets/mpii_leeds/images"):
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        print("Done.")
except Exception as e:
    print("Error downloading COCO dataset:", e)


# MPII annotations https://github.com/Arifkhan21/MPII-Dataset-in-CSV/archive/refs/heads/master.zip
try:
    if not os.path.exists("MPII-Dataset-in-CSV-master"):
        print("Downloading MPII annotations...")
        urllib.request.urlretrieve(
            "https://github.com/Arifkhan21/MPII-Dataset-in-CSV/archive/refs/heads/master.zip",
            "mpii_dataset.zip",
        )
        print("Extracting MPII annotations...")
        patoolib.extract_archive("mpii_dataset.zip", outdir="./")
        os.remove("mpii_dataset.zip")
        print("Done.")
except Exception as e:
    print("Error downloading MPII annotations:", e)


# download https://drive.google.com/file/d/1EPFRE507IF7Pc4cVQm9wAjxmnrONDrFS
try:
    if not os.path.exists("./Data/Datasets/mpii_leeds/posetypes"):
        print("Downloading MPII pose types...")
        id = "1EPFRE507IF7Pc4cVQm9wAjxmnrONDrFS"
        gdown.download(id=id, output="label-linux-compress.tar.gz")
        print("Extracting MPII pose types...")
        patoolib.extract_archive(
            "label-linux-compress.tar.gz",
            outdir="./Data/Datasets/mpii_leeds/posetypes/",
        )
        os.remove("label-linux-compress.tar.gz")
        print("Done.")
except Exception as e:
    print("Error downloading MPII pose types:", e)


# download https://drive.google.com/file/d/1KZDNb6B0fZrmlVk2YrJ15Q8thXHjwKGm
try:
    if not os.path.exists("./MPHB-label-txt"):
        print("Downloading MPII image list...")
        id = "1KZDNb6B0fZrmlVk2YrJ15Q8thXHjwKGm"
        gdown.download(id=id, output="MPHB-label-txt.zip")
        print("Extracting MPII image list...")
        with zipfile.ZipFile("MPHB-label-txt.zip", "r") as zip_ref:
            zip_ref.extractall("./")
        os.remove("MPHB-label-txt.zip")
        print("Done.")
except Exception as e:
    print("Error downloading MPII image list:", e)

# download https://datasets.d2.mpi-inf.mpg.de/andriluka14cvpr/mpii_human_pose_v1_u12_2.zip
try:
    if not os.path.exists("./mpii_human_pose_v1_u12_2.zip"):
        print("Downloading MPII mat annotations...")
        urllib.request.urlretrieve(
            "https://datasets.d2.mpi-inf.mpg.de/andriluka14cvpr/mpii_human_pose_v1_u12_2.zip",
            "mpii_human_pose_v1_u12_2.zip",
        )
        print("Extracting MPII mat annotations...")
        patoolib.extract_archive("mpii_human_pose_v1_u12_2.zip", outdir="./")
        os.remove("mpii_human_pose_v1_u12_2.zip")
        print("Done.")
except Exception as e:
    print("Error downloading MPII mat annotations:", e)

# leeds addnotations from https://drive.google.com/file/d/1GZxlTLuMfA3VRvz2jyv8fhJDqElNrgKS/view
try:
    if not os.path.exists("./LEEDS_annotations.json"):
        print("Downloading Leeds dataset...")
        id = "1GZxlTLuMfA3VRvz2jyv8fhJDqElNrgKS"
        gdown.download(id=id, output="LEEDS_annotations.json")
        print("Done.")
except Exception as e:
    print("Error downloading Leeds dataset:", e)

try:
    if not os.path.exists("./Data/Datasets/mpii_leeds/annotations/mpii_dataset.json"):
        # leeds names
        imageDict = {}
        with open("./MPHB-label-txt/MPHB-label.txt", "r") as file:
            dataL = file.readlines()
            for i in range(len(dataL)):
                if dataL[i][:5] == "idx: " and "source: LSP: " == dataL[i + 3][:13]:
                    imageDict[dataL[i + 3][13:-1]] = (dataL[i][5:-1], dataL[i + 2][:-1])

        # open LEEDS_annotations.json
        dfLeeds = pd.read_json("./LEEDS_annotations.json")

        # change img_paths to remove everything before last '/'
        dfLeeds["img_paths"] = dfLeeds["img_paths"].apply(lambda x: x.split("/")[-1])

        # rename fieds in img_paths column matching source in imagelist
        for i in range(dfLeeds.shape[0]):
            if dfLeeds["img_paths"][i] in imageDict:
                dfLeeds.loc[i, "NAME"] = imageDict[dfLeeds["img_paths"][i]][0]
                dfLeeds.loc[i, "bbox"] = imageDict[dfLeeds["img_paths"][i]][1]
            else:
                dfLeeds.drop(i, inplace=True)
                i -= 1

        # convert joint_self to keypoint list

        for i in range(10000, 10000 + dfLeeds.shape[0]):
            keypoint = []
            for j in range(0, 16):
                keypoint.append(dfLeeds["joint_self"][i][j][0])
                keypoint.append(dfLeeds["joint_self"][i][j][1])
                keypoint.append(dfLeeds["joint_self"][i][j][2])
            dfLeeds.loc[[i], "keypoints"] = pd.Series([keypoint], index=[i])

        # MPII names
        imageDict = {}
        with open("./MPHB-label-txt/MPHB-label.txt", "r") as file:
            datam = file.readlines()
            for i in range(len(datam)):
                if datam[i][:5] == "idx: " and "source: MPII: " == datam[i + 3][:14]:
                    imageDict[datam[i + 3][14:-1]] = (datam[i][5:-1], datam[i + 2][:-1])

        import scipy.io

        mat = scipy.io.loadmat("mpii_human_pose_v1_u12_2/mpii_human_pose_v1_u12_1.mat")
        imagesWithOnePerson = {}
        for i in range(len(mat["RELEASE"][0][0][0][0])):
            try:
                if len(mat["RELEASE"][0][0][0][0][i][1][0]) == 1:
                    imagesWithOnePerson[
                        mat["RELEASE"][0][0][0][0][i][0][0][0][0][0]
                    ] = 1
            except:
                pass

        # open MPII
        dfMPII = pd.read_csv("./MPII-Dataset-in-CSV-master/mpii_dataset.csv")

        # remove last two columns and first
        dfMPII = dfMPII.iloc[:, 1:-2]

        # rename fieds in NAME column matching source in imagelist
        for i in range(dfMPII.shape[0]):
            if (dfMPII["NAME"][i] in imageDict) and (
                dfMPII["NAME"][i] in imagesWithOnePerson
            ):
                name, bbox = imageDict[dfMPII["NAME"][i]]
                dfMPII.loc[i, "NAME"] = name
                dfMPII.loc[i, "bbox"] = bbox
            else:
                dfMPII.drop(i, inplace=True)
                i -= 1

        # merge columns r ankle_X	r ankle_Y	r knee_X	r knee_Y	r hip_X	r hip_Y	l hip_X	l hip_Y	l knee_X	...	r elbow_Y	r shoulder_X	r shoulder_Y	l shoulder_X	l shoulder_Y	l elbow_X	l elbow_Y	l wrist_X	l wrist_Y
        # into one column with keypoints
        # add keypoints column
        dfCocoFormat = dfMPII
        for i in range(dfMPII.shape[0]):
            keypoint = []
            for j in range(1, 33, 2):
                keypoint.append(dfMPII.iloc[i, j])
                keypoint.append(dfMPII.iloc[i, j + 1])
                keypoint.append(1)
            index = dfMPII.index[i]
            dfMPII.loc[[index], "keypoints"] = pd.Series([keypoint], index=[index])

        dfLeeds = dfLeeds[["NAME", "keypoints", "bbox"]]
        dfMPII = dfMPII[["NAME", "keypoints", "bbox"]]
        # merge two, leaving only NAME and keypoints columns
        dfLeeds = dfLeeds.rename(columns={"NAME": "img"})
        dfMPII = dfMPII.rename(columns={"NAME": "img"})

        # merge two dataframes
        df = pd.concat([dfLeeds, dfMPII], ignore_index=True)

        # convert to coco format
        # from rankle rknee rhip lhip lknee lankle pelvis thorax upperneck headtop rwrist relbow rshoulder lshoulder lelbow lwrist
        # to nose, left-eye, right-eye, left-ear, right-ear, left-shoulder, right-shoulder, left-elbow, right-elbow, left-wrist, right-wrist, left-hip, right-hip, left-knee, right-knee, left-ankle, right-ankle

        translation = [13, 12, 14, 11, 15, 10, 3, 2, 4, 1, 5, 0]  # from 5 to 16 in coco
        for i in range(df.shape[0]):
            keypoint = df["keypoints"][i]
            new_keypoint = [-1] * 51
            # skip 5 face keypoints
            for j in range(5, 17):
                new_keypoint[3 * j + 0] = keypoint[3 * translation[j - 5] + 0]
                new_keypoint[3 * j + 1] = keypoint[3 * translation[j - 5] + 1]
                new_keypoint[3 * j + 2] = keypoint[3 * translation[j - 5] + 2]
            df.loc[[i], "keypoints"] = pd.Series([new_keypoint], index=[i])

        # change all -1 to 0
        for i in range(df.shape[0]):
            keypoint = df["keypoints"][i]
            for j in range(51):
                if keypoint[j] == -1:
                    keypoint[j] = 0
                    keypoint[j + 1] = 0
                    keypoint[j + 2] = 0
                elif j % 3 == 0 and j < 51:
                    keypoint[j + 2] = 1
            df.loc[[i], "keypoints"] = pd.Series([keypoint], index=[i])

        # remove all images with 0 keypoints
        for i in range(df.shape[0]):
            keypoint = df["keypoints"][i]
            if sum(keypoint) == 0:
                df.drop(i, inplace=True)
                i -= 1

        # convert bbox to list of 4 floats
        for i in range(df.shape[0]):
            bbox = df["bbox"][i]
            bbox = [float(x) for x in bbox.split()]
            df.loc[[i], "bbox"] = pd.Series([bbox], index=[i])

        # convert bbox to coco format [x, y, width, height]
        for i in range(df.shape[0]):
            bbox = df["bbox"][i]
            new_bbox = [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]]
            df.loc[[i], "bbox"] = pd.Series([new_bbox], index=[i])

        # save to ./datasets/mpii/mpii_dataset.csv
        df.to_csv("./Data/Datasets/mpii_leeds/mpii_dataset.csv", index=False)
        # load
        # keypoints as list of ints
        df = pd.read_csv(
            "./Data/Datasets/mpii_leeds/mpii_dataset.csv",
            converters={"keypoints": eval, "bbox": eval},
        )

        # change to coco json
        import json

        data = {}
        data["images"] = []
        data["annotations"] = []

        for i in range(df.shape[0]):
            width = 0
            height = 0
            # fill with 0 left side up to 5
            filename = str(df["img"][i])
            filename = filename.zfill(5) + ".jpg"
            try:
                img = Image.open("./Data/Datasets/mpii_leeds/images/" + filename)
                width = img.size[0]
                height = img.size[1]
                data["images"].append(
                    {
                        "id": int(df["img"][i]),
                        "file_name": str(df["img"][i]) + ".jpg",
                        "width": width,
                        "height": height,
                    }
                )
                num_keypoints = 0
                for j in range(0, 51, 3):
                    if df["keypoints"][i][j + 2] == 1:
                        num_keypoints += 1
                data["annotations"].append(
                    {
                        "image_id": int(df["img"][i]),
                        "id": int(df["img"][i]),
                        "bbox": df["bbox"][i],
                        "keypoints": df["keypoints"][i],
                        "category_id": 0,
                        "num_keypoints": num_keypoints,
                        "iscrowd": 0,
                        "area": df["bbox"][i][2] * df["bbox"][i][3],
                    }
                )
            except:
                pass

        data["categories"] = [
            {
                "supercategory": "person",
                "id": 1,
                "name": "person",
                "keypoints": [
                    "nose",
                    "left_eye",
                    "right_eye",
                    "left_ear",
                    "right_ear",
                    "left_shoulder",
                    "right_shoulder",
                    "left_elbow",
                    "right_elbow",
                    "left_wrist",
                    "right_wrist",
                    "left_hip",
                    "right_hip",
                    "left_knee",
                    "right_knee",
                    "left_ankle",
                    "right_ankle",
                ],
                "skeleton": [
                    [16, 14],
                    [14, 12],
                    [17, 15],
                    [15, 13],
                    [12, 13],
                    [6, 12],
                    [7, 13],
                    [6, 7],
                    [6, 8],
                    [7, 9],
                    [8, 10],
                    [9, 11],
                    [2, 3],
                    [1, 2],
                    [1, 3],
                    [2, 4],
                    [3, 5],
                    [4, 6],
                    [5, 7],
                ],
            }
        ]

        # create
        if not os.path.exists("./Data/Datasets/mpii_leeds/annotations/"):
            os.makedirs("./Data/Datasets/mpii_leeds/annotations/")
        with open("./Data/Datasets/mpii_leeds/annotations/mpii_dataset.json", "w") as f:
            json.dump(data, f, default=str)

        # txt for yolo
        txtPath = os.getcwd() + "/Data/Datasets/mpii_leeds/txtannotations/"
        imagesPath = os.getcwd() + "/Data/Datasets/mpii_leeds/images/"
        if not os.path.exists(txtPath):
            os.makedirs(txtPath)
        with open(txtPath + "yolo.txt", "w") as f:
            for img in os.listdir(imagesPath):
                if int(img[:-4]) in df["img"].values:
                    f.write("./" + img + "\n")
                else:
                    # remove image
                    os.remove(imagesPath + img)

except Exception as e:
    print("Error processing MPII_Leeds data:", e)

# replace all xlsx posetypes with csv
try:
    for root, dirs, files in os.walk("./Data/Datasets/mpii_leeds/posetypes/"):
        for file in files:
            if file.endswith(".xlsx"):
                df = pd.read_excel(
                    os.path.join(root, file), index_col=None, header=None
                )
                df.to_csv(os.path.join(root, file[:-4] + "csv"), index=False)
                os.remove(os.path.join(root, file))
except Exception as e:
    print("Error processing MPII_Leeds data:", e)


# cleanup
try:
    if os.path.exists("MPHB-label-txt"):
        shutil.rmtree("MPHB-label-txt")
    if os.path.exists("mpii_human_pose_v1_u12_2"):
        shutil.rmtree("mpii_human_pose_v1_u12_2")
    if os.path.exists("MPII-Dataset-in-CSV-master"):
        shutil.rmtree("MPII-Dataset-in-CSV-master")
    if os.path.exists("LEEDS_annotations.json"):
        os.remove("LEEDS_annotations.json")

except Exception as e:
    print("Error cleaning up:", e)

config = configparser.ConfigParser()
config.read(SAVE_PATH)
config["DEFAULT"]["downloaded"] = "True"
with open(SAVE_PATH, "w") as configfile:
    config.write(configfile)
