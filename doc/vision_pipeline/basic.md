# Kamera Node
Nimmt ein Bild auf und verarbeitet dieses
Ruft python logic auf preprocessing.py und coord_transformation.py

Pub:
    ObjCoords
    ObjFeatures

# Machine Learning Node

Verarbeitet die die Obj FEatures, für eine Aussage über den zusehenden Obj Typ
Ruft classify.py auf

Sub:
    ObjFeatures

Pub:
    ObjType

# Coord Prediction Node

Berechnet die die Geschwindigkeit des Objekts
Ruft coord_prediction.py auf

Sub:
    ObjCoords

Pub:
    FuturePostion

# Planner Node

Fügt die komenden Inforamtionen wieder zusammen und gibt diese weiter 
Ruft PostProcessing auf

Sub:
    FuturePostion
    ObjType

Pub:
    ObjData