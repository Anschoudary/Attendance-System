from flask import render_template, request, redirect, url_for, flash
import cv2
from datetime import datetime
from . import db
from .models import Attendance
from .utils import train_model  # Assuming your train_model method is in utils.py
import os
from flask import Blueprint

main = Blueprint('main', __name__)

# Main route
@main.route('/')
def index():
    return render_template('index.html')

# Add Person route
from .camera import Camera  # Assuming the Camera class is saved in camera.py

@main.route('/add_person', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        person_name = request.form.get('person_name')

        if not person_name:
            flash("Please enter a name.", "error")
            return redirect(url_for('main.add_person'))

        person_dir = f'data/{person_name}'
        os.makedirs(person_dir, exist_ok=True)

        camera = Camera()
        cap = camera.open_camera()
        if not cap.isOpened():
            flash("Error: Unable to access the camera.", "error")
            return redirect(url_for('main.add_person'))

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        images_captured = 0

        try:
            while images_captured < 100:
                ret, frame = cap.read()
                if not ret:
                    flash("Error: Could not read frame from camera.", "error")
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y + h, x:x + w]
                    cv2.imwrite(f'{person_dir}/{images_captured + 1}.jpg', roi_gray)
                    images_captured += 1

                cv2.imshow('Capturing Images', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            # cap.release()
            # cv2.destroyAllWindows()
            camera.release_camera()

        if images_captured < 100:
            flash(f"Only {images_captured} images captured. Ensure at least 100 images.", "warning")
            return redirect(url_for('main.add_person'))

        flash(f"Images captured for {person_name}. Training model...", "info")
        recognizer = train_model('data')
        recognizer, label_map = train_model('data')
        if recognizer:
            flash(f"Model trained successfully for {person_name}.", "success")
        else:
            flash("Error: Could not train the model. Check data and try again.", "error")

        return redirect(url_for('main.add_person'))

    return render_template('add_person.html')

# Detect Person route
@main.route('/detect_person', methods=['GET', 'POST'])
def detect_person():
    if request.method == 'POST':
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        recognizer, label_map = train_model('data')

        if not recognizer:
            flash("Error: Could not load face recognition model.", "error")
            return redirect(url_for('main.index'))

        camera = Camera()
        cap = camera.open_camera()
        if not cap.isOpened():
            flash("Error: Unable to access the camera.", "error")
            return redirect(url_for('main.detect_person'))

        try:
            flash("Starting face detection. Press 'q' to stop.", "info")
            while True:
                ret, frame = cap.read()
                if not ret:
                    flash("Error: Could not read frame from camera.", "error")
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y + h, x:x + w]
                    label, confidence = recognizer.predict(roi_gray)
                    name = label_map.get(label, "Unknown")

                    if name != "Unknown":
                        current_date = datetime.now().date()
                        current_time = datetime.now().time()

                        existing_record = Attendance.query.filter_by(name=name, date=current_date).first()
                        if not existing_record:
                            new_attendance = Attendance(name=name, date=current_date, time=current_time)
                            db.session.add(new_attendance)
                            db.session.commit()

                    cv2.putText(frame, f"{name} ({confidence:.2f})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            camera.release_camera()

        return redirect(url_for('main.detect_person'))

    return render_template('detect_person.html')

# View Attendance route
@main.route('/view_attendance')
def view_attendance():
    attendances = Attendance.query.all()
    return render_template('view_attendance.html', attendances=attendances)

# Delete Person route
@main.route('/delete_person', methods=['GET', 'POST'])
def delete_person():
    if request.method == 'POST':
        person_name = request.form.get('person_name')

        if not person_name:
            flash("Please provide a person's name.", "error")
            return redirect(url_for('main.delete_person'))

        # Check if the person exists
        person_dir = os.path.join('data', person_name)
        if os.path.exists(person_dir):
            # Delete the person's folder
            import shutil
            shutil.rmtree(person_dir)

            # Delete related attendance records
            Attendance.query.filter_by(name=person_name).delete()
            db.session.commit()

            flash(f"Successfully deleted {person_name} and their attendance records.", "success")
        else:
            flash(f"Person '{person_name}' does not exist.", "error")

        return redirect(url_for('main.delete_person'))

    # If GET method, display the delete form
    return render_template('delete_person.html')

