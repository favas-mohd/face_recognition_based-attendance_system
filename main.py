import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os
import shutil
import cv2
import numpy as np
import face_recognition
import csv
from datetime import date
from PIL import Image, ImageTk
from collections import defaultdict


# Ensure directory exists
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# Function to load images from a directory
def load_images_from_directory(directory):
    images_dict = {}
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
                name = filename.split("_")[0].upper()  # Capitalize the name
                if name not in images_dict:
                    images_dict[name] = os.path.join(directory, filename)
    return images_dict


# Function to train the face recognition model
def train_model(images_dict):
    encodeListKnown = []
    classNames = list(images_dict.keys())
    for person_name in classNames:
        image_path = images_dict[person_name]
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        if len(face_encodings) > 0:
            encode = face_encodings[0]
            encodeListKnown.append(encode)
        else:
            print("No face detected in image:", image_path)
    return encodeListKnown, classNames


class WebcamCaptureGUI:
    def __init__(self, master, name, person_id):
        self.master = master
        self.master.title("Webcam Feed")

        self.name = name.upper()  # Capitalize the name
        self.person_id = person_id.upper()  # Capitalize the ID

        self.video_frame = tk.Label(master)
        self.video_frame.pack()

        self.cap = cv2.VideoCapture(0)
        self.show_feed()

        self.capture_button = tk.Button(master, text="Capture Image", command=self.capture_image)
        self.capture_button.pack()

    def show_feed(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.video_frame.config(image=self.photo)
            self.video_frame.image = self.photo
            self.video_frame.after(10, self.show_feed)

    def capture_image(self):
        ret, frame = self.cap.read()
        if ret:
            index = 1
            ensure_directory_exists("ImagesAttendance")
            while os.path.exists(f"ImagesAttendance/{self.name}_{self.person_id}_{index}.jpg"):
                index += 1
            cv2.imwrite(f"ImagesAttendance/{self.name}_{self.person_id}_{index}.jpg", frame)
            messagebox.showinfo("Success", f"Image captured for {self.name} (ID: {self.person_id})")
        else:
            messagebox.showerror("Error", "Failed to capture image")

    def close(self):
        self.cap.release()
        self.master.destroy()


class AddImagesGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Add Images")

        self.name = simpledialog.askstring("Input", "Enter person's name:")
        self.person_id = simpledialog.askstring("Input", "Enter person's ID:")

        if self.name and self.person_id:
            self.name = self.name.upper()  # Capitalize the name
            self.person_id = self.person_id.upper()  # Capitalize the ID
            if self.check_existing_id():
                self.add_from_files_button = tk.Button(master, text="Select from Files",
                                                       command=self.add_images_from_files)
                self.add_from_files_button.pack()

                self.take_using_webcam_button = tk.Button(master, text="Take using Webcam",
                                                          command=self.take_images_using_webcam)
                self.take_using_webcam_button.pack()
            else:
                messagebox.showerror("Error", "ID already exists with a different name.")
        else:
            messagebox.showwarning("Warning", "No name or ID entered.")

    def check_existing_id(self):
        # Ensure the directory exists
        ensure_directory_exists("ImagesAttendance")
        for filename in os.listdir("ImagesAttendance"):
            if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
                name, id_in_file, _ = filename.split("_")
                if id_in_file.upper() == self.person_id and name != self.name:
                    return False
        return True

    def add_images_from_files(self):
        if self.name and self.person_id:
            file_paths = filedialog.askopenfilenames(title="Select images")
            if file_paths:
                ensure_directory_exists("ImagesAttendance")
                for i, file_path in enumerate(file_paths):
                    new_image_path = f"ImagesAttendance/{self.name}_{self.person_id}_{i + 1}.jpg"
                    shutil.copy(file_path, new_image_path)
                messagebox.showinfo("Success", f"Images added for {self.name} (ID: {self.person_id})")
            else:
                messagebox.showwarning("Warning", "No images selected.")
        else:
            messagebox.showwarning("Warning", "No name or ID entered.")

    def take_images_using_webcam(self):
        if self.name and self.person_id:
            WebcamCaptureGUI(tk.Toplevel(), self.name, self.person_id)


def take_attendance(subject_name, tolerance=0.5, new_session=True):
    subject_name = subject_name.upper()  # Capitalize the subject name
    images_dict = load_images_from_directory("ImagesAttendance")
    encodeListKnown, classNames = train_model(images_dict)
    print("classNames:", classNames)

    today = date.today()
    folder_name = today.strftime('%Y-%m-%d')
    ensure_directory_exists(folder_name)
    attendance_file = f"{folder_name}/{subject_name}_{today.strftime('%Y-%m-%d')}.csv"
    attendance_dict = {}
    session_number = 1

    if os.path.exists(attendance_file):
        with open(attendance_file, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)  # Read header
            if "Session1" in header:
                session_number = int(header[-1].replace("Session", "")) + 1 if new_session else int(
                    header[-1].replace("Session", ""))
            for row in reader:
                attendance_dict[row[0].upper()] = row[1:]  # Capitalize names

    # Ensure all names have an entry for the current session
    for name in classNames:
        if name not in attendance_dict:
            attendance_dict[name] = ["Absent"] * session_number
        else:
            if len(attendance_dict[name]) < session_number:
                attendance_dict[name].append("Absent")

    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read frame from webcam")
            break

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=tolerance)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()

                # Always display name and mark present message
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, f"{name} - Marked Present", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1,
                            (255, 255, 255), 2)

                # Ensure the name exists in the dictionary
                if name not in attendance_dict:
                    attendance_dict[name] = ["Absent"] * session_number
                attendance_dict[name][-1] = "Present"
                print(f"Marked {name} as Present for Session {session_number}")

        # Identify and mark unknown individuals
        for faceLoc in facesCurFrame:
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            # Check if the face is not recognized
            if all(not match for match in matches):
                # Draw red bounding box around face
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
                cv2.putText(img, "Unknown", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow('Webcam', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    with open(attendance_file, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ["Name"] + [f"Session{i + 1}" for i in range(session_number)]
        writer.writerow(header)
        for name, sessions in attendance_dict.items():
            writer.writerow([name] + sessions)
    messagebox.showinfo("Success", f"Attendance for {subject_name} recorded successfully!")


def create_consolidated_csv():
    today = date.today()
    month_name = today.strftime('%B')  # Get the full name of the current month
    consolidated_csv_file = f"Consolidated_{month_name}.csv"  # Change the file name format

    attendance_data = defaultdict(lambda: defaultdict(int))
    for folder_name in os.listdir('.'):
        if os.path.isdir(folder_name) and folder_name != 'ImagesAttendance':
            for csv_file in os.listdir(folder_name):
                if csv_file.endswith('.csv'):
                    subject_name = csv_file.split('_')[0]
                    with open(os.path.join(folder_name, csv_file), 'r') as file:
                        reader = csv.reader(file)
                        header = next(reader)  # Skip header
                        session_count = len(header) - 1  # Excluding the Name column
                        for row in reader:
                            name = row[0].upper()  # Capitalize names
                            for session_index in range(1, session_count + 1):
                                if row[session_index] == "Present":
                                    attendance_data[name][subject_name] += 1

    # Write consolidated attendance data to CSV file
    with open(consolidated_csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        subjects = sorted(set(subject for record in attendance_data.values() for subject in record))
        writer.writerow(["Name"] + subjects)
        for name, record in attendance_data.items():
            writer.writerow([name] + [record.get(subject, 0) for subject in subjects])

    messagebox.showinfo("Success", f"Consolidated attendance CSV file created: {consolidated_csv_file}")


# Function to create the GUI
def create_gui():
    root = tk.Tk()
    root.title("Attendance System")

    # Function to handle the "Take Attendance" button click
    def on_take_attendance():
        subject_name = simpledialog.askstring("Input", "Enter subject name:")
        if subject_name:
            subject_name = subject_name.upper()  # Capitalize the subject name
            today = date.today()
            folder_name = today.strftime('%Y-%m-%d')
            attendance_file = f"{folder_name}/{subject_name}_{today.strftime('%Y-%m-%d')}.csv"
            if os.path.exists(attendance_file):
                dialog = tk.Toplevel(root)
                dialog.title("Session Exists")

                tk.Label(dialog, text=f"Attendance for {subject_name} already exists. Would you like to take a new session or continue existing?").pack()

                def on_existing():
                    dialog.destroy()
                    take_attendance(subject_name, new_session=False)

                def on_new():
                    dialog.destroy()
                    take_attendance(subject_name, new_session=True)

                tk.Button(dialog, text="Existing", command=on_existing).pack(side=tk.LEFT)
                tk.Button(dialog, text="New", command=on_new).pack(side=tk.RIGHT)
            else:
                take_attendance(subject_name, new_session=True)

    # Function to handle the "Add Images" button click
    def on_add_images():
        AddImagesGUI(tk.Toplevel())

    # Function to handle the "Create Consolidated CSV" button click
    def on_create_consolidated_csv():
        create_consolidated_csv()

    # Button to take attendance
    take_attendance_button = tk.Button(root, text="Take Attendance", command=on_take_attendance)
    take_attendance_button.pack()

    # Button to add images
    add_images_button = tk.Button(root, text="Add Images", command=on_add_images)
    add_images_button.pack()

    # Button to create consolidated CSV
    create_consolidated_csv_button = tk.Button(root, text="Create Consolidated CSV", command=on_create_consolidated_csv)
    create_consolidated_csv_button.pack()

    root.mainloop()


# Main function
def main():
    create_gui()


if __name__ == "__main__":
    main()
