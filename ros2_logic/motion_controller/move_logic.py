'''
 Wichtige Punkte, die noch überdacht werden müssen:
    - [def should_is_comp] Wie gehen wir damit um, wenn die IST_WERTE mit extrem wankenden Nachkommastellen ankommen, unsere SOLL aber nur ganzzahlen sind?

'''



Class MotionOrder():
'''
    Grober Funktionsablauf:
    - IST-Daten werden dauerhaft aktuallisiert (max.20Hz)
    - Soll-Daten kommen rein (goal_data)
    - Werden mit Ist-Daten verglichen
        IF (IST == SOLL) {Rückmeldung -> Zielstatus: job_finished = true}
        ELSE
        - Rufe "ffw_controller" für jede einzelne Achse auf und berechne a
        - versende die Daten über "send_it_accel" an den Roboter
        - if (IST != SOLL) {THROW NE EXEPTION} [TODO: hier könnte man ein erneuten anfahrversuch machen, in einer Schleife]
            ELSE {def send_state(self, state) = true publishen}
'''


    def __init__(self): 
        self.Xr_ist
        self.Yr_ist
        self.Zr_ist

        self.Xr_soll
        self.Yr_soll
        self.Zr_soll
        self.gripper_soll

    def getter_is_pos(Xr_ist, Yr_ist, Zr_ist):
        self.Xr_ist = Xr_ist
        self.Yr_ist = Yr_ist
        self.Zr_ist = Zr_ist
        return True

    def getter_should_pos(Xr_soll, Yr_soll, Zr_soll, gripper_soll)
        self.Xr_soll = Xr_soll
        self.Yr_soll = Yr_soll
        self.Zr_soll = Zr_soll
        self.gripper_soll = gripper_soll

    
    def should_is_comp():                           
        if (self.Xr_ist == self.Xr_soll and self.Yr_ist == self.Yr_soll and self.Zr_ist == self.Zr_soll){
            return True
        }
        else  { 
            return False
        }

