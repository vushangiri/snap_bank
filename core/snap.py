import base64
import os
import cv2
import numpy as np
import pandas as pd
from flask import Flask, render_template, send_from_directory, request, redirect, flash
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit
import face_recognition
import json

## app config
app = Flask(__name__, template_folder="../assets/templates", static_folder="../assets/static")
app.config["SECRET_KEY"] = "secret!"

# config upload folder
UPLOAD_FOLDER = '../assets/static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# check if file type is in allowed list
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

## initialize socketIO 
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")


# Load a sample picture and learn how to recognize it.
# jungey_image = face_recognition.load_image_file("../assets/static/images/jungey.jpg")
# jungey_face_encoding = face_recognition.face_encodings(jungey_image)[0]
# print(type(jungey_face_encoding))

# Load a second sample picture and learn how to recognize it.
# haku_image = face_recognition.load_image_file("../assets/static/images/haku.jpg")
# haku_face_encoding = face_recognition.face_encodings(haku_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    
]
known_face_names = [
    "Jungey",
    "Haku"
]


## route for favicon
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
            os.path.join(app.root_path, "../assets/templates"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon"
            )


## decode base64 images
def base64_to_image(base64_string):
    base64_data = base64_string.split(",")[1]
    image_bytes = base64.b64decode(base64_data)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image


## socketIO connection test
@socketio.on("connect")
def test_connect():
    print("Connected")
    emit("my_response", {"data": "Connected"})


## receive video feed and compare each frame with known face encodings
@socketio.on("image")
def receive_image(data_img):
    image_data = data_img['data']
    res_data = []
    # print(image_data[0])
    # print(image_data[-1])
    for dt_img in image_data:
        image = dt_img
        cnt = data_img['img_count'] 
        image = base64_to_image(image)
        rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        frame_resized = cv2.resize(gray, (400, 225))
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, frame_encoded = cv2.imencode(".jpeg", frame_resized, encode_param)
        processed_img_data = base64.b64encode(frame_encoded).decode()
        b64_src = "data:image/jpeg;base64,"
        processed_img_data = b64_src + processed_img_data
        # processed_img_data = 'test'
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
        name = "okay"
        result_image = []
        store_csv = pd.read_csv('store.csv', header=None)
        try:
            # current_arr = np.array(map(lambda x: np.float64(x), store_csv.iloc[cnt][2]))
            current_arr = np.array(json.loads(store_csv.iloc[cnt][2]))
            # print(type(store_csv.iloc[cnt][2]))
            # print(np.array(store_csv.iloc[0][2]))
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces([current_arr], face_encoding)

                # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance([current_arr], face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    result_image = store_csv.iloc[cnt][1]
                    res_data.append(dt_img)
                    break
            # processed_img_data = f"../assets/static/images/{store_csv.iloc[cnt][1]}"
            # processed_img_data = data_img['data']
        except Exception as e:
            print(e) 
            name = "Unknown"
    # if name != 'Unknown': print(known_face_names)
    processed_img_data = res_data if res_data else data_img['data']

    emit("processed_image", {'data': processed_img_data, 'details': name, 'result_image': result_image,'img_count': cnt + 1})


## undefined
@app.route("/face")
def face():
    return render_template("face.html")



@app.route("/retrieve")
def retrieve():
    return render_template("retrieve.html")

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload_images", methods=['GET', 'POST'])
def upload_images():
    import csv
    if request.method == 'POST':
        print('files', request.files)
        if 'fileImage' not in request.files:
            print('No file part')
            flash('No file part')
            return redirect('/upload')
        files = request.files.getlist('fileImage')
        
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        st = open('store.json', 'r')
        store = json.load(st)
        image_count = store["count"]["image_count"]
        img_list = []
        csv_row = []
        for file in files:
            if file.filename == '':
                print('No selected file')
                flash('No files selected. Please select an image file.')
                return redirect('/upload')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                fn = filename.split('.')
                image_count += 1
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{str(image_count)}.{fn[-1]}"))
                img_list.append(f"{str(image_count)}.{fn[-1]}")
                image = face_recognition.load_image_file(file)
                image_face_encoding = face_recognition.face_encodings(image)
                for fe in image_face_encoding:
                    csv_row.append([store["data"]["event_id"], f"{str(image_count)}.{fn[-1]}", list(fe)])

                print('file upload successful')
        flash('Files successfully uploaded')
        store["count"]["image_count"] = image_count
        store['data']['images'] += img_list
        dmp_file = json.dumps(store, indent=4)
        file = open('store.json', 'w')
        file.write(dmp_file)
        file.close()
        st.close()
        csv_file = open("store.csv", 'w', newline='')
        writer = csv.writer(csv_file)
        writer.writerows(csv_row)
        csv_file.close()
        return redirect('/')


if __name__ == "__main__":

    ## socket io config
    socketio.run(app, debug=True, port=5000, host='0.0.0.0')

    ## app config to reload template on debugging mode
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0')
    
