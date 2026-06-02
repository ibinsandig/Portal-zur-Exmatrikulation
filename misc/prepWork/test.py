import os
import cv2 as cv
import numpy as np
import pandas as pd

def extract_features_from_contour(cnt):
    features = {}
    
    # 1. Basis-Werte
    features['area'] = cv.contourArea(cnt)
    features['perimeter'] = cv.arcLength(cnt, True)
    
    if features['area'] == 0 or features['perimeter'] == 0:
        return None
        
    # 2. Polygon Approximation & corners
    epsilon = 0.04 * features['perimeter']
    approx = cv.approxPolyDP(cnt, epsilon, True)
    features['corners'] = len(approx)
    
    # 3. Bounding Box & aspect ratio
    x, y, w, h = cv.boundingRect(cnt)
    features['aspect_ratio'] = float(w) / h
    
    # 4. Circularity
    if features['perimeter'] > 0:
        features['circularity'] = (4 * np.pi * features['area']) / (features['perimeter'] ** 2)
    else:
        features['circularity'] = 0.0
    
    # 5. Hu-Moments
    M = cv.moments(cnt)
    hu = cv.HuMoments(M).flatten()
    for i in range(7):
        features[f'hu_{i}'] = hu[i]
        
    return features

def build_dataset(base_dir, output_csv):
    data_list = []
    
    # Iteriere durch die Unterordner (cat, circle, square, unicorn)
    for label in os.listdir(base_dir):
        label_dir = os.path.join(base_dir, label)
        
        # Überspringe Dateien, falls sich welche im Hauptordner befinden
        if not os.path.isdir(label_dir):
            continue
            
        # Iteriere durch alle Bilder im jeweiligen Kategorie-Ordner
        for filename in os.listdir(label_dir):
            if not filename.endswith(".png"):
                continue
                
            img_path = os.path.join(label_dir, filename)
            img = cv.imread(img_path)
            
            if img is None:
                continue
                
            # Bild binarisieren, um Konturen zu finden
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            _, thresh = cv.threshold(gray, 127, 255, cv.THRESH_BINARY_INV)
            
            # Konturen extrahieren
            contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Wir gehen davon aus, dass die größte Kontur das gesuchte Objekt ist
                main_contour = max(contours, key=cv.contourArea)
                features = extract_features_from_contour(main_contour)
                
                if features is not None:
                    # Den Ordnernamen als Label anhängen
                    features['label'] = label
                    data_list.append(features)
                    
    # Liste in einen Pandas DataFrame umwandeln und als CSV speichern
    df = pd.DataFrame(data_list)
    df.to_csv(output_csv, index=False)
    
    print(f"Fertig! Es wurden {len(data_list)} Objekte verarbeitet.")
    print(f"Die Daten wurden in '{output_csv}' gespeichert.")

if __name__ == "__main__":
    # Relativer Pfad zu deinem 'obj'-Ordner
    IMAGE_DIR = "dev_pictures/obj"
    
    # Name der Ausgabe-Datei
    OUTPUT_FILE = "dataset_features.csv"
    
    build_dataset(IMAGE_DIR, OUTPUT_FILE)