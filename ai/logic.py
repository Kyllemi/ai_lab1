import math
from PIL import ImageDraw


# вектор
def extract_feature_vector(pil_img, rows, cols, threshold=128):
    gray = pil_img.convert("L")
    w, h = gray.size
    pixels = gray.load()
    r_step, c_step = h / rows, w / cols
    abs_v = []

    for r in range(rows):
        for c in range(cols):
            y0, y1 = (
                int(r * r_step),
                h if r == rows - 1 else int((r + 1) * r_step),
            )
            x0, x1 = (
                int(c * c_step),
                w if c == cols - 1 else int((c + 1) * c_step),
            )
            count = sum(
                1
                for y in range(y0, y1)
                for x in range(x0, x1)
                if pixels[x, y] < threshold
            )
            abs_v.append(count)
    max_v = max(abs_v) if abs_v and max(abs_v) > 0 else 1
    return abs_v, [round(v / max_v, 4) for v in abs_v]


# сітка
def draw_grid_on_image(image, rows, cols):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    w, h = img.size
    for i in range(1, cols):
        draw.line([(int(i * w / cols), 0), (int(i * w / cols), h)], fill="red")
    for i in range(1, rows):
        draw.line([(0, int(i * h / rows)), (w, int(i * h / rows))], fill="red")
    return img


# схожість
def calculate_distance(v1, v2, metric="euclidean"):
    if metric == "manhattan":
        return sum(abs(a - b) for a, b in zip(v1, v2))
    if metric == "chebyshev":
        return max(abs(a - b) for a, b in zip(v1, v2))
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))
