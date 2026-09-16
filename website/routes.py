from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from .models import User, Project, Character, Recording
from comp_vision.pose import PoseDetection
from comp_vision.camera_motion import track_camera
import uuid
from . import db
import os
import cv2
import numpy as np

routes = Blueprint("routes", __name__)

pose_detector = PoseDetection()

@routes.route("/")
def index():
    return render_template("index.html")


@routes.route("/webcam")
def webcam():
    
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
        
    return render_template("webcam.html")


@routes.route("/upload-recording", methods=["POST"])
def upload_recording():
    
    #Check that user is logged in
    if "user_id" not in session:
        return jsonify({"message": "You must be logged in."}), 401
    
    #Looking for a file named video is not returning an error message
    if "video" not in request.files:
        return jsonify({"message": "No video uploaded."}), 400
    
    #Getting the video file 
    video = request.files["video"]

    #Geting the logged-in user
    user_id = session["user_id"]


    #Getting the active project
    # project_id = session.get("project_id")


    # if not project_id:
    #     return jsonify({"message": "No active project."}), 400

    #Create unique ID for filename
    unique_id = str(uuid.uuid4())
    #Naming the path with the unique ID
    filename = "recording_%s.webm" % (unique_id)
    
    #Get the Flask application's root directory
    project_root = routes.root_path
    
    #Go up from the website folder to FreeFlow
    project_root = os.path.dirname(project_root)

    #Creating a folder path for the user
    folder_path = os.path.join(project_root, "data", "videos", "user_%s" % (user_id))
    os.makedirs(folder_path, exist_ok=True)
    #Complete the video file path
    absolute_video_path = os.path.join(folder_path, filename)

    #Save actual video
    video.save(absolute_video_path)


    #Creating the db record
    recording = Recording(project_id=1,user_id=user_id, recording_uuid=unique_id, video_path=absolute_video_path) #Have to add project details later (currently just testing)

    #Saving the video file to the db
    db.session.add(recording)
    db.session.commit()

    #Returning a success message
    return jsonify({"message": "Recording successfully uploaded.", "recording_id": recording.id, "recording_uuid": recording.recording_uuid, "video_path": absolute_video_path})

@routes.route("/create-project", methods=["POST"])
def create_project():

    #Check that user is logged in
    if "user_id" not in session:
        return jsonify({"message": "Please log in first."}), 401
    
    data = request.get_json()
    
    
    #Getting user's info
    user_id = session["user_id"]
    data = request.get_json()
    project_name = data.get("project_name")
    character_id = data.get("character_id")


    #Create project
    project = Project(user_id=user_id, character_id=character_id, project_name=project_name, status="Recording")

    db.session.add(project)
    db.session.commit()

    #Store currently active project
    session["project_id"] = project.id


    return jsonify({
        "message": "Project created successfully.",
        "project_id": project.id
    })

@routes.route("/process-frame", methods=["POST"])
def process_frame():

    #Check that the user is logged in
    if "user_id" not in session:
        return jsonify({"message": "You must be logged in."}), 401

    #Check that a frame was included in the request
    if "frame" not in request.files:
        return jsonify({"message": "No frame received."}), 400

    #Get the uploaded frame
    frame_file = request.files["frame"]

    #Read the uploaded file into memory
    file_bytes = np.frombuffer(frame_file.read(), np.uint8)

    #Decode the JPEG into an OpenCV image
    frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    #Make sure OpenCV successfully decoded the frame
    if frame is None:
        return jsonify({"message": "Could not decode frame."}), 400

    #Run MediaPipe pose detection
    landmarks = pose_detector.process_frame(frame)
    #Converting the frame to a gray image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #Finding the movement of the camera throughout frames
    camera_points = track_camera(gray)

    #Return the landmarks to the browser
    return jsonify({"landmarks": landmarks}) 
