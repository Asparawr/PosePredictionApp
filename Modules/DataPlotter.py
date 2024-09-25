import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json

from Resources.Consts import (
    DATASETS_PATH,
    IMAGE_FOLDER,
    TEMP_IMAGE_PATH,
    ANNOTATION_FOLDER,
    SKELETON,
)
from Modules.DataLoader import PathLoader
from Modules.Config import ConfigManager
from Modules.Translate import TranslateManager


def PlotImage():
    imageId = ConfigManager.config["SELECTED"]["image"]
    dataset = ConfigManager.config["SELECTED"]["dataset"]
    plot_annotations = ConfigManager.config["SELECTED"]["enable_annotations"] == "1"
    plot_predictions = ConfigManager.config["SELECTED"]["enable_predictions"] == "1"
    best_predictions_count = (
        int(ConfigManager.config["SELECTED"]["best_predictions_count"])
        if ConfigManager.config["SELECTED"]["best_predictions_count"] != ""
        else 0
    )
    if dataset == "":
        return
    # Save Temp image with plot
    image_path = os.path.join(
        DATASETS_PATH,
        dataset,
        IMAGE_FOLDER,
        imageId,
    )
    imageId = int(imageId.split(".")[0])  # Remove extension
    image = plt.imread(image_path)

    # preserver Image size
    h, w, _ = image.shape
    dpi = 100
    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    font_size = (image.shape[0] + image.shape[1]) / 150
    dot_size = font_size * 5
    line_width = font_size / 3

    plt.imshow(image)
    plt.axis("off")

    # Plot annotations
    annotations = ConfigManager.config["SELECTED"]["annotations"]
    if plot_annotations and annotations != "":
        annotations_path = os.path.join(
            DATASETS_PATH,
            dataset,
            ANNOTATION_FOLDER,
            annotations,
        )

        # Plot annotations
        with open(annotations_path) as f:
            data = json.load(f)

        keypoints = None
        for annotation in data["annotations"]:
            if annotation["image_id"] == imageId:
                keypoints = annotation["keypoints"]
                for pair in SKELETON:
                    x1, y1 = (
                        keypoints[(pair[0] - 1) * 3],
                        keypoints[(pair[0] - 1) * 3 + 1],
                    )
                    x2, y2 = (
                        keypoints[(pair[1] - 1) * 3],
                        keypoints[(pair[1] - 1) * 3 + 1],
                    )
                    if x1 != 0 and x2 != 0 and y1 != 0 and y2 != 0:
                        plt.plot([x1, x2], [y1, y2], c="g", linewidth=line_width)
                        plt.scatter([x1, x2], [y1, y2], c="g", s=dot_size, marker="o")

    # Plot predictions
    prediction = ConfigManager.config["SELECTED"]["prediction"]
    predictions_path = PathLoader.GetPredictionPath(ConfigManager.config)
    if os.path.exists(predictions_path) and prediction != "" and plot_predictions:
        with open(predictions_path) as f:
            data = json.load(f)

        best_predictions = []
        min_score = 0
        for annotation in data:
            if annotation["image_id"] == imageId:
                if (
                    len(best_predictions) < best_predictions_count
                    or annotation["score"] > min_score
                ):
                    best_prediction = annotation
                    if len(best_predictions) > best_predictions_count:
                        for i, pred in enumerate(best_predictions):
                            if pred["score"] == min_score:
                                best_predictions.pop(i)
                                break
                    if min_score < annotation["score"]:
                        min_score = annotation["score"]
                    best_predictions.append(best_prediction)

        for best_prediction in best_predictions:
            keypoints = best_prediction["keypoints"]
            for pair in SKELETON:
                x1, y1 = (
                    keypoints[(pair[0] - 1) * 3],
                    keypoints[(pair[0] - 1) * 3 + 1],
                )
                x2, y2 = (
                    keypoints[(pair[1] - 1) * 3],
                    keypoints[(pair[1] - 1) * 3 + 1],
                )
                if x1 != 0 and x2 != 0 and y1 != 0 and y2 != 0:
                    plt.plot([x1, x2], [y1, y2], c="r", linewidth=line_width)
                    plt.scatter([x1, x2], [y1, y2], s=dot_size, marker="o", c="r")

    # Legend
    green_patch = mpatches.Patch(
        color="green", label=TranslateManager.Translate("Annotations")
    )
    red_patch = mpatches.Patch(
        color="red", label=TranslateManager.Translate("Predictions")
    )
    if plot_annotations and plot_predictions:
        plt.legend(
            handles=[green_patch, red_patch],
            loc="upper left",
            fontsize=font_size,
        )
    elif plot_annotations:
        plt.legend(
            handles=[green_patch],
            loc="upper left",
            fontsize=font_size,
        )
    elif plot_predictions:
        plt.legend(
            handles=[red_patch],
            loc="upper left",
            fontsize=font_size,
        )

    # Save plot
    plt.savefig(TEMP_IMAGE_PATH, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close()


if __name__ == "__main__":
    PlotImage()
