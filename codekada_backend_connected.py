# -*- coding: utf-8 -*-
"""Codekada_backend_connected.ipynb"""

import cv2
import numpy as np
import os
import csv

# -------------------------
# CONFIG
# -------------------------
video_path = "actualspring.mp4"
output_csv = "SPRING1.csv"

print("Working dir:", os.getcwd())

if not os.path.exists(video_path):
    raise FileNotFoundError("Video not found.")

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    raise RuntimeError("Video failed to open.")

ret, frame = cap.read()
if not ret:
    raise RuntimeError("Cannot read first frame.")

# -------------------------
# DISPLAY FIX
# -------------------------
display_scale = 0.6
cv2.namedWindow("Stable Physics Tracking", cv2.WINDOW_NORMAL)

# -------------------------
# TRACKER (FIXED)
# -------------------------
def create_tracker():
    # CSRT (best)
    if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerCSRT_create"):
        return cv2.legacy.TrackerCSRT_create()
    elif hasattr(cv2, "TrackerCSRT_create"):
        return cv2.TrackerCSRT_create()

    # KCF fallback (FIXED FOR NEW OPENCV)
    elif hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerKCF_create"):
        return cv2.legacy.TrackerKCF_create()
    elif hasattr(cv2, "TrackerKCF_create"):
        return cv2.TrackerKCF_create()

    else:
        raise RuntimeError("No tracker available. Install opencv-contrib-python")

# -------------------------
# ROI SELECTION
# -------------------------
roi_scale = 0.5
frame_small = cv2.resize(frame, (0, 0), fx=roi_scale, fy=roi_scale)

bbox_small = cv2.selectROI("Select Object", frame_small, False)
cv2.destroyAllWindows()

x, y, w, h = bbox_small

bbox = (
    int(x / roi_scale),
    int(y / roi_scale),
    int(w / roi_scale),
    int(h / roi_scale)
)

tracker = create_tracker()
tracker.init(frame, bbox)

# -------------------------
# STATE
# -------------------------
centers = []
trail = []

lost_frames = 0
max_lost = 25

fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0:
    fps = 30

smooth_cx, smooth_cy = None, None
vx, vy = 0.0, 0.0

alpha = 0.35
beta = 0.75

# -------------------------
# MAIN LOOP
# -------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    success, bbox = tracker.update(frame)

    if success:
        lost_frames = 0

        x, y, w, h = map(int, bbox)

        roi = frame[y:y+h, x:x+w]
        if roi.size == 0:
            continue

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        _, mask = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        M = cv2.moments(mask)

        if M["m00"] != 0:
            dx = M["m10"] / M["m00"]
            dy = M["m01"] / M["m00"]
        else:
            dx, dy = w / 2, h / 2

        cx = x + dx
        cy = y + dy

        if len(centers) > 2:
            px, py = centers[-1]
            if abs(cx - px) > 150 or abs(cy - py) > 150:
                continue

        if smooth_cx is None:
            smooth_cx, smooth_cy = cx, cy
            vx, vy = 0.0, 0.0
        else:
            vx = beta * vx + (1 - beta) * (cx - smooth_cx)
            vy = beta * vy + (1 - beta) * (cy - smooth_cy)

            smooth_cx += vx
            smooth_cy += vy

            smooth_cx = alpha * cx + (1 - alpha) * smooth_cx
            smooth_cy = alpha * cy + (1 - alpha) * smooth_cy

        centers.append((smooth_cx, smooth_cy))
        trail.append((int(smooth_cx), int(smooth_cy)))

        if len(trail) > 500:
            trail = trail[-500:]

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.circle(
            frame,
            (int(smooth_cx), int(smooth_cy)),
            4,
            (0, 0, 255),
            -1
        )

        start = max(1, len(trail) - 120)
        for i in range(start, len(trail)):
            cv2.line(frame, trail[i - 1], trail[i], (255, 0, 0), 2)

    else:
        lost_frames += 1

        cv2.putText(
            frame,
            f"Lost ({lost_frames}/{max_lost})",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

        if lost_frames > max_lost:
            bbox_small = cv2.selectROI("Re-select object", frame, False)
            cv2.destroyAllWindows()

            x, y, w, h = bbox_small
            bbox = (x, y, w, h)

            tracker = create_tracker()
            tracker.init(frame, bbox)

            lost_frames = 0
            trail.clear()
            smooth_cx, smooth_cy = None, None
            vx, vy = 0.0, 0.0

    frame_display = cv2.resize(
        frame, (0, 0), fx=display_scale, fy=display_scale
    )
    cv2.imshow("Stable Physics Tracking", frame_display)

    wait_time = max(1, int(1000 / fps))
    if cv2.waitKey(wait_time) & 0xFF == ord('q'):
        break

# -------------------------
# SAVE DATA
# -------------------------
cap.release()
cv2.destroyAllWindows()

if len(centers) > 0:
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y"])
        for c in centers:
            writer.writerow([c[0], c[1]])

    np.save("centers.npy", centers)
    np.save("dt.npy", 1 / fps)

    print("\nDATA EXPORT COMPLETE")
    print("--------------------")
    print("samples:", len(centers))
    print("fps:", fps)
    print("saved csv:", output_csv)
    print("saved npy: centers.npy, dt.npy")

else:
    print("No data collected.")