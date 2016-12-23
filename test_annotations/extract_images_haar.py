#!/usr/bin/env python
# Martin Kersner, m.kersner@gmail.com
# 2016/12/23

import os
import sys
import cv2
import sqlite3
import ast
import numpy
import math

BLUE_COLOR_   = (255,0,0)
GREEN_COLOR_  = (0,255,0)
RED_COLOR_    = (0,0,255)
WHITE_COLOR_  = (255,255,255)
BLACK_COLOR_  = (0,0,0)
YELLOW_COLOR_ = (0,255,255)

NOT_YET_ = -1

def drawRectangle(frame, x, y, w, h, color=(255,255,255)):
  p1 = (int(x), int(y))
  p2 = (int(x+w), int(y+h))

  cv2.rectangle(frame, p1, p2, color) 

def drawText(img, text, x, y, color=(255,255,255)):
  offset = -5
  cv2.putText(img, text, (int(x), int(y+offset)), cv2.FONT_HERSHEY_PLAIN, 1.0, color)

def cropImage(img, x, y, w, h):
  return img[int(y):int(y+h), int(x):int(x+w)]

def timeToFrameNumber(t, fps=30):
  frame_number = t*fps

  if math.modf(frame_number)[0] >= 0.5:
    return int(math.ceil(frame_number))
  else:
    return int(math.floor(frame_number))

def interpolate(r1, r2, frac):
  if (frac < 0 or frac > 1):
    print "interpolation error"
    exit(1)

  ifrac = 1.0 - frac;

  x1 = int(r1["x"]*ifrac + r2["x"]*frac)
  y1 = int(r1["y"]*ifrac + r2["y"]*frac)
  x2 = int((r1["x"]+r1["w"])*ifrac + (r2["x"]+r2["w"])*frac)
  y2 = int((r1["y"]+r1["h"])*ifrac + (r2["y"]+r2["h"])*frac)

  rec = {}
  rec["x"] = x1
  rec["y"] = y1
  rec["w"] = x2-x1
  rec["h"] = y2-y1

  return rec

def getNextCouple(lst, idx):
  if (idx >= len(lst)-1):
    return None

  d = {}
  d["prev"] = lst[idx]
  d["next"] = lst[idx+1]

  return d

def getFrac(frame_number, current_keyframe, next_keyframe):
  return (frame_number - current_keyframe) / (1.0 * (next_keyframe - current_keyframe))

def getRect(annot, current_keyframe, frame_number):
  rec = annot.get(frame_number)

  if rec == None: 
    # interpolation
    r1 = annot.get(current_keyframe)

    if r1["next_frame"] == -1:
        return None, current_keyframe

    if frame_number < current_keyframe:
        return NOT_YET_, current_keyframe

    r2 = annot.get(r1["next_frame"])
    
    frac = getFrac(frame_number, current_keyframe, r1["next_frame"])
    rec = interpolate(r1, r2, frac)
  else:
    # keyframe
    current_keyframe = frame_number
    
  return rec, current_keyframe

def getAnnotations(c, video_id):
  c.execute("SELECT annotation  FROM annotator_video WHERE ID = {0};".format(video_id))
  record = c.fetchone()
  s_record = str(record[0][1:-1].replace("\"", "\'").replace("true", "\'true\'").replace("false", "\'false\'"))
  return ast.literal_eval(s_record)

def getColor(obj_type):
  if obj_type == "Car":
    return RED_COLOR_
  elif obj_type == "Pedestrian":
    return GREEN_COLOR_
  elif obj_type == "Cyclist":
    return BLUE_COLOR_
  elif obj_type == "Bus":
    return WHITE_COLOR_
  elif obj_type == "Truck":
    return BLACK_COLOR_

def mkdir(directory):
  if not os.path.exists(directory):
    os.makedirs(directory)

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

def reformatObject(obj, obj_type):
  annot = {}
  
  for o in obj:
    tmp_frame_number = timeToFrameNumber(o["frame"])
    annot[tmp_frame_number] = {"h": o["h"], "w": o["w"], "x": o["x"], "y": o["y"], "type": obj_type}
  
  keys = annot.keys()
  keys.sort()
  
  for i, k in enumerate(keys):
    if (len(keys)-1) == i:
        annot[k]["next_frame"] = -1
    else:
        annot[k]["next_frame"] = keys[i+1]
  
  return annot, timeToFrameNumber(obj[0]["frame"])

################################################################################

def main():
  db_path, video_path, output_path, video_id = getParameters(sys.argv)
  
  do_crop = True
  
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  db_annotations =  getAnnotations(c, video_id)
  
  annot = []
  current_keyframe = []

  if isinstance(db_annotations, tuple): # more than one annotated object
    for idx, obj in enumerate(db_annotations):
      a, ck = reformatObject(obj["keyframes"], obj["type"])
      annot.append(a)
      current_keyframe.append(ck)
  else: # one annotated object
      a, ck = reformatObject(db_annotations["keyframes"], db_annotations["type"])
      annot.append(a)
      current_keyframe.append(ck)

  # video
  cap = cv2.VideoCapture(video_path)
  frame_number = 0
  
  while(True):
    ret, frame = cap.read()
    clear_frame = frame.copy()
    drawRectangle(frame, 40, 150, 1200, 370, YELLOW_COLOR_) # ROI
  
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
