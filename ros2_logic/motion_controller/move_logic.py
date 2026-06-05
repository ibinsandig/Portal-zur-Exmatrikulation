from motion_controller.controller import Controller
import logging
import time

#=============================================================

# Soll ist Vergleich Schwellwert: 

th_move_logic= 0.0005    #TODO WEgen der Z-AChse (die war bei abs(0.00014))

#=============================================================

class MotionOrder():

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

        self.controller_x = Controller(3.0,5.5) 
        self.controller_y = Controller(3.0,6.0)
        self.controller_z = Controller(3.0,6.5)


    
    def set_is_pos(self, Xr_ist, Yr_ist, Zr_ist):    
        '''
        Setzt die aktuelle Ist_Position des Roboters. 
        Nimmt einen TimeStamp beim erhalten der Daten an. Relevant für den Regler.
        '''
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
        '''
        Vergleicht den aktuellen Positionswert jeder einzelnen Achse mit dem Zielwert unter beachtung eines Schwellwerts.
        '''

        if (abs(self.Xr_ist - self.Xr_soll) < th_move_logic
            and abs(self.Yr_ist - self.Yr_soll) < th_move_logic 
            and abs(self.Zr_ist - self.Zr_soll) < th_move_logic): 
            self.logger.info(f" [Motion]: Ist - Soll vergleich in Toleranz {th_move_logic}")
            return True
        else: 
            self.logger.info(f"SOll=!IST, x:{abs(self.Xr_ist - self.Xr_soll)}, y:{abs(self.Yr_ist - self.Yr_soll)} ,z:{abs(self.Zr_ist - self.Zr_soll)}")
            return False
    
    def time_step_calc(self):
        '''
        Errechnet die vergangene Zeit zwischen dem aktuellen Positionswert und dem letzten Positonswert. 
        Beim ersten Druchgang wird ein Schätzwert von 0.1 Sekunden genommen.
        '''
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
        '''
        Berechnung der Beschleunigungswerte der einzelnen Achsen.

        Eine für jede einzelne Achse bereits erstellte Instanz wird aufgerufen und die aktuellen Soll-, Ist- und Zeitwerte werden übergeben.
        Die Werte kd und kp sind bei der instanzierung für jede Achse individuell bereits übergeben.
        '''
    
        accelofx = self.controller_x.compute(self.Xr_soll, self.Xr_ist, self.time_step)         
        accelofy = self.controller_y.compute(self.Yr_soll, self.Yr_ist, self.time_step)
        accelofz = self.controller_z.compute(self.Zr_soll, self.Zr_ist, self.time_step)
        

        self.logger.info(f" [Motion]: wanted_accel: x,y,z berechnet {accelofx, accelofy, accelofz }")

        return accelofx, accelofy, accelofz