import torch
import cv2
import numpy as np
from torchvision.transforms import Compose
from PIL import Image

# Check if Metal backend is available for M1 optimization
device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
print(f"Using device: {device}")

# Load MiDaS model for depth estimation
def load_midas_model():
    model_type = "DPT_Large"  # or use "DPT_Hybrid" for faster inference
    model = torch.hub.load("intel-isl/MiDaS", model_type)
    model.to(device)
    model.eval()
    return model

# Preprocess frame for MiDaS
def preprocess_frame(frame):
    transform = torch.hub.load("intel-isl/MiDaS", "transforms").dpt_transform
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    input_image = Image.fromarray(frame_rgb)
    input_tensor = transform(input_image).unsqueeze(0).to(device)
    return input_tensor

# Estimate depth
def estimate_depth(model, input_tensor):
    with torch.no_grad():
        depth = model(input_tensor)
        depth = torch.nn.functional.interpolate(
            depth.unsqueeze(1),
            size=input_tensor.shape[2:],
            mode="bicubic",
            align_corners=False,
        ).squeeze().cpu().numpy()
    return depth

# Normalize depth map for visualization
def normalize_depth(depth_map):
    depth_min = depth_map.min()
    depth_max = depth_map.max()
    depth_map = (depth_map - depth_min) / (depth_max - depth_min)
    depth_map = (depth_map * 255).astype(np.uint8)
    return depth_map

# Main function for real-time depth estimation
def real_time_depth_estimation():
    # Load MiDaS model
    model = load_midas_model()

    # Start webcam feed
    cap = cv2.VideoCapture(0)  # Use 0 for default webcam
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Resize frame for faster processing
        frame_resized = cv2.resize(frame, (384, 384))  # Resize to model's input resolution
        input_tensor = preprocess_frame(frame_resized)

        # Estimate depth
        depth_map = estimate_depth(model, input_tensor)

        # Normalize depth map for display
        depth_map_normalized = normalize_depth(depth_map)

        # Display the original frame and depth map side by side
        depth_colored = cv2.applyColorMap(depth_map_normalized, cv2.COLORMAP_PLASMA)
        combined_display = np.hstack((frame_resized, depth_colored))

        cv2.imshow("Webcam Feed (Left) | Depth Map (Right)", combined_display)

        # Exit loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release webcam and close OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

# Run the real-time depth estimation
if __name__ == "__main__":
    real_time_depth_estimation()
