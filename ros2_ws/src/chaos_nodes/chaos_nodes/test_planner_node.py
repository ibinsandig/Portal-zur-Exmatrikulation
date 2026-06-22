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
                [1, 1, 0.100, -0.07, 0.0, 0.025],
                [2, 2, 0.110, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 1
            [
                [1, 1, 0.099, -0.07, 0.0, 0.025],
                [2, 2, 0.109, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 2
            [
                [1, 1, 0.098, -0.07, 0.0, 0.025],
                [2, 2, 0.108, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 3
            [
                [1, 1, 0.097, -0.07, 0.0, 0.025],
                [2, 2, 0.107, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 4
            [
                [1, 1, 0.096, -0.07, 0.0, 0.025],
                [2, 2, 0.106, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 5
            [
                [1, 1, 0.095, -0.07, 0.0, 0.025],
                [2, 2, 0.105, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 6
            [
                [1, 1, 0.094, -0.07, 0.0, 0.025],
                [2, 2, 0.104, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 7
            [
                [1, 1, 0.093, -0.07, 0.0, 0.025],
                [2, 2, 0.103, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 8
            [
                [1, 1, 0.092, -0.07, 0.0, 0.025],
                [2, 2, 0.102, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 9
            [
                [1, 1, 0.091, -0.07, 0.0, 0.025],
                [2, 2, 0.101, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 10
            [
                [1, 1, 0.090, -0.07, 0.0, 0.025],
                [2, 2, 0.100, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 11
            [
                [1, 1, 0.089, -0.07, 0.0, 0.025],
                [2, 2, 0.099, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 12
            [
                [1, 1, 0.088, -0.07, 0.0, 0.025],
                [2, 2, 0.098, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 13
            [
                [1, 1, 0.087, -0.07, 0.0, 0.025],
                [2, 2, 0.097, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 14
            [
                [1, 1, 0.086, -0.07, 0.0, 0.025],
                [2, 2, 0.096, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 15
            [
                [1, 1, 0.085, -0.07, 0.0, 0.025],
                [2, 2, 0.095, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 16
            [
                [1, 1, 0.084, -0.07, 0.0, 0.025],
                [2, 2, 0.094, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 17
            [
                [1, 1, 0.083, -0.07, 0.0, 0.025],
                [2, 2, 0.093, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 18
            [
                [1, 1, 0.082, -0.07, 0.0, 0.025],
                [2, 2, 0.092, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 19
            [
                [1, 1, 0.081, -0.07, 0.0, 0.025],
                [2, 2, 0.091, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 20
            [
                [1, 1, 0.080, -0.07, 0.0, 0.025],
                [2, 2, 0.090, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 21
            [
                [1, 1, 0.079, -0.07, 0.0, 0.025],
                [2, 2, 0.089, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 22
            [
                [1, 1, 0.078, -0.07, 0.0, 0.025],
                [2, 2, 0.088, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 23
            [
                [1, 1, 0.077, -0.07, 0.0, 0.025],
                [2, 2, 0.087, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 24
            [
                [1, 1, 0.076, -0.07, 0.0, 0.025],
                [2, 2, 0.086, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 25
            [
                [1, 1, 0.075, -0.07, 0.0, 0.025],
                [2, 2, 0.085, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 26
            [
                [1, 1, 0.074, -0.07, 0.0, 0.025],
                [2, 2, 0.084, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 27
            [
                [1, 1, 0.073, -0.07, 0.0, 0.025],
                [2, 2, 0.083, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 28
            [
                [1, 1, 0.072, -0.07, 0.0, 0.025],
                [2, 2, 0.082, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 29
            [
                [1, 1, 0.071, -0.07, 0.0, 0.025],
                [2, 2, 0.081, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 30
            [
                [1, 1, 0.070, -0.07, 0.0, 0.025],
                [2, 2, 0.080, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 31
            [
                [1, 1, 0.069, -0.07, 0.0, 0.025],
                [2, 2, 0.079, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 32
            [
                [1, 1, 0.068, -0.07, 0.0, 0.025],
                [2, 2, 0.078, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 33
            [
                [1, 1, 0.067, -0.07, 0.0, 0.025],
                [2, 2, 0.077, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 34
            [
                [1, 1, 0.066, -0.07, 0.0, 0.025],
                [2, 2, 0.076, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 35
            [
                [1, 1, 0.065, -0.07, 0.0, 0.025],
                [2, 2, 0.075, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 36
            [
                [1, 1, 0.064, -0.07, 0.0, 0.025],
                [2, 2, 0.074, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 37
            [
                [1, 1, 0.063, -0.07, 0.0, 0.025],
                [2, 2, 0.073, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 38
            [
                [1, 1, 0.062, -0.07, 0.0, 0.025],
                [2, 2, 0.072, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 39
            [
                [1, 1, 0.061, -0.07, 0.0, 0.025],
                [2, 2, 0.071, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 40
            [
                [1, 1, 0.060, -0.07, 0.0, 0.025],
                [2, 2, 0.070, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 41
            [
                [1, 1, 0.059, -0.07, 0.0, 0.025],
                [2, 2, 0.069, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 42
            [
                [1, 1, 0.058, -0.07, 0.0, 0.025],
                [2, 2, 0.068, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 43
            [
                [1, 1, 0.057, -0.07, 0.0, 0.025],
                [2, 2, 0.067, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 44
            [
                [1, 1, 0.056, -0.07, 0.0, 0.025],
                [2, 2, 0.066, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 45
            [
                [1, 1, 0.055, -0.07, 0.0, 0.025],
                [2, 2, 0.065, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 46
            [
                [1, 1, 0.054, -0.07, 0.0, 0.025],
                [2, 2, 0.064, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 47
            [
                [1, 1, 0.053, -0.07, 0.0, 0.025],
                [2, 2, 0.063, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 48
            [
                [1, 1, 0.052, -0.07, 0.0, 0.025],
                [2, 2, 0.062, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 49
            [
                [1, 1, 0.051, -0.07, 0.0, 0.025],
                [2, 2, 0.061, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 50
            [
                [1, 1, 0.050, -0.07, 0.0, 0.025],
                [2, 2, 0.060, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 51
            [
                [1, 1, 0.049, -0.07, 0.0, 0.025],
                [2, 2, 0.059, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 52
            [
                [1, 1, 0.048, -0.07, 0.0, 0.025],
                [2, 2, 0.058, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 53
            [
                [1, 1, 0.047, -0.07, 0.0, 0.025],
                [2, 2, 0.057, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 54
            [
                [1, 1, 0.046, -0.07, 0.0, 0.025],
                [2, 2, 0.056, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 55
            [
                [1, 1, 0.045, -0.07, 0.0, 0.025],
                [2, 2, 0.055, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 56
            [
                [1, 1, 0.044, -0.07, 0.0, 0.025],
                [2, 2, 0.054, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 57
            [
                [1, 1, 0.043, -0.07, 0.0, 0.025],
                [2, 2, 0.053, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 58
            [
                [1, 1, 0.042, -0.07, 0.0, 0.025],
                [2, 2, 0.052, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 59
            [
                [1, 1, 0.041, -0.07, 0.0, 0.025],
                [2, 2, 0.051, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 60
            [
                [1, 1, 0.040, -0.07, 0.0, 0.025],
                [2, 2, 0.050, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 61
            [
                [1, 1, 0.039, -0.07, 0.0, 0.025],
                [2, 2, 0.049, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 62
            [
                [1, 1, 0.038, -0.07, 0.0, 0.025],
                [2, 2, 0.048, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 63
            [
                [1, 1, 0.037, -0.07, 0.0, 0.025],
                [2, 2, 0.047, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 64
            [
                [1, 1, 0.036, -0.07, 0.0, 0.025],
                [2, 2, 0.046, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 65
            [
                [1, 1, 0.035, -0.07, 0.0, 0.025],
                [2, 2, 0.045, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 66
            [
                [1, 1, 0.034, -0.07, 0.0, 0.025],
                [2, 2, 0.044, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 67
            [
                [1, 1, 0.033, -0.07, 0.0, 0.025],
                [2, 2, 0.043, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 68
            [
                [1, 1, 0.032, -0.07, 0.0, 0.025],
                [2, 2, 0.042, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 69
            [
                [1, 1, 0.031, -0.07, 0.0, 0.025],
                [2, 2, 0.041, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 70
            [
                [1, 1, 0.030, -0.07, 0.0, 0.025],
                [2, 2, 0.040, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 71
            [
                [1, 1, 0.029, -0.07, 0.0, 0.025],
                [2, 2, 0.039, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 72
            [
                [1, 1, 0.028, -0.07, 0.0, 0.025],
                [2, 2, 0.038, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 73
            [
                [1, 1, 0.027, -0.07, 0.0, 0.025],
                [2, 2, 0.037, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 74
            [
                [1, 1, 0.026, -0.07, 0.0, 0.025],
                [2, 2, 0.036, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 75
            [
                [1, 1, 0.025, -0.07, 0.0, 0.025],
                [2, 2, 0.035, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 76
            [
                [1, 1, 0.024, -0.07, 0.0, 0.025],
                [2, 2, 0.034, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 77
            [
                [1, 1, 0.023, -0.07, 0.0, 0.025],
                [2, 2, 0.033, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 78
            [
                [1, 1, 0.022, -0.07, 0.0, 0.025],
                [2, 2, 0.032, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 79
            [
                [1, 1, 0.021, -0.07, 0.0, 0.025],
                [2, 2, 0.031, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 80
            [
                [1, 1, 0.020, -0.07, 0.0, 0.025],
                [2, 2, 0.030, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 81
            [
                [1, 1, 0.019, -0.07, 0.0, 0.025],
                [2, 2, 0.029, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 82
            [
                [1, 1, 0.018, -0.07, 0.0, 0.025],
                [2, 2, 0.028, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 83
            [
                [1, 1, 0.017, -0.07, 0.0, 0.025],
                [2, 2, 0.027, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 84
            [
                [1, 1, 0.016, -0.07, 0.0, 0.025],
                [2, 2, 0.026, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 85
            [
                [1, 1, 0.015, -0.07, 0.0, 0.025],
                [2, 2, 0.025, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 86
            [
                [1, 1, 0.014, -0.07, 0.0, 0.025],
                [2, 2, 0.024, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 87
            [
                [1, 1, 0.013, -0.07, 0.0, 0.025],
                [2, 2, 0.023, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 88
            [
                [1, 1, 0.012, -0.07, 0.0, 0.025],
                [2, 2, 0.022, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 89
            [
                [1, 1, 0.011, -0.07, 0.0, 0.025],
                [2, 2, 0.021, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 90
            [
                [1, 1, 0.010, -0.07, 0.0, 0.025],
                [2, 2, 0.020, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 91
            [
                [1, 1, 0.009, -0.07, 0.0, 0.025],
                [2, 2, 0.019, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 92
            [
                [1, 1, 0.008, -0.07, 0.0, 0.025],
                [2, 2, 0.018, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 93
            [
                [1, 1, 0.007, -0.07, 0.0, 0.025],
                [2, 2, 0.017, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 94
            [
                [1, 1, 0.006, -0.07, 0.0, 0.025],
                [2, 2, 0.016, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 95
            [
                [1, 1, 0.005, -0.07, 0.0, 0.025],
                [2, 2, 0.015, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 96
            [
                [1, 1, 0.004, -0.07, 0.0, 0.025],
                [2, 2, 0.014, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 97
            [
                [1, 1, 0.003, -0.07, 0.0, 0.025],
                [2, 2, 0.013, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 98
            [
                [1, 1, 0.002, -0.07, 0.0, 0.025],
                [2, 2, 0.012, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 99
            [
                [1, 1, 0.001, -0.07, 0.0, 0.025],
                [2, 2, 0.011, -0.07, 0.0, 0.015]
            ],
            # Zeitschritt 100
            [
                [1, 1, 0.000, -0.07, 0.0, 0.025],
                [2, 2, 0.010, -0.07, 0.0, 0.015]
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
            self.spezial_timer = self.create_timer(0.1, self.pub_1)
            print("Timer für id1 wurde gestartet")
        else:
            print("Timer für testdaten_1 konnte nicht erstellt werden!")
    
    def pub_1(self):

        if self.schritt_id1 < (len(self.liste_id_1)-7):
            frame = self.liste_id_1[self.schritt_id1]   
            print(frame)
   
            objdata = ObjData()

            objdata.point = Point()
            objdata.point.x = float(frame[2])
            objdata.point.y = float(frame[3])
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
    
