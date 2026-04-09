# Beschreibung der einzelnen Nodes

## motion (controller)

[SerialMapping]
sendet an motion: Roboterpositionsdaten (float Xr_ist, float Yr_ist, float Zr_ist, Bool greifer_ist)
bekommt von motion: Achsbeschleunigung (float Xa, float Ya, float Za, Bool greifer)

[main_node]
sendet an motion: Zieldaten (float Xr_soll, float Yr_soll, float Zr_soll, Bool greifer_soll)
bekommt von motion: Zielstatus (Bool job_fineshed)

[Motion_NODE]

'''
Motion bekommt grundlegned nur einen Punkt im RKS zum Anfahren. Regelt dort hin und meldet sich zurück ob der Punkt erreicht wurde oder nicht. 
'''

- Fragen dauerhaft nach Zieldaten
- Empfangen die aktuelle Positon des Robis
- Bei erhalt von neuen Zieldaten (Roboterkoordinaten), soll er diese Anfahren
- Überprüfen durch akutelle Roboter_ist_positon, ob wir das Ziel erreicht haben (evt sicherung durch Abschalten nach zu langer Zeit nicht erreichen)
- Rückmeldung an main_node über bool job_finished


## mainy_node

[Vorgedanke für init]: Roboter fährt an endanschläge um dort die 0,0,0 Position zu definieren/initialisieren

[machinelearning]
sendet an mainy: data_deluxe (int32 obj_type, float32 X_world, float32 Y_world, float32 Z_world)

[motion]
sendet an mainy:  Zielstatus (Bool job_fineshed)
empfängt von mainy: Zieldaten (float Xr_soll, float Yr_soll, float Zr_soll, Bool greifer_soll)

- Fragen nach reinkommenden Cam_delux_daten 
- Wenn neue Daten kommen: Umrechung WKS in RKS 
- Switch-Case entscheidung je nach Bauteil (katze, Einhorn, aussschuss), entscheidet den Endpunkt
- Schickt die Zieldaten von Visionblock im RKS an motion (bool true)
- $Motion führt die Bewegung bis zum "pick"$
- goalstate sendet ein Truen (angekommen)
- Schicken Zieldaten vom Switch-Case (katze, einhorn) im RKS an motion (bool true)
- goalstate sendet ein True (angekommen)
- schicken SELBE ZIELDATEN des Switch-Case im RKS an motin (ABER mit bool false)
- (nach einer kurzen Zeit, nach bool flase): schicken wir die RKS-Daten zum Anfahren des Default punktes / DIREKT zum nächstgeschickten Bauteil

## machine learning Node

[Kamera Node]
sendet an machinlearning: objektData (x_world, y_world, z_world, (Objekt_Daten))

- Nehmen Objektdaten zum füttern des Machinelearning -> bekommen Typ (katze, einhorn, 67)
- gibt Typ und predicted_world_coordinates weiter an mainy

## Kamera Node

- Bild wird vorverarbeitet (Numpy-arry in Grauwerten)
- Warpen des Bildes (verzehren zur planaren Ebene zum Fließband)
- Segmentierung und herrausziehen der einzelnen Objektdaten 
- Koordinatenprediction 
- Coordiatentransformation von KKS zu WKS 