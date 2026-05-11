from motion_controller.feedforward import Controller
import logging
import time

#=============================================================

# Soll ist Vergleich Schwellwert: 

th_move_logic= 0.0001

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

        self.Xr_ist = 0.0
        self.Yr_ist = 0.0
        self.Zr_ist = 0.0

        self.Xr_soll = 0.0 
        self.Yr_soll = 0.0
        self.Zr_soll = 0.0

        self.last_pos_x = 0.0
        self.last_pos_y = 0.0
        self.last_pos_z = 0.0

        self.time_stamp = None
        self.last_time_stamp = None
        self.time_step = 0.1

        self.controller_x = Controller(0.5,0.5)
        self.controller_y = Controller(0.5,0.5)
        self.controller_z = Controller(0.5,0.5)


    
    def set_is_pos(self, Xr_ist, Yr_ist, Zr_ist):    
        self.Xr_ist = Xr_ist
        self.Yr_ist = Yr_ist
        self.Zr_ist = Zr_ist
        self.logger.info("[Motion]: MotionOrder: set_is_pos")
        self.time_step_calc()
        return True

    def set_should_pos(self, Xr_soll, Yr_soll, Zr_soll): 
        self.Xr_soll = Xr_soll
        self.Yr_soll = Yr_soll
        self.Zr_soll = Zr_soll
        self.logger.info("[Motion]: MotionOrder: setter_should_pos")
        return True

    
    def should_is_comp(self):                                
        if (abs(self.Xr_ist - self.Xr_soll) < th_move_logic
            and abs(self.Yr_ist - self.Yr_soll) < th_move_logic 
            and abs(self.Zr_ist - self.Zr_soll) < th_move_logic): 
            self.logger.info(f" [Motion]: Ist - Soll vergleich in Toleranz {th_move_logic}")
            return True
        else: 
            self.logger.info(" [Motion]: Ist-soll-Vergleich - keine Übereinstimmung!")
            return False
    
    def time_step_calc(self):
        self.time_stamp = time.time()

        if self.last_time_stamp == None:
            self.time_step = 0.1
            self.last_time_stamp = self.time_stamp
            return True
        
        else:
            self.time_step = abs(self.time_stamp - self.last_time_stamp)
            self.last_time_stamp = self.time_stamp
            return True
    

    
    def wanted_accel(self):
    
        accelofx = self.controller_x.compute(self.Xr_soll, self.Xr_ist, self.time_step)         
        accelofy = self.controller_y.compute(self.Yr_soll, self.Yr_ist, self.time_step)
        accelofz = self.controller_z.compute(self.Zr_soll, self.Zr_ist, self.time_step)
        

        self.logger.info(f" [Motion]: wanted_accel: x,y,z berechnet {accelofx, accelofy, accelofz }")

        return accelofx, accelofy, accelofz