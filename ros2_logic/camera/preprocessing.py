import cv2 as cv
from cv2 import aruco
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config_vm as cfg

class ImagePreprocessor:
    """Bildvorverarbeitung: Führt Kamerakalibrierung via ArUco-Marker durch und stellt Methoden zur Bildentzerrung, Segmentierung und Feature-Extraktion bereit."""

    def __init__(self):
        """Initialisiert ArUco-Detektor (DICT_4X4_100) und interne Homographie-Matrizen."""
        aruco_dict = aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_100)
        parameters = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(aruco_dict, parameters)

        self.H_pre = None       # setup
        self.H_pre_inv = None   # setup
        self.M_all = None      # world to pixel
        self.M_all_inv = None  # pixel to world
        self.H_inv = None
        self.H = None
        self.pts2_proportional = None
        self.width = None
        self.height = None
        self.img_warped = None

    def setup(self, init_frame):
        """Berechnet Homographie-Matrizen anhand von ArUco-Markern im Initialisierungsbild. Setzt H_inv bei Erfolg.

        Args:
            init_frame (numpy.ndarray): Grayscale-Bild mit mindestens 2 sichtbaren ArUco-Markern
        """

        corners = None

        corners, ids, rejected = self.detector.detectMarkers(init_frame)

        if len(corners) < 2:
            print('Nicht genügend Marker gefunden 1. Homography')
            cv.imwrite('first_image.png', init_frame)
            return 

        dstPoints = np.concatenate(corners, axis=1)
        print(dstPoints)
        H_pre, _ = cv.findHomography(srcPoints=cfg.SRC_COORDS_2, dstPoints=dstPoints, method=0)
        H_pre_inv = np.linalg.inv(H_pre)

        pts1 = np.float32([
            corners[1][0][0],  # oben-links
            corners[1][0][1],  # oben-rechts
            corners[0][0][3],  # unten-links
            corners[0][0][2],  # unten-rechts
        ])  

        pts1_reshaped = pts1.astype(np.float32).reshape(-1, 1, 2)

        world_coords = cv.perspectiveTransform(pts1_reshaped, H_pre_inv)

        offset_raw = np.array([
            [-0.006, +0.006],  # mm - X offset -6, Y offset -6
            [-0.006, -0.006],  # mm - X offset +6, Y offset -6
            [+0.006, +0.006],  # mm - X offset -6, Y offset +6
            [+0.006, -0.006] 
        ], dtype=np.float32)

        offset = offset_raw.reshape(-1, 1, 2)
        pts1_2 = world_coords + offset
        pts1_2_pixel = cv.perspectiveTransform(pts1_2, H_pre)

        print('Offset ausgerechnet')

        min_x = np.min(pts1_2_pixel[:, 0, 0])
        max_x = np.max(pts1_2_pixel[:, 0, 0])
        min_y = np.min(pts1_2_pixel[:, 0, 1])
        max_y = np.max(pts1_2_pixel[:, 0, 1])

        self.width = int(max_x - min_x)
        self.height = int(max_y - min_y)

        pts2_proportional = np.float32([
            [0, 0],
            [self.width, 0],
            [0, self.height],
            [self.width, self.height]
        ])
        self.M_all = cv.getPerspectiveTransform(pts1_2_pixel, pts2_proportional)
        self.M_all_inv = np.linalg.inv(self.M_all)

        aruco_warped = cv.warpPerspective(init_frame, self.M_all, (self.width, self.height))

        cv.imwrite('debug_warped_image.png', aruco_warped)
        print("DEBUG: Das verzerrte Bild wurde als 'debug_warped_image.png' gespeichert.")

        corners_2, ids, rejected = self.detector.detectMarkers(aruco_warped)


        if len(corners_2) < 2:
            return

        sorted_pairs = sorted(zip(ids.flatten(), corners_2), key=lambda x: x[0], reverse=True)
        sorted_corners = [pair[1] for pair in sorted_pairs]

        dstPoints = np.concatenate(sorted_corners, axis=1)

        self.H, _ = cv.findHomography(
            srcPoints=cfg.SRC_COORDS_2,
            dstPoints=dstPoints,
            method=0
        )

        print(len(corners_2))

        if len(corners_2) < 2:
            print('Nicht genügend Marker gefunden im warped Bild')
            return 
        print("Berechnen der Homographie")

        dstPoints = np.concatenate(corners_2, axis=1)
        self.H, _ = cv.findHomography(srcPoints= cfg.SRC_COORDS_2, dstPoints=dstPoints, method=0)
        self.H_inv = np.linalg.inv(self.H)

        #test_pixel = np.float32([[[corners_2[0][0][0][0], corners_2[0][0][0][1]]]])
        #test_world = cv.perspectiveTransform(test_pixel, self.H_inv)

        #print(f"(in)Sanity check: Pixel --> Welt {test_pixel} → Welt {test_world}")  #Ergebnis sollte annähernd an SRC_COORDS_2 sein

        # Vergleich aller 8 Punkte, nicht nur des ersten
        for i, corner_set in enumerate(sorted_corners):
            for j, corner in enumerate(corner_set[0]):
                px = np.float32([[[corner[0], corner[1]]]])
                world = cv.perspectiveTransform(px, self.H)
                expected = cfg.SRC_COORDS_2[0][i*4 + j]
                print(f"Ecke {i},{j}: Pixel {corner} → Welt {world[0,0]} | Erwartet {expected}")

        print('Setup erfolgreich')
               
    def warp_image(self, frame):
        """Entzerrt einen Frame mit der berechneten Perspektivtransformation M_all.

        Args:
            frame (numpy.ndarray): Grayscale-Rohbild

        Returns:
            numpy.ndarray: Entzerrtes Bild in Weltgröße (self.width x self.height)
        """

        self.img_warped = cv.warpPerspective(frame, self.M_all, (self.width, self.height))

        return self.img_warped
    
    def segment_object(self, frame):
        """Schwellenwertbasierte Segmentierung zur Konturfindung heller Objekte (Threshold > 210).

        Args:
            frame (numpy.ndarray): Entzerrtes Grayscale-Bild

        Returns:
            tuple: Konturliste (OpenCV-Format)
        """

        ret, img_thresh = cv.threshold(frame, 210, 255, cv.THRESH_BINARY)
        uint8_img_thresh = img_thresh.astype(np.uint8)
        contours, hierarchy = cv.findContours(uint8_img_thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

        return contours

    def get_grippoint(self, contours, image_shape):
        """Berechnet den optimalen Greifpunkt der größten Kontur.

        Args:
            contours (list): Liste von OpenCV-Konturen
            image_shape (tuple): Shape des Quellbilds (h, w, ...)

        Returns:
            tuple: (x, y) Pixelkoordinate des Greifpunkts oder None bei leerer Konturliste
        """

        if not contours:
            return None
        largest = max(contours, key=cv.contourArea)

        mask = np.zeros(image_shape[:2], dtype=np.uint8)
        cv.drawContours(mask, [largest], -1, 255, thickness=cv.FILLED)

        dist = cv.distanceTransform(mask, cv.DIST_L2, 5)

        _, _, _, max_loc = cv.minMaxLoc(dist)
        return max_loc  # x, y 

    def pixel_to_world(self, pixel):
        """Transformiert eine Pixelkoordinate via inverser Homographie in Weltkoordinaten.

        Args:
            pixel (tuple): (x, y) Pixelkoordinate

        Returns:
            numpy.ndarray: Weltkoordinate [x, y] in Metern oder None bei ungültigem Eingabewert
        """

        # print(f"Pixel rein: {pixel}")  

        if pixel is None:
            print("no pixel")
            return None

        pixel_array = np.array([pixel], dtype=np.float32).reshape(-1, 1, 2)
        world = cv.perspectiveTransform(pixel_array, self.H_inv)
        print(f"Pixel rein: {pixel}")
        print(f"Welt raus: {world[0, 0]}")
        return world[0, 0]

    def extract_features_from_contour(self, cnt):
        """Extrahiert logarithmierte Hu-Momente (hu_2, hu_3) aus einer Kontur.

        Args:
            cnt (numpy.ndarray): OpenCV-Kontur

        Returns:
            dict: {'hu_2': float, 'hu_3': float} oder None bei Fläche/Umfang == 0
        """

        area = cv.contourArea(cnt)
        perimeter = cv.arcLength(cnt, True)
        
        if area == 0 or perimeter == 0:
            return None 
        
        hu_raw = cv.HuMoments(cv.moments(cnt)).flatten()
        with np.errstate(divide="ignore"):
            hu_log = -np.sign(hu_raw) * np.log10(np.abs(hu_raw) + 1e-10)
        
        return {
            'hu_2': hu_log[2],
            'hu_3': hu_log[3],
        }