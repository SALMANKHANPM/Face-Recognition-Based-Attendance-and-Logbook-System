import pickle
import numpy as np
import cv2 as cv
import face_recognition as fr
from datetime import datetime
from firebaseHandler import login, logbookLogin, logbookLogout, fetchAndDeleteReason

import threading as th


def modelThread(db, currentRoute, reason=None):
    t = th.Thread(target=model, args=(db, currentRoute, reason))
    t.start()


def model(db, currentRoute, reason=None):
    capture = cv.VideoCapture(0)
    capture.set(3, 1000)
    capture.set(4, 800)
    with open('EncodeFile.p', 'rb') as file:
        encodeListWithIDs = pickle.load(file)
    encodeListKnown, studentIDs = encodeListWithIDs
    print(studentIDs)

    encountered_indices = {}

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
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        cv.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

                        defaultId = studentIDs[matchIndex]

                        now = datetime.now()
                        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

                        # Fetching DATA
                        studentInfo = db.child(f'Students/{defaultId}').get()

                        cv.putText(img, "ID: " + defaultId, (x1 + 6, y2 + 20), cv.FONT_HERSHEY_COMPLEX, 1,
                                   (255, 255, 255), 2)

                        if studentInfo.val() is None:
                            cv.putText(img, 'Not Found', (x1 + 6, y2 + 50), cv.FONT_HERSHEY_COMPLEX, .5,
                                       (255, 255, 255), 1)
                        else:
                            datetimeObject = datetime.strptime(studentInfo.val()['Last_attendance_time'],
                                                               "%Y-%m-%d %H:%M:%S")
                            secondsElapsed = (datetime.now() - datetimeObject).total_seconds()

                            res = ''

                            if currentRoute == 0:  # For Attendance
                                print('Im in Attendance')
                                if secondsElapsed > 30:
                                    if matchIndex not in encountered_indices:
                                        cv.putText(img, 'Captured', (x1 + 6, y2 + 50), cv.FONT_HERSHEY_COMPLEX, .5,
                                                   (255, 255, 255), 1)
                                        res = login(defaultId, dt_string)  # Assuming login() is defined correctly
                                        print('Attendance Captured')
                                        encountered_indices[matchIndex] = True
                                    else:
                                        cv.putText(img, res, (x1 + 6, y2 + 50), cv.FONT_HERSHEY_COMPLEX, .5,
                                                   (255, 255, 255), 1)
                                    print("Attendance Already Marked")

                            elif currentRoute == 1:  # For Login entry into Logbook
                                print('Im in Login')
                                print(reason)
                                if secondsElapsed > 10:
                                    if matchIndex not in encountered_indices:
                                        cv.putText(img, 'Captured', (x1 + 6, y2 + 50), cv.FONT_HERSHEY_COMPLEX, .5,
                                                   (255, 255, 255), 1)
                                        reason = fetchAndDeleteReason()
                                        res = logbookLogin(defaultId, reason)  # Modify reason as needed
                                        print('Login Captured')
                                        print(reason)
                                        encountered_indices[matchIndex] = True
                                    else:
                                        cv.putText(img, 'Login Already Recorded', (x1 + 6, y2 + 50),
                                                   cv.FONT_HERSHEY_COMPLEX, .5,
                                                   (255, 255, 255), 1)
                                        print(reason)
                                        print("Login Already Recorded")

                            elif currentRoute == 2:
                                print('Im in Logout')
                                # For Logout entry into Logbook
                                if secondsElapsed > 10:
                                    if matchIndex not in encountered_indices:
                                        cv.putText(img, 'Logout Success', (x1 + 6, y2 + 50), cv.FONT_HERSHEY_COMPLEX,
                                                   .5,
                                                   (255, 255, 255), 1)
                                        res = logbookLogout(defaultId)  # No dt_string needed here
                                        print('Logout Captured')
                                        encountered_indices[matchIndex] = True
                                    else:
                                        cv.putText(img, 'Logout Already Recorded', (x1 + 6, y2 + 50),
                                                   cv.FONT_HERSHEY_COMPLEX, .5,
                                                   (255, 255, 255), 1)
                                    print("Logout Already Recorded")

            ret, buffer = cv.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield frame

    except Exception as e:
        print("An error occurred:", e)
    finally:
        capture.release()


def detectFace():
    face_cascase = cv.CascadeClassifier(cv.data.haarcascades + 'xml/haarcascade_frontalface_default.xml')

    capture = cv.VideoCapture(0)
    ret, frame = capture.read()

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    faces = face_cascase.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    capture.release()

    return frame
