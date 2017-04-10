#!/usr/bin/env python
# Martin Kersner, m.kersner@gmail.com
# 2016/12/23

import os
import sys
import cv2
from pascal_voc_writer import PascalVocWriter 
from utils import *
from colors import *

# TODO truncated, difficult

def saveCrop(img, path, name):
  mkdir(path)
  output_path = os.path.join(path, name)

  cv2.imwrite(output_path, img)

def makeImageName(frame_number, ext):
  return str(frame_number) + "." + ext

def getParameters(argv):
  if len(argv) != 5:
    print "Usage:"
    print "./extract_pascal_voc.py path/to/db video_id path/to/video path/to/output/folder"
    exit(1)

  db_path     = argv[1]
  video_id    = argv[2]
  video_path  = argv[3]
  output_path = argv[4]

  return db_path, video_path, output_path, video_id

def main():
  do_draw = False

  db_name = "HY" # not important
  ext     = "jpg"

  annotations_dir_name = "annotations"
  images_dir_name      = "images"

  ROI = {"x": 0,
         "y": 0,
         "w": 1280,
         "h": 720}

  ##############################################################################

  db_path, video_path, output_path, video_id = getParameters(sys.argv)
  db_annotations = getAnnotations(db_path, video_id)
  annot, current_keyframe = convertAnnotations(db_annotations)
  truncated = [0]*len(annot)

  mkdir(output_path)

  # video
  cap = cv2.VideoCapture(video_path)
  frame_width  = int(cap.get(3))
  frame_height = int(cap.get(4))
  depth        = 3 # expect video with 3 color channels
  dims = (frame_height, frame_width, depth)

  frame_number = 0
  
  while(True):
    ret, frame = cap.read()
    if not ret: break

    clear_frame = frame.copy()
    # drawRectangle(frame, ROI["x"], ROI["y"], ROI["w"], ROI["h"], YELLOW_COLOR_) # ROI
  
    tmp_img_name = makeImageName(frame_number, ext)
    pascal_writer = PascalVocWriter(output_path,
                                    tmp_img_name,
                                    dims,
                                    databaseSrc=db_name)

    for idx, a in enumerate(annot):
      try:
        rect, current_keyframe[idx], truncated[idx] = getRect(a, current_keyframe[idx], truncated[idx], frame_number)
      except (NoAnnotationException, NoAnnotationInFrameException):
        continue
      except LastObjectKeyFrameException:
        # all annotations for particular object were already displayed
        # => remove object annotation
        annot[idx] = None
        if finishedAnnotating(annot):
          exit()
  
      if rect:
        rect = cropRectangle(ROI, rect)
        obj_type = a.values()[0]["type"]

        if do_draw:
          drawRectangle(frame, rect["x"], rect["y"], rect["w"], rect["h"], getColor(obj_type)) # object
          drawText(frame, obj_type, rect["x"], rect["y"], getColor(obj_type))

        # image
        cropped_frame = cropImage(clear_frame, ROI["x"], ROI["y"], ROI["w"], ROI["h"])
        saveCrop(cropped_frame, os.path.join(output_path, images_dir_name), tmp_img_name)

        # annotation
        pascal_writer.addBndBox(rect["x"]-ROI["x"]+1,
                                rect["y"]-ROI["y"]+1,
                                rect["x"]-ROI["x"]+rect["w"],
                                rect["y"]-ROI["y"]+rect["h"],
                                obj_type,
                                truncated[idx])

        pascal_writer.save(os.path.join(output_path, annotations_dir_name))

    if do_draw:
      cv2.imshow("frame", frame)
      if cv2.waitKey(0) & 0xFF == ord('q'):
        break

    frame_number += 1
    print frame_number
  
  cap.release()

  if do_draw:
    cv2.destroyAllWindows()

if __name__ == "__main__":
  main()
