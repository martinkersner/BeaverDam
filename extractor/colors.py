# Martin Kersner, m.kersner@gmail.com
# 2016/12/26 

BLUE_COLOR_   = (255,0,0)
GREEN_COLOR_  = (0,255,0)
RED_COLOR_    = (0,0,255)
WHITE_COLOR_  = (255,255,255)
BLACK_COLOR_  = (0,0,0)
YELLOW_COLOR_ = (0,255,255)

def getColor(obj_type):
  if obj_type == "Car":
    return RED_COLOR_
  elif obj_type == "Pedestrian":
    return GREEN_COLOR_
  elif obj_type == "Cyclist":
    return BLUE_COLOR_
  elif obj_type == "Bus":
    return WHITE_COLOR_
  elif obj_type == "Truck":
    return BLACK_COLOR_
