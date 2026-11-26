#!/usr/bin/env python3
"""THE WORLD - a one-page dense broadsheet for Wednesday 25 November 2026.

Pure Python standard library only: no third-party imports, no network,
deterministic output. Renders entry.png (1024 x 1024) into
$MAKEFUN_OUTPUT_DIR (or the current directory).

Layout: navy masthead, lead story, dotted world map + by-the-numbers rail,
12 story cards, 9 briefs, sport footer. 23 stories in total.
"""
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 243, 234)
NAVY = (20, 33, 61)
RED = (178, 34, 34)
INK = (24, 24, 24)
GREY = (112, 109, 100)
LIGHT = (214, 209, 196)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font
# 5x7 pixel font, authored here. Each glyph is 7 rows; bit 4 is the left
# column, bit 0 the right column. All text is rendered uppercase.
FONT = {
    'A': (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    'B': (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    'C': (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    'D': (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    'E': (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    'F': (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    'G': (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    'H': (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    'I': (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    'J': (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    'K': (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    'L': (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    'M': (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    'N': (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    'O': (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    'P': (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    'Q': (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    'R': (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    'S': (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    'T': (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    'U': (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    'V': (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    'W': (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    'X': (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    'Y': (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    'Z': (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    '0': (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    '1': (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    '2': (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    '3': (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    '4': (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    '5': (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    '6': (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    '7': (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    '8': (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    '9': (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0b01100, 0b01100),
    ',': (0, 0, 0, 0, 0b01100, 0b00100, 0b01000),
    ':': (0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ';': (0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    '!': (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    '?': (0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0, 0b00100),
    '-': (0, 0, 0, 0b01110, 0, 0, 0),
    '(': (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ')': (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    '/': (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    '%': (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    '&': (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    '+': (0, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0),
    '=': (0, 0, 0b11111, 0, 0b11111, 0, 0),
    '"': (0b01010, 0b01010, 0b01010, 0, 0, 0, 0),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    '$': (0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
    '#': (0b01010, 0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b01010),
    '@': (0b01110, 0b10001, 0b10111, 0b10101, 0b10110, 0b10000, 0b01110),
    '*': (0, 0b10101, 0b01110, 0b11111, 0b01110, 0b10101, 0),
    '_': (0, 0, 0, 0, 0, 0, 0b11111),
}

# ---------------------------------------------------------------- canvas
buf = bytearray(bytes(PAPER) * (W * H))


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = c


def fill_rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    row = bytes(c) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        buf[i:i + len(row)] = row


def hline(x, y, w, c, t=1):
    fill_rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    fill_rect(x, y, t, h, c)


def frame(x, y, w, h, c, t=1):
    hline(x, y, w, c, t)
    hline(x, y + h - t, w, c, t)
    vline(x, y, h, c, t)
    vline(x + w - t, y, h, c, t)


def disc(cx, cy, r, c):
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r + r:
                px(cx + dx, cy + dy, c)


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    fill_rect(cx + col * scale, y + row * scale,
                              scale, scale, c)
        cx += 6 * scale
    return cx - x


def draw_centered(y, s, scale, c, x0=0, x1=W):
    w = text_w(s.upper(), scale)
    draw_text(x0 + (x1 - x0 - w) // 2, y, s, scale, c)


def wrap(s, max_w, scale):
    """Greedy word wrap; returns a list of lines."""
    words = s.upper().split(' ')
    lines = []
    cur = ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- map
# Dotted world map: land is approximated by ellipses in lon/lat degrees
# (centre lon, centre lat, rx, ry). Dots are plotted on a 4-degree grid.
LAND = [
    # North America
    (-152, 65, 14, 6), (-105, 58, 28, 9), (-98, 40, 20, 8),
    (-95, 20, 8, 6), (-42, 73, 10, 5),
    # South America
    (-62, 2, 12, 8), (-64, -18, 8, 12), (-68, -38, 4, 8),
    # Africa
    (10, 18, 20, 10), (22, -8, 12, 14), (24, -28, 7, 5),
    (47, -19, 2, 6),
    # Europe
    (16, 63, 8, 7), (12, 50, 14, 6), (-2, 54, 3, 4), (-4, 40, 5, 3),
    # Asia
    (95, 64, 40, 8), (75, 48, 18, 8), (108, 32, 14, 9),
    (78, 21, 7, 8), (45, 24, 8, 7), (101, 14, 7, 7),
    (115, -3, 14, 3), (138, 37, 3, 6), (127, 39, 2, 3),
    # Oceania
    (134, -25, 14, 8), (147, -42, 2, 2), (172, -41, 2, 4),
]

# Red pins: (lon, lat) of places in today's stories.
PINS = [(56.5, 26.5), (30.5, 50.4), (46.7, 24.6),
        (50.1, 53.2), (149.1, -35.3), (30.7, 46.5)]

MAP_X, MAP_Y, MAP_W, MAP_H = 12, 244, 688, 256
LAT_TOP, LAT_BOT = 82.0, -58.0


def in_land(lon, lat):
    for (clon, clat, rx, ry) in LAND:
        dx = (lon - clon) / rx
        dy = (lat - clat) / ry
        if dx * dx + dy * dy <= 1.0:
            return True
    return False


def map_xy(lon, lat):
    x = MAP_X + (lon + 180.0) / 360.0 * MAP_W
    y = MAP_Y + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * MAP_H
    return int(x), int(y)


def draw_map():
    lon = -180
    while lon < 180:
        lat = LAT_TOP
        while lat > LAT_BOT:
            if in_land(lon, lat):
                x, y = map_xy(lon, lat)
                disc(x, y, 2, NAVY)
            lat -= 4
        lon += 4
    for (lon, lat) in PINS:
        x, y = map_xy(lon, lat)
        disc(x, y, 3, RED)
        disc(x, y, 1, WHITE)


# ---------------------------------------------------------------- content
# All stories are real news reported on Wednesday 25 November 2026.
LEAD_KICKER = "LEAD - STRAIT OF HORMUZ"
LEAD_HEAD = ["TANKERS ABLAZE IN HORMUZ",
             "AS IRAN SAYS MINES STRUCK SHIPS"]
LEAD_DEK = ["IRAN'S REVOLUTIONARY GUARD SAYS TWO TANKERS HIT NAVAL MINES AND",
            "CAUGHT FIRE IN THE STRAIT. HOUTHIS STRIKE A SAUDI REFINERY."]

NUMBERS = [
    ("-6.16%", "KOSPI PLUNGE, SEOUL"),
    ("50,018", "DOW, FIRST CLOSE ABOVE 50,000"),
    ("$54.9BN", "DELL RECORD QUARTER REVENUE"),
    ("4.3%", "US Q3 GDP GROWTH, REVISED UP"),
    ("490,334", "RUSSIAN WAR DEAD SINCE 2022 (BBC)"),
]

# (kicker, headline, summary) - 12 cards, 4 columns x 3 rows.
CARDS = [
    ("MIDDLE EAST", "HOUTHIS HIT SAUDI REFINERY",
     "Ras Tanura attacked; Riyadh tower strike hurt 11."),
    ("EUROPE", "UKRAINE HITS TWO REFINERIES",
     "Drones set Rosneft plants ablaze in Samara region."),
    ("EUROPE", "RUSSIA STRIKES ODESA, KYIV",
     "Two killed in Odesa; Kyiv apartment block ablaze."),
    ("ASIA", "HUAWEI CONVICTED IN US TRIAL",
     "Jury finds firm guilty on 10 of 12 counts."),
    ("MARKETS", "ASIAN STOCKS TUMBLE",
     "KOSPI -6.16%, Nikkei -2.78% as AI rout spreads."),
    ("SPACE", "PAKISTAN'S FIRST ASTRONAUT",
     "Shenzhou-24 docks at Tiangong space station."),
    ("PACIFIC", "SOLOMONS SIGN CANBERRA PACT",
     "Treaty bars foreign military bases on islands."),
    ("AFRICA", "19 KILLED IN SUDAN STRIKES",
     "RSF drones hit two cities, rights group says."),
    ("MIDDLE EAST", "HAMAS COLONEL KILLED IN GAZA",
     "Israel strike kills Abuelouf, wife and children."),
    ("CLIMATE", "POPE LAMENTS COP31 FAILURE",
     "'Extreme events linked to climate crisis grow.'"),
    ("AMERICAS", "US PLANS NEW TARIFFS",
     "Levies on 14 partners, 20-40%, from January."),
    ("ASIA", "SIX DEAD IN BOGOR MINE FLOOD",
     "Around 20 miners still trapped in West Java."),
]

# 9 one-line briefs, 3 columns x 3 rows.
BRIEFS = [
    "COLOMBIA: Hostages freed in Cartagena supermarket raid.",
    "DELL: Record quarter - revenue $54.9bn, AI servers $22bn.",
    "NIGERIA: Militants kill at least 30 in Niger region.",
    "SPACEX: FCC clears up to 1m orbital data satellites.",
    "US: CIA and spy agency hit by cyber breach.",
    "BANGLADESH: Garment wage up 36% after protests.",
    "MUSIC: Duran Duran's Andy Taylor dies at 65.",
    "CRYPTO: Bitcoin slips below $58,000.",
    "TRAVEL: Eurostar hit by union strikes.",
]

SPORT_LINES = [
    "SPORT - LAKERS TOP JAZZ AS DONCIC SCORES 28",
    "SINNER OUT FOR EXTENDED SPELL AFTER KNEE SURGERY",
]

# ---------------------------------------------------------------- layout
def draw_masthead():
    fill_rect(8, 8, W - 16, 78, NAVY)
    draw_centered(20, "THE WORLD", 9, WHITE)
    draw_centered(94, "WEDNESDAY, NOVEMBER 25, 2026", 2, NAVY)
    hline(12, 116, W - 24, RED, 3)


def draw_lead():
    draw_text(12, 128, LEAD_KICKER, 1, RED)
    draw_centered(142, LEAD_HEAD[0], 4, INK)
    draw_centered(174, LEAD_HEAD[1], 4, INK)
    draw_centered(206, LEAD_DEK[0], 2, INK)
    draw_centered(222, LEAD_DEK[1], 2, INK)
    hline(12, 240, W - 24, LIGHT, 1)


def draw_map_section():
    draw_text(12, 248, "THE WORLD IN DOTS", 1, NAVY)
    draw_text(712, 248, "BY THE NUMBERS", 1, NAVY)
    draw_map()
    draw_centered(508, "SIX CONTINENTS, ONE DAY - RED PINS MARK TODAY'S STORIES",
                  1, GREY, 12, 700)


def draw_numbers():
    y = 266
    for (num, label) in NUMBERS:
        draw_text(712, y, num, 3, RED)
        lab = wrap(label, 300, 1)
        ly = y + 26
        for ln in lab[:2]:
            draw_text(712, ly, ln, 1, INK)
            ly += 9
        y += 52
        if y < 500:
            hline(712, y - 6, 300, LIGHT, 1)


def draw_cards():
    cw, ch, gap = 244, 92, 8
    for i, (kick, head, summ) in enumerate(CARDS):
        col = i % 4
        row = i // 4
        x = 12 + col * (cw + gap)
        y = 566 + row * (ch + 10)
        frame(x, y, cw, ch, LIGHT, 1)
        fill_rect(x, y, cw, 3, NAVY)
        draw_text(x + 8, y + 8, kick, 1, RED)
        hl = wrap(head, cw - 16, 2)
        hy = y + 20
        for ln in hl[:2]:
            draw_text(x + 8, hy, ln, 2, INK)
            hy += 16
        sl = wrap(summ, cw - 16, 1)
        sy = y + 56
        for ln in sl[:2]:
            draw_text(x + 8, sy, ln, 1, GREY)
            sy += 9


def draw_briefs():
    draw_text(12, 872, "IN BRIEF", 1, NAVY)
    hline(12, 884, W - 24, NAVY, 2)
    bw = 325
    for i, b in enumerate(BRIEFS):
        col = i % 3
        row = i // 3
        x = 12 + col * (bw + 8)
        y = 892 + row * 24
        lines = wrap(b, bw, 1)
        ly = y
        for ln in lines[:2]:
            draw_text(x, ly, ln, 1, INK)
            ly += 9


def draw_sport():
    fill_rect(8, 962, W - 16, 54, NAVY)
    draw_centered(972, SPORT_LINES[0], 2, WHITE)
    draw_centered(992, SPORT_LINES[1], 2, WHITE)


def draw_page():
    draw_masthead()
    draw_lead()
    draw_map_section()
    draw_numbers()
    draw_cards()
    draw_briefs()
    draw_sport()
    frame(4, 4, W - 8, H - 8, NAVY, 2)


# ---------------------------------------------------------------- png
def png_bytes():
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        return out + struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    draw_page()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "."
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes())
    print("wrote", path)


if __name__ == "__main__":
    main()
