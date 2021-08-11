
Detectron2 is Facebook AI Research's next generation software system
that implements state-of-the-art object detection algorithms.
It is a ground-up rewrite of the previous version,
[Detectron](https://github.com/facebookresearch/Detectron/),
and it originates from [maskrcnn-benchmark](https://github.com/facebookresearch/maskrcnn-benchmark/).

## Quick Start
shell command
1. `conda create -n keypoint python==3.7`
2. `conda activate keypoint`
3. `git clone -b keypoints_infer --single-branch http://192.168.1.126:9000/lab/keypoints_detection.git`
   - login is required (username, password)
4. `cd keypoints_detection`
5. setup
   ```
   pip install -r requirement.txt
   python setup.py build develop
   ```
7. execution
   ```
   python tools/magic.py --config_file $CONFIG_FILE_PATH --image_path $IMAGE_PATH --result_path $RESULT_PATH
   
   # ex.
   python tools/magic.py --config_file configs/COCO-Keypoints/keypoint_sports.yaml --image_path outputs/soccer.jpg
   ```

## License

Detectron2 is released under the [Apache 2.0 license](LICENSE).
