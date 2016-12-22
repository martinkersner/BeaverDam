#!/usr/bin/env python

import cv2
import sqlite3
import ast
import numpy
import math
import os

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

def myfun(annot, current_keyframe, frame_number):
  rec = annot.get(frame_number)

  if rec == None: 
    # interpolation
    r1 = annot.get(current_keyframe)

    if r1["next_frame"] == -1:
        return None, None

    r2 = annot.get(r1["next_frame"])
    frac = (frame_number - current_keyframe) / (1.0 * (r1["next_frame"] - current_keyframe))
    
    rec = interpolate(r1, r2, frac)
  else:
    current_keyframe = frame_number
    
  return current_keyframe, rec

def getAnnotations(c):
  c.execute('SELECT annotation  FROM annotator_video WHERE ID = 4;')
  record = c.fetchone()
  s_record = str(record[0][1:-1].replace("\"", "\'").replace("true", "\'true\'").replace("false", "\'false\'"))
  return ast.literal_eval(s_record)

def getColor(obj_type):
  # TODO  set colors
  if obj_type == "Car":
    return (255,255,0)
  elif obj_type == "Pedestrian":
    return (0,255,0)
  elif obj_type == "Cyclist":
    return (0,255,255)
  elif obj_type == "Bus":
    return (255,255,255)
  elif obj_type == "Truck":
    return (0,0,0)

################################################################################
db_path    = "../db.sqlite3"
video_path = "/home/martin/DeepLearning/BeaverDam/annotator/static/videos/4.mp4" # TODO pass path through script parameters
crop_output_dir = "crop_output"
do_crop = True

conn = sqlite3.connect(db_path)
c = conn.cursor()
db_annotations =  getAnnotations(c)

annot_all = []
for obj in db_annotations:
  annot_tmp = {}

  for o in obj['keyframes']:
    tmp_frame_number = timeToFrameNumber(o['frame'])
    annot_tmp[tmp_frame_number] = {'h': o['h'], 'w': o['w'], 'x': o['x'], 'y': o['y'], 'type': obj['type']}

  keys = annot_tmp.keys()
  keys.sort()

  for i, k in enumerate(keys):
    if len(keys)-1 == i:
        annot_tmp[k]["next_frame"] = -1
    else:
        annot_tmp[k]["next_frame"] = keys[i+1]

  annot_all.append(annot_tmp)

# video
cap = cv2.VideoCapture(video_path)
frame_number = 0
current_keyframe = [0]*len(annot_all)

while(True):
  ret, frame = cap.read()
  clear_frame = frame.copy()
  drawRectangle(frame, 40, 150, 1200, 370, (0,0,255))

  for i, annot_tmp in enumerate(annot_all):
    if annot_tmp:
      current_keyframe[i], rec = myfun(annot_tmp, current_keyframe[i], frame_number)
      obj_type = annot_tmp[0]["type"]

      if rec:
        drawRectangle(frame, rec["x"], rec["y"], rec["w"], rec["h"], getColor(obj_type))
        drawText(frame, obj_type, rec["x"], rec["y"], getColor(obj_type))
        if do_crop:
          cropped_frame = cropImage(clear_frame, rec["x"], rec["y"], rec["w"], rec["h"])
          crop_output_path = os.path.join(crop_output_dir, str(i) + str(frame_number) + ".png") # directory for each class
          cv2.imwrite(crop_output_path, cropped_frame)
      else:
        annot_all[i] = None

  cv2.imshow('frame', frame)
  if cv2.waitKey(0) & 0xFF == ord('q'):
    break

  frame_number += 1
  print frame_number

cap.release()
cv2.destroyAllWindows()
