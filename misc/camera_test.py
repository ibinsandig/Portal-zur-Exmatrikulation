import cv2 as cv
import time

cam = cv.VideoCapture(1q)
if not cam.isOpened():
    print('Fehler: Kamera konnte nicht geöffnet werden.')
    exit(1)

# Kurz warten, damit die Kamera bereit ist
time.sleep(1)

while True:
    ret, frame = cam.read()
    if ret:
        cv.imshow('Livebild', frame)
        # 'q' drücken zum Beenden
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print('Fehler beim Bildempfang.')
        break

cam.release()
cv.destroyAllWindows()