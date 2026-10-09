"""Complete, sample-aligned windows. Never pad or join separate recordings."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class WindowPlan:
    window_s: float = 10.0
    hop_s: float = 1.0

    def spans(self, sample_count, fs):
        if not all(math.isfinite(v) and v > 0 for v in (fs, self.window_s, self.hop_s)):
            raise ValueError("Window duration, step and sample rate must be positive")
        if self.hop_s > self.window_s:
            raise ValueError("Window step must not exceed window duration")
        width, hop = round(self.window_s * fs), round(self.hop_s * fs)
        if width < 2 or hop < 1:
            raise ValueError("Window or step is shorter than the sample resolution")
        if sample_count < width:
            return []
        starts = list(range(0, sample_count - width + 1, hop))
        # Cover the final samples with a full end-aligned window, without padding.
        if starts[-1] != sample_count - width:
            starts.append(sample_count - width)
        return [(start, start + width) for start in starts]
