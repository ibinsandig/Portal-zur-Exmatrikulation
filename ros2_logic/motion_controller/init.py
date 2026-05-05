
import logging

#========================================================
    #Endpunktanfahren Beschleunigung: 
init_accel_x = -0.005
init_accel_y = 0.005
init_accel_z = -0.005   #Bei Z-Positiv nach unten! KEIN ANSCHLAG!

    #Threshhold für Bewegungsabfrage:
th_endlagenabfrage = 0.001

#========================================================
class Init():
    def __init__(self):
        
    #========================================================
    
        self.logger = logging.getLogger("Init")
        logging.basicConfig(level=logging.INFO)

    #========================================================
        self.Xr_ist = 0.0
        self.Yr_ist = 0.0
        self.Zr_ist = 0.0

        self.last_pos_x = 0.0
        self.last_pos_y = 0.0
        self.last_pos_z = 0.0

        self.count_start = 0
        self.count_rise = 0
    #========================================================

        self.counter = 0
        self.endlageerreicht = False
        self.endlagenabfrage = False
        
#================================================================================================================
    def set_init_is_pos(self, Xr_ist, Yr_ist, Zr_ist):    #wird dauerhaft von MotionNode aufgerufen.
        
        self.Xr_ist = Xr_ist
        self.Yr_ist = Yr_ist
        self.Zr_ist = Zr_ist
        
        if self.endlagenabfrage == True:       
            if ((abs(self.last_pos_x - self.Xr_ist) < th_endlagenabfrage) 
                and (abs(self.last_pos_y - self.Yr_ist) < th_endlagenabfrage) 
                and (abs(self.last_pos_z - self.Zr_ist) < th_endlagenabfrage)):  
                self.counter += 1
                self.logger.info(f" [INIT] Counter_endlagenabfrage: {self.counter}")
                if self.counter >= 5:
                    self.endlageerreicht = True
                    self.endlagenabfrage = False

        self.last_pos_x = self.Xr_ist
        self.last_pos_y = self.Yr_ist
        self.last_pos_z = self.Zr_ist
        
#================================================================================================================
    def endpoint_accel_rise(self):
        accel_x = init_accel_x
        accel_y = init_accel_y
        accel_z = init_accel_z
        self.logger.info(f" [INIT] endpoint_accel_rise: {init_accel_x}, {init_accel_y}, {init_accel_z}")
        return accel_x, accel_y, accel_z

    def endpoint_accel_zero(self):
        accel_x = 0.0
        accel_y = 0.0
        accel_z = 0.0
        self.logger.info(f" [INIT] endpoint_accel_zero: {accel_x}, {accel_y}, {accel_z}")
        #self.endlagenabfrage = True 
        return accel_x, accel_y, accel_z
    
#================================================================================================================

    def endablagenabfrage(self):
        self.endlagenabfrage = True

#================================================================================================================

    def endablageerreicht(self):
        return self.endlageerreicht
    
#================================================================================================================

    def offset_calc(self):
        pos_x_offset = self.Xr_ist
        pos_y_offset = self.Yr_ist
        pos_z_offset = self.Zr_ist
        return pos_x_offset, pos_y_offset, pos_z_offset

#================================================================================================================
    def counter_start(self):
        self.count_start += 1
        if self.count_start >= 10:
            self.logger.info(" [INIT] counter_start: ist bei 10 angekommen")
            return True
        return False
    
    def counter_rise(self):
        self.count_rise += 1
        if self.count_rise >= 10:
            self.logger.info(" [INIT] counter_rise: ist bei 10 angekommen")
            return True
        return False

#================================================================================================================
