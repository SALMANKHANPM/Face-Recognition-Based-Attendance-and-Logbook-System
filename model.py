import pickle
import numpy as np
import cv2 as cv
import face_recognition as fr
from datetime import datetime
from firebaseHandler import login, logout


# def model(db):
#     global stuData
#     stuData = None
#     capture = cv.VideoCapture(0)
#     capture.set(3, 640)
#     capture.set(4, 480)
#
#     with open('EncodeFile.p', 'rb') as file:
#         encodeListWithIDs = pickle.load(file)
#     encodeListKnown, studentIDs = encodeListWithIDs
#     print(studentIDs)
#
#     try:
#         while True:
#             success, img = capture.read()
#             if not success:
#                 break
#
#             imgResize = cv.resize(img, (0, 0), None, 0.25, 0.25)
#             imgConverted = cv.cvtColor(imgResize, cv.COLOR_BGR2RGB)
#
#             faceCurFrame = fr.face_locations(imgConverted)
#             encodeCurFrame = fr.face_encodings(imgConverted, faceCurFrame)
#
#             if faceCurFrame:
#                 for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
#                     faceMatches = fr.compare_faces(encodeListKnown, encodeFace)
#                     faceDistance = fr.face_distance(encodeListKnown, encodeFace)
#
#                     matchIndex = np.argmin(faceDistance)
#
#                     if faceMatches[matchIndex]:
#                         y1, x2, y2, x1 = faceLoc
#                         y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  # Scale back up face locations since the frame was scaled down
#                         cv.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Draw rectangle around the face
#
#                         defaultId = studentIDs[matchIndex]
#
#
#                         # Get the current date and time
#                         now = datetime.now()
#                         dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
#                         print("date and time =", dt_string)
#
#                         # Fetching DATA
#                         studentInfo = db.child(f'Students/{defaultId}').get()
#                         print("studentInfo:", studentInfo.val()['Name'])
#                         stuData = studentInfo.val()
#
#                         name = studentInfo.val()['Name']
#                         cv.putText(img, name, (x1 + 6, y2 - 6), cv.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
#                         cv.putText(img, "ID: " + defaultId, (x1 + 6, y2 + 20), cv.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
#                         cv.putText(img, 'Captured', (x1 + 6, y2 + 50), cv.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
#                         if studentInfo.val() is None:
#                             print("Error: studentInfo is None")
#                         else:
#                             # Fetching and Updating Attendance based on the time elapsed
#                             datetimeObject = datetime.strptime(studentInfo.val()['Last_attendance_time'],
#                                                                "%Y-%m-%d %H:%M:%S")
#                             secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
#                             # print(secondsElapsed)
#                             if secondsElapsed > 30:
#                                 ref = db.child(defaultId)
#                                 studentInfo.val()['Total_attendance'] += 1
#                                 ref.update({'Total_attendance': studentInfo.val()['Total_attendance']})
#                                 ref.update({'Last_attendance_time': dt_string})
#                                 cv.putText(img, 'Attendance Marked Already', (x1 + 6, y2 + 80), cv.FONT_HERSHEY_COMPLEX, 1,
#                                            (255, 255, 255), 2)
#                                 print("Attendance Marked")
#
#             ret, buffer = cv.imencode('.jpg', img)
#             frame = buffer.tobytes()
#             yield frame, stuData
#
#     except Exception as e:
#         print("An error occurred:", e)
#     finally:
#         capture.release()
#         cv.destroyAllWindows()


def model(db):
    capture = cv.VideoCapture(0)
    capture.set(3, 1500)
    capture.set(4, 1000)

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
                            print("Error: studentInfo is None")
                        else:
                            datetimeObject = datetime.strptime(studentInfo.val()['Last_attendance_time'],
                                                               "%Y-%m-%d %H:%M:%S")
                            secondsElapsed = (datetime.now() - datetimeObject).total_seconds()

                            if secondsElapsed > 30:
                                if matchIndex not in encountered_indices:
                                    cv.putText(img, 'Captured', (x1 + 6, y2 + 50), cv.FONT_HERSHEY_COMPLEX, .5,
                                               (255, 255, 255), 1)
                                    login(defaultId, dt_string)
                                    print('Captured')
                                    encountered_indices[matchIndex] = True
                                else:
                                    cv.putText(img, 'Already Taken', (x1 + 6, y2 + 50), cv.FONT_HERSHEY_COMPLEX, .5,
                                               (255, 255, 255), 1)
                                print("Attendance Marked")

                            if secondsElapsed / 60 > 1:
                                encountered_indices.pop(matchIndex, None)
                                cv.putText(img, 'Logged Out', (x1 + 6, y2 + 50), cv.FONT_HERSHEY_COMPLEX, .5,
                                           (255, 255, 255), 1)
                                logout(defaultId)

            ret, buffer = cv.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield frame

    except Exception as e:
        print("An error occurred:", e)
    finally:
        capture.release()
        cv.destroyAllWindows()
