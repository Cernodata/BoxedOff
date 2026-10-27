"""Build the Cube Drop print pack from the brand guide.

Wordmark outlines come from Montserrat (SIL Open Font License).
The mark is an isometric cube with a gap between the three faces.
"""

from __future__ import annotations

import math
import shutil
import zipfile
from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.pdfgen.canvas import FILL_NON_ZERO

ROOT = Path(__file__).resolve().parent
FONT_PATH = ROOT / "_src" / "Montserrat.ttf"
OUT = ROOT / "CUBEDROP-brand-pack"
ZIP_PATH = ROOT.parent / "CUBEDROP-brand-pack.zip"
LOGO_DIR = ROOT.parent / "logo"
SITE = ROOT.parent.parent / "site"

ORANGE = (0xFF, 0x7A, 0x00)
CHARCOAL = (0x1A, 0x1A, 0x1A)
GREY = (0xE9, 0xE9, 0xE9)
OFFWHITE = (0xF8, 0xF8, 0xF8)
WHITE = (0xFF, 0xFF, 0xFF)

CUBE_H = 22.0
WORD_MM = 16.5
WORD_TRACK = 0.01
TAG_SCALE = 0.34
TAG_TRACK = 0.18
TM_SCALE = 0.28
GAP_MM = 4.2
TAG_GAP_MM = 1.7
STACK_GAP_MM = 3.2
FACE_SCALE = 0.86
PT = 72.0 / 25.4


class OpsPen(BasePen):
    def __init__(self, glyph_set):
        super().__init__(glyph_set)
        self.ops: list[tuple] = []

    def _moveTo(self, pt):
        self.ops.append(("M", pt[0], pt[1]))

    def _lineTo(self, pt):
        self.ops.append(("L", pt[0], pt[1]))

    def _curveToOne(self, p1, p2, p3):
        self.ops.append(("C", p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]))

    def _qCurveToOne(self, p1, p2):
        cx, cy = self._getCurrentPoint()
        self.ops.append(
            (
                "C",
                cx + 2 / 3 * (p1[0] - cx),
                cy + 2 / 3 * (p1[1] - cy),
                p2[0] + 2 / 3 * (p1[0] - p2[0]),
                p2[1] + 2 / 3 * (p1[1] - p2[1]),
                p2[0],
                p2[1],
            )
        )

    def _closePath(self):
        self.ops.append(("Z",))

    def _endPath(self):
        self.ops.append(("Z",))


def load_font(weight: float) -> TTFont:
    font = TTFont(FONT_PATH)
    instantiateVariableFont(font, {"wght": weight}, inplace=True, overlap=True)
    return font


def text_ops(font: TTFont, text: str, size: float, tracking_em: float, x: float, baseline: float):
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    tracking = tracking_em * size
    ops: list[tuple] = []
    cursor = x
    for index, char in enumerate(text):
        glyph = glyph_set[cmap[ord(char)]]
        pen = OpsPen(glyph_set)
        glyph.draw(pen)
        for op in pen.ops:
            if op[0] == "M":
                ops.append(("M", cursor + op[1] * scale, baseline + op[2] * scale))
            elif op[0] == "L":
                ops.append(("L", cursor + op[1] * scale, baseline + op[2] * scale))
            elif op[0] == "C":
                ops.append(
                    (
                        "C",
                        cursor + op[1] * scale,
                        baseline + op[2] * scale,
                        cursor + op[3] * scale,
                        baseline + op[4] * scale,
                        cursor + op[5] * scale,
                        baseline + op[6] * scale,
                    )
                )
            else:
                ops.append(("Z",))
        cursor += glyph.width * scale
        if index < len(text) - 1:
            cursor += tracking
    return ops


def bounds_of(ops: list[tuple]) -> tuple[float, float, float, float]:
    pts: list[tuple[float, float]] = []
    cx = cy = 0.0
    for op in ops:
        if op[0] in ("M", "L"):
            cx, cy = op[1], op[2]
            pts.append((cx, cy))
        elif op[0] == "C":
            p0 = (cx, cy)
            p1 = (op[1], op[2])
            p2 = (op[3], op[4])
            p3 = (op[5], op[6])
            pts.extend((p0, p3))
            pts.extend(cubic_extrema(p0, p1, p2, p3))
            cx, cy = p3
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def cubic_at(p0, p1, p2, p3, t):
    u = 1 - t
    return (
        u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
    )


def cubic_extrema(p0, p1, p2, p3):
    found = []
    for axis in (0, 1):
        a = -p0[axis] + 3 * p1[axis] - 3 * p2[axis] + p3[axis]
        b = 2 * p0[axis] - 4 * p1[axis] + 2 * p2[axis]
        c = p1[axis] - p0[axis]
        for t in quadratic_roots(a, b, c):
            if 0 < t < 1:
                found.append(cubic_at(p0, p1, p2, p3, t))
    return found


