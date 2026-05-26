

'''
Berechnung des Pseudo-PD Reglers (auch Feedforward)
"Grundlegend wird der Störfaktor im Vorhinhein geschätzt und mit in den Regler ADDIERT"

1. Fehlerberechnung
2. Geschwindigkeit über letzte Position errechnen (D-Anteil)
3. beschleunigung mit feedforward

delta_s =      Eingestellte Zeit zwischen zwei Reglerdurchläufen ( basicly die timer_callback zeit?  ~ über callback2 -> 20hz)
ffw =          Feedforward - Statischer Wert, der zur kompensation von Außeneinflüssen ist. Ist hier hauptsächlich für die Z-Achse interessant. 
kp =           Faktor für Proportionalwert (Für die Beschleunigung. Je weiter weg, desto schneller fahren wir an)
kd =           Faktor für Differentialwert (Je schneller wir uns dem Ziel nähern, desto mehr bremsen wir)

goal_pos =     Zielposition des Roboters 
curr_pos =     Akutelle von /RobotPos gegebene Position
last_pos =     Letze bekannte Position. Bei Start, mit 0 initialisiert!
excel =        Berechnete beschleunigung 


TODO: Optimierungsbedarf:  
-> raw_velocity = (curr_pos - last_pos) / delta_s mcqueen = (alpha * last_velocity) + ((1.0 - alpha) * raw_velocity) # Tiefpassfilter
'''



class Controller():
    def __init__(self, kp, kd):
        self.last_error = 0.0
        self.first = True
        self.kp = kp
        self.kd = kd

    def compute(self, goal_pos, curr_pos, delta_t):
        error = goal_pos - curr_pos

        if self.first:
            speed = 0.0
            self.first = False
        else:
            speed = (error - self.last_error) / delta_t

        self.last_error = error

        accel = self.kp * error + self.kd * speed

        return accel
'''
Alternative:
- c(S) = kp + kd * (s/Tf*s+1) 

Regler in Matlab auslegen.
'''

