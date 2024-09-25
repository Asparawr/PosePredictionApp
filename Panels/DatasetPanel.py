import os
import shutil
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog

from Resources.Consts import (
    DATASETS_PATH,
    ANNOTATION_FOLDER,
    IMAGE_FOLDER,
    POSETYPES_FOLDER,
)
from Widgets.Popups import CallbackPopup, CallbackWithTextBoxPopup
from Modules.DataLoader import ImageLoader, AnnotationsLoader, PoseTypeLoader
from Modules.Events import EventManager
from Modules.Config import ConfigManager
from Modules.Translate import TranslateManager


class DatasetPanel(ttk.Frame):
    def __init__(self, parent, app, style):
        super().__init__()
        self.style = style
        self.app = app

        self.frame = ttk.LabelFrame(
            parent, text=TranslateManager.Translate("Dataset"), padding=(20, 10)
        )
        self.frame.grid(row=1, column=0, padx=(20, 10), pady=(10, 0), sticky="nsew")

        self.InitDatasetWidgets()
        self.InitImageWidgets()
        self.InitAnnotationWidgets()
        self.InitPoseTypeWidgets()

        # disable button if no dataset is selected
        self.UpdateButtonStates()

    def InitDatasetWidgets(self):
        # OptionMenu for existing datasets
        self.datasets = [""] + [
            f
            for f in os.listdir(DATASETS_PATH)
            if os.path.isdir(os.path.join(DATASETS_PATH, f))
        ]
        self.dataset_var = tk.StringVar()
        if ConfigManager.config["SELECTED"]["dataset"] in self.datasets:
            self.dataset_var.set(ConfigManager.config["SELECTED"]["dataset"])
        self.dataset_menu = ttk.OptionMenu(self.frame, self.dataset_var, *self.datasets)
        self.dataset_menu.grid(
            row=0, column=1, columnspan=3, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.dataset_menu.config(width=20)
        self.dataset_var.trace_add("write", EventManager.set_dataset_event)
        self.dataset_var.trace_add("write", self.UpdateButtonStates)
        self.dataset_var.trace_add("write", self.UpdateDatasetNameConfig)

        # Button to delete a dataset
        self.delete_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Delete"),
            command=self.DeleteDatasetPrompt,
        )
        self.delete_button.grid(
            row=0, column=4, padx=(10, 10), pady=(10, 10), sticky="ew"
        )

        # Button to create a new dataset
        self.add_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Add new"),
            command=self.NewDatasetPrompt,
        )
        self.add_button.grid(row=0, column=5, padx=(10, 10), pady=(10, 10), sticky="ew")

    def InitImageWidgets(self):
        # Show image count
        self.image_count_var = tk.StringVar()
        self.image_count_label = ttk.Label(
            self.frame,
            textvariable=self.image_count_var,
            font=("Arial", 12, "bold"),
            anchor="center",
        )
        self.image_count_label.grid(
            row=1,
            column=1,
            columnspan=1,
            padx=(10, 10),
            pady=(0, 0),
            sticky="ew",
        )
        self.UpdateImageCount()
        self.dataset_var.trace_add("write", self.UpdateImageCount)

        # Add image from zip button
        self.add_image_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Add images from zip"),
            command=self.AddImagesFromZip,
        )
        self.add_image_button.grid(
            row=1, column=2, columnspan=2, padx=(10, 10), pady=(10, 10), sticky="ew"
        )

        # Clear images button
        self.clear_images_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Clear images"),
            command=self.ClearImages,
        )
        self.clear_images_button.grid(
            row=1, column=4, columnspan=2, padx=(10, 10), pady=(10, 10), sticky="ew"
        )

    def InitAnnotationWidgets(self):
        # Label for annotation
        self.annotation_label = ttk.Label(
            self.frame,
            text=TranslateManager.Translate("Annotations"),
            font=("Arial", 12, "bold"),
            anchor="center",
        )
        self.annotation_label.grid(
            row=3, column=1, columnspan=1, padx=(10, 10), pady=(10, 0), sticky="ew"
        )

        # OptionMenu to select existing annotation
        self.annotations_var = tk.StringVar()
        self.annotation_menu = ttk.OptionMenu(self.frame, self.annotations_var, "")
        self.annotation_menu.grid(
            row=3, column=2, columnspan=2, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.annotation_menu.config(width=20)
        self.UpdateAnnotationList()
        self.annotations_var.trace_add("write", EventManager.set_annotations_event)
        self.annotations_var.trace_add("write", self.UpdateAnnotationConfig)
        self.dataset_var.trace_add("write", self.UpdateAnnotationList)

        # Button to delete an annotation
        self.remove_annotation_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Delete"),
            command=self.DeleteAnnotationPrompt,
        )

        self.remove_annotation_button.grid(
            row=3, column=4, padx=(10, 10), pady=(10, 10), sticky="ew"
        )

        # Button to create a new annotation
        self.add_annotation_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Add json"),
            command=self.NewAnnotationPrompt,
        )
        self.add_annotation_button.grid(
            row=3, column=5, padx=(10, 10), pady=(10, 10), sticky="ew"
        )

    def InitPoseTypeWidgets(self):
        # Label for pose types
        self.pose_types_label = ttk.Label(
            self.frame,
            text=TranslateManager.Translate("Pose Types"),
            font=("Arial", 12, "bold"),
            anchor="center",
        )
        self.pose_types_label.grid(
            row=5, column=1, columnspan=1, padx=(10, 10), pady=(10, 0), sticky="ew"
        )

        # OptionMenu to select existing pose type
        self.pose_var = tk.StringVar()
        self.pose_menu = ttk.OptionMenu(self.frame, self.pose_var, "")
        self.pose_menu.grid(
            row=5, column=2, columnspan=2, padx=(10, 10), pady=(10, 0), sticky="ew"
        )
        self.pose_menu.config(width=20)
        self.UpdatePoseTypeList()
        self.pose_var.trace_add("write", self.UpdatePoseTypeConfig)
        self.dataset_var.trace_add("write", self.UpdatePoseTypeList)

        # Button to delete a pose type
        self.remove_pose_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Delete"),
            command=self.DeletePoseTypePrompt,
        )
        self.remove_pose_button.grid(
            row=5, column=4, padx=(10, 10), pady=(10, 0), sticky="ew"
        )

        # Button to create a new pose type
        self.add_pose_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Add csv"),
            command=self.NewPoseTypePrompt,
        )
        self.add_pose_button.grid(
            row=5, column=5, padx=(10, 10), pady=(10, 0), sticky="ew"
        )

    def UpdateButtonStates(self, *args):
        if self.dataset_var.get() == "":
            self.add_image_button["state"] = "disabled"
            self.clear_images_button["state"] = "disabled"
        else:
            self.add_image_button["state"] = "normal"
            self.clear_images_button["state"] = "normal"

    def UpdateDatasetNameConfig(self, *args):
        ConfigManager.config["SELECTED"]["dataset"] = self.dataset_var.get()
        ConfigManager.config["SELECTED"]["image"] = ""
        ConfigManager.config["SELECTED"]["image_id"] = ""
        ConfigManager.SaveConfig()

    def NewDatasetPrompt(self):
        CallbackWithTextBoxPopup(
            self,
            self.app,
            TranslateManager.Translate("Add new dataset"),
            TranslateManager.Translate("Name of the new dataset:"),
            self.NewDataset,
        )

    def NewDataset(self, name):
        # Create new folder
        dataset_path = os.path.join(DATASETS_PATH, name)
        os.makedirs(dataset_path, exist_ok=True)

        # Create subfolders
        os.makedirs(os.path.join(dataset_path, ANNOTATION_FOLDER), exist_ok=True)
        os.makedirs(os.path.join(dataset_path, IMAGE_FOLDER), exist_ok=True)
        os.makedirs(os.path.join(dataset_path, POSETYPES_FOLDER), exist_ok=True)

        # Update
        self.datasets.append(name)
        self.dataset_menu.set_menu(*self.datasets)
        self.dataset_var.set(name)
        ConfigManager.config["SELECTED"]["dataset"] = name
        ConfigManager.SaveConfig()

    def DeleteDatasetPrompt(self):
        CallbackPopup(
            self,
            self.app,
            TranslateManager.Translate("Delete Dataset"),
            TranslateManager.Translate("Are you sure you want to delete this dataset?"),
            self.DeleteDataset,
        )

    def DeleteDataset(self):
        # Delete folder
        dataset_name = self.dataset_var.get()
        dataset_path = os.path.join(DATASETS_PATH, dataset_name)
        if os.path.exists(dataset_path):
            shutil.rmtree(dataset_path)
        self.datasets.remove(dataset_name)
        self.dataset_menu.set_menu(*self.datasets)
        self.dataset_var.set("")
        ConfigManager.config["SELECTED"]["dataset"] = ""
        ConfigManager.SaveConfig()

    def AddImagesFromZip(self):
        dataset_name = self.dataset_var.get()
        if dataset_name == "":
            return
        # Show prompt to select zip file
        zip_path = filedialog.askopenfilename(
            title=TranslateManager.Translate("Select zip file"),
            filetypes=[("Zip files", "*.zip")],
        )
        if zip_path == "":
            return
        ImageLoader.AddImagesFromZip(self.app, zip_path, dataset_name)
        self.UpdateImageCount()

    def UpdateImageCount(self, *args):
        dataset_name = self.dataset_var.get()
        if dataset_name == "":
            self.image_count_var.set("")
            return
        self.image_count_var.set(
            TranslateManager.Translate("Images: ")
            + str(
                ImageLoader.CountAllImagesInFolder(
                    DATASETS_PATH + dataset_name + "/" + IMAGE_FOLDER
                )
            )
        )

    def ClearImages(self):
        dataset_name = self.dataset_var.get()
        if dataset_name == "":
            return
        ImageLoader.ClearImages(self.app, dataset_name)
        self.UpdateImageCount()

    def UpdateAnnotationList(self, *args):
        dataset_name = self.dataset_var.get()
        if dataset_name == "":
            self.annotations = [""]
        else:
            annotations_path = os.path.join(
                DATASETS_PATH, dataset_name, ANNOTATION_FOLDER
            )
            self.annotations = [""] + [
                f
                for f in os.listdir(annotations_path)
                if os.path.isfile(os.path.join(annotations_path, f))
            ]
        self.annotations_var.set("")
        self.annotation_menu.set_menu(*self.annotations)
        if ConfigManager.config["SELECTED"]["annotations"] in self.annotations:
            self.annotations_var.set(ConfigManager.config["SELECTED"]["annotations"])

    def UpdateAnnotationConfig(self, *args):
        ConfigManager.config["SELECTED"]["annotations"] = self.annotations_var.get()
        ConfigManager.SaveConfig()

    def NewAnnotationPrompt(self):
        dataset_name = self.dataset_var.get()
        if dataset_name == "":
            return
        new_annotation = AnnotationsLoader.AddAnnotationJson(self.app, dataset_name)
        if new_annotation:
            self.UpdateAnnotationList()
            self.annotations_var.set(new_annotation)

    def DeleteAnnotationPrompt(self):
        CallbackPopup(
            self,
            self.app,
            TranslateManager.Translate("Delete Annotation"),
            TranslateManager.Translate(
                "Are you sure you want to delete this annotation?"
            ),
            self.DeleteAnnotation,
        )

    def DeleteAnnotation(self):
        dataset_name = self.dataset_var.get()
        annotation_name = self.annotations_var.get()
        if dataset_name == "" or annotation_name == "":
            return
        annotation_path = os.path.join(
            DATASETS_PATH, dataset_name, ANNOTATION_FOLDER, annotation_name
        )
        os.remove(annotation_path)
        self.UpdateAnnotationList()
        self.annotations_var.set("")

    def UpdatePoseTypeList(self, *args):
        dataset_name = self.dataset_var.get()
        if dataset_name == "":
            self.pose_types = [""]
        else:
            # create folder if not exists
            if not os.path.exists(
                os.path.join(DATASETS_PATH, dataset_name, POSETYPES_FOLDER)
            ):
                os.makedirs(
                    os.path.join(DATASETS_PATH, dataset_name, POSETYPES_FOLDER),
                    exist_ok=True,
                )
            pose_types_path = os.path.join(
                DATASETS_PATH, dataset_name, POSETYPES_FOLDER
            )
            self.pose_types = [""] + [
                f
                for f in os.listdir(pose_types_path)
                if os.path.isfile(os.path.join(pose_types_path, f))
            ]
        self.pose_var.set("")
        self.pose_menu.set_menu(*self.pose_types)
        if ConfigManager.config["SELECTED"]["pose_type"] in self.pose_types:
            self.pose_var.set(ConfigManager.config["SELECTED"]["pose_type"])

    def UpdatePoseTypeConfig(self, *args):
        ConfigManager.config["SELECTED"]["pose_type"] = self.pose_var.get()
        ConfigManager.SaveConfig()

    def NewPoseTypePrompt(self):
        dataset_name = self.dataset_var.get()
        if dataset_name == "":
            return
        new_pose = PoseTypeLoader.AddPoseTypeCsv(self.app, dataset_name)
        if new_pose:
            self.UpdatePoseTypeList()
            self.pose_var.set(new_pose)

    def DeletePoseTypePrompt(self):
        CallbackPopup(
            self,
            self.app,
            TranslateManager.Translate("Delete Pose Type"),
            TranslateManager.Translate(
                "Are you sure you want to delete this pose type?"
            ),
            self.DeletePoseType,
        )

    def DeletePoseType(self):
        dataset_name = self.dataset_var.get()
        pose_name = self.pose_var.get()
        if dataset_name == "" or pose_name == "":
            return
        pose_path = os.path.join(
            DATASETS_PATH, dataset_name, POSETYPES_FOLDER, pose_name
        )
        os.remove(pose_path)
        self.UpdatePoseTypeList()
        self.pose_var.set("")
