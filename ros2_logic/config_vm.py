import numpy as np

x1_initial = 246. # mm
y1_initial = -44. # mm

x2_initial = -244. # mm
y2_initial = -102. # mm

x3_initial = 304. # mm
y3_initial = -102. # mm

offset_second_marker_1 = 222.
offset_second_marker_2 = 280.

SRC_COORDS_1 = (np.array([[[ -44.,  246.],  [-102., 244.],   [-102., 304.],  [ -44.,304.], 
                                [ -44., 222 + 246.], [-102., 222 + 246.], [-102., 282. + 244], [ -44., 282. + 244]]], dtype= np.float32))

SRC_COORDS_2 = np.array([[[0.246, -0.044], [0.244, -0.102], [0.304, -0.102], [0.304, -0.044],
                          [0.468, -0.044], [0.466, -0.102], [0.526, -0.102], [0.528, -0.044]]], dtype=np.float32)


OFFSET_AREA = None

OFFSET_OBJ_TYPE = None

X_MIN_SAFE = 0
X_MAX_SAFE = 550.0

GRIP_OFFSETS = {
    0:  (0.0,  0.0),   # rejected
    1:  (15.0, 5.0),   # Cat
    27: (20.0, 10.0),  # Unicorn
}