
import logging

#========================================================
    #Endpunktanfahren Beschleunigung: 
init_accel_x = -0.005
init_accel_y = 0.005
init_accel_z = -0.005   #Bei Z-Positiv nach unten! KEIN ANSCHLAG!

    #Threshhold für Bewegungsabfrage:
th = 0.001

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
    #========================================================

        self.counter = 0
        self.endlageerreicht = False
        self.endlagenabfrage = False
        
#================================================================================================================
    def set_init_is_pos(self, Xr_ist, Yr_ist, Zr_ist):    #wird dauerhaft von MotionNode aufgerufen.
        
        self.Xr_ist = Xr_ist
        self.Yr_ist = Yr_ist
        self.Zr_ist = Zr_ist
        
        if self.endlagenabfrage:        #TODO th besser bennen
            if ((abs(self.last_pos_x - self.Xr_ist) < th) 
                and (abs(self.last_pos_y - self.Yr_ist) < th) 
                and (abs(self.last_pos_z - self.Zr_ist) < th)):  
                self.counter += 1
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
        self.logger.info(f"Kurze Beschleunigung Richtung Endpunkt. Beschleunigung = {init_accel_x}")
        self.endlagenabfrage = True #TODO: FÜr den fall das das Anfahren zu lange dauert und die Endlagenabfrage ungewollt 3 mal hoch zählt --> Variable erst in accel_zero auf TRUE setzen!
        return accel_x, accel_y, accel_z

    def endpoint_accel_zero(self):
        accel_x = 0.0
        accel_y = 0.0
        accel_z = 0.0
        self.logger.info(f"Beschleunigung Richtung Endpunkte beenden. Beschleunigung = {init_accel_x}")
        #self.endlagenabfrage = True 
        return accel_x, accel_y, accel_z
    
#================================================================================================================

    def endablageerreicht(self):
        return self.endlageerreicht
    
#================================================================================================================

    def offset_calc(self):
        pos_x_offset = self.Xr_ist
        pos_y_offset = self.Yr_ist
        pos_z_offset = self.Zr_ist
        return pos_x_offset, pos_y_offset, pos_z_offset

