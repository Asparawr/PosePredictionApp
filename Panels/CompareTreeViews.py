import os
from tkinter import ttk
import json

from Widgets.TreeView import MultiTreeView

from Resources.Consts import AP_TYPES, AR_TYPES, COMPARE_TYPES, KEYPOINTS
from Modules.DataLoader import PathLoader
from Modules.Events import EventManager
from Modules.Config import ConfigManager
from Modules.Translate import TranslateManager


class CompareTreeViews(ttk.Frame):
    def __init__(self, parent, app, style):
        super().__init__()
        self.style = style
        self.app = app

        self.frame = ttk.Frame(parent, padding=(10, 5))
        self.frame.grid(row=1, column=0, padx=(20, 20), pady=(0, 0), sticky="nsew")
        # minimum size
        self.frame.columnconfigure(0, weight=1000)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1000)
        self.frame.columnconfigure(3, weight=1)
        self.frame.rowconfigure(0, weight=10)
        self.frame.rowconfigure(1, weight=10)
        self.frame.rowconfigure(2, weight=1)

        self.InitTreeViewWidgets()
        EventManager.set_compare_type_event += self.RefreshTypeTreeview
        EventManager.set_compare_dataset_event += self.RefreshTypeTreeview
        EventManager.set_compare_dataset_event += self.RefreshPredictionsTreeview

    def InitTreeViewWidgets(self):
        # Predictions treeview
        self.predictions_treeview = MultiTreeView(self.frame, 10, 0, 0, 1, 3)
        self.predictions_treeview.heading(
            "#0", text=TranslateManager.Translate("Predictions"), anchor="w"
        )
        self.RefreshPredictionsTreeview()
        self.predictions_treeview.bind("<ButtonRelease-1>", self.OnPredictionClick)
        # select from save
        if ConfigManager.config["COMPARE"]["predictions"] != "":
            for item in json.loads(ConfigManager.config["COMPARE"]["predictions"]):
                for model_type_item in self.predictions_treeview.get_children():
                    added_model_type = False
                    for model_item in self.predictions_treeview.get_children(
                        model_type_item
                    ):
                        if item in self.predictions_treeview.get_children(model_item):
                            self.predictions_treeview.selection_add(item)
                            added_model_type = True
                            self.predictions_treeview.item(model_item, open=True)
                    if added_model_type:
                        self.predictions_treeview.item(model_type_item, open=True)

        # Type treeview
        self.type_treeview = MultiTreeView(self.frame, 5, 1, 0, 1, 3)
        self.type_treeview.bind("<ButtonRelease-1>", self.OnTypeClick)
        # Add columns
        self.RefreshTypeTreeview()
        # select from save
        if ConfigManager.config["COMPARE"]["types"] != "":
            for item in json.loads(ConfigManager.config["COMPARE"]["types"]):
                if item in self.type_treeview.get_children():
                    self.type_treeview.selection_add(item)

        # AP treeview
        self.ap_treeview = MultiTreeView(self.frame, 4, 2, 0, 1)
        self.ap_treeview.heading("#0", text="AP", anchor="w")

        for ap_type in AP_TYPES:
            self.ap_treeview.insert("", "end", ap_type, text=ap_type)
        self.ap_treeview.bind("<ButtonRelease-1>", self.OnApClick)
        # select from save
        for item in json.loads(ConfigManager.config["COMPARE"]["ap"]):
            if item in self.ap_treeview.get_children():
                self.ap_treeview.selection_add(item)

        # AR treeview
        self.ar_treeview = MultiTreeView(self.frame, 4, 2, 2, 1)
        self.ar_treeview.heading("#0", text="AR", anchor="w")
        for ar_type in AR_TYPES:
            self.ar_treeview.insert("", "end", ar_type, text=ar_type)
        self.ar_treeview.bind("<ButtonRelease-1>", self.OnArClick)
        # select from save
        for item in json.loads(ConfigManager.config["COMPARE"]["ar"]):
            if item in self.ar_treeview.get_children():
                self.ar_treeview.selection_add(item)

    def RefreshPredictionsTreeview(self, *args):
        # Clear treeview
        for i in self.predictions_treeview.get_children():
            self.predictions_treeview.delete(i)
        # Add rows
        path = PathLoader.GetCompareEvaluationsPath(ConfigManager.config)
        # Each column is folder deeper
        for i, folder in enumerate(os.listdir(path)):
            self.predictions_treeview.insert("", "end", i, text=folder)
            for j, file in enumerate(os.listdir(path + folder)):
                id = str(i) + "A" + str(j)
                self.predictions_treeview.insert(i, "end", id, text=file)
                for k, prediction in enumerate(os.listdir(path + folder + "/" + file)):
                    self.predictions_treeview.insert(
                        id,
                        "end",
                        path + folder + "/" + file + "/" + prediction,
                        text=prediction,
                    )

    def RefreshTypeTreeview(self):
        # Clear treeview
        for i in self.type_treeview.get_children():
            self.type_treeview.delete(i)

        type = ConfigManager.config["COMPARE"]["type"]
        if type == COMPARE_TYPES[0]:
            # Hide Type treeview
            self.type_treeview.grid_remove()
            return
        elif type == COMPARE_TYPES[1]:
            # Show Type treeview
            self.type_treeview.grid()
            # Add columns
            self.type_treeview.heading(
                "#0", text=TranslateManager.Translate("Keypoint name"), anchor="w"
            )
            for key in KEYPOINTS:
                self.type_treeview.insert(
                    "", "end", key, text=TranslateManager.Translate(key)
                )

        elif type == COMPARE_TYPES[2]:
            # Show Type treeview
            self.type_treeview.grid()
            # Add columns
            self.type_treeview.heading(
                "#0", text=TranslateManager.Translate("Pose Type"), anchor="w"
            )
            path = PathLoader.GetComparePoseTypesPath(ConfigManager.config)
            # List all files in the directory
            for i, file in enumerate(os.listdir(path)):
                if file.endswith(".csv"):
                    self.type_treeview.insert("", "end", file, text=file[:-4])

    def OnPredictionClick(self, *args):
        item = self.predictions_treeview.focus()
        # Deselect if doesn't start with B or already selected
        if not item.endswith(".json"):
            self.predictions_treeview.selection_remove(item)
            return

        if item in self.predictions_treeview.selection():
            self.predictions_treeview.selection_remove(item)
        else:
            # Select
            self.predictions_treeview.selection_add(item)

        # Save selected predictions
        ConfigManager.config["COMPARE"]["predictions"] = json.dumps(
            self.predictions_treeview.selection()
        )
        ConfigManager.SaveConfig()
        EventManager.set_compare_predictions_event()

    def OnTypeClick(self, *args):
        item = self.type_treeview.focus()
        if item in self.type_treeview.selection():
            self.type_treeview.selection_remove(item)
        else:
            # Select
            self.type_treeview.selection_add(item)

        # Save selected type
        ConfigManager.config["COMPARE"]["types"] = json.dumps(
            self.type_treeview.selection()
        )
        ConfigManager.SaveConfig()
        EventManager.set_compare_types_event()

    def OnApClick(self, *args):
        item = self.ap_treeview.focus()
        if item in self.ap_treeview.selection():
            self.ap_treeview.selection_remove(item)
        else:
            # Select
            self.ap_treeview.selection_add(item)

        # Save selected type
        ConfigManager.config["COMPARE"]["ap"] = json.dumps(self.ap_treeview.selection())
        ConfigManager.SaveConfig()
        EventManager.set_compare_ap_event()

    def OnArClick(self, *args):
        item = self.ar_treeview.focus()
        if item in self.ar_treeview.selection():
            self.ar_treeview.selection_remove(item)
        else:
            # Select
            self.ar_treeview.selection_add(item)

        # Save selected type
        ConfigManager.config["COMPARE"]["ar"] = json.dumps(self.ar_treeview.selection())
        ConfigManager.SaveConfig()
        EventManager.set_compare_ar_event()
