# face_recognition_based-attendance_system
An automated attendance system using face recognition technology, built with Python and OpenCV, for accurate and efficient attendance tracking. The system features live capture and a user-friendly Flask-based interface.
# Attendance System using Face Recognition

## Features

- Face recognition for attendance marking
- Capture images using a webcam
- Add multiple images for the same person
- Prevent adding different names with an existing ID
- GUI-based application using Tkinter
- Generate consolidated attendance reports

## System Requirements

- Python 3.x
- OpenCV
- face-recognition
- tkinter
- dlib
- PIL (Pillow)

## Installation

1. Clone the repository:

    ```bash
     git clone https://github.com/favas-mohd/face_recognition_based-attendance_system.git
    cd face_recognition_based-attendance_system
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Download the `shape_predictor_68_face_landmarks.dat` file and place it in the project directory. You can get it from [dlib's model repository](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2).

## Usage

1. Run the application:

    ```bash
    python main.py
    ```

2. Use the interface to capture images, add new users, and mark attendance.

### GUI Features

- **Take Attendance**: Allows taking attendance for a given subject. If attendance for the subject already exists for the day, you can choose to continue the existing session or start a new session.
- **Add Images**: Allows adding images for new users. You can either select images from files or capture them using a webcam.
- **Create Consolidated CSV**: Generates a consolidated CSV file for the attendance records of the current month.

## Project Structure

```plaintext
attendance-system/
│
├── main.py                # Main application file
├── requirements.txt       # List of dependencies
├── shape_predictor_68_face_landmarks.dat  # Face landmarks data file
├── ImagesAttendance/      # Directory to store captured images
├── README.md              # Project readme
└── Other files and directories
