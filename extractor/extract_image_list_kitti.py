#!/usr/bin/env python
# Martin Kersner, m.kersner@gmail.com
# 2016/12/23

import os
import sys
import shutil
import cv2
import argparse
from pascal_voc_writer import PascalVocWriter 
from utils import *
from colors import *

# def saveCrop(img, path, name):
  # mkdir(path)
  # output_path = os.path.join(path, name)

  # cv2.imwrite(output_path, img)

def getParameters(argv):
  parser = argparse.ArgumentParser(description='Extract annotations from BeaverDam')
  parser.add_argument('--db_path', dest='db_path', required=True)
  parser.add_argument('--id', dest='id', required=True)
  parser.add_argument('--output_path', dest='output_path', required=True)

  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument('--kitti', dest='kitti_format', action='store_true')
  group.add_argument('--voc', dest='voc_format', action='store_true')

  return parser.parse_args()

def main():
  do_draw = False
  image_list = []

  img_db_path = "../annotator/static/images"
  annotations_dir_name = "ann"
  images_dir_name      = "img"

  # ROI = {"x": 0,
         # "y": 0,
         # "w": 1280,
         # "h": 720}

  # KITTI SIZE
  ROI = {"x": 0,
         "y": 0,
         "w": 1242,
         "h": 375}

  ##############################################################################

  args = getParameters(sys.argv)
  db_annotations, _, db_image_list, db_dirname = getImageListInformation(args.db_path, args.id)

  # TODO remove already existing
  # TODO warning
  # create output directory with image list name
  mkdir(args.output_path)
  output_full_path = os.path.join(args.output_path, db_dirname)
  mkdir(output_full_path)

  # create ann and img subdirectories
  mkdir(os.path.join(output_full_path, annotations_dir_name))
  mkdir(os.path.join(output_full_path, images_dir_name))

  # path to directory of input images
  img_input_path = os.path.join(img_db_path, db_dirname)

  annotation_converted = {}
  for ann in db_annotations:
    keyframe = ann["keyframes"][0]["frame"]
    if keyframe in annotation_converted:
      annotation_converted[keyframe].append(ann)
    else:
      annotation_converted[keyframe] = [(ann)]

  for keyframe in annotation_converted:
    image_list.append(keyframe)
    image_name = db_image_list[keyframe].split(".")[0]

    # drawRectangle(frame, ROI["x"], ROI["y"], ROI["w"], ROI["h"], YELLOW_COLOR_) # ROI
  
    for ann in annotation_converted[keyframe]:
      rect = getRectImageList(ann["keyframes"][0]) # each annotated object has its won annotation
      obj_type = ann["type"]

      # if do_draw:
        # drawRectangle(frame, rect["x"], rect["y"], rect["w"], rect["h"], getColor(obj_type)) # object
        # drawText(frame, obj_type, rect["x"], rect["y"], getColor(obj_type))

      # image
      # cropped_frame = cropImage(clear_frame, ROI["x"], ROI["y"], ROI["w"], ROI["h"])
      # saveCrop(cropped_frame, os.path.join(output_path, images_dir_name), tmp_img_name)

      # annotation
      if args.kitti_format:
        with open(os.path.join(output_full_path, annotations_dir_name, str(image_name)+".txt"), "a") as f: 
          f.write("{} 0.0 0 0.0 {} {} {} {} 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n".format(obj_type, rect["x"], rect["y"], rect["x"]+rect["w"], rect["y"]+rect["h"]))

      # if do_draw:
        # cv2.imshow("frame", frame)
        # if cv2.waitKey(0) & 0xFF == ord('q'):
          # break

  # copy images
  for idx in image_list:
    shutil.copyfile(os.path.join(img_input_path, db_image_list[idx]),
                    os.path.join(output_full_path, images_dir_name, db_image_list[idx]))
  
  # if do_draw:
    # cv2.destroyAllWindows()

if __name__ == "__main__":
  main()
