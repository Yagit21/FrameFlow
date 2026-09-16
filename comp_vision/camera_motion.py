import cv2
import numpy as np

#Lucas-Kanade optical flow parameters
lk_params = dict( winSize=(7, 7), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

#Previous frame information
prev_gray = None #Gray-scaled version of frame
prev_pts = None #Stores the previous frame's point coordinates


def track_camera(gray):
    global prev_gray, prev_pts
    #Extracting the height and width of the image in pixels
    height, width = gray.shape[:2]

    #Checking the very first frame (since previous is None and there is fewer than 4 points in the previous frame )
    if prev_gray is None or prev_pts is None or len(prev_pts) < 4:

        #Creating a ORB detector that looks for 200 distinct features
        orb = cv2.ORB_create(nfeatures=200)

        #Detect ORB keypoints on the current frame (first)
        keypoints = orb.detect(gray, None)

        #Intialising a list that will store points close to the border of the frame
        edge_points = []

        #Defining a boundary size which is 15% of the frame's height and width
        margin_x = int(width * 0.15)
        margin_y = int(height * 0.15)
        #Looping through each keypoint
        for kp in keypoints:
            #Extracting the coordinates of the current point
            x, y = kp.pt
            #Checking if the point falls inside the margin at either left, right, top, or bottom
            is_near_left = x < margin_x
            is_near_right = x > (width - margin_x)
            is_near_top = y < margin_y
            is_near_bottom = y > (height - margin_y)
            #If the point does fall inside the margin then it it saved as an edge point
            if (is_near_left or is_near_right or is_near_top or is_near_bottom):
                edge_points.append([x, y])

        #Making sure there is enough points (so that later camera translation can be calculated)
        if len(edge_points) >= 4:
            #Converting the list of coordinates into a NumPy array since OpenCV's optical flow functions expect it in that form
            prev_pts = np.array(edge_points, dtype=np.float32).reshape(-1, 1, 2)
            #Storing the current frame to compare to the next frame
            prev_gray = gray.copy()
            #Printing how many points were found (if it works)
            print("ORB points found:", len(prev_pts))

        return None

    #This is where I compare the previous frame to the current frame 
    #next_pts is the new position of the points in the new frame, status is an indication of if tracking succeeded (1) or failed for each point, error measuring the uncertainity of tracking for each point
    next_pts, status, error = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_pts, None, **lk_params)

    #Make sure Lucas-Kanade returned points
    if next_pts is None:
        prev_gray = gray.copy()
        prev_pts = None #If tracking failed the tracker resets so the frame reruns the function
        return None

    #Filtering with NumPy to find coordinates from the prev frame that successfully were tracked
    good_old = prev_pts[status == 1]
    good_new = next_pts[status == 1] #Keeping the corresponding new coordinates that are a success

    print("Tracked points:", len(good_new))

    #Debugging Testing
    #Looping through each successful point pair
    for old, new in zip(good_old, good_new):
        #Getting the coordinates of the prev point's position and now new position
        old_x, old_y = old
        new_x, new_y = new
        #Subtracting the new position from the old position to find how many pixels it shifted (both Y and X)
        movement_x = new_x - old_x
        movement_y = new_y - old_y
        #Printing the direction it shifted to see if it is tracking the camera
        print("Movement:", round(movement_x, 2), round(movement_y, 2))

    #Overwriting the old frame with the current frame to redo the process
    prev_gray = gray.copy()
    #If there is atleast 4 points that have been successfully tracked 
    if len(good_new) >= 4:
        prev_pts = good_new.reshape(-1, 1, 2) #Shape those points back into OpenCV format and store them in prev_pts
    else:
        prev_pts = None #Starts the process again with no prev_pts

    #Return the old and new tracked points
    return good_old, good_new