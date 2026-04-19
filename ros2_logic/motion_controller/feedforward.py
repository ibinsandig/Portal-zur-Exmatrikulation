
#****************** Faktor einstellung **************************************************************************************

delta_t = None      
ffw = None          
kp = None           
kd = None                        

#****************** Regler berechnung ***************************************************************************************

'''
Berechnung des Pseudo-PD Reglers (auch Feedforward)
"Grundlegend wird der Störfaktor im Vorhinhein geschätzt und mit in den Regler ADDIERT"

1. Fehlerberechnung
2. Geschwindigkeit über letzte Position errechnen (D-Anteil)
3. beschleunigung mit feedforward

delta_s =      Eingestellte Zeit zwischen zwei Reglerdurchläufen ( basicly die timer_callback zeit?)
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

def ffw_controller(goal_pos, curr_pos, last_pos):

    restpos = goal_pos - curr_pos
    mcqueen = (curr_pos - last_pos) / delta_t
    excel = kp * restpos - kd * mcqueen + ffw 

    return excel


'''
Alternative:
- c(S) = kp + kd * (s/Tf*s+1) 

Regler in Matlab auslegen.
'''

