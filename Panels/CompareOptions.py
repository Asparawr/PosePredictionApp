import os
from tkinter import filedialog, ttk
import tkinter as tk

from Modules.DataLoader import ImageLoader
from Resources.Consts import DATASETS_PATH, COMPARE_TYPES
from Modules.Events import EventManager
from Modules.Config import ConfigManager
from Modules.Translate import TranslateManager


class CompareOptions(ttk.Frame):
    def __init__(self, parent, app, style):
        super().__init__()
        self.style = style
        self.app = app

        self.frame = ttk.Frame(parent, padding=(10, 10))
        self.frame.grid(
            row=0, column=0, columnspan=2, padx=(20, 20), pady=(5, 0), sticky="nsew"
        )
        # columns
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=10)
        self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(3, weight=10)
        self.frame.columnconfigure(4, weight=100)
        self.frame.columnconfigure(5, weight=100)
        # minimum size
        self.InitWidgets()

    def InitWidgets(self):
        # Label
        ttk.Label(self.frame, text=TranslateManager.Translate("Dataset:")).grid(
            row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="w"
        )

        # OptionMenu for existing datasets
        self.datasets = [""] + [
            f
            for f in os.listdir(DATASETS_PATH)
            if os.path.isdir(os.path.join(DATASETS_PATH, f))
        ]
        self.dataset_var = tk.StringVar()
        if ConfigManager.config["COMPARE"]["dataset"] in self.datasets:
            self.dataset_var.set(ConfigManager.config["COMPARE"]["dataset"])
        self.dataset_menu = ttk.OptionMenu(self.frame, self.dataset_var, *self.datasets)
        self.dataset_menu.grid(
            row=0, column=1, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.dataset_menu.config(width=20)
        self.dataset_var.trace_add("write", self.SetDataset)

        # Label
        ttk.Label(self.frame, text=TranslateManager.Translate("Comparison type:")).grid(
            row=0, column=2, padx=(10, 10), pady=(10, 10), sticky="w"
        )

        # OptionMenu for comparison types
        self.compare_types = [""] + COMPARE_TYPES
        self.compare_type_var = tk.StringVar()
        if ConfigManager.config["COMPARE"]["type"] in self.compare_types:
            self.compare_type_var.set(ConfigManager.config["COMPARE"]["type"])
        self.compare_type_menu = ttk.OptionMenu(
            self.frame, self.compare_type_var, *self.compare_types
        )
        self.compare_type_menu.grid(
            row=0, column=3, padx=(10, 10), pady=(10, 10), sticky="ew"
        )
        self.compare_type_menu.config(width=20)
        self.compare_type_var.trace_add("write", self.SetCompareType)

        # Export button
        export_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Export csv"),
            command=self.Export,
        )
        export_button.grid(row=0, column=4, padx=(10, 10), pady=(10, 10), sticky="we")

        # Save table image button
        save_button = ttk.Button(
            self.frame,
            text=TranslateManager.Translate("Save table image"),
            command=self.SaveImage,
        )
        save_button.grid(row=0, column=5, padx=(10, 10), pady=(10, 10), sticky="we")

    def SetDataset(self, *args):
        ConfigManager.config["COMPARE"]["dataset"] = self.dataset_var.get()
        ConfigManager.config["COMPARE"]["predictions"] = ""
        ConfigManager.config["COMPARE"]["types"] = ""
        ConfigManager.SaveConfig()
        EventManager.set_compare_dataset_event()

    def SetCompareType(self, *args):
        ConfigManager.config["COMPARE"]["type"] = self.compare_type_var.get()
        ConfigManager.config["COMPARE"]["types"] = ""
        ConfigManager.SaveConfig()
        EventManager.set_compare_type_event()

    def Export(self):
        ImageLoader.SaveCurrentTableCsv()

    def SaveImage(self):
        ImageLoader.SaveCurrentTableImage()
