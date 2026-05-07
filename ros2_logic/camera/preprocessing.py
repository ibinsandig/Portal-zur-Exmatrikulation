import cv2 as cv
from cv2 import aruco
import numpy as np

import config_vm

class ImagePreprocessor:
    def __init__(self):
        aruco_dict = aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_100)
        parameters = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(aruco_dict, parameters)
        
    def calibrate(self, init_frame):
        corners, ids, rejected = self.detector.detectMarkers(init_frame)
        dstPoints = np.concatenate(corners, axis=1)

        self.H, status = cv.findHomography(srcPoints=config_vm.SRC_COORDS, dstPoints=dstPoints, method=0)
        self.H_inv = np.linalg.inv(self.H)

    def pixel_to_world(self, pixel):
        
        world = cv.perspectiveTransform(self.H_inv, pixel)
        
        return world

    def crop_image(self, frame):
        pass

    def segment_object(self, frame):
        pass

    def focus_center(self, frame):
        pass 

    def object_orientation(self, frame):
        pass

    def object_data(self, frame):
        pass