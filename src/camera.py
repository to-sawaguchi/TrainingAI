import cv2
import mediapipe as mp
import numpy as np
import time 

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(1)
        self.counter = 0 
        self.stage = None
        self.timer = None  
        self.pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.prev_time = time.time()
        self.FRAME_RATE = 10  # フレームレートを定義
        self.final_count = None  # 追加する行

    def __del__(self):
        self.video.release()

    def calculate_angle(self, a, b, c):
        a = np.array(a) 
        b = np.array(b) 
        c = np.array(c) 
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        if angle > 180.0:
            angle = 360 - angle
        return angle
    
    def get_arm_curl_count(self): 
        if self.final_count is not None:
            return self.final_count
        else:
            return self.counter

    def get_timer(self):  
        if self.timer is not None:
            return time.time() - self.timer
        else:
            return 0

    def get_frame(self):
        while True:
            success, image = self.video.read()
            elapsed_time = time.time() - self.prev_time
            if elapsed_time > 1./self.FRAME_RATE:
                self.prev_time = time.time()
                break
                
        if image is not None:  # 画像が空でないことをチェック
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
 
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        try:
            landmarks = results.pose_landmarks.landmark
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            angle = self.calculate_angle(shoulder, elbow, wrist)
            if angle > 160:
                self.stage = "down"
            if angle < 30 and self.stage =='down':
                self.stage = "up"
                self.counter += 1
                self.timer = time.time()  
        except:
            pass

        if self.timer is not None and time.time() - self.timer > 6:
            self.final_count = self.counter
            self.counter = 0
            self.timer = None

        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))

        cv2.putText(image, 'REPS: '+str(self.counter), 
                    (10,60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(image, 'STAGE: '+str(self.stage), 
                    (10,120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

