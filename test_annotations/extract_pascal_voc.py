#!/usr/bin/env python
# Martin Kersner, m.kersner@gmail.com
# 2016/12/23

from pascal_voc_writer import PascalVocWriter 

def main():
  width  = 100
  height = 100
  depth  = 3
  dims = (width, height, depth)

  db_name       = "HY"
  img_dir_name  = "foldername"
  file_name     = "0"
  out_dir_name  = "here"

  # TODO truncated, difficult

  # for 
  tmp = PascalVocWriter(img_dir_name, file_name, dims, databaseSrc=db_name)

  # xmin, ymin, xmax, ymax, label
  tmp.addBndBox(10,10,20,30,'chair')
  tmp.addBndBox(1,1,600,600,'car')
  tmp.save(out_dir_name)

if __name__ == "__main__":
  main()
