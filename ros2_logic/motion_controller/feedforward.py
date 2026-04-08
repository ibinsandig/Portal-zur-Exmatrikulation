
#****************** Faktor einstellung **************************************************************************************

delta_s = None      
ffw = None          
kp = None           
kd = None           

#****************** Über Interfaces  ****************************************************************************************

goal_pos = None     
curr_pos = None     
last_pos = 0        
excel = None        

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

'''

restpos = goal_pos - curr_pos

mcqueen = (curr_pos - last_pos) / delta_s

excel = kp * restpos + kd * mcqueen + ffw 
