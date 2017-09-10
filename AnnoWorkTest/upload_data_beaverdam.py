#!/usr/bin/env python
# Dae-Yong, romanity@naver.com
# 2017/09/10

import os
import sys
import shutil
import cv2
import argparse
import sqlite3
import random
import math
import re

################# UTIL PART ###############

SAVE_TEXT_PREFIX="/SetSize%s_Part%02d.txt"

def getImageFileListInDir(file_root_path):
    file_list = os.listdir(file_root_path)

    img_list = []
    numImages = 0
    for file_name in file_list:
        if file_name.endswith(".png"):
            img_list.append(file_name)
            numImages += 1

    return img_list, numImages

def partitioningSet(file_list, size_of_partition):
    output = []
    for n in range(0, len(file_list), size_of_partition):
        output.append(list(file_list[n:n+size_of_partition]))
    return output

def setPrefixForBeaverDam(file_list):

    numList = len(file_list)

    output = []
    for n in range(0, int(numList)):
        lineCount = 0
        img_file_name_list = ""
        for file_name in file_list[n]:
            lineCount += 1

            if lineCount == 1:
                temp_file_name = '[\"' + file_name + '\",'
            elif lineCount == len(file_list[n]):
                temp_file_name = '\"' + file_name + '\"]'
            else:
                temp_file_name = '\"' + file_name + '\",'
            
            img_file_name_list += temp_file_name
        
        output.append(img_file_name_list)

    return output

def saveListInTextFiles(file_root_path, file_list, size_of_partition):

    # Count Image Files in Directory
    for n in range(0, len(file_list)):
        temp = file_root_path + SAVE_TEXT_PREFIX%(size_of_partition,n)

        f = open(temp, "w")
        f.write(file_list[n])
        f.close()
        print("Image File List File is Saved: %s"%temp) 

def checkListInTextFiles(file_root_path, size_of_partition):
    
    # Count Image Files in Directory
    _, numImageFiles = getImageFileListInDir(file_root_path)

    # Compute Number of Text Files Should be
    validCount = (numImageFiles / size_of_partition) + 1
  
    for n in range(0, validCount):
        fileName = file_root_path + SAVE_TEXT_PREFIX%(size_of_partition, n)
        if not os.path.isfile(fileName):
            return False

    return True

def readListInTextFiles(file_root_path, size_of_partition):

    # Count Image Files in Directory
    _, numImageFiles = getImageFileListInDir(file_root_path)

    # Count Text Files Regarded to the size of Partition
    validCount = int(math.ceil(float(numImageFiles) / float(size_of_partition)))

    output = []
    for n in range(0, validCount):
        file_name = file_root_path + SAVE_TEXT_PREFIX%(size_of_partition, n)

        with open(file_name, "r") as f:
            data = f.read()
            output.append(data)

    return output

def prepareImageListTextFiles(img_list_full_path, size_of_partition):

    # Get File List
    file_name_list, numImageFiles = getImageFileListInDir(img_list_full_path)

    # Shuffling
    file_name_list_shuffle = random.sample(file_name_list, numImageFiles)

    # Set Division
    file_name_list_division = partitioningSet(file_name_list_shuffle, size_of_partition)

    # Set Prefix for BeaverDam
    file_name_list_with_prefix = setPrefixForBeaverDam(file_name_list_division)    

    # Save List File in Text
    saveListInTextFiles(img_list_full_path, file_name_list_with_prefix, size_of_partition) 

# It does not work in BeaverDam - just let it be to let you know about it
def setSymbolicLinkToBeaverDamDataPath(img_root_path):

    image_list, _ = getImageFileListInDir(img_root_path)

    dst_path = os.path.join("./annotator/static/images", img_root_path.split('/')[-1])

    if not os.path.isdir(dst_path):
        os.makedirs(dst_path)

    for file_name in image_list:
        src_file_path = os.path.join(img_root_path, file_name)
        dst_file_path = os.path.join(dst_path, file_name)

        if not os.path.islink(dst_file_path):
            print("Symlink Src: %s"%src_file_path)
            print("Symlink Dst: %s"%dst_file_path)
            os.symlink(src_file_path, dst_file_path)

