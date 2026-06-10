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
import testmode
import os
_TESTMODE_DIR = os.path.dirname(testmode.__file__)
img_path_cat   = os.path.join(_TESTMODE_DIR, 'unicorn_0.png')
img_path_aruco = os.path.join(_TESTMODE_DIR, 'aruco.png')

class Camera(Node):

#TODO Logik für das erkennen mehrerer Objekt auf dem Fliesband, möglicherweise über die Distanz die zurückgelegt wurde/ ab einem Punkt wird das näxhste Objekt beachtet

    def __init__(self):
        super().__init__('camera')

        self.pub_obj_coords = self.create_publisher(ObjCoords, '/obj_coords', 10)
        self.pub_obj_festures = self.create_publisher(ObjFeatures, '/obj_features', 10)
        timer_time = 1/30   # sek

        self.start_time = time.time()

        # Zum Testen ohne Kamera
        self.testmode = False


        self.frame_count = 1  

        path_camera = 4     # PortalCam = /dev/video4

        try:
            self.PrePro = ImagePreprocessor()
        except Exception as e:
            self.get_logger().error(f'Fehler bei ImagePrepocessor: {str(e)}')
            raise e            

        if self.testmode:
            try:
                init_frame = cv.imread(img_path_aruco)
                
                if init_frame is None:
                    self.get_logger().error(f"TEST: Konnte das Bild unter {img_path_aruco} nicht laden. Überprüfen Sie den Pfad.")
                    raise Exception("Bild konnte nicht geladen werden.")
                

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
            frame = cv.imread(img_path_cat)
            
            if frame is None:
                self.get_logger().error(f"TEST: Konnte das Bild unter {img_path_cat} nicht laden.")
                return

            try:
                obj_coords_msg, obj_features_msg = self.process_img(frame)
                
                if obj_coords_msg is None or obj_features_msg is None:
                    self.get_logger().debug('TEST: Keine gültigen Daten zum Veröffentlichen')
                    return
                
            except Exception as e:
                self.get_logger().error(f'TEST: Fehler bei der Bildverarbeitung: {str(e)}')
                return

            try:
                self.pub_obj_coords.publish(obj_coords_msg)
                self.pub_obj_festures.publish(obj_features_msg)
                self.get_logger().info('TEST: Daten erfolgreich veröffentlicht')
            except Exception as e:
                self.get_logger().error(f'TEST: Fehler beim Senden der Daten: {str(e)}')

            

        else:

            frame = self.read_camera()

            try:
                obj_coords_msg, obj_features_msg = self.process_img(frame)
                
                if obj_coords_msg is None or obj_features_msg is None:
                    self.get_logger().debug('Keine gültigen Daten zum Veröffentlichen')
                    return
                
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

        if not contours:
            self.get_logger().info('Keine Konturen gefunden')
            return None, None

        pixel_obj_coords = self.PrePro.obj_position(contours)
        
        if pixel_obj_coords is None:
            self.get_logger().warn('Objekt Position konnte nicht ermittelt werden')
            return None, None
        print('pixel_obj_coords: ')
        print(pixel_obj_coords)

        world_obj_coords = self.PrePro.pixel_to_world(pixel_obj_coords)
        obj_features_dict = self.PrePro.extract_features_from_contour(contours[0])

        if obj_features_dict is None:
            self.get_logger().warn('Features konnten nicht extrahiert werden')
            return None, None

        pose2d = Pose2D()
        pose2d.x = float(world_obj_coords[0])
        pose2d.y = float(world_obj_coords[1])
        pose2d.theta = self.PrePro.extract_orientation(contours[0])
        
        obj_coords_msg = ObjCoords()
        obj_coords_msg.pose2d = pose2d
        obj_coords_msg.timestamp = self.time_since_start()
        obj_coords_msg.id = self.frame_count

        obj_features_msg = ObjFeatures()
        obj_features_msg.id = 0
        obj_features_msg.hu_2 = float(obj_features_dict.get('hu_2', 0))
        obj_features_msg.hu_3 = float(obj_features_dict.get('hu_3', 0))
        
        return obj_coords_msg, obj_features_msg
    
    def time_since_start(self):
            
        timestamp = time.time() - self.start_time

        return timestamp
 
def main(args=None):
    rclpy.init(args=args)
    camera = Camera()
    rclpy.spin(camera)
    camera.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()