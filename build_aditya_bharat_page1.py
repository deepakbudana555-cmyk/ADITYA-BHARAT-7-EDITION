# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — PAGE 01 MASTER BROADSHEET BUILDER (34x53 cm | Print Area 32x51 cm)
=================================================================================================
Strictly implements the official 'Aditya Bharat' Stylesheet & Page 1 Architecture:
  - Total Page Size   : 34.0 cm x 53.0 cm (1.0 cm margin on all 4 sides)
  - Fixed Print Area  : 32.0 cm x 51.0 cm (8 Columns, 4.0 mm Gutter, 11.25 pt Baseline Grid)
  - Headline Font     : 'DB Rasrand Bold' (DB RASRANG BOLD), Leading = Point Size + 1.0 pt, 100% K Black
  - Body Text         : 'DB Hindi' Regular, 11.0 pt / 11.25 pt Leading, Baseline Locked, 100% K Black
  - Photo Caption     : 'DB Hindi 7' Bold, 10.0 pt / 10.2 pt Leading, 100% K Black
  - 3-Tone Byline     : City (100% K Black) | Pipe (Red) | Agency (60% Gray) + Gray Rule Below (1-Line strict)
  - Red Subject Blurb : 1-Word Subject in 'DB Hindi 6' 22.0 pt White on Red Box + 3.0 pt Gray Rule Below
  - Box Headline      : 16.0 pt (or 18-24 pt for package boxes) in 'DB Rasrand Bold'
  - All Photos        : Converted & saved in CMYK Color Mode (300 DPI)
