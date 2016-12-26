# Martin Kersner, m.kersner@gmail.com
# 2016/12/26 

import os
import math
import ast
import sqlite3
import cv2

LAST_FRAME_ = -1

class NoAnnotationException(Exception):
  pass

class NoAnnotationInFrameException(Exception):
  pass

class LastObjectKeyFrameException(Exception):
  pass

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
  if not annot:
    raise(NoAnnotationException)

  rec = annot.get(frame_number)

  if rec == None: 
    # interpolation
    r1 = annot.get(current_keyframe)

    if r1["next_frame"] == LAST_FRAME_:
      raise(LastObjectKeyFrameException)

    if frame_number < current_keyframe:
      raise(NoAnnotationInFrameException)

    r2 = annot.get(r1["next_frame"])
    
    frac = getFrac(frame_number, current_keyframe, r1["next_frame"])
    rec = interpolate(r1, r2, frac)
  else:
    # keyframe
    current_keyframe = frame_number
    
  return rec, current_keyframe

def getAnnotations(db_path, video_id):
  with sqlite3.connect(db_path) as conn:
    c = conn.cursor()
    c.execute("SELECT annotation  FROM annotator_video WHERE ID = {0};".format(video_id))
    record = c.fetchone()
    s_record = str(record[0][1:-1].replace("\"", "\'").replace("true", "\'true\'").replace("false", "\'false\'"))
    return ast.literal_eval(s_record)

def mkdir(directory):
  if not os.path.exists(directory):
    os.makedirs(directory)

def reformatObject(obj, obj_type):
  annot = {}
  
  for o in obj:
    tmp_frame_number = timeToFrameNumber(o["frame"])
    annot[tmp_frame_number] = {"h": o["h"], "w": o["w"], "x": o["x"], "y": o["y"], "type": obj_type}
  
  keys = annot.keys()
  keys.sort()
  
  for i, k in enumerate(keys):
    if (len(keys)-1) == i:
        annot[k]["next_frame"] = LAST_FRAME_
    else:
        annot[k]["next_frame"] = keys[i+1]
  
  return annot, timeToFrameNumber(obj[0]["frame"])

def convertAnnotations(db_annotations):
  annot      = []
  current_kf = []

  if isinstance(db_annotations, tuple): # more than one annotated object
    for idx, obj in enumerate(db_annotations):
      a, ck = reformatObject(obj["keyframes"], obj["type"])
      annot.append(a)
      current_kf.append(ck)
  else: # one annotated object
      a, ck = reformatObject(db_annotations["keyframes"], db_annotations["type"])
      annot.append(a)
      current_kf.append(ck)

  return annot, current_kf

def drawRectangle(frame, x, y, w, h, color=(255,255,255)):
  p1 = (int(x), int(y))
  p2 = (int(x+w), int(y+h))

  cv2.rectangle(frame, p1, p2, color) 

def drawText(img, text, x, y, color=(255,255,255)):
  offset = -5
  cv2.putText(img, text, (int(x), int(y+offset)), cv2.FONT_HERSHEY_PLAIN, 1.0, color)

def finishedAnnotating(annotations):
  finished = True

  for a in annotations:
    if a != None:
      finished = False
      break

  return finished
