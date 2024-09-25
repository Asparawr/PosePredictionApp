WIDTH = 1600
HEIGHT = 900

MODEL_TYPES = ["YoloPose", "OpenPose", "AlphaPose-HRNet"]

SAVE_PATH = "./Resources/config.ini"
YOLO_CONFIG_PATH = "./Resources/YoloConfig.yaml"
YOLO_DATA_CONFIG_PATH = "./Resources/YoloDataConfig.yaml"

DATASETS_PATH = "./Data/Datasets/"
MODELS_PATH = "./Data/Models/"
PREDICTIONS_PATH = "/Predictions/"
EVALUATIONS_PATH = "/Evaluations/"

IMAGE_FOLDER = "images/"
LABELS_FOLDER = "labels/"
ANNOTATION_FOLDER = "annotations/"
POSETYPES_FOLDER = "posetypes/"
TXT_ANNOTATIONS_FILE = "yolo.txt"

YOLO_MODEL_PATH = "./Data/Models/ultralytics/"
ALPHAPOSE_MODEL_PATH = "./Data/Models/HRNet/"
OPENPOSE_MODEL_PATH = "./Data/Models/openpose/"
ALPHAPOSE_CONFIG_PATH = "configs/coco/hrnet/256x192_w32_lr1e-3.yaml"
ALPHAPOSE_FULL_CONFIG_PATH = ALPHAPOSE_MODEL_PATH + ALPHAPOSE_CONFIG_PATH

YOLO_MODELS_PATH = YOLO_MODEL_PATH + "pretrained_models/"
ALPHAPOSE_MODELS_PATH = ALPHAPOSE_MODEL_PATH + "pretrained_models/"
OPENPOSE_MODELS = ["BODY_25", "COCO", "MPII", "HAND", "FACE"]

TEMP_IMAGE_PATH = "./Data/temp.jpg"
TEMP_COMPARE_PATH = "./Data/tempCompare.png"
TEMP_COMPARE_CSV_PATH = "./Data/tempCompare.csv"

COMPARE_TYPES = ["Whole", "By keypoints", "By type"]
AP_TYPES = {"AP50:90": 0, "AP50": 1, "AP75": 2, "APM50:95": 3, "APL50:95": 4}
AR_TYPES = {"AR50:90": 5, "AR50": 6, "AR75": 7, "ARM50:95": 8, "ARL50:95": 9}

SKELETON = [
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
]
KEYPOINTS = {
    "Nose": 0,
    "Left eye": 1,
    "Right eye": 2,
    "Left ear": 3,
    "Right ear": 4,
    "Left shoulder": 5,
    "Right shoulder": 6,
    "Left elbow": 7,
    "Right elbow": 8,
    "Left wrist": 9,
    "Right wrist": 10,
    "Left hip": 11,
    "Right hip": 12,
    "Left knee": 13,
    "Right knee": 14,
    "Left ankle": 15,
    "Right ankle": 16,
}
OPENPOSE_KEY_REORDER = [0, 16, 15, 18, 17, 5, 2, 6, 3, 7, 4, 12, 9, 13, 10, 14, 11]
