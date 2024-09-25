from tkinter import filedialog, ttk
import tkinter as tk
import os
import subprocess
import threading

from Modules.Events import EventManager
from Resources.Consts import PREDICTIONS_PATH
from Modules.Threading import PopenAndCall
from Modules.DataLoader import PathLoader
from Modules.Config import ConfigManager
from Modules.Translate import TranslateManager

from Widgets.Popups import (
    CallbackWithTextBoxPopup,
    ThreadPopup,
    BaseOkPopup,
    CallbackPopup,
)
from Modules.Predict import *


class PredictionPanel(ttk.Frame):
    def __init__(self, parent, app, style):
        super().__init__()
        self.style = style
        self.app = app
        self.showing_settings_id = -1

        self.frame = ttk.LabelFrame(
            parent, text=TranslateManager.Translate("Prediction"), padding=(20, 10)
        )
        self.frame.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="nsew")
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(3, weight=1)
        self.frame.columnconfigure(4, weight=1)

        self.InitPredictionWidgets()
        self.SetPredictions()
        EventManager.set_model_event += self.SetPredictions
        EventManager.set_dataset_event += self.SetPredictions
        self.prediction_var.trace_add("write", EventManager.set_predictions_event)
        self.prediction_var.trace_add("write", self.UpdateSelectedPrediction)

    def InitPredictionWidgets(self):
        # OptionMenu with all predictions from current model
        self.predictions = [""]
        self.prediction_var = tk.StringVar()
        if ConfigManager.config["SELECTED"]["prediction"] in self.predictions:
            self.prediction_var.set(ConfigManager.config["SELECTED"]["prediction"])
        self.prediction_menu = ttk.OptionMenu(
            self.frame, self.prediction_var, *self.predictions
        )
        self.prediction_menu.grid(
            row=0, column=0, columnspan=3, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.prediction_menu.config(width=20)

        # Delete button
        delete_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Delete"),
            command=self.DeletePrompt,
        )
        delete_button.grid(row=0, column=3, padx=(10, 10), pady=(10, 10), sticky="ew")

        # Add button to upload new prediction
        upload_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Add json"),
            command=self.UploadPrediction,
        )
        upload_button.grid(row=0, column=4, padx=(10, 10), pady=(10, 10), sticky="ew")

        # Predict button
        predict_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Predict"),
            command=self.PredictPopup,
        )
        predict_button.grid(
            row=1, column=0, columnspan=5, padx=(10, 10), pady=(10, 10), sticky="ew"
        )

    def SetPredictions(self, *args):
        self.predictions = [""]
        # based on selected model type and model if it is selected
        if (
            ConfigManager.config["SELECTED"]["model_type"] != ""
            and ConfigManager.config["SELECTED"]["current_model"] != ""
        ):
            prediction_path = PathLoader.GetAllPredictionsPath(ConfigManager.config)
            for file in os.listdir(prediction_path):
                if file.endswith(".json"):
                    self.predictions.append(file)

        self.prediction_menu.set_menu(*self.predictions)
        if ConfigManager.config["SELECTED"]["prediction"] in self.predictions:
            self.prediction_var.set(ConfigManager.config["SELECTED"]["prediction"])
        else:
            self.prediction_var.set("")

    def UpdateSelectedPrediction(self, *args):
        ConfigManager.config["SELECTED"]["prediction"] = self.prediction_var.get()
        ConfigManager.SaveConfig()

    def UploadPrediction(self):
        # get from user
        json_path = filedialog.askopenfilename(
            title=TranslateManager.Translate("Select json file"),
            filetypes=[("Json files", "*.json")],
        )
        if json_path == "":
            return
        # evaluate if file is json
        if not json_path.endswith(".json"):
            BaseOkPopup(
                self.app,
                self.app,
                TranslateManager.Translate("Error"),
                TranslateManager.Translate("File is not json!"),
            )
            return
        # copy to predictions folder
        self.prediction_name = os.path.basename(json_path)[: -len(".json")]
        prediction_path = (
            PathLoader.GetAllPredictionsPath(ConfigManager.config)
            + self.prediction_name
            + ".json"
        )
        if os.path.exists(prediction_path):
            os.remove(prediction_path)
        shutil.copy(json_path, prediction_path)
        ConfigManager.config["SELECTED"]["prediction"] = self.prediction_name
        ConfigManager.SaveConfig()
        self.prediction_var.set(self.prediction_name)
        self.Evaluate()

    def DeletePrompt(self):
        if self.prediction_var.get() == "":
            return
        CallbackPopup(
            self.app.master,
            self.app,
            TranslateManager.Translate("Delete"),
            TranslateManager.Translate("Are you sure you want to delete prediction: "),
            self.Delete,
        )

    def Delete(self):
        prediction_name = self.prediction_var.get()
        if prediction_name == "":
            return
        prediction_path = PathLoader.GetPredictionPath(ConfigManager.config)
        if os.path.exists(prediction_path):
            os.remove(prediction_path)
            ConfigManager.config["SELECTED"]["prediction"] = ""
            ConfigManager.SaveConfig()
            self.prediction_var.set("")

        # also del evaluation
        evaluation_path = (
            PathLoader.GetEvaluationsPath(ConfigManager.config) + prediction_name
        )
        if os.path.exists(evaluation_path):
            os.remove(evaluation_path)

        self.SetPredictions()

    def PredictPopup(self):
        CallbackWithTextBoxPopup(
            self.app.master,
            self.app,
            TranslateManager.Translate("Predict"),
            TranslateManager.Translate("Prediction name: "),
            self.Predict,
        )

    def Predict(self, prediction_name):
        self.prediction_name = prediction_name
        # if empty relaunch
        if prediction_name == "":
            self.PredictPopup()
            return
        thread = PopenAndCall(
            self.OnPredictDone, "python -m Modules.Predict " + prediction_name
        )
        self.prediction_popup = ThreadPopup(
            self.app.master,
            self.app,
            TranslateManager.Translate("Predict"),
            TranslateManager.Translate("Prediction in progress..."),
            thread,
        )

    def OnPredictDone(self):
        # check if pred file exists
        ConfigManager.config["SELECTED"]["prediction"] = self.prediction_name + ".json"
        if not os.path.exists(PathLoader.GetPredictionPath(ConfigManager.config)):
            ConfigManager.config["SELECTED"]["prediction"] = ""
        self.prediction_popup.destroy()
        ConfigManager.config["SELECTED"]["prediction"] = self.prediction_name + ".json"
        ConfigManager.SaveConfig()
        self.prediction_var.set(self.prediction_name)
        self.Evaluate()

    def Evaluate(self):
        thread = PopenAndCall(
            self.OnEvaluateDone, "python -m Modules.Evaluate " + self.prediction_name
        )
        self.evaluation_popup = ThreadPopup(
            self.app.master,
            self.app,
            TranslateManager.Translate("Evaluate"),
            TranslateManager.Translate("Evaluating..."),
            thread,
        )

    def OnEvaluateDone(self):
        BaseOkPopup(
            self.app,
            self.app,
            TranslateManager.Translate("Success"),
            TranslateManager.Translate(
                "Prediction and evaluation finished successfully!"
            ),
        )
        self.evaluation_popup.destroy()
