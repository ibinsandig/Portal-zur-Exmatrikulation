import ros


#=============================================================================

class MainyLogic():
    def __init__(self):
        
        self.obj_id = None
        self.obj_typ = None
        self.obj_coord_x = None
        self.obj_coord_y = None
        self.obj_coord_z_up = 0.07          #Nochmal Testen TODO
        self.obj_coord_x_down = 0.090       #nochmal testen TODO

        self.init_done = False
        self.auftrag = False
        self.state = "none"



    def init_abfrage(self, init_done):
        self.init_done = init_done
    
    def auftragseingang_main(self, obj_id, obj_typ, obj_coord_x, obj_coord_y):
        self.obj_id = obj_id
        self.obj_typ = obj_typ
        self.obj_coord_x = obj_coord_x
        self.obj_coord_y = obj_coord_y
        
        self.auftrag = True

    def state_machine(self):
        
        if not self.auftrag or not self.init_done:
            raise Exception("Kein Auftragseingang oder fehlende Init")

        if self.state == "obj_pick":    
            self._obj_pick()
            
        elif self.state == "obj_default":
            self._obj_default()

        elif self.state == "obj_sort":
            self._obj_sort()

        elif self.state == "obj_drop":
            self._obj_drop()
            
        else:
            print(f"Unbekannter State: {self.state} ")



    def _obj_pick(self):
        pass

    def _obj_default(self):
        pass
    
    def _obj_sort(self):
        pass

    def _obj_drop(self):
        pass
