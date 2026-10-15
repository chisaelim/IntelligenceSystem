from dataclasses import dataclass


@dataclass
class Detection:
    track_id: int
    label: str
    confidence: float
    box: tuple  # x1, y1, x2, y2 in pixels
