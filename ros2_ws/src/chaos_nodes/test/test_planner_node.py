import rclpy
from rclpy.node import Node
from rclpy.time import timer 
from chaos_topics.msg import ObjData


#================================================================================================

class Test_planer(Node):
    def __init__(self):
        
        super().__init__('Test_planer')

        self.pub_testplaner = self.create_publisher(ObjData, '/test_planer', 10)

        #Liste mit Objekten. [id, typ, x, y, theta, obj_geschindigkeit]
        self.testobjekt_1 = [[1,1,0.10,0.06, 0.0, 0.01],
                             [2,2,0.11,0.08, ],
                             [3,1,0.09,0.07]
                            ]
        
        self.timer = self.create_timer(0.1, self.testdaten_publisher)
        
        self.objdata = ObjData()
          

    def testdaten_publisher():
        
        for i in self.testobjekte: 
            
            self.Objdata.id = self.testobjekte[[0],[0]]
            

        pass

    

def main():
    rclpy.init(args=None)
    main = Test_planer()
    rclpy.spin(main)
    main.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
    
