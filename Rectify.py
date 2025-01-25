import cv2
import numpy as np

# Directories
OUTPUT_DIR = "Calibration_Files"

def draw_epipolar_lines(image, line_spacing=20, color=(255, 0, 0)):
    """
    Draw horizontal epipolar lines for visualization.
    :param image: The rectified image.
    :param line_spacing: Spacing between lines in pixels.
    :param color: Line color in BGR format.
    :return: Image with epipolar lines drawn.
    """
    img_with_lines = image.copy()
    for y in range(0, img_with_lines.shape[0], line_spacing):
        cv2.line(img_with_lines, (0, y), (img_with_lines.shape[1], y), color, 1)
    return img_with_lines

# Load calibration data
cameraMatrixL = np.loadtxt(f"{OUTPUT_DIR}/CmL.txt")
distCoeffsL = np.loadtxt(f"{OUTPUT_DIR}/DcL.txt")
cameraMatrixR = np.loadtxt(f"{OUTPUT_DIR}/CmR.txt")
distCoeffsR = np.loadtxt(f"{OUTPUT_DIR}/DcR.txt")
RL = np.loadtxt(f"{OUTPUT_DIR}/RectifL.txt")
RR = np.loadtxt(f"{OUTPUT_DIR}/RectifR.txt")
PL = np.loadtxt(f"{OUTPUT_DIR}/ProjL.txt")
PR = np.loadtxt(f"{OUTPUT_DIR}/ProjR.txt")

# Load binary maps
mapLx = np.load(f"{OUTPUT_DIR}/umapL.npy")
mapLy = np.load(f"{OUTPUT_DIR}/rmapL.npy")
mapRx = np.load(f"{OUTPUT_DIR}/umapR.npy")
mapRy = np.load(f"{OUTPUT_DIR}/rmapR.npy")

# Load a pair of images
imgL = cv2.imread("calib_images/stereoLeft/imageL0.png", cv2.IMREAD_GRAYSCALE)
imgR = cv2.imread("calib_images/stereoRight/imageR0.png", cv2.IMREAD_GRAYSCALE)

if imgL is None or imgR is None:
    print("Error: Could not load the input images")
    exit()

# Rectify images
rectifiedL = cv2.remap(imgL, mapLx, mapLy, cv2.INTER_LINEAR)
rectifiedR = cv2.remap(imgR, mapRx, mapRy, cv2.INTER_LINEAR)

# Draw epipolar lines for validation
rectifiedL_with_lines = draw_epipolar_lines(rectifiedL)
rectifiedR_with_lines = draw_epipolar_lines(rectifiedR)

# Show rectified images with epipolar lines
cv2.imshow("Rectified Left with Epipolar Lines", rectifiedL_with_lines)
cv2.imshow("Rectified Right with Epipolar Lines", rectifiedR_with_lines)

# Save rectified images for reference
cv2.imwrite(f"{OUTPUT_DIR}/Rectified_Left.png", rectifiedL_with_lines)
cv2.imwrite(f"{OUTPUT_DIR}/Rectified_Right.png", rectifiedR_with_lines)

# Generate disparity map for depth estimation using StereoSGBM
window_size = 5
stereo = cv2.StereoSGBM_create(
    minDisparity=0,
    numDisparities=16,  # Must be divisible by 16
    blockSize=window_size,
    P1=8 * 3 * window_size ** 2,
    P2=32 * 3 * window_size ** 2,
    disp12MaxDiff=1,
    uniquenessRatio=10,
    speckleWindowSize=100,
    speckleRange=32,
)

# Compute disparity map
disparity = stereo.compute(rectifiedL, rectifiedR)

# Normalize disparity map for visualization
disparity_normalized = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

# Show and save the disparity map
cv2.imshow("Disparity Map - SGBM", disparity_normalized)
cv2.imwrite(f"{OUTPUT_DIR}/Disparity_Map_SGBM.png", disparity_normalized)

cv2.waitKey(0)
cv2.destroyAllWindows()
