import cv2 as cv

def main():
    # Kamera öffnen (0 = Standardkamera)
    cap = cv.VideoCapture(0)

    cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)


    cv.namedWindow('Live Video', cv.WINDOW_NORMAL)
    cv.resizeWindow('Live Video', 1280 , 720)


    if not cap.isOpened():
        print("Fehler: Kamera konnte nicht geöffnet werden.")
        return

    print("Live-Anzeige läuft. Drücke 'q' zum Beenden.")

    while True:
        # Bildrahmen lesen
        ret, frame = cap.read()

        if not ret:
            print("Fehler: Konnte keinen Bildrahmen lesen.")
            break

        # Anzeige des Frames
        cv.imshow('Live Video', frame)

        # Auf Taste 'q' warten (27 ms Verzögerung)
        if cv.waitKey(27) & 0xFF == ord('q'):
            break

    # Ressourcen freigeben
    cap.release()
    cv.destroyAllWindows()

    print("Programm beendet.")

if __name__ == '__main__':
    main()

