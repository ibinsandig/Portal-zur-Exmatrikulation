import rclpy
from rclpy.node import Node
import cv2 as cv
from chaos_interfaces.msg import ObjData
from camera.preprocessing import ImagePreprocessor

class Camera(Node):

    def __init__(self):
        super().__init__('camera')

        self.pub_obj_data = self.create_publisher(ObjData, '/obj_data', 10)
        timer_time = 1/30   # sek

        path_camera = 0     # PortalCam = /dev/video4

        self.PrePro = ImagePreprocessor()

        try:
            self.img = cv.VideoCapture(path_camera)
        except Exception as e:
            self.get_logger().error(f'Fehler beim Initialiesieren der Kamera: {str(e)}')
            raise e
        
        self.img.set(cv.CAP_PROP_BUFFERSIZE, 1)
        self.data = self.create_timer(timer_time, self.timer_callback)
        self.get_logger().info('Camera-Node gestartet')

    def timer_callback(self):
        """Timer Callback - liest Bild und verarbeitet es schrittweise"""
        success, frame = self.img.read()

        if not success:
            self.get_logger().error('Bild konnte nicht gelesen werden')
            return

        try:
            cropped_frame = self.PrePro.crop_image(frame)
            
            mask = self.PrePro.segment_object(cropped_frame)
            
            centers = self.PrePro.focus_center(mask)

            orientations = self.PrePro.object_orientation(mask)
            
            objects_data = self.PrePro.object_data(mask)
                
        except Exception as e:
            self.get_logger().error(f'Fehler bei der Bildverarbeitung: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    camera = Camera()
    rclpy.spin(camera)
    camera.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()