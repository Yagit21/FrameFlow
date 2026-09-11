console.log("webcam.js has loaded!"); //Testing if webcam has loaded

document.addEventListener("DOMContentLoaded", () => { 
    //Getting the variables needed 
    const video = document.getElementById("webcam");
    const startButton = document.getElementById("startButton");
    const recordButton = document.getElementById("recordButton");
    const stopButton = document.getElementById("stopButton");
    const statusText = document.getElementById("status");

    //Webcam recording variables
    let stream;
    let recorder;
    let recordedChunks = [];
    
    //Live Pose Tracking variables
    let tracking = false;
    let lastFrameTime = 0;

    //Canvas used to capture indiviual webcam frames
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");

    

    //When the user clicks the start button
    startButton.addEventListener("click", async () => {

        try {
            //Requesting to access the user's webcam without access to audio (requesting a nice resolution and framerate)
            stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        width: { ideal: 1280 },
                        height: { ideal: 720 },
                        frameRate: { ideal: 30, max: 30 }
                    },
                    audio: false
                });
            //Getting the live webcam into a into a video HTML element 
            video.srcObject = stream;
            //Enabling the record button only after the user's camera is connected
            recordButton.disabled = false;
            statusText.textContent = "Camera connected."; 

            //Start live pose tracking
            tracking = true;
            statusText.textContent = "Starting pose tracking";
    
        //Checking actucal camera resolution
        console.log("Camera resolution:", video.videoWidth, "x", video.videoHeight);

        //Ensure the video is playing
        video.onloadeddata = function(){
            //Setting a smaller resolution for frames
            canvas.width = 640;
            canvas.height = 480;

            //Start capturing frames
            requestAnimationFrame(processVideo);
        };

        } catch (error) {
            //If user's camera does not connect successfully 
            console.error(error);
            statusText.textContent =
                "Unable to access camera.";
        }

    });

    async function processVideo(timestamp){
        //Stop tracking if it is disabled
        if (!tracking){
            return;
        }

        //Only sending a frame every 100ms (around 10 frames per second)
        if (timestamp - lastFrameTime >= 100){
            lastFrameTime = timestamp;

            //Draw the current webcam frame onto the canvas
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            //Convert the canvas image into a JPEG file
            canvas.toBlob(async (blob) => {
                if (!blob){
                    console.error("Could not create image blob.");
                    return;
                }
                //Create a form containing the frame
                const formData = new FormData();
                formData.append("frame", blob, "frame.jpg");
                
                try{
                    //Send the frame to Flask
                    const response = await fetch(
                        "/process-frame",
                        {
                            method: "POST",
                            body: formData
                        }
                    );
                    //Check whether Flask returned an error
                    if (!response.ok){
                        console.error("Frame processing failed:", response.status);
                        return;
                    }
                    //Converting Flask's response into a JSON
                    const result = await response.json();

                    //Check how many landmarks MediaPipe found
                    console.log("Landmarks detected:", result.landmarks.length);
                } catch (error){
                    console.error(error);
                }

            }, "image/jpeg", 0.8);
        }

        requestAnimationFrame(processVideo);
    }

    //If user clicks the record button
    recordButton.addEventListener("click", () => {
        //Reseting the data entry so that old recordings are not influencing new ones
        recordedChunks = [];
        //Standard web video formats
        const mimeTypes = [
            "video/webm;codecs=vp9",
            "video/webm;codecs=vp8",
            "video/webm"
        ];

        let mimeType = "";
        //Loop through and stop at the firt one the user's computer supports
        for (const type of mimeTypes) {
            if (MediaRecorder.isTypeSupported(type)) {
                mimeType = type;
                break;
            }
        }
        //Setting the recording bitrate to 2.5 Megabites per second
        const recorderOptions = {
            videoBitsPerSecond: 2_500_000
        };

        if (mimeType) {
            recorderOptions.mimeType = mimeType;
        }

        //Creating a MediaRecorder instance of the stream
        recorder = new MediaRecorder(stream, recorderOptions);
        //The event listener to record new data
        recorder.ondataavailable = (event) => {
            //Checking if the data is not empty
            if (event.data.size > 0) {
                recordedChunks.push(event.data); //Saving the data into the recordChuncks array
            }
        };
    //Showing error messages
    recorder.onerror = (event) => {

        console.error("Recording error:", event.error);

        statusText.textContent =
            "Recording error.";

    };

    //Running this event once the recording stops
    recorder.onstop = () => {
        //Checking the format of the data if it doesn't have a format it defaults to video/webm
        const actualMimeType =
            recorder.mimeType || "video/webm";
        //Combining all the small data pieces into one unified object
        const blob = new Blob(
            recordedChunks,
            {
                type: actualMimeType
            }
        );
        //Total size of final recording in bytes
        console.log("Recording size:", blob.size, "bytes");
            //Sending the file into the uploadRecording function
            uploadRecording(blob);

        };

        //Starting the recording
        recorder.start(1000);
        //Disabling the record button and enabling the stop button so the user does not click the wrong button
        recordButton.disabled = true;
        stopButton.disabled = false;
        statusText.textContent = "Recording..."; //An indication that the user is recording

    });

    //Event for when the stop button is clicked
    stopButton.addEventListener("click", () => {
        //Stoping the recording 
        recorder.stop();
        //Disabling the stop button and enabling the record button
        recordButton.disabled = false;
        stopButton.disabled = true;

        statusText.textContent = "Processing recording..."; //Changing the text status

    });

    //Upload recording function
    async function uploadRecording(blob) {

        const formData = new FormData(); //Creating a form data object that can send binary files over requests

        formData.append("video", blob, "recording.webm"); //Assigning the binary video data (blob) to the form with the key name 'video' and the name of the file 'recording.webm'

        //Sending a POST request to the endpoint /upload-recording and awaiting a response
        const response = await fetch(
            "/upload-recording",
            {
                method: "POST",
                body: formData
            }
        );
        //Parse the server as an await JSON response
        const result = await response.json();

        statusText.textContent = result.message;

    }
});