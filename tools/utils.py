import json
import os
from collections import defaultdict
from tqdm import tqdm
import funcy
from sklearn.model_selection import train_test_split
import shutil
import glob
import logging
import subprocess
import cv2


KEYPOINTS_CLASS = [

]


class Logger:
    def __init__(self, configs: dict):
        self.configs = configs

    def set_logger(self, log_name: str):
        self.logger = logging.getLogger(__name__)
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s|%(filename)s:%(lineno)s] : %(message)s')
        stream_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(os.path.join(self.configs.get("target_dir"), f"{log_name}_log.txt"))
        stream_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(level=logging.DEBUG)

    def view_error_files(self, error_logs: dict):
        self.logger.debug("\n======================\n"
                          f"ERROR FILE: {error_logs}"
                          "\n======================\n")


class Utils:
    def __init__(self):
        self.json_files = defaultdict(str)
        self.error_logs = defaultdict(str)

    @property
    def update_errros(self):
        return self.error_logs

    @update_errros.setter
    def update_errors(self, error_logs:dict, name: str):
        pass

    def load_image(self, image_path: str):
        try:
            image = cv2.imread(image_path)
            return image
        except:
            message = f'there is no image from {image_path}'
            return message

    def draw_circle(self, image, keypoints, radian=20, color=(0,255,0), thickness=-1):
        for per_instance in keypoints:
            for pi_keypoint in per_instance:
                center_points = pi_keypoint[:2]
                cv2.circle(image, tuple(center_points), radian, color, thickness)
        return image

    def draw_line(self, image, keypoints, skeleton, colors, thickness=-1):
        for per_instance in keypoints:
            for sk, c in zip(skeleton, colors):
                center_points = [tuple(per_instance[sk[0]][:2]), tuple(per_instance[sk[1]][:2])]
                cv2.line(image, center_points[0], center_points[1], c, thickness)
        return image

    def save_images(self, image, output_dir, name):
        cv2.imwrite(os.path.join(output_dir, f"results_{name}"), image)

    def load_json(self, path: str):
        with open(path, mode='r', encoding='utf8') as file:
            data = json.load(file)
        return data

    def file_check(self, root_dir: str, ext: str):
        self.raw_json_files = defaultdict(str)
        for file_path in glob.iglob(os.path.join(root_dir, f"**/*{ext}"), recursive=True):
            name = os.path.basename(file_path)
            self.raw_json_files[name] = file_path

    def find_jsons(self, root_dir: str, logger, default_ext=".json"):
        self.file_check(root_dir, default_ext)
        for name, path in tqdm(self.raw_json_files.items(), desc=os.path.basename(root_dir)):
            self.json_files[name] = self.load_json(path)

    def is_dir(self, root_dir: str):
        if not os.path.isdir(root_dir):
            os.makedirs(root_dir)

    def rsync_images(self, source_dir: str, target_dir: str, logger, ext=".jpg"):
        logger.debug(f"\n==================\n"
                     f"do rsync images"
                     f"\n==================\n")
        save_dir = os.path.join(target_dir, "images")
        self.is_dir(save_dir)
        command = f"rsync -avzh --no-group --no-owner --no-perms {source_dir}/*{ext} {save_dir}/"

        while True:
            try:
                subprocess.check_call(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                proc = subprocess.Popen(command, shell=True)
                if proc.wait() == 0:
                    break
            except subprocess.CalledProcessError:
                self.error_logs["rsync_errors"] = source_dir
                logger.debug(f"ERROR: {source_dir} is not rsync")
                break
        logger.debug(f"\n==================\n"
                     f"source: {source_dir} to target: {target_dir} rsync is done"
                     f"\n==================\n")


    def copy_images(self, source_dir:str, target_dir:str, image_data:dict, type: str):
        self.is_dir(os.path.join(target_dir, type))
        for image_ann in tqdm(image_data):
            shutil.copy(os.path.join(source_dir, "images", image_ann.get("file_name")), os.path.join(target_dir, type, image_ann.get("file_name")))

class Merge:
    pass

class Copy:
    pass

class Splits:
    pass

class COCO:
    def __init__(self, init_coco):
        self.coco_annotations = init_coco
        self.image_id = 0
        self.annotation_id = 0

    def convert_image_format(self, image_ann: dict):
        '''
            이번에 전달받은 format 의 경우 image 1장당 json 1장
        '''

        convert_ann = {
            "license": 1,
            "file_name": image_ann.get("filename"),
            "width": image_ann.get("width"),
            "height": image_ann.get("height"),
            "date_captured": "",
            "id": self.image_id
        }

        return convert_ann

    def area(self, bbox):
        return bbox[2] * bbox[3]

    def convert_ann_format(self, anns: list):
        new_anns = []
        for ann in anns:
            if ann.get("points"):
                new_anns.append({
                    "area": self.area(ann.get("box")),
                    "category_id": 1, # TODO: keypoints detection 의 경우 category_id 가 1
                    "iscrowd": 0,
                    "bbox": ann.get("box"), # 이번에 전달받은 데이터 포멧은 xywh
                    "id": self.annotation_id,
                    "image_id": self.image_id,
                    "keypoints": ann.get("points"),
                    "num_keypoints": int(len(ann.get("points")) / 3)
                })
                self.annotation_id += 1
        return new_anns

    def convert_raw_to_coco(self, json_files: dict):
        for file_name, json_data in tqdm(json_files.items()):
            images = self.convert_image_format(json_data.get("images")[0])
            annotations = self.convert_ann_format(json_data.get("annotations"))

            self.coco_annotations["images"].append(images)
            self.coco_annotations["annotations"].extend(annotations)

            self.image_id += 1

    def split_train_val(self, ratio: float):
        info = self.coco_annotations['info']
        licenses = self.coco_annotations['licenses']
        images = self.coco_annotations['images']
        annotations = self.coco_annotations['annotations']
        categories = self.coco_annotations['categories']

        images_with_annotations = funcy.lmap(lambda a: int(a['image_id']), annotations)

        train_images, val_images = train_test_split(images, train_size=ratio)
        train_annotationns = self.filter_annotations(annotations, train_images)
        val_annnotations = self.filter_annotations(annotations, val_images)

        train_datasets = self.make_datasets(info, licenses, train_images, train_annotationns, categories)
        val_datasets = self.make_datasets(info, licenses, val_images, val_annnotations, categories)

        return train_datasets, val_datasets

    def filter_annotations(self, annotations, images):
        image_ids = funcy.lmap(lambda i: int(i['id']), images)
        return funcy.lfilter(lambda a: int(a['image_id']) in image_ids, annotations)

    def make_datasets(self, info, licenses, images, annotations, categories):
        dataset = {
            "info": info,
            "licenses": licenses,
            "images": images,
            "annotations": annotations,
            "categories": categories
        }

        return dataset

    def save_coco(self, target_dir: str, datasets: dict):
        with open(target_dir, "wt", encoding="UTF-8") as coco:
            json.dump(datasets, coco, indent=2, sort_keys=True)


class Meta:
    def __init__(self):
        self.coco_format = self.init_coco_format()

    def init_coco_format(self):
        coco_json = {
            "images": [],
            "annotations": [],
            "categories": [],
            "info": {
                "contributor": "AISTUDIO",
                "year": 2021,
                "date_created": "Fri Jun 05 2020 09:41:21 +0900",
                "description": "",
                "version": 1,
                "url": "https://www.aistudio.co.kr"
            },
            "licenses": {
                "id": 0,
                "name": "aistudio",
                "url": ""
            }
        }
        return coco_json

    def update_coco_keypoints_annotations(self, images, annotations, categories):
        self.coco_format["images"] = images
        self.coco_format["annotations"] = annotations
        self.coco_format["categories"] = categories




if __name__ == '__main__':
    source_dir = '/mnt/dms/keypoints/1_inspected_data/sports/whole'
    target_dir = '/mnt/dms/keypoints/3_run_data/sports/whole/1st_training'

    utils = Utils()

    train_data = utils.load_json(os.path.join(source_dir, "annotations" ,"train.json"))
    val_data = utils.load_json(os.path.join(source_dir, "annotations", "val.json"))

    utils.copy_images(source_dir, target_dir, train_data.get("images"), "train")
    utils.copy_images(source_dir, target_dir, val_data.get("images"), "val")