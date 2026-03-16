# Funktionale Anforderungen

    • Sortierung
    • Rate korrekt sortierter Teile > 90%
    • Rate falsch sortierter Teil < 5%
    • Geschwindigkeit Förderband > 0,01m/s
    • Fail-safemode

# Nicht funktionale Anforderungen

    • Projektplan vor Arbeitsstart
    • Ableitung von Anforderungen schriftlich und abgesprochen mit Stakeholdern
    • Architektur und Designentscheidung aus abgeleiteten Anforderungen
    • Anforderungen müssen getestet werden

# Pflichtmeilensteine
    • Notwendige Koordinatensysteme festgelegt
    • Ausgabe der prädizierten Positionen im definierten Weltkoordinatensytem inkl. Test
    • Regelung auf einen Punkt im definierten Weltkoordinatensystem inkl. Test

# Projektplanung


## Projektplanung vor Arbeitsstart

- Festlegen der Koordinatensysteme [Vorgegebener Meilenstein]
- SW_Architektur
- Kick-Off Präsentation
-
- Grundlegende Hardwareansprache
- ROS-Architektur
-
- Kamera-Modul [ROS-Knoten + Logic]
- Motor-/ Roboteransteuerung [ROS-Knoten + Regler]
- Regelung auf einen Punkt im def. Weltkoor. inkl. Test
-
- Ausgabe der prädizierten Positionen im definierten Weltkoordinatensytem inkl. Test
- Finaler Funktionstest 
- Finale Präsentation vorbereiten 
- Dokumentation fertigstellen  
-
- Vorstellung des Projekts
- Abgabe Doku und Präsentation

## Zeitliche Planung 

| Datum | Besonderheit / ToDo |
|-------|---------------------|
[23.03.26] | Festlegen Koordinatensysteme // SW_Architektur // Rahmenbedingungen festlegen
[30.03.26] | Ausbesserung auf Bäziz des gegivenen Fhädbäcks // Initialisieren des Repos und Ordnerstruktur anhand der SW
[06.04.26] | Kick-Off Präsentation
[13.04.26] | ROS-Struktur für Portalroboter- und Kamera-Modul Knoten
[20.04.26] | 
[27.04.26] | Motor- / Roboteransteuerung (Logic)
[04.05.26] | 
[11.05.26] | Motor- / Roboteransteuerung (Regler)
[18.05.26] | 
[25.05.26] | Pfingsferien - Puff-her für nicht erledigte Meilensteine
[01.06.26] | 
[08.06.26] | 
[15.06.26] | Kamera-Modul (logic)
[22.06.26] | BigBang integration (Gesamttest aller Module)
[29.06.26] | 
[06.07.26] | 
[10.07.26] | Letzer Vorlesungstag // Präsentation und Finale Dokumentation erstellen
[17.07.26] |
[24.07.26] | Finale Präsentation & Abgabe Schriftliche Ausarbeitung




# Physischer Ablauf

- Einlegen des Teils (entweder Katze oder Einhorn)
- Band läuft kontinuierlich 
- Kamera erkennt Bauteil
- SW-KameraModul erkennt ob Katze, Einhorn oder Ausschuss
- Kamera gibt Position zum Greifen. 
- Portalroboter fährt auf die vorhergesagte Postion
- Sauger saugt Teil an und hebt es an (min. höhe sind die Kisten)
- Fährt über passende Kiste und lässt Teil los
- Fährt wieder auf Default-Position

# Wichtige Punkte

## Koordinatensysteme

- Drei Stück. 

> Kamera-Koordinatensystem

> Portalroboter-Koordinatensystem

> Welt-Koordinatensystem



