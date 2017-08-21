Welcome to our annotation tool!

Your task is to accurately draw annotation boxes around predefined objects in each image.
We need this so that we can train a computer to detect objects in image.

## Quick Instructions
1. Select correct class for object you want to annotate.
2. Draw a box accurately around an object (covering every part you can see).
3. Adjust the box to keep it accurate.
4. After all objects are annotated in image, press 's' key to go to next image.

### Examples of correct and wrong annotations

![](http://i.imgur.com/eH7447y.png)
![](http://i.imgur.com/OJFawLh.png)

### Occluded objects I

![](http://i.imgur.com/konMqlX.png)
![](http://i.imgur.com/K4nrQ2G.png)

### Occluded objects II

![](http://i.imgur.com/Hw7mXi9.png)
![](http://i.imgur.com/WduYbXi.png)

### Not fully visible objects

![](http://i.imgur.com/gINgF8e.png)
![](http://i.imgur.com/8vrWefC.png)

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
- Traffic Lights

### Traffic Lights
- RedLight
- GreenLight
- RedLight+GreenArrow
- OrangeLight
- RedLight+OrangeLight
- GreenLight+GreenArrow
- GreenLight+OrangeLight

<center>
  <img src="http://i.imgur.com/tMdlITv.jpg"/><br/ >
  Example of traffic light rule in the dataset.
</center>

Even though colors of traffic light are not good to recognize, you need to label the traffic light following above bulbs.

In case of traffic lights you **shouldn't** annotate only bulbs but whole traffic light without pole.

### Traffic Light Annotation Examples
<center>
  <img src="http://i.imgur.com/hfPBBIW.png" /><br/ >
  <img src="http://i.imgur.com/gjRLznZ.png" /><br/ >
  <img src="http://i.imgur.com/YrsyYeI.png" />
</center>

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
