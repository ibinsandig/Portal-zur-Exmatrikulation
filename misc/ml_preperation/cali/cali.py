import numpy as np
import cv2
import yaml
import time

# ==============================
# ChArUco Board Parameter
# ==============================
SQUARES_X = 7
SQUARES_Y = 5
BOARD_WIDTH = 224  # mm
BOARD_HEIGHT = 156  # mm

SQUARE_LENGTH = BOARD_WIDTH / SQUARES_X
MARKER_LENGTH = SQUARE_LENGTH * 0.75

# ==============================
# Board erstellen
# ==============================
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
board = cv2.aruco.CharucoBoard(
    (SQUARES_X, SQUARES_Y),
    SQUARE_LENGTH,
    MARKER_LENGTH,
    aruco_dict
)

charuco_detector = cv2.aruco.CharucoDetector(board)

# ==============================
# Datenspeicher
# ==============================
all_charuco_corners = []
all_charuco_ids = []
image_size = None

# ==============================
# Kamera starten
# ==============================

cap = cv2.VideoCapture(0)

# Kamera prüfen
if not cap.isOpened():
    print("❌ Kamera konnte nicht geöffnet werden!")
    exit()

# Optionale Auflösung
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

found = 0
required_images = 20

print(f"Sammle {required_images} Kalibrierungsbilder...")
print("Bewege das ChArUco Board in verschiedene Positionen und Winkel")
print("Drücke 'q' zum Abbrechen\n")

cv2.namedWindow('ChArUco Detection', cv2.WINDOW_NORMAL)
cv2.resizeWindow('ChArUco Detection', 1280, 720)
# ==============================
# Hauptloop
# ==============================
while found < required_images:
    ret, img = cap.read()
    if not ret:
        print("❌ Fehler beim Lesen der Kamera")
        break

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if image_size is None:
        image_size = gray.shape[::-1]

    # Detection
    charuco_corners, charuco_ids, marker_corners, marker_ids = charuco_detector.detectBoard(gray)

    display_img = img.copy()

    # Marker zeichnen
    if marker_corners is not None and marker_ids is not None:
        cv2.aruco.drawDetectedMarkers(display_img, marker_corners, marker_ids)

    # ChArUco Ecken zeichnen
    if charuco_corners is not None and charuco_ids is not None:
        cv2.aruco.drawDetectedCornersCharuco(display_img, charuco_corners, charuco_ids)

    # Overlay Infos
    cv2.putText(display_img, f"Bilder: {found}/{required_images}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Gültiges Bild speichern
    if charuco_corners is not None and len(charuco_corners) > 6:
        all_charuco_corners.append(charuco_corners)
        all_charuco_ids.append(charuco_ids)
        found += 1

        print(f"Bild {found}/{required_images} erfasst ({len(charuco_corners)} Ecken)")
        time.sleep(0.3)  # kleine Pause gegen Duplikate

    # IMMER anzeigen
    cv2.imshow('ChArUco Detection', display_img)

    print("Marker:", 0 if marker_ids is None else len(marker_ids),
      "| Charuco:", 0 if charuco_ids is None else len(charuco_ids))

    # Exit mit q
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# ==============================
# Cleanup
# ==============================
cap.release()
cv2.destroyAllWindows()

# ==============================
# Kalibrierung
# ==============================
if len(all_charuco_corners) < 5:
    print("❌ Zu wenige gültige Bilder für Kalibrierung!")
    exit()

print("\nStarte Kalibrierung...")

ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(
    all_charuco_corners,
    all_charuco_ids,
    board,
    image_size,
    None,
    None
)

if ret:
    print("\n✅ Kalibrierung erfolgreich!")
    print(f"Reprojection Error: {ret:.4f} Pixel")

    data = {
        'camera_matrix': np.asarray(camera_matrix).tolist(),
        'dist_coeff': np.asarray(dist_coeffs).tolist(),
        'reprojection_error': float(ret),
        'board_config': {
            'squares_x': SQUARES_X,
            'squares_y': SQUARES_Y,
            'square_length': float(SQUARE_LENGTH),
            'marker_length': float(MARKER_LENGTH)
        }
    }

    with open("charuco_cali.yaml", "w") as f:
        yaml.dump(data, f)

    print("\n📁 Kalibrierung gespeichert in 'charuco_cali.yaml'")
    print("\nKamera-Matrix:")
    print(camera_matrix)
    print("\nVerzerrungskoeffizienten:")
    print(dist_coeffs)

else:
    print("❌ Kalibrierung fehlgeschlagen!")