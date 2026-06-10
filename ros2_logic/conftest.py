import sys
import os
import cv2
import pytest

# Add packages under ros2_logic to sys.path in correct order so we can import and patch them
base_dir = os.path.dirname(os.path.abspath(__file__))
# First add the root ros2_logic directory
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
# Then insert subdirectories at the front (index 0) so they take precedence
for folder in ['camera', 'coord_pred', 'machine_learning', 'planner']:
    path = os.path.abspath(os.path.join(base_dir, folder))
    if path not in sys.path:
        sys.path.insert(0, path)

# -------------------------------------------------------------
# Data Collectors
# -------------------------------------------------------------
images_read = []
preprocessor_setups = []
detections = []
classifications = []
speeds = []
grip_points = []

# Cache to associate image numpy arrays with filenames
image_cache = {}

# Keep track of pixels to associate them with the image they were segmented from
pixel_positions = {}
last_segmented_image = None

# -------------------------------------------------------------
# Patching / Hooking
# -------------------------------------------------------------

# 1. Patch cv2.imread
original_imread = cv2.imread

def custom_imread(filename, *args, **kwargs):
    img = original_imread(filename, *args, **kwargs)
    basename = os.path.basename(filename)
    success = img is not None
    
    # Track details of the read image (avoid duplicates to keep the report clean)
    if not any(item['path'] == filename for item in images_read):
        images_read.append({
            'path': filename,
            'basename': basename,
            'shape': img.shape if success else None,
            'success': success
        })
    
    if success:
        image_cache[id(img)] = basename
    return img

cv2.imread = custom_imread

# 2. Patch ImagePreprocessor.setup
try:
    from preprocessing import ImagePreprocessor
    original_setup = ImagePreprocessor.setup

    def custom_setup(self, init_frame):
        res = original_setup(self, init_frame)
        img_name = image_cache.get(id(init_frame), "Unknown Image")
        preprocessor_setups.append({
            'image': img_name,
            'success': self.H is not None,
            'width': self.width if self.H is not None else None,
            'height': self.height if self.H is not None else None
        })
        return res
    ImagePreprocessor.setup = custom_setup

    # Patch ImagePreprocessor.warp_image to preserve image identity/name
    original_warp_image = ImagePreprocessor.warp_image

    def custom_warp_image(self, frame):
        warped = original_warp_image(self, frame)
        if warped is not None and id(frame) in image_cache:
            image_cache[id(warped)] = image_cache[id(frame)]
        return warped
    ImagePreprocessor.warp_image = custom_warp_image

    # Patch ImagePreprocessor.segment_object to record last segmented image
    original_segment_object = ImagePreprocessor.segment_object

    def custom_segment_object(self, frame):
        global last_segmented_image
        last_segmented_image = image_cache.get(id(frame), "Unknown Image")
        contours = original_segment_object(self, frame)
        return contours
    ImagePreprocessor.segment_object = custom_segment_object

    # Patch ImagePreprocessor.obj_position to map calculated position back to image name
    original_obj_position = ImagePreprocessor.obj_position

    def custom_obj_position(self, contours):
        pos = original_obj_position(self, contours)
        if pos is not None and last_segmented_image is not None:
            pixel_positions[pos] = last_segmented_image
        return pos
    ImagePreprocessor.obj_position = custom_obj_position

    # Patch ImagePreprocessor.pixel_to_world to correlate pixel/world coordinates and image
    original_pixel_to_world = ImagePreprocessor.pixel_to_world

    def custom_pixel_to_world(self, pixel):
        world = original_pixel_to_world(self, pixel)
        if pixel is not None and world is not None:
            image_name = pixel_positions.get(pixel, last_segmented_image or "Unknown Image")
            detections.append({
                'image': image_name,
                'pixel': pixel,
                'world': (float(world[0]), float(world[1]))
            })
        return world
    ImagePreprocessor.pixel_to_world = custom_pixel_to_world

except Exception as e:
    # Modules might not be present in every path configuration, handle gracefully
    pass