def copyImageFilesToBeaverDamDataPath(img_root_path, img_file_name_list, 
                                      min_index_of_list, num_upload_data):

    dst_path = os.path.join('./annotator/static/images', img_root_path.split('/')[-1])

    if not os.path.isdir(dst_path):
        os.makedirs(dst_path)

    numFiles = len(img_file_name_list)
    start_idx = min_index_of_list
    end_idx = num_upload_data
    if min_index_of_list + num_upload_data - 1 >= numFiles:
        end_idx = numFiles

    for n in range(start_idx, end_idx):
        temp = re.findall('"(.+?)"', img_file_name_list[n])

        for file_name in temp:

            src_file_path = os.path.join(img_root_path, file_name)
            dst_file_path = os.path.join(dst_path, file_name)

            if not os.path.isfile(dst_file_path):
                print('Copy to BeaverDam Data Path')
                print("Src File Path: %s"%src_file_path)
                print("Dst File Path: %s"%dst_file_path)

                shutil.copyfile(src_file_path, dst_file_path)


def addImageListOntoDB(db_path, name_of_sequence, name_of_seq_beaverdam, file_name_list, min_index, num_upload_data):

    start_idx = min_index
    end_idx = num_upload_data

    if min_index >= len(file_name_list):
        print("Number of index is larger than the number of image list")
        return False
    
    if min_index + num_upload_data - 1 >= len(file_name_list):
        end_idx = len(file_name_list)

    for n in range(start_idx, end_idx):
        file_name_list_ = file_name_list[n]

        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT MAX(id) FROM annotator_video")

            # val = (118, )
            val = c.fetchall()
            val = re.findall('\((.+?),', str(val))[0]

            if val == 'None':
                maxId = 1
            else:
                maxId = int(val) + 1

            # annotator_video = {id, annotation/source/host/filename/image_list/rejected/verified)}
            input_id = maxId
            input_annotation = ''
            input_source = ''
            input_host = "../../static/images" + "/%s"%name_of_sequence
            input_filename = name_of_seq_beaverdam
            input_img_list = file_name_list_
            input_rejected = 0
            input_verified = 0

            input_statement = "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'"%(
                                input_id,
                                input_annotation,
                                input_source,
                                input_host,
                                input_filename,
                                input_img_list,
                                input_rejected,
                                input_verified)

            c.execute("INSERT INTO annotator_video VALUES(%s)"%input_statement)        

######################################################

################ INPUT PARAMETERS  ###################
def getParameters(argv):
    parser = argparse.ArgumentParser(description='Upload Image Lists onto BeaverDam')
    parser.add_argument('--db_path', dest='db_path', required=True)
    parser.add_argument('--img_root_path', dest='img_root_path', required=True)
    parser.add_argument('--size_of_partition', dest='size_of_partition', required=True)
    parser.add_argument('--name_of_seq_beaverdam', dest='name_of_seq_beaverdam', required=True)
    parser.add_argument('--min_index_of_list', dest='min_index', required=True)
    parser.add_argument('--num_upload_data', dest='num_upload_data', required=True)

    return parser.parse_args()

################ MAIN #################
def main():

    args = getParameters(sys.argv)
    db_path = args.db_path
    img_root_path = args.img_root_path
    name_of_sequence = str(img_root_path).split('/')[-1]
    name_of_seq_beaverdam = args.name_of_seq_beaverdam
    size_of_partition = int(args.size_of_partition)
    
    min_index_of_list = int(args.min_index)
    num_upload_data = int(args.num_upload_data)

    if num_upload_data <= 0:
        print("num_upload_data can not be less than 1")
        return False

    print("-------------------- INPUT INFO --------------------")
    print("DB Path: %s"%db_path)
    print("Image Root Path: %s"%img_root_path)
    print("Size of Partition: %s"%size_of_partition)
    print("Name of Seq. BeaverDam: %s"%name_of_seq_beaverdam)
    print("Upload Index: %s-%s"%(min_index_of_list, min_index_of_list + num_upload_data -1))
    print("--------------------------------------------------")
    
    if not checkListInTextFiles(img_root_path, size_of_partition):
        prepareImageListTextFiles(img_root_path, size_of_partition)

    img_file_name_list = readListInTextFiles(img_root_path, size_of_partition)

    print("------Image File List Partition------")
    for file_list in img_file_name_list:
        print(file_list)
    print("-------------------------------------")

    copyImageFilesToBeaverDamDataPath(img_root_path, img_file_name_list, 
            min_index_of_list, num_upload_data)

    addImageListOntoDB(db_path, name_of_sequence, name_of_seq_beaverdam, img_file_name_list,
            min_index_of_list, num_upload_data)

if __name__ == "__main__":
    main()

