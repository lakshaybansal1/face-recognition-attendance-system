"""
Face Recognition Attendance System - Main Application
Author: Lakshay Bansal
University at Albany - Computer Science

Description:
Real-time face recognition based attendance system using
OpenCV, face_recognition, Firebase Realtime Database, and
a custom GUI overlay.

This file has been refactored and customized by Lakshay Bansal.
"""

import os
import pickle
import cv2
import numpy as np
import face_recognition
import cvzone
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, db




def setup_firebase():
    """Initialize Firebase only once."""
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://faceattendancesystem-961cf-default-rtdb.firebaseio.com/"
        })


setup_firebase()
students_ref = db.reference("Students")



def load_mode_images(folder_path: str):
    """Load all mode UI images into a list."""
    images = []
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        images.append(cv2.imread(full_path))
    return images


def load_encodings(file_path: str):
    """Load known face encodings and their corresponding student IDs."""
    print("Loading face encodings...")
    with open(file_path, "rb") as f:
        known_encodings, known_ids = pickle.load(f)
    print("Encodings loaded successfully.")
    return known_encodings, known_ids




def can_mark_attendance(last_time_str: str, cooldown_seconds: int = 30) -> bool:
    """Check if enough time has passed to mark attendance again."""
    try:
        last_time = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return True

    elapsed = (datetime.now() - last_time).total_seconds()
    return elapsed > cooldown_seconds


def update_attendance(student_id: str, student_data: dict):
    """Update attendance count and timestamp in Firebase."""
    new_total = student_data.get("total_attendance", 0) + 1

    students_ref.child(student_id).update({
        "total_attendance": new_total,
        "last_attendance_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    student_data["total_attendance"] = new_total
    student_data["last_attendance_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")




def main():
    # Webcam configuration
    camera = cv2.VideoCapture(0)
    camera.set(3, 640)
    camera.set(4, 480)

    background_img = cv2.imread("Resources/background.png")

    # Load UI modes
    mode_images = load_mode_images("Resources/Modes")

    # Load encodings
    known_encodings, known_ids = load_encodings("EncodeFile.p")

    # Runtime state variables
    current_mode = 0
    frame_counter = 0
    active_id = None
    active_student = None
    active_student_img = None

    while True:
        success, frame = camera.read()
        if not success:
            print("Warning: Unable to read from webcam.")
            continue

        # Resize and convert for faster processing
        small_frame = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # Draw camera feed on background
        background_img[162:162 + 480, 55:55 + 640] = frame
        background_img[44:44 + 633, 808:808 + 414] = mode_images[current_mode]

        if face_locations:
            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                distances = face_recognition.face_distance(known_encodings, face_encoding)

                best_match_index = np.argmin(distances)

                if matches[best_match_index]:
                    # Scale face location back to original size
                    top, right, bottom, left = face_location
                    top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4

                    box = 55 + left, 162 + top, right - left, bottom - top
                    cvzone.cornerRect(background_img, box, rt=0)

                    active_id = known_ids[best_match_index]

                    if frame_counter == 0:
                        cvzone.putTextRect(background_img, "Checking...", (275, 400))
                        cv2.imshow("Face Attendance", background_img)
                        cv2.waitKey(1)

                        frame_counter = 1
                        current_mode = 1

            

            if frame_counter == 1:
                active_student = students_ref.child(active_id).get()

                if not active_student:
                    print(f"No record found for student ID: {active_id}")
                    frame_counter = 0
                    current_mode = 0
                    continue

                # Ensure required fields exist
                active_student.setdefault("name", active_id)
                active_student.setdefault("branch", "N/A")
                active_student.setdefault("total_attendance", 0)
                active_student.setdefault("last_attendance_time", "2000-01-01 00:00:00")

                # Load local student image
                image_path = f"Images/{active_id}.jpg"
                if not os.path.exists(image_path):
                    print(f"Missing local image for {active_id}")
                    frame_counter = 0
                    current_mode = 0
                    continue

                raw_img = cv2.imread(image_path)
                active_student_img = cv2.resize(raw_img, (216, 216))
                background_img[175:175 + 216, 909:909 + 216] = active_student_img

                # Attendance update
                if can_mark_attendance(active_student["last_attendance_time"]):
                    update_attendance(active_id, active_student)
                else:
                    current_mode = 3
                    frame_counter = 0

         

            if current_mode != 3:
                if 10 < frame_counter < 20:
                    current_mode = 2

                background_img[44:44 + 633, 808:808 + 414] = mode_images[current_mode]

                if frame_counter <= 10:
                    # Display student information
                    cv2.putText(
                        background_img,
                        str(active_student["total_attendance"]),
                        (1080, 630),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (255, 255, 255),
                        1
                    )

                    cv2.putText(
                        background_img,
                        str(active_student["branch"]),
                        (950, 550),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.4,
                        (255, 255, 255),
                        1
                    )

                    cv2.putText(
                        background_img,
                        str(active_id),
                        (950, 493),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.5,
                        (255, 255, 255),
                        1
                    )

                    (text_width, _), _ = cv2.getTextSize(
                        active_student["name"],
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        1
                    )

                    center_offset = (414 - text_width) // 2
                    cv2.putText(
                        background_img,
                        active_student["name"],
                        (808 + center_offset, 445),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (255, 255, 255),
                        1
                    )

                    background_img[175:175 + 216, 909:909 + 216] = active_student_img

                frame_counter += 1

                if frame_counter >= 20:
                    frame_counter = 0
                    current_mode = 0
                    active_student = None
                    active_student_img = None
                    background_img[44:44 + 633, 808:808 + 414] = mode_images[current_mode]

        else:
            current_mode = 0
            frame_counter = 0

        cv2.imshow("Face Attendance", background_img)
        cv2.waitKey(1)




if __name__ == "__main__":
    main()
