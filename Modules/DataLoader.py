import os
from tkinter import filedialog
import shutil
import json

from Modules.Events import EventManager
from Resources.Consts import *
from Widgets.Popups import BaseOkPopup
from Modules.Translate import TranslateManager


class PathLoader:
    @staticmethod
    def GetEvaluationsPath(config):
        dataset = DATASETS_PATH + config["SELECTED"]["dataset"]
        model_type = config["SELECTED"]["model_type"]
        model = config["SELECTED"]["current_model"]
        path = dataset + EVALUATIONS_PATH + model_type + "/" + model + "/"

        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def GetAllPredictionsPath(config):
        dataset = DATASETS_PATH + config["SELECTED"]["dataset"]
        model_type = config["SELECTED"]["model_type"]
        model = config["SELECTED"]["current_model"]
        path = dataset + PREDICTIONS_PATH + model_type + "/" + model + "/"

        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def GetPredictionPath(config):
        prediction = config["SELECTED"]["prediction"]
        path = PathLoader.GetAllPredictionsPath(config)

        return path + "/" + prediction

    @staticmethod
    def GetAnnotationsPath(config):
        dataset = config["SELECTED"]["dataset"]
        annotations = config["SELECTED"]["annotations"]
        path = DATASETS_PATH + dataset + "/" + ANNOTATION_FOLDER

        if not os.path.exists(path):
            os.makedirs(path)
        return path + annotations

    @staticmethod
    def GetImagesPath(config):
        dataset = config["SELECTED"]["dataset"]
        path = DATASETS_PATH + dataset + "/" + IMAGE_FOLDER

        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def GetPoseTypesPath(config):
        dataset = config["SELECTED"]["dataset"]
        path = DATASETS_PATH + dataset + "/" + POSETYPES_FOLDER

        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def GetCompareEvaluationsPath(config):
        dataset = config["COMPARE"]["dataset"]
        path = DATASETS_PATH + dataset + EVALUATIONS_PATH

        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def GetPoseTypesPath(config):
        dataset = config["SELECTED"]["dataset"]
        path = DATASETS_PATH + dataset + "/" + POSETYPES_FOLDER

        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def GetComparePoseTypesPath(config):
        dataset = config["COMPARE"]["dataset"]
        path = DATASETS_PATH + dataset + "/" + POSETYPES_FOLDER

        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def GetComparePoseTypesPath(config):
        dataset = config["COMPARE"]["dataset"]
        path = DATASETS_PATH + dataset + "/" + POSETYPES_FOLDER

        if not os.path.exists(path):
            os.makedirs(path)
        return path


class ImageLoader:
    @staticmethod
    def GetAllImagesInFolder(folder):
        images = []
        for file in os.listdir(folder):
            path = os.path.join(folder, file)
            if os.path.isfile(path):
                images.append(file)
        return images

    @staticmethod
    def CountAllImagesInFolder(folder):
        return len(os.listdir(folder))

    @staticmethod
    def AddImagesFromZip(app, zip_path, dataset_name):
        try:
            image_path = os.path.join(DATASETS_PATH, dataset_name + "/" + IMAGE_FOLDER)
            # Unzip to dataset folder
            shutil.unpack_archive(zip_path, image_path)
            # Move all images to main folder
            for root, dirs, files in os.walk(image_path):
                for file in files:
                    # remove if file is not image
                    if not file.lower().endswith((".png", ".jpg", ".jpeg")):
                        os.remove(os.path.join(root, file))
                        pass

                    # pass if already in main folder
                    if root == image_path:
                        continue

                    # remove if exists
                    if os.path.exists(os.path.join(image_path, file)):
                        os.remove(os.path.join(image_path, file))

                    shutil.move(
                        os.path.join(root, file),
                        image_path,
                    )
            # clear all subfolders
            for root, dirs, files in os.walk(image_path):
                for dir in dirs:
                    shutil.rmtree(os.path.join(root, dir))
        except Exception as e:
            # Show fail popup
            BaseOkPopup(
                app,
                app,
                TranslateManager.Translate("Error"),
                TranslateManager.Translate("Failed to load images from zip file"),
            )
            return

        BaseOkPopup(
            app,
            app,
            TranslateManager.Translate("Success"),
            TranslateManager.Translate("Images loaded successfully"),
        )
        EventManager.set_dataset_event()

    @staticmethod
    def ClearImages(app, dataset_name):
        image_path = os.path.join(DATASETS_PATH, dataset_name + "/" + IMAGE_FOLDER)
        for root, dirs, files in os.walk(image_path):
            for file in files:
                os.remove(os.path.join(root, file))
        BaseOkPopup(
            app,
            app,
            TranslateManager.Translate("Success"),
            TranslateManager.Translate("Images cleared successfully"),
        )

    @staticmethod
    def SaveCurrentImage():
        file = filedialog.asksaveasfilename(
            title="Save Image",
            filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg")],
        )
        if file == "":
            return
        if not file.lower().endswith((".png", ".jpg")):
            file += ".png"

        shutil.copyfile(TEMP_IMAGE_PATH, file)

    @staticmethod
    def SaveCurrentTableImage():
        file = filedialog.asksaveasfilename(
            title="Save Image",
            filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg")],
        )
        if file == "":
            return
        if not file.lower().endswith((".png", ".jpg")):
            file += ".png"

        shutil.copyfile(TEMP_COMPARE_PATH, file)

    @staticmethod
    def SaveCurrentTableCsv():
        file = filedialog.asksaveasfilename(
            title="Save Image",
            filetypes=[("CSV files", "*.csv")],
        )
        if file == "":
            return
        if not file.lower().endswith((".csv")):
            file += ".csv"

        shutil.copyfile(TEMP_COMPARE_CSV_PATH, file)


