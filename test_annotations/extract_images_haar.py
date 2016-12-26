#!/usr/bin/env python
# Martin Kersner, m.kersner@gmail.com
# 2016/12/23

import os
import sys
import cv2
from utils import *
from colors import *

NOT_YET_ = -1

def saveCrop(img, path, frame_number, obj_type, ext="png"):
  mkdir(path)
  object_path = os.path.join(path, obj_type)
  mkdir(object_path)
  output_path = os.path.join(object_path, str(frame_number) + "." + ext)

  cv2.imwrite(output_path, img)

def getParameters(argv):
  if len(argv) != 5:
    print "Usage:"
    print "./extract_images_haar.py path/to/db video_id path/to/video path/to/output/folder "
    exit(1)

  db_path     = argv[1]
  video_id    = argv[2]
  video_path  = argv[3]
  output_path = argv[4]

  return db_path, video_path, output_path, video_id

################################################################################

ROI = {"x":        40,
       "y":       150,
       "width":  1200,
       "height":  370}

def main():
  db_path, video_path, output_path, video_id = getParameters(sys.argv)
  
  do_crop = True
  
  db_annotations =  getAnnotations(db_path, video_id)
  
  annot, current_keyframe = convertAnnotations(db_annotations)

  # video
  cap = cv2.VideoCapture(video_path)
  frame_number = 0
  
  while(True):
    ret, frame = cap.read()
    clear_frame = frame.copy()
    drawRectangle(frame, ROI["x"], ROI["y"], ROI["width"], ROI["height"], YELLOW_COLOR_) # ROI
  
    for idx, a in enumerate(annot):
      if a:
        rect, current_keyframe[idx] = getRect(a, current_keyframe[idx], frame_number)
  
        if rect == NOT_YET_:
          pass
        elif rect:
          # drawing
          obj_type = a.values()[0]["type"]
          drawRectangle(frame, rect["x"], rect["y"], rect["w"], rect["h"], getColor(obj_type))
          drawText(frame, obj_type, rect["x"], rect["y"], getColor(obj_type))

          # cropping
          if do_crop:
            cropped_frame = cropImage(clear_frame, rect["x"], rect["y"], rect["w"], rect["h"])
            saveCrop(cropped_frame, output_path, frame_number, obj_type)
        else:
          # all annotations for particular object were already displayed
          # => remove object annotation
          annot[idx] = None
  
    cv2.imshow("frame", frame)
    if cv2.waitKey(0) & 0xFF == ord('q'):
      break
  
    frame_number += 1
    print frame_number
  
  cap.release()
  cv2.destroyAllWindows()

if __name__ == "__main__":
  main()
