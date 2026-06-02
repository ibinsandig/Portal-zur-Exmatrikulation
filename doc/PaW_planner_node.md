# Planner - Vorverarbeitung der Kameradaten 

## Schnittstellen 

### Subscription 

- /obj_typ [integer typ, time_stemp, integer id] -> 

- /future_position [integer id, time_stemp, geometrie_msg_2D]

- /obj_finished [integer id]

### Published 

- /obj_data []
int8 id
int8 speed
int8 obj_type


## Ablauf

"Main-node bekommt immer nur das nächst mögliche Objekt. Diese Daten werden abgeglichen, bei verwendbarkeit abgearbeitet. Wenn abgearbeitet oder ungültig, ID per Topic zurückmelden. ID wird aus QUEUE gelöscht. Nächstes Objekt wird gesendet und von Main wieder verarbeitet."

Die Erhaltenen Topics aus Vision&ML werden anhand der ID zugeordnet, in die Queue reingeschrieben. 

- Führt die kommenden DAten aus  Future Position und obj type anhand der ID zusammen.
Und Schreibt sie in eine Liste.
-genauso wird das offset zum picken bestimmt
- Derälteste Eintrag bzw. die kleisnte ID wird mit der aktuellen Position(neu berechnet) und dem type und der ID gepublished.
- Nicht gewollte Obj werden herausgefiltert und gelöscht.