#!/usr/bin/env python
# Martin Kersner, m.kersner@gmail.com
# 2016/12/23

import os
import sys
import cv2
from utils import *
from colors import *

def saveCrop(img, path, frame_number, obj_id, obj_type, ext):
  object_path = os.path.join(path, obj_type)
  mkdir(object_path)
  output_path = os.path.join(object_path, str(frame_number) + "-" + str(obj_id) + "." + ext)

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

def main():
  do_draw = False
  ext     = "jpg"

  ROI = {"x": 40,
         "y": 150,
         "w": 1200,
         "h": 370}

  ##############################################################################

  db_path, video_path, output_path, video_id = getParameters(sys.argv)
  db_annotations =  getAnnotations(db_path, video_id)
  annot, current_keyframe = convertAnnotations(db_annotations)

  mkdir(output_path)

  # video
  cap = cv2.VideoCapture(video_path)

  frame_number = 0
  
  while(True):
    ret, frame = cap.read()
    if not ret: break

    clear_frame = frame.copy()
    drawRectangle(frame, ROI["x"], ROI["y"], ROI["w"], ROI["h"], YELLOW_COLOR_) # ROI
  
    for idx, a in enumerate(annot):
      try:
        rect, current_keyframe[idx] = getRect(a, current_keyframe[idx], frame_number)
      except (NoAnnotationException, NoAnnotationInFrameException):
        continue
      except LastObjectKeyFrameException:
        # all annotations for particular object were already displayed
        # => remove object annotation
        annot[idx] = None
        if finishedAnnotating(annot):
          exit()
  
      obj_type = a.values()[0]["type"]

      # drawing
      if do_draw:
        drawRectangle(frame, rect["x"], rect["y"], rect["w"], rect["h"], getColor(obj_type))
        drawText(frame, obj_type, rect["x"], rect["y"], getColor(obj_type))

      # cropping
      cropped_frame = cropImage(clear_frame, rect["x"], rect["y"], rect["w"], rect["h"])
      saveCrop(cropped_frame, output_path, frame_number, idx, obj_type, ext)

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
