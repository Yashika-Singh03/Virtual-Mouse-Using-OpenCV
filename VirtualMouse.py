import cv2
import numpy as np
import time
import autopy
import HandTracking as ht
import tkinter as tk
from threading import Thread

# Webcam and smoothing settings
wCam, hCam = 640, 480
frameR = 100
smoothening = 7
plocX, plocY = 0, 0
clocX, clocY = 0, 0
cap = None
running = False

# Hand Detector
detector = ht.HandDetector(maxHands=1)
screen_width, screen_height = autopy.screen.size()

def start_mouse_control():
    global cap, running, plocX, plocY, clocX, clocY
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Camera not found or in use.")
            return

        cap.set(3, wCam)
        cap.set(4, hCam)

        pTime = 0
        running = True
        click_cooldown = 0  # Cooldown frames after a click

        while running:
            success, img = cap.read()
            if not success:
                print("Error: Failed to grab frame.")
                break

            img = detector.findHands(img)
            lmList, _ = detector.findPosition(img)

            if len(lmList) != 0:
                x1, y1 = lmList[8][1:]  # Index finger tip
                x2, y2 = lmList[12][1:]  # Middle finger tip

                fingers = detector.fingersUp()
                cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

                # Move Mode
                if fingers[1] == 1 and fingers[2] == 0:
                    x3 = np.interp(x1, (frameR, wCam - frameR), (0, screen_width))
                    y3 = np.interp(y1, (frameR, hCam - frameR), (0, screen_height))

                    clocX = plocX + (x3 - plocX) / smoothening
                    clocY = plocY + (y3 - plocY) / smoothening

                    autopy.mouse.move(screen_width - clocX, clocY)
                    cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                    plocX, plocY = clocX, clocY

                # Click Mode
                if fingers[1] == 1 and fingers[2] == 1:
                    length, _, coords = detector.findDistance(8, 12, img)
                    if length < 40 and click_cooldown == 0:
                        autopy.mouse.click()
                        click_cooldown = 10  # prevent multiple clicks

                        # Visual Click Animation
                        cx, cy = coords[4], coords[5]
                        cv2.circle(img, (cx, cy), 20, (0, 255, 0), cv2.FILLED)

            if click_cooldown > 0:
                click_cooldown -= 1

            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, f'FPS: {int(fps)}', (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

            cv2.imshow("Virtual Mouse", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error: {e}")
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()

def start_thread():
    thread = Thread(target=start_mouse_control)
    thread.start()

def stop_mouse_control():
    global running
    running = False

# GUI
root = tk.Tk()
root.title("Virtual Mouse Project")
root.geometry("600x350")
root.config(bg="#f0f0f0")

# Title Label
title_label = tk.Label(root, text="Virtual Mouse Using OpenCV", font=('Helvetica', 16, 'bold'), bg="#f0f0f0", fg="#4b0082")
title_label.pack(pady=20)

# College Name
college_label = tk.Label(root, text="College: Bundelkhand Institute of Engineering & Technology", font=('Helvetica', 12), bg="#f0f0f0", fg="#2e8b57")
college_label.pack(pady=5)

# Team Members
team_label = tk.Label(root, text="Team Members:\nYashika Singh (Team Leader) \n Bhaskar Yadav \n Anchal Maurya\n Shrawan Kumar \n Zaid Arif", font=('Helvetica', 12), bg="#f0f0f0", fg="#2e8b57")
team_label.pack(pady=10)

# Buttons
button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=15)

start_btn = tk.Button(button_frame, text="Start Virtual Mouse", command=start_thread, font=('Arial', 12), bg="green", fg="white", width=20)
start_btn.grid(row=0, column=0, padx=10)

stop_btn = tk.Button(button_frame, text="Exit", command=lambda: [stop_mouse_control(), root.destroy()], font=('Arial', 12), bg="red", fg="white", width=20)
stop_btn.grid(row=0, column=1, padx=10)

root.mainloop()
