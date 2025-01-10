import cv2
import os
import numpy as np
from .models import Person

def capture_images(face_cascade, person_dir, num_images=100):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    images_captured = 0
    while images_captured < num_images:
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame from camera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            cv2.imwrite(f'{person_dir}/{images_captured + 1}.jpg', roi_gray)
            images_captured += 1

            if images_captured >= num_images:
                break

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def train_model(data_dir):
    try:
        faces = []
        labels = []
        label_map = {}

        # Iterate through each person's directory
        for idx, person_name in enumerate(os.listdir(data_dir)):
            person_path = os.path.join(data_dir, person_name)
            if not os.path.isdir(person_path):
                continue

            label_map[idx] = person_name

            # Read each image in the person's folder
            for image_name in os.listdir(person_path):
                image_path = os.path.join(person_path, image_name)
                image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if image is None:
                    continue

                faces.append(image)
                labels.append(idx)

        # If no faces or labels are found, return an error
        if not faces or not labels:
            print("Error: No valid data found for training.")
            return None, None

        # Train the recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(labels))

        # Save the trained model (optional)
        model_path = os.path.join(data_dir, "trained_model.yml")
        recognizer.write(model_path)

        return recognizer, label_map
    except Exception as e:
        print(f"Error in train_model: {e}")
        return None, None

