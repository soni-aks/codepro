

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
  help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=32,
  help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space

#green color

greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
#red color

#greenLower=np.array([30,150,50])
#greenUpper=np.array([255,255,180])

#blue color

#greenLower = np.array([110,50,50])
#greenUpper = np.array([130,255,255])

# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
pts = deque(maxlen=args["buffer"])
counter = 0
(dX, dY) = (0, 0)
direction = ""

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
  camera = cv2.VideoCapture(0)

# otherwise, grab a reference to the video file
else:
  camera = cv2.VideoCapture(args["video"])

# keep looping
while True:
  # grab the current frame
  (grabbed, frame) = camera.read()

  # if we are viewing a video and we did not grab a frame,
  # then we have reached the end of the video
  if args.get("video") and not grabbed:
    break

  # resize the frame, blur it, and convert it to the HSV
  # color space
  frame_width = 800
  frame = imutils.resize(frame, width=frame_width)

  center_x = frame.shape[1]/2
  center_y = frame.shape[1]/2
  blurred = cv2.GaussianBlur(frame, (11, 11), 0)
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

  # construct a mask for the color "green", then perform
  # a series of dilations and erosions to remove any small
  # blobs left in the mask
  mask = cv2.inRange(hsv, greenLower, greenUpper)
  mask = cv2.erode(mask, None, iterations=2)
  mask = cv2.dilate(mask, None, iterations=2)

  # find contours in the mask and initialize the current
  # (x, y) center of the ball
  cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)[-2]
  cv2.imshow("mask",mask)
  center = None
  for cnt in cnts:
                approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)    #approximating each contour #2nd arg - epsilon i.e accuracy parameter
                print(len(approx));
                if len(approx)==5:
                    print("pentagon");
                    #font = cv2.FONT_HERSHEY_SIMPLEX
                    #cv2.putText(frame,'Pentagon',(100,200), font, 2,(255,255,255),2,cv2.LINE_AA)
                    #cv2.drawContours(img,[cnt],0,255,-1)
                elif len(approx)==3:
                    print("triangle");
                    #font = cv2.FONT_HERSHEY_SIMPLEX
                    #cv2.putText(frame,'Triangle',(200,200), font, 2,(255,255,255),2,cv2.LINE_AA)
                   # cv2.drawContours(img,[cnt],0,(0,255,0),-1)
                #elif len(approx)==4:
                    #print("square");
                 #   font = cv2.FONT_HERSHEY_SIMPLEX
                  #  cv2.putText(frame,'Square',(100,300), font, 2,(255,255,255),2,cv2.LINE_AA)
                    #cv2.drawContours(img,[cnt],0,(0,0,255),-1)
                elif len(approx) == 9:
                    print("sphere");
                    #font = cv2.FONT_HERSHEY_SIMPLEX
                    #cv2.putText(frame,'Sphere',(200,300), font, 2,(255,255,255),2,cv2.LINE_AA)
                    #cv2.drawContours(img,[cnt],0,(255,255,0),-1)
                elif len(approx) > 15:
                    print("circle");
                    #font = cv2.FONT_HERSHEY_SIMPLEX
                    #cv2.putText(frame,'Circle',(400,600), font, 2,(255,255,255),2,cv2.LINE_AA)
                    break;
                    #cv2.drawContours(img,[cnt],0,(0,255,255),-1)

  # only proceed if at least one contour was found
  if len(cnts) > 0:
    # find the largest contour in the mask, then use
    # it to compute the minimum enclosing circle and
    # centroid
    c = max(cnts, key=cv2.contourArea)
    ((x, y), radius) = cv2.minEnclosingCircle(c)
    M = cv2.moments(c)  #center of the mass and area of the object
    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

    # only proceed if the radius meets a minimum size
    if radius > 10:
      # draw the circle and centroid on the frame,
      # then update the list of tracked points
      cv2.circle(frame, (int(x), int(y)), int(radius),
        (0, 255, 255), 2)
      cv2.circle(frame, center, 5, (0, 0, 255), -1)
      pts.appendleft(center)

      cv2.line(frame,(int(center_x),int(center_y)),(int(x),int(y)),(255,255,255),1,1)
      
      x_slice = (x/(frame_width/10))
      x_slice_int = int(x_slice) + 1
      print(x_slice_int, " slice quadrant")

      norm_radius = radius/frame_width

      dist = 2*(1.598/norm_radius)
      
      print(dist, "distance from center")
      cv2.putText(frame,str(int(dist))+"cm",(int(x)+8,int(y)+8),cv2.FONT_HERSHEY_DUPLEX, 2,(255,0,0),2,cv2.LINE_AA)

  # loop over the set of tracked points
  for i in np.arange(1, len(pts)):
    # if either of the tracked points are None, ignore
    # them
    if pts[i - 1] is None or pts[i] is None:
      continue

    # check to see if enough points have been accumulated in
    # the buffer
    if counter >= 10 and i == 1 and pts[-10] is not None:
      # compute the difference between the x and y
      # coordinates and re-initialize the direction
      # text variables
      dX = pts[-10][0] - pts[i][0]
      dY = pts[-10][1] - pts[i][1]
      (dirX, dirY) = ("", "")

      # ensure there is significant movement in the
      # x-direction
      if np.abs(dX) > 20:
        dirX = "East" if np.sign(dX) == 1 else "West"

      # ensure there is significant movement in the
      # y-direction
      if np.abs(dY) > 20:
        dirY = "North" if np.sign(dY) == 1 else "South"

      # handle when both directions are non-empty
      if dirX != "" and dirY != "":
        direction = "{}-{}".format(dirY, dirX)

      # otherwise, only one direction is non-empty
      else:
        direction = dirX if dirX != "" else dirY

    # otherwise, compute the thickness of the line and
    # draw the connecting lines
    thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
    cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

  # show the movement deltas and the direction of movement on
  # the frame
  cv2.putText(frame, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
    0.65, (0, 0, 255), 3)
  cv2.putText(frame, "dx: {}, dy: {}".format(dX, dY),
    (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
    0.35, (0, 0, 255), 1)

  # show the frame to our screen and increment the frame counter
  cv2.imshow("Frame", frame)
  key = cv2.waitKey(1) & 0xFF
  counter += 1

  # if the 'q' key is pressed, stop the loop
  if key == ord("q"):
    break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
