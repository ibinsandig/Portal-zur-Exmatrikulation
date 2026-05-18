import cv2 as cv
from cv2 import aruco
import numpy as np

import config_vm

class ImagePreprocessor:
    def __init__(self):
        aruco_dict = aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_100)
        parameters = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(aruco_dict, parameters)

        self.H = None
        self.H_inv = None
        self.H_warp = None

        self.pts2_proportional = None
        self.width = None
        self.height = None
        self.img_warped = None

    def calibrate(self, init_frame):
        """
        Führt die Kamerakalibrierung anhand von Aruco-Markern durch.
        """
        corners, ids, rejected = self.detector.detectMarkers(init_frame)
        
        if not corners or len(corners) < 4:
            # Nicht genug Marker gefunden
            return False

        dstPoints = np.concatenate(corners, axis=1)
        self.H, _ = cv.findHomography(srcPoints=config_vm.SRC_COORDS, dstPoints=dstPoints, method=0)
        self.H_inv = np.linalg.inv(self.H)

        pts1 = np.float32([
            corners[1][0][0],  # oben-links
            corners[1][0][1],  # oben-rechts
            corners[0][0][3],  # unten-links
            corners[0][0][2],  # unten-rechts
        ])

        pts1_reshaped = pts1.astype(np.float32).reshape(-1, 1, 2)

        world_frame = cv.perspectiveTransform(pts1_reshaped, self.H_inv)

        offset_raw = np.array([
            [-6, +6],  # mm - X offset -6, Y offset -6
            [+6, +6],  # mm - X offset +6, Y offset -6
            [-6, -6],  # mm - X offset -6, Y offset +6
            [+6, -6]   # mm - X offset +6, Y offset +6
        ], dtype=np.float32)

        offset = offset_raw.reshape(-1, 1, 2)
        pts1_2 = world_frame + offset
        pts1_2_pixel = cv.perspectiveTransform(pts1_2, self.H)

        min_x = np.min(pts1_2_pixel[:, 0, 0])
        max_x = np.max(pts1_2_pixel[:, 0, 0])
        min_y = np.min(pts1_2_pixel[:, 0, 1])
        max_y = np.max(pts1_2_pixel[:, 0, 1])

        self.width = int(max_x - min_x)
        self.height = int(max_y - min_y)

        self.pts2_proportional = np.float32([
            [0, 0],
            [self.width, 0],
            [0, self.height],
            [self.width, self.height]
        ])
        self.H_warp = cv.getPerspectiveTransform(pts1_2_pixel, self.pts2_proportional)
        
        return True

    def warp_image(self, frame):
        """
        Wendet die vorberechnete Perspektiventransformation an.
        """
        if self.H_warp is None:
            return None
            
        self.img_warped = cv.warpPerspective(frame, self.H_warp, (self.width, self.height))
        return self.img_warped

    def segment_objects(self, frame):
        """
        Sucht nach Objekten im entzerrten (warped) Bild und gibt eine Liste 
        mit deren Features sowie den zugehörigen Bildausschnitten (ROIs) zurück.
        """
        if frame is None:
            return []

        gray_image = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        
        # 70 als Schwellenwert aus dem Test-Notebook übernommen
        ret, img_thresh = cv.threshold(gray_image, 70, 255, cv.THRESH_BINARY)
        uint8_img_thresh = img_thresh.astype(np.uint8)

        contours, hierarchy = cv.findContours(uint8_img_thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        
        detected_objects = []

        for cnt in contours:
            area = cv.contourArea(cnt)
            if area < 50:  # Rauschen herausfiltern
                continue
                
            features = self.extract_features_from_contour(cnt)
            if features is None:
                continue
            
            # Bildausschnitt (Region of Interest) ausschneiden
            x, y, w, h = cv.boundingRect(cnt)
            roi = frame[y:y+h, x:x+w]
            features['roi'] = roi
            
            # Mittelpunkt im Warp-Bild
            M = cv.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
            
            features['cx'] = cX
            features['cy'] = cY
            
            detected_objects.append(features)

        return detected_objects

    def extract_features_from_contour(self, cnt):
        """
        Extrahiert die relevanten geometrischen Features für das Machine Learning 
        aus einer einzelnen Kontur.
        """
        features = {}
        
        # 1. Basis-Werte
        features['area'] = cv.contourArea(cnt)
        features['perimeter'] = cv.arcLength(cnt, True)
        
        # Schutz vor Division durch Null
        if features['area'] == 0 or features['perimeter'] == 0:
            return None 
            
        # 2. Polygon & Ecken
        epsilon = 0.04 * features['perimeter']
        approx = cv.approxPolyDP(cnt, epsilon, True)
        features['corners'] = len(approx)
        
        # 3. Bounding Box & Seitenverhältnis
        x, y, w, h = cv.boundingRect(cnt)
        features['aspect_ratio'] = float(w) / h
        
        # 4. Circularity
        features['circularity'] = (4 * np.pi * features['area']) / (features['perimeter'] ** 2)
        
        # 5. Hu-Momente
        M = cv.moments(cnt)
        hu = cv.HuMoments(M).flatten()
        for i in range(7):
            features[f'hu_{i}'] = hu[i]
            
        return features

    def pixel_to_world(self, pixel_x, pixel_y):
        """
        Transformiert einen Pixelpunkt aus dem entzerrten (warped) Bild 
        zurück in reale Weltkoordinaten (Roboter-Koordinaten).
        """
        if self.H_warp is None or self.H_inv is None:
            return None
            
        # 1. Vom Warp-Bild zurück zum verzerrten Originalbild
        _, H_warp_inv = cv.invert(self.H_warp)
        pt_warp = np.float32([[[pixel_x, pixel_y]]])
        pt_cam = cv.perspectiveTransform(pt_warp, H_warp_inv)
        
        # 2. Vom Originalbild in die physikalischen Weltkoordinaten
        pt_world = cv.perspectiveTransform(pt_cam, self.H_inv)
        
        return pt_world[0][0][0], pt_world[0][0][1]
