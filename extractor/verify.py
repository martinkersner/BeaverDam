#!/usr/bin/env python
# Martin Kersner, m.kersner@gmail.com
# 2016/12/23

import os
import sys
import shutil
import cv2
import argparse
import json
import string
from pascal_voc_writer import PascalVocWriter 
from utils import *
from colors import *
import numpy as np

class MissingAnnotationKeyframe(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

def get_parameters(argv):
  parser = argparse.ArgumentParser(description='Extract annotations from BeaverDam')
  parser.add_argument('--db_path', dest='db_path', required=True)
  parser.add_argument('--id1', dest='id_one', required=True)
  parser.add_argument('--id2', dest='id_two', required=True)
  parser.add_argument('--ann1', dest='ann_one', required=True)
  parser.add_argument('--ann2', dest='ann_two', required=True)

  return parser.parse_args()

def convert_annotations(db_annotations):
  annotation_converted = {}
  for ann in db_annotations:
    keyframe = ann["keyframes"][0]["frame"]
    if keyframe in annotation_converted:
      annotation_converted[keyframe].append(ann)
    else:
      annotation_converted[keyframe] = [(ann)]

  return annotation_converted

def IOU(a, b, w=1280, h=720):
  za = np.zeros((h, w))
  zb = np.zeros((h, w))

  oa = np.ones((a[3], a[2]))
  ob = np.ones((b[3], b[2]))

  za[a[1]:a[1]+a[3], a[0]:a[0]+a[2]] = oa
  zb[b[1]:b[1]+b[3], b[0]:b[0]+b[2]] = ob

  inter = (za*zb)>0
  union = (za+zb)>0

  sum_inter = sum(sum(inter))*1.0
  sum_union = sum(sum(union))

  if sum_inter <= 0:
    return 0
  else:
    return sum_inter/sum_union

def make_box_from_annotation(a_full):
  a = a_full["keyframes"][0]
  return [float(a["x"]), float(a["y"]), float(a["w"]), float(a["h"])]

def preprocess_list(lst):
  return [ int(i) if i > 0 else 0 for i in lst]

def list_wrong_annotations(a1_dict, a2_len):
  w1 = []
  w2_all = range(a2_len)
  c2 = []

  for i in a1_dict:
    if a1_dict[i]["idx"] < 0:
      w1.append(i)
    else:
      c2.append(a1_dict[i]["idx"])

  w2 = filter(lambda x: x not in c2, w2_all)  
  return w1, w2

def verify_image_annotation(a1_full, a2_full, threshold=0.7):
  ## Types of errors
  # 1) Does not find correspnding annotation (all other annotations have lower IOU then given threshold).
  # 2) Different number of annotation boxes.
  # 3) Different class for the highest (over threshold) IOU.
  a1_dict = {}

  for idx1, a1 in enumerate(a1_full):
    b1 = make_box_from_annotation(a1)    
    b1 = preprocess_list(b1)
    t1 = a1["type"]

    a1_dict[idx1] = {}
    a1_dict[idx1]["iou"] = 0.0
    a1_dict[idx1]["idx"] = -1 

    for idx2, a2 in enumerate(a2_full):
      b2 = make_box_from_annotation(a2)    
      b2 = preprocess_list(b2)
      t2 = a2["type"]

      iou = IOU(b1, b2)

      if t1 == t2 and iou > threshold and iou > a1_dict[idx1]["iou"]:
        a1_dict[idx1]["iou"] = iou
        a1_dict[idx1]["idx"] = idx2

  w1, w2 = list_wrong_annotations(a1_dict, len(a2_full))

  return w1, w2

def highlight_wrong_annotation(ann_dict, wrong_idx_list): 
  for idx, ann in enumerate(ann_dict):
    if idx in wrong_idx_list:
      ann["wrong"] = "true"

  return ann_dict

def json_dump(json_annotation):
  return string.replace(string.replace(json.dumps(json_annotation), "\"false\"", "false"), "\"true\"", "true")

def dump2file(filename, text):
  with open(filename, 'w') as f:
    for line in text:
      f.write(line)

def main():
  args = get_parameters(sys.argv)
  db_annotations_one, _, _, _ = getImageListInformation(args.db_path, args.id_one)
  db_annotations_two, _, _, _ = getImageListInformation(args.db_path, args.id_two)

  converted1 = convert_annotations(db_annotations_one)
  converted2 = convert_annotations(db_annotations_two)

  annotation1 = []
  annotation2 = []

  sorted1 = sorted(converted1.keys())
  sorted2 = sorted(converted2.keys())

  if len(sorted1) != len(sorted2):
    image_list_id = args.id_one if len(sorted1) < len(sorted2) else args.id_two
    print("Image subset with id " + image_list_id + " is missing annotations on some images.")
    exit()

  for k1, k2 in zip(sorted1, sorted2):
    print(k1, k2)
    if k1 != k2:
      raise MissingAnnotationKeyframe()

    print("ID ", k1)

    if len(converted1[k1]) > len(converted2[k2]):
      w1, w2 = verify_image_annotation(converted1[k1], converted2[k2])
    else:
      w2, w1 = verify_image_annotation(converted2[k2], converted1[k1])

    if len(w1) > 0:
      c1 = highlight_wrong_annotation(converted1[k1], w1)
    else:
      c1 = converted1[k1]

    if len(w2) > 0:
      c2 = highlight_wrong_annotation(converted2[k2], w2)
    else:
      c2 = converted2[k2]

    for c in c1:
      annotation1.append(c)

    for c in c2:
      annotation2.append(c)

  # print(json_dump(annotation1))
  # print(json_dump(annotation2))

  dump2file(args.ann_one, json_dump(annotation1))
  dump2file(args.ann_two, json_dump(annotation2))
  
if __name__ == "__main__":
  main()
