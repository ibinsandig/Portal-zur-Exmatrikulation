import numpy as np

SRC_COORDS = (np.array([[[ 0.,  0.],  [60., 0.],   [60., 60.],  [ 0.,60.], 
                                [ 0., 222.], [60., 222.], [60., 282.], [ 0., 282.]]], dtype= np.float32))

OFFSET_AREA = None

OFFSET_OBJ_TYPE = None

X_MIN_SAFE = 100.0
X_MAX_SAFE = 550.0

GRIP_OFFSETS = {
    0:  (0.0,  0.0),   # rejected
    1:  (15.0, 5.0),   # Cat
    27: (20.0, 10.0),  # Unicorn
}