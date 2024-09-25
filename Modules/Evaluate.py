import sys
import configparser
import numpy as np
import json
import contextlib

from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

from Resources.Consts import *
from Modules.DataLoader import PathLoader


class Evaluator:
    def __init__(self):
        self.predicions_path = ""
        self.annotations_path = ""

    def Evaluate(self, config, name):
        self.evalutation_path = PathLoader.GetEvaluationsPath(config)
        self.predicions_path = PathLoader.GetAllPredictionsPath(config)
        self.annotations_path = PathLoader.GetAnnotationsPath(config)
        self.prediction_path = self.predicions_path + name + ".json"

        with contextlib.redirect_stdout(None):
            results = {}
            cocoGt = COCO(self.annotations_path)
            cocoDt = cocoGt.loadRes(self.prediction_path)

            self.imgIds = []
            for data in cocoDt.dataset["annotations"]:
                if data["image_id"] not in results:
                    results[data["image_id"]] = []
                    self.imgIds.append(data["image_id"])

            for i in range(0, 17):
                cocoGt = COCO(self.annotations_path)
                cocoGt.dataset["annotations"] = self.ClearAllKeypointsExcept(
                    i, cocoGt.dataset["annotations"]
                )
                self.cocoEval = COCOeval(cocoGt, cocoDt, "keypoints")
                for imgId in self.imgIds:
                    self.cocoEval.params.imgIds = [imgId]
                    self.cocoEval.evaluate()
                    self.cocoEval.accumulate()
                    self.cocoEval.summarize()
                    results[imgId].append(self.cocoEval.stats.tolist())

            # save results
            with open(self.evalutation_path + name + ".json", "w") as f:
                json.dump(results, f)


def ClearAllKeypointsExcept(self, keypointId, annotations):
    for ann in annotations:
        keypoints = np.array(ann["keypoints"]).reshape(-1, 3)
        for i in range(17):
            if i != keypointId:
                keypoints[i] = np.array([0, 0, 0])
        ann["keypoints"] = keypoints.reshape(-1).tolist()
        ann["num_keypoints"] = 1
        if np.sum(keypoints[:, 2]) == 0:
            ann["iscrowd"] = 1
    return annotations


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(SAVE_PATH)
    evaluator = Evaluator()
    evaluator.Evaluate(config, str(sys.argv[1]))
