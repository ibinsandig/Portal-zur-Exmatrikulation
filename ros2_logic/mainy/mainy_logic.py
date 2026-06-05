
#=============================================================================

class MainyLogic():
    def __init__(self):
        
        self.obj_id =  0                   #TODO2 Hier definieren 0 ist systembelegt (nicht für objekte)                    
        self.obj_typ = 0                    # 0 ist "NICHT ERKANNT"
        self.obj_coord_x = None
        self.obj_coord_y = None
        self.obj_coord_z_up = 0.07          #Nochmal Testen und ggf. justieren TODO
        self.obj_coord_z_down = 0.090       #nochmal testen TODO
        self.obj_coord_theta = None

        self.coord_x_default = 0.20
        self.coord_y_default = -0.08

        self.coord_x_sort_unicorn = 0.20    #TODO Muss noch bestimmt werden (praktisches Annähern)
        self.coord_y_sort_unicorn = -0.11    #TODO

        self.coord_x_sort_cat = 0.015        #TODO
        self.coord_y_sort_cat = -0.11        #TODO

        self.init_done = False
        self.auftrag = False
        self.goal_reached = False
        self.work_done = False

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
    def goal_reached_flag(self, goal_reached):
        self.goal_reached = goal_reached

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


            if self.goal_reached == True:
                self.state = "obj_default_pos_grip"
                self.goal_reached = False
            
            print(f"State: {self.state}, x:{self.obj_coord_x}, y:{self.obj_coord_y}, z:{self.obj_coord_z_down}, True, True")
            return self.obj_coord_x, self.obj_coord_y, self.obj_coord_z_down, True, True


        elif self.state == "obj_default_pos_grip":

            if self.goal_reached == True: 
                self.state = "obj_sort"
                self.goal_reached = False

            print(f"State: {self.state}, x:{self.coord_x_default}, y:{self.coord_y_default}, z:{self.obj_coord_z_up}, True, True")
            return self.coord_x_default, self.coord_y_default, self.obj_coord_z_up, True, True


        elif self.state == "obj_sort":

            if self.goal_reached == True:
                self.state = "obj_drop"
                self.goal_reached = False

            if self.obj_typ == 2:           #TODO Name/ID Muss noch in der Planner_Node festgelegt werden
                print(f"State: {self.state}, x:{self.coord_x_sort_unicorn}, y:{self.coord_y_sort_unicorn}, z:{self.obj_coord_z_up}, True, True")
                return self.coord_x_sort_unicorn, self.coord_y_sort_unicorn, self.obj_coord_z_up, True, True
            
            if self.obj_typ == 1:               #TODO NAME/ID Muss noch in der Planner_Node festgelegt werden
                print(f"State: {self.state}, x:{self.coord_x_sort_cat}, y:{self.coord_y_sort_cat}, z:{self.obj_coord_z_up}, True, True")
                return self.coord_x_sort_cat, self.coord_y_sort_cat, self.obj_coord_z_up, True, True


        elif self.state == "obj_drop":

            if self.goal_reached == True:
                self.state = 'obj_default_pos_lose'
                self.goal_reached = False

            if self.obj_typ == 2: 
                print(f"State: {self.state}, x:{self.coord_x_sort_unicorn}, y:{self.coord_y_sort_unicorn}, z:{self.obj_coord_z_up}, False, True")         
                return self.coord_x_sort_unicorn, self.coord_y_sort_unicorn, self.obj_coord_z_up, False, True
        
            if self.obj_typ == 1: 
                print(f"State: {self.state}, x:{self.coord_x_sort_cat}, y:{self.coord_y_sort_cat}, z:{self.obj_coord_z_up}, False, True")               
                return self.coord_x_sort_cat, self.coord_y_sort_cat, self.obj_coord_z_up, False, True
            

        elif self.state == "obj_default_pos_lose":

            if self.goal_reached == True:
                self.state = 'jobless'         #TODO hier evt RUNTIMEERROR mit Auftragseingang und state"obj_pick"
                self.goal_reached = False

            self.work_done = True 
            print(f"State: {self.state}, x:{self.coord_x_default}, y:{self.coord_y_default}, z:{self.obj_coord_z_up}, False, True")  
            return self.coord_x_default, self.coord_y_default, self.obj_coord_z_up, False, True
        
        #=================================================

        else:
            print(f"Unbekannter State: {self.state} ")
            return self.coord_x_default,self.coord_y_default,self.obj_coord_z_up,False,False

#================================================================================================================