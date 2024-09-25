from tkinter import ttk
import tkinter as tk
from Widgets.Popups import CallbackPopup
from Resources.Consts import SAVE_PATH
from Modules.Events import EventManager
from Modules.Config import ConfigManager
from Modules.Translate import TranslateManager


class WindowOptions(ttk.Frame):
    def __init__(self, parent, app, style):
        super().__init__()
        self.style = style
        self.frame = ttk.Frame(parent)
        self.frame.grid(
            row=1, column=0, columnspan=2, padx=(0, 20), pady=(0, 0), sticky="nsew"
        )
        self.app = app

        if "theme" in ConfigManager.config["DEFAULT"]:
            if ConfigManager.config["DEFAULT"]["theme"] == "dark":
                self.isDarkMode = True
            else:
                self.isDarkMode = False
        else:
            self.isDarkMode = False

        # Set the theme
        self.SetDarkMode()

        # Language switch
        # e = tk.StringVar(value=option_menu_list[1])
        languages = ["", "English", "Polski"]
        current = (
            languages[2]
            if ConfigManager.config["DEFAULT"]["language"] == "pl"
            else languages[1]
        )
        self.selectedLanguage = tk.StringVar(value=current)
        self.languageMenu = ttk.OptionMenu(
            self.frame, self.selectedLanguage, *languages
        )
        self.languageMenu.grid(row=1, column=0, padx=20, pady=15, sticky="sw")
        self.languageMenu.config(width=15)
        self.selectedLanguage.trace_add("write", lambda *args: self.ChangeLanguage())

        # Dark mode switch
        switch = ttk.Checkbutton(
            self.frame, text=TranslateManager.Translate("Dark Mode"), style="Switch"
        )
        switch.grid(row=1, column=0, padx=180, pady=20, sticky="sw")
        switch.state(["selected"] if self.isDarkMode else ["!selected"])
        switch.bind("<Button-1>", lambda event: self.ChangeDarkMode())

        # Update inspector switch
        updateInspector = ttk.Checkbutton(
            self.frame,
            text=TranslateManager.Translate("Update Inspector"),
            style="Switch",
        )
        updateInspector.grid(row=1, column=0, padx=320, pady=20, sticky="sw")
        updateInspector.state(
            ["selected"]
            if ConfigManager.config["DEFAULT"]["update_inspector"] == "True"
            else ["!selected"]
        )
        updateInspector.bind("<Button-1>", lambda event: self.ChangeUpdateInspector())

    def ChangeDarkMode(self):
        self.isDarkMode = not self.isDarkMode
        self.SetDarkMode()
        ConfigManager.config["DEFAULT"]["theme"] = (
            "dark" if self.isDarkMode else "light"
        )
        ConfigManager.SaveConfig()
        EventManager.darkmode_switch_event()

    def SetDarkMode(self):
        if self.isDarkMode:
            self.style.theme_use("forest-dark")
        else:
            self.style.theme_use("forest-light")

    def ChangeUpdateInspector(self):
        ConfigManager.config["DEFAULT"]["update_inspector"] = (
            "True"
            if ConfigManager.config["DEFAULT"]["update_inspector"] == "False"
            else "False"
        )
        ConfigManager.SaveConfig()
        EventManager.update_inspector_switch_event()

    def ChangeLanguage(self):
        ConfigManager.config["DEFAULT"]["language"] = (
            "pl" if self.selectedLanguage.get() == "Polski" else "en"
        )
        ConfigManager.SaveConfig()
        CallbackPopup(
            self.frame,
            self.app,
            TranslateManager.Translate("Restart"),
            TranslateManager.Translate("Restart to apply changes"),
            self.app.Restart,
        )
