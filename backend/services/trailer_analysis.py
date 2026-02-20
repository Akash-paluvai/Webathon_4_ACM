"""
Phase-4 Trailer Feature Extraction
Uses pre-trained / rule-based libraries only (OpenCV, librosa, ffmpeg).
No ML training. No DB writes. Returns a plain dict of features.
"""

import os
import subprocess
import tempfile
from typing import Dict, Any

import cv2
import numpy as np
import librosa


def _extract_audio(video_path: str, audio_path: str) -> bool:
    """Extract audio from a video file using ffmpeg. Returns True on success."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", video_path,
                "-vn",                # no video
                "-acodec", "pcm_s16le",
                "-ar", "22050",       # sample rate librosa expects
                "-ac", "1",           # mono
                audio_path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _analyse_video(video_path: str) -> Dict[str, Any]:
    """
    Analyse the video track with OpenCV:
    - average_shot_length_sec
    - scene_change_frequency (changes per second)
    - average_brightness (0-255 scale)
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    prev_hist = None
    scene_changes: list[int] = []
    brightness_values: list[float] = []

    # Threshold for histogram diff to count as a scene change.
    SCENE_THRESHOLD = 0.6

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # --- brightness (mean pixel intensity) ---
        brightness_values.append(float(np.mean(gray)))

        # --- scene change detection via histogram correlation ---
        hist = cv2.calcHist([gray], [0], None, [64], [0, 256])
        cv2.normalize(hist, hist)

        if prev_hist is not None:
            corr = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
            if corr < SCENE_THRESHOLD:
                scene_changes.append(frame_idx)

        prev_hist = hist
        frame_idx += 1

    cap.release()

    duration_sec = total_frames / fps if fps > 0 else 0.0
    num_scenes = len(scene_changes) + 1  # segments between cuts

    avg_shot_length = duration_sec / num_scenes if num_scenes > 0 else duration_sec
    scene_change_freq = len(scene_changes) / duration_sec if duration_sec > 0 else 0.0
    avg_brightness = float(np.mean(brightness_values)) if brightness_values else 0.0

    return {
        "total_frames": total_frames,
        "fps": round(fps, 2),
        "duration_sec": round(duration_sec, 2),
        "scene_change_count": len(scene_changes),
        "average_shot_length_sec": round(avg_shot_length, 2),
        "scene_change_frequency_per_sec": round(scene_change_freq, 4),
        "average_brightness": round(avg_brightness, 2),
    }


def _analyse_audio(video_path: str) -> Dict[str, Any]:
    """
    Extract audio via ffmpeg, then compute energy features with librosa.
    Returns an empty dict if audio extraction fails (e.g. silent trailer).
    """
    tmp_wav = None
    try:
        tmp_fd, tmp_wav = tempfile.mkstemp(suffix=".wav")
        os.close(tmp_fd)

        if not _extract_audio(video_path, tmp_wav):
            return {"audio_available": False}

        y, sr = librosa.load(tmp_wav, sr=22050, mono=True)
        if len(y) == 0:
            return {"audio_available": False}

        rms = librosa.feature.rms(y=y)[0]
        audio_energy_mean = float(np.mean(rms))
        audio_energy_max = float(np.max(rms))
        audio_energy_std = float(np.std(rms))

        return {
            "audio_available": True,
            "audio_energy_mean": round(audio_energy_mean, 6),
            "audio_energy_max": round(audio_energy_max, 6),
            "audio_energy_std": round(audio_energy_std, 6),
        }

    finally:
        if tmp_wav and os.path.exists(tmp_wav):
            os.remove(tmp_wav)


def extract_trailer_features(video_path: str) -> Dict[str, Any]:
    """
    Main entry point.
    Accepts a path to an MP4 trailer file and returns a flat dict of features:
        - total_frames, fps, duration_sec
        - scene_change_count, average_shot_length_sec, scene_change_frequency_per_sec
        - average_brightness
        - audio_energy_mean, audio_energy_max, audio_energy_std
    No models are trained. No database writes.
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    video_features = _analyse_video(video_path)
    audio_features = _analyse_audio(video_path)

    return {**video_features, **audio_features}