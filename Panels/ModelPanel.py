from tkinter import filedialog, ttk
import tkinter as tk
import os

from Resources.Consts import (
    MODEL_TYPES,
    YOLO_MODELS_PATH,
    OPENPOSE_MODELS,
    ALPHAPOSE_MODELS_PATH,
)
from Modules.Events import EventManager
from Modules.Config import ConfigManager
from Modules.Translate import TranslateManager
from Modules.DataLoader import ModelLoader

from Widgets.Popups import CallbackPopup


class ModelPanel(ttk.Frame):
    def __init__(self, parent, app, style):
        super().__init__()
        self.style = style
        self.app = app
        self.showing_settings_id = -1

        self.frame = ttk.LabelFrame(
            parent, text=TranslateManager.Translate("Model"), padding=(20, 10)
        )
        self.frame.grid(row=2, column=0, padx=(20, 10), pady=(10, 0), sticky="nsew")

        self.InitModelSelectionWidgets()
        self.InitYoloSettingsWidgets()
        self.InitOpenPoseSettingsWidgets()
        self.InitAlphaPoseSettingsWidgets()
        self.SetSelectedModelType()

    def InitModelSelectionWidgets(self):
        # OptionMenu for 3 model types
        self.model_types = [""] + MODEL_TYPES
        self.model_type_var = tk.StringVar()
        if ConfigManager.config["SELECTED"]["model_type"] in self.model_types:
            self.model_type_var.set(ConfigManager.config["SELECTED"]["model_type"])
        self.model_type_menu = ttk.OptionMenu(
            self.frame, self.model_type_var, *self.model_types
        )
        self.model_type_menu.grid(
            row=0, column=0, columnspan=2, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.model_type_menu.config(width=20)
        self.model_type_var.trace_add("write", self.UpdateSelectedModelType)

        # OptionMenu for models
        self.model_var = tk.StringVar()
        self.models = [""]
        self.model_menu = ttk.OptionMenu(self.frame, self.model_var, *self.models)
        self.model_menu.grid(
            row=0, column=2, columnspan=2, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.model_menu.config(width=20)
        self.model_var.trace_add("write", self.UpdateSelectedModel)

    def InitYoloSettingsWidgets(self):
        self.InitModelButtonsWidgets()
        # Conf textbox
        self.conf_label = ttk.Label(
            self.frame, text=TranslateManager.Translate("Confidence")
        )
        self.conf_label.grid(row=3, column=0, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.conf_var = tk.StringVar()
        self.conf_var.set(ConfigManager.config["YOLO"]["conf"])
        self.conf_entry = ttk.Entry(self.frame, textvariable=self.conf_var)
        self.conf_entry.grid(row=3, column=1, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.conf_var.trace_add("write", self.UpdateConf)

        # IOU textbox
        self.iou_label = ttk.Label(self.frame, text=TranslateManager.Translate("IOU"))
        self.iou_label.grid(row=2, column=0, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.iou_var = tk.StringVar()
        self.iou_var.set(ConfigManager.config["YOLO"]["iou"])
        self.iou_entry = ttk.Entry(self.frame, textvariable=self.iou_var)
        self.iou_entry.grid(row=2, column=1, padx=(10, 10), pady=(10, 10), sticky="ew")
        self.iou_var.trace_add("write", self.UpdateIou)

        # Max detections textbox
        self.max_detections_label = ttk.Label(
            self.frame, text=TranslateManager.Translate("Max detections")
        )
        self.max_detections_label.grid(
            row=2, column=2, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.max_detections_var = tk.StringVar()
        self.max_detections_var.set(ConfigManager.config["YOLO"]["max_det"])
        self.max_detections_entry = ttk.Entry(
            self.frame, textvariable=self.max_detections_var
        )
        self.max_detections_entry.grid(
            row=2, column=3, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.max_detections_var.trace_add("write", self.UpdateMaxDetections)

    def InitOpenPoseSettingsWidgets(self):
        # net_resolution string
        self.net_resolution_label = ttk.Label(
            self.frame, text=TranslateManager.Translate("Net resolution")
        )
        self.net_resolution_label.grid(
            row=2, column=0, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.net_resolution_var = tk.StringVar()
        self.net_resolution_var.set(ConfigManager.config["OPENPOSE"]["net_resolution"])
        self.net_resolution_entry = ttk.Entry(
            self.frame, textvariable=self.net_resolution_var
        )
        self.net_resolution_entry.grid(
            row=2, column=1, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.net_resolution_var.trace_add("write", self.UpdateNetResolution)

        # scale_number int
        self.scale_number_label = ttk.Label(
            self.frame, text=TranslateManager.Translate("Scale number")
        )
        self.scale_number_label.grid(
            row=2, column=2, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.scale_number_var = tk.StringVar()
        self.scale_number_var.set(ConfigManager.config["OPENPOSE"]["scale_number"])
        self.scale_number_entry = ttk.Entry(
            self.frame, textvariable=self.scale_number_var
        )
        self.scale_number_entry.grid(
            row=2, column=3, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.scale_number_var.trace_add("write", self.UpdateScaleNumber)

        # scale_gap float
        self.scale_gap_label = ttk.Label(
            self.frame, text=TranslateManager.Translate("Scale gap")
        )
        self.scale_gap_label.grid(
            row=3, column=0, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.scale_gap_var = tk.StringVar()
        self.scale_gap_var.set(ConfigManager.config["OPENPOSE"]["scale_gap"])
        self.scale_gap_entry = ttk.Entry(self.frame, textvariable=self.scale_gap_var)
        self.scale_gap_entry.grid(
            row=3, column=1, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.scale_gap_var.trace_add("write", self.UpdateScaleGap)

    def InitAlphaPoseSettingsWidgets(self):
        # NMS_THRES
        self.nms_thres_label = ttk.Label(
            self.frame, text=TranslateManager.Translate("NMS Threshold")
        )
        self.nms_thres_label.grid(
            row=2, column=0, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.nms_thres_var = tk.StringVar()
        self.nms_thres_var.set(ConfigManager.config["ALPHAPOSE"]["nms_thres"])
        self.nms_thres_entry = ttk.Entry(self.frame, textvariable=self.nms_thres_var)
        self.nms_thres_entry.grid(
            row=2, column=1, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.nms_thres_var.trace_add("write", self.UpdateNmsThres)

        # confidence
        self.hrnet_conf_label = ttk.Label(
            self.frame, text=TranslateManager.Translate("Confidence")
        )
        self.hrnet_conf_label.grid(
            row=2, column=2, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.hernet_conf_var = tk.StringVar()
        self.hernet_conf_var.set(ConfigManager.config["ALPHAPOSE"]["confidence"])
        self.hrnet_conf_entry = ttk.Entry(self.frame, textvariable=self.hernet_conf_var)
        self.hrnet_conf_entry.grid(
            row=2, column=3, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.hernet_conf_var.trace_add("write", self.UpdateHrnetConf)

    def InitModelButtonsWidgets(self):
        # Delete model button
        self.delete_model_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Delete Model"),
            command=self.DeleteModelPrompt,
        )
        self.delete_model_button.grid(
            row=1, column=0, columnspan=2, padx=(10, 10), pady=(10, 10), sticky="ew"
        )

        # Add model button
        self.add_model_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Add Model"),
            command=self.AddModel,
        )
        self.add_model_button.grid(
            row=1, column=2, columnspan=2, padx=(10, 10), pady=(10, 10), sticky="ew"
        )

    def UpdateSelectedModelType(self, *args):
        ConfigManager.config["SELECTED"]["model_type"] = self.model_type_var.get()
        ConfigManager.config["SELECTED"]["prediction"] = ""
        ConfigManager.SaveConfig()
        self.SetSelectedModelType()

    def SetSelectedModelType(self):
        self.UpdateModelList()
        model_type = self.model_type_var.get()
        if model_type == MODEL_TYPES[0]:
            self.ShowYoloSettingsWidgets()
        elif model_type == MODEL_TYPES[1]:
            self.ShowOpenPoseSettingsWidgets()
        elif model_type == MODEL_TYPES[2]:
            self.ShowAlphaPoseSettingsWidgets()
        EventManager.set_model_event()

    def UpdateModelList(self, *args):
        model_type = self.model_type_var.get()
        if model_type == "":
            self.models = [""]
        else:
            if model_type == MODEL_TYPES[0]:
                self.models = [""]
                for file in os.listdir(YOLO_MODELS_PATH):
                    if file.endswith(".pt"):
                        self.models.append(file)
                if ConfigManager.config["SELECTED"]["yolo_model"] in self.models:
                    self.model_var.set(ConfigManager.config["SELECTED"]["yolo_model"])
                else:
                    self.model_var.set("")

            elif model_type == MODEL_TYPES[1]:
                self.models = [""] + OPENPOSE_MODELS
                if ConfigManager.config["SELECTED"]["openpose_model"] in self.models:
                    self.model_var.set(
                        ConfigManager.config["SELECTED"]["openpose_model"]
                    )
                else:
                    self.model_var.set("")

            elif model_type == MODEL_TYPES[2]:
                self.models = [""]
                for file in os.listdir(ALPHAPOSE_MODELS_PATH):
                    if file.endswith(".pth"):
                        self.models.append(file)
                if ConfigManager.config["SELECTED"]["alphapose_model"] in self.models:
                    self.model_var.set(
                        ConfigManager.config["SELECTED"]["alphapose_model"]
                    )
                else:
                    self.model_var.set("")

        self.model_menu.set_menu(*self.models)

    def UpdateSelectedModel(self, *args):
        model_type = self.model_type_var.get()
        if model_type == MODEL_TYPES[0]:
            ConfigManager.config["SELECTED"]["yolo_model"] = self.model_var.get()
        elif model_type == MODEL_TYPES[2]:
            ConfigManager.config["SELECTED"]["alphapose_model"] = self.model_var.get()
        ConfigManager.config["SELECTED"]["current_model"] = self.model_var.get()
        ConfigManager.SaveConfig()
        EventManager.set_model_event()

    def ShowYoloSettingsWidgets(self):
        self.ShowModelButtonsWidgets()
        self.HideOpenPoseSettingsWidgets()
        self.HideAlphaPoseSettingsWidgets()
        self.conf_label.grid()
        self.conf_entry.grid()
        self.iou_label.grid()
        self.iou_entry.grid()
        self.max_detections_label.grid()
        self.max_detections_entry.grid()
        self.model_menu.grid()

    def ShowOpenPoseSettingsWidgets(self):
        self.model_menu.grid_remove()
        self.HideModelButtonsWidgets()
        self.HideYoloSettingsWidgets()
        self.HideAlphaPoseSettingsWidgets()
        self.net_resolution_label.grid()
        self.net_resolution_entry.grid()
        self.scale_number_label.grid()
        self.scale_number_entry.grid()
        self.scale_gap_label.grid()
        self.scale_gap_entry.grid()

    def ShowAlphaPoseSettingsWidgets(self):
        self.ShowModelButtonsWidgets()
        self.HideYoloSettingsWidgets()
        self.HideOpenPoseSettingsWidgets()
        self.nms_thres_label.grid()
        self.nms_thres_entry.grid()
        self.hrnet_conf_label.grid()
        self.hrnet_conf_entry.grid()
        self.model_menu.grid()

    def ShowModelButtonsWidgets(self):
        self.delete_model_button.grid()
        self.add_model_button.grid()

    def HideYoloSettingsWidgets(self):
        self.conf_label.grid_remove()
        self.conf_entry.grid_remove()
        self.iou_label.grid_remove()
        self.iou_entry.grid_remove()
        self.max_detections_label.grid_remove()
        self.max_detections_entry.grid_remove()

    def HideOpenPoseSettingsWidgets(self):
        self.net_resolution_label.grid_remove()
        self.net_resolution_entry.grid_remove()
        self.scale_number_label.grid_remove()
        self.scale_number_entry.grid_remove()
        self.scale_gap_label.grid_remove()
        self.scale_gap_entry.grid_remove()

    def HideAlphaPoseSettingsWidgets(self):
        self.nms_thres_label.grid_remove()
        self.nms_thres_entry.grid_remove()
        self.hrnet_conf_label.grid_remove()
        self.hrnet_conf_entry.grid_remove()

    def HideModelButtonsWidgets(self):
        self.delete_model_button.grid_remove()
        self.add_model_button.grid_remove()

    def AddModel(self):
        if self.model_type_var.get() == MODEL_TYPES[0]:
            new_model = ModelLoader.AddYoloModel(self.app)
        elif self.model_type_var.get() == MODEL_TYPES[2]:
            new_model = ModelLoader.AddHRNetModel(self.app)
        if new_model:
            self.UpdateModelList()
            self.model_var.set(new_model)

    def DeleteModelPrompt(self):
        if self.model_var.get() == "":
            return
        popup = CallbackPopup(
            self.app,
            self.app,
            TranslateManager.Translate("Delete Model"),
            TranslateManager.Translate("Are you sure you want to delete this model?"),
            self.DeleteModel,
        )
        popup.mainloop()

    def DeleteModel(self):
        if self.model_type_var.get() == MODEL_TYPES[0]:
            ModelLoader.DeleteYoloModel(self.app, self.model_var.get())
        elif self.model_type_var.get() == MODEL_TYPES[2]:
            ModelLoader.DeleteHRNetModel(self.app, self.model_var.get())
        self.UpdateModelList()

    def UpdateConf(self, *args):
        # check if it's float
        try:
            float(self.conf_var.get())
        except ValueError:
            self.conf_var.set(ConfigManager.config["YOLO"]["conf"])
            return
        ConfigManager.config["YOLO"]["conf"] = self.conf_var.get()
        ConfigManager.SaveConfig()

    def UpdateIou(self, *args):
        # check if it's float
        try:
            float(self.iou_var.get())
        except ValueError:
            self.iou_var.set(ConfigManager.config["YOLO"]["iou"])
            return
        ConfigManager.config["YOLO"]["iou"] = self.iou_var.get()
        ConfigManager.SaveConfig()

    def UpdateMaxDetections(self, *args):
        # check if it's int
        try:
            int(self.max_detections_var.get())
        except ValueError:
            self.max_detections_var.set(ConfigManager.config["YOLO"]["max_det"])
            return
        ConfigManager.config["YOLO"]["max_det"] = self.max_detections_var.get()
        ConfigManager.SaveConfig()

    def UpdateNetResolution(self, *args):
        ConfigManager.config["OPENPOSE"][
            "net_resolution"
        ] = self.net_resolution_var.get()
        ConfigManager.SaveConfig()

    def UpdateScaleNumber(self, *args):
        # check if it's int
        try:
            int(self.scale_number_var.get())
        except ValueError:
            self.scale_number_var.set(ConfigManager.config["OPENPOSE"]["scale_number"])
            return
        ConfigManager.config["OPENPOSE"]["scale_number"] = self.scale_number_var.get()
        ConfigManager.SaveConfig()

    def UpdateScaleGap(self, *args):
        # check if it's float
        try:
            float(self.scale_gap_var.get())
        except ValueError:
            self.scale_gap_var.set(ConfigManager.config["OPENPOSE"]["scale_gap"])
            return
        ConfigManager.config["OPENPOSE"]["scale_gap"] = self.scale_gap_var.get()
        ConfigManager.SaveConfig()

    def UpdateNmsThres(self, *args):
        # check if it's float
        try:
            float(self.nms_thres_var.get())
        except ValueError:
            self.nms_thres_var.set(ConfigManager.config["ALPHAPOSE"]["nms_thres"])
            return
        ConfigManager.config["ALPHAPOSE"]["nms_thres"] = self.nms_thres_var.get()
        ConfigManager.SaveConfig()

    def UpdateHrnetConf(self, *args):
        # check if it's float
        try:
            float(self.hernet_conf_var.get())
        except ValueError:
            self.hernet_conf_var.set(ConfigManager.config["ALPHAPOSE"]["confidence"])
            return
        ConfigManager.config["ALPHAPOSE"]["confidence"] = self.hernet_conf_var.get()
        ConfigManager.SaveConfig()
