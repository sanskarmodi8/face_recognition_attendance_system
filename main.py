import tkinter as tk
import cv2
import os
from PIL import Image, ImageTk
import subprocess
import util
import mediapipe as mp

class App:
    
    def __init__(self):
        
        self.face_detector = mp.solutions.face_detection.FaceDetection() # create face detector
        
        self.main_window = tk.Tk() # create main window
        self.main_window.title('Attendance System')
        self.main_window.geometry('1200x520+350+100') # set size to 1200x520 and position to (350, 100)
        
        self.login_btn_main_window = util.get_button(self.main_window, 'Login', 'green', self.login) # create login button
        self.login_btn_main_window.place(x=750, y=300) # place login button
        
        self.register_btn_main_window = util.get_button(self.main_window, 'Register new user', 'gray', self.register, fg='black') # create login button
        self.register_btn_main_window.place(x=750, y=400) # place register button
        
        self.webcam_label = util.get_img_label(self.main_window) # create webcam label
        self.webcam_label.place(x=10, y=0, width=700, height=500) # place webcam label
        
        self.add_webcam(self.webcam_label) # add webcam to webcam label
        
        self.db_dir = os.path.join(os.getcwd(), 'images', 'known_imgs') # create db directory
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)
        
    def add_webcam(self, label):
        
        if 'cap' not in self.__dict__: # if webcam is not added yet then add it
            self.cap = cv2.VideoCapture(0)
            
        self._label = label # set internal label to the label passed as argument
        self.process_webcam() # start processing webcam
        
    def process_webcam(self):
        
        _ , frame = self.cap.read() # read frame from webcam
        self.most_recent_capture_arr = frame # save most recent frame
        self.most_recent_capture_arr=self.add_detections(self.most_recent_capture_arr) # add detections to most recent frame
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # convert frame to RGB
        self.most_recent_capture_pil = Image.fromarray(img) # convert frame to PIL image format # pillow is used to convert numpy array to image
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil) # convert PIL image to tkinter image
        self._label.imgtk = imgtk # save tkinter image to internal label
        self._label.configure(image=imgtk) # set internal label to tkinter image
        self._label.after(20, self.process_webcam) # recurse after 20 ms
    
        
    def add_detections(self, frame):
        # Convert the frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces in the frame
        face_results = self.face_detector.process(frame_rgb)

        # Check if any faces are detected
        if face_results.detections:
            for detection in face_results.detections:
                # Get the bounding box coordinates
                bbox = detection.location_data.relative_bounding_box
                h, w, c = frame.shape
                self.xmin = int(bbox.xmin * w - 0.1*bbox.width*w) # 0.1 is subtracted to increase the width of the bounding box from left
                self.ymin = int(bbox.ymin * h - 0.3*bbox.height*h) # 0.3 is subtracted to increase the height of the bounding box from top
                self.xmax = int((bbox.xmin + bbox.width ) * w + 0.1*bbox.width*w) # 0.1 is added to increase the width of the bounding box from right
                self.ymax = int((bbox.ymin + bbox.height) * h)
                
                # Get the confidence value
                self.confidence = detection.score

                if self.confidence[0] > 0.8:

                    if self.check_liveliness():
                        # Draw the bounding box on the frame
                        cv2.rectangle(frame, (self.xmin, self.ymin), (self.xmax, self.ymax), (0, 255, 0), 2)
                        
                    else:
                        # Draw the bounding box on the frame
                        cv2.rectangle(frame, (self.xmin, self.ymin), (self.xmax, self.ymax), (0, 0, 255), 2)
                        # Display spoof 
                        cv2.putText(img=frame, text=f"Spoof!", org=(self.xmin, self.ymin-10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.0, color=(0, 0, 255), thickness=2)
                    
        return frame
                            
            
    def start(self):
        
        self.main_window.mainloop() # start main loop
        
    def login(self):

        unknown_img_path = './.tmp.jpg'
        cv2.imwrite(unknown_img_path, self.most_recent_capture_arr)

        # Facial recognition output
        output = str(subprocess.check_output(['face_recognition', self.db_dir, unknown_img_path]))

        output = output.split(',')[1].split('\\')[0]

        os.remove(unknown_img_path)

        if output in ['no_persons_found']:
            util.msg_box('Error', 'No person found')

        elif output in ['unknown_person']:
            util.msg_box('Stranger', 'Unknown person')
        else:
            
            # Check liveliness using facial landmarks
            liveliness_result = self.check_liveliness()

            if liveliness_result:
                util.msg_box('Attendance Marked', 'Welcome ' + output)
                file_path = 'attendance.txt'
                with open(file_path, 'a') as file:
                    file.write(output + '\n')
                    file.close()
            else:
                util.msg_box('Spoofing Detected', 'You are a fake. Spoofing')

    def check_liveliness(self):
        
        return True

                
    def register(self):
        
        self.register_window = tk.Toplevel(self.main_window) # create register window
        self.register_window.geometry('1200x520+370+120')
        
        self.register_user_name_label = util.get_text_label(self.register_window, 'Enter your name:') # create text label
        self.register_user_name_label.place(x=750, y=70) # place text label
        
        self.register_user_name = util.get_entry_text(self.register_window) # create entry text
        self.register_user_name.place(x=750, y=150) # place entry text
        
        self.accept_btn_register_window = util.get_button(self.register_window, 'Accept', 'green', self.register_user) # create accept button
        self.accept_btn_register_window.place(x=750, y=300) # place accept button
        
        self.tryagain_btn_register_window = util.get_button(self.register_window, 'Try Again', 'red', self.register_user_tryagain) # create tryagain button
        self.tryagain_btn_register_window.place(x=750, y=400) # place tryagain button
        
        self.capture_label = util.get_img_label(self.register_window) # create capture label
        self.capture_label.place(x=10, y=0, width=700, height=500) # place capture label
        
        self.add_img_to_label(self.capture_label) # add captured image to capture label
        
    def register_user(self):
        
        name = self.register_user_name.get('1.0', 'end-1c') # get name from entry text # 1.0 means from line 1 character 0 and end-1c means till end minus 1 character
        cv2.imwrite(os.path.join(self.db_dir, name + '.jpg'), self.register_user_capture) # save captured image to db directory
        
        util.msg_box('Success', 'User registered successfully') # show success message
        self.register_window.destroy() # destroy register window
    
    def register_user_tryagain(self):
        
        self.register_window.destroy() # destroy register window
    
    def add_img_to_label(self, label):
        
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil) # convert PIL image to tkinter image
        label.imgtk = imgtk # save tkinter image to internal label
        label.configure(image=imgtk) # set internal label to tkinter image
        
        self.register_user_capture = self.most_recent_capture_arr.copy() # save captured image
    
if __name__ == '__main__':
    
    app = App()
    app.start()
    