# 3. Patch Classifier.classify
try:
    from classify import Classifier
    original_classify = Classifier.classify

    def custom_classify(self, hu_2, hu_3):
        pred, conf = original_classify(self, hu_2, hu_3)
        classifications.append({
            'hu_2': hu_2,
            'hu_3': hu_3,
            'pred': pred,
            'conf': conf
        })
        return pred, conf
    Classifier.classify = custom_classify
except Exception as e:
    pass

# 4. Patch CoordinatesPrediction.calculate_speed_with_ID
try:
    from coord_pred import CoordinatesPrediction
    original_calculate_speed = CoordinatesPrediction.calculate_speed_with_ID

    def custom_calculate_speed(self, id, x, t):
        speed = original_calculate_speed(self, id, x, t)
        speeds.append({
            'id': id,
            'x': x,
            't': t,
            'speed': speed
        })
        return speed
    CoordinatesPrediction.calculate_speed_with_ID = custom_calculate_speed
except Exception as e:
    pass

# 5. Patch PostProcessor.calculate_grip_point
try:
    from postprocessing import PostProcessor
    original_calculate_grip_point = PostProcessor.calculate_grip_point

    def custom_calculate_grip_point(self, pose2d, obj_type):
        grip = original_calculate_grip_point(self, pose2d, obj_type)
        grip_points.append({
            'x': pose2d.x,
            'y': pose2d.y,
            'theta': pose2d.theta,
            'obj_type': obj_type,
            'grip_x': grip['x'],
            'grip_y': grip['y'],
            'grip_theta': grip['theta']
        })
        return grip
    PostProcessor.calculate_grip_point = custom_calculate_grip_point
except Exception as e:
    pass


# -------------------------------------------------------------
# Helper for terminal representation
# -------------------------------------------------------------
def format_table(headers, keys, data):
    if not data:
        return "  (Keine Daten erfasst)\n"
    
    widths = [len(h) for h in headers]
    for row in data:
        for i, key in enumerate(keys):
            val_str = str(row.get(key, ''))
            if len(val_str) > widths[i]:
                widths[i] = len(val_str)
                
    top = "┌─" + "─┬─".join("─" * w for w in widths) + "─┐"
    header_line = "│ " + " │ ".join(f"{h:<{widths[i]}}" for i, h in enumerate(headers)) + " │"
    divider = "├─" + "─┼─".join("─" * w for w in widths) + "─┤"
    bottom = "└─" + "─┴─".join("─" * w for w in widths) + "─┘"
    
    lines = [top, header_line, divider]
    for row in data:
        row_line = "│ " + " │ ".join(f"{str(row.get(key, '')):<{widths[i]}}" for i, key in enumerate(keys)) + " │"
        lines.append(row_line)
    lines.append(bottom)
    return "\n".join("  " + l for l in lines) + "\n"


