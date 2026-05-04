Input: Bild

Output: 
    - Objekt Type
    - prädizierte Koordinaten(x, y)


# Tasks:
    - Bild aufnehmen

# Förderbandebene erstellen

        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)  # oder z.B. DICT_4X4_50
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict)

        corners, ids, rejected = detector.detectMarkers(image)

        H, status = cv2.findHomography(pts_img, pts_world)

        pixel = np.array([[[800.0, 560.0]]], dtype=np.float32)

        world = cv2.perspectiveTransform(pixel, H)

        X, Y = world[0,0,0], world[0,0,1]

    - Bild in Graufarben konvertieren
    - Segmentierungssteps durchführen
    - Wichtige Attribute extrahieren fürs ml
    - 