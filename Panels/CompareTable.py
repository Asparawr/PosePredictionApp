import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

from Modules.Events import EventManager
from Modules.Threading import PopenAndCall
from Resources.Consts import TEMP_COMPARE_PATH


class CompareTable(ttk.Frame):
    def __init__(self, parent, app, style):
        super().__init__()
        self.style = style
        self.app = app
        self.reload_thread = None

        self.frame = ttk.Frame(parent, padding=(0, 10))
        self.frame.grid(
            row=1, rowspan=3, column=1, padx=(0, 20), pady=(0, 0), sticky="nsew"
        )
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self.InitTableWidgets()
        EventManager.set_compare_dataset_event += self.ReloadTable
        EventManager.set_compare_type_event += self.ReloadTable
        EventManager.set_compare_predictions_event += self.ReloadTable
        EventManager.set_compare_types_event += self.ReloadTable
        EventManager.set_compare_ap_event += self.ReloadTable
        EventManager.set_compare_ar_event += self.ReloadTable

    def InitTableWidgets(self):
        # Frame for the image
        self.image_frame = ttk.Frame(self.frame)
        self.image_frame.grid(
            row=0,
            column=0,
            padx=(5, 10),
            pady=(20, 10),
            sticky="nsew",
        )

        # Image
        self.image = tk.PhotoImage()
        self.image_label = ttk.Label(self.image_frame, image=self.image)
        self.image_label.pack(expand=True)

    def ReloadTable(self):
        # In another thread to prevent lag
        if self.reload_thread is not None and self.reload_thread.stopped() != True:
            self.reload_thread.stop()
        width = self.image_frame.winfo_width() - 10
        height = self.image_frame.winfo_height() - 10
        self.reload_thread = PopenAndCall(
            self.UpdateTable,
            "python -m Modules.EvaluateTable " + str(width) + " " + str(height),
        )

    def UpdateTable(self, *args):
        img = Image.open(TEMP_COMPARE_PATH)
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
