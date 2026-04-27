import cv2 as cv
import os
from datetime import datetime


def main():
    # Kamera öffnen (0 = Standardkamera)
    cap = cv.VideoCapture(0)

    cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

    if not cap.isOpened():
        print("Fehler: Kamera konnte nicht geöffnet werden.")
        return

    # Aufnahme-Verzeichnis erstellen
    save_dir = "captured_images"
    os.makedirs(save_dir, exist_ok=True)

    print("Live-Anzeige läuft.")
    print("Drücke 's' zum Aufnehmen eines Bildes.")
    print("Drücke 'q' zum Beenden.")

    frame_count = 0

    while True:
        # Bildrahmen lesen
        ret, frame = cap.read()

        if not ret:
            print("Fehler: Konnte keinen Bildrahmen lesen.")
            break

        # Anzeige des Frames
        cv.imshow('Kamera', frame)

        # Auf Taste warten (27 ms Verzögerung)
        key = cv.waitKey(27) & 0xFF

        if key == ord('s'):
            # Bild speichern
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            frame_count += 1
            filename = f"{save_dir}/image_{timestamp}_{frame_count:03d}.jpg"
            cv.imwrite(filename, frame)
            print(f"Bild gespeichert: {filename}")

        elif key == ord('q'):
            break

    # Ressourcen freigeben
    cap.release()
    cv.destroyAllWindows()

    print("Programm beendet.")


if __name__ == '__main__':
    main()

