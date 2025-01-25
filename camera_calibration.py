import cv2
import numpy as np
import glob
import os

# Adjust these to match your checkerboard
CHECKERBOARD = (9, 6)  # (columns, rows) of interior corners
SQUARE_SIZE = 25.0     # millimeters per square side (or any consistent unit)

# Paths
CALIB_IMAGES_DIR = "calib_images"
LEFT_IMAGES_DIR = os.path.join(CALIB_IMAGES_DIR, "stereoLeft")
RIGHT_IMAGES_DIR = os.path.join(CALIB_IMAGES_DIR, "stereoRight")
OUTPUT_DIR = "Calibration_Files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    # Prepare object points (like [0,0,0], [1,0,0], [2,0,0] ... in real scale)
    objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    objp *= SQUARE_SIZE

    # Arrays to store detected corners
    objpoints = []   # 3d points in real world
    imgpointsL = []  # 2d points in left image plane
    imgpointsR = []  # 2d points in right image plane

    # Get list of left/right images
    left_imgs = sorted(glob.glob(os.path.join(LEFT_IMAGES_DIR, "imageL*.png")))
    right_imgs = sorted(glob.glob(os.path.join(RIGHT_IMAGES_DIR, "imageR*.png")))

    # Ensure that the number of left and right images match
    assert len(left_imgs) == len(right_imgs), "Mismatch in number of left and right images"

    for (lf, rf) in zip(left_imgs, right_imgs):
        imgL = cv2.imread(lf, cv2.IMREAD_GRAYSCALE)
        imgR = cv2.imread(rf, cv2.IMREAD_GRAYSCALE)

        if imgL is None or imgR is None:
            print(f"Error reading images: {lf}, {rf}")
            continue

        retL, cornersL = cv2.findChessboardCorners(imgL, CHECKERBOARD, None)
        retR, cornersR = cv2.findChessboardCorners(imgR, CHECKERBOARD, None)

        if retL and retR:
            # Refine corners
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            cornersL = cv2.cornerSubPix(imgL, cornersL, (11, 11), (-1, -1), criteria)
            cornersR = cv2.cornerSubPix(imgR, cornersR, (11, 11), (-1, -1), criteria)

            # Save the points
            objpoints.append(objp)
            imgpointsL.append(cornersL)
            imgpointsR.append(cornersR)
        else:
            print(f"Chessboard corners not detected in images: {lf}, {rf}")

    # Check if sufficient points were collected
    if not objpoints:
        print("No valid chessboard corners were found in any image pair.")
        return

    # Image shape
    h, w = imgL.shape[:2]

    # Initialize calibration matrices
    cameraMatrixL = np.zeros((3, 3))
    distCoeffsL = np.zeros((5, 1))
    cameraMatrixR = np.zeros((3, 3))
    distCoeffsR = np.zeros((5, 1))

    # Stereo calibration
    criteria_stereo = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5)
    ret, cameraMatrixL, distCoeffsL, cameraMatrixR, distCoeffsR, R, T, E, F = cv2.stereoCalibrate(
        objpoints,
        imgpointsL,
        imgpointsR,
        cameraMatrixL,
        distCoeffsL,
        cameraMatrixR,
        distCoeffsR,
        (w, h),
        criteria=criteria_stereo,
        flags=0
    )

    print("Stereo calibration RMS error =", ret)

    # Stereo Rectification
    # alpha=0 means crop image to remove all black borders
    rectify_scale = 0  
    RL, RR, PL, PR, Q, roiL, roiR = cv2.stereoRectify(
        cameraMatrixL, distCoeffsL,
        cameraMatrixR, distCoeffsR,
        (w, h),
        R, T,
        alpha=rectify_scale
    )

    # Compute undistort+rectify maps
    mapLx, mapLy = cv2.initUndistortRectifyMap(cameraMatrixL, distCoeffsL, RL, PL, (w, h), cv2.CV_32FC1)
    mapRx, mapRy = cv2.initUndistortRectifyMap(cameraMatrixR, distCoeffsR, RR, PR, (w, h), cv2.CV_32FC1)

    # ---------------------------
    # Save all calibration data
    # Use float format for matrices/distortion (fmt='%.6f' is typical)
    # Use integer format for ROI (fmt='%d') to store them as int
    # ---------------------------

    # Save camera and distortion
    np.savetxt(os.path.join(OUTPUT_DIR, "CmL.txt"), cameraMatrixL, fmt='%.6f')
    np.savetxt(os.path.join(OUTPUT_DIR, "DcL.txt"), distCoeffsL,  fmt='%.6f')
    np.savetxt(os.path.join(OUTPUT_DIR, "CmR.txt"), cameraMatrixR, fmt='%.6f')
    np.savetxt(os.path.join(OUTPUT_DIR, "DcR.txt"), distCoeffsR,  fmt='%.6f')

    # Save rectification & projection
    np.savetxt(os.path.join(OUTPUT_DIR, "RectifL.txt"), RL, fmt='%.6f')
    np.savetxt(os.path.join(OUTPUT_DIR, "RectifR.txt"), RR, fmt='%.6f')
    np.savetxt(os.path.join(OUTPUT_DIR, "ProjL.txt"), PL,   fmt='%.6f')
    np.savetxt(os.path.join(OUTPUT_DIR, "ProjR.txt"), PR,   fmt='%.6f')

    # Save rotation, translation, essential & fundamental
    np.savetxt(os.path.join(OUTPUT_DIR, "Rtn.txt"),  R, fmt='%.6f')
    np.savetxt(os.path.join(OUTPUT_DIR, "Trnsl.txt"), T, fmt='%.6f')
    np.savetxt(os.path.join(OUTPUT_DIR, "Q.txt"),    Q, fmt='%.6f')
    np.savetxt(os.path.join(OUTPUT_DIR, "E.txt"),    E, fmt='%.6f')
    np.savetxt(os.path.join(OUTPUT_DIR, "F.txt"),    F, fmt='%.6f')

    # Save the ROI with integer formatting
    np.savetxt(os.path.join(OUTPUT_DIR, "ROIL.txt"), roiL, fmt='%d')
    np.savetxt(os.path.join(OUTPUT_DIR, "ROIR.txt"), roiR, fmt='%d')

    # Save the float32 remap arrays as text (if you want) but can be large
    # For text, we can also store with e.g. '%.6f'
    np.savetxt(os.path.join(OUTPUT_DIR, "umapL.txt"), mapLx, fmt='%.6f')
    np.savetxt(os.path.join(OUTPUT_DIR, "rmapL.txt"), mapLy, fmt='%.6f')
    np.savetxt(os.path.join(OUTPUT_DIR, "umapR.txt"), mapRx, fmt='%.6f')
    np.savetxt(os.path.join(OUTPUT_DIR, "rmapR.txt"), mapRy, fmt='%.6f')

    # Additionally, save binary .npy files for the remap arrays (preferred for speed/accuracy)
    np.save(os.path.join(OUTPUT_DIR, "umapL.npy"), mapLx)
    np.save(os.path.join(OUTPUT_DIR, "rmapL.npy"), mapLy)
    np.save(os.path.join(OUTPUT_DIR, "umapR.npy"), mapRx)
    np.save(os.path.join(OUTPUT_DIR, "rmapR.npy"), mapRy)

    print(f"\nStereo calibration RMS error = {ret:.6f}")
    print(f"Calibration files saved to '{OUTPUT_DIR}'")
    print("Done.")

if __name__ == "__main__":
    main()
