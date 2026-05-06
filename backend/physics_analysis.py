import numpy as np
from scipy.signal import find_peaks, savgol_filter


def _savgol_window(length):
    if length < 5:
        raise ValueError("At least 5 tracked samples are required for physics analysis.")

    window = min(11, length // 2 * 2 - 1)
    return max(window, 5)


def _dominant_omega(y, fps):
    fft = np.fft.fft(y)
    freqs = np.fft.fftfreq(len(y), d=1 / fps)
    mask = freqs > 0
    if not np.any(mask):
        raise ValueError("Could not estimate frequency from tracked motion.")

    dominant_freq = freqs[mask][np.argmax(np.abs(fft[mask]))]
    return float(2 * np.pi * dominant_freq)


def _estimate_damping(y, t):
    peaks, _ = find_peaks(y, distance=10)
    peaks_t = t[peaks]
    peaks_y = np.abs(y[peaks])

    if len(peaks_y) < 2:
        raise ValueError("Could not estimate damping; not enough motion peaks detected.")

    valid = peaks_y > 0.1 * np.max(peaks_y)
    peaks_t = peaks_t[valid]
    peaks_y = peaks_y[valid]

    if len(peaks_y) < 2:
        raise ValueError("Could not estimate damping; peaks are too weak after filtering.")

    gamma = -np.polyfit(peaks_t, np.log(peaks_y + 1e-12), 1)[0]
    return float(gamma), peaks_t, peaks_y


def _estimate_segment(y, t, fps):
    omega = _dominant_omega(y, fps)
    gamma, _, _ = _estimate_damping(y, t)
    return omega, gamma


def analyze_physics(centers, fps, mass):
    if mass <= 0:
        raise ValueError("Mass must be positive.")

    centers = np.array([(point["x"], point["y"]) for point in centers], dtype=float)
    if len(centers) < 10:
        raise ValueError("Not enough tracked samples for physics analysis.")

    t = np.arange(len(centers)) / fps
    y = -centers[:, 1]

    y_smooth = savgol_filter(y, _savgol_window(len(y)), 3)
    y0 = y_smooth - np.mean(y_smooth)
    trend = np.polyfit(t, y0, 1)
    y0 = y0 - (trend[0] * t + trend[1])

    velocity = np.gradient(y0, 1 / fps)

    omega = _dominant_omega(y0, fps)
    gamma, peaks_t, peaks_y = _estimate_damping(y0, t)
    omega0 = float(np.sqrt(omega**2 + gamma**2))
    zeta = float(gamma / omega0)

    if zeta < 1:
        regime = "Underdamped"
    elif np.isclose(zeta, 1, atol=0.05):
        regime = "Critically damped"
    else:
        regime = "Overdamped"

    spring_constant = float(mass * omega0**2)

    y_damped_removed = y0 * np.exp(gamma * t)
    matrix = np.column_stack([np.cos(omega * t), np.sin(omega * t)])
    coef, _, _, _ = np.linalg.lstsq(matrix, y_damped_removed, rcond=None)
    b, c = coef

    amplitude = float(np.sqrt(b**2 + c**2))
    phase = float(np.arctan2(-c, b))
    y_model = np.exp(-gamma * t) * amplitude * np.cos(omega * t + phase)

    energy = 0.5 * mass * velocity**2 + 0.5 * spring_constant * y0**2

    rmse = float(np.sqrt(np.mean((y0 - y_model) ** 2)))
    nrmse = float(rmse / (np.max(y0) - np.min(y0)))

    mid = len(y0) // 2
    omega_drift_percent = None
    gamma_drift_percent = None
    if mid >= 10 and len(y0) - mid >= 10:
        try:
            w1, g1 = _estimate_segment(y0[:mid], t[:mid], fps)
            w2, g2 = _estimate_segment(y0[mid:], t[mid:], fps)
            if w2 != 0:
                omega_drift_percent = float(abs(w1 - w2) / abs(w2) * 100)
            if g2 != 0:
                gamma_drift_percent = float(abs(g1 - g2) / abs(g2) * 100)
        except ValueError:
            pass

    return {
        "mass": float(mass),
        "omega": omega,
        "omega0": omega0,
        "gamma": gamma,
        "springConstant": spring_constant,
        "zeta": zeta,
        "regime": regime,
        "phase": phase,
        "amplitude": amplitude,
        "rmse": rmse,
        "nrmse": nrmse,
        "omegaDriftPercent": omega_drift_percent,
        "gammaDriftPercent": gamma_drift_percent,
        "energy": {
            "min": float(np.min(energy)),
            "max": float(np.max(energy)),
            "mean": float(np.mean(energy)),
        },
        "peakCount": int(len(peaks_y)),
        "series": {
            "time": t.tolist(),
            "displacement": y0.tolist(),
            "model": y_model.tolist(),
            "velocity": velocity.tolist(),
            "energy": energy.tolist(),
            "peaks": [{"time": float(x), "value": float(y)} for x, y in zip(peaks_t, peaks_y)],
        },
    }
