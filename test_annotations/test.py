#!/usr/bin/env python

import cv2
import sqlite3
import ast
import numpy
import math

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


################################################################################
db_path    = "../db.sqlite3"
video_path = "/home/martin/DeepLearning/BeaverDam/annotator/static/videos/4.mp4"
crop_output_dir = "crop_output"

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('SELECT annotation  FROM annotator_video WHERE ID = 4;')
record = c.fetchone()
s_record = str(record[0][1:-1].replace("\"", "\'").replace("true", "\'true\'"))
dict_record = ast.literal_eval(s_record)
print dict_record

annot = {}
for r in dict_record['keyframes']:
  tmp_frame_number = timeToFrameNumber(r['frame'])
  annot[tmp_frame_number] = {'h': r['h'], 'w': r['w'], 'x': r['x'], 'y': r['y']}

keys = annot.keys()
keys.sort()

for i,k in enumerate(keys):
  if len(keys)-1 == i:
      annot[k]["next_frame"] = -1
  else:
      annot[k]["next_frame"] = keys[i+1]

# video
cap = cv2.VideoCapture(video_path)
frame_number = 0
current_keyframe = 0
color = (255,255,255)

while(True):
  ret, frame = cap.read()
  clear_frame = frame.copy()
  drawRectangle(frame, 40, 100, 1200, 370, (0,0,255))

  if annot:
    current_keyframe, rec = myfun(annot, current_keyframe, frame_number)

    if rec:
      drawRectangle(frame, rec["x"], rec["y"], rec["w"], rec["h"], color)
      drawText(frame, "car", rec["x"], rec["y"], color)
      cropped_frame = cropImage(clear_frame, rec["x"], rec["y"], rec["w"], rec["h"])
      crop_output_path = crop_output_dir + str(frame_number) + ".png"
      cv2.imwrite(crop_output_path, cropped_frame)
    else:
      annot = None

  cv2.imshow('frame', frame)
  if cv2.waitKey(40) & 0xFF == ord('q'):
    break

  frame_number += 1
  print frame_number

cap.release()
cv2.destroyAllWindows()
