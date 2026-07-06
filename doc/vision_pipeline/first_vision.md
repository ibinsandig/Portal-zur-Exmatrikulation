# Vision-Pipeline: Implementierungs-Details

<!-- Written, maintained and owned by Linus Braun -->

## Übersicht

Diese Dokumentation beschreibt die detaillierte Implementierung der Vision- und Verarbeitungs-Pipeline des Portal-zur-Exmatrikulation-Systems. Die Pipeline besteht aus vier ROS2-Nodes sowie den zugehörigen Logik-Klassen.

**Datenfluss**:
```
Camera-Node → CoordPred-Node → Planner-Node
     ↓
MachineLearning-Node → Planner-Node
```

| Modul | Klasse | Datei |
|---|---|---|
| ROS2-Node | `Camera` | `chaos_nodes/camera.py` |
| ROS2-Node | `CoordPred` | `chaos_nodes/coord_pred.py` |
| ROS2-Node | `Machine_learning` | `chaos_nodes/machine_learning.py` |
| ROS2-Node | `Planner` | `chaos_nodes/planner.py` |
| Logik | `ImagePreprocessor` | `ros2_logic/camera/preprocessing.py` |
| Logik | `CoordinatesPrediction` | `ros2_logic/coord_pred/coord_pred.py` |
| Logik | `Classifier` | `ros2_logic/machine_learning/classify.py` |
| Logik | `PostProcessor` | `ros2_logic/planner/postprocessing.py` |

---

## Camera Node – Detaillierte Implementierung

### ROS2-Komponenten

| Komponente | Topic / Device | Konfiguration |
|---|---|---|
| **Publisher** | `/obj_coords` | `ObjCoords`, Queue=10 |
| **Publisher** | `/obj_features` | `ObjFeatures`, Queue=10 |
| **Timer** | – | 1/5 Sekunden (5 Hz) |
| **Kamera** | `/dev/video4` | OpenCV VideoCapture(4), 1920×1080 |

### Konstruktor `__init__()`

#### Initialisierungsablauf

1. **Publisher erstellen** für `/obj_coords` und `/obj_features`
2. **ImagePreprocessor instanziieren**
3. **Kamera öffnen** (`/dev/video4`, 1920×1080, Buffer=1)
4. **Kalibrierungs-Setup:**
   - 5 Sekunden warten → Nutzer legt ArUco-Marker ein
   - `setup()` wiederholt aufrufen bis `H_inv is not None`
   - 10 Sekunden warten → Nutzer entfernt Marker
5. **Timer starten** (5 Hz)

**Buffer-Size = 1**: Verhindert Zwischenspeicherung alter Frames und gewährleistet immer das aktuellste Bild.

#### Initialisierte Instanzvariablen

| Variable | Typ | Init-Wert | Zweck |
|---|---|---|---|
| `pub_obj_coords` | Publisher | – | Publiziert Weltkoordinaten |
| `pub_obj_festures` | Publisher | – | Publiziert Hu-Moment-Features |
| `PrePro` | `ImagePreprocessor` | Instanz | Bildvorverarbeitung |
| `img` | `cv.VideoCapture` | video4 | Kamera-Handle |
| `currend_id` | int | 1 | Laufende Objekt-ID |
| `last_pos_x` | float | None | Letzte X-Position für ID-Vergabe |

---

### Methode `timer_callback()`

**Alle 1/5 Sekunden**:

1. **Frame erfassen und verarbeiten**
   ```python
   obj_coords_msg, obj_features_msg = self.process_img(self.read_camera())
   ```
2. **Validierung**: Falls eines der Ergebnisse `None` ist → abbrechen
3. **Publizieren** auf `/obj_coords` und `/obj_features`

---

### Methode `read_camera()`

#### Schritte

1. **Frame erfassen**
   ```python
   success, frame = self.img.read()
   ```
2. **Fehlerbehandlung**: Bei `success == False` → `None` zurückgeben
3. **BGR → Grayscale**
   ```python
   gray_image = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
   ```
4. **Bild rotieren** (180°, `cv.rotate(gray_image, 2)`)

#### Rückgabewert

- **Erfolg**: `numpy.ndarray` – Shape `(h, w)`, dtype=uint8
- **Fehler**: `None`

---

### Methode `process_img(frame)`

#### Eingabe
- **`frame`** (numpy.ndarray): Grayscale-Bild von `read_camera()`