def quadratic_roots(a, b, c):
    if abs(a) < 1e-9:
        if abs(b) < 1e-9:
            return []
        return [-c / b]
    disc = b * b - 4 * a * c
    if disc < 0:
        return []
    root = disc**0.5
    return [(-b + root) / (2 * a), (-b - root) / (2 * a)]


def shift(ops, dx, dy):
    moved = []
    for op in ops:
        if op[0] in ("M", "L"):
            moved.append((op[0], op[1] + dx, op[2] + dy))
        elif op[0] == "C":
            moved.append((op[0], op[1] + dx, op[2] + dy, op[3] + dx, op[4] + dy, op[5] + dx, op[6] + dy))
        else:
            moved.append(op)
    return moved


def poly_ops(poly):
    ops = [("M", poly[0][0], poly[0][1])]
    ops.extend(("L", x, y) for x, y in poly[1:])
    ops.append(("Z",))
    return ops


def scale_poly(poly, k):
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    return [((x - cx) * k + cx, (y - cy) * k + cy) for x, y in poly]


def cube_faces(height: float):
    s = 100.0
    dx = s * math.sqrt(3) / 2
    dy = s / 2
    front = (0.0, s)
    bottom = (0.0, 0.0)
    left_bottom = (-dx, dy)
    right_bottom = (dx, dy)
    left = (-dx, dy + s)
    right = (dx, dy + s)
    top = (0.0, s + 2 * dy)
    faces = [
        [top, right, front, left],
        [left, front, bottom, left_bottom],
        [front, right, right_bottom, bottom],
    ]
    faces = [scale_poly(face, FACE_SCALE) for face in faces]
    pts = [point for face in faces for point in face]
    minx = min(p[0] for p in pts)
    miny = min(p[1] for p in pts)
    maxy = max(p[1] for p in pts)
    scale = height / (maxy - miny)
    return [[((x - minx) * scale, (y - miny) * scale) for x, y in face] for face in faces]


def cube_layers(colour, height=CUBE_H, origin=(0.0, 0.0)):
    layers = []
    for face in cube_faces(height):
        moved = [(x + origin[0], y + origin[1]) for x, y in face]
        layers.append((colour, poly_ops(moved)))
    return layers


def cube_width(height=CUBE_H):
    faces = cube_faces(height)
    xs = [x for face in faces for x, _ in face]
    return max(xs) - min(xs)


def center_x(ops, cx):
    minx, _, maxx, _ = bounds_of(ops)
    return shift(ops, cx - (minx + maxx) / 2, 0)


class Art:
    def __init__(self, name, label, layers, fixed=None):
        self.name = name
        self.label = label
        self.layers = layers
        if fixed:
            self.bounds = fixed
        else:
            boxes = [bounds_of(ops) for _, ops in layers]
            self.bounds = (
                min(b[0] for b in boxes),
                min(b[1] for b in boxes),
                max(b[2] for b in boxes),
                max(b[3] for b in boxes),
            )

    @property
    def size_mm(self):
        x0, y0, x1, y1 = self.bounds
        return x1 - x0, y1 - y0


def word_block(font_bold, font_regular, word_colour):
    word = text_ops(font_bold, "CUBE DROP", WORD_MM, WORD_TRACK, 0, 0)
    word_box = bounds_of(word)
    tm = text_ops(font_bold, "TM", WORD_MM * TM_SCALE, 0.02, 0, 0)
    tm_box = bounds_of(tm)
    tm = shift(tm, word_box[2] + 0.55, word_box[3] - tm_box[3] + 0.15)
    tag = text_ops(font_regular, "STORAGE", WORD_MM * TAG_SCALE, TAG_TRACK, 0, 0)
    tag_box = bounds_of(tag)
    tag_shift = ((word_box[0] + word_box[2]) / 2) - ((tag_box[0] + tag_box[2]) / 2)
    tag = shift(tag, tag_shift, word_box[1] - TAG_GAP_MM - tag_box[3])
    return [(word_colour, word), (word_colour, tm), (word_colour, tag)]


