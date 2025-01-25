# import requests
# import os
# import time

# LEFT_CAM_IP = "192.168.0.178:81"
# RIGHT_CAM_IP = "192.168.0.159:81"

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


import requests
import os
import time
import cv2
import threading
import numpy as np

LEFT_CAM_IP = "192.168.0.178:81"
RIGHT_CAM_IP = "192.168.0.159:81"

OUTPUT_DIR = "calib_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_video_frame(ip):
    url = f"http://{ip}/stream"
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print(f"Unable to open stream for {ip}")
        return None
    return cap



def capture_image(ip):
    """
    Capture a single image from the ESP32-CAM's HTTP server.
    """
    url = f"http://{ip}/capture"
    r = requests.get(url, timeout=5)
    if r.status_code == 200:
        return r.content  # JPEG bytes
    else:
        print(f"Error capturing from {ip} -> status code: {r.status_code}")
        return None

def display_feeds(left_cap, right_cap):
    """
    Continuously display video feeds from both cameras.
    """
    while True:
        # Read frames from left and right cameras
        ret_left, left_frame = left_cap.read()
        ret_right, right_frame = right_cap.read()

        # Ensure frames are valid before displaying
        if ret_left and left_frame is not None:
            cv2.imshow("Left Camera", left_frame)
        else:
            print("Failed to fetch frame from Left Camera")

        if ret_right and right_frame is not None:
            cv2.imshow("Right Camera", right_frame)
        else:
            print("Failed to fetch frame from Right Camera")

        # Close the video feeds when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def main():
    pair_count = 0
    print("Press ENTER to capture a new pair of images (q to quit).")

    # Start video feeds
    left_cap = fetch_video_frame(LEFT_CAM_IP)
    right_cap = fetch_video_frame(RIGHT_CAM_IP)

    if left_cap is None or right_cap is None:
        print("Error opening video feeds. Check camera connections.")
        return

    # Start a thread to display the video feeds
    threading.Thread(target=display_feeds, args=(left_cap, right_cap), daemon=True).start()

    while True:
        cmd = input(">")
        if cmd.lower() == 'q':
            break

        # Capture images from both cameras
        left_img_data = capture_image(LEFT_CAM_IP)
        time.sleep(0.2)
        right_img_data = capture_image(RIGHT_CAM_IP)

        if left_img_data and right_img_data:
            left_path = os.path.join(OUTPUT_DIR, f"L_{pair_count:03d}.jpg")
            right_path = os.path.join(OUTPUT_DIR, f"R_{pair_count:03d}.jpg")
            with open(left_path, 'wb') as f:
                f.write(left_img_data)
            with open(right_path, 'wb') as f:
                f.write(right_img_data)
            print(f"Captured pair #{pair_count} -> {left_path}, {right_path}")
            pair_count += 1
        else:
            print("Capture failed. Check camera connections/IP addresses.")

    # Release video feeds
    left_cap.release()
    right_cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
