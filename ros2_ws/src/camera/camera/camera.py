import rclpy
from rclpy.node import Node
import cv2 as cv
from chaos_interfaces.msg import ObjData
class Camera(Node):
    def __init__(self):
        super().__init__('camera')

        self.publisher = self.create_publisher(ObjData, '/obj_data', 10)
        timer_time = 1/30   # sek

        path_camera = 0     # /dev/video0 

        try:
            self.img = cv.VideoCapture(path_camera)
        except Exception as e:
            self.get_logger().error(f'Fehler beim Initialiesieren der Kamera: {str(e)}')
            raise e
        
        self.img.set(cv.CAP_PROP_BUFFERSIZE, 1)
        
        self.data = self.create_timer(timer_time, self.timer_callback)

        self.get_logger().info('Camera-Node gestartet')



    def timer_callback(self):
        msg = 0
        self.publisher.publish(msg)    
    
    def read_camera(self):
        
        success, frame = self.img.read()

        if not success:
            self.get_logger().error('Bild konnte nicht gelesen werden')
            return None

def main(args=None):
    rclpy.init(args=args)
    camera = Camera()
    rclpy.spin(camera)
    camera.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()