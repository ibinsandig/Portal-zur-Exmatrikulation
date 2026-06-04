
#=============================================================================

class MainyLogic():
    def __init__(self):
        
        self.obj_id = None
        self.obj_typ = None
        self.obj_coord_x = None
        self.obj_coord_y = None
        self.obj_coord_z_up = 0.07          #Nochmal Testen und ggf. justieren TODO
        self.obj_coord_x_down = 0.090       #nochmal testen TODO
        self.obj_coord_theta = None

        self.coord_x_default = 0.06
        self.coord_y_default = -0.08

        self.coord_x_sort_unicorn = None    #TODO Muss noch bestimmt werden (praktisches Annähern)
        self.coord_y_sort_unicorn = None    #TODO

        self.coord_x_sort_cat = None        #TODO
        self.coord_y_sort_cat = None        #TODO

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
    def goal_reached(self, goal_reached):
        self.goal_reached = goal_reached

#================================================================================================================

    def work_done(self):
        return self.work_done, self.obj_id

#================================================================================================================

    def state_machine(self):
        
        if not self.init_done:
            print("Fehlende Init, default werte gepublished")
            return self.coord_x_default,self.coord_y_default,self.obj_coord_z_up,False
        
        if self.state == 'jobless':
            print("State_machine ist Jobless, default Werte gepublished")
            return self.coord_x_default,self.coord_y_default,self.obj_coord_z_up,False

        #=================================================

        if self.state == "obj_pick":    

            if self.goal_reached == True:
                self.state = "obj_dafault_pos_grip"
                self.goal_reached = False
            
            return self.obj_coord_x, self.obj_coord_y, self.obj_coord_x_down, True


        elif self.state == "obj_default_pos_grip":

            if self.goal_reached == True: 
                self.state == "obj_sort"
                self.goal_reached = False

            return self.coord_x_default, self.coord_y_default, self.obj_coord_z_up, True


        elif self.state == "obj_sort":

            if self.goal_reached == True:
                self.state == "obj_drop"
                self.goal_reached = False

            if self.obj_typ == 'unicorn':           #TODO Name/ID Muss noch in der Planner_Node festgelegt werden
                return self.coord_x_sort_unicorn, self.coord_y_sort_unicorn, self.obj_coord_z_up, True
            
            if self.obj_typ == 'cat':               #TODO NAME/ID Muss noch in der Planner_Node festgelegt werden
                return self.coord_x_sort_cat, self.coord_y_sort_cat, self.obj_coord_z_up, True


        elif self.state == "obj_drop":

            if self.goal_reached == True:
                self.state == 'obj_default_pos_lose'
                self.goal_reached = False

            if self.obj_typ == 'unicorn':          
                return self.coord_x_sort_unicorn, self.coord_y_sort_unicorn, self.obj_coord_z_up, False
        
            if self.obj_typ == 'cat':              
                return self.coord_x_sort_cat, self.coord_y_sort_cat, self.obj_coord_z_up, False
            

        elif self.state == "obj_default_pos_lose":

            if self.goal_reached == True:
                self.state == 'jobless'         #TODO hier evt RUNTIMEERROR mit Auftragseingang und state"obj_pick"
                self.goal_reached = False

            self.work_done = True 
            return self.coord_x_default, self.coord_y_default, self.obj_coord_z_up, False
        
        #=================================================

        else:
            print(f"Unbekannter State: {self.state} ")
            return self.coord_x_default,self.coord_y_default,self.obj_coord_z_up,False,False

#================================================================================================================