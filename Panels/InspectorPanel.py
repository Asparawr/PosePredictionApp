from tkinter import ttk
import tkinter as tk
import os
from PIL import ImageTk, Image

from Resources.Consts import DATASETS_PATH, IMAGE_FOLDER, TEMP_IMAGE_PATH
from Modules.DataLoader import ImageLoader
from Modules.DataPlotter import PlotImage
from Modules.Events import EventManager
from Widgets.TreeView import TreeView
from Modules.Config import ConfigManager
from Modules.Translate import TranslateManager
from Modules.Threading import PopenAndCall


class InspectorPanel(ttk.Frame):
    def __init__(self, parent, app, style):
        super().__init__()
        self.style = style
        self.app = app
        self.thread = None

        self.frame = ttk.LabelFrame(
            parent, text=TranslateManager.Translate("Inspector"), padding=(20, 10)
        )
        self.frame.grid(
            row=1, rowspan=3, column=1, padx=(10, 20), pady=(10, 10), sticky="nsew"
        )
        self.frame.columnconfigure(index=0, weight=4)
        self.frame.columnconfigure(index=1, weight=1)
        self.frame.columnconfigure(index=2, weight=10000)
        self.frame.rowconfigure(index=0, weight=10000)
        self.frame.rowconfigure(index=1, weight=1)

        self.InitTreeViewWidgets()
        self.InitImageViewWidgets()
        self.InitSettingsWidgets()
        # Set treeview data
        self.SetTreeviewData()

        EventManager.set_dataset_event += self.SetTreeviewData
        EventManager.set_model_event += self.SetTreeviewData
        EventManager.set_annotations_event += self.OnTreeviewClick
        EventManager.set_predictions_event += self.OnTreeviewClick
        EventManager.enable_inspector_event += self.SetTreeviewData
        EventManager.darkmode_switch_event += self.ResetTreeview
        EventManager.update_inspector_switch_event += self.HandleUpdateInspectorSwitch

    def InitTreeViewWidgets(self):
        self.treeview = TreeView(self.frame, 24, 0, 0, 2, 1)
        # Handle click
        self.treeview.bind("<ButtonRelease-1>", self.OnTreeviewClick)

    def InitImageViewWidgets(self):
        # Frame for the image
        self.image_frame = ttk.Frame(self.frame)
        self.image_frame.grid(
            row=0,
            column=2,
            padx=(5, 10),
            pady=(20, 10),
            sticky="nsew",
        )

        # Image
        self.image = tk.PhotoImage()
        self.image_label = ttk.Label(self.image_frame, image=self.image)
        self.image_label.pack(expand=True)

    def InitSettingsWidgets(self):
        # Settings frame
        self.settings_frame = ttk.Frame(self.frame)
        self.settings_frame.grid(
            row=1, column=1, columnspan=3, padx=(30, 10), pady=(0, 10), sticky="nsew"
        )

        # Save button
        self.save_button = ttk.Button(
            self.settings_frame,
            text=TranslateManager.Translate("Save image"),
            command=self.SaveImage,
        )
        self.save_button.grid(row=0, column=0, pady=(10, 0))

        # Enable annotations checkbox
        self.enable_annotations_var = tk.IntVar()
        if ConfigManager.config["SELECTED"]["enable_annotations"] == "1":
            self.enable_annotations_var.set(1)
        else:
            self.enable_annotations_var.set(0)
        self.enable_annotations_checkbox = ttk.Checkbutton(
            self.settings_frame,
            text=TranslateManager.Translate("Enable Annotations"),
            variable=self.enable_annotations_var,
        )
        self.enable_annotations_checkbox.grid(
            row=0, column=1, pady=(20, 10), padx=(20, 0)
        )
        # Update on change
        self.enable_annotations_var.trace_add("write", self.OnAnnotationsClick)

        # Enable predictions checkbox
        self.enable_predictions_var = tk.IntVar()
        if ConfigManager.config["SELECTED"]["enable_predictions"] == "1":
            self.enable_predictions_var.set(1)
        else:
            self.enable_predictions_var.set(0)
        self.enable_predictions_checkbox = ttk.Checkbutton(
            self.settings_frame,
            text=TranslateManager.Translate("Enable Predictions"),
            variable=self.enable_predictions_var,
        )
        self.enable_predictions_checkbox.grid(
            row=0, column=2, pady=(20, 10), padx=(20, 0)
        )
        # Update on change
        self.enable_predictions_var.trace_add("write", self.OnPredictionsClick)

        # How many best predictions to show
        self.predictions_var = tk.StringVar()
        self.predictions_var.set(ConfigManager.config["SELECTED"]["num_predictions"])
        self.predictions_label = ttk.Label(
            self.settings_frame, text=TranslateManager.Translate("Best predictions:")
        )
        self.predictions_label.grid(row=0, column=3, pady=(20, 10), padx=(20, 0))
        self.predictions_entry = ttk.Entry(
            self.settings_frame, textvariable=self.predictions_var
        )
        self.predictions_entry.grid(row=0, column=4, pady=(20, 10), padx=(5, 0))
        self.predictions_var.trace_add("write", self.UpdatePredictionsCount)

    def HandleUpdateInspectorSwitch(self):
        if ConfigManager.config["SELECTED"]["update_inspector"] == "True":
            self.SetTreeviewData()
        else:
            self.treeview.delete(*self.treeview.get_children())

    def ResetTreeview(self):
        self.treeview.destroy()
        self.treeScroll.destroy()
        self.InitTreeViewWidgets()
        self.SetTreeviewData()

    def SetTreeviewData(self, *args):
        if ConfigManager.config["SELECTED"]["update_inspector"] == "False":
            return

        # Clear all items
        self.treeview.delete(*self.treeview.get_children())

        # Load from dataset
        if ConfigManager.config["SELECTED"]["dataset"] != "":
            files = ImageLoader().GetAllImagesInFolder(
                os.path.join(
                    DATASETS_PATH,
                    ConfigManager.config["SELECTED"]["dataset"],
                    IMAGE_FOLDER,
                )
            )
            for file in files:
                if file.endswith(".jpg"):
                    self.treeview.insert("", "end", text=file)

        # Load saved
        if ConfigManager.config["SELECTED"]["image"] != "":
            for item in self.treeview.get_children():
                if (
                    self.treeview.item(item, "text")
                    == ConfigManager.config["SELECTED"]["image"]
                ):
                    self.treeview.selection_set(item)
                    break
            # Enqueue to update image delayed
            self.after(1000, self.OnTreeviewClick)

    def OnAnnotationsClick(self, *args):
        ConfigManager.config["SELECTED"]["enable_annotations"] = str(
            self.enable_annotations_var.get()
        )
        ConfigManager.SaveConfig()
        self.OnTreeviewClick()

    def OnPredictionsClick(self, *args):
        ConfigManager.config["SELECTED"]["enable_predictions"] = str(
            self.enable_predictions_var.get()
        )
        ConfigManager.SaveConfig()
        self.OnTreeviewClick()

    def OnTreeviewClick(self, *args):
        if self.thread is not None:
            self.thread.stop()

        if self.treeview.selection() == ():
            return
        item = self.treeview.selection()[0]

        ConfigManager.config["SELECTED"]["image"] = self.treeview.item(item, "text")
        ConfigManager.config["SELECTED"]["plot_annotations"] = str(
            self.enable_annotations_var.get()
        )
        ConfigManager.config["SELECTED"]["plot_predictions"] = str(
            self.enable_predictions_var.get()
        )
        ConfigManager.config["SELECTED"][
            "best_predictions_count"
        ] = self.predictions_var.get()
        ConfigManager.SaveConfig()

        self.thread = PopenAndCall(self.SetImage, "python -m Modules.DataPlotter")

    def SetImage(self):
        img = Image.open(TEMP_IMAGE_PATH)
        # Resize to match window size
        # get width from free space in frame
        width = self.image_frame.winfo_width() - 10
        # get height from free space in frame
        height = self.image_frame.winfo_height() - 10
        img.thumbnail((width, height))

        self.image = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.image)
        self.image_label.image = self.image
        self.image_frame.update()
        self.image_frame.update_idletasks()

    def SaveImage(self):
        ImageLoader.SaveCurrentImage()

    def UpdatePredictionsCount(self, *args):
        new_value = self.predictions_var.get()
        # Remove everything that is not a digit
        self.predictions_var.set(
            "".join(filter(str.isdigit, self.predictions_var.get()))
        )
        if len(self.predictions_var.get()) > 10:
            self.predictions_var.set(
                self.predictions_var.get()[:10]
            )  # Limit to 10 digits

        if (
            new_value == self.predictions_var.get() and new_value != ""
        ):  # Input new digit
            ConfigManager.config["SELECTED"][
                "num_predictions"
            ] = self.predictions_var.get()
            ConfigManager.SaveConfig()
            self.OnTreeviewClick()
