


import subprocess
import os
from pathlib import Path
import json

# source_dir = '/mnt/dms/keypoints/1_inspected_data/sports/whole/annotations'
# source_dir = '/mnt/dms/keypoints/1_inspected_data/sports/basketball/Basketball_1/annotations'
#
# with open(os.path.join(source_dir, "train.json")) as file:
#     data = json.load(file)
# print()
#
#


source_dir = "/mnt/dms/keypoints/0_raw_data/sports/football/football_3"
target_dir = "/mnt/dms/keypoints/1_inspected_data/sports/rsync_test"

command = f"rsync -avzh --no-group --no-owner --no-perms {source_dir}/*.jpg {target_dir}/"

Path(target_dir).mkdir(exist_ok=True, parents=True)
while True:
    try:
        subprocess.check_call(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        proc = subprocess.Popen(command, shell=True)
        if proc.wait() == 0:
            break
    except subprocess.CalledProcessError:
        print("subprocess error")
        break
print("DONE")
# proc.wait()
#
#
# configs = {
#   "root_dirs": [
#     "/mnt/dms/keypoints/0_raw_data/sports/basketball/Basketball_1",
#     "/mnt/dms/keypoints/0_raw_data/sports/basketball/Basketball_2",
#     "/mnt/dms/keypoints/0_raw_data/sports/basketball/Basketball_3",
#     "/mnt/dms/keypoints/0_raw_data/sports/basketball/Basketball_4",
#     "/mnt/dms/keypoints/0_raw_data/sports/basketball/Basketball_5",
#     "/mnt/dms/keypoints/0_raw_data/sports/football/football_1",
#     "/mnt/dms/keypoints/0_raw_data/sports/football/football_2",
#     "/mnt/dms/keypoints/0_raw_data/sports/football/football_3",
#     "/mnt/dms/keypoints/0_raw_data/sports/golf/Golf_1",
#     "/mnt/dms/keypoints/0_raw_data/sports/golf/Golf_2",
#     "/mnt/dms/keypoints/0_raw_data/sports/golf/Golf_3",
#     "/mnt/dms/keypoints/0_raw_data/sports/golf/Golf_4",
#     "/mnt/dms/keypoints/0_raw_data/sports/golf/Golf_5"
#   ],
#   "target_dir": "/mnt/dms/keypoints/1_inspected_data/sports/whole"
# }
#
# save_dir = os.path.join(configs.get("target_dir"), "images")
# Path(save_dir).mkdir(exist_ok=True, parents=True)
# for root_dir in configs.get("root_dir"):
#     while True:
#         print(f"{root_dir} rsync is starting now")
#         proc = subprocess.Popen(f"rsync -avzh {root_dir}/*.jpg {save_dir}/", shell=True)
#         if proc.wait() == 0:
#             break
#     print(f"{root_dir} file rsycn is DONE")