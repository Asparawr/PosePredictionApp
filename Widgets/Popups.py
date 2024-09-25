import tkinter as tk
from tkinter import ttk
import os
from Resources.Consts import SAVE_PATH
from Modules.Config import ConfigManager
from Modules.Translate import TranslateManager


class BasePopup(tk.Toplevel):
    def __init__(self, master, app, title, message):
        super().__init__(master)
        self.title(title)
        self.geometry("300x100")
        self.resizable(False, False)
        self.app = app
        self.message = message
        self.CreateWidgets()

    def CreateWidgets(self):
        # Set background to full window
        self.configure(background=self.app.style.lookup("TFrame", "background"))
        label = ttk.Label(self, text=self.message)
        label.pack(pady=10)
        self.CreateBottomWidgets()

    def CreateBottomWidgets(self):
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=10)
        self.Style = ttk.Style()

        # Center the window
        x_cordinate = int((self.winfo_screenwidth() / 2) - (300 / 2))
        y_cordinate = int((self.winfo_screenheight() / 2) - (100 / 2))
        self.geometry("+{}+{}".format(x_cordinate, y_cordinate))


class BaseOkPopup(BasePopup):
    def __init__(self, master, app, title, message):
        super().__init__(master, app, title, message)

    def CreateBottomWidgets(self):
        super().CreateBottomWidgets()
        ok_button = ttk.Button(
            self.button_frame, text=TranslateManager.Translate("Ok"), command=self.ok
        )
        ok_button.grid(row=0, column=0, padx=10)

    def ok(self):
        self.destroy()


class BaseYesNoPopup(BasePopup):
    def __init__(self, master, app, title, message):
        super().__init__(master, app, title, message)

    def CreateBottomWidgets(self):
        super().CreateBottomWidgets()
        yes_button = ttk.Button(
            self.button_frame, text=TranslateManager.Translate("Yes"), command=self.yes
        )
        yes_button.grid(row=0, column=0, padx=10)

        no_button = ttk.Button(
            self.button_frame, text=TranslateManager.Translate("No"), command=self.no
        )
        no_button.grid(row=0, column=1, padx=10)

    def yes(self):
        pass

    def no(self):
        pass


class DownloadDataPopup(BaseYesNoPopup):
    def __init__(self, master, app):
        self.message = TranslateManager.Translate("Download default data?")
        super().__init__(
            master, app, TranslateManager.Translate("Download Data"), self.message
        )
        self.geometry("300x130")
        self.dont_show = False

    def CreateWidgets(self):
        # additional don't show again checkbox
        super().CreateWidgets()
        self.dont_show = ttk.Checkbutton(
            self, text=TranslateManager.Translate("Don't show again"), style="Switch"
        )
        self.dont_show.pack(pady=10)
        self.dont_show.state(["!selected"])
        self.dont_show.bind("<Button-1>", lambda event: self.SwitchShow())

    def yes(self):
        # Launch ../InitDownload.py
        os.system("python -m Modules.InitDownload")
        self.destroy()

    def no(self):
        self.destroy()
        if self.dont_show:
            ConfigManager.config["DEFAULT"]["downloaded"] = "True"
            with open(SAVE_PATH, "w") as configfile:
                ConfigManager.config.write(configfile)

    def SwitchShow(self):
        self.dont_show = not self.dont_show


class CallbackPopup(BaseYesNoPopup):
    def __init__(self, master, app, title, message, callback):
        self.callback = callback
        super().__init__(master, app, title, message)

    def yes(self):
        self.callback()
        self.destroy()

    def no(self):
        self.destroy()


class CallbackWithTextBoxPopup(BaseYesNoPopup):
    def __init__(self, master, app, title, message, callback):
        self.callback = callback
        super().__init__(master, app, title, message)

    def CreateBottomWidgets(self):
        self.entry = ttk.Entry(self)
        self.entry.pack(pady=10)
        super().CreateBottomWidgets()
        self.geometry("300x160")

    def yes(self):
        self.callback(self.entry.get())
        self.destroy()

    def no(self):
        self.destroy()


class ThreadPopup(BasePopup):
    def __init__(self, master, app, title, message, thread):
        self.thread = thread
        super().__init__(master, app, title, message)

    def CreateBottomWidgets(self):
        super().CreateBottomWidgets()
        stop_button = ttk.Button(
            self.button_frame,
            text=TranslateManager.Translate("Stop"),
            command=self.stop,
        )
        stop_button.grid(row=0, column=1, padx=10)

    def stop(self):
        # Stop the process
        self.thread.stop()
        self.destroy()
