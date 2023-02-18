import cv2


class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(1,cv2.CAP_DSHOW)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()
