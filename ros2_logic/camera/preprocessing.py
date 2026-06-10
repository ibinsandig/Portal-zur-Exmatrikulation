import cv2 as cv
from cv2 import aruco
import numpy as np
import sys
import os

# Add the parent directory (ros2_logic) to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))    #TODO Was zum Fick läuft hier falsch?

#import ros2_logic.config_vm
import config_vm



class ImagePreprocessor:
    def __init__(self):
        aruco_dict = aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_100)
        parameters = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(aruco_dict, parameters)

        self.H = None       # setup
        self.H_inv = None   # setup
        self.H_warp = None      # world to pixel
        self.H_inv_warp = None  # pixel to world

        self.pts2_proportional = None
        self.width = None
        self.height = None
        self.img_warped = None

    def setup(self, init_frame):
        corners = None

        corners, ids, rejected = self.detector.detectMarkers(init_frame) #TODO Fehler Vermeidung für zwei Marker

        if len(corners) < 2:
            print('Nicht genügend Marker gefunden')
            return 

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

        world_coords = cv.perspectiveTransform(pts1_reshaped, self.H_inv)

        offset_raw = np.array([
            [-6, +6],  # mm - X offset -6, Y offset -6
            [+6, +6],  # mm - X offset +6, Y offset -6
            [-6, -6],  # mm - X offset -6, Y offset +6
            [+6, -6]   # mm - X offset +6, Y offset +6
        ], dtype=np.float32)

        offset = offset_raw.reshape(-1, 1, 2)
        pts1_2 = world_coords + offset
        pts1_2_pixel = cv.perspectiveTransform(pts1_2, self.H)

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
        self.H_warp = cv.getPerspectiveTransform(pts1_2_pixel, pts2_proportional)
        self.H_inv_warp = np.linalg.inv(self.H_warp)

        print('Setup erfolgreich')
               

    def warp_image(self, frame):
        self.img_warped = cv.warpPerspective(frame, self.H_warp, (self.width, self.height))

        return self.img_warped
    
    def segment_object(self, frame):
        gray_image = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        ret, img_thresh = cv.threshold(gray_image, 150, 255, cv.THRESH_BINARY)
        uint8_img_thresh = img_thresh.astype(np.uint8)
        contours, hierarchy = cv.findContours(uint8_img_thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

        return contours

    def obj_position(self, contours):

        #TODO mehrere Objekte Ausgeben

        if not contours:
            return None
            print("Klasse: Keine Konturen gefunden")
        
        print(contours)

        largest_contour = max(contours, key=cv.contourArea)
        M = cv.moments(largest_contour)
        if M["m00"] == 0:
            return None
        
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        return (cX, cY)

    def pixel_to_world(self, pixel):
        if pixel is None:
            print("zero pixel")
            return None
        # Convert tuple to numpy array with proper shape for perspectiveTransform
        pixel_array = np.array([pixel], dtype=np.float32).reshape(-1, 1, 2)
        world = cv.perspectiveTransform(pixel_array, self.H_inv_warp)
        print(world[0, 0])
        return world[0, 0]  # Return as (x, y) tuple-like array

    def extract_features_from_contour(self, cnt):
        """Extract only hu_2 and hu_3 (log-scaled) for machine learning classification."""
        area = cv.contourArea(cnt)
        perimeter = cv.arcLength(cnt, True)
        
        if area == 0 or perimeter == 0:
            return None
        
        hu_raw = cv.HuMoments(cv.moments(cnt)).flatten()
        with np.errstate(divide="ignore"):
            hu_log = -np.sign(hu_raw) * np.log10(np.abs(hu_raw) + 1e-10)
        
        return {
            'hu_2': float(hu_log[2]),
            'hu_3': float(hu_log[3]),
        }
    
    def extract_orientation(self, cnt):
        rect = cv.minAreaRect(cnt)
            # rect = (center, (width, height), angle)
        angle = rect[2]
            
            # Normalisieren
        if rect[1][0] < rect[1][1]:  # width < height
            angle += 90
                
        return float(angle)