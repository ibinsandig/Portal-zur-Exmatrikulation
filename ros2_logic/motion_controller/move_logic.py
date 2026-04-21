from motion_controller.feedforward import ffw_controller #Bei problemen hier nur "from .feedforward import ffw_controller" schreiben
import logging

#=============================================================

# Soll ist Vergleich Schwellwert: 

th = 0.2

#=============================================================

class MotionOrder():

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

        self.logger = logging.getLogger("MotionOrder")
        logging.basicConfig(level=logging.INFO)

        self.logger.info("MotionOrder aufgerufen!")

        self.Xr_ist = 0.0
        self.Yr_ist = 0.0
        self.Zr_ist = 0.0

        self.Xr_soll = 0.0 
        self.Yr_soll = 0.0
        self.Zr_soll = 0.0

        self.last_pos_x = 0.0
        self.last_pos_y = 0.0
        self.last_pos_z = 0.0

    
    def set_is_pos(self, Xr_ist, Yr_ist, Zr_ist):    
        self.Xr_ist = Xr_ist
        self.Yr_ist = Yr_ist
        self.Zr_ist = Zr_ist
        #TODO: Offset von INIT muss hier mit eingerechnet werden! Sonst fahren wir mit den Rando-hardware-koordinaten vom Roboter und nicht von unserem genullten Roboter-Koordinatensystem!
        self.logger.info("setter_is_pos: Ist-Pos wurd in Logic geladen und mit Offset addiert!")
        return True

    def set_should_pos(self, Xr_soll, Yr_soll, Zr_soll): 
        self.Xr_soll = Xr_soll
        self.Yr_soll = Yr_soll
        self.Zr_soll = Zr_soll
        self.logger.info("setter_should_pos: Soll Pos ist in Logic geladen!")
        return True

    
    def should_is_comp(self):                                    
        if abs(self.Xr_ist - self.Xr_soll) < th and abs(self.Yr_ist - self.Yr_soll) < th and abs(self.Zr_ist - self.Zr_soll) < th: 
            self.logger.info("comparrer: Ist - Soll vergleich ist unter der Toleranz (< 0.2)")
            return True
        else: 
            self.logger.info("comparrer: Ist-SOll vergleich hat keine Übereinstimmung festgestellt!")
            return False
        
    
    def wanted_accel(self):
    
        accelofx = ffw_controller(self.Xr_soll, self.Xr_ist, self.last_pos_x)
        self.last_pos_x = self.Xr_ist             
        accelofy = ffw_controller(self.Yr_soll, self.Yr_ist, self.last_pos_y)
        self.last_pos_y = self.Yr_ist
        accelofz = ffw_controller(self.Zr_soll, self.Zr_ist, self.last_pos_z)
        self.last_pos_z = self.Zr_ist

        self.logger.info("wanted_accel: x,y,z beschleunigung sind berechnet worden")

        return accelofx, accelofy, accelofz