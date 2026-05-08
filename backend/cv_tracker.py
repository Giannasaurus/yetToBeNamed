import csv
from pathlib import Path

import cv2
import numpy as np


def _resize_frame(frame, max_dimension):
    height, width = frame.shape[:2]
    largest_dimension = max(height, width)
    if largest_dimension <= max_dimension:
        return frame, 1.0

    scale = max_dimension / largest_dimension
    resized = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    return resized, scale


def _red_marker_center(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red_1 = np.array([0, 80, 70])
    upper_red_1 = np.array([12, 255, 255])
    lower_red_2 = np.array([168, 80, 70])
    upper_red_2 = np.array([180, 255, 255])
    mask = cv2.bitwise_or(
        cv2.inRange(hsv, lower_red_1, upper_red_1),
        cv2.inRange(hsv, lower_red_2, upper_red_2),
    )
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 8:
            continue
        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            continue
        candidates.append((area, moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]))

    if not candidates:
        return None

    _, cx, cy = max(candidates, key=lambda item: item[0])
    return float(cx), float(cy)


def _write_tracking_outputs(output_dir, centers, fps):
    csv_path = output_dir / "tracking.csv"
    npy_path = output_dir / "centers.npy"
    dt_path = output_dir / "dt.npy"

    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y"])
        writer.writerows(centers)

    np.save(npy_path, centers)
    np.save(dt_path, 1 / fps)

    return csv_path, npy_path, dt_path


class TemplateTracker:
    def init(self, frame, bbox):
        self.bbox = tuple(map(int, bbox))
        x, y, w, h = self.bbox
        self.template = cv2.cvtColor(frame[y : y + h, x : x + w], cv2.COLOR_BGR2GRAY)
        if self.template.size == 0:
            raise RuntimeError("Initial tracking box is empty.")
        return True

    def update(self, frame):
        x, y, w, h = self.bbox
        margin = 100
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(frame.shape[1], x + w + margin)
        y2 = min(frame.shape[0], y + h + margin)

        search = cv2.cvtColor(frame[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
        if search.shape[0] < h or search.shape[1] < w:
            return False, self.bbox

        result = cv2.matchTemplate(search, self.template, cv2.TM_CCOEFF_NORMED)
        _, max_value, _, max_location = cv2.minMaxLoc(result)
        if max_value < 0.35:
            return False, self.bbox

        next_x = x1 + max_location[0]
        next_y = y1 + max_location[1]
        self.bbox = (next_x, next_y, w, h)
        return True, self.bbox


def create_tracker():
    if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerKCF_create"):
        return cv2.legacy.TrackerKCF_create()
    if hasattr(cv2, "TrackerKCF_create"):
        return cv2.TrackerKCF_create()
    if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerCSRT_create"):
        return cv2.legacy.TrackerCSRT_create()
    if hasattr(cv2, "TrackerCSRT_create"):
        return cv2.TrackerCSRT_create()
    return TemplateTracker()


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


def _analyze_red_marker(video_path, output_dir, max_frames, max_dimension, frame_stride):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError("Video failed to open.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30

    centers = []
    read_frames = 0
    processed_frames = 0
    smooth_cx, smooth_cy = None, None
    alpha = 0.35

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        read_frames += 1
        if read_frames % frame_stride != 0:
            continue
        if processed_frames >= max_frames:
            break

        frame, _ = _resize_frame(frame, max_dimension)
        processed_frames += 1
        center = _red_marker_center(frame)
        if center is None:
            continue

        cx, cy = center
        if smooth_cx is None:
            smooth_cx, smooth_cy = cx, cy
        else:
            smooth_cx = alpha * cx + (1 - alpha) * smooth_cx
            smooth_cy = alpha * cy + (1 - alpha) * smooth_cy

        centers.append((float(smooth_cx), float(smooth_cy)))

    cap.release()

    if len(centers) < 10:
        raise RuntimeError("Could not track enough red marker samples.")

    csv_path, npy_path, dt_path = _write_tracking_outputs(output_dir, centers, fps / frame_stride)

    return {
        "centers": [{"x": x, "y": y} for x, y in centers],
        "csv": str(csv_path),
        "npy": str(npy_path),
        "dt": frame_stride / fps,
        "fps": fps / frame_stride,
        "samples": len(centers),
    }


def analyze_video(
    video_path,
    bbox=None,
    output_dir=None,
    max_lost=25,
    max_frames=180,
    max_dimension=360,
    frame_stride=1,
):
    video_path = Path(video_path)
    output_dir = Path(output_dir or video_path.parent)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        return _analyze_red_marker(video_path, output_dir, max_frames, max_dimension, frame_stride)
    except RuntimeError:
        pass

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError("Video failed to open.")

    ret, frame = cap.read()
    if not ret:
        cap.release()
        raise RuntimeError("Cannot read first frame.")

    frame, _ = _resize_frame(frame, max_dimension)

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
    read_frames = 0
    processed_frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        read_frames += 1
        if read_frames % frame_stride != 0:
            continue
        if processed_frames >= max_frames:
            break

        frame, _ = _resize_frame(frame, max_dimension)
        processed_frames += 1

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

    csv_path, npy_path, dt_path = _write_tracking_outputs(output_dir, centers, fps / frame_stride)

    return {
        "centers": [{"x": x, "y": y} for x, y in centers],
        "csv": str(csv_path),
        "npy": str(npy_path),
        "dt": frame_stride / fps,
        "fps": fps / frame_stride,
        "samples": len(centers),
    }
