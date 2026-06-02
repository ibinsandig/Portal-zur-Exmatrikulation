import cv2

cap = cv2.VideoCapture(4)
counter = 0

# Fenster skalierbar machen
cv2.namedWindow("Kamera", cv2.WINDOW_NORMAL)

# Fenstergröße anpassen, z.B. 1280x720
cv2.resizeWindow("Kamera", 1280, 720)

# Optional: Kamerauflösung setzen
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

print("Leertaste = Foto | Q = Beenden")                
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Bild auf Fenstergröße skalieren
    frame = cv2.resize(frame, (1280, 720))

    cv2.imshow("Kamera", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord(' '):
        filename = f"foto_{counter}.png"
        cv2.imwrite(filename, frame)
        print(f"Gespeichert: {filename}")
        counter += 1
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()