def build_arts(font_bold, font_regular):
    block = word_block(font_bold, font_regular, CHARCOAL)
    block_box = bounds_of([op for _, ops in block for op in ops])
    word_only = bounds_of(block[0][1])
    cube = cube_layers(ORANGE)
    cube_box = bounds_of([op for _, ops in cube for op in ops])
    # Sit the cube on the cap-height centre of CUBE DROP.
    cube_dy = (word_only[1] + word_only[3]) / 2 - (cube_box[1] + cube_box[3]) / 2
    cube = [(c, shift(ops, 0, cube_dy)) for c, ops in cube]
    cube_box = bounds_of([op for _, ops in cube for op in ops])
    text_dx = cube_box[2] + GAP_MM - block_box[0]
    block = [(c, shift(ops, text_dx, 0)) for c, ops in block]

    def paint(mark, word, slash):
        layers = cube_layers(mark)
        layers = [(c, shift(ops, 0, cube_dy)) for c, ops in layers]
        painted = word_block(font_bold, font_regular, word)
        painted = [(c, shift(ops, text_dx, 0)) for c, ops in painted]
        return layers + painted

    def stack(mark, word, slash):
        layers = cube_layers(mark)
        cbox = bounds_of([op for _, ops in layers for op in ops])
        painted = word_block(font_bold, font_regular, word)
        pbox = bounds_of([op for _, ops in painted for op in ops])
        cx = (cbox[0] + cbox[2]) / 2
        px = (pbox[0] + pbox[2]) / 2
        dy = cbox[1] - STACK_GAP_MM - pbox[3]
        return layers + [(c, shift(ops, cx - px, dy)) for c, ops in painted]

    side = CUBE_H + 8
    badge = (0.0, 0.0, side, side)
    inset = (side - cube_width()) / 2
    # cube_faces min x is 0, so inset is the left pad. Vertical pad uses the height.
    pad_y = (side - CUBE_H) / 2

    arts = [
        Art("logo-horizontal-colour", "Horizontal, full colour.", paint(ORANGE, CHARCOAL, ORANGE)),
        Art("logo-horizontal-reversed", "Horizontal, reversed for dark grounds.", paint(ORANGE, WHITE, ORANGE)),
        Art("logo-horizontal-black", "Horizontal, charcoal only.", paint(CHARCOAL, CHARCOAL, CHARCOAL)),
        Art("logo-horizontal-white", "Horizontal, white only.", paint(WHITE, WHITE, WHITE)),
        Art("logo-stacked-colour", "Stacked, full colour.", stack(ORANGE, CHARCOAL, ORANGE)),
        Art("logo-stacked-reversed", "Stacked, reversed.", stack(ORANGE, WHITE, ORANGE)),
        Art("logo-stacked-black", "Stacked, charcoal.", stack(CHARCOAL, CHARCOAL, CHARCOAL)),
        Art("logo-stacked-white", "Stacked, white.", stack(WHITE, WHITE, WHITE)),
        Art("icon-orange", "Cube only, orange.", cube_layers(ORANGE)),
        Art("icon-black", "Cube only, charcoal.", cube_layers(CHARCOAL)),
        Art("icon-white", "Cube only, white.", cube_layers(WHITE)),
        Art(
            "icon-orange-on-charcoal",
            "Cube on a charcoal square.",
            [(CHARCOAL, poly_ops([(0, 0), (side, 0), (side, side), (0, side)]))]
            + cube_layers(ORANGE, origin=(inset, pad_y)),
            badge,
        ),
    ]
    return arts


def ribbon(points, radius):
    if len(points) < 2:
        return []
    left = []
    right = []
    dirs = []
    for i in range(len(points)):
        if i == 0:
            dx, dy = points[1][0] - points[0][0], points[1][1] - points[0][1]
        elif i == len(points) - 1:
            dx, dy = points[-1][0] - points[-2][0], points[-1][1] - points[-2][1]
        else:
            dx = points[i + 1][0] - points[i - 1][0]
            dy = points[i + 1][1] - points[i - 1][1]
        length = math.hypot(dx, dy) or 1
        dirs.append((dx / length, dy / length))
        left.append((points[i][0] - dy / length * radius, points[i][1] + dx / length * radius))
        right.append((points[i][0] + dy / length * radius, points[i][1] - dx / length * radius))

    def cap(center, direction, start_side):
        angle = math.atan2(direction[1], direction[0])
        pts = []
        for step in range(7):
            a = angle + math.pi / 2 + math.pi * step / 6
            if start_side == "left":
                a = angle - math.pi / 2 + math.pi * step / 6
            pts.append((center[0] + math.cos(a) * radius, center[1] + math.sin(a) * radius))
        return pts

    # left side, cap at end, right side reversed, cap at start
    end_cap = cap(points[-1], dirs[-1], "left")
    start_cap = cap(points[0], (-dirs[0][0], -dirs[0][1]), "left")
    poly = left + end_cap + list(reversed(right)) + start_cap
    return poly_ops(poly)


