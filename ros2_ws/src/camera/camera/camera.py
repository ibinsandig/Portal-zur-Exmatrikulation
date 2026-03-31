import rclpy
from rclpy.node import Node
import cv2 as cv

class Camera(Node):
    def init(self):
        super().__init__('camera')

        self.publisher = self.create_publisher(ImageData, '/obj_data', 10)
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
        pass
    

    def read_camera():
        pass

def main()

if __name__ == 'main':
    main()