# -------------------------------------------------------------
# Pytest Hook for Summary Report
# -------------------------------------------------------------
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    # Print custom summary section header
    terminalreporter.write_sep('=', 'TEST RUN DATA FEEDBACK SUMMARY', bold=True, green=True)
    
    # 1. Section: Images Read
    terminalreporter.write_line("\n📌 1. EINGELESENE BILDER (cv2.imread)", bold=True, yellow=True)
    img_data = []
    for item in images_read:
        shape = item['shape']
        shape_str = f"{shape[1]}x{shape[0]} ({shape[2]} ch)" if shape else "N/A"
        img_data.append({
            'filename': item['basename'],
            'dimensions': shape_str,
            'status': "ERFOLGREICH" if item['success'] else "FEHLGESCHLAGEN"
        })
    terminalreporter.write_line(format_table(
        ["Dateiname", "Dimensionen", "Status"],
        ["filename", "dimensions", "status"],
        img_data
    ))
    
    # 2. Section: Preprocessor Setup
    terminalreporter.write_line("📌 2. HOMOGRAPHIE-SETUP (ImagePreprocessor.setup)", bold=True, yellow=True)
    setup_data = []
    for item in preprocessor_setups:
        size_str = f"{item['width']}x{item['height']} px" if item['success'] else "N/A"
        setup_data.append({
            'image': item['image'],
            'status': "ERFOLGREICH" if item['success'] else "FEHLGESCHLAGEN",
            'resolution': size_str
        })
    terminalreporter.write_line(format_table(
        ["Referenz-Bild", "Setup Status", "Ziel-Auflösung"],
        ["image", "status", "resolution"],
        setup_data
    ))
    
    # 3. Section: Segmented objects & coordinates
    terminalreporter.write_line("📌 3. ERFASSTE OBJEKT-KOORDINATEN (Pixel & Welt)", bold=True, yellow=True)
    det_data = []
    # Deduplicate coordinate entries to keep report readable
    seen_dets = set()
    for item in detections:
        key = (item['image'], item['pixel'], item['world'])
        if key in seen_dets:
            continue
        seen_dets.add(key)
        
        pixel_str = f"({item['pixel'][0]}, {item['pixel'][1]})"
        world_str = f"({item['world'][0]:.2f}, {item['world'][1]:.2f})"
        det_data.append({
            'image': item['image'],
            'pixel': pixel_str,
            'world': world_str
        })
    terminalreporter.write_line(format_table(
        ["Bildquelle", "Pixel-Zentroid (x, y)", "Welt-Koordinaten (X, Y)"],
        ["image", "pixel", "world"],
        det_data
    ))
    
    # 4. Section: Classifications
    terminalreporter.write_line("📌 4. KLASSIFIZIERUNGS-ERGEBNISSE (Classifier)", bold=True, yellow=True)
    class_data = []
    # Map class IDs to names
    type_names = {0: "Rejected", 1: "Cat", 27: "Unicorn"}
    for item in classifications:
        pred = item['pred']
        type_name = type_names.get(pred, f"Unknown ({pred})")
        hu_str = f"hu2={item['hu_2']:.6f}, hu3={item['hu_3']:.6f}"
        class_data.append({
            'moments': hu_str,
            'pred_id': str(pred),
            'label': type_name,
            'confidence': f"{item['conf']*100:.1f}%"
        })
    terminalreporter.write_line(format_table(
        ["Hu-Momente (Eingabe)", "Typ-ID", "Klassifizierung", "Konfidenz"],
        ["moments", "pred_id", "label", "confidence"],
        class_data
    ))
    
    # 5. Section: Speed calculation
    terminalreporter.write_line("📌 5. GESCHWINDIGKEITSBERECHNUNG (CoordinatesPrediction)", bold=True, yellow=True)
    speed_data = []
    for item in speeds:
        speed_val = item['speed']
        speed_str = "Erster Frame / ID-Wechsel" if speed_val == -100 else f"{speed_val:.2f} mm/s"
        speed_data.append({
            'id': str(item['id']),
            'coord_x': f"{item['x']:.2f} mm",
            'time': f"{item['t']:.2f} s",
            'speed': speed_str
        })
    terminalreporter.write_line(format_table(
        ["Objekt-ID", "Koordinate X", "Zeitstempel t", "Berechnete Geschw."],
        ["id", "coord_x", "time", "speed"],
        speed_data
    ))
    
    # 6. Section: Grip Points
    terminalreporter.write_line("📌 6. GREIFPUNKT-POSTPROCESSING (PostProcessor)", bold=True, yellow=True)
    grip_data = []
    for item in grip_points:
        obj_t = item['obj_type']
        label = type_names.get(obj_t, f"Unknown ({obj_t})")
        pose_str = f"({item['x']:.1f}, {item['y']:.1f}, θ={item['theta']:.1f}°)"
        grip_str = f"({item['grip_x']:.1f}, {item['grip_y']:.1f}, θ={item['grip_theta']:.1f}°)"
        grip_data.append({
            'label': label,
            'pose': pose_str,
            'grip': grip_str
        })
    terminalreporter.write_line(format_table(
        ["Objekttyp", "Objekt-Pose (x, y, θ)", "Greifpunkt (x, y, θ)"],
        ["label", "pose", "grip"],
        grip_data
    ))
