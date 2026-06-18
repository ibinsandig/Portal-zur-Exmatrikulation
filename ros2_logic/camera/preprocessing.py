import cv2 as cv
from cv2 import aruco
import numpy as np
import sys
import os

# Add the parent directory (ros2_logic) to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))    #TODO import korrigieren

#import ros2_logic.config_vm
import config_vm



class ImagePreprocessor:
    def __init__(self):
        aruco_dict = aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_100)
        parameters = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(aruco_dict, parameters)

        self.H_pre = None       # setup
        self.H_pre_inv = None   # setup
        self.M_all = None      # world to pixel
        self.M_all_inv = None  # pixel to world

        self.pts2_proportional = None
        self.width = None
        self.height = None
        self.img_warped = None

    def setup(self, init_frame):
        corners = None

        corners, ids, rejected = self.detector.detectMarkers(init_frame)

        if len(corners) < 2:
            print('Nicht genügend Marker gefunden')
            return 

        dstPoints = np.concatenate(corners, axis=1)
        H_pre, _ = cv.findHomography(srcPoints=config_vm.SRC_COORDS, dstPoints=dstPoints, method=0)
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
            [-6, +6],  # mm - X offset -6, Y offset -6
            [+6, +6],  # mm - X offset +6, Y offset -6
            [-6, -6],  # mm - X offset -6, Y offset +6
            [+6, -6]   # mm - X offset +6, Y offset +6
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

        corners, ids, rejected = self.detector.detectMarkers(aruco_warped)

        if len(corners) < 2:
            print('Nicht genügend Marker gefunden im warped Bild')
            return 

        dstPoints = np.concatenate(corners, axis=1)
        self.H, _ = cv.findHomography(srcPoints= config_vm.SRC_COORDS, dstPoints=dstPoints, method=0)
        self.H_inv = np.linalg.inv(self.H)

        print('Setup erfolgreich')
               
    def warp_image(self, frame):
        self.img_warped = cv.warpPerspective(frame, self.M_all, (self.width, self.height))

        return self.img_warped
    
    def segment_object(self, frame):

        ret, img_thresh = cv.threshold(frame, 150, 255, cv.THRESH_BINARY)
        uint8_img_thresh = img_thresh.astype(np.uint8)
        contours, hierarchy = cv.findContours(uint8_img_thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

        return contours

    def obj_position(self, contours):

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
            print("no pixel")
            return None

        pixel_array = np.array([pixel], dtype=np.float32).reshape(-1, 1, 2)
        world = cv.perspectiveTransform(pixel_array, self.M_all_inv)
        print(world[0, 0])
        return world[0, 0]

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
            'hu_2': hu_log[2],
            'hu_3': hu_log[3],
        }
    
    def extract_orientation(self, cnt):
        rect = cv.minAreaRect(cnt)
            # rect = (center, (width, height), angle)
        angle = rect[2]
            
        if rect[1][0] < rect[1][1]:  # width < height
            angle += 90
                
        return float(angle)