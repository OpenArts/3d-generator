from __future__ import annotations


def apply_strength_curve(value: float, curve: float = 1.0) -> float:
    value = max(0.0, min(1.0, value))
    if curve <= 0:
        return value
    return value ** curve