#### Verarbeitungsschritte

**1. Bildentzerrung**
```python
warped_image = self.PrePro.warp_image(frame)
```

**2. Segmentierung**
```python
contours = self.PrePro.segment_object(warped_image)
```
Nur Konturen mit Fläche > 100 Pixel werden weiterverarbeitet.

**3. Weltkoordinaten berechnen**
```python
pixel_pos = self.PrePro.get_grippoint([cnt], warped_image.shape)
world_pos = self.PrePro.pixel_to_world(pixel_pos)
```

**4. Sicherer Bereich filtern**
```python
valid_objects = [obj for obj in objects
    if cfg.X_MIN_SAFE < obj['world_pos'][0] < cfg.X_MAX_SAFE]
```
Nur Objekte innerhalb `[X_MIN_SAFE, X_MAX_SAFE]` werden berücksichtigt.

**5. Führendes Objekt auswählen**
```python
most_advanced = max(valid_objects, key=lambda obj: obj['world_pos'][0])
```
Das Objekt mit dem größten X-Wert (am weitesten fortgeschritten auf dem Band) wird gewählt.

**6. Features extrahieren**
```python
obj_features_dict = self.PrePro.extract_features_from_contour(most_advanced['contour'])
```

**7. ROS2-Nachrichten erstellen** (`ObjCoords`, `ObjFeatures`) und ID vergeben via `assign_id()`

#### Rückgabewerte

| Szenario | Rückgabe |
|---|---|
| Kein Frame | `(None, None)` |
| Keine Konturen | `(None, None)` |
| Kein Objekt im sicheren Bereich | `(None, None)` |
| Features nicht extrahierbar | `(None, None)` |
| Erfolg | `(ObjCoords, ObjFeatures)` |

---

### Methode `assign_id(x, threshold=0.05)`

#### Logik

```
Wenn last_pos_x bekannt:
    Abstand = |x - last_pos_x|
    Abstand ≥ threshold → neue ID (currend_id + 1)
    Abstand < threshold → gleiche ID
Sonst:
    erste Messung → ID bleibt 1
```

**Threshold = 0.05 m**: Sprünge kleiner als 5 cm gelten als dasselbe Objekt.

#### Rückgabewert
- **Typ**: `int` – aktuelle Objekt-ID

---

## CoordPred Node – Detaillierte Implementierung

### ROS2-Komponenten

| Komponente | Topic | Typ | Konfiguration |
|---|---|---|---|
| **Subscriber** | `/obj_coords` | `ObjCoords` | Queue=10 |
| **Publisher** | `/future_position` | `FuturePosition` | Queue=10 |

### Konstruktor `__init__()`

Initialisiert Subscriber, Publisher und eine Instanz von `CoordinatesPrediction`.

---

### Methode `listener_callback(msg)`

#### Eingabe
- **`msg`** (`ObjCoords`): ID, Pose2D (x, y, theta), Zeitstempel

#### Verarbeitungsschritte

1. **Geschwindigkeit berechnen**
   ```python
   result = self.PrePro.add_measurement(id=msg.id, x=msg.pose2d.x, t=msg.timestamp)
   ```
   Gibt `None` zurück, wenn noch keine Geschwindigkeit berechenbar.

2. **FuturePosition-Nachricht befüllen**
   ```python
   future_position.id        = result['id']
   future_position.pose2d    = msg.pose2d
   future_position.timestamp = msg.timestamp
   future_position.speed     = float(result['speed'])
   ```

3. **Publizieren** auf `/future_position`

---

## Machine_learning Node – Detaillierte Implementierung

### ROS2-Komponenten

| Komponente | Topic | Typ | Konfiguration |
|---|---|---|---|
| **Subscriber** | `/obj_features` | `ObjFeatures` | Queue=10 |
| **Publisher** | `/obj_type` | `ObjType` | Queue=10 |

### Konstruktor `__init__()`

Initialisiert Subscriber, Publisher und eine Instanz von `Classifier`.

---

### Methode `listener_callback(msg)`

#### Eingabe
- **`msg`** (`ObjFeatures`): ID, hu_2, hu_3

#### Verarbeitungsschritte

1. **Klassifikation**
   ```python
   smoothed_label, confidence = self.classifier.classify(
       id=msg.id, hu_2=msg.hu_2, hu_3=msg.hu_3)
   ```

