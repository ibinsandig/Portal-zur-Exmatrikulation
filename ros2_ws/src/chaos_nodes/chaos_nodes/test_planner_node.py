import rclpy
from rclpy.node import Node
from chaos_topics.msg import ObjData
from std_msgs.msg import Bool
from geometry_msgs.msg import Point



#================================================================================================

class Test_planer(Node):
    def __init__(self):
        super().__init__('Test_planer')

        self.sub_start_test = self.create_subscription(Bool, '/start_test_1', self.testdaten_1_timer,10)
        self.sub_start_test = self.create_subscription(Bool, '/start_test_2', self.testdaten_2_timer,10)

        self.pub_testplaner = self.create_publisher(ObjData, '/obj_data', 10)

        #Liste mit Objekten. [id, typ, x, y, theta, obj_geschindigkeit]
        self.test_daten = [
            # Zeitschritt 0
            [
                [1, 1, 0.100, -0.065, 0.0, 0.025],
                [2, 2, 0.110, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 1
            [
                [1, 1, 0.0975, -0.065, 0.0, 0.015],
                [2, 2, 0.1085, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 2
            [
                [1, 1, 0.096, -0.065, 0.0, 0.025],
                [2, 2, 0.106, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 3
            [
                [1, 1, 0.0935, -0.065, 0.0, 0.015],
                [2, 2, 0.1045, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 4
            [
                [1, 1, 0.092, -0.065, 0.0, 0.025],
                [2, 2, 0.102, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 5
            [
                [1, 1, 0.0895, -0.065, 0.0, 0.015],
                [2, 2, 0.1005, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 6
            [
                [1, 1, 0.088, -0.065, 0.0, 0.025],
                [2, 2, 0.098, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 7
            [
                [1, 1, 0.0855, -0.065, 0.0, 0.015],
                [2, 2, 0.0965, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 8
            [
                [1, 1, 0.084, -0.065, 0.0, 0.025],
                [2, 2, 0.094, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 9
            [
                [1, 1, 0.0815, -0.065, 0.0, 0.015],
                [2, 2, 0.0925, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 10
            [
                [1, 1, 0.080, -0.065, 0.0, 0.025],
                [2, 2, 0.090, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 11
            [
                [1, 1, 0.0775, -0.065, 0.0, 0.015],
                [2, 2, 0.0885, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 12
            [
                [1, 1, 0.076, -0.065, 0.0, 0.025],
                [2, 2, 0.086, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 13
            [
                [1, 1, 0.0735, -0.065, 0.0, 0.015],
                [2, 2, 0.0845, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 14
            [
                [1, 1, 0.072, -0.065, 0.0, 0.025],
                [2, 2, 0.082, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 15
            [
                [1, 1, 0.0695, -0.065, 0.0, 0.015],
                [2, 2, 0.0805, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 16
            [
                [1, 1, 0.068, -0.065, 0.0, 0.025],
                [2, 2, 0.078, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 17
            [
                [1, 1, 0.0655, -0.065, 0.0, 0.015],
                [2, 2, 0.0765, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 18
            [
                [1, 1, 0.064, -0.065, 0.0, 0.025],
                [2, 2, 0.074, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 19
            [
                [1, 1, 0.0615, -0.065, 0.0, 0.015],
                [2, 2, 0.0725, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 20
            [
                [1, 1, 0.060, -0.065, 0.0, 0.025],
                [2, 2, 0.070, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 21
            [
                [1, 1, 0.0575, -0.065, 0.0, 0.015],
                [2, 2, 0.0685, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 22
            [
                [1, 1, 0.056, -0.065, 0.0, 0.025],
                [2, 2, 0.066, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 23
            [
                [1, 1, 0.0535, -0.065, 0.0, 0.015],
                [2, 2, 0.0645, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 24
            [
                [1, 1, 0.052, -0.065, 0.0, 0.025],
                [2, 2, 0.062, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 25
            [
                [1, 1, 0.0495, -0.065, 0.0, 0.015],
                [2, 2, 0.0605, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 26
            [
                [1, 1, 0.048, -0.065, 0.0, 0.025],
                [2, 2, 0.058, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 27
            [
                [1, 1, 0.0455, -0.065, 0.0, 0.015],
                [2, 2, 0.0565, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 28
            [
                [1, 1, 0.044, -0.065, 0.0, 0.025],
                [2, 2, 0.054, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 29
            [
                [1, 1, 0.0415, -0.065, 0.0, 0.015],
                [2, 2, 0.0525, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 30
            [
                [1, 1, 0.040, -0.065, 0.0, 0.025],
                [2, 2, 0.050, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 31
            [
                [1, 1, 0.0375, -0.065, 0.0, 0.015],
                [2, 2, 0.0485, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 32
            [
                [1, 1, 0.036, -0.065, 0.0, 0.025],
                [2, 2, 0.046, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 33
            [
                [1, 1, 0.0335, -0.065, 0.0, 0.015],
                [2, 2, 0.0445, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 34
            [
                [1, 1, 0.032, -0.065, 0.0, 0.025],
                [2, 2, 0.042, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 35
            [
                [1, 1, 0.0295, -0.065, 0.0, 0.015],
                [2, 2, 0.0405, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 36
            [
                [1, 1, 0.028, -0.065, 0.0, 0.025],
                [2, 2, 0.038, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 37
            [
                [1, 1, 0.0255, -0.065, 0.0, 0.015],
                [2, 2, 0.0365, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 38
            [
                [1, 1, 0.024, -0.065, 0.0, 0.025],
                [2, 2, 0.034, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 39
            [
                [1, 1, 0.0215, -0.065, 0.0, 0.015],
                [2, 2, 0.0325, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 40
            [
                [1, 1, 0.020, -0.065, 0.0, 0.025],
                [2, 2, 0.030, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 41
            [
                [1, 1, 0.0175, -0.065, 0.0, 0.015],
                [2, 2, 0.0285, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 42
            [
                [1, 1, 0.016, -0.065, 0.0, 0.025],
                [2, 2, 0.026, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 43
            [
                [1, 1, 0.0135, -0.065, 0.0, 0.015],
                [2, 2, 0.0245, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 44
            [
                [1, 1, 0.012, -0.065, 0.0, 0.025],
                [2, 2, 0.022, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 45
            [
                [1, 1, 0.0095, -0.065, 0.0, 0.015],
                [2, 2, 0.0205, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 46
            [
                [1, 1, 0.008, -0.065, 0.0, 0.025],
                [2, 2, 0.018, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 47
            [
                [1, 1, 0.0055, -0.065, 0.0, 0.015],
                [2, 2, 0.0165, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 48
            [
                [1, 1, 0.004, -0.065, 0.0, 0.025],
                [2, 2, 0.014, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 49
            [
                [1, 1, 0.0015, -0.065, 0.0, 0.015],
                [2, 2, 0.0125, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 50 (ID 1 erreicht Ziel)
            [
                [1, 1, 0.000, -0.065, 0.0, 0.000],
                [2, 2, 0.010, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 51
            [
                [1, 1, 0.000, -0.065, 0.0, 0.000],
                [2, 2, 0.0085, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 52
            [
                [1, 1, 0.000, -0.065, 0.0, 0.000],
                [2, 2, 0.006, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 53
            [
                [1, 1, 0.000, -0.065, 0.0, 0.000],
                [2, 2, 0.0045, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 54
            [
                [1, 1, 0.000, -0.065, 0.0, 0.000],
                [2, 2, 0.002, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 55
            [
                [1, 1, 0.000, -0.065, 0.0, 0.000],
                [2, 2, 0.0005, -0.07, 0.0, 0.025]
            ],
            # Zeitschritt 56 (ID 2 erreicht Ziel)
            [
                [1, 1, 0.000, -0.065, 0.0, 0.000],
                [2, 2, 0.000, -0.07, 0.0, 0.000]
            ]
        ]
        
        self.liste_id_1 = []
        self.liste_id_2 = []

        for frame in self.test_daten:
            for objekt in frame:
                if objekt[0] == 1:
                    self.liste_id_1.append(objekt)
                elif objekt[0] == 2:
                    self.liste_id_2.append(objekt)
                else:
                    print("Fehler beim Objekte aus Liste extrahieren")

        self.spezial_timer = None

        self.schritt_id1 = 0
        self.schritt_id2 = 0

        print("planerTest NOde gestartet")

    def testdaten_1_timer(self, msg):
        print("Bool gestartet")
        if self.spezial_timer is None:
            self.spezial_timer = self.create_timer(0.2, self.pub_1)
            print("Timer für id1 wurde gestartet")
        else:
            print("Timer für testdaten_1 konnte nicht erstellt werden!")
    
    def pub_1(self):

        if self.schritt_id1 < (len(self.liste_id_1)-7):
            frame = self.liste_id_1[self.schritt_id1]   
            print(frame)
   
            objdata = ObjData()

            objdata.point = Point()
            objdata.point.x = float(frame[3])
            objdata.point.y = float(frame[4])
            objdata.point.z = float(0.0)

            objdata.id = frame[0]
            objdata.obj_typ = frame[1]
            objdata.obj_speed = frame[5]
        
            self.pub_testplaner.publish(objdata)

            self.schritt_id1 += 1

        else: 
            print("ID_1 ist druchgelaufen und am Ende der Strecke")
            self.spezial_timer.cancel()
            self.spezial_timer = None

            self.schritt_id1 = 0
        

    def testdaten_2_timer(self, msg):
        if self.spezial_timer is None:
            self.spezial_timer = self.create_timer(0.2, self.pub_2)
        else:
            print("Timer für testdaten_2 konnte nicht erstellt werden!")
    
    def pub_2(self):

        if self.schritt_id2 < len(self.liste_id_2):
            frame = self.liste_id_2[self.schritt_id2]   
            print(frame)
   
       
            objdata = ObjData()

            objdata.point = Point()
            objdata.point.x = float(frame[3])
            objdata.point.y = float(frame[4])
            objdata.point.z = float(0.0)

            objdata.id = frame[0]
            objdata.obj_typ = frame[1]
            objdata.obj_speed = frame[5]
        
            self.pub_testplaner.publish(objdata)

            self.schritt_id2 += 1

        else: 
            print("ID_2 ist druchgelaufen und am Ende der Strecke")
            self.spezial_timer.cancel()
            self.spezial_timer = None

            self.schritt_id2 = 0




def main():
    rclpy.init(args=None)
    main = Test_planer()
    rclpy.spin(main)
    main.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
    
