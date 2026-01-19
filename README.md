# 🎥 Face Recognition Attendance System

Developed and maintained by **Lakshay Bansal**  
University at Albany — Department of Computer Science  

An innovative Face Recognition-based Attendance System that uses deep learning to capture and recognize student faces, update attendance records in real-time using Firebase, and provide a user-friendly GUI for manual database management.

---

## ✨ Features

- **🎬 Real-Time Face Recognition**: Detects and recognizes student faces in real-time using a webcam and deep learning techniques.
- **📊 Firebase Integration**: Stores and manages student data and attendance records using Firebase Realtime Database.
- **📈 Automatic Attendance Marking**: Automatically updates attendance status in Firebase for recognized students.
- **🖥️ Manual Database Management GUI**: Built with `Tkinter` for easy addition, removal, and modification of student records.
- **📤 Export to Excel**: Export student data to an Excel file for reporting and analysis.

---

## 📋 Prerequisites

- **Python 3.x**
- Required Python Libraries:  
  `opencv-python`, `numpy`, `face_recognition`, `cvzone`, `firebase-admin`, `tkinter`, `pandas`
- **Dlib and CMake**: Install Visual Studio with **Desktop Development with C++** to compile required C++ libraries.
- A Firebase project with Realtime Database configured.
- A valid `serviceAccountKey.json` file for Firebase authentication.

---

## 🚀 Setup Instructions

1. **Clone the Repository**:

```bash
git clone https://github.com/LakshayBansal/Face-Recognition-Attendance-System.git
cd Face-Recognition-Attendance-System
