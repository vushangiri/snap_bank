import base64
import os
import cv2
import numpy as np
from flask import Flask, render_template, send_from_directory, request, redirect, flash
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit
import face_recognition
import numpy as np

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
app.config["SECRET_KEY"] = "secret!"

# configure upload folder
UPLOAD_FOLDER = '../frontend/static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# check if file type is in allowed list
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# app.add_url_rule('/frontend/static/<path:filename>', endpoint='fstatic',
#                  view_func=app.send_static_file)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")


# Load a sample picture and learn how to recognize it.
jungey_image = face_recognition.load_image_file("../frontend/static/images/jungey.jpg")
jungey_face_encoding = face_recognition.face_encodings(jungey_image)[0]

# Load a second sample picture and learn how to recognize it.
haku_image = face_recognition.load_image_file("../frontend/static/images/haku.jpg")
haku_face_encoding = face_recognition.face_encodings(haku_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    jungey_face_encoding,
    haku_face_encoding
]
known_face_names = [
    "Jungey",
    "Haku"
]

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
            os.path.join(app.root_path, "../frontend/templates"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon"
            )

def base64_to_image(base64_string):
    base64_data = base64_string.split(",")[1]
    image_bytes = base64.b64decode(base64_data)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image

@socketio.on("connect")
def test_connect():
    print("Connected")
    emit("my_response", {"data": "Connected"})

@socketio.on("image")
def receive_image(image):
    image = base64_to_image(image)
    rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    frame_resized = cv2.resize(gray, (400, 225))
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, frame_encoded = cv2.imencode(".jpeg", frame_resized, encode_param)
    processed_img_data = base64.b64encode(frame_encoded).decode()
    b64_src = "data:image/jpeg;base64,"
    processed_img_data = b64_src + processed_img_data
    # print("img_data_processed", processed_img_data)
    # print(type(frame))

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    # rgb_frame = frame[:, :, ::-1]

    # Find all the faces and face enqcodings in the frame of video
    face_locations = face_recognition.face_locations(rgb_frame)
    # print(face_locations)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    # print(rgb_frame)
    # Loop through each face in this frame of video
    name = "Unknown"
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        
        # If a match was found in known_face_encodings, just use the first one.
        # if True in matches:
        #     first_match_index = matches.index(True)
        #     name = known_face_names[first_match_index]

        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            break
    # if name != 'Unknown': print(known_face_names)

    emit("processed_image", {'data': processed_img_data, 'details': name})

@app.route("/face")
def face():
    return render_template("face.html")

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload_images", methods=['GET', 'POST'])
def upload_images():
    if request.method == 'POST':
        print('files', request.files)
        if 'fileImage' not in request.files:
            print('No file part')
            flash('No file part')
            return redirect('/upload')
        files = request.files.getlist('fileImage')
        
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        for file in files:
            if file.filename == '':
                print('No selected file')
                flash('No files selected. Please select an image file.')
                return redirect('/upload')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                print('file upload successful')
        flash('Files successfully uploaded')
        return redirect('/')


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000, host='0.0.0.0')
    
