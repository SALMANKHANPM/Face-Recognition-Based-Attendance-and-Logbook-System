import pickle
import numpy as np
import cv2 as cv
import face_recognition as fr
from datetime import datetime


def model(db):

    capture = cv.VideoCapture(0)
    capture.set(3, 640)
    capture.set(4, 480)


    with open('EncodeFile.p', 'rb') as file:
        encodeListWithIDs = pickle.load(file)
    encodeListKnown, studentIDs = encodeListWithIDs
    print(studentIDs)

    try:
        while True:
            success, img = capture.read()
            if not success:
                break

            imgResize = cv.resize(img, (0, 0), None, 0.25, 0.25)
            imgConverted = cv.cvtColor(imgResize, cv.COLOR_BGR2RGB)

            faceCurFrame = fr.face_locations(imgConverted)
            encodeCurFrame = fr.face_encodings(imgConverted, faceCurFrame)

            if faceCurFrame:
                for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                    faceMatches = fr.compare_faces(encodeListKnown, encodeFace)
                    faceDistance = fr.face_distance(encodeListKnown, encodeFace)

                    matchIndex = np.argmin(faceDistance)

                    if faceMatches[matchIndex]:
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  # Scale back up face locations since the frame was scaled down
                        cv.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Draw rectangle around the face

                        defaultId = studentIDs[matchIndex]
                        print(defaultId)

                        # Get the current date and time
                        now = datetime.now()
                        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                        print("date and time =", dt_string)

                        # Fetching DATA
                        studentInfo = db.child(f'Students/{defaultId}').get()
                        print("studentInfo:", studentInfo)

                        # # Fetching and Updating Attendance based on the time elapsed
                        if studentInfo is not None:
                            datetimeObject = datetime.strptime(studentInfo['Last_attendance_time'], "%d/%m/%Y %H:%M:%S")
                            secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                        # print(secondsElapsed)
                            if secondsElapsed > 30:
                                ref = db.child(defaultId)
                                studentInfo.val()['Total_attendance'] += 1
                                ref.update({'Total_attendance': studentInfo.val()['Total_attendance']})
                                ref.update({'Last_attendance_time': dt_string})

            ret, buffer = cv.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    except Exception as e:
        print("An error occurred:", e)
    finally:
        capture.release()
        cv.destroyAllWindows()
