import rclpy
from rclpy.node import Node
import cv2 as cv
from chaos_topics.msg import ObjCoords
from chaos_topics.msg import ObjFeatures
from geometry_msgs.msg import Pose2D
from camera.preprocessing import ImagePreprocessor
import time
import numpy as np

# Testmodus
#import testmode.cat as cat
#import testmode.aruco as aruco

#import cat
#import aruco

img_path_aruco = "~/Robotik/4_Semester/robotik_projekt_3/Portal-zur-Exmatrikulation/ros2_ws/src/chaos_nodes/chaos_nodes/aruco.png"
img_path_cat = "~/Robotik/4_Semester/robotik_projekt_3/Portal-zur-Exmatrikulation/ros2_ws/src/chaos_nodes/chaos_nodes/cat.png"

class Camera(Node):

    def __init__(self):
        super().__init__('camera')

        self.pub_obj_coords = self.create_publisher(ObjCoords, '/obj_coords', 10)
        self.pub_obj_festures = self.create_publisher(ObjFeatures, '/obj_features', 10)
        timer_time = 1/30   # sek

        self.testmode = True # Zum Testen ohne Kamera

        path_camera = 4     # PortalCam = /dev/video4

        try:
            self.PrePro = ImagePreprocessor()
        except Exception as e:
            self.get_logger().error(f'Fehler bei ImagePrepocessor: {str(e)}')
            raise e            

        if self.testmode:
            try:
                # 1. Bild mit cv2.imread() laden
                init_frame = cv.imread(img_path_aruco)
                
                if init_frame is None:
                    self.get_logger().error(f"FEHLER: Konnte das Bild unter {img_path_aruco} nicht laden. Überprüfen Sie den Pfad.")
                    raise Exception("Bild konnte nicht geladen werden.")
                
                # 2. Das geladene Bildobjekt an setup übergeben
                self.PrePro.setup(init_frame)
            except Exception as e:
                self.get_logger().error(f'TEST: Fehler beim Setup der Kamera: {str(e)}')
                raise e
            
            if self.PrePro.H_inv_warp is None:
                self.get_logger().info('TEST: Setup gescheitert')

        else:

            try:
                self.img = cv.VideoCapture(path_camera)
            except Exception as e:
                self.get_logger().error(f'Fehler beim Initialisieren der Kamera: {str(e)}')
                raise e

            self.img.set(cv.CAP_PROP_BUFFERSIZE, 0)

            while(True):
                print('Setup Kamera...')

                try:
                    self.PrePro.setup(self.read_camera())
                except Exception as e:
                    self.get_logger().error(f'Fehler beim Setup der Kamera: {str(e)}')
                    raise e
                
                if self.PrePro.H_inv_warp is not None:
                    break

        self.data = self.create_timer(timer_time, self.timer_callback)
        self.get_logger().info('Kamera-Node gestartet')

    def timer_callback(self): #TODO Einfügen der features nicht korrekt

        if self.testmode:
            frame = img_path_cat

            try:
                obj_coords_msg, obj_features_msg = self.process_img(frame)
                
            except Exception as e:
                self.get_logger().error(f'Fehler bei der Bildverarbeitung: {str(e)}')
                return

            try:
                self.pub_obj_coords.publish(obj_coords_msg)
                self.pub_obj_festures.publish(obj_features_msg)

            except Exception as e:
                self.get_logger().error(f'Fehler beim Senden der Daten: {str(e)}')

        else:

            frame = self.read_camera()

            try:
                obj_coords_msg, obj_features_msg = self.process_img(frame)
                
            except Exception as e:
                self.get_logger().error(f'Fehler bei der Bildverarbeitung: {str(e)}')
                return

            try:
                self.pub_obj_coords.publish(obj_coords_msg)
                self.pub_obj_festures.publish(obj_features_msg)

            except Exception as e:
                self.get_logger().error(f'Fehler beim Senden der Daten: {str(e)}')


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

        #TODO Baustell für publish Format
        
        return world_obj_coords, obj_features

def main(args=None):
    rclpy.init(args=args)
    camera = Camera()
    rclpy.spin(camera)
    camera.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()