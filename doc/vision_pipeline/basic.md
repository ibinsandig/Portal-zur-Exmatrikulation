# Kamera Node
Nimmt ein Bild auf und verarbeitet dieses
Ruft python logic auf preprocessing.py und coord_transformation.py

preprocessing.py
    calibrate():
    *Kalibrierung:* Bei erstmaligem Startup wird einmalig die Funktion aufgerufen. Bei Änderungen der Kamera- oder Förderbandgeometrie ist ein manueller Neustart mit neuer Daten notwendig, um die Homografie-Matrix (H) neu zu bestimmen. ArUco-Marker dienen als primäre Referenz zur Definition der Weltkoordinaten.
    Hierbei wird mithilfe von Homografie ein Bild mit zwei Aruco Markern aufgenommen. Mit denenen dann eine Koordinaten ebene inst Bild gezogen werden kann, sowie auch eine Entzerrung des Bildes. Zur BEstimmung der H MAtrix.
    Aufgrund der ArUco-Marker wird der Bildauschnitt (Region of Interest, ROI) präzise auf das Förderband und die dort platzierten Objekte reduziert.

    Vorverarbeiten:
- Hier wird das vorformatierte Bild (inkl. Timestamp/Frame-Nr.) übergeben.
- Bild wird in Graustufen umgewandelt.
- Optional: Histogramm spreizung (z.B. für bessere Segmentierung).
- Objekte werden mittels klar definierter Segmentierungsverfahren (z.B. Otsu-Thresholding) isoliert.
- Für jedes Objekt wird ein Bounding Box und dessen Schwerpunkt bestimmt.
- Die Zielkoordinate wird mithilfe der Homografie-Matrix berechnet und an coord_pred.py übergeben.
- Ein Objekt erhält basierend auf seiner Bewegung und Koordinate eine zuverlässige, persistente ID (ID Management).
- Die erweiterten Objekt-Merkmale (ObjFeatures) werden extrahiert (Fläche, Formparameter, etc.).

coord_pred.py:
    Hier wird vom BIld koordinatensystem ind WEltkoordiantesystem umgerechnet mit Hilfe der H-MAtrix bei der Kalibrierung


Pub:
ObjCoords: Aktuelle Koordinaten des Objekts in Welt-Koordinaten (inkl. ID, Timestamp).
ObjFeatures: Erweiterte Merkmale des Objekts (z.B. Area, Circularity, Moment).

# Machine Learning Node

Verarbeitet die die Obj FEatures, für eine Aussage über den zusehenden Obj Typ

classify.py:
    Hier werden die übergebenen Features in das trainierte Modell gegeben und ein objTyp dabei bestimmt.

Sub:
    ObjFeatures

Pub:
    ObjType

# Coord Prediction Node

Berechnet die die Geschwindigkeit des Objekts
coord_prediction.py:
    Mit Hilfe mehrerer Positionen des Objekts gleicher ID und des Timestamps wird die Geschwindigkeit bestimmt (Empfehlung: Kalman-Filter zur Rauschminderung). 

Sub:
    ObjCoords

Pub:
    FuturePostion

# Planner Node

Fügt die komenden Inforamtionen wieder zusammen und gibt diese weiter 

postprocessing.py:
    AM Schluss wird mit Hilfer der IDS der ObjType den anderen DAten zu geordnet.

Sub:
    ObjCoords (mit Zeitstempel)
    ObjType (mit Vertrauensscore/Confidence)

Pub:
    ObjData