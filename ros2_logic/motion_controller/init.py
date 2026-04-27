
import logging

#========================================================
    #Endpunktanfahren Beschleunigung: 
init_accel_x = 0.005
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
    def set_rob_is_pos(self, Xr_ist, Yr_ist, Zr_ist):    #wird dauerhaft von MotionNode aufgerufen.
        
        self.Xr_ist = Xr_ist
        self.Yr_ist = Yr_ist
        self.Zr_ist = Zr_ist
        
        if self.endlagenabfrage:        #TODO
            if ((abs(self.last_pos_x - self.Xr_ist) < th) 
                and (abs(self.last_pos_y - self.Yr_ist) < th) 
                and (abs(self.last_pos_z - self.Zr_ist) < th)):  
                self.counter += 1
                if self.counter >= 3:
                    self.endlageerreicht = True
                    self.endlagenabfrage = False

        self.last_pos_x = self.Xr_ist
        self.last_pos_y = self.Yr_ist
        self.last_pos_z = self.Zr_ist
        
#================================================================================================================
    def endpunkt_anfahren(self):
        accel_x = init_accel_x
        accel_y = init_accel_y
        accel_z = init_accel_z
        self.logger.info(f"Endpunkte werden angefahren. Beschleunigung = {init_accel_x}")
        self.endlagenabfrage = True #Solange dieses Flag nicht gesetzt ist, wird die "set_rob_is_pos"-Funktion niemals "self.endlageereicht = True" setzten
        return accel_x, accel_y, accel_z
