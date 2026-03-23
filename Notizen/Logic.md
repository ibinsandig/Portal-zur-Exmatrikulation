# Mainlogic und Software_Architektur

## Kamerablock

1. Kamera bekommt bild 
2. Kamera preprocessed Bild (Graustufen, entrauschen)
3. Machinevision erkennt und Identifiziert objekt (katze oder Einhörn)
4. Machinvision berechnet Koordinaten im Welt-Koordinatensystem (Wo objekt in Bildaufnahme ist)
5. Daten werden als CustomMessage per /obj_data topic gepublished (type, pos, speed)

## Mainblock

main_node subscribed /obj_data 

main_node subsribed /RobotPos 

main_node published /RobotCmd 

**kommuniziert mit main_logic**

main_logic dient als Statemachine

- Beim Hochfahren des Systems wird die **Init** aufgerufen.
    - Roboter faehrt Achsen auf Endanschlag 
    - Nullpunkt wird gesetzt 
    - Kamera wird hochgefahren/angeschaltet
- Sprung in main-loop
- Abfrage, Objekt gefunden? (schleife bis TRUE)
- Sprung in **pick** 
    - Achsen X und Y fahren auf prediktete Postion 
    - Z fährt auf endposition (kurz über Band, band = 0 + höhe der Chips/Bauteile)
    - 

