#!/usr/bin/env python
# Martin Kersner, m.kersner@gmail.com
# 2017/05/26

import argparse
import string
import json

def get_parameters():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input', dest='input', required=True)

  return parser.parse_args()

def json_dump(json_annotation):
  return string.replace(string.replace(json.dumps(json_annotation), "\"false\"", "false"), "\"true\"", "true")

def main():
  param = get_parameters()
  ann_all = []

  with open(param.input, "r") as input_list:
    for idx, filename in enumerate(input_list):
      filename = filename.strip()

      with open(filename, "r") as f:
        for line in f:
          ann = {}
          annotation = line.strip()
          ann_str = annotation.split(" ")

          score = float(ann_str[15])
          if score < 0.02:
            continue

          object_type = ann_str[0]
          x = int(float(ann_str[4]))
          y = int(float(ann_str[5]))
          w = int(float(ann_str[6])) - int(float(ann_str[4]))
          h = int(float(ann_str[7])) - int(float(ann_str[5]))

          keyframes = {}
          keyframes["x"] = x
          keyframes["y"] = y
          keyframes["w"] = w
          keyframes["h"] = h
          keyframes["continueInterpolation"] = "false"
          keyframes["frame"] = idx 

          ann["color"] = "#3315a8"
          ann["wrong"] = "false"
          ann["type"]  = object_type 
          ann["keyframes"] = [keyframes]

          ann_all.append(ann)

  print(json_dump(ann_all))

if __name__ == "__main__":
  main()
