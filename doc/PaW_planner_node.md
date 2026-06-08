# Planner - Vorverarbeitung der Kameradaten 

## Schnittstellen 

### Subscription 

- /obj_typ [integer typ, time_stemp, integer id] -> 

- /future_position [integer id, time_stemp, geometrie_msg_2D]

- /obj_finished [integer id]

### Published 

- /obj_data [
int8 id
int8 obj_type 
geometry_msg_2D (x,y,theta)
]


## Ablauf

"Main-node bekommt immer nur das nächst mögliche Objekt. Diese Daten werden abgeglichen, bei verwendbarkeit abgearbeitet. Wenn abgearbeitet oder ungültig, ID per Topic zurückmelden. ID wird aus QUEUE gelöscht. Nächstes Objekt wird gesendet und von Main wieder verarbeitet."

Die Erhaltenen Topics aus Vision&ML werden anhand der ID zugeordnet, in die Queue reingeschrieben. 

- Führt die kommenden DAten aus  Future Position und obj type anhand der ID zusammen.
Und Schreibt sie in eine Liste.
-genauso wird das offset zum picken bestimmt
- Derälteste Eintrag bzw. die kleisnte ID wird mit der aktuellen Position(neu berechnet) und dem type und der ID gepublished.
- Nicht gewollte Obj werden herausgefiltert und gelöscht.

!!!! >>> Auch für die Zeitliche Berechnung zuständig!. Kurz um: Erfasste Objekte werden in die Queue gelegt. 
                                                                Und dann das Erste per Timer genommen, berechnet,
                                                                verworfen oder eben an die Mainy weitergegeben.
                                                                (Mainy macht immer nur einen Auftrag fertig!, und nutzt
                                                                dafür die bekommenen koordinaten ohne berechnungen!!!!)
                                                                Hier nicht vergessen, eine Justier-Variable für die Zeit-
                                                                berechnung einzubauen!


TODO's: 

Thema Weltcoordinatensystem [TCP Punkt muss als TCP_OFFSET auf die Welt-Robot-Koordinatensystem]
Thmea Punktabarbeiten [dauerhaftes PUNKT übergeben?, oder Zeitvorrechnen und Punktübergeben]