def line_icons():
    def house(colour, size):
        r = size * 0.045
        roof = [(0.16 * size, 0.46 * size), (0.50 * size, 0.84 * size), (0.84 * size, 0.46 * size)]
        wall = [
            (0.28 * size, 0.50 * size),
            (0.28 * size, 0.14 * size),
            (0.72 * size, 0.14 * size),
            (0.72 * size, 0.50 * size),
        ]
        door = [
            (0.44 * size, 0.14 * size),
            (0.44 * size, 0.40 * size),
            (0.56 * size, 0.40 * size),
            (0.56 * size, 0.14 * size),
        ]
        return [(colour, ribbon(path, r)) for path in (roof, wall, door)]

    def heart(colour, size):
        r = size * 0.045
        pts = []
        for i in range(80):
            t = math.pi * 2 * i / 80
            x = 16 * math.sin(t) ** 3
            y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            pts.append((x, y))
        minx, maxx = min(p[0] for p in pts), max(p[0] for p in pts)
        miny, maxy = min(p[1] for p in pts), max(p[1] for p in pts)
        scale = (size * 0.72) / max(maxx - minx, maxy - miny)
        cx = (minx + maxx) / 2
        cy = (miny + maxy) / 2
        placed = [((x - cx) * scale + size / 2, (y - cy) * scale + size / 2) for x, y in pts]
        return [(colour, ribbon(placed, r))]

    icons = []
    for name, builder in (("care", house), ("living", heart)):
        for colour_name, colour in (("orange", ORANGE), ("black", CHARCOAL), ("white", WHITE)):
            icons.append(Art(f"icon-{name}-{colour_name}", f"{name.title()} icon, {colour_name}.", builder(colour, 22)))
    return icons


def svg_path(ops, origin, height):
    x0, y0 = origin
    parts = []
    for op in ops:
        if op[0] == "M":
            parts.append(f"M {op[1] - x0:.3f} {height - (op[2] - y0):.3f}")
        elif op[0] == "L":
            parts.append(f"L {op[1] - x0:.3f} {height - (op[2] - y0):.3f}")
        elif op[0] == "C":
            parts.append(
                "C "
                + " ".join(
                    f"{v:.3f}"
                    for v in (
                        op[1] - x0,
                        height - (op[2] - y0),
                        op[3] - x0,
                        height - (op[4] - y0),
                        op[5] - x0,
                        height - (op[6] - y0),
                    )
                )
            )
        else:
            parts.append("Z")
    return " ".join(parts)


def write_svg(art: Art, path: Path):
    x0, y0, x1, y1 = art.bounds
    w, h = x1 - x0, y1 - y0
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}mm" height="{h:.3f}mm" viewBox="0 0 {w:.3f} {h:.3f}">',
        f"<title>{art.label}</title>",
    ]
    for rgb, ops in art.layers:
        colour = f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
        lines.append(f'<path fill="{colour}" fill-rule="nonzero" d="{svg_path(ops, (x0, y0), h)}"/>')
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_pdf(art: Art, path: Path):
    x0, y0, x1, y1 = art.bounds
    w, h = (x1 - x0) * PT, (y1 - y0) * PT
    c = pdfcanvas.Canvas(str(path), pagesize=(w, h))
    c.setTitle(f"Cube Drop {art.name}")
    c.setAuthor("Cube Drop")
    draw_layers(c, art.layers, x0, y0, 0, 0, PT)
    c.save()


def draw_layers(c, layers, x0, y0, ox, oy, scale):
    for rgb, ops in layers:
        path_obj = c.beginPath()
        for op in ops:
            if op[0] == "M":
                path_obj.moveTo(ox + (op[1] - x0) * scale, oy + (op[2] - y0) * scale)
            elif op[0] == "L":
                path_obj.lineTo(ox + (op[1] - x0) * scale, oy + (op[2] - y0) * scale)
            elif op[0] == "C":
                path_obj.curveTo(
                    ox + (op[1] - x0) * scale,
                    oy + (op[2] - y0) * scale,
                    ox + (op[3] - x0) * scale,
                    oy + (op[4] - y0) * scale,
                    ox + (op[5] - x0) * scale,
                    oy + (op[6] - y0) * scale,
                )
            else:
                path_obj.close()
        c.setFillColor(Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255))
        c.drawPath(path_obj, stroke=0, fill=1, fillMode=FILL_NON_ZERO)


