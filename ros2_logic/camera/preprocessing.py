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
        self.pts2_proportional = None
        self.width = None
        self.height = None
        self.img_warped = None

    def calibrate(self, init_frame):
        corners = self.detect_aruco(init_frame)
        dstPoints = np.concatenate(corners, axis=1)
        self.H, _ = cv.findHomography(srcPoints=config_vm.SRC_COORDS, dstPoints=dstPoints, method=0)

        self.H, status = cv.findHomography(srcPoints=config_vm.SRC_COORDS, dstPoints=dstPoints, method=0)
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

        self.calculate_proportion(pts1_2_pixel)

        H_warp = cv.getPerspectiveTransform(pts1_2_pixel, self.pts2_proportional)
        self.img_warped = cv.warpPerspective(init_frame, H_warp, (self.width, self.height))

    def warp_image(self, frame):
        H_warp = cv.getPerspectiveTransform(pts1_2_pixel, self.pts2_proportional)
        self.img_warped = cv.warpPerspective(init_frame, H_warp, (self.width, self.height))


    def calculate_proportion(self, pixel):
        min_x = np.min(pixel[:, 0, 0])
        max_x = np.max(pixel[:, 0, 0])
        min_y = np.min(pixel[:, 0, 1])
        max_y = np.max(pixel[:, 0, 1])

        self.width = int(max_x - min_x)
        self.height = int(max_y - min_y)

        self.pts2_proportional = np.float32([
            [0, 0],
            [self.width, 0],
            [0, self.height],
            [self.width, self.height]
        ])


    def detect_aruco(self, frame):
        corners, ids, rejected = self.detector.detectMarkers(frame)
        return corners

    def pixel_to_world(self, pixel):
        
        world = cv.perspectiveTransform(self.H_inv, pixel)
        
        return world
    
    def world_to_pixel(self, world):

        pixel_coords = cv.perspectiveTransform(self.H, world)

        return pixel_coords



    def segment_object(self, frame):
        pass