class AnnotationsLoader:
    @staticmethod
    def AddAnnotationJson(app, dataset_name):
        try:
            annotation_path = os.path.join(
                DATASETS_PATH, dataset_name + "/annotations/"
            )
            if not os.path.exists(annotation_path):
                os.makedirs(annotation_path)
            file_path = filedialog.askopenfilename(
                initialdir=DATASETS_PATH,
                title="Select file",
                filetypes=[("JSON files", "*.json")],
            )
            if file_path == "":
                return
            # check if json is in coco format
            with open(file_path) as f:
                data = json.load(f)
                if (
                    "images" not in data
                    or "annotations" not in data
                    or "categories" not in data
                ):
                    BaseOkPopup(
                        app,
                        app,
                        TranslateManager.Translate("Error"),
                        TranslateManager.Translate("JSON file is not in COCO format"),
                    )
                    return

            shutil.copy(file_path, annotation_path)
        except Exception as e:
            # Show fail popup
            BaseOkPopup(
                app,
                app,
                TranslateManager.Translate("Error"),
                TranslateManager.Translate("Failed to load annotations from json file"),
            )
            return

        BaseOkPopup(
            app,
            app,
            TranslateManager.Translate("Success"),
            TranslateManager.Translate("Annotations added successfully"),
        )
        return file_path.split("/")[-1]


class PoseTypeLoader:
    @staticmethod
    def AddPoseTypeCsv(app, dataset_name):
        try:
            posetype_path = os.path.join(DATASETS_PATH, dataset_name + "/posetypes/")
            if not os.path.exists(posetype_path):
                os.makedirs(posetype_path)
            file_path = filedialog.askopenfilename(
                initialdir=DATASETS_PATH,
                title="Select file",
                filetypes=[("CSV files", "*.csv")],
            )
            if file_path == "":
                return
            # check if it's a csv with one column
            with open(file_path) as f:
                data = f.read()
                if len(data.split("\n")[0].split(",")) != 1:
                    BaseOkPopup(
                        app,
                        app,
                        TranslateManager.Translate("Error"),
                        TranslateManager.Translate("CSV file must have one column"),
                    )
                    return
            shutil.copy(file_path, posetype_path)
        except Exception as e:
            # Show fail popup
            BaseOkPopup(
                app,
                app,
                TranslateManager.Translate("Error"),
                TranslateManager.Translate("Failed to load posetypes from csv file"),
            )
            return

        BaseOkPopup(
            app,
            app,
            TranslateManager.Translate("Success"),
            TranslateManager.Translate("Posetypes added successfully"),
        )
        return file_path.split("/")[-1]


class ModelLoader:
    @staticmethod
    def AddYoloModel(app):
        try:
            model_path = os.path.join(YOLO_MODELS_PATH)
            if not os.path.exists(model_path):
                os.makedirs(model_path)
            file_path = filedialog.askopenfilename(
                initialdir=DATASETS_PATH,
                title="Select file",
                filetypes=[("Yolo files", "*.pt")],
            )
            if file_path == "":
                return
            shutil.copy(file_path, model_path)
        except Exception as e:
            # Show fail popup
            BaseOkPopup(
                app,
                app,
                TranslateManager.Translate("Error"),
                TranslateManager.Translate("Failed to load model file"),
            )
            return

        BaseOkPopup(
            app,
            app,
            TranslateManager.Translate("Success"),
            TranslateManager.Translate("Model added successfully"),
        )
        return file_path.split("/")[-1]

    @staticmethod
    def DeleteYoloModel(app, model_name):
        try:
            model_path = os.path.join(YOLO_MODELS_PATH, model_name)
            if os.path.exists(model_path):
                os.remove(model_path)
        except Exception as e:
            # Show fail popup
            BaseOkPopup(
                app,
                app,
                TranslateManager.Translate("Error"),
                TranslateManager.Translate("Failed to delete model file"),
            )
            return

        BaseOkPopup(
            app,
            app,
            TranslateManager.Translate("Success"),
            TranslateManager.Translate("Model deleted successfully"),
        )
        return model_name

    @staticmethod
    def AddHRNetModel(app):
        try:
            model_path = os.path.join(ALPHAPOSE_MODELS_PATH)
            if not os.path.exists(model_path):
                os.makedirs(model_path)
            file_path = filedialog.askopenfilename(
                initialdir=DATASETS_PATH,
                title="Select file",
                filetypes=[("HRNet files", "*.pth")],
            )
            if file_path == "":
                return
            shutil.copy(file_path, model_path)
        except Exception as e:
            # Show fail popup
            BaseOkPopup(
                app,
                app,
                TranslateManager.Translate("Error"),
                TranslateManager.Translate("Failed to load model file"),
            )
            return

        BaseOkPopup(
            app,
            app,
            TranslateManager.Translate("Success"),
            TranslateManager.Translate("Model added successfully"),
        )
        return file_path.split("/")[-1]

    @staticmethod
    def DeleteHRNetModel(app, model_name):
        try:
            model_path = os.path.join(ALPHAPOSE_MODELS_PATH, model_name)
            if os.path.exists(model_path):
                os.remove(model_path)
        except Exception as e:
            # Show fail popup
            BaseOkPopup(
                app,
                app,
                TranslateManager.Translate("Error"),
                TranslateManager.Translate("Failed to delete model file"),
            )
            return

        BaseOkPopup(
            app,
            app,
            TranslateManager.Translate("Success"),
            TranslateManager.Translate("Model deleted successfully"),
        )
        return model_name