def write_eps(art: Art, path: Path):
    x0, y0, x1, y1 = art.bounds
    w, h = (x1 - x0) * PT, (y1 - y0) * PT
    chunks = [
        "%!PS-Adobe-3.0 EPSF-3.0",
        f"%%BoundingBox: 0 0 {int(w + 0.999)} {int(h + 0.999)}",
        f"%%HiResBoundingBox: 0 0 {w:.3f} {h:.3f}",
        f"%%Title: Cube Drop {art.name}",
        "%%Creator: Cube Drop",
        "%%LanguageLevel: 2",
        "%%EndComments",
        "gsave",
    ]
    for rgb, ops in art.layers:
        chunks.append(f"{rgb[0] / 255:.6f} {rgb[1] / 255:.6f} {rgb[2] / 255:.6f} setrgbcolor")
        chunks.append("newpath")
        for op in ops:
            if op[0] == "M":
                chunks.append(f"{(op[1] - x0) * PT:.3f} {(op[2] - y0) * PT:.3f} moveto")
            elif op[0] == "L":
                chunks.append(f"{(op[1] - x0) * PT:.3f} {(op[2] - y0) * PT:.3f} lineto")
            elif op[0] == "C":
                chunks.append(
                    f"{(op[1] - x0) * PT:.3f} {(op[2] - y0) * PT:.3f} "
                    f"{(op[3] - x0) * PT:.3f} {(op[4] - y0) * PT:.3f} "
                    f"{(op[5] - x0) * PT:.3f} {(op[6] - y0) * PT:.3f} curveto"
                )
            else:
                chunks.append("closepath")
        chunks.append("fill")
    chunks.extend(["grestore", "showpage", "%%EOF", ""])
    path.write_text("\n".join(chunks), encoding="utf-8")


def flatten(ops, tol):
    contours = []
    current = []
    cx = cy = sx = sy = 0.0

    def line_to(x, y):
        nonlocal cx, cy
        current.append((x, y))
        cx, cy = x, y

    for op in ops:
        if op[0] == "M":
            if len(current) > 2:
                contours.append(current)
            cx, cy = op[1], op[2]
            sx, sy = cx, cy
            current = [(cx, cy)]
        elif op[0] == "L":
            line_to(op[1], op[2])
        elif op[0] == "C":
            for point in flatten_cubic((cx, cy), (op[1], op[2]), (op[3], op[4]), (op[5], op[6]), tol):
                line_to(*point)
        elif op[0] == "Z":
            if current and current[0] != current[-1]:
                current.append(current[0])
            if len(current) > 2:
                contours.append(current)
            current = []
            cx, cy = sx, sy
    if len(current) > 2:
        contours.append(current)
    return contours


def flatten_cubic(p0, p1, p2, p3, tol):
    points = []

    def recur(a, b, c, d, depth):
        if depth > 12 or (dist_to_line(b, a, d) <= tol and dist_to_line(c, a, d) <= tol):
            points.append(d)
            return
        ab, bc, cd = mid(a, b), mid(b, c), mid(c, d)
        abc, bcd = mid(ab, bc), mid(bc, cd)
        abcd = mid(abc, bcd)
        recur(a, ab, abc, abcd, depth + 1)
        recur(abcd, bcd, cd, d, depth + 1)

    recur(p0, p1, p2, p3, 0)
    return points


