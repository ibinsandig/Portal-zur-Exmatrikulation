

#****************** Faktor einstellung **************************************************************************************
   
#gravity_offset = 0.0          
kp = 0.8                #power = mit vollgas losfahren
kd = 1                #dämfen = abbremsen bei näherkommen des Ziels            

#****************** Regler berechnung ***************************************************************************************

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
- Reale Zeitdifferenz für ESP32 verzögerung einrechnen: dass machen wir am besten beim initialisieren über eine Abfrage der aktuellen zeit und sobald die Funktion aufgerufen wird, schauen wir die dann herschende Zeit an und ziehen die voneinander ab. Hier wäre ein Tiefpassfilter möglich bei der Berechnung der Geschwindigkeit (mcqueen) 
-> raw_velocity = (curr_pos - last_pos) / delta_s mcqueen = (alpha * last_velocity) + ((1.0 - alpha) * raw_velocity) # Tiefpassfilter
'''


# class ControllerNe():
#     def __init__(self):
#         #self.gravity_offset = gravity_offset
#         #self.gravity_offset = gravity_offset
#         self.kp = kp
#         self.kd = kd
#         self.last_x_e = 0.0
#         self.last_y_e = 0.0
#         self.last_z_e = 0.0 
#         self.first_x = True
#         self.first_y = True
#         self.first_z = True

# # eher eine Funktion als 3 - also hier eher 3 mal instanzieren als 3 einzelne funktionen aufrufen.
# # Die self.Variablen sollten HIER und nicht in Move_logic sein.

#     def controller_x_axes(self, goal_pos, curr_pos, last_pos, delta_t):

#         restpos = goal_pos - curr_pos

#         if self.first_x:
#             mcqueen = 0.0
#             self.first_x = False
#         else:
#             mcqueen = (restpos - self.last_x_e) / delta_t

#         self.last_x_e = restpos

#         excel = self.kp * restpos - self.kd * mcqueen

#         return excel



#     def controller_y_axes(self, goal_pos, curr_pos, last_pos, delta_t):
        
#         restpos = goal_pos - curr_pos

#         mcqueen = (curr_pos - last_pos) / delta_t

#         excel = self.kp * restpos - self.kd * mcqueen

#         return excel



#     def controller_z_axes(self, goal_pos, curr_pos, last_pos, delta_t):

#         restpos = goal_pos - curr_pos

#         mcqueen = (curr_pos - last_pos) / delta_t

#         excel = self.kp * restpos - self.kd * mcqueen

#         return excel

class Controller():
    def __init__(self, kp, kd):
        self.last_error = 0.0
        self.first = True
        self.kp = kp
        self.kd = kd

    def compute(self, goal_pos, curr_pos, delta_t):
        restpos = goal_pos - curr_pos

        if self.first:
            mcqueen = 0.0
            self.first = False
        else:
            mcqueen = (restpos - self.last_error) / delta_t

        self.last_error = restpos

        excel = self.kp * restpos - self.kd * mcqueen

        return excel

'''
Alternative:
- c(S) = kp + kd * (s/Tf*s+1) 

Regler in Matlab auslegen.
'''

