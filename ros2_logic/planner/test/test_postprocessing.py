import pytest
import sys
import os
import math

# Add the parent directory (planner) to the system path to import postprocessing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from postprocessing import PostProcessor, GRIP_OFFSETS


class DummyPose2D:
    """A dummy class to mimic geometry_msgs.msg.Pose2D in tests."""
    def __init__(self, x=0.0, y=0.0, theta=0.0):
        self.x = x
        self.y = y
        self.theta = theta


class TestPostProcessor:
    """Test cases for the PostProcessor class."""

    def setup_method(self):
        """Setup a fresh PostProcessor instance before each test."""
        self.processor = PostProcessor()

    def test_init_state(self):
        """Verify the initial state of the PostProcessor."""
        assert len(self.processor.pending) == 0
        assert len(self.processor.queue) == 0
        assert len(self.processor.queued_ids) == 0
        assert self.processor.get_next() is None

    def test_add_obj_type_rejected(self):
        """Objects with type 0 (rejected) should be discarded immediately."""
        self.processor.add_obj_type(id=1, obj_type=0)
        assert 1 not in self.processor.pending
        assert 1 not in self.processor.queued_ids
        assert len(self.processor.queue) == 0

    def test_add_obj_type_valid(self):
        """Valid object types should be added to pending, but not queued yet without position."""
        self.processor.add_obj_type(id=1, obj_type=1)
        assert 1 in self.processor.pending
        assert self.processor.pending[1]['obj_type'] == 1
        assert 1 not in self.processor.queued_ids
        assert self.processor.get_next() is None

    def test_add_future_position_only(self):
        """Adding future position first should prepare the pending object structure."""
        pose = DummyPose2D(10.0, 20.0, 0.0)
        self.processor.add_future_position(id=1, pose2d=pose, speed=5.0)
        assert 1 in self.processor.pending
        assert self.processor.pending[1]['pose2d'] == pose
        assert self.processor.pending[1]['speed'] == 5.0
        assert 1 not in self.processor.queued_ids
        assert self.processor.get_next() is None

    def test_merge_success(self):
        """When both type and position are available, the object should be queued."""
        pose = DummyPose2D(10.0, 20.0, 0.0)
        self.processor.add_obj_type(id=1, obj_type=1)
        self.processor.add_future_position(id=1, pose2d=pose, speed=5.0)

        assert 1 in self.processor.queued_ids
        assert len(self.processor.queue) == 1
        assert self.processor.queue[0] == 1

        output = self.processor.get_next()
        assert output is not None
        assert output['id'] == 1
        assert output['obj_type'] == 1
        assert output['pose2d'] == pose
        assert output['speed'] == 5.0
        assert 'grip_point' in output

    def test_add_future_position_after_already_queued(self):
        """Adding future position when already queued should update it but not double queue."""
        pose1 = DummyPose2D(10.0, 20.0, 0.0)
        self.processor.add_obj_type(id=1, obj_type=1)
        self.processor.add_future_position(id=1, pose2d=pose1, speed=5.0)
        
        assert len(self.processor.queue) == 1
        
        pose2 = DummyPose2D(15.0, 25.0, 0.0)
        self.processor.add_future_position(id=1, pose2d=pose2, speed=6.0)
        
        assert len(self.processor.queue) == 1
        output = self.processor.get_next()
        assert output['pose2d'] == pose2
        assert output['speed'] == 6.0

    def test_finish_obj(self):
        """Finishing an object should clean up its tracking state completely."""
        pose = DummyPose2D(10.0, 20.0, 0.0)
        self.processor.add_obj_type(id=1, obj_type=1)
        self.processor.add_future_position(id=1, pose2d=pose, speed=5.0)

        assert 1 in self.processor.queued_ids
        self.processor.finish_obj(1)

        assert 1 not in self.processor.queued_ids
        assert 1 not in self.processor.pending
        assert len(self.processor.queue) == 0
        assert self.processor.get_next() is None

    def test_calculate_grip_point_theta_zero(self):
        """Grip point calculation with orientation theta=0 should apply raw offset."""
        pose = DummyPose2D(100.0, 200.0, 0.0)
        
        # Test Cat (ID 1) -> offset is (15.0, 5.0)
        grip = self.processor.calculate_grip_point(pose, obj_type=1)
        assert pytest.approx(grip['x']) == 100.0 + 15.0
        assert pytest.approx(grip['y']) == 200.0 + 5.0
        assert grip['theta'] == 0

        # Test Unicorn (ID 27) -> offset is (20.0, 10.0)
        grip = self.processor.calculate_grip_point(pose, obj_type=27)
        assert pytest.approx(grip['x']) == 100.0 + 20.0
        assert pytest.approx(grip['y']) == 200.0 + 10.0
        assert grip['theta'] == 0

        # Test Unknown -> default offset is (10.0, 0.0)
        grip = self.processor.calculate_grip_point(pose, obj_type=999)
        assert pytest.approx(grip['x']) == 100.0 + 10.0
        assert pytest.approx(grip['y']) == 200.0 + 0.0
        assert grip['theta'] == 0

    def test_calculate_grip_point_theta_rotated(self):
        """Grip point offset should rotate correctly with non-zero orientation."""
        # 90 degrees rotation
        pose = DummyPose2D(100.0, 200.0, 90.0)
        
        # Cat (ID 1) -> offset (15.0, 5.0)
        # cos(90) = 0, sin(90) = 1
        # grip_x = 100.0 + 15 * 0 - 5 * 1 = 95.0
        # grip_y = 200.0 + 15 * 1 + 5 * 0 = 215.0
        grip = self.processor.calculate_grip_point(pose, obj_type=1)
        assert pytest.approx(grip['x']) == 95.0
        assert pytest.approx(grip['y']) == 215.0