def mid(a, b):
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def dist_to_line(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = (dx * dx + dy * dy) ** 0.5
    if length < 1e-9:
        return ((p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2) ** 0.5
    return abs(dy * p[0] - dx * p[1] + b[0] * a[1] - b[1] * a[0]) / length


def signed_area(pts):
    area = 0.0
    for i in range(len(pts) - 1):
        area += pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1]
    return area / 2


def raster(art: Art, longest: int = 4096) -> Image.Image:
    x0, y0, x1, y1 = art.bounds
    bw, bh = max(x1 - x0, 0.01), max(y1 - y0, 0.01)
    scale = longest / max(bw, bh)
    width = max(1, round(bw * scale))
    height = max(1, round(bh * scale))
    super_scale = 4
    tol = 0.35 / (scale * super_scale)
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sw, sh = width * super_scale, height * super_scale

    def to_px(x, y):
        return x * scale * super_scale, (bh - y) * scale * super_scale

    for rgb, ops in art.layers:
        contours = flatten(shift(ops, -x0, -y0), tol)
        if not contours:
            continue
        areas = [signed_area(c) for c in contours]
        outer_sign = 1 if areas[max(range(len(areas)), key=lambda i: abs(areas[i]))] > 0 else -1
        mask_big = Image.new("L", (sw, sh), 0)
        draw = ImageDraw.Draw(mask_big)
        ordered = sorted(zip(areas, contours), key=lambda item: 0 if item[0] * outer_sign > 0 else 1)
        for area, contour in ordered:
            fill = 255 if area * outer_sign > 0 else 0
            pixels = [to_px(x, y) for x, y in contour]
            if len(pixels) >= 3:
                draw.polygon(pixels, fill=fill)
        mask = mask_big.resize((width, height), Image.Resampling.LANCZOS)
        layer = Image.new("RGBA", (width, height), (*rgb, 255))
        layer.putalpha(mask)
        image.alpha_composite(layer)
    return image


def write_png(art: Art, path: Path):
    image = raster(art)
    bw, bh = art.size_mm
    image.save(path, "PNG", dpi=(image.width / (bw / 25.4), image.height / (bh / 25.4)), optimize=True)
    return image


def hex_of(rgb):
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def cmyk_of(rgb):
    r, g, b = (channel / 255 for channel in rgb)
    k = 1 - max(r, g, b)
    if k >= 0.999:
        return (0, 0, 0, 100)
    return tuple(round(channel * 100) for channel in ((1 - r - k) / (1 - k), (1 - g - k) / (1 - k), (1 - b - k) / (1 - k), k))


def write_how_to(arts, path: Path):
    orange = cmyk_of(ORANGE)
    lines = [
        "CUBE DROP — logo pack for decals, vinyl and stationery",
        "",
        "Use the SVG or PDF. They are vectors and scale to any size.",
        "EPS is for older plotters. PNG is for software that cannot take vectors.",
        "At 100% the sizes below match across SVG, PDF, EPS and PNG.",
        "White and reversed files can look blank on a white screen. The artwork is still there.",
        "Previews are for looking at. Do not print from the previews folder.",
        "",
        "COLOURS",
        f"Orange     {hex_of(ORANGE)}   RGB {ORANGE[0]} {ORANGE[1]} {ORANGE[2]}   CMYK {orange[0]} {orange[1]} {orange[2]} {orange[3]}",
        f"Charcoal   {hex_of(CHARCOAL)}   RGB {CHARCOAL[0]} {CHARCOAL[1]} {CHARCOAL[2]}   print 100% K",
        f"Light grey {hex_of(GREY)}   RGB {GREY[0]} {GREY[1]} {GREY[2]}",
        f"Off white  {hex_of(OFFWHITE)}   RGB {OFFWHITE[0]} {OFFWHITE[1]} {OFFWHITE[2]}",
        "",
        "WHICH FILE",
        "Letterhead, cards, invoices on white     logo-horizontal-colour",
        "Van, container, window on a dark ground  logo-horizontal-reversed",
        "Black-only print or black vinyl          logo-horizontal-black",
        "White vinyl                              logo-horizontal-white",
        "Tall space                               logo-stacked-colour",
        "Small badge, embroidery, favicon         icon-orange",
        "",
        "RULES",
        "Clear space around the logo equals the height of the cube.",
        "Do not stretch, distort or alter the logo.",
        "Use only these colours. Do not add shadows, outlines or effects.",
        "Wordmark: Montserrat Bold. The line under the name is STORAGE.",
        "Cube Drop is a storage-to-you service. Do not add Care or Living.",
        "",
        "SIZE AT 100%",
    ]
    for art in arts:
        w, h = art.size_mm
        lines.append(f"{art.name:<32} {w:6.1f} mm  ×  {h:5.1f} mm")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def draw_art_in(c, art, x, y, w, h):
    x0, y0, x1, y1 = art.bounds
    aw, ah = (x1 - x0) * PT, (y1 - y0) * PT
    scale = min(w / aw, h / ah)
    ox = x + (w - aw * scale) / 2
    oy = y + (h - ah * scale) / 2
    draw_layers(c, art.layers, x0, y0, ox, oy, PT * scale)


def write_spec(arts: dict, path: Path):
    c = pdfcanvas.Canvas(str(path), pagesize=A4)
    c.setTitle("Cube Drop brand specification")
    c.setAuthor("Cube Drop")
    width, height = A4
    margin = 16 * PT
    by = lambda name: arts[name]
    draw_art_in(c, by("logo-horizontal-colour"), margin, height - 34 * PT, 120 * PT, 22 * PT)
    c.setFillColor(Color(0.25, 0.25, 0.25))
    c.setFont("Helvetica", 9)
    c.drawString(margin, height - 42 * PT, "Logo pack for vinyl, decals and stationery. Vectors scale. Sizes are at 100%.")
    swatch_y = height - 78 * PT
    swatches = [
        (ORANGE, "Orange", hex_of(ORANGE), f"CMYK {' '.join(str(n) for n in cmyk_of(ORANGE))}"),
        (CHARCOAL, "Charcoal", hex_of(CHARCOAL), "Print 100% K"),
        (GREY, "Light grey", hex_of(GREY), "Grounds and rules"),
        (OFFWHITE, "Off white", hex_of(OFFWHITE), "Page colour"),
    ]
    for index, (rgb, name, hex_code, note) in enumerate(swatches):
        x = margin + index * 46 * PT
        c.setFillColor(Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255))
        c.rect(x, swatch_y, 22 * PT, 14 * PT, stroke=0, fill=1)
        c.setStrokeColor(Color(0.85, 0.85, 0.85))
        c.setLineWidth(0.4)
        c.rect(x, swatch_y, 22 * PT, 14 * PT, stroke=1, fill=0)
        c.setFillColor(Color(*[v / 255 for v in CHARCOAL]))
        c.setFont("Helvetica", 8)
        c.drawString(x, swatch_y - 12, name)
        c.setFillColor(Color(0.35, 0.35, 0.35))
        c.drawString(x, swatch_y - 22, hex_code)
        c.drawString(x, swatch_y - 32, note)
    panel_top = swatch_y - 52 * PT
    panel_h = 28 * PT
    panel_w = (width - margin * 2 - 8 * PT) / 2
    c.setFillColor(Color(*[v / 255 for v in OFFWHITE]))
    c.rect(margin, panel_top - panel_h, panel_w, panel_h, stroke=0, fill=1)
    draw_art_in(c, by("logo-horizontal-colour"), margin + 6 * PT, panel_top - panel_h + 5 * PT, panel_w - 12 * PT, panel_h - 10 * PT)
    right = margin + panel_w + 8 * PT
    c.setFillColor(Color(*[v / 255 for v in CHARCOAL]))
    c.rect(right, panel_top - panel_h, panel_w, panel_h, stroke=0, fill=1)
    draw_art_in(c, by("logo-horizontal-reversed"), right + 6 * PT, panel_top - panel_h + 5 * PT, panel_w - 12 * PT, panel_h - 10 * PT)
    c.setFillColor(Color(0.35, 0.35, 0.35))
    c.setFont("Helvetica", 8)
    c.drawString(margin, panel_top - panel_h - 12, "Full colour — stationery")
    c.drawString(right, panel_top - panel_h - 12, "Reversed — dark van or container")
    row_y = panel_top - panel_h - 52 * PT
    tiles = [
        ("logo-stacked-colour", OFFWHITE, "Stacked"),
        ("icon-orange", OFFWHITE, "Cube"),
        ("icon-orange-on-charcoal", CHARCOAL, "On charcoal"),
    ]
    tile = 32 * PT
    for index, (name, ground, caption) in enumerate(tiles):
        x = margin + index * (tile + 8 * PT)
        c.setFillColor(Color(*[v / 255 for v in ground]))
        c.rect(x, row_y, tile, tile, stroke=0, fill=1)
        draw_art_in(c, by(name), x + 3 * PT, row_y + 3 * PT, tile - 6 * PT, tile - 6 * PT)
        c.setFillColor(Color(0.35, 0.35, 0.35))
        c.setFont("Helvetica", 8)
        c.drawString(x, row_y - 12, caption)
    y = row_y - 36 * PT
    c.setFillColor(Color(*[v / 255 for v in CHARCOAL]))
    c.setFont("Helvetica", 11)
    c.drawString(margin, y, "Rules")
    rules = [
        "Clear space on every side equals the height of the cube.",
        "Do not stretch, distort, recolour, or add shadows and outlines.",
        "Montserrat Bold for CUBE DROP. Montserrat Regular for STORAGE underneath.",
        "The only line under the name is STORAGE. This is a storage-to-you service.",
        "Orange is #FF7A00. Charcoal is #1A1A1A. Do not swap in another orange.",
    ]
    c.setFont("Helvetica", 9)
    for index, rule in enumerate(rules):
        c.drawString(margin, y - 16 - index * 13, rule)
    c.showPage()
    c.setFillColor(Color(*[v / 255 for v in CHARCOAL]))
    c.setFont("Helvetica", 12)
    c.drawString(margin, height - 28 * PT, "Which file to send")
    jobs = [
        ("Letterhead, cards, invoices", "logo-horizontal-colour"),
        ("Van, container or window on charcoal", "logo-horizontal-reversed"),
        ("Single-colour black print or vinyl", "logo-horizontal-black"),
        ("Cut white vinyl", "logo-horizontal-white"),
        ("Tall space, colour", "logo-stacked-colour"),
        ("Favicon, embroidery, small badge", "icon-orange"),
    ]
    c.setFont("Helvetica", 9)
    y = height - 50 * PT
    for job, filename in jobs:
        c.setFillColor(Color(*[v / 255 for v in CHARCOAL]))
        c.drawString(margin, y, job)
        c.setFillColor(Color(*[v / 255 for v in ORANGE]))
        c.drawString(margin + 230, y, filename)
        y -= 16
    y -= 8
    c.setFillColor(Color(*[v / 255 for v in CHARCOAL]))
    c.setFont("Helvetica", 11)
    c.drawString(margin, y, "Formats")
    notes = [
        "svg   First choice for Illustrator, CorelDRAW, Inkscape and most plotters.",
        "pdf   Same artwork, page cropped to the mark.",
        "eps   For older vinyl software.",
        "png   High resolution and transparent. Use when a vector will not open.",
        "100% size matches in every format.",
    ]
    c.setFont("Helvetica", 9)
    for index, note in enumerate(notes):
        c.drawString(margin, y - 16 - index * 13, note)
    c.save()


