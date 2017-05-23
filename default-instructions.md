Welcome to our annotation tool!

Your task is to accurately draw annotation boxes around predefined objects in each image.
We need this so that we can train a computer to detect objects in image.

## Quick Instructions
1. Select correct class for object you want to annotate.
2. Draw a box accurately around an object (covering every part you can see).
3. Adjust the box to keep it accurate.
4. After all objects are annotated in image, press 's' key to go to next image.

For example:
### Good:
![](https://raw.githubusercontent.com/wiki/xysense/BeaverDam/images/good_1.png)
![](https://raw.githubusercontent.com/wiki/xysense/BeaverDam/images/good_2.png)
### Bad:
![](https://raw.githubusercontent.com/wiki/xysense/BeaverDam/images/bad_1.png)
![](https://raw.githubusercontent.com/wiki/xysense/BeaverDam/images/bad_2.png)

## Keyboard shortcuts
- `s` move to the next image
- `a` move to the previous image
- `d` delete selected annotation box

## Object classes
- Van
- Bus
- Truck
- Pedestrian
- Cyclist
- Motorcyclist

## Detailed Instructions
1. We need you to draw an accurate annotation box around each object (defined above) you see in the image.
2. Before you annotate any object, make sure that you selected correct object class.
3. We recommend you to annotate all objects of the same class at first and then move on other group of objects.
4. After you finish annotating all required objects in image press `s` key to move to the next image.
5. If you want to go back to the previous image press `a` key.
6. If you didn't annotate object precisely at first attempt, annotation box can be refined. Move cursor on edge (or corner) of annotation box. Two-way arrow cursor will appear. Click and drag annotation box in direction you want to refine.
7. Save annotations regularly by clicking on Submit button. If you don’t submit, annotations will not be saved. Before closing browser or changing image sequence, don’t forget to save your annotations.
8. If you annotate object with wrong class, you have to delete annotation, select correct object class and make annotation again.

## FAQ
### How accurate do I need to be?
We require a tight rectangle covering object visible in image.

### How good object annotations looks like?
- Each annotation box should include object fully. Edges of object should be included.
- If object is occluded imagine its real size and annotate it.
- If objects are occluded, don’t annotate them as one object. Annotate them separately.
- If object is truncated, annotate object up to the end of image and imagine how annotation box would look like if object was fully visible.

### How small objects should I annotate?
Annotation tools has set minimal size of object. If you can correctly annotate object with annotation tool, then this object should be annotated.
