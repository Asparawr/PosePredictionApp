import csv
import pandas as pd

from Modules.Config import ConfigManager

translations = pd.read_csv(
    "Resources/Translations.csv",
    quotechar='"',
    delimiter=",",
    quoting=csv.QUOTE_ALL,
    skipinitialspace=True,
)


class TranslateManager:
    languageId = 1 if ConfigManager.config["DEFAULT"]["language"] == "pl" else 0

    @staticmethod
    def Translate(text):
        if TranslateManager.languageId != 0:
            for index, row in translations.iterrows():
                if row.iloc[0] == text:
                    out = row.iloc[TranslateManager.languageId]
                    if out != "" and pd.isna(out) == False:
                        return out
                    else:
                        return text
            # Add to translations
            translations.loc[translations.shape[0]] = [text, ""]
            translations.to_csv("Resources/Translations.csv", index=False)
        return text
