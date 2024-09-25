import sys
import pandas as pd
import json
import plotly.graph_objects as go

from Modules.DataLoader import PathLoader
from Modules.Translate import TranslateManager
from Resources.Consts import *
from Modules.Config import ConfigManager


def CreateEvaluationTable(width, height):
    type = ConfigManager.config["COMPARE"]["type"]
    if ConfigManager.config["COMPARE"]["predictions"] != "":
        predictions = json.loads(ConfigManager.config["COMPARE"]["predictions"])
    else:
        predictions = []

    if ConfigManager.config["COMPARE"]["types"] != "":
        types = json.loads(ConfigManager.config["COMPARE"]["types"])
    else:
        types = []

    if ConfigManager.config["COMPARE"]["ap"] != "":
        ap = json.loads(ConfigManager.config["COMPARE"]["ap"])
    else:
        ap = []

    if ConfigManager.config["COMPARE"]["ar"] != "":
        ar = json.loads(ConfigManager.config["COMPARE"]["ar"])
    else:
        ar = []

    predictions_paths = [prediction[:-5] for prediction in predictions]
    predictions_names = [prediction[:-5].split("/")[-1] for prediction in predictions]
    table = pd.DataFrame()
    if type == COMPARE_TYPES[0]:
        # AP/AR as columns
        # Predictions as row index
        table = pd.DataFrame(index=predictions_names, columns=ap + ar)

        for i, prediction in enumerate(predictions_paths):
            for ap_type in ap:
                table.loc[predictions_names[i], ap_type] = CalculateAPAR(
                    prediction,
                    AP_TYPES[ap_type],
                )
            for ar_type in ar:
                table.loc[predictions_names[i], ar_type] = CalculateAPAR(
                    prediction,
                    AR_TYPES[ar_type],
                )
    elif type == COMPARE_TYPES[1]:
        # Keypoints as columns
        # Predictions + AP/AR as row index
        indexes = []
        for name in predictions_names:
            for ap_type in ap:
                indexes.append(name + " " + ap_type)
            for a in ar:
                indexes.append(name + " " + a)
        # TranslateManager each type
        tran_types = types.copy()
        for i, pose in enumerate(tran_types):
            tran_types[i] = TranslateManager.Translate(pose)
        table = pd.DataFrame(index=indexes, columns=tran_types)

        for i, prediction in enumerate(predictions_paths):
            for ap_type in ap:
                for j, pose in enumerate(types):
                    table.loc[predictions_names[i] + " " + ap_type, tran_types[j]] = (
                        CalculateKeypoint(
                            prediction,
                            KEYPOINTS[pose],
                            AP_TYPES[ap_type],
                        )
                    )
            for ar_type in ar:
                for j, pose in enumerate(types):
                    table.loc[predictions_names[i] + " " + ar_type, tran_types[j]] = (
                        CalculateKeypoint(
                            prediction,
                            KEYPOINTS[pose],
                            AR_TYPES[ar_type],
                        )
                    )
    elif type == COMPARE_TYPES[2]:
        # Pose types as columns
        # Predictions + AP/AR as row index
        indexes = []
        for name in predictions_names:
            for ap_type in ap:
                indexes.append(name + " " + ap_type)
            for a in ar:
                indexes.append(name + " " + a)
        types_names = [pose[:-4] for pose in types]  # without csv
        table = pd.DataFrame(index=indexes, columns=types_names)

        for i, prediction in enumerate(predictions_paths):
            for ap_type in ap:
                for pose_type in types:
                    table.loc[predictions_names[i] + " " + ap_type, pose_type[:-4]] = (
                        CalculatePoseType(
                            prediction,
                            pose_type,
                            AP_TYPES[ap_type],
                        )
                    )
            for ar_type in ar:
                for pose_type in types:
                    table.loc[predictions_names[i] + " " + ar_type, pose_type[:-4]] = (
                        CalculatePoseType(
                            prediction,
                            pose_type,
                            AR_TYPES[ar_type],
                        )
                    )

    # round to 2 decimal places
    for col in table.columns:
        table[col] = table[col].apply(lambda x: round(x, 2))

    # Save table as image png
    table.reset_index(inplace=True)
    table.rename(columns={"index": ""}, inplace=True)

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(table.columns),
                    fill_color="paleturquoise",
                    align="center",
                    height=60,
                    font_size=22,
                ),
                cells=dict(
                    values=[table[col] for col in table.columns],
                    fill_color="lavender",
                    align="center",
                    height=60,
                    font_size=22,
                ),
            )
        ]
    )

    # remove background
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

    # remove borders
    fig.update_xaxes(showline=True, linewidth=2, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=2, linecolor="black", mirror=True)
    # make bigger
    fig.update_layout(width=width, height=height)

    fig.write_image(TEMP_COMPARE_PATH, format="png")

    # Save table as csv
    table.to_csv(TEMP_COMPARE_CSV_PATH, index=False)


def CalculateAPAR(prediction, id):
    with open(prediction + ".json") as f:
        data = json.load(f)
    out = 0
    count = 0
    for img in data:
        for keypoint in data[img]:
            if keypoint[id] != -1:
                out += keypoint[id]
                count += 1

    if count == 0:
        return -1
    return out / count


def CalculateKeypoint(prediction, keypoint_id, id):
    with open(prediction + ".json") as f:
        data = json.load(f)

    out = 0
    count = 0
    for img in data:
        if data[img][keypoint_id][id] != -1:
            out += data[img][keypoint_id][id]
            count += 1

    if count == 0:
        return -1
    return out / count


def CalculatePoseType(prediction, pose_file, id):
    with open(prediction + ".json") as f:
        data = json.load(f)
    out = 0
    count = 0
    pose_path = PathLoader.GetComparePoseTypesPath(ConfigManager.config) + pose_file
    with open(pose_path) as f:  # from csv
        img_pose_list = f.read().split("\n")

    for img_id in img_pose_list:
        if img_id in data:
            for keypoint in data[img_id]:
                if keypoint[id] != -1:
                    out += keypoint[id]
                    count += 1

    if count == 0:
        return -1
    return out / count


if __name__ == "__main__":
    CreateEvaluationTable(int(sys.argv[1]), int(sys.argv[2]))
