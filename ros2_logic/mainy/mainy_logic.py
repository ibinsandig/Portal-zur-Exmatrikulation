
#=============================================================================

class MainyLogic():
    def __init__(self):
        
        self.obj_id =  0                   #TODO2 Hier definieren 0 ist systembelegt (nicht für objekte)                    
        self.obj_typ = 0                    # 0 ist "NICHT ERKANNT"
        self.obj_coord_x = None
        self.obj_coord_y = None
        self.obj_coord_z_up = 0.07          
        self.obj_coord_z_down = 0.095       
        self.obj_coord_theta = None

        self.obj_coord_z_mid = 0.085        #Noch ungenutz, hier muss pre-pick besprochen werden

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

    def auftragseingang_main(self, obj_id, obj_typ, obj_coord_x, obj_coord_y, obj_coord_theta):
        self.obj_id = obj_id
        self.obj_typ = obj_typ
        self.obj_coord_x = obj_coord_x
        self.obj_coord_y = obj_coord_y
        self.obj_coord_theta = obj_coord_theta
        
        self.state = 'obj_pick'
        self.work_done = False

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

    def state_machine(self):
        
        if not self.init_done:
            print("Fehlende Init, Publisher für aktuellen Zyklus geblockt")
            return self.coord_x_default,self.coord_y_default,self.obj_coord_z_up,False,False
        
        if self.state == 'jobless':
            print("State_machine ist Jobless, Publisher für aktuellen Zyklus geblockt")
            return self.coord_x_default,self.coord_y_default,self.obj_coord_z_up,False,False

        #=================================================

        if self.state == "obj_pick":    


            if self.goal_reached_rising == True:
                self.state = "obj_default_pos_grip"
            
            print(f"State: {self.state}, x:{self.obj_coord_x}, y:{self.obj_coord_y}, z:{self.obj_coord_z_down}, True, True")
            return self.obj_coord_x, self.obj_coord_y, self.obj_coord_z_down, True, True


        elif self.state == "obj_default_pos_grip":

            if self.goal_reached_rising == True: 
                self.state = "obj_sort"

            print(f"State: {self.state}, x:{self.coord_x_default}, y:{self.coord_y_default}, z:{self.obj_coord_z_up}, True, True")
            return self.coord_x_default, self.coord_y_default, self.obj_coord_z_up, True, True


        elif self.state == "obj_sort":

            if self.goal_reached_rising == True:
                self.state = "obj_drop"

            if self.obj_typ == 2:           
                print(f"State: {self.state}, x:{self.coord_x_sort_unicorn}, y:{self.coord_y_sort_unicorn}, z:{self.obj_coord_z_up}, True, True")
                return self.coord_x_sort_unicorn, self.coord_y_sort_unicorn, self.obj_coord_z_up, True, True
            
            if self.obj_typ == 1:               
                print(f"State: {self.state}, x:{self.coord_x_sort_cat}, y:{self.coord_y_sort_cat}, z:{self.obj_coord_z_up}, True, True")
                return self.coord_x_sort_cat, self.coord_y_sort_cat, self.obj_coord_z_up, True, True


        elif self.state == "obj_drop":
            
            self.state = 'obj_default_pos_lose'

            if self.obj_typ == 2: 
                print(f"State: {self.state}, x:{self.coord_x_sort_unicorn}, y:{self.coord_y_sort_unicorn}, z:{self.obj_coord_z_up}, False, True")         
                return self.coord_x_sort_unicorn, self.coord_y_sort_unicorn, self.obj_coord_z_up, False, True
        
            if self.obj_typ == 1: 
                print(f"State: {self.state}, x:{self.coord_x_sort_cat}, y:{self.coord_y_sort_cat}, z:{self.obj_coord_z_up}, False, True")               
                return self.coord_x_sort_cat, self.coord_y_sort_cat, self.obj_coord_z_up, False, True
            

        elif self.state == "obj_default_pos_lose":

            if self.goal_reached_rising == True:        #TODO BENJI EWALD EVT WENIGER NERVEN MIT == true WEG MACHEN WIEL UNNÖTIG
                self.state = 'jobless'         

            self.work_done = True 
            print(f"State: {self.state}, x:{self.coord_x_default}, y:{self.coord_y_default}, z:{self.obj_coord_z_up}, False, True")  
            return self.coord_x_default, self.coord_y_default, self.obj_coord_z_up, False, True
        
        #=================================================

        else:
            print(f"Unbekannter State: {self.state} ")
            return self.coord_x_default,self.coord_y_default,self.obj_coord_z_up,False,False

#================================================================================================================