2. **ObjType-Nachricht befüllen**
   ```python
   pub_data.id       = msg.id
   pub_data.obj_type = smoothed_label
   ```

3. **Publizieren** auf `/obj_type`

---

## Planner Node – Detaillierte Implementierung

### ROS2-Komponenten

| Komponente | Topic | Typ | Konfiguration |
|---|---|---|---|
| **Subscriber** | `/obj_type` | `ObjType` | Queue=10 |
| **Subscriber** | `/future_position` | `FuturePosition` | Queue=10 |
| **Subscriber** | `/obj_finished` | `Int16` | Queue=10 |
| **Publisher** | `/obj_data` | `ObjData` | Queue=10 |
| **Timer** | – | 0.1 Sekunden (10 Hz) | – |

### Konstruktor `__init__()`

Initialisiert alle drei Subscriber, den Publisher, den Timer (10 Hz) und eine Instanz von `PostProcessor`.

---

### Methode `callback_obj_type(msg)`

Ruft `PostProcessor.add_obj_type(msg.id, msg.obj_type)` auf.

---

### Methode `callback_future_position(msg)`

Ruft `PostProcessor.add_future_position(msg.id, msg.pose2d, msg.speed, msg.timestamp)` auf.

---

### Methode `callback_obj_finished(msg)`

Ruft `PostProcessor.finish_obj(msg.data)` auf und entfernt das Objekt aus der Queue.

---

### Methode `timer_callback()`

#### Verarbeitungsschritte

1. **Nächstes Objekt holen**
   ```python
   obj = self.PostPro.get_next()
   ```
   Bei `None` → abbrechen (Queue leer oder unvollständige Daten).

2. **Rejected-Objekte verwerfen**
   ```python
   if obj['obj_type'] == 0:
       self.PostPro.finish_obj(obj['id'])
       return
   ```

3. **ObjData-Nachricht befüllen**
   ```python
   pub_data.id        = obj['id']
   pub_data.obj_typ   = obj['obj_type']
   pub_data.point.x   = float(obj['grip_point']['x'])
   pub_data.point.y   = float(obj['grip_point']['y'])
   pub_data.obj_speed = float(obj['speed'])
   ```

4. **Publizieren** auf `/obj_data`

---

## ImagePreprocessor – Detaillierte Implementierung

### Konstruktor `__init__()`

#### Initialisierte Komponenten

| Komponente | Typ | Zweck |
|---|---|---|
| `self.detector` | `aruco.ArucoDetector` | Marker-Erkennung (DICT_4X4_100) |
| `self.H_pre` | `numpy.ndarray` (3×3) | Vorläufige Homographie (Setup) |
| `self.H_pre_inv` | `numpy.ndarray` (3×3) | Inverse vorläufige Homographie |
| `self.M_all` | `numpy.ndarray` (3×3) | Pixel → entzerrtes Bild |
| `self.M_all_inv` | `numpy.ndarray` (3×3) | Entzerrtes Bild → Pixel |
| `self.H` | `numpy.ndarray` (3×3) | Pixel → Weltkoordinaten |
| `self.H_inv` | `numpy.ndarray` (3×3) | Weltkoordinaten → Pixel (gesetzt nach erfolgreichem Setup) |
| `self.width` | int | Breite des entzerrten Bilds |
| `self.height` | int | Höhe des entzerrten Bilds |

---

### Methode `setup(init_frame)`

#### Eingabe
- **`init_frame`** (numpy.ndarray): Grayscale-Bild mit mindestens 2 sichtbaren ArUco-Markern

#### Berechnungsschritte

**1. Marker-Erkennung**
```python
corners, ids, rejected = self.detector.detectMarkers(init_frame)
```
Weniger als 2 Marker gefunden → abbrechen, Debug-Bild speichern.

**2. Vorläufige Homographie (H_pre)**
```python
H_pre, _ = cv.findHomography(srcPoints=cfg.SRC_COORDS_2, dstPoints=dstPoints, method=0)
H_pre_inv = np.linalg.inv(H_pre)
```
Mappt Konfigurationskoordinaten auf Bildpixel und umgekehrt.

**3. Offset-Korrektur**

Marker-Ecken werden um ±6 mm in Weltkoordinaten verschoben, um die physische Marker-Rahmengröße zu kompensieren:
```python
offset_raw = np.array([
    [-0.006, +0.006],  # oben-links
    [-0.006, -0.006],  # oben-rechts
    [+0.006, +0.006],  # unten-links
    [+0.006, -0.006]   # unten-rechts
], dtype=np.float32)
```

