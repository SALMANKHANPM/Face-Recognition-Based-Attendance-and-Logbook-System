import cv2 as cv
import face_recognition as fr
import numpy as np
import pickle
from datetime import datetime
from firebaseHandler import initializeFirebase

def model():
    # Initialize Firebase and get the database reference
    _, db = initializeFirebase()

    # Set up the video capture device
    capture = cv.VideoCapture(0)
    capture.set(3, 640)  # Set the width
    capture.set(4, 480)  # Set the height

    # Load the face recognition model
    with open('EncodeFile.p', 'rb') as file:
        encodeListWithIDs = pickle.load(file)
    encodeListKnown, studentIDs = encodeListWithIDs

    while True:
        success, img = capture.read()
        if not success:
            break  # If the frame is not successfully read, break the loop

        imgResize = cv.resize(img, (0, 0), None, 0.25, 0.25)
        imgConverted = cv.cvtColor(imgResize, cv.COLOR_BGR2RGB)

        faceCurFrame = fr.face_locations(imgConverted)
        encodeCurFrame = fr.face_encodings(imgConverted, faceCurFrame)

        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            faceMatches = fr.compare_faces(encodeListKnown, encodeFace)
            faceDistance = fr.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDistance)

            if faceMatches[matchIndex]:
                y1, x2, y2, x1 = [coordinate * 4 for coordinate in faceLoc]  # Scale back up face locations
                cv.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Draw rectangle around the face

                student_id = studentIDs[matchIndex]
                try:
                    # Database interaction
                    studentInfo = db.child(f'Students/{student_id}').get()
                    if studentInfo is not None:
                        last_attendance_time = studentInfo['Last_attendance_time']
                        datetimeObject = datetime.strptime(last_attendance_time, "%d/%m/%Y %H:%M:%S")
                        secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                        if secondsElapsed > 30:
                            total_attendance = studentInfo.val()['Total_attendance'] + 1
                            ref = db.child(student_id)
                            ref.update({
                                'Total_attendance': total_attendance,
                                'Last_attendance_time': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            })
                except Exception as e:
                    print(f"Failed to update database: {e}")

        # Encode and yield the frame
        frame = cv.imencode('.jpg', img)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Release the video capture device and close any open windows
    capture.release()