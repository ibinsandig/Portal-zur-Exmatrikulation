# Regler auslegung zum Ansteuern der Motoren des Portalroboters

## Planung und erste gedankengänge

**PDF-Regler**

Der PDF (Pseudo-Derivative-Feedback) Regler eignet sich gut für beschleunigungsbasierte Ansteuerung. 
Er verlagert die Differenzelemnt (D-Anteil) in die Rückführung und reagiert so extrem stabil auf abrupte Beschleunigungsänderungen, ohne das das System stark zum Schwingen gebracht wird. 

Es handelt sich um ein PT2-Strecvkenmodell (weil wir zweimal integrieren: Beschleunigung -> Geschwindigkeit -> Position)

*Warum PDF statt PID bei Beschleunigungsvorgaben?*

Sanfteres Anlaufen: Da der P-Anteil nicht direkt auf den Sollwertsprung wirkt (kein "Proportional Kick"), folgt der Motor der Beschleunigungsrampe wesentlich sauberer.
Störunterdrückung: Er verhält sich extrem robust gegenüber Lastwechseln, was bei Robotern (z. B. wechselnder Untergrund oder Gewicht) entscheidend ist.


## Zweite Version (auch Programmtechnisch umgesetzt)

Regler als Funktion in eigener Datei ausgelagert:

**def ffw_controller()**

**Mitzugebende Variablen:**
- goal_pos (zielposition, von mainy)
- curr_pos (aktuelle Position, von /RoboPos)
- last_pos (vorherige Position, bei start einfach 0)

**Zurückgegebener Wert:**
- beschleunigung des jeweiligen Motors


FeedForWard Regler 
```
def ffw_controller(goal_pos, curr_pos, last_pos):
    restpos = goal_pos - curr_pos
    excel = kp * restpos - kd * mcqueen + ffw 
    return excel 
```
Zur Faktor Einstellung: 
```
delta_t = None      
ffw = None          
kp = None           
kd = None 

```

---
---

#  Motion Node

## Publisher Logic

### Warum die MSG deklaration (Zeile 29 & 30) in der Init?

>        self.robot_cmd = RobotCmd()
>        self.goal_state = GoalState()
*So bleiben die Informationen bis zum erneuten Funktionsaufruf in der Instanzvariable erhalten! 

### Alternative Version:

Die Declaration wird in die Funktion geschrieben.
Hier werden die Informationen immer nach Ende der Funktion gelöscht!

```
def send_it_accel(self,x,y,z,picky):
    msg = RobotCmd()
    msg.accel_x = x
    msg.accel_y = y
    msg.accel_z = z 
    msg.activate_gripper = picky
    self.publisher_cmd.publish(msg)
```

# TODO 

- Greifer Logic umsetzten [Prio: NIEDRIG]
- PHYSISCH AUF Defaultpunkt fahren [PRIO: HIGH]
- Regler auslegen  [PRIO: EXORBITANT]

