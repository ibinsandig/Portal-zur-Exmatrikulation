import cv2 as cv
import time

cam = cv.VideoCapture(4)
cam.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
cam.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

if not cam.isOpened():
    print('Fehler: Kamera konnte nicht geöffnet werden.')
    exit(1)

# --- NEU: Fenster konfigurieren ---
cv.namedWindow('Livebild', cv.WINDOW_NORMAL) # Fenster skalierbar machen
cv.resizeWindow('Livebild', 960, 540)        # Fenster auf handliche Größe setzen
# ----------------------------------

time.sleep(1)

while True:
    ret, frame = cam.read()
    if ret:
        cv.imshow('Livebild', frame) # Nutzt das oben definierte Fenster
        
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print('Fehler beim Bildempfang.')
        break

cam.release()
cv.destroyAllWindows()


