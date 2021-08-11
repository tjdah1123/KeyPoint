import os
import numpy as np
import torch
from torchvision import transforms
import cv2
from copy import deepcopy

from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor, default_setup


class D2BaseModel:

    def init(self, args):
        self.args = args

    def build_model(self):
        self.detectron_configs = self.setup()
        self.model = DefaultPredictor(self.detectron_configs)

    def setup(self):
        cfg = get_cfg()
        cfg.merge_from_file(self.args.config_file)
        # cfg.merge_from_list(self.args.opts)
        cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, cfg.MODEL.WEIGHTS)
        default_setup(cfg, self.args)
        cfg.freeze()
        return cfg


class D2KeypointModel(D2BaseModel):
    def __init__(self, args):
        super().init(args)
        super().build_model()

    def convert_keypoints(self, keypoints):
        keypoints = np.asarray(keypoints).astype(np.int32)
        return keypoints

    def __call__(self, image):
        outputs = self.model(image)
        scores = outputs["instances"].to("cpu").scores
        keypoints = outputs["instances"].to("cpu").pred_keypoints

        return self.convert_keypoints(keypoints)
