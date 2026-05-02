import cv2
import numpy as np
import os

def detect_and_segment_objects(image_path):
    """
    Loads an image, performs object detection/segmentation, and returns detection results.
    
    NOTE: This function is a placeholder. In a real-world scenario, you would integrate
    a specific model (e.g., YOLO, Mask R-CNN) here.
    
    Args:
        image_path (str): Path to the input image.
        
    Returns:
        list: A list of dictionaries, where each dict represents an object
              with 'center' (x, y) and 'mask' (segmentation mask).
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    # 1. Load the image
    img = cv2.imread(image_path)
    if img is None:
        raise IOError(f"Could not read image at {image_path}. Check file format or permissions.")
    
    print(f"Image loaded successfully. Dimensions: {img.shape[:2]}...")

    # --- PLACEHOLDER FOR REAL DETECTION/SEGMENTATION LOGIC ---
    # Replace this section with actual model inference (e.g., running a deep learning model)
    # For demonstration, we assume one detection and generate a mock result.
    
    # Mock detection result: assume we found one object centered at (200, 150)
    detected_objects = []
    mock_center = (200, 150)
    mock_mask = np.zeros_like(img)
    # Simulate a small mask area for the mock object
    mock_mask[140:160, 190:210] = 255 
    
    detected_objects.append({
        'center': mock_center,
        'mask': mock_mask,
        'bbox': (190, 140, 210, 160) # Bbox (x_min, y_min, x_max, y_max)
    })
    
    return detected_objects, img

def process_image_and_detect_centroids(image_path):
    """
    Performs object detection, calculates the centroid for each object,
    and draws them onto the original image.
    
    Args:
        image_path (str): Path to the input image.
        
    Returns:
        np.array: The image with centroids drawn.
    """
    try:
        detected_objects, original_img = detect_and_segment_objects(image_path)
        
        # Create a copy to draw the results on
        output_img = original_img.copy()
        
        for obj in detected_objects:
            center_x, center_y = obj['center']
            
            # 1. Draw Bounding Box (Optional visualization)
            x_min, y_min, x_max, y_max = obj['bbox']
            cv2.rectangle(output_img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            
            # 2. Draw Centroid/Midpoint
            cv2.circle(output_img, (center_x, center_y), 5, (255, 0, 0), -1)
            
            # 3. Label the centroid (Optional)
            cv2.putText(output_img, 'Center', (center_x + 10, center_y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # 4. Use the segmentation mask for visualization (If needed)
            # You might blend the mask into the output image here
            
            print(f"Centroid detected at: ({center_x}, {center_y})")

        # Display the resulting image (or save it)
        cv2.imshow("Object Detection with Centroids", output_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return output_img

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None
    except IOError as e:
        print(f"Error processing image: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# --- Example Usage ---
if __name__ == "__main__":
    # NOTE: Use the provided image file path for testing the functionality.
    image_file_path = "misc/vision/bild_49.jpg" 
    
    # To run this script, ensure 'misc/vision/bild_49.jpg' exists relative to where you execute it.
    
    print("--- Starting Object Detection Process ---")
    
    processed_image = process_image_and_detect_centroids(image_file_path)
    
    # If successful, you might want to save the output
    if processed_image is not None:
        output_path = "output_segmented.jpg"
        cv2.imwrite(output_path, processed_image)
        print(f"Process finished. Output saved to {output_path}")