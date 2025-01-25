# import requests
# import os
# import time

# LEFT_CAM_IP = "192.168.1.50"
# RIGHT_CAM_IP = "192.168.1.51"

# OUTPUT_DIR = "calib_images"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# def capture_image(ip):
#     # Grab a frame from the ESP32-CAM's HTTP server
#     url = f"http://{ip}/capture"
#     r = requests.get(url, timeout=5)
#     if r.status_code == 200:
#         return r.content  # JPEG bytes
#     else:
#         print(f"Error capturing from {ip} -> status code: {r.status_code}")
#         return None

# def main():
#     pair_count = 0
#     print("Press ENTER to capture a new pair of images (q to quit).")

#     while True:
#         cmd = input(">")
#         if cmd.lower() == 'q':
#             break

#         # Capture from left
#         left_img_data = capture_image(LEFT_CAM_IP)
#         # short delay
#         time.sleep(0.2)
#         # Capture from right
#         right_img_data = capture_image(RIGHT_CAM_IP)

#         if left_img_data and right_img_data:
#             left_path = os.path.join(OUTPUT_DIR, f"L_{pair_count:03d}.jpg")
#             right_path = os.path.join(OUTPUT_DIR, f"R_{pair_count:03d}.jpg")
#             with open(left_path, 'wb') as f:
#                 f.write(left_img_data)
#             with open(right_path, 'wb') as f:
#                 f.write(right_img_data)
#             print(f"Captured pair #{pair_count} -> {left_path}, {right_path}")
#             pair_count += 1
#         else:
#             print("Capture failed. Check camera connections/IP addresses.")

# if __name__ == "__main__":
#     main()


# import cv2
# import numpy as np

# # Update the URLs of the ESP32-CAM streams
# url1 = 'http://192.168.0.159:81/stream'  # Camera 1 stream URL
# url2 = 'http://192.168.0.178:81/stream'  # Camera 2 stream URL

# # Initialize video capture for both cameras
# cap1 = cv2.VideoCapture(url1)
# cap2 = cv2.VideoCapture(url2)

# # Check if streams are accessible
# if not cap1.isOpened():
#     print("Error: Could not open stream for Camera 1")
# if not cap2.isOpened():
#     print("Error: Could not open stream for Camera 2")

# num = 0  # Image counter

# while True:
#     # Read frames from both cameras
#     ret1, img1 = cap1.read()
#     ret2, img2 = cap2.read()

#     # Check if frames are successfully captured
#     if ret1 and ret2:
#         # Combine frames side by side for easier visualization
#         combined_frame = np.hstack((img1, img2))
#         cv2.imshow('ESP32-CAM Feeds (Left | Right)', combined_frame)
#     elif ret1:
#         # Show only Camera 1 if Camera 2 fails
#         cv2.imshow('ESP32-CAM 1', img1)
#     elif ret2:
#         # Show only Camera 2 if Camera 1 fails
#         cv2.imshow('ESP32-CAM 2', img2)

#     # Keyboard controls
#     k = cv2.waitKey(5)
#     if k == 27:  # Press 'Esc' to exit
#         break
#     elif k == ord('s'):  # Press 's' to save images
#         if ret1:
#             cv2.imwrite(f'images/stereoLeft/imageL{num}.png', img1)
#         if ret2:
#             cv2.imwrite(f'images/stereoRight/imageR{num}.png', img2)
#         print(f"Images saved! Image number: {num}")
#         num += 1

# # Release resources and close all OpenCV windows
# cap1.release()
# cap2.release()
# cv2.destroyAllWindows()




import cv2
import numpy as np
import os

# Update the URLs of the ESP32-CAM streams
url1 = 'http://192.168.0.159:81/stream'  # Camera 1 stream URL
url2 = 'http://192.168.0.178:81/stream'  # Camera 2 stream URL

# Initialize video capture for both cameras
cap1 = cv2.VideoCapture(url1)
cap2 = cv2.VideoCapture(url2)

# Check if streams are accessible
if not cap1.isOpened():
    print("Error: Could not open stream for Camera 1")
if not cap2.isOpened():
    print("Error: Could not open stream for Camera 2")

# Create directories for saving images
os.makedirs('images/stereoLeft', exist_ok=True)
os.makedirs('images/stereoRight', exist_ok=True)

num = 0  # Image counter

while True:
    # Read frames from both cameras
    ret1, img1 = cap1.read()
    ret2, img2 = cap2.read()

    # Check if frames are successfully captured
    if ret1 and ret2:
        # Combine frames side by side for easier visualization
        combined_frame = np.hstack((img1, img2))
        cv2.imshow('ESP32-CAM Feeds (Left | Right)', combined_frame)
    elif ret1:
        # Show only Camera 1 if Camera 2 fails
        cv2.imshow('ESP32-CAM 1', img1)
    elif ret2:
        # Show only Camera 2 if Camera 1 fails
        cv2.imshow('ESP32-CAM 2', img2)

    # Keyboard controls
    k = cv2.waitKey(5)
    if k == 27:  # Press 'Esc' to exit
        break
    elif k == ord('s'):  # Press 's' to save images
        if ret1:
            cv2.imwrite(f'images/stereoLeft/imageL{num}.png', img1)
        if ret2:
            cv2.imwrite(f'images/stereoRight/imageR{num}.png', img2)
        print(f"Images saved! Image number: {num}")
        num += 1

# Release resources and close all OpenCV windows
cap1.release()
cap2.release()
cv2.destroyAllWindows()