**4. Perspektivtransformation M_all berechnen**
```python
self.M_all = cv.getPerspectiveTransform(pts1_2_pixel, pts2_proportional)
self.M_all_inv = np.linalg.inv(self.M_all)
```
Transformiert das Rohbild auf ein rechteckiges, unverzerrtes Bild der Größe `(self.width, self.height)`.

**5. Finale Homographie H im entzerrten Bild**

ArUco-Marker im entzerrten Bild detektieren, nach ID absteigend sortieren und zweite Homographie berechnen:
```python
self.H, _ = cv.findHomography(srcPoints=cfg.SRC_COORDS_2, dstPoints=dstPoints, method=0)
self.H_inv = np.linalg.inv(self.H)
```

**Setup erfolgreich** wenn `H_inv is not None`.

#### Fehlerszenarien

| Szenario | Verhalten |
|---|---|
| < 2 Marker im Rohbild | Abbruch, Debug-Bild gespeichert |
| < 2 Marker im entzerrten Bild | Abbruch, `H_inv` bleibt `None` |
| Setup erfolgreich | `H_inv` gesetzt, Ausgabe aller Sanity-Check-Werte |

---

### Methode `warp_image(frame)`

#### Eingabe / Ausgabe

- **Eingabe**: Grayscale-Rohbild
- **Ausgabe**: Entzerrtes Bild der Größe `(self.width, self.height)`

```python
self.img_warped = cv.warpPerspective(frame, self.M_all, (self.width, self.height))
```

---

### Methode `segment_object(frame)`

#### Schwellenwertbasierte Segmentierung

```python
ret, img_thresh = cv.threshold(frame, 210, 255, cv.THRESH_BINARY)
contours, _ = cv.findContours(uint8_img_thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
```

- **Threshold 210**: Nur sehr helle Objekte (Förderbandgüter auf hellem Hintergrund)
- **RETR_EXTERNAL**: Nur äußere Konturen
- **CHAIN_APPROX_NONE**: Alle Konturpunkte gespeichert

#### Rückgabewert
- **Typ**: `tuple` – Liste aller gefundenen Konturen

---

### Methode `get_grippoint(contours, image_shape)`

#### Algorithmus: Distanztransformation

```python
largest = max(contours, key=cv.contourArea)
mask = np.zeros(image_shape[:2], dtype=np.uint8)
cv.drawContours(mask, [largest], -1, 255, thickness=cv.FILLED)
dist = cv.distanceTransform(mask, cv.DIST_L2, 5)
_, _, _, max_loc = cv.minMaxLoc(dist)
```

**Idee**: Das Maximum der Distanztransformation ist der Punkt, der am weitesten von allen Konturrändern entfernt ist – geometrisch der robusteste Greifpunkt.

#### Rückgabewert
- **Erfolg**: `(x, y)` – Pixelkoordinate des Greifpunkts
- **Fehler**: `None` bei leerer Konturliste

---

### Methode `pixel_to_world(pixel)`

#### Koordinatentransformation

```python
pixel_array = np.array([pixel], dtype=np.float32).reshape(-1, 1, 2)
world = cv.perspectiveTransform(pixel_array, self.H_inv)
return world[0, 0]
```

- **Eingabe**: `(x, y)` in Pixel
- **Ausgabe**: `[x, y]` in Metern (Weltkoordinaten)
- **Fehler**: `None` bei `pixel is None`

---

### Methode `extract_features_from_contour(cnt)`

#### Feature-Berechnung

```python
hu_raw = cv.HuMoments(cv.moments(cnt)).flatten()
hu_log = -np.sign(hu_raw) * np.log10(np.abs(hu_raw) + 1e-10)
```

**Logarithmierung**: Hu-Momente spannen viele Größenordnungen – die logarithmierte Form normalisiert sie für den Klassifikator.

**Epsilon `1e-10`**: Verhindert `log(0)` bei sehr kleinen Momenten.

#### Rückgabewert

- **Erfolg**: `{'hu_2': float, 'hu_3': float}`
- **Fehler**: `None` bei Fläche oder Umfang == 0

---

## CoordinatesPrediction – Detaillierte Implementierung

### Konstruktor `__init__()`

#### Initialisierte Instanzvariablen

