import rclpy
from rclpy.node import Node
import cv2 as cv
from chaos_topics.msg import ObjCoords
from chaos_topics.msg import ObjFeatures
from geometry_msgs.msg import Pose2D
from camera.preprocessing import ImagePreprocessor
import time
import numpy as np
import config_vm as cfg

class Camera(Node):

    def __init__(self):
        super().__init__('camera')

        self.pub_obj_coords = self.create_publisher(ObjCoords, '/obj_coords', 10)
        self.pub_obj_festures = self.create_publisher(ObjFeatures, '/obj_features', 10)
        timer_time = 1/5   # nicht zu groß wählen, sonst gibt es Probleme mit der id vergabe

        path_camera = 4    # PortalCam = /dev/video4

        self.currend_id = 1
        self.last_pos_x = None

        try:
            self.PrePro = ImagePreprocessor()
        except Exception as e:
            self.get_logger().error(f'Fehler bei ImagePrepocessor: {str(e)}')
            raise e            

        try:
            self.img = cv.VideoCapture(path_camera)
            self.img.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
            self.img.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
        except Exception as e:
            self.get_logger().error(f'Fehler beim Initialisieren der Kamera: {str(e)}')
            raise e

        #self.img.set(cv.CAP_PROP_BUFFERSIZE, 0)

        self.get_logger().info("Legen Sie den Aruco-Marker ein")
        time.sleep(5)

        while(True):
            print('Setup Kamera...')

            try:
                self.PrePro.setup(self.read_camera())
            except Exception as e:
                self.get_logger().error(f'Fehler beim Lesen der Kamera: {str(e)}')
                raise e
                
            if self.PrePro.H_inv is not None:
                i=0
                while(i < 10):
                    self.get_logger().info("Entfernen Sie den Aruco-Marker")
                    time.sleep(1)
                    i += 1
                break
            

        self.data = self.create_timer(timer_time, self.timer_callback)
        self.get_logger().info('Kamera-Node gestartet!!!')

    def timer_callback(self):

            try:
                obj_coords_msg, obj_features_msg = self.process_img(self.read_camera())
                
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
        
        gray_image = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        img_rotated = cv.rotate(gray_image, 2)
        return img_rotated

    def process_img(self, frame):

        warped_image = self.PrePro.warp_image(frame)
        contours = self.PrePro.segment_object(warped_image)

        if not contours:
            self.get_logger().info('Keine Konturen gefunden')
            return None, None

        valid_contours = [cnt for cnt in contours if cv.contourArea(cnt) > 25]

        if not valid_contours:
            self.get_logger().info('Keine gültigen Konturen gefunden')
            return None, None

        objects = []
        for cnt in valid_contours:
            pixel_pos = self.PrePro.obj_position([cnt])
            if pixel_pos is None:
                continue
            world_pos = self.PrePro.pixel_to_world(pixel_pos)
            objects.append({'contour': cnt, 'world_pos': world_pos})

        if not objects:
            self.get_logger().warn('Keine Objekte mit Weltkoordinaten gefunden')
            return None, None

        print(objects)
        # Nur Objekte im sicheren Bereich
        valid_objects = [
            obj for obj in objects
            if cfg.X_MIN_SAFE <= obj['world_pos'][0] <= cfg.X_MAX_SAFE
        ]

        if not valid_objects:
            self.get_logger().info('Kein Objekt im sicheren Bereich')
            return None, None

        # Am weitesten fortgeschrittenes Objekt auswählen
        most_advanced = max(valid_objects, key=lambda obj: obj['world_pos'][0])

        world_pos = most_advanced['world_pos']

        # Features + Orientierung vom selben Objekt extrahieren
        obj_features_dict = self.PrePro.extract_features_from_contour(most_advanced['contour'])

        if obj_features_dict is None:
            self.get_logger().warn('Features konnten nicht extrahiert werden')
            return None, None

        pose2d = Pose2D()
        pose2d.x = float(world_pos[0])                                          
        pose2d.y = float(world_pos[1])                                          
        pose2d.theta = self.PrePro.extract_orientation(most_advanced['contour']) 

        obj_coords_msg = ObjCoords()
        obj_coords_msg.pose2d = pose2d
        obj_coords_msg.timestamp = time.time()


        obj_features_msg = ObjFeatures()
        obj_features_msg.hu_2 = float(obj_features_dict.get('hu_2', 0))
        obj_features_msg.hu_3 = float(obj_features_dict.get('hu_3', 0))

        assigned_id = self.assign_id(world_pos[0])
        obj_coords_msg.id = assigned_id
        obj_features_msg.id = assigned_id

        return obj_coords_msg, obj_features_msg

    def assign_id(self, x, threshold=30.0): # x = 200
        
        if self.last_pos_x is not None:     # = 220
            distance = abs(x - self.last_pos_x) # = 20

            if distance >= threshold:   # 20 >= 30  -> false
                self.currend_id += 1
                self.last_pos_x = x
                return self.currend_id

            else:
                self.last_pos_x = x
                return self.currend_id

        else:
            self.last_pos_x = x
            return self.currend_id

def main(args=None):
    rclpy.init(args=args)
    camera = Camera()
    rclpy.spin(camera)
    camera.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()