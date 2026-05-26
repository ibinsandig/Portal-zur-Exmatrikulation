# Regler auslegung zum Ansteuern der Motoren des Portalroboters

## Zweite Version (auch Programmtechnisch umgesetzt)

Regler als Funktion in eigener Klasse ausgelagert:

**class Controller()**

Mitzugebende Variablen beim Instanzieren:
- kp (Wert für den Proportional Anteil)
- kd (Wert für den derivativ-Anteil)

**def compute()**

Mitzugebende Variablen beim Instanzieren:
- goal_pos (zielposition, von mainy)
- curr_pos (aktuelle Position, von /RoboPos)
- delta_t (Zeitabstand zwischen den letzten Zwei Positionen)

**Zurückgegebener Wert:**
- beschleunigung



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

- Greifer Logic umsetzten [Prio: TEST]

- PHYSISCH AUF Defaultpunkt fahren [Prio: Mid]
- Regler optimieren [Prio: Mid]
- Problem mit Y_Achse verfahren beheben [Prio: HIGH]
- DocStrings im Code erweitern [Prio: Low]