def write_previews(arts, folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    groups = {
        "preview-on-light.png": (
            OFFWHITE,
            [
                "logo-horizontal-colour",
                "logo-stacked-colour",
                "logo-horizontal-black",
                "icon-orange",
                "icon-black",
            ],
        ),
        "preview-on-dark.png": (
            CHARCOAL,
            [
                "logo-horizontal-reversed",
                "logo-stacked-reversed",
                "logo-horizontal-white",
                "icon-white",
                "icon-orange",
                "icon-orange-on-charcoal",
            ],
        ),
    }
    lookup = {art.name: art for art in arts}
    for filename, (ground, names) in groups.items():
        thumbs = []
        for name in names:
            image = raster(lookup[name], longest=1100)
            scale = 220 / image.height
            thumbs.append(image.resize((max(1, round(image.width * scale)), 220), Image.Resampling.LANCZOS))
        gap = 28
        width = max(image.width for image in thumbs) + gap * 2
        height = sum(image.height for image in thumbs) + gap * (len(thumbs) + 1)
        sheet = Image.new("RGBA", (width, height), (*ground, 255))
        y = gap
        for image in thumbs:
            sheet.alpha_composite(image, ((width - image.width) // 2, y))
            y += image.height + gap
        sheet.convert("RGB").save(folder / filename, "PNG", optimize=True)


def write_favicon(art: Art):
    """Charcoal tile, orange cube, used as the browser icon."""
    side = 32
    faces = cube_faces(22)
    width = max(x for face in faces for x, _ in face)
    pad_x = (side - width) / 2
    pad_y = (side - 22) / 2
    layers = [(CHARCOAL, poly_ops([(0, 0), (side, 0), (side, side), (0, side)]))]
    layers += cube_layers(ORANGE, origin=(pad_x, pad_y))
    badge = Art("favicon", "Favicon", layers, (0, 0, side, side))
    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">',
    ]
    for rgb, ops in layers:
        svg.append(f'<path fill="#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}" d="{svg_path(ops, (0, 0), side)}"/>')
    svg.append("</svg>")
    (SITE / "favicon.svg").write_text("\n".join(svg), encoding="utf-8")
    LOGO_DIR.mkdir(parents=True, exist_ok=True)
    bare = Art("cube", "Cube", cube_layers(ORANGE))
    write_svg(bare, LOGO_DIR / "cube.svg")
    image = raster(badge, longest=512)
    image.resize((32, 32), Image.Resampling.LANCZOS).save(SITE / "favicon-32.png")
    image.resize((180, 180), Image.Resampling.LANCZOS).save(SITE / "apple-touch-icon.png")
    image.resize((32, 32), Image.Resampling.LANCZOS).save(SITE / "favicon.ico", sizes=[(32, 32)])


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    old = ROOT / "BOXEDOFF-brand-pack"
    if old.exists():
        shutil.rmtree(old)
    old_zip = ROOT.parent / "BOXEDOFF-brand-pack.zip"
    if old_zip.exists():
        old_zip.unlink()
    for folder in ("svg", "pdf", "eps", "png", "previews"):
        (OUT / folder).mkdir(parents=True)
    font_bold = load_font(700)
    font_regular = load_font(400)
    arts = build_arts(font_bold, font_regular)
    for art in arts:
        write_svg(art, OUT / "svg" / f"{art.name}.svg")
        write_pdf(art, OUT / "pdf" / f"{art.name}.pdf")
        write_eps(art, OUT / "eps" / f"{art.name}.eps")
        write_png(art, OUT / "png" / f"{art.name}.png")
        w, h = art.size_mm
        print(f"{art.name:32} {w:6.1f} x {h:5.1f} mm")
    write_how_to(arts, OUT / "HOW-TO-USE.txt")
    write_spec({art.name: art for art in arts}, OUT / "CUBEDROP-specification.pdf")
    write_previews(arts, OUT / "previews")
    write_favicon(next(art for art in arts if art.name == "icon-orange"))
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in OUT.rglob("*"):
            if file.is_file():
                archive.write(file, Path("CUBEDROP-brand-pack") / file.relative_to(OUT))
    print(f"zip {ZIP_PATH} ({ZIP_PATH.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
