import cv2

class Camera:
    _instance = None
    cap = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Camera, cls).__new__(cls)
        return cls._instance

    def open_camera(self):
        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
        return self.cap

    def release_camera(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            cv2.destroyAllWindows()
