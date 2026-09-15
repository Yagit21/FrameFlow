import cv2
import numpy as np

#Defining parameters for lucas-kanade optical flow method
lk_params = dict(winSize=(7,7), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

#Global Variables
prev_gray = None
prev_pts = None


#Where I will store camera movement details
camera_movement = []

def getting_keyframes(file, np_image, frame, gray):
    global prev_gray, prev_pts, orb, camera_movement
    
    height, width = gray.shape[:2]
    #Detect ORB points and filter for frame edges
    if prev_gray is None or prev_pts is None or len(prev_pts) < 4:
        #Defining ORB 
        orb = cv2.ORB_create(nfeatures=200)
        keypoints = orb.detect(gray, None)
        
        #Each keypoint from the edge of the camera
        edge_points = []
        
        #Define an outer boundary margin (e.g., within 15% of any frame edge)
        margin_x = int(width * 0.15)
        margin_y = int(height * 0.15)

        for kp in keypoints:
            x, y = kp.pt
            #Check if the keypoint resides near any of the 4 borders
            is_near_left = x < margin_x
            is_near_right = x > (width - margin_x)
            is_near_top = y < margin_y
            is_near_bottom = y > (height - margin_y)

            if is_near_left or is_near_right or is_near_top or is_near_bottom:
                edge_points.append([x, y])
            
        if edge_points:
            #Convert to float32 numpy format which is needed for Lucas-Kanade
            prev_pts = np.array(edge_points, dtype=np.float32).reshape(-1, 1, 2)
            prev_gray = gray.copy()
        
 

    