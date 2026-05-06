import csv
from pathlib import Path

import cv2
import numpy as np


def create_tracker():
    if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerCSRT_create"):
        return cv2.legacy.TrackerCSRT_create()
    if hasattr(cv2, "TrackerCSRT_create"):
        return cv2.TrackerCSRT_create()
    if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerKCF_create"):
        return cv2.legacy.TrackerKCF_create()
    if hasattr(cv2, "TrackerKCF_create"):
        return cv2.TrackerKCF_create()
    raise RuntimeError("No tracker available. Install opencv-contrib-python.")


def _auto_bbox(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise RuntimeError("Could not find a trackable object in the first frame.")

    frame_area = frame.shape[0] * frame.shape[1]
    candidates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if 25 <= area <= frame_area * 0.2:
            candidates.append((area, x, y, w, h))

    if not candidates:
        raise RuntimeError("Could not isolate a reasonable tracking box.")

    _, x, y, w, h = max(candidates, key=lambda item: item[0])
    padding = 12
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(frame.shape[1] - x, w + padding * 2)
    h = min(frame.shape[0] - y, h + padding * 2)
    return (x, y, w, h)


def analyze_video(video_path, bbox=None, output_dir=None, max_lost=25):
    video_path = Path(video_path)
    output_dir = Path(output_dir or video_path.parent)
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError("Video failed to open.")

    ret, frame = cap.read()
    if not ret:
        cap.release()
        raise RuntimeError("Cannot read first frame.")

    if bbox is None:
        bbox = _auto_bbox(frame)

    tracker = create_tracker()
    tracker.init(frame, tuple(map(int, bbox)))

    centers = []
    trail = []
    lost_frames = 0

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30

    smooth_cx, smooth_cy = None, None
    vx, vy = 0.0, 0.0
    alpha = 0.35
    beta = 0.75

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        success, bbox = tracker.update(frame)
        if not success:
            lost_frames += 1
            if lost_frames > max_lost:
                break
            continue

        lost_frames = 0
        x, y, w, h = map(int, bbox)
        roi = frame[y : y + h, x : x + w]
        if roi.size == 0:
            continue

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        moments = cv2.moments(mask)
        if moments["m00"] != 0:
            dx = moments["m10"] / moments["m00"]
            dy = moments["m01"] / moments["m00"]
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

        centers.append((float(smooth_cx), float(smooth_cy)))
        trail.append((int(smooth_cx), int(smooth_cy)))
        if len(trail) > 500:
            trail = trail[-500:]

    cap.release()

    csv_path = output_dir / "tracking.csv"
    npy_path = output_dir / "centers.npy"
    dt_path = output_dir / "dt.npy"

    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y"])
        writer.writerows(centers)

    np.save(npy_path, centers)
    np.save(dt_path, 1 / fps)

    return {
        "centers": [{"x": x, "y": y} for x, y in centers],
        "csv": str(csv_path),
        "npy": str(npy_path),
        "dt": 1 / fps,
        "fps": fps,
        "samples": len(centers),
    }