| Variable | Typ | Init-Wert | Zweck |
|---|---|---|---|
| `buffer_size` | int | 5 | Maximale Anzahl gepufferter Geschwindigkeiten |
| `current_id` | int | None | Aktuelle Objekt-ID |
| `queue` | `deque` | leer | Speichert `(x, t)`-Tupel der aktuellen ID |
| `speed_buffer` | `deque` | leer | Speichert berechnete Einzelgeschwindigkeiten |

---

### Methode `add_measurement(id, x, t)`

#### Eingabe

- **`id`** (int): Objekt-ID
- **`x`** (float): X-Weltkoordinate in Metern
- **`t`** (float): Unix-Zeitstempel in Sekunden

#### Berechnungsschritte

**1. ID-Wechsel erkennen**
```python
if id != self.current_id:
    self.queue.clear()
    self.speed_buffer.clear()
    self.current_id = id
```

**2. Messung eintragen** und auf mindestens 2 Einträge prüfen

**3. Momentangeschwindigkeit berechnen**
```python
speed = (x_curr - x_prev) / (t_curr - t_prev)
```
Bei `t_curr == t_prev` → `None` (Division durch 0 verhindern).

**4. Gleitender Median-Filter**
```python
self.speed_buffer.append(speed)
if len(self.speed_buffer) > self.buffer_size:
    self.speed_buffer.popleft()
smoothed_speed = statistics.median(self.speed_buffer)
```

#### Rückgabewerte

| Szenario | Rückgabe |
|---|---|
| Erste Messung einer ID | `None` |
| Zeitstempel identisch | `None` |
| Erfolg | `{'id': int, 'speed': float}` |

---

## Classifier – Detaillierte Implementierung

### Konstruktor `__init__(buffer_size=5)`

#### Geladenes Modell

```python
model_path = os.path.join(os.path.dirname(__file__), "model", "decision_tree.pkl")
data = joblib.load(model_path)
self.model = data
```

**Modell**: Decision-Tree, trainiert auf logarithmierten Hu-Momenten `hu_2` und `hu_3`.

#### Initialisierte Instanzvariablen

| Variable | Typ | Init-Wert | Zweck |
|---|---|---|---|
| `model` | Decision-Tree | geladen | Klassifikationsmodell |
| `selector` | None | None | Feature-Selektor (optional, derzeit deaktiviert) |
| `all_features` | list | `["hu_2", "hu_3"]` | Feature-Reihenfolge |
| `buffer_size` | int | 5 | Puffergröße für Glättung |
| `current_id` | int | None | Aktuelle Objekt-ID |
| `label_buffer` | `deque` | leer | Gepufferte Einzelvorhersagen |

---

### Methode `classify(id, hu_2, hu_3)`

#### Eingabe

- **`id`** (int): Objekt-ID (Buffer wird bei neuer ID geleert)
- **`hu_2`** (float): Logarithmiertes Hu-Moment
- **`hu_3`** (float): Logarithmiertes Hu-Moment

#### Berechnungsschritte

**1. Feature-DataFrame erstellen**
```python
X = pd.DataFrame([{"hu_2": hu_2, "hu_3": hu_3}])[self.all_features]
```

**2. Vorhersage**
```python
prediction = self.model.predict(X_sel)[0]
confidence = float(self.model.predict_proba(X_sel).max())
```

**3. Label-Mapping** (String → Integer)
```python
label_map = {"rejected": 0, "cat": 1, "unicorn": 2}
```

**4. Median-Glättung**
```python
self.label_buffer.append(prediction)
smoothed_label = int(statistics.median(self.label_buffer))
```

#### Rückgabewert

- **Typ**: `(int, float)` – `(smoothed_label, confidence)`
- **Label**: `0`=rejected, `1`=cat, `2`=unicorn

---

## PostProcessor – Detaillierte Implementierung

### Konstruktor `__init__()`

Initialisiert eine `OrderedDict`-Queue. Die Reihenfolge der Einfügung bestimmt die Verarbeitungsreihenfolge.

---

### Methode `add_obj_type(id, obj_type)`

Fügt den Objekttyp in den Queue-Eintrag ein. ID 0 wird verworfen (entspricht `rejected`-Objekten, die noch nicht vollständig klassifiziert wurden).

```python
self.queue[id]['obj_type'] = obj_type
```

---

### Methode `add_future_position(id, pose2d, speed, timestamp)`

