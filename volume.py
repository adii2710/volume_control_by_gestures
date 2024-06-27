import time
import cv2
import numpy as np
import handtrackingmodule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import streamlit as st
from PIL import Image

# *******************webCam values************************
wCam, hCam = 640, 480 
#*********************************************************
pTime = 0
cTime = 0
increase_vol=Image.open("increase_vol.jpg")
decrease_vol=Image.open("decrease_vol.jpg")
st.sidebar.markdown("""
    # Instructions to use the app:
    Only can be used on computer system.
""")
st.sidebar.image(increase_vol, caption='Increase Volume')
st.sidebar.image(decrease_vol, caption='Decrease Volume')
st.title("Volume Control by Hand Gestures")
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector()

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()

min_vol = volRange[0]
max_vol = volRange[1]
volShow = 0
vol = 0
sysvol = 0
increaseVol = 0

frame_window = st.image([])

while True:
    success, img = cap.read()
    if not success:
        st.write("Failed to grab frame")
        break

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        x3, y3 = lmList[12][1], lmList[12][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cm, cn = (x1 + x3) // 2, (y1 + y3) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        length2 = math.hypot(x3 - x1, y3 - y1)
        cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)  
        cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (x3, y3), 10, (0, 255, 0), cv2.FILLED)
        
        volShow = volume.GetMasterVolumeLevel()
        if length < 40:
            cv2.circle(img, (cx, cy), 10, (240, 0, 0), cv2.FILLED)
            volShow = volume.GetMasterVolumeLevel()
            vol = np.interp(volShow, [min_vol, max_vol], [0, 100])
            increaseVol = vol + 1
            sysvol = np.interp(increaseVol , [0, 100], [min_vol, max_vol])
            volume.SetMasterVolumeLevel(sysvol, None)
        if length2 < 40 and not (volShow < -65):
            cv2.circle(img, (cm, cn), 10, (240, 0, 0), cv2.FILLED)
            volShow = volume.GetMasterVolumeLevel()
            vol = np.interp(volShow, [min_vol, max_vol], [0, 100])
            increaseVol = vol - 1
            sysvol = np.interp(increaseVol , [0, 100], [min_vol, max_vol])
            volume.SetMasterVolumeLevel(sysvol, None)
        if length > 250:
            cv2.circle(img, (cx, cy), 13, (0, 0, 255), cv2.FILLED)
    
    volShow = volume.GetMasterVolumeLevel()
    vol = np.interp(volShow, [min_vol, max_vol], [0, 100])
    cv2.putText(img, f"Volume:{int(vol)}%", (10, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (24, 45, 53), 3)
        
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    frame_window.image(imgRGB)
