#!/usr/bin/env bash
# Martin Kersner, m.kersner@gmail.com
# 2017/05/17

# ./add_image_list.sh /path/to/directory/with/images/

# Images have to located withing subdirectory of BeaverDam annotator/static/images/NAME_OF_DIRECTORY/
# You have to specify absolute path e.g. /home/ubuntu/BeaverDam/annotator/static/images/NAME_OF_DIRECTORY/
# Currently, only PNG files are utilized.

IMAGE_LIST_PATH=$1
IMAGE_LIST_NAME=`basename "$IMAGE_LIST_PATH"`

## image list
FIRST_IMAGE=true
IMAGE_LIST="["
for IMAGE_NAME in `ls $IMAGE_LIST_PATH | grep -E "*.png"`;
do
  if [ "$FIRST_IMAGE" = true ]; then
    IMAGE_LIST=$IMAGE_LIST\"$IMAGE_NAME\"
    FIRST_IMAGE=false
  else
    IMAGE_LIST=$IMAGE_LIST","\"$IMAGE_NAME\"
  fi
done
IMAGE_LIST=$IMAGE_LIST"]"

## host
function host_check {
  if [ -z "$1" ]; then
    >&2 echo "Images have to located withing subdirectory of BeaverDam annotator/static/images/NAME_OF_DIRECTORY/"
    >&2 echo "You have to specify absolute path e.g. /home/ubuntu/BeaverDam/annotator/static/images/NAME_OF_DIRECTORY/"
    echo "-1" # image list wasn't inserted to database
  fi
}

HOST="../../"`echo "$IMAGE_LIST_PATH" | grep -o "static.*"`
host_check "$HOST"

## insert image list to database
COMMAND_FILE=commands.txt

rm -f $COMMAND_FILE
touch $COMMAND_FILE

echo "INSERT INTO annotator_video " \
		 "(annotation, source, host, filename, image_list, rejected, verified) " \
		 "VALUES('', '', '$HOST', '$IMAGE_LIST_NAME', '$IMAGE_LIST', 0, 0);" >> $COMMAND_FILE

echo ".q" >> $COMMAND_FILE

sqlite3 db.sqlite3 < $COMMAND_FILE

rm -f $COMMAND_FILE

# get ID of inserted image list
MAX_ID=`sqlite3 db.sqlite3 "SELECT MAX(id) FROM annotator_video;"`
echo "$MAX_ID"
