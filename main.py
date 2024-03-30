# Function to update database on GitHub
def update_database_on_github():
    try:
        print("Adding changes to Git staging area...")
        subprocess.run(["git", "add", DB_FILE])

        print("Committing changes...")
        subprocess.run(["git", "commit", "-m", "Update database"])

        print("Pushing changes to GitHub...")
        subprocess.run(["git", "push", "origin", "main"])

        print("Database update successful!")
    except Exception as e:
        print("Error occurred while updating database on GitHub:")
        print(e)


import cv2
import face_recognition
import numpy as np
import sqlite3
import time
import subprocess
import os  # Import os module for directory manipulation

# Constants
CAMERA_INDEX = 0  # Index for the laptop's built-in camera
FONT = cv2.FONT_HERSHEY_DUPLEX
TEXT_COLOR = (255, 255, 255)
RECTANGLE_COLOR = (0, 0, 255)
RECOGNITION_DELAY = 2  # Delay in seconds between each face recognition operation
GITHUB_TOKEN = "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"  # Replace with your GitHub access token
GITHUB_REPO_URL = "https://github.com/ZebinPepin/Automated-Facial-Recognition"
DB_FILE = "known_faces.db"  # SQLite database file
GIT_REPO_DIR = "C:/Users/pepinz/PycharmProjects/SeniorDesignTesting/venv"  # Path to your Git repository directory


# Function to create a SQLite database connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn


# Function to create the known_faces table
def create_table(conn):
    sql_create_table = """CREATE TABLE IF NOT EXISTS known_faces (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            face_encoding BLOB NOT NULL
                        );"""
    try:
        c = conn.cursor()
        c.execute(sql_create_table)
    except sqlite3.Error as e:
        print(e)


# Function to load known faces from SQLite database
def load_known_faces(conn):
    known_faces = []
    known_names = []
    try:
        c = conn.cursor()
        c.execute("SELECT name, face_encoding FROM known_faces")
        rows = c.fetchall()
        for row in rows:
            known_names.append(row[0])
            known_faces.append(np.frombuffer(row[1], dtype=np.float64))
    except sqlite3.Error as e:
        print(e)
    return known_faces, known_names


# Function to recognize faces and display labels
def recognize_faces(frame, known_faces, known_names, conn):
    # Detect face locations and face encodings
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        top, right, bottom, left = face_location

        # Compare the face encoding of the detected face with all known face encodings
        matches = face_recognition.compare_faces(known_faces, face_encoding)

        # Check if any match is found
        if any(matches):
            # If a match is found, label it as the known face
            label = known_names[matches.index(True)]
        else:
            # Generate a new name for the person
            new_name = f"Person{len(known_names) + 1}"

            # Insert the new face into the database
            try:
                c = conn.cursor()
                c.execute("INSERT INTO known_faces (name, face_encoding) VALUES (?, ?)",
                          (new_name, face_encoding.tobytes()))
                conn.commit()
                print(f"Added {new_name} to the database.")

                # Update known_faces and known_names
                known_faces.append(face_encoding)
                known_names.append(new_name)

                # Change directory to the Git repository
                os.chdir(GIT_REPO_DIR)

                # Update database on GitHub
                update_database_on_github()
            except sqlite3.Error as e:
                print(e)

            # Set label as the new name
            label = new_name

        # Draw the rectangle and display the label on the entire frame
        cv2.rectangle(frame, (left, top), (right, bottom), RECTANGLE_COLOR, 2)
        cv2.putText(frame, label, (left + 6, bottom - 6), FONT, 0.5, TEXT_COLOR, 1)

    return frame


# Function to update database on GitHub
def update_database_on_github():
    try:
        print("Adding changes to Git staging area...")
        subprocess.run(["git", "add", DB_FILE])

        print("Committing changes...")
        subprocess.run(["git", "commit", "-m", "Update database"])

        print("Pushing changes to GitHub...")
        subprocess.run(["git", "push", GITHUB_REPO_URL, "master", f"-u {GITHUB_TOKEN}"])

        print("Database update successful!")
    except Exception as e:
        print("Error occurred while updating database on GitHub:")
        print(e)


# Main function
def main():
    # Create or connect to the SQLite database
    conn = create_connection(DB_FILE)
    if conn is not None:
        create_table(conn)
    else:
        print("Error! Cannot create the database connection.")
        return

    # Load known faces from the SQLite database
    known_faces, known_names = load_known_faces(conn)

    # Open laptop camera
    laptop_cap = cv2.VideoCapture(CAMERA_INDEX)

    while True:
        # Capture frame from laptop camera
        ret_laptop, frame_laptop = laptop_cap.read()

        if ret_laptop:
            # Recognize faces and display labels for laptop camera
            frame_laptop = recognize_faces(frame_laptop, known_faces, known_names, conn)

            # Display the resulting frame from laptop camera
            cv2.imshow('Laptop Camera - Facial Recognition', frame_laptop)

        # Wait for a while before performing the next face recognition operation
        time.sleep(RECOGNITION_DELAY)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Debugging output to check if update_database_on_github() is reached
        print("Attempting to update database on GitHub...")
        update_database_on_github()

    # Release the camera and close all windows
    laptop_cap.release()
    cv2.destroyAllWindows()


# Run the main function if the script is executed
if __name__ == "__main__":
    main()
