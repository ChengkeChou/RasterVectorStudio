from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image
from skimage import color, segmentation, filters


@dataclass
class SegmentParams:
    n_segments: int = 400
    compactness: float = 10.0


def segment_and_sample_colors(img_path: Path, params: SegmentParams) -> Tuple[np.ndarray, np.ndarray]:
    """示例：SLIC 分割并对每个超像素取均值颜色。
    返回 (labels, mean_colors[labels])，作为后续填充/描边的参考。
    """
    im = Image.open(img_path).convert("RGB")
    arr = np.asarray(im)
    lab = color.rgb2lab(arr)
    labels = segmentation.slic(lab, n_segments=params.n_segments, compactness=params.compactness, start_label=0)
    # 计算每个标签的平均颜色
    mean_colors = np.zeros((labels.max()+1, 3), dtype=np.float64)
    counts = np.bincount(labels.ravel())
    for c in range(3):
        sums = np.bincount(labels.ravel(), weights=arr[..., c].ravel())
        mean_colors[:, c] = sums / np.maximum(counts, 1)
    return labels, mean_colors
