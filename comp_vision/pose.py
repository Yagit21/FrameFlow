import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
import cv2


#MediaPipe pose landmark connections
POSE_CONNECTIONS = [
    (11, 13), (13, 15),
    (12, 14), (14, 16),
    (11, 12),
    (11, 23), (12, 24),
    (23, 24),
    (23, 25), (25, 27),
    (24, 26), (26, 28),
    (27, 29), (29, 31),
    (28, 30), (30, 32)
]


class PoseDetection:

    def __init__(self):

        #Set up the MediaPipe Pose Landmarker model
        base_options = BaseOptions(
            model_asset_path="comp_vision/pose_landmarker_full.task"
        )

        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.7
        )

        #Create the MediaPipe detector once
        self.detector = vision.PoseLandmarker.create_from_options(options)


    def process_frame(self, frame):

        #Changing BGR to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #Convert the OpenCV image into a MediaPipe Image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        #Run MediaPipe pose detection
        result = self.detector.detect(mp_image)

        #Create a list to store the landmarks
        landmarks = []

        #Check whether MediaPipe detected a person
        if result.pose_landmarks:

            #Get the first detected person's landmarks
            pose = result.pose_landmarks[0]

            #Store all 33 landmarks
            for index, lm in enumerate(pose):

                landmarks.append({
                    "index": index,
                    "x": lm.x,
                    "y": lm.y,
                    "z": lm.z,
                    "visibility": lm.visibility
                })

        return landmarks