"""

import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

VAULT_DIR = Path(__file__).resolve().parent
FONTS_DIR = VAULT_DIR / "Document Fonts"
PHOTOS_DIR = VAULT_DIR / "photos"
FONTS_DIR.mkdir(parents=True, exist_ok=True)
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

win_fonts = Path(r"C:\Windows\Fonts")
if win_fonts.exists():
    for f in win_fonts.glob("DB*.ttf"):
        dst = FONTS_DIR / f.name
        if not dst.exists():
            try:
                shutil.copy2(f, dst)
            except Exception:
                pass

RAW_PHOTO_MAP = {
    "ab_p1_flyer_cmyk.jpg": [
        Path(r"E:\RND\HINDI - TEST\photos\flyer_photo.jpg"),
        Path(r"E:\RND\Gujarat_Samachar\editions\19_Oct_2026\photos\gs_oct19_national_04.jpg"),
    ],
    "ab_p1_lead_cmyk.jpg": [
        Path(r"E:\RND\HINDI - TEST\photos\lead_photo.jpg"),
        Path(r"E:\RND\Gujarat_Samachar\editions\19_Oct_2026\photos\gs_oct19_business_tech_world_03.jpg"),
    ],
    "ab_p1_second_lead_cmyk.jpg": [
        Path(r"E:\RND\HINDI - TEST\photos\photo_04_239454_p1_solar_826978_print.jpg"),
        Path(r"E:\RND\HINDI - TEST\photos\state_page_photo.jpg"),
    ],
    "ab_p1_anchor_cmyk.jpg": [
        Path(r"E:\RND\HINDI - TEST\photos\anchor_photo.jpg"),
        Path(r"E:\RND\Gujarat_Samachar\editions\19_Oct_2026\photos\gs_oct19_business_tech_world_09.jpg"),
    ],
}

for dst_name, candidates in RAW_PHOTO_MAP.items():
    dst_p = PHOTOS_DIR / dst_name
    for src_p in candidates:
        if src_p.exists():
            try:
                with Image.open(src_p) as im:
                    cmyk_im = im.convert("CMYK")
                    cmyk_im.save(dst_p, "JPEG", quality=95, dpi=(300, 300))
            except Exception:
                shutil.copy2(src_p, dst_p)
            break

PORT = 47123
CM_TO_PT = 72.0 / 2.54
MM_TO_PT = CM_TO_PT / 10.0

def cm(val: float) -> float:
    return round(val * CM_TO_PT, 2)

def mm(val: float) -> float:
    return round(val * MM_TO_PT, 2)


class AdityaBharatPage1Grid:
    def __init__(self):
        self.page_w_cm = 34.0
        self.page_h_cm = 53.0
        self.margin_x_cm = 1.0
        self.margin_y_cm = 1.0
        self.print_w_cm = 32.0
        self.print_h_cm = 51.0
        self.cols = 8
        self.gutter_mm = 4.0

        self.width_pt = cm(self.page_w_cm)
        self.height_pt = cm(self.page_h_cm)
        self.margin_x_pt = cm(self.margin_x_cm)
        self.margin_y_pt = cm(self.margin_y_cm)
        self.print_w_pt = cm(self.print_w_cm)
        self.print_h_pt = cm(self.print_h_cm)
        self.gutter_pt = mm(self.gutter_mm)

        self.col_w_pt = (self.print_w_pt - (self.cols - 1) * self.gutter_pt) / self.cols
        self.print_x0 = self.margin_x_pt
        self.print_y0 = self.margin_y_pt
        self.print_x1 = round(self.margin_x_pt + self.print_w_pt, 2)
        self.print_y1 = round(self.margin_y_pt + self.print_h_pt, 2)

        # Zone 1: 6.0 cm Masthead Space (y = 1.0 .. 7.0 cm)
        self.masthead_h_cm = 6.0
        self.masthead_y0 = self.print_y0
        self.masthead_y1 = round(self.masthead_y0 + cm(self.masthead_h_cm), 2)

        # Zone 2: 12.5 cm Top Flyer across 8 Columns (y = 7.0 .. 19.5 cm)
        self.flyer_h_cm = 12.5
        self.flyer_y0 = self.masthead_y1
        self.flyer_y1 = round(self.flyer_y0 + cm(self.flyer_h_cm), 2)

        # Zone 4: 10.0 cm Bottom Anchor Band (y = 42.0 .. 52.0 cm)
        self.bottom_h_cm = 10.0
        self.bottom_y1 = self.print_y1
        self.bottom_y0 = round(self.bottom_y1 - cm(self.bottom_h_cm), 2)

    def col_x0(self, col_1based: int) -> float:
        return round(self.margin_x_pt + (col_1based - 1) * (self.col_w_pt + self.gutter_pt), 2)

    def col_x1(self, col_1based: int, col_span: int) -> float:
        end_col = col_1based + col_span - 1
        return round(self.col_x0(end_col) + self.col_w_pt, 2)


sock = None
f_in = None
req_id = 0

def connect_page_designer():
    global sock, f_in
    for candidate_port in (49200, 47123):
        try:
            sock = socket.create_connection(("127.0.0.1", candidate_port), timeout=2.0)
            sock.settimeout(30.0)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            f_in = sock.makefile("r", encoding="utf-8")
            return
        except Exception:
            pass

    pd_exe = Path(r"E:\RND\Gujarat_Samachar\Page_Designer_Software\pagedesigner.exe")
    if not pd_exe.exists():
        pd_exe = Path(r"E:\RND\open page layout software\pagedesigner.exe")
    subprocess.Popen([str(pd_exe), "--control", str(PORT)], cwd=str(pd_exe.parent))
    for _ in range(30):
        time.sleep(0.4)
        try:
            sock = socket.create_connection(("127.0.0.1", PORT), timeout=2.0)
            sock.settimeout(30.0)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            f_in = sock.makefile("r", encoding="utf-8")
            return
        except Exception:
            pass
    raise RuntimeError("Could not connect to Page Designer on port 47123")


def rpc(method: str, params: dict = None):
    import os
    if os.environ.get("AB_SKIP_SAVE") == "1" and method in ("app.save", "app.export"):
        return None
    global req_id
    req_id += 1
    payload = {"id": req_id, "method": method, "params": params or {}}
    sock.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
    resp = json.loads(f_in.readline())
    if not resp.get("ok"):
        raise RuntimeError(f"RPC {method} failed: {resp}")
    return resp.get("result")


def cmd(command: str, params: dict = None):
    import os
    if command == "file.close" and (os.environ.get("AB_NO_CLOSE") == "1" or os.environ.get("AB_TARGET_SPREAD") is not None):
        return None
    p = dict(params or {})
    if os.environ.get("AB_TARGET_SPREAD") is not None and "spread" in p:
        p["spread"] = int(os.environ["AB_TARGET_SPREAD"])
    return rpc("engine.execute", {"command": command, "params": p})


def batch(commands: list):
    import os
    ts = os.environ.get("AB_TARGET_SPREAD")
    skip_new = os.environ.get("AB_SKIP_FILE_NEW") == "1"
    new_cmds = []
    for c in commands:
        if not isinstance(c, dict):
            continue
        if skip_new and c.get("command") == "file.new":
            continue
        c2 = dict(c)
        if isinstance(c2.get("params"), dict):
            p2 = dict(c2["params"])
            if ts is not None and "spread" in p2:
                p2["spread"] = int(ts)
            c2["params"] = p2
        new_cmds.append(c2)
    has_new = any(isinstance(c, dict) and c.get("command") == "file.new" for c in new_cmds)
    if has_new:
        new_cmds = list(new_cmds) + [{"command": "view.fitPage", "params": {}}]
    if not new_cmds:
        return []
    return rpc("engine.batch", {"commands": new_cmds})


def _utf8_byte_pos(text: str, char_pos: int) -> int:
    return len(text[:char_pos].encode("utf-8"))


BASELINE_START_PT = 28.35
BASELINE_INC_PT = 11.25


def snap_underflow_top(body_y1: float, num_underflow_lines: int = 4) -> float:
    last_k = int((body_y1 - 4.35 - BASELINE_START_PT) // BASELINE_INC_PT)
    first_underflow_k = last_k - (num_underflow_lines - 1)
    first_underflow_baseline_y = BASELINE_START_PT + first_underflow_k * BASELINE_INC_PT
    return round(first_underflow_baseline_y - 9.65, 2)


def snap_frame_bottom_to_baseline(raw_y1: float) -> float:
    k = int((raw_y1 - 4.35 - BASELINE_START_PT) // BASELINE_INC_PT)
    return round(BASELINE_START_PT + k * BASELINE_INC_PT + 4.55, 2)


def fit_aditya_bharat_headline(
    spread_idx: int,
    x0: float,
    cur_y: float,
    x1: float,
    raw_text: str,
    target_lines: int,
    font_family: str = "DB Rasrand Bold",
    font_style: str = "Bold",
    fill_swatch: str = "[Black]",
    hi_pt: float = 82.0,
    lo_pt: float = 16.0,
    plus_one_pt_leading: bool = True,
    align: str = "left",
    fixed_pt: float = None,
):
    """
    Fits an Aditya Bharat headline in 'DB Rasrand Bold' with STRICT Leading = Point Size + 1.0 pt!
    Guarantees rendered lines <= target_lines with zero overset.
    """
    temp_h = cm(6.5)
    clean_text = " ".join(raw_text.replace("\n", " ").split())
    r = cmd("frame.create", {
        "spread": spread_idx,
        "rect": [x0, cur_y, x1, cur_y + temp_h],
        "content": "text",
        "text": clean_text,
    })
    fid, sid = r["id"], r["story"]

    def calc_lead(pt_val: float) -> float:
        return round(pt_val + 1.0, 2) if plus_one_pt_leading else round(pt_val * 1.05, 2)

    def max_pt_for_line(line_str: str) -> float:
        if fixed_pt is not None:
            return fixed_pt
        batch([
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
            {"command": "text.delete", "params": {}},
            {"command": "text.insert", "params": {"text": line_str}},
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
            {"command": "type.char", "params": {"attrs": {
                "fontFamily": font_family,
                "fontStyle": font_style,
                "hScale": 1.0,
                "tracking": 0.0,
            }}},
            {"command": "type.para", "params": {"attrs": {"align": "left", "hyphenate": False}}},
        ])
        lo = int(lo_pt * 2)
        hi = int(hi_pt * 2)
        best = lo_pt
        while lo <= hi:
            mid = (lo + hi) // 2
            pt = round(mid / 2.0, 1)
            lead = calc_lead(pt)
            st = batch([
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
                {"command": "type.char", "params": {"attrs": {"size": pt, "leading": {"kind": "points", "value": lead}}}},
                {"command": "story.get", "params": {"story": sid}},
            ])[-1]
            if st.get("lines") == 1 and st.get("overset") is None:
                best = pt
                lo = mid + 1
            else:
                hi = mid - 1
        return best

    def stretch_line(start_b: int, end_b: int, exp_lines: int):
        chosen_hs = 1.0
        for hs100 in range(106, 99, -1):
            hs = round(hs100 / 100.0, 2)
            st = batch([
                {"command": "text.select", "params": {"story": sid, "anchor": start_b, "focus": end_b}},
                {"command": "type.char", "params": {"attrs": {"hScale": hs, "tracking": 0.0}}},
                {"command": "story.get", "params": {"story": sid}},
            ])[-1]
            if st.get("lines") == exp_lines and st.get("overset") is None:
                chosen_hs = hs
                break
        for trk in range(18, -1, -3):
            st = batch([
                {"command": "text.select", "params": {"story": sid, "anchor": start_b, "focus": end_b}},
                {"command": "type.char", "params": {"attrs": {"hScale": chosen_hs, "tracking": float(trk)}}},
                {"command": "story.get", "params": {"story": sid}},
            ])[-1]
            if st.get("lines") == exp_lines and st.get("overset") is None:
                break

    words = clean_text.split(" ")
    n = len(words)
    if target_lines == 1 or n < 2:
        best_pt = max_pt_for_line(clean_text)
        lead = calc_lead(best_pt)
        batch([
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
            {"command": "text.delete", "params": {}},
            {"command": "text.insert", "params": {"text": clean_text}},
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
            {"command": "type.char", "params": {"attrs": {
                "fontFamily": font_family,
                "fontStyle": font_style,
                "size": best_pt,
                "leading": {"kind": "points", "value": lead},
                "fill": fill_swatch,
                "fillTint": 1.0,
                "hScale": 1.0,
                "tracking": 0.0,
            }}},
            {"command": "type.para", "params": {"attrs": {"align": align, "hyphenate": False}}},
        ])
        stretch_line(0, 99999, 1)
        actual_lines = 1
    else:
        candidates = []
        for idx in range(1, n):
            l1 = " ".join(words[:idx])
            l2 = " ".join(words[idx:])
            candidates.append((abs(len(l1) - len(l2)), l1, l2))
        candidates.sort(key=lambda x: x[0])
        best_split = (candidates[0][1], candidates[0][2])
        best_score = -999.0
        best_pt = fixed_pt if fixed_pt is not None else lo_pt
        if fixed_pt is None:
            for _, l1, l2 in candidates[:5]:
                pt1 = max_pt_for_line(l1)
                pt2 = max_pt_for_line(l2)
                raw_min = min(pt1, pt2, hi_pt)
                score = raw_min - 0.6 * abs(pt1 - pt2)
                if score > best_score:
                    best_score = score
                    best_split = (l1, l2)
                    best_pt = raw_min
        joined = f"{best_split[0]}\n{best_split[1]}"
        lead = calc_lead(best_pt)
        batch([
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
            {"command": "text.delete", "params": {}},
            {"command": "text.insert", "params": {"text": joined}},
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
            {"command": "type.char", "params": {"attrs": {
                "fontFamily": font_family,
                "fontStyle": font_style,
                "size": best_pt,
                "leading": {"kind": "points", "value": lead},
                "fill": fill_swatch,
                "fillTint": 1.0,
                "hScale": 1.0,
                "tracking": 0.0,
            }}},
            {"command": "type.para", "params": {"attrs": {"align": align, "hyphenate": False}}},
        ])
        st_now = cmd("story.get", {"story": sid})
        # If still > 2 lines, step down hScale slightly until strictly 2 lines
        while (st_now.get("lines") or 2) > 2 and best_pt > 14.0:
            best_pt = round(best_pt - 0.5, 1)
            lead = calc_lead(best_pt)
            st_now = batch([
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
                {"command": "type.char", "params": {"attrs": {"size": best_pt, "leading": {"kind": "points", "value": lead}}}},
                {"command": "story.get", "params": {"story": sid}},
            ])[-1]
        txt_now = st_now.get("text", joined)
        nl_pos = txt_now.find("\n")
        if nl_pos > 0:
            b_nl = _utf8_byte_pos(txt_now, nl_pos)
            stretch_line(0, b_nl, 2)
            stretch_line(b_nl + 1, 99999, 2)
        actual_lines = 2

    curr_h = temp_h
    st_init = cmd("story.get", {"story": sid})
    rendered_lines = st_init.get("lines") or actual_lines
    lead_now = calc_lead(best_pt)
    lo_h = max(14, int(lead_now * rendered_lines))
    hi_h = max(lo_h + 18, int(lead_now * rendered_lines + 34))
    best_h = hi_h
    while lo_h <= hi_h:
        mid_h = ((lo_h + hi_h) // 4) * 2
        if mid_h < lo_h:
            mid_h = lo_h
        st = batch([
            {"command": "transform.resize", "params": {"ids": [fid], "from": [x0, cur_y, x1, cur_y + curr_h], "to": [x0, cur_y, x1, cur_y + mid_h]}},
            {"command": "story.get", "params": {"story": sid}},
        ])[-1]
        curr_h = mid_h
        if (st.get("lines") or 0) <= rendered_lines and st.get("overset") is None:
            best_h = mid_h
            hi_h = mid_h - 2
        else:
            lo_h = mid_h + 2
    if curr_h != best_h:
        cmd("transform.resize", {"ids": [fid], "from": [x0, cur_y, x1, cur_y + curr_h], "to": [x0, cur_y, x1, cur_y + best_h]})
        curr_h = best_h

    return fid, sid, best_pt, curr_h


def place_red_subject_blurb(spread_idx: int, x0: float, y0: float, word_text: str):
    """
    Places the Aditya Bharat Red Subject Blurb (matching Screenshot 2):
      - Solid Red Box ('FlyerCrimson') on left edge
      - 1-Word category in 'DB Hindi 6', 22.0 pt, White ('[Paper]')
      - 3.0 pt Gray Rule ('ClosingGray') at the bottom of the red blurb
      - Text Wrap ('boundingBox') so body text wraps cleanly on the right
    """
    bw = cm(1.95)
    bh = cm(1.30)
    bx0, by0 = round(x0, 2), round(y0, 2)
    bx1, by1 = round(bx0 + bw, 2), round(by0 + bh, 2)

    r_box = cmd("frame.create", {
        "spread": spread_idx,
        "rect": [bx0, by0, bx1, by1],
        "content": "text",
        "text": word_text,
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_box["id"]], "swatch": "FlyerCrimson", "tint": 1.0}},
        {"command": "object.stroke", "params": {"ids": [r_box["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
        {"command": "object.textWrap", "params": {"ids": [r_box["id"]], "mode": "boundingBox", "offset": [1.5, 0.0, 2.5, 4.5]}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_box["id"]],
            "columns": 1,
            "inset": [0.0, 1.0, 2.5, 1.0],
            "verticalJustification": "center",
        }},
        {"command": "text.select", "params": {"story": r_box["story"], "anchor": 0, "focus": 999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi 6",
            "fontStyle": "Regular",
            "size": 22.0,
            "leading": {"kind": "points", "value": 22.0},
            "fill": "[Paper]",
            "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "firstLineIndent": 0.0, "hyphenate": False, "gridAlign": "none"}}},
    ])
    # Verify non-overset; if DB Hindi 6 Regular isn't matched by style name, fall back to DB Hindi Bold 22pt
    st_blurb = cmd("story.get", {"story": r_box["story"]})
    if st_blurb.get("overset") is not None or (st_blurb.get("lines") or 0) == 0:
        batch([
            {"command": "text.select", "params": {"story": r_box["story"], "anchor": 0, "focus": 999}},
            {"command": "type.char", "params": {"attrs": {
                "fontFamily": "DB Hindi",
                "fontStyle": "Bold",
                "size": 22.0,
                "leading": {"kind": "points", "value": 22.0},
                "fill": "[Paper]",
                "fillTint": 1.0,
            }}},
        ])
    # 3.0 pt Gray Rule at bottom of the Red Blurb
    rule_y = round(by1 - 3.2, 2)
    r_grule = cmd("line.create", {
        "spread": spread_idx,
        "a": [round(bx0 + 3.5, 2), rule_y],
        "b": [round(bx1 - 3.5, 2), rule_y],
    })
    cmd("object.stroke", {"ids": [r_grule["id"]], "swatch": "ClosingGray", "weight": 3.0, "tint": 1.0})
    return r_box["id"]


def place_photo_and_caption_cmyk(
    spread_idx: int,
    px0: float,
    py0: float,
    px1: float,
    cap_y1: float,
    photo_filename: str,
    caption_text: str,
    cap_h: float = 23.5,
):
    """
    Places a CMYK Photo + 'DB Hindi 7' 10.0 pt / 10.2 pt leading Caption directly below it.
    """
    cap_y0 = round(cap_y1 - cap_h, 2)
    py1 = round(cap_y0 - 2.0, 2)

    r_photo = cmd("frame.create", {
        "spread": spread_idx,
        "rect": [px0, py0, px1, py1],
        "content": "graphic",
    })
    batch([
        {"command": "file.place", "params": {"frame": r_photo["id"], "path": str(PHOTOS_DIR / photo_filename)}},
        {"command": "object.fit", "params": {"ids": [r_photo["id"]], "mode": "fillProportionally"}},
        {"command": "object.stroke", "params": {"ids": [r_photo["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
        {"command": "object.textWrap", "params": {"ids": [r_photo["id"]], "mode": "boundingBox", "offset": [0.0, 0.0, 2.0, 0.0]}},
    ])

    r_cap = cmd("frame.create", {
        "spread": spread_idx,
        "rect": [px0, cap_y0, px1, cap_y1],
        "content": "text",
        "text": caption_text,
    })
    batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_cap["id"]], "columns": 1, "verticalJustification": "top"}},
        {"command": "object.textWrap", "params": {"ids": [r_cap["id"]], "mode": "boundingBox", "offset": [0.0, 0.0, 3.0, 0.0]}},
        {"command": "text.select", "params": {"story": r_cap["story"], "anchor": 0, "focus": 999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi 7",
            "fontStyle": "Bold",
            "size": 10.0,
            "leading": {"kind": "points", "value": 10.2},
            "fill": "[Black]",
            "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "leftJustified", "firstLineIndent": 0.0, "hyphenate": False}}},
    ])
    return r_photo["id"], r_cap["id"]


EXTRA_HINDI_SENTENCES = (
    "\nकेंद्र और राज्य सरकारों के समन्वय से इस राष्ट्रीय महायोजना को निर्धारित समय-सीमा के भीतर पूरा करने का लक्ष्य रखा गया है। "
    "मंत्रालय के वरिष्ठ अधिकारियों के अनुसार आधुनिक तकनीक और डिजिटल निगरानी प्रणाली के माध्यम से प्रत्येक चरण की प्रगति की समीक्षा की जा रही है। "
    "अर्थशास्त्रियों और औद्योगिक विशेषज्ञों का मानना है कि इस ऐतिहासिक पहल से देश के करोड़ों नागरिकों को सीधा लाभ मिलेगा और रोजगार के नए अवसर सृजित होंगे। "
    "स्थानीय प्रशासन और संबंधित विभागों को भी निर्देश दिए गए हैं कि आम नागरिकों को सभी सेवाएं पारदर्शी और त्वरित रूप से उपलब्ध कराई जाएं।"
)


def fit_aditya_bharat_body(
    sid: int,
    byline_city: str,
    byline_agency: str,
    raw_body: str,
):
    """
    Fits Aditya Bharat story flow:
      1. 3-Tone Byline on 1 single line: City (100% Black Bold) | Pipe (Red) | Agency (60% Gray) centered,
         with a full-column Gray Rule below ('ClosingGray', 0.85 pt) + matra-safe gap.
      2. Body Copy: 'DB Hindi' Regular, 11.0 pt / 11.25 pt leading, Baseline Grid Locked ('allLines'),
         100% Pure Black ('[Black]').
    """
    has_byline = bool(byline_city and byline_agency)
    byline_line = f"{byline_city.strip()} | {byline_agency.strip()}\n" if has_byline else ""
    city_b = len(byline_city.strip().encode("utf-8")) if has_byline else 0
    pipe_b = len(" | ".encode("utf-8")) if has_byline else 0
    agency_b = len(byline_agency.strip().encode("utf-8")) if has_byline else 0
    byline_total_b = len(byline_line.encode("utf-8"))

    def apply_style(body_str: str):
        full_txt = byline_line + body_str
        cmds = [
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
            {"command": "text.delete", "params": {}},
            {"command": "text.insert", "params": {"text": full_txt}},
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
            {"command": "type.char", "params": {"attrs": {
                "fontFamily": "DB Hindi",
                "fontStyle": "Regular",
                "size": 11.0,
                "leading": {"kind": "points", "value": 11.25},
                "fill": "[Black]",
                "fillTint": 1.0,
                "hScale": 1.0,
                "tracking": 0.0,
            }}},
            {"command": "type.para", "params": {"attrs": {
                "align": "leftJustified",
                "firstLineIndent": 8.0,
                "spaceBefore": 0.0,
                "spaceAfter": 0.0,
                "hyphenate": False,
                "gridAlign": "allLines",
                "ruleBelow": {"on": False},
            }}},
        ]
        if has_byline:
            cmds.extend([
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": byline_total_b - 1}},
                {"command": "type.char", "params": {"attrs": {
                    "fontFamily": "DB Hindi",
                    "fontStyle": "Bold",
                    "size": 11.5,
                    "leading": {"kind": "points", "value": 12.5},
                    "fill": "[Black]",
                    "fillTint": 1.0,
                }}},
                {"command": "type.para", "params": {"attrs": {
                    "align": "center",
                    "firstLineIndent": 0.0,
                    "spaceBefore": 0.0,
                    "spaceAfter": 6.5,
                    "gridAlign": "none",
                    "ruleBelow": {
                        "on": True,
                        "weight": 0.85,
                        "color": "ClosingGray",
                        "tint": 1.0,
                        "columnWidth": True,
                        "offset": 3.5,
                    },
                }}},
                {"command": "text.select", "params": {"story": sid, "anchor": city_b, "focus": city_b + pipe_b}},
                {"command": "type.char", "params": {"attrs": {
                    "fill": "FlyerCrimson",
                    "fillTint": 1.0,
                }}},
                {"command": "text.select", "params": {"story": sid, "anchor": city_b + pipe_b, "focus": city_b + pipe_b + agency_b}},
                {"command": "type.char", "params": {"attrs": {
                    "fill": "ClosingGray",
                    "fillTint": 1.0,
                }}},
            ])
        cmds.append({"command": "story.get", "params": {"story": sid}})
        return batch(cmds)[-1]

    ext_text = raw_body.strip()
    st = apply_style(ext_text)
    while st.get("overset") is None:
        ext_text = ext_text + EXTRA_HINDI_SENTENCES
        st = apply_style(ext_text)

    paras = [p.strip() for p in ext_text.split("\n") if p.strip()]
    tokens = []
    for p_idx, p in enumerate(paras):
        p_words = p.split(" ")
        for w_idx, w in enumerate(p_words):
            if not w:
                continue
            sep = "\n" if (w_idx == len(p_words) - 1 and p_idx < len(paras) - 1) else " "
            tokens.append((w, sep))

    def build_tokens(k: int) -> str:
        if k <= 0:
            return ""
        parts = [tokens[i][0] + tokens[i][1] for i in range(k - 1)]
        last_w = tokens[k - 1][0].rstrip("।.,;:")
        parts.append(last_w)
        joined = "".join(parts).strip()
        if not joined.endswith("।"):
            joined += "।"
        return joined

    lo_w, hi_w = 5, len(tokens)
    best_k = lo_w
    while lo_w <= hi_w:
        mid_w = (lo_w + hi_w) // 2
        cand = build_tokens(mid_w)
        st_c = apply_style(cand)
        if st_c.get("overset") is None:
            best_k = mid_w
            lo_w = mid_w + 1
        else:
            hi_w = mid_w - 1

    final_body = build_tokens(best_k)
    st_f = apply_style(final_body)
    return st_f.get("lines", 0)


def build_aditya_bharat_page1():
    t0 = time.perf_counter()
    connect_page_designer()
    grid = AdityaBharatPage1Grid()

    for _ in range(5):
        try:
            cmd("file.close", {"save": False})
        except Exception:
            break

    batch([
        {"command": "file.new", "params": {
            "width": grid.width_pt,
            "height": grid.height_pt,
            "pages": 1,
            "facingPages": False,
            "columns": grid.cols,
            "gutter": grid.gutter_pt,
            "margins": grid.margin_x_pt,
            "title": "आदित्य भारत — पेज 01 मास्टर फ्रंट पेज (34x53 सेमी | प्रिंट एरिया 32x51 सेमी)",
        }},
        {"command": "document.preferences", "params": {
            "baselineGrid": {
                "start": grid.margin_y_pt,
                "increment": 11.25,
                "relativeTo": "topOfPage",
            }
        }},
        {"command": "swatch.create", "params": {"name": "FlyerCrimson", "color": "#c4121a"}},
        {"command": "swatch.create", "params": {"name": "ClosingGray", "color": "#808285"}},
        {"command": "swatch.create", "params": {"name": "BoxGray40", "color": "#cccccc"}},
        {"command": "swatch.create", "params": {"name": "EditPointerBg", "color": "#f4f4f4"}},
    ])

    # ==========================================================================
    # ZONE 1: 6.0 CM FRONT PAGE MASTHEAD SPACE (y = 1.0 .. 7.0 cm, Cols 1..8)
    # ==========================================================================
    mh_x0, mh_y0, mh_x1, mh_y1 = grid.print_x0, grid.masthead_y0, grid.print_x1, grid.masthead_y1
    folio_h = cm(0.80)
    folio_y0 = round(mh_y1 - folio_h, 2)

    fit_aditya_bharat_headline(
        0, mh_x0, round(mh_y0 + cm(0.35), 2), mh_x1,
        raw_text="आदित्य भारत",
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="FlyerCrimson",
        hi_pt=96.0,
        lo_pt=78.0,
        align="center",
        fixed_pt=92.0,
    )

    r_mh_line1 = cmd("line.create", {"spread": 0, "a": [mh_x0, folio_y0], "b": [mh_x1, folio_y0]})
    r_mh_line2 = cmd("line.create", {"spread": 0, "a": [mh_x0, mh_y1], "b": [mh_x1, mh_y1]})
    cmd("object.stroke", {"ids": [r_mh_line1["id"], r_mh_line2["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    r_folio = cmd("frame.create", {
        "spread": 0,
        "rect": [mh_x0, folio_y0, mh_x1, mh_y1],
        "content": "text",
        "text": "इंदौर, भोपाल, रायपुर, अहमदाबाद और नई दिल्ली से एक साथ प्रकाशित   |   मंगलवार, 20 अक्टूबर 2026   |   पृष्ठ : 08   |   मूल्य : रु. 5.00",
    })
    batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_folio["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_folio["story"], "anchor": 0, "focus": 999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Bold",
            "size": 12.0,
            "leading": {"kind": "points", "value": 13.0},
            "fill": "[Black]",
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "hyphenate": False}}},
    ])

    # ==========================================================================
    # ZONE 2: TOP 8-COLUMN FLYER (Height = 12.5 cm, y = 7.0 .. 19.5 cm, Cols 1..8)
    #   - Top Subhead ABOVE Headline: 18.0 pt ('DB Hindi' Bold)
    #   - 8-Col Flyer Headline: 'DB Rasrand Bold' (Leading = pt + 1.0 pt)
    #   - Below: 6 Columns Text (Cols 1..3 & Cols 6..8) + Center 2-Col Photo (Cols 4..5)
    # ==========================================================================
    fl_x0, fl_y0, fl_x1 = grid.print_x0, grid.flyer_y0, grid.print_x1
    fl_y1 = snap_frame_bottom_to_baseline(grid.flyer_y1)
    fl_cur_y = round(fl_y0 + mm(2.0), 2)

    fl_subhead = "आगामी पांच वर्षों में दस लाख करोड़ रुपये का निवेश होगा : पच्चीस लाख युवाओं को मिलेगा प्रत्यक्ष रोजगार और महानगरों में प्रदूषण से मिलेगी बड़ी राहत"
    _, _, _, fl_sub_h = fit_aditya_bharat_headline(
        0, fl_x0, fl_cur_y, fl_x1,
        raw_text=fl_subhead,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=18.0,
        lo_pt=18.0,
        align="center",
        fixed_pt=18.0,
    )
    fl_cur_y = round(fl_cur_y + fl_sub_h + 1.5, 2)

    fl_headline = "पचास प्रमुख शहरों में दौड़ेगी हाई-स्पीड ग्रीन मेट्रो"
    _, _, fl_h_pt, fl_h_h = fit_aditya_bharat_headline(
        0, fl_x0, fl_cur_y, fl_x1,
        raw_text=fl_headline,
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=68.0,
        lo_pt=52.0,
        align="center",
    )
    fl_cur_y = round(fl_cur_y + fl_h_h + 3.0, 2)

    fl_body_y0 = fl_cur_y
    fl_body_y1 = fl_y1

    r_fl_body = cmd("frame.create", {
        "spread": 0,
        "rect": [fl_x0, fl_body_y0, fl_x1, fl_body_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_fl_body["id"]],
        "columns": 8,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })

    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(4),
        fl_body_y0,
        grid.col_x1(4, 2),
        fl_body_y1,
        "ab_p1_flyer_cmyk.jpg",
        "नई दिल्ली में हाई-स्पीड ग्रीन मेट्रो कॉरिडोर के आधुनिक मॉडल का परिचालन दृश्य। — फाइल फोटो",
        cap_h=23.5,
    )

    place_red_subject_blurb(0, grid.col_x0(1), round(fl_body_y0 + cm(2.6), 2), "सौगात")

    fl_body_copy = (
        "केंद्रीय मंत्रिमंडल ने देश के पचास प्रमुख शहरों में हाई-स्पीड ग्रीन मेट्रो और स्मार्ट इंडस्ट्रियल कॉरिडोर के निर्माण को मंजूरी दे दी है। "
        "देश के शहरी बुनियादी ढांचे और औद्योगिक विकास को नई रफ्तार देने के लिए इस महत्वाकांक्षी योजना के तहत आगामी पांच वर्षों में दस लाख करोड़ "
        "रुपये का सीधा पूंजीगत निवेश किया जाएगा। प्रधानमंत्री की अध्यक्षता में हुई उच्चस्तरीय बैठक में यह निर्णय लिया गया कि सभी नए मेट्रो कॉरिडोर "
        "सौ प्रतिशत सौर ऊर्जा और हरित हाइड्रोजन तकनीक से संचालित होंगे।\n"
        "इसके साथ ही दिल्ली-मुंबई, अमृतसर-कोलकाता और बेंगलुरु-चेन्नई औद्योगिक गलियारों के पास बीस नए लॉजिस्टिक्स हब और मैन्युफैक्चरिंग क्लस्टर विकसित "
        "किए जाएंगे, जिससे पच्चीस लाख से अधिक युवाओं को प्रत्यक्ष रोजगार प्राप्त होगा। केंद्रीय शहरी विकास एवं आवासन मंत्रालय के वरिष्ठ अधिकारियों ने "
        "बताया कि प्रथम चरण में मध्य प्रदेश, छत्तीसगढ़, राजस्थान, गुजरात, उत्तर प्रदेश और महाराष्ट्र के बारह प्रमुख औद्योगिक नगरों को इस हाई-स्पीड "
        "नेटवर्क से जोड़ा जाएगा। प्रत्येक शहर में मेट्रो स्टेशनों को रेलवे जंक्शन, अंतरराज्यीय बस टर्मिनल और एयरपोर्ट से सीधे कनेक्ट करने के लिए "
        "मल्टी-मॉडल ट्रांसपोर्ट हब बनाए जाएंगे ताकि यात्रियों को एक ही कार्ड से निर्बाध यात्रा की सुविधा मिल सके।\n"
        "आर्थिक मामलों की मंत्रिमंडलीय समिति के अनुसार इस परियोजना के लिए केंद्र सरकार पैंतीस प्रतिशत अनुदान देगी, जबकि शेष राशि राज्य सरकारों और "
        "सार्वजनिक-निजी भागीदारी के माध्यम से जुटाई जाएगी। स्वदेशी कोच निर्माण को बढ़ावा देने के लिए मेक इन इंडिया के तहत पचहत्तर प्रतिशत मेट्रो कोच "
        "और सिग्नलिंग उपकरण देश के भीतर ही तैयार किए जाएंगे। इससे देश के सूक्ष्म, लघु और मध्यम उद्यमों को तीन लाख करोड़ रुपये के नए कार्यादेश मिलेंगे।"
    )
    fit_aditya_bharat_body(r_fl_body["story"], "नई दिल्ली", "ब्यूरो", fl_body_copy)

    sep1_y = round(fl_y1 + mm(1.5), 2)
    r_sep1 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep1_y], "b": [grid.print_x1, sep1_y]})
    cmd("object.stroke", {"ids": [r_sep1["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # ZONE 3: MIDDLE BAND (y = sep1_y + 2mm .. bottom_y0 - 3mm, Cols 1..8)
    # ==========================================================================
    mid_y0 = round(sep1_y + mm(2.0), 2)
    sep2_y = round(grid.bottom_y0 - mm(1.8), 2)
    mid_y1 = snap_frame_bottom_to_baseline(sep2_y - mm(1.5))

    # --- 3A. MAIN LEAD STORY IN COLS 1..5 (5 COLUMNS) ---
    lead_x0 = grid.col_x0(1)
    lead_x1 = grid.col_x1(1, 5)
    lead_cur_y = mid_y0

    lead_headline = "जीएसटी सुधारों और त्योहारी मांग से भारतीय अर्थव्यवस्था को मिली नई रफ्तार"
    _, _, lead_h_pt, lead_hh = fit_aditya_bharat_headline(
        0, lead_x0, lead_cur_y, lead_x1,
        raw_text=lead_headline,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=72.0,
        lo_pt=44.0,
        align="left",
    )
    lead_cur_y = round(lead_cur_y + lead_hh + 1.0, 2)

    lead_subhead = "विनिर्माण और सेवा क्षेत्र में रिकॉर्ड उछाल : विदेशी मुद्रा भंडार सात सौ बारह अरब डॉलर के पार, बाजारों में दोगुनी बिक्री"
    _, _, _, lead_sub_h = fit_aditya_bharat_headline(
        0, lead_x0, lead_cur_y, lead_x1,
        raw_text=lead_subhead,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=17.5,
        lo_pt=13.5,
        align="left",
    )
    lead_cur_y = round(lead_cur_y + lead_sub_h + 3.5, 2)

    lead_body_y0 = lead_cur_y
    lead_body_y1 = mid_y1

    # 3A-1. Col 1 (1 Column Full Story Box in 40% Gray with 2.5 mm inset on all 4 sides!)
    gbox_x0 = grid.col_x0(1)
    gbox_x1 = grid.col_x1(1, 1)
    inset_2_5mm = mm(2.5)  # 7.09 pt exact 2.5 mm on all 4 sides

    def fit_box_completely(
        sid: int,
        head_str: str,
        raw_bullets: str,
        head_pt: float = 18.0,
        head_align: str = "center",
        body_pt: float = 10.8,
        body_lead: float = 11.4,
        para_space: float = 2.8,
    ):
        head_line = head_str.strip() + "\n"
        head_b = len(head_line.encode("utf-8"))
        extra_bullets = (
            "\n• ग्रामीण और अर्ध-शहरी क्षेत्रों में स्वरोजगार व कौशल विकास केंद्रों का विस्तार किया गया।"
            "\n• कृषि प्रसंस्करण, कोल्ड स्टोरेज और आधुनिक वेयरहाउस निर्माण के लिए विशेष अनुदान जारी।"
            "\n• सौर ऊर्जा, हरित हाइड्रोजन और इलेक्ट्रिक वाहन विनिर्माण में रिकॉर्ड विदेशी निवेश आया।"
            "\n• राष्ट्रीय राजमार्गों और मालढुलाई गलियारों के निर्माण से लॉजिस्टिक्स लागत में बड़ी कमी आई।"
        )

        def style_box(b_txt: str):
            full_t = head_line + b_txt
            return batch([
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
                {"command": "text.delete", "params": {}},
                {"command": "text.insert", "params": {"text": full_t}},
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
                {"command": "type.char", "params": {"attrs": {
                    "fontFamily": "DB Hindi",
                    "fontStyle": "Bold",
                    "size": body_pt,
                    "leading": {"kind": "points", "value": body_lead},
                    "fill": "[Black]",
                    "fillTint": 1.0,
                }}},
                {"command": "type.para", "params": {"attrs": {
                    "align": "leftJustified",
                    "firstLineIndent": 0.0,
                    "spaceBefore": 0.0,
                    "spaceAfter": para_space,
                    "hyphenate": False,
                    "gridAlign": "none",
                    "ruleBelow": {"on": False},
                }}},
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": head_b - 1}},
                {"command": "type.char", "params": {"attrs": {
                    "fontFamily": "DB Rasrand Bold",
                    "fontStyle": "Bold",
                    "size": head_pt,
                    "leading": {"kind": "points", "value": round(head_pt + 1.0, 2)},
                    "fill": "[Black]",
                    "fillTint": 1.0,
                }}},
                {"command": "type.para", "params": {"attrs": {
                    "align": head_align,
                    "spaceAfter": 5.5,
                    "ruleBelow": {
                        "on": True,
                        "weight": 1.3,
                        "color": "[Black]",
                        "tint": 1.0,
                        "columnWidth": True,
                        "offset": 3.0,
                    },
                }}},
                {"command": "story.get", "params": {"story": sid}},
            ])[-1]

        ext_b = raw_bullets.strip()
        st = style_box(ext_b)
        while st.get("overset") is None:
            ext_b = ext_b + extra_bullets
            st = style_box(ext_b)

        b_paras = [p.strip() for p in ext_b.split("\n") if p.strip()]
        b_tokens = []
        for p_i, p in enumerate(b_paras):
            w_list = p.split(" ")
            for w_i, w in enumerate(w_list):
                if not w:
                    continue
                if w == "•" and w_i + 1 < len(w_list):
                    continue
                if w_i > 0 and w_list[w_i - 1] == "•":
                    w = "• " + w
                sep = "\n" if (w_i == len(w_list) - 1 and p_i < len(b_paras) - 1) else " "
                b_tokens.append((w, sep))

        def build_b(k: int) -> str:
            if k <= 0:
                return ""
            pts = [b_tokens[i][0] + b_tokens[i][1] for i in range(k - 1)]
            lw = b_tokens[k - 1][0].rstrip("।.,;:")
            pts.append(lw)
            j = "".join(pts).strip()
            if not j.endswith("।"):
                j += "।"
            return j

        lo, hi = 5, len(b_tokens)
        best = lo
        while lo <= hi:
            mid = (lo + hi) // 2
            st_c = style_box(build_b(mid))
            if st_c.get("overset") is None:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        style_box(build_b(best))

    r_gbox = cmd("frame.create", {
        "spread": 0,
        "rect": [gbox_x0, lead_body_y0, gbox_x1, lead_body_y1],
        "content": "text",
        "text": "",
    })
    gbox_body = (
        "• दूसरी तिमाही में सकल घरेलू उत्पाद की वृद्धि दर आठ दशमलव दो प्रतिशत पर पहुंची।\n"
        "• ऑटो, आवास और निर्माण क्षेत्र में इस तिमाही के दौरान चालीस प्रतिशत की ऐतिहासिक बढ़ोतरी।\n"
        "• देश का विदेशी मुद्रा भंडार सात सौ बारह अरब डॉलर के सर्वकालिक शिखर पर पहुंचा।\n"
        "• सूक्ष्म, लघु और मध्यम उद्यमों के लिए दो लाख करोड़ की विशेष ऋण गारंटी योजना लागू।\n"
        "• ग्रामीण बाजारों में ट्रैक्टर, दोपहिया वाहनों और कृषि उपकरणों की मांग में भारी उछाल।\n"
        "• रक्षा, फार्मा और डिजिटल सेवाओं के निर्यात ने स्थापित किया नया वैश्विक कीर्तिमान।\n"
        "• औद्योगिक गलियारों में नए निवेश से लाखों युवाओं के लिए रोजगार के अवसर खुले।\n"
        "• डिजिटल लेनदेन और हरित ऊर्जा क्षेत्र में भी भारत ने रचा नया कीर्तिमान।"
    )
    batch([
        {"command": "object.fill", "params": {"ids": [r_gbox["id"]], "swatch": "[Black]", "tint": 0.20}},
        {"command": "object.stroke", "params": {"ids": [r_gbox["id"]], "swatch": "ClosingGray", "weight": 0.75, "tint": 1.0}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_gbox["id"]],
            "columns": 1,
            "inset": [inset_2_5mm, inset_2_5mm, inset_2_5mm, inset_2_5mm],
            "verticalJustification": "top",
        }},
    ])
    fit_box_completely(r_gbox["story"], "आर्थिक रफ्तार", gbox_body, head_pt=18.0, head_align="center", body_pt=10.8, body_lead=11.4, para_space=2.3)

    # 3A-2. Cols 2..5 (4 Columns of Lead Body Copy + Center Photo in Cols 3..4 + Caption + Box + Text Flow)
    lbody_x0 = grid.col_x0(2)
    lbody_x1 = grid.col_x1(2, 4)
    r_lead_body = cmd("frame.create", {
        "spread": 0,
        "rect": [lbody_x0, lead_body_y0, lbody_x1, lead_body_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_lead_body["id"]],
        "columns": 4,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })

    lpx0 = grid.col_x0(3)
    lpx1 = grid.col_x1(3, 2)
    lpy0 = lead_body_y0

    spec_box_y1 = round(snap_underflow_top(lead_body_y1, num_underflow_lines=5) - 3.0, 2)
    spec_box_h = cm(4.78)
    spec_box_y0 = round(spec_box_y1 - spec_box_h, 2)
    lcap_y1 = round(spec_box_y0 - 4.0, 2)

    place_photo_and_caption_cmyk(
        0, lpx0, lpy0, lpx1, lcap_y1,
        "ab_p1_lead_cmyk.jpg",
        "त्योहारी सीजन के दौरान राजधानी के प्रमुख बाजारों में खरीदारी के लिए उमड़ी ग्राहकों की भारी भीड़। — फाइल फोटो",
        cap_h=23.5,
    )

    # 2-Column Highlight Box below Lead Photo Caption (1-line 16 pt DB Rasrand Bold Box Headline & 2.5 mm inset)
    r_spec_box = cmd("frame.create", {
        "spread": 0,
        "rect": [lpx0, spec_box_y0, lpx1, spec_box_y1],
        "content": "text",
        "text": "",
    })
    spec_body = (
        "• देश के पचास लाख सूक्ष्म और लघु उद्यमों के लिए दो लाख करोड़ की नई क्रेडिट गारंटी योजना लागू।\n"
        "• ग्रामीण महिलाओं के स्वयं सहायता समूहों को डिजिटल विपणन और निर्यात के लिए विशेष अनुदान।\n"
        "• घरेलू इलेक्ट्रॉनिक्स, कपड़ा और ऑटो पार्ट्स निर्माण इकाइयों को बिजली शुल्क व जीएसटी रिफंड में राहत।\n"
        "• जिला स्तर पर नए स्टार्टअप क्लस्टर और युवाओं को बिना गारंटी दस लाख रुपये तक कार्यशील पूंजी ऋण।"
    )
    batch([
        {"command": "object.fill", "params": {"ids": [r_spec_box["id"]], "swatch": "EditPointerBg", "tint": 1.0}},
        {"command": "object.stroke", "params": {"ids": [r_spec_box["id"]], "swatch": "ClosingGray", "weight": 0.75, "tint": 1.0}},
        {"command": "object.textWrap", "params": {"ids": [r_spec_box["id"]], "mode": "boundingBox", "offset": [2.0, 0.0, 3.0, 0.0]}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_spec_box["id"]],
            "columns": 1,
            "inset": [inset_2_5mm, inset_2_5mm, inset_2_5mm, inset_2_5mm],
            "verticalJustification": "top",
        }},
    ])
    fit_box_completely(r_spec_box["story"], "विशेष पैकेज : छोटे उद्यमों को सस्ता ऋण", spec_body, head_pt=16.0, head_align="left", body_pt=10.5, body_lead=11.3, para_space=2.2)

    place_red_subject_blurb(0, grid.col_x0(2), round(lead_body_y0 + cm(3.1), 2), "शानदार")

    lead_body_copy = (
        "भारतीय अर्थव्यवस्था ने वैश्विक चुनौतियों के बावजूद चालू वित्त वर्ष की दूसरी तिमाही में शानदार प्रदर्शन करते हुए आठ दशमलव दो "
        "प्रतिशत की विकास दर हासिल की है। केंद्रीय वित्त मंत्रालय द्वारा जारी ताजा आर्थिक समीक्षा रिपोर्ट के अनुसार वस्तु एवं सेवा कर संग्रह, "
        "औद्योगिक उत्पादन सूचकांक और ग्रामीण उपभोग में आई जबरदस्त तेजी ने देश के आर्थिक पहिए को नई गति प्रदान की है।\n"
        "त्योहारी सीजन के दौरान देशभर के बाजारों में ऑटोमोबाइल, आवास, इलेक्ट्रॉनिक्स और स्वर्ण आभूषणों की बिक्री में पिछले वर्ष की तुलना में "
        "चालीस प्रतिशत से अधिक की वृद्धि दर्ज की गई है। वित्त मंत्री ने कहा कि सरकार द्वारा बुनियादी ढांचे में किए जा रहे रिकॉर्ड पूंजीगत निवेश "
        "और उत्पादन आधारित प्रोत्साहन योजनाओं के कारण भारत दुनिया का सबसे आकर्षक विनिर्माण केंद्र बनकर उभरा है।\n"
        "भारतीय रिजर्व बैंक के आंकड़ों के मुताबिक देश का विदेशी मुद्रा भंडार बढ़कर सात सौ बारह अरब डॉलर के सर्वकालिक उच्च स्तर पर पहुंच गया है। "
        "इसके साथ ही बैंकिंग क्षेत्र में गैर-निष्पादित परिसंपत्तियों का स्तर घटकर पिछले बारह वर्षों के न्यूनतम स्तर पर आ गया है, जिससे उद्योगों को "
        "सस्ती दरों पर ऋण मिल रहा है। कृषि और ग्रामीण अर्थव्यवस्था में भी मानसून की अनुकूल स्थिति और सरकारी खरीद नीतियों के चलते सकारात्मक उछाल देखा जा रहा है।"
    )
    fit_aditya_bharat_body(r_lead_body["story"], "नई दिल्ली", "ब्यूरो", lead_body_copy)

    # --- 3B. RIGHT WING IN COLS 6..8 (3 COLUMNS): SECOND LEAD + THIRD NEWS + FOURTH SINGLE-COL NEWS ---
    rw_x0 = grid.col_x0(6)
    rw_x1 = grid.col_x1(6, 3)
    rw_split_y = round(mid_y0 + (mid_y1 - mid_y0) * 0.54, 2)
    rw_top_y1 = snap_frame_bottom_to_baseline(rw_split_y - 3.0)

    sl_cur_y = mid_y0
    _, _, _, sl_k_h = fit_aditya_bharat_headline(
        0, rw_x0, sl_cur_y, rw_x1,
        raw_text="सुप्रीम कोर्ट की संविधान पीठ का ऐतिहासिक निर्देश : हरित क्षेत्रों का संरक्षण अनिवार्य",
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=14.5,
        lo_pt=12.5,
        align="left",
    )
    sl_cur_y = round(sl_cur_y + sl_k_h + 1.0, 2)

    _, _, sl_h_pt, sl_hh = fit_aditya_bharat_headline(
        0, rw_x0, sl_cur_y, rw_x1,
        raw_text="स्वच्छ पर्यावरण और प्रदूषण मुक्त हवा देश के हर नागरिक का मौलिक अधिकार",
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=38.0,
        lo_pt=28.0,
        align="left",
    )
    sl_cur_y = round(sl_cur_y + sl_hh + 2.5, 2)

    r_sl_body = cmd("frame.create", {
        "spread": 0,
        "rect": [rw_x0, sl_cur_y, rw_x1, rw_top_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_sl_body["id"]],
        "columns": 3,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })

    sl_cap_y1 = round(snap_underflow_top(rw_top_y1, num_underflow_lines=4) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(7),
        sl_cur_y,
        grid.col_x1(7, 2),
        sl_cap_y1,
        "ab_p1_second_lead_cmyk.jpg",
        "राजधानी में हरित परिवहन और पर्यावरण संरक्षण अभियान का दृश्य। — फाइल फोटो",
        cap_h=23.0,
    )

    sl_body_copy = (
        "सर्वोच्च न्यायालय की संविधान पीठ ने एक ऐतिहासिक फैसले में स्पष्ट किया है कि स्वच्छ पर्यावरण और प्रदूषण मुक्त वायु प्रत्येक "
        "नागरिक का बुनियादी मौलिक अधिकार है। अदालत ने सभी राज्य सरकारों को निर्देश दिया है कि शहरी नियोजन में हरित क्षेत्रों का अनुपात "
        "अनिवार्य रूप से पच्चीस प्रतिशत रखा जाए और औद्योगिक इकाइयों के उत्सर्जन की रियल-टाइम डिजिटल निगरानी की जाए।\n"
        "पीठ ने यह भी आदेश दिया कि नदियों के किनारे अवैध निर्माण और रासायनिक कचरा बहाने वाले कारखानों पर कठोर दंडात्मक कार्रवाई की जाए "
        "तथा पर्यावरण संरक्षण कोष की राशि का उपयोग केवल वनीकरण और स्वच्छ जल स्रोतों के पुनर्जीवन में ही किया जाए।"
    )
    fit_aditya_bharat_body(r_sl_body["story"], "नई दिल्ली", "एजेंसी", sl_body_copy)

    r_rw_div = cmd("line.create", {"spread": 0, "a": [rw_x0, rw_split_y], "b": [rw_x1, rw_split_y]})
    cmd("object.stroke", {"ids": [r_rw_div["id"]], "swatch": "ClosingGray", "weight": 0.75, "tint": 1.0})

    rw_bot_y0 = round(rw_split_y + 4.0, 2)
    # Bottom-Left of Right Wing (Cols 6..7, 2 Columns): THIRD NEWS STORY
    t3_x0 = grid.col_x0(6)
    t3_x1 = grid.col_x1(6, 2)
    _, _, _, t3_hh = fit_aditya_bharat_headline(
        0, t3_x0, rw_bot_y0, t3_x1,
        raw_text="सेना के बेड़े में शामिल हुए पंद्रह स्वदेशी प्रचंड हेलीकॉप्टर",
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=30.0,
        lo_pt=24.0,
        align="left",
    )
    t3_by0 = round(rw_bot_y0 + t3_hh + 2.0, 2)
    r_t3_body = cmd("frame.create", {
        "spread": 0,
        "rect": [t3_x0, t3_by0, t3_x1, mid_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_t3_body["id"]],
        "columns": 2,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, t3_x0, round(t3_by0 + cm(2.4), 2), "ताकत")
    t3_body_copy = (
        "सियाचिन से लेकर रेगिस्तानी इलाकों तक हर मौसम में दुश्मन के ठिकानों को ध्वस्त करने में सक्षम स्वदेशी लड़ाकू हेलीकॉप्टर प्रचंड की नई "
        "स्क्वाड्रन पश्चिमी सीमा पर तैनात कर दी गई है। रक्षा मंत्रालय के अनुसार इन हेलीकॉप्टरों में अस्सी प्रतिशत से अधिक स्वदेशी उपकरण, आधुनिक "
        "रडार प्रणाली और हवा से हवा में मार करने वाली घातक मिसाइलें लगाई गई हैं।\n"
        "रक्षा मंत्री ने वैज्ञानिकों और इंजीनियरों को बधाई देते हुए कहा कि भारत अब रक्षा आयातक से बदलकर विश्व के पचास से अधिक देशों को सैन्य "
        "उपकरण निर्यात करने वाला प्रमुख राष्ट्र बन गया है।"
    )
    fit_aditya_bharat_body(r_t3_body["story"], "जोधपुर", "एजेंसी", t3_body_copy)

    # Bottom-Right of Right Wing (Col 8, 1 Column): FOURTH SINGLE-COLUMN NEWS (strict 2-line headline)
    t4_x0 = grid.col_x0(8)
    t4_x1 = grid.col_x1(8, 1)
    _, _, _, t4_hh = fit_aditya_bharat_headline(
        0, t4_x0, rw_bot_y0, t4_x1,
        raw_text="रबी फसलों के एमएसपी में बढ़ोतरी",
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=21.0,
        lo_pt=16.5,
        align="left",
    )
    t4_by0 = round(rw_bot_y0 + t4_hh + 2.0, 2)
    r_t4_body = cmd("frame.create", {
        "spread": 0,
        "rect": [t4_x0, t4_by0, t4_x1, mid_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {"ids": [r_t4_body["id"]], "columns": 1, "verticalJustification": "top"})
    t4_body_copy = (
        "केंद्र सरकार ने किसानों को बड़ी राहत देते हुए गेहूं, चना, मसूर और सरसों सहित प्रमुख रबी फसलों के न्यूनतम समर्थन मूल्य में उल्लेखनीय "
        "बढ़ोतरी की घोषणा की है। कृषि मंत्रालय के अनुसार देशभर की मंडियों में डिजिटल खरीद केंद्र स्थापित किए जाएंगे और किसानों के बैंक खातों "
        "में अड़तालीस घंटे के भीतर सीधा भुगतान सुनिश्चित किया जाएगा।"
    )
    fit_aditya_bharat_body(r_t4_body["story"], "नई दिल्ली", "एजेंसी", t4_body_copy)

    r_sep2 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep2_y], "b": [grid.print_x1, sep2_y]})
    cmd("object.stroke", {"ids": [r_sep2["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # ZONE 4: 10.0 CM BOTTOM BAND (y = 42.0 .. 52.0 cm, Cols 1..8 = 1 + 5 + 2)
    #   - Left Col 1 (1 Col)    : Single-Column Story
    #   - Center Cols 2..6 (5C) : Bottom Anchor Story (45-50 pt 1-Line Headline in DB Rasrand Bold)
    #   - Right Cols 7..8 (2C)  : Right 2-Column Story
    # ==========================================================================
    bot_y0 = grid.bottom_y0
    bot_y1 = snap_frame_bottom_to_baseline(grid.bottom_y1)

    # --- 4A. Left Col 1 (1 Column Story, strict 2-line headline) ---
    b1_x0 = grid.col_x0(1)
    b1_x1 = grid.col_x1(1, 1)
    _, _, _, b1_hh = fit_aditya_bharat_headline(
        0, b1_x0, bot_y0, b1_x1,
        raw_text="डिजिटल पेमेंट का नया विश्व रिकॉर्ड",
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=21.0,
        lo_pt=16.5,
        align="left",
    )
    b1_by0 = round(bot_y0 + b1_hh + 2.0, 2)
    r_b1_body = cmd("frame.create", {
        "spread": 0,
        "rect": [b1_x0, b1_by0, b1_x1, bot_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {"ids": [r_b1_body["id"]], "columns": 1, "verticalJustification": "top"})
    b1_body_copy = (
        "भारतीय रिजर्व बैंक द्वारा जारी ताजा आंकड़ों के अनुसार इस माह यूपीआई के माध्यम से होने वाले डिजिटल लेनदेन ने अब तक के सभी रिकॉर्ड "
        "तोड़ दिए हैं। ग्रामीण और अर्ध-शहरी क्षेत्रों में क्यूआर कोड और वॉइस पेमेंट तकनीक के विस्तार से छोटे व्यापारियों का कारोबार पैंतीस "
        "प्रतिशत बढ़ा है तथा भारत डिजिटल भुगतान में विश्व का सबसे अग्रणी देश बन गया है।"
    )
    fit_aditya_bharat_body(r_b1_body["story"], "मुंबई", "एजेंसी", b1_body_copy)

    # --- 4B. Center Cols 2..6 (5-Column Bottom Anchor Story, 45-50 pt 1-Line Headline in DB Rasrand Bold) ---
    anc_x0 = grid.col_x0(2)
    anc_x1 = grid.col_x1(2, 5)
    anc_cur_y = bot_y0

    _, _, anc_h_pt, anc_hh = fit_aditya_bharat_headline(
        0, anc_x0, anc_cur_y, anc_x1,
        raw_text="स्वदेशी एआई मिशन से बदलेगा भारत",
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=50.0,
        lo_pt=45.0,
        align="center",
    )
    anc_cur_y = round(anc_cur_y + anc_hh + 1.0, 2)

    _, _, _, anc_sub_h = fit_aditya_bharat_headline(
        0, anc_x0, anc_cur_y, anc_x1,
        raw_text="बाईस भारतीय भाषाओं में तैयार होगा डिजिटल ज्ञान कोष : दस हजार स्टार्टअप्स को मिलेगा सुपरकंप्यूटिंग और स्वदेशी चिप निर्माण का सीधा लाभ",
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=15.5,
        lo_pt=12.5,
        align="center",
    )
    anc_cur_y = round(anc_cur_y + anc_sub_h + 3.0, 2)

    r_anc_body = cmd("frame.create", {
        "spread": 0,
        "rect": [anc_x0, anc_cur_y, anc_x1, bot_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_anc_body["id"]],
        "columns": 5,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })

    anc_cap_y1 = round(snap_underflow_top(bot_y1, num_underflow_lines=3) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(3),
        anc_cur_y,
        grid.col_x1(3, 2),
        anc_cap_y1,
        "ab_p1_anchor_cmyk.jpg",
        "बेंगलुरु के राष्ट्रीय अनुसंधान केंद्र में विकसित स्वदेशी आर्टिफिशियल इंटेलिजेंस व नैनो-चिप प्रणाली। — फाइल फोटो",
        cap_h=23.0,
    )

    anc_body_copy = (
        "भारत को इक्कीसवीं सदी की वैश्विक डिजिटल महाशक्ति बनाने की दिशा में कदम बढ़ाते हुए केंद्र सरकार ने इंडिया एआई और सेमीकंडक्टर मिशन "
        "के दूसरे चरण का शुभारंभ कर दिया है। इस अभियान के अंतर्गत देश के प्रमुख भारतीय प्रौद्योगिकी संस्थानों और भारतीय विज्ञान संस्थान के "
        "वैज्ञानिक मिलकर बाईस भारतीय भाषाओं में काम करने वाला स्वदेशी लार्ज लैंग्वेज मॉडल तैयार कर रहे हैं। इससे करोड़ों किसानों, छात्रों "
        "और नागरिकों को अपनी मातृभाषा में स्वास्थ्य, कृषि, शिक्षा और कानूनी सेवाओं की सटीक जानकारी तुरंत उपलब्ध हो सकेगी। "
        "गुजरात के धोलेरा, साणंद और असम के मोरीगांव में निर्माणाधीन सेमीकंडक्टर फैब इकाइयों में आगामी वर्ष से स्वदेशी माइक्रोप्रोसेसर चिप्स का "
        "व्यावसायिक उत्पादन प्रारंभ हो जाएगा। मंत्रालय के अनुसार देश के दस हजार से अधिक डीप-टेक स्टार्टअप्स और युवा शोधकर्ताओं को पच्चीस हजार "
        "हाई-परफॉर्मेंस ग्राफिक्स प्रोसेसिंग यूनिट्स से युक्त राष्ट्रीय सुपरकंप्यूटिंग ग्रिड की सुविधा रियायती दरों पर उपलब्ध कराई जाएगी।"
    )
    fit_aditya_bharat_body(r_anc_body["story"], "बेंगलुरु", "एजेंसी", anc_body_copy)

    # --- 4C. Right Cols 7..8 (2-Column Story) ---
    b3_x0 = grid.col_x0(7)
    b3_x1 = grid.col_x1(7, 2)
    _, _, _, b3_hh = fit_aditya_bharat_headline(
        0, b3_x0, bot_y0, b3_x1,
        raw_text="त्योहारी सीजन में चलेंगी तीन हजार विशेष ट्रेनें",
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=28.0,
        lo_pt=22.0,
        align="left",
    )
    b3_by0 = round(bot_y0 + b3_hh + 2.0, 2)
    r_b3_body = cmd("frame.create", {
        "spread": 0,
        "rect": [b3_x0, b3_by0, b3_x1, bot_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_b3_body["id"]],
        "columns": 2,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, b3_x0, round(b3_by0 + cm(2.2), 2), "राहत")
    b3_body_copy = (
        "त्योहारी सीजन में घर लौटने वाले करोड़ों रेल यात्रियों को कन्फर्म सीट उपलब्ध कराने के लिए रेल मंत्रालय ने विशेष परिचालन योजना लागू "
        "की है। नई दिल्ली, मुंबई, इंदौर, भोपाल, रायपुर और अहमदाबाद से प्रमुख राज्यों के लिए प्रतिदिन डेढ़ सौ से अधिक अतिरिक्त वंदे भारत और "
        "अमृत भारत एक्सप्रेस ट्रेनें चलाई जा रही हैं। प्रमुख जंक्शनों पर विशेष नियंत्रण कक्ष और सुरक्षा बल चौबीस घंटे सक्रिय रहेंगे।"
    )
    fit_aditya_bharat_body(r_b3_body["story"], "मोहाली", "एजेंसी", b3_body_copy)

    cmd("edit.deselectAll")
    cmd("view.fitPage", {})

    out_pd = VAULT_DIR / "Aditya_Bharat_Page_01_34x53.pagedesigner"
    out_png = VAULT_DIR / "Aditya_Bharat_Page_01_34x53.png"
    out_pdf = VAULT_DIR / "Aditya_Bharat_Page_01_CMYK_34x53.pdf"
    rpc("app.save", {"path": str(out_pd)})
    rpc("app.export", {"path": str(out_png), "page": 0, "scale": 1.5})
    try:
        rpc("app.export", {"path": str(out_pdf), "page": 0})
    except Exception:
        pass

    artifact_png = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\8707c72d-58b0-4715-a099-3efffcd57514\aditya_bharat_page_01_34x53.png")
    artifact_png.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_png, artifact_png)

    print(
        f"=== ADITYA BHARAT PAGE 01 BUILT IN {time.perf_counter()-t0:.2f}s ===\n"
        f"    FlyerHead={fl_h_pt}pt | LeadHead={lead_h_pt}pt | AnchorHead={anc_h_pt}pt\n"
        f"    Saved: {out_pd}"
    )


if __name__ == "__main__":
    build_aditya_bharat_page1()
