import rclpy
from rclpy.node import Node
import cv2 as cv
from chaos_topics.msg import ObjCoords
from chaos_topics.msg import ObjFeatures
from camera.preprocessing3 import ImagePreprocessor

class Camera(Node):

    def __init__(self):
        super().__init__('camera')

        self.pub_obj_coords = self.create_publisher(ObjCoords, '/obj_coords', 10)
        self.pub_obj_festures = self.create_publisher(ObjFeatures, '/obj_features', 10)
        timer_time = 1/30   # sek

        path_camera = 0     # PortalCam = /dev/video4

        try:
            self.PrePro = ImagePreprocessor()
        except Exception as e:
            self.get_logger().error(f'Fehler bei ImagePrepocessor: {str(e)}')
            raise e            

        try:
            self.img = cv.VideoCapture(path_camera)
        except Exception as e:
            self.get_logger().error(f'Fehler beim Initialiesieren der Kamera: {str(e)}')
            raise e

        self.img.set(cv.CAP_PROP_BUFFERSIZE, 1)
        self.data = self.create_timer(timer_time, self.timer_callback)
        self.get_logger().info('Camera-Node gestartet')

    def timer_callback(self):

        frame = self.read_camera()

        try:
            self.process_img(frame)
                
        except Exception as e:
            self.get_logger().error(f'Fehler bei der Bildverarbeitung: {str(e)}')

    def read_camera(self):
        success , frame = self.img.read()

        if not success:
            self.get_logger().error('Bild konnte nicht gelesen werden')
            return
        
        img_rotated = cv.rotate(frame, 2)
        return img_rotated

    def process_img(self, frame):
        warped_image = self.PrePro.warp_image(frame)
        contours = self.PrePro.segment_object(warped_image)

        pixel_obj_coords = self.PrePro.obj_position(contours)

        world_obj_coords = self.PrePro.pixel_to_world(pixel_obj_coords)

        obj_features = self.PrePro.extract_features_from_contour(contours[0])

        return world_obj_coords, obj_features

def main(args=None):
    rclpy.init(args=args)
    camera = Camera()
    rclpy.spin(camera)
    camera.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()