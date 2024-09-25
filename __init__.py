import tkinter as tk
from tkinter import ttk
import os
import sys
from Resources.Consts import WIDTH, HEIGHT

from Widgets.Popups import DownloadDataPopup
from Panels.DatasetPanel import DatasetPanel
from Panels.InspectorPanel import InspectorPanel
from Panels.ModelPanel import ModelPanel
from Panels.PredictionPanel import PredictionPanel
from Panels.WindowOptionsPanel import WindowOptions

from Panels.CompareOptions import CompareOptions
from Panels.CompareTable import CompareTable
from Panels.CompareTreeViews import CompareTreeViews
from Modules.Config import ConfigManager
from Modules.Translate import TranslateManager

sys.path.insert(0, os.getcwd())


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Import the tcl file
        self.tk.call("source", "Resources\\Forest-ttk-theme-master\\forest-light.tcl")
        self.tk.call("source", "Resources\\Forest-ttk-theme-master\\forest-dark.tcl")

        # Create a style
        self.style = ttk.Style(self)

        self.title("Yolo")
        self.option_add("*tearOff", False)
        self.frame = ttk.Frame(self)
        self.frame.pack(fill="both", expand=True)

        # two rows
        self.frame.columnconfigure(0, weight=10000)
        self.frame.rowconfigure(0, weight=1)

        self.window_options = WindowOptions(self.frame, self, self.style)

        # Notebook
        notebook = ttk.Notebook(self.frame)
        notebook.grid(row=0, column=0, sticky="nsew")

        # init window frame
        self.overview_frame = ttk.Frame(notebook)
        self.overview_frame.pack(fill="both", expand=True)
        notebook.add(self.overview_frame, text=TranslateManager.Translate("Overview"))

        self.overview_frame.columnconfigure(index=0, weight=1)
        self.overview_frame.columnconfigure(index=1, weight=100)
        self.overview_frame.rowconfigure(index=1, weight=1000)
        self.overview_frame.rowconfigure(index=2, weight=20000)
        self.overview_frame.rowconfigure(index=3, weight=1000)

        # Panel classes
        self.dataset_panel = DatasetPanel(self.overview_frame, self, self.style)
        self.inspector_panel = InspectorPanel(self.overview_frame, self, self.style)
        self.model_panel = ModelPanel(self.overview_frame, self, self.style)
        self.prediction_panel = PredictionPanel(self.overview_frame, self, self.style)

        # Compare frame
        self.compare_frame = ttk.Frame(notebook)
        self.compare_frame.pack(fill="both", expand=True)
        notebook.add(self.compare_frame, text=TranslateManager.Translate("Compare"))

        self.compare_frame.columnconfigure(index=0, weight=1)
        self.compare_frame.columnconfigure(index=1, weight=6)
        self.overview_frame.rowconfigure(index=0, weight=1)
        self.compare_frame.rowconfigure(index=1, weight=100)

        # Compare panel classes
        self.compare_options = CompareOptions(self.compare_frame, self, self.style)
        self.compare_table = CompareTable(self.compare_frame, self, self.style)
        self.compare_treeviews = CompareTreeViews(self.compare_frame, self, self.style)

        # Center the self, and set minsize
        self.update()
        self.minsize(WIDTH, HEIGHT)
        x_cordinate = int((self.winfo_screenwidth() / 2) - (WIDTH / 2))
        y_cordinate = int((self.winfo_screenheight() / 2) - (HEIGHT / 2))
        self.geometry("+{}+{}".format(x_cordinate, y_cordinate))

        # Check default init
        if ConfigManager.config["DEFAULT"]["downloaded"] == "False":
            DownloadDataPopup(self.overview_frame, self)

    def Restart(self):
        self.destroy()
        global app
        app = App()


if __name__ == "__main__":
    global app
    app = App()
    app.mainloop()
