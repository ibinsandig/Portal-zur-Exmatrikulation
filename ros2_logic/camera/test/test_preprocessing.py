import pytest
import sys
import os
import cv2 as cv
import numpy as np

# Add the parent directory (camera) and the package directory (ros2_logic) to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from preprocessing import ImagePreprocessor

# Path to the testmode images directory
TESTMODE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'testmode'))


class TestImagePreprocessor:
    """Test cases for the ImagePreprocessor class."""

    def setup_method(self):
        """Setup a fresh ImagePreprocessor instance before each test."""
        self.preprocessor = ImagePreprocessor()

    def test_init_state(self):
        """Verify the initial state of the preprocessor."""
        assert self.preprocessor.detector is not None
        assert self.preprocessor.H_pre is None
        assert self.preprocessor.H_pre_inv is None
        assert self.preprocessor.M_all is None
        assert self.preprocessor.M_all_inv is None
        assert self.preprocessor.width is None
        assert self.preprocessor.height is None
        assert self.preprocessor.img_warped is None

    def test_setup_failure_no_markers(self):
        """Setup should fail and output None when there are no ArUco markers in the image."""
        # Create a black image
        blank_image = np.zeros((100, 100, 3), dtype=np.uint8)
        self.preprocessor.setup(blank_image)
        
        assert self.preprocessor.H_pre is None
        assert self.preprocessor.M_all is None

    def test_setup_success(self):
        """Setup should successfully compute homography matrices with the reference ArUco image."""
        aruco_img = cv.imread(os.path.join(TESTMODE_DIR, 'aruco.png'))
        assert aruco_img is not None, "Could not load test image aruco.png"
        
        self.preprocessor.setup(aruco_img)
        
        assert self.preprocessor.H_pre is not None
        assert self.preprocessor.H_pre_inv is not None
        assert self.preprocessor.M_all is not None
        assert self.preprocessor.M_all_inv is not None
        assert isinstance(self.preprocessor.width, int)
        assert isinstance(self.preprocessor.height, int)
        assert self.preprocessor.width > 0
        assert self.preprocessor.height > 0

    def test_warp_image(self):
        """Warping an image should return a warped frame matching the configured width and height."""
        aruco_img = cv.imread(os.path.join(TESTMODE_DIR, 'aruco.png'))
        self.preprocessor.setup(aruco_img)
        
        cat_img = cv.imread(os.path.join(TESTMODE_DIR, 'cat_0.png'))
        assert cat_img is not None, "Could not load test image cat_0.png"
        
        warped = self.preprocessor.warp_image(cat_img)
        assert warped is not None
        assert warped.shape[1] == self.preprocessor.width
        assert warped.shape[0] == self.preprocessor.height
        assert warped.shape[2] == 3

    def test_segment_object(self):
        """Segmentation should return external contours of foreground objects."""
        aruco_img = cv.imread(os.path.join(TESTMODE_DIR, 'aruco.png'))
        self.preprocessor.setup(aruco_img)
        
        cat_img = cv.imread(os.path.join(TESTMODE_DIR, 'cat_0.png'))
        warped = self.preprocessor.warp_image(cat_img)
        
        contours = self.preprocessor.segment_object(warped)
        assert isinstance(contours, tuple) or isinstance(contours, list)
        assert len(contours) > 0
        assert isinstance(contours[0], np.ndarray)

    def test_obj_position(self):
        """Object position should return the centroid of the largest contour, or None for empty input."""
        # Empty contours test
        assert self.preprocessor.obj_position([]) is None
        
        # Real image test
        aruco_img = cv.imread(os.path.join(TESTMODE_DIR, 'aruco.png'))
        self.preprocessor.setup(aruco_img)
        
        cat_img = cv.imread(os.path.join(TESTMODE_DIR, 'cat_0.png'))
        warped = self.preprocessor.warp_image(cat_img)
        contours = self.preprocessor.segment_object(warped)
        
        pos = self.preprocessor.obj_position(contours)
        assert pos is not None
        assert len(pos) == 2
        assert isinstance(pos[0], int)
        assert isinstance(pos[1], int)
        # Position should be within image boundaries
        assert 0 <= pos[0] < self.preprocessor.width
        assert 0 <= pos[1] < self.preprocessor.height

    def test_pixel_to_world(self):
        """pixel_to_world should transform pixel coordinates to world coordinates using H_inv_warp."""
        # None argument test
        assert self.preprocessor.pixel_to_world(None) is None
        
        # Real homography transformation test
        aruco_img = cv.imread(os.path.join(TESTMODE_DIR, 'aruco.png'))
        self.preprocessor.setup(aruco_img)
        
        pixel = (100, 100)
        world = self.preprocessor.pixel_to_world(pixel)
        assert world is not None
        assert len(world) == 2
        assert isinstance(world[0], float) or isinstance(world[0], np.float32)

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

    def test_extract_orientation(self):
        """extract_orientation should calculate rotation angles for minAreaRect contours."""
        aruco_img = cv.imread(os.path.join(TESTMODE_DIR, 'aruco.png'))
        self.preprocessor.setup(aruco_img)
        cat_img = cv.imread(os.path.join(TESTMODE_DIR, 'cat_0.png'))
        warped = self.preprocessor.warp_image(cat_img)
        contours = self.preprocessor.segment_object(warped)
        largest_contour = max(contours, key=cv.contourArea)
        
        angle = self.preprocessor.extract_orientation(largest_contour)
        assert isinstance(angle, float)

    def test_speed_calculation_from_images(self):
        """Verify speed calculation by locating object positions in consecutive frames _0 and _1."""
        try:
            from coord_pred import CoordinatesPrediction
        except (ImportError, ModuleNotFoundError):
            from coord_pred.coord_pred import CoordinatesPrediction


        aruco_img = cv.imread(os.path.join(TESTMODE_DIR, 'aruco.png'))
        self.preprocessor.setup(aruco_img)
        
        objects = ['cat', 'unicorn', 'rejected']
        # Known expected speeds with t0=0.0 and t1=0.5
        expected_speeds = {
            'cat': 153.5377,
            'unicorn': 269.2299,
            'rejected': 63.5727
        }

        for name in objects:
            img_0 = cv.imread(os.path.join(TESTMODE_DIR, f'{name}_0.png'))
            img_1 = cv.imread(os.path.join(TESTMODE_DIR, f'{name}_1.png'))
            
            # Step 1: Preprocess, warp, segment and find positions
            w_0 = self.preprocessor.warp_image(img_0)
            p_0 = self.preprocessor.obj_position(self.preprocessor.segment_object(w_0))
            world_0 = self.preprocessor.pixel_to_world(p_0)
            
            w_1 = self.preprocessor.warp_image(img_1)
            p_1 = self.preprocessor.obj_position(self.preprocessor.segment_object(w_1))
            world_1 = self.preprocessor.pixel_to_world(p_1)
            
            # Step 2: Calculate speed using CoordinatesPrediction
            pred = CoordinatesPrediction()
            # First call returns -100
            res_0 = pred.calculate_speed_with_ID(id=1, x=world_0[0], t=0.0)
            assert res_0 == -100
            
            # Second call calculates speed
            speed = pred.calculate_speed_with_ID(id=1, x=world_1[0], t=0.5)
            
            # Assert speed is close to expected
            assert pytest.approx(speed, rel=1e-3) == expected_speeds[name]

