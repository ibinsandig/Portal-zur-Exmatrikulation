
#=============================================================================

class MainyLogic():
    def __init__(self):
        
        self.obj_id =  0                   #TODO2 Hier definieren 0 ist systembelegt (nicht für objekte)  
        self.obj_id_prev = 99999999                  
        self.obj_typ = 0                    # 0 ist "NICHT ERKANNT"
        self.obj_coord_x = None
        self.obj_coord_y = None
        self.obj_coord_z_up = 0.07          
        self.obj_coord_z_down = 0.099       
        self.obj_speed = None               

        self.obj_coord_x_extrapolated = 0.0
        self.obj_time_last_cam_msg = None

        self.obj_coord_z_mid = 0.085        

        self.coord_x_default = 0.15
        self.coord_y_default = -0.08

        self.coord_x_sort_unicorn = 0.20    #TODO Muss noch bestimmt werden (praktisches Annähern)
        self.coord_y_sort_unicorn = -0.12    #2

        self.coord_x_sort_cat = 0.015        #TODO
        self.coord_y_sort_cat = -0.12        #1

        self.init_done = False
        self.auftrag = False
        self.goal_reached = False
        self.work_done = False
        self.goal_reached_previous = False
        self.goal_reached_rising = False


        self.state = "jobless"

    #================================================================================================================

    def init_abfrage(self, init_done):
        self.init_done = init_done
    
    #================================================================================================================

    def auftragseingang_main(self, obj_id): 
        '''
        Prüft ob ein neues Objket mit neuer ID von PlannerNode kommt und startet ggf. die Statemachine. Setzt die WorkDone Flag auf False. 
        '''
        self.obj_id = obj_id

        if self.obj_id is not self.obj_id_prev:   
            self.obj_id_prev = obj_id
            self.state = 'obj_pick_pre_pos'
            self.work_done = False
    
    #================================================================================================================

    def obj_current_pos(self, obj_typ, obj_coord_x, obj_coord_y, obj_speed):

        self.obj_typ = obj_typ 
        self.obj_coord_x = obj_coord_x
        self.obj_coord_y = obj_coord_y
        self.obj_speed = obj_speed

#================================================================================================================

    def flankenerkennung(self, current_goal_reached):
        '''
        Goal_reached gilt nur als True, wenn wir von einer Steigenden Flanke sprechen. 
        '''
        self.goal_reached_rising = current_goal_reached and not self.goal_reached_previous
        
        self.goal_reached_previous = current_goal_reached   
   
    def goal_reached_flag(self, goal_reached):
        self.flankenerkennung(goal_reached)
#================================================================================================================

    def work_done_flag(self):
        return self.work_done, self.obj_id
    
#================================================================================================================

    def extrapolation(self, zeit_jetzt):    
        '''
        Extrapolation wird nun über die Eingehenden OJK Daten getriggert. (Diese kommen allerdigns eh von einem timer_callback aus der PlannerNode)
        '''
        if self.obj_coord_x is None or self.obj_speed is None:
            print("Extrapolation: Keine X-Coordinate, Keine Geschwindigkeit!")
            return
    
        if self.obj_time_last_cam_msg is None:
            self.obj_time_last_cam_msg = zeit_jetzt
            return
    
        vergangene_zeit = zeit_jetzt - self.obj_time_last_cam_msg


        self.obj_coord_x_extrapolated = self.obj_coord_x + self.obj_speed * vergangene_zeit

        self.obj_time_last_cam_msg = zeit_jetzt


#================================================================================================================

    def state_machine(self):
        
        if not self.init_done:
            print("Fehlende Init, Publisher für aktuellen Zyklus geblockt")
            return self.coord_x_default,self.coord_y_default,self.obj_coord_z_up,False,False
        
        if self.state == 'jobless':
            print("State_machine ist Jobless, Publisher für aktuellen Zyklus geblockt")
            self.work_done = False
            return self.coord_x_default,self.coord_y_default,self.obj_coord_z_up,False,False




        #=======================Pick_Prozess-Start==========================

        if self.state == "obj_pick_pre_pos":    
            #Anfahren der zweiten Vorposition in Y und Z. X noch in Default lassen. In dieser Zeit bekommen wir zwei DatenPuntke für die Extrapolation.

            if self.goal_reached_rising == True:
                self.state = "obj_pick_up" 
            
            print(f"State: {self.state}: Zielpos Y, sowie x_default voranfahren")
            return self.coord_x_default, self.obj_coord_y, self.obj_coord_z_mid, True, True
        
        #=================================================

        if self.state == "obj_pick_up":
            # Abfrage ob, das Baueil bereits unter uns durch gefahren ist.

            if self.coord_x_default >= self.obj_coord_x:
                
                self.state = "obj_default_pos_grip"

                print(f"State: {self.state}: Wenn Bauteil unter x_default durch gefahren ist, picke auf x_extrapolated")
                return self.obj_coord_x_extrapolated, self.obj_coord_y, self.obj_coord_z_down, True, True
    
            else:
                print(f"State: {self.state} x_default >= ist_obj_coord_x, Solange wird auf xdefault gefahren!")
                return self.coord_x_default, self.obj_coord_y, self.obj_coord_z_mid, True, True
            
        #=================================================

        elif self.state == "obj_default_pos_grip":

            if self.goal_reached_rising == True: 
                self.state = "obj_sort"

            print(f"State: {self.state}")
            return self.obj_coord_x_extrapolated, self.coord_y_default, self.obj_coord_z_up, True, True


        #====================Pick_Prozess-Ende=============================


        elif self.state == "obj_sort":

            if self.goal_reached_rising == True:
                self.state = "obj_drop"

            if self.obj_typ == 2: #TODO Umbenennung von Zahl auf String           
                print(f"State: {self.state}")
                return self.coord_x_sort_unicorn, self.coord_y_sort_unicorn, self.obj_coord_z_up, True, True
            
            if self.obj_typ == 1:               
                print(f"State: {self.state}")
                return self.coord_x_sort_cat, self.coord_y_sort_cat, self.obj_coord_z_up, True, True


        elif self.state == "obj_drop":
            
            self.state = 'obj_default_pos_lose'

            if self.obj_typ == 2: 
                print(f"State: {self.state}")      
                return self.coord_x_sort_unicorn, self.coord_y_sort_unicorn, self.obj_coord_z_up, False, True
        
            if self.obj_typ == 1: 
                print(f"State: {self.state}")              
                return self.coord_x_sort_cat, self.coord_y_sort_cat, self.obj_coord_z_up, False, True
            

        elif self.state == "obj_default_pos_lose":

            if self.goal_reached_rising == True:        
                self.state = 'jobless'         

            self.work_done = True 
            print(f"State: {self.state}")
            return self.coord_x_default, self.coord_y_default, self.obj_coord_z_up, False, True
        
        #=================================================

        else:
            print(f"Unbekannter State: {self.state} ")
            return self.coord_x_default,self.coord_y_default,self.obj_coord_z_up,False,False

#================================================================================================================