Fügt Pose, Geschwindigkeit und Zeitstempel in den Queue-Eintrag ein. ID 0 wird verworfen.

```python
self.queue[id]['pose2d']     = pose2d
self.queue[id]['speed']      = speed
self.queue[id]['timestamp']  = timestamp
```

---

### Methode `get_next()`

Iteriert über die Queue und gibt das erste vollständig beschriebene Objekt zurück:

```python
if 'obj_type' in data and 'pose2d' in data and 'speed' in data and 'timestamp' in data:
    return self.build_output(id, data)
```

**Vollständigkeitsbedingung**: Alle vier Felder müssen vorhanden sein.

#### Rückgabewert
- **Erfolg**: Ausgabe-Dict von `build_output()`
- **Fehler**: `None`

---

### Methode `finish_obj(id)`

Entfernt ein Objekt aus der Queue:

```python
self.queue.pop(id, None)
```

`pop(..., None)` verhindert eine Exception, wenn die ID bereits entfernt wurde.

---

### Methode `build_output(id, data)`

Berechnet den aktuellen Greifpunkt und gibt das vollständige Ausgabe-Dict zurück:

```python
return {
    'id':         id,
    'obj_type':   obj_type,
    'speed':      data['speed'],
    'grip_point': grip          # {'x', 'y', 'theta'}
}
```

---

### Methode `calculate_current_position(pose2d, timestamp, speed)`

#### Mathematische Grundlage

Das Objekt bewegt sich mit konstanter Geschwindigkeit auf dem Förderband in X-Richtung:

$$x_{aktuell} = x_{gemessen} + v \cdot \Delta t$$

```python
timestamp_diff = time.time() - timestamp
current_x = pose2d.x + speed * timestamp_diff
current_y = pose2d.y  # Y bleibt konstant
```

**Annahme**: Lineare Bewegung, keine Beschleunigung, Y-Koordinate unveränderlich.

#### Rückgabewert

```python
return {'x': current_x, 'y': current_y, 'theta': 0}
```

---

## Message-Definitionen

### ObjCoords

| Feld | Typ | Bedeutung |
|---|---|---|
| `id` | int | Objekt-ID |
| `pose2d` | `geometry_msgs/Pose2D` | Position (x, y) in Metern + Orientierung theta |
| `timestamp` | float | Unix-Zeitstempel der Messung |

### ObjFeatures

| Feld | Typ | Bedeutung |
|---|---|---|
| `id` | int | Objekt-ID |
| `hu_2` | float | Logarithmiertes Hu-Moment hu_2 |
| `hu_3` | float | Logarithmiertes Hu-Moment hu_3 |

### ObjType

| Feld | Typ | Bedeutung |
|---|---|---|
| `id` | int | Objekt-ID |
| `obj_type` | int | 0=rejected, 1=cat, 2=unicorn |

### FuturePosition

| Feld | Typ | Bedeutung |
|---|---|---|
| `id` | int | Objekt-ID |
| `pose2d` | `geometry_msgs/Pose2D` | Aktuelle Position |
| `speed` | float | Geglättete Geschwindigkeit in m/s |
| `timestamp` | float | Unix-Zeitstempel der Positionsmessung |

### ObjData

| Feld | Typ | Bedeutung |
|---|---|---|
| `id` | int | Objekt-ID |
| `obj_typ` | int | Objekttyp (1=cat, 2=unicorn) |
| `point` | `geometry_msgs/Point` | Berechneter Greifpunkt (x, y, z=0) in Metern |
| `obj_speed` | float | Objektgeschwindigkeit in m/s |

---

## Abhängigkeiten und Imports

### Externe Bibliotheken

```python
import cv2 as cv              # OpenCV Hauptbibliothek
from cv2 import aruco         # ArUco-Modul
import numpy as np            # Array-Operationen
import joblib                 # Modell laden (.pkl)
import pandas as pd           # Feature-DataFrame
import statistics             # Median-Berechnung
from collections import deque, OrderedDict
import time                   # Unix-Zeitstempel
```

### ROS2-Interfaces

```python
from chaos_topics.msg import ObjCoords, ObjFeatures, ObjType, FuturePosition, ObjData
from geometry_msgs.msg import Pose2D, Point
from std_msgs.msg import Int16
```

### Konfiguration

```python
import config_vm as cfg  # Enthält: X_MIN_SAFE, X_MAX_SAFE, SRC_COORDS_2
```
