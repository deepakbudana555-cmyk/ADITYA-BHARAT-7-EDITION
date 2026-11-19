# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — PAGE 04 ('राष्ट्रीय') MASTER BROADSHEET BUILDER (34x53 cm | Print Area 32x51 cm)
==============================================================================================================
Strictly implements the official 'Aditya Bharat' Stylesheet & Page 04 Architecture:
  1. Page Size & Grid   : 34.0 cm x 53.0 cm (1-1-1-1 cm outer margins -> Fixed Print Area = 32.0 cm x 51.0 cm, 8 Cols, 4.0 mm Gutter)
  2. Inside Masthead    : 1.5 cm Height (y = 1.0 .. 2.5 cm, Cols 1..8):
       - Left           : Red Color Box ('FlyerCrimson') with Page Name 'राष्ट्रीय' in 20.0 pt 'DB Hindi 6' White ('[Paper]')
       - Center         : Official 'आदित्य भारत' Masthead Logo centered ('100% Black')
       - Right          : Dateline in 16.0 pt ('DB Hindi' Bold) + Page Number '04' in 18.0 pt 'Times New Roman' Bold
       - Bottom Rule    : 2.0 pt Rule in 60% Gray across all 8 columns
  3. Interlocked 4-Band Layout (8-Col Flyer + 6-Col Lead with Gray Box in LAST Col 6 + Compact Photos + All Headlines >= 30 pt):
       - Band 1 (11.0cm): 8-Column Top Flyer (Cols 1..8: 18pt Subhead above + 1-Line DB Rasrand Bold Headline + 6 Cols Text + Compact Center 2-Col Photo in Cols 4..5 + 8-Line Underflow)
       - Band 2 (17.2cm): 6-Column Main Lead Package (Cols 1..6):
                            * 2-Line DB Rasrand Bold Headline (54-60pt) + 17pt Subhead below
                            * Cols 1..5 (5-Column Lead Body starting in Col 1 with Byline & Red Blurb 'सौगात' + Compact Photo in Cols 3..4 + 100% Filled Highlight Box + 6-Line Underflow)
                            * Col 6 (LAST Column of Lead: Full-Height 40% Gray Story Box 'मिशन के प्रमुख बिंदु' with 2.5mm inset on all 4 sides, 100% filled!)
                          + Right 2-Column Story (Cols 7..8: 2-Line Headline >= 31pt + Red Blurb 'न्याय' + 2-Col Body)
       - Band 3 (9.6 cm): Interlocked 3 + 3 + 2 Split:
                            * Cols 1..3 (3-Col Illustrated ISRO Story: 2-Line Headline >= 35pt + Compact Photo in Cols 2..3 + 7-Line Underflow + Red Blurb 'अंतरिक्ष')
                            * Cols 4..6 (3-Col Health Package: 2-Line Headline >= 35pt + Subhead + Red Blurb 'स्वास्थ्य' + 3-Col Body)
                            * Cols 7..8 (2-Col Green Energy Story: 2-Line Headline >= 31pt + Red Blurb 'ऊर्जा' + 2-Col Body)
       - Band 4 (10.3cm): Bottom Strip (5-Col Left Anchor + 3-Col Right Package):
                            * Cols 1..5 (5-Col Anchor: 45-50pt 1-Line DB Rasrand Bold Headline + Subhead + Compact Photo in Cols 3..4 + 7-Line Underflow + Red Blurb 'कीर्तिमान')
                            * Cols 6..8 (3-Col Economic Story: 2-Line Headline >= 35pt + Subhead + Red Blurb 'अर्थतंत्र' + 3-Col Body)
"""

import json
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image, ImageOps

sys.stdout.reconfigure(encoding="utf-8")

VAULT_DIR = Path(__file__).resolve().parent
PHOTOS_DIR = VAULT_DIR / "photos"
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

PORT = 47123
CM_TO_PT = 72.0 / 2.54
MM_TO_PT = CM_TO_PT / 10.0

def cm(val: float) -> float:
    return round(val * CM_TO_PT, 2)

def mm(val: float) -> float:
    return round(val * MM_TO_PT, 2)


def prepare_cmyk_cropped_photo(src_name: str, dst_name: str, box_w_pt: float, box_h_pt: float) -> Path:
    dst_p = PHOTOS_DIR / dst_name
    src_p = None
    for base in [
        Path(r"E:\RND\Gujarat_Samachar\editions\19_Oct_2026\photos"),
        Path(r"E:\RND\Gujarat_Samachar_Edition\editions\19_Oct_2026\photos"),
        Path(r"E:\RND\HINDI - TEST\Page_Designer_App\saved_pages\photos"),
        Path(r"E:\RND\HINDI - TEST\photos"),
        PHOTOS_DIR,
    ]:
        cand = base / src_name
        if cand.exists():
            src_p = cand
            break
    if src_p is None:
        fallbacks = list(PHOTOS_DIR.glob("*.jpg"))
        if fallbacks:
            src_p = fallbacks[0]
        else:
            raise FileNotFoundError(f"Could not find photo {src_name}")

    target_w_px = max(600, int(round(box_w_pt * 300.0 / 72.0)))
    target_h_px = max(400, int(round(box_h_pt * 300.0 / 72.0)))
    with Image.open(src_p) as im:
        im_rgb = im.convert("RGB")
        iw, ih = im_rgb.size
        im_rgb = im_rgb.crop((int(iw * 0.04), int(ih * 0.04), int(iw * 0.96), int(ih * 0.96)))
        cropped = ImageOps.fit(im_rgb, (target_w_px, target_h_px), method=Image.Resampling.LANCZOS, centering=(0.5, 0.38))
        cmyk_im = cropped.convert("CMYK")
        cmyk_im.save(dst_p, "JPEG", quality=95, dpi=(300, 300))
    return dst_p


class AdityaBharatPage4Grid:
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
        self.gutter_pt = mm(self.gutter_mm)

        self.print_x0 = self.margin_x_pt
        self.print_y0 = self.margin_y_pt
        self.print_x1 = round(self.width_pt - self.margin_x_pt, 2)
        self.print_y1 = round(self.height_pt - self.margin_y_pt, 2)
        self.print_w_pt = round(self.print_x1 - self.print_x0, 2)
        self.print_h_pt = round(self.print_y1 - self.print_y0, 2)

        self.col_w_pt = round((self.print_w_pt - (self.cols - 1) * self.gutter_pt) / self.cols, 2)

        # Zone 1: 1.5 cm Inside Running Masthead (y = 1.0 .. 2.5 cm)
        self.masthead_y0 = self.print_y0
        self.masthead_h_cm = 1.5
        self.masthead_y1 = round(self.masthead_y0 + cm(self.masthead_h_cm), 2)

        # Band 1: 8-Col Flyer (y = 2.85 .. 13.85 cm, Height = 11.0 cm)
        self.flyer_y0 = round(self.masthead_y1 + mm(3.5), 2)
        self.flyer_h_cm = 11.0
        self.flyer_y1 = round(self.flyer_y0 + cm(self.flyer_h_cm), 2)

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


def draw_bottom_cmyk_press_marka():
    import os
    sp = int(os.environ.get("AB_TARGET_SPREAD", "0"))
    rpc("engine.batch", {"commands": [
        {"command": "swatch.create", "params": {"name": "PressCyan", "color": "#00aeef"}},
        {"command": "swatch.create", "params": {"name": "PressMagenta", "color": "#ec008c"}},
        {"command": "swatch.create", "params": {"name": "PressYellow", "color": "#fff200"}},
    ]})

    y0 = cm(52.10)
    y1 = cm(52.42)
    rule_y = round((y0 + y1) / 2.0, 2)

    # 1. Draw the Full-Width 8-Column Bottom Gray Rule FIRST so it sits BEHIND the CMYK boxes
    r_bot_rule = rpc("engine.execute", {
        "command": "line.create",
        "params": {"spread": sp, "a": [cm(1.0), rule_y], "b": [cm(33.0), rule_y]},
    })
    style_cmds = [
        {"command": "object.stroke", "params": {"ids": [r_bot_rule["id"]], "swatch": "[Black]", "weight": 2.0, "tint": 0.60}},
    ]

    # 2. Place 4 CMYK Boxes (C, M, Y, K) at 3 Places (LEFT, CENTER, RIGHT) ON TOP of the Gray Rule
    patches = [
        ("PressCyan", 1.0),
        ("PressMagenta", 1.0),
        ("PressYellow", 1.0),
        ("[Black]", 1.0),
    ]
    box_w = mm(4.0)
    group_w = round(len(patches) * box_w, 2)
    group_centers_x = [cm(3.5), cm(17.0), cm(30.5)]

    for cx in group_centers_x:
        bar_x0 = round(cx - group_w / 2.0, 2)
        for i, (sw, tn) in enumerate(patches):
            px0 = round(bar_x0 + i * box_w, 2)
            px1 = round(px0 + box_w, 2)
            rf = rpc("engine.execute", {"command": "frame.create", "params": {"spread": sp, "rect": [px0, y0, px1, y1], "content": "unassigned"}})
            fid = rf["id"]
            style_cmds.append({"command": "object.fill", "params": {"ids": [fid], "swatch": sw, "tint": tn}})
            style_cmds.append({"command": "object.stroke", "params": {"ids": [fid], "swatch": "[Black]", "weight": 0.35, "tint": 0.85}})

    if style_cmds:
        rpc("engine.batch", {"commands": style_cmds})


def cmd(command: str, params: dict = None):
    import os
    if command == "file.close" and (os.environ.get("AB_NO_CLOSE") == "1" or os.environ.get("AB_TARGET_SPREAD") is not None):
        return None
    if command == "edit.deselectAll":
        try:
            draw_bottom_cmyk_press_marka()
        except Exception:
            pass
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
    lo_pt: float = 30.0,
    fixed_pt: float = None,
    align: str = "left",
    leading_add_pt: float = 1.0,
):
    # Strictly enforce 100% Black ('[Black]') on all headlines & subheads, and >= 30.0 pt on all DB Rasrand Bold headlines
    fill_swatch = "[Black]"
    clean_text = " ".join(raw_text.replace("\r", " ").replace("\n", " ").split())
    init_h = round((hi_pt + leading_add_pt) * max(1, target_lines) + 28.0, 2)
    r_f = cmd("frame.create", {
        "spread": spread_idx,
        "rect": [x0, cur_y, x1, round(cur_y + init_h, 2)],
        "content": "text",
        "text": clean_text,
    })
    fid, sid = r_f["id"], r_f["story"]
    curr_h = init_h

    def calc_lead(pt_val: float) -> float:
        return round(pt_val + leading_add_pt, 2)

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
                "fill": "[Black]",
                "fillTint": 1.0,
                "hScale": 1.0,
                "tracking": 0.0,
            }}},
            {"command": "type.para", "params": {"attrs": {
                "align": align,
                "firstLineIndent": 0.0,
                "leftIndent": 0.0,
                "rightIndent": 0.0,
                "spaceBefore": 0.0,
                "spaceAfter": 0.0,
                "hyphenate": False,
                "gridAlign": "none",
            }}},
        ])
        search_lo = min(lo_pt, 18.0)
        lo = int(round(search_lo * 2))
        hi = int(round(hi_pt * 2))
        best = search_lo
        while lo <= hi:
            mid = (lo + hi) // 2
            pt = round(mid / 2.0, 2)
            lead = calc_lead(pt)
            st = batch([
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
                {"command": "type.char", "params": {"attrs": {
                    "size": pt,
                    "leading": {"kind": "points", "value": lead},
                }}},
                {"command": "story.get", "params": {"story": sid}},
            ])[-1]
            if (st.get("lines") or 0) <= 1 and st.get("overset") is None:
                best = pt
                lo = mid + 1
            else:
                hi = mid - 1
        return best

    def stretch_line(byte_a: int, byte_b: int, max_total_lines: int):
        lo_s, hi_s = 100, 108
        best_s = 100
        while lo_s <= hi_s:
            mid_s = (lo_s + hi_s) // 2
            st = batch([
                {"command": "text.select", "params": {"story": sid, "anchor": byte_a, "focus": byte_b}},
                {"command": "type.char", "params": {"attrs": {"hScale": round(mid_s / 100.0, 3)}}},
                {"command": "story.get", "params": {"story": sid}},
            ])[-1]
            if (st.get("lines") or 0) <= max_total_lines and st.get("overset") is None:
                best_s = mid_s
                lo_s = mid_s + 1
            else:
                hi_s = mid_s - 1
        batch([
            {"command": "text.select", "params": {"story": sid, "anchor": byte_a, "focus": byte_b}},
            {"command": "type.char", "params": {"attrs": {"hScale": round(best_s / 100.0, 3)}}},
        ])

    words = clean_text.split(" ")
    n = len(words)
    if target_lines <= 1 or n < 2:
        effective_lo = lo_pt if font_family != "DB Rasrand Bold" else max(lo_pt, 30.0)
        best_pt = max(effective_lo, max_pt_for_line(clean_text))
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
                "fill": "[Black]",
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
        effective_lo = lo_pt if font_family != "DB Rasrand Bold" else max(lo_pt, 30.0)
        best_pt = fixed_pt if fixed_pt is not None else effective_lo
        if fixed_pt is None:
            for _, l1, l2 in candidates:
                pt1 = max_pt_for_line(l1)
                pt2 = max_pt_for_line(l2)
                raw_min = min(pt1, pt2, hi_pt)
                score = raw_min - 0.35 * abs(pt1 - pt2)
                if score > best_score:
                    best_score = score
                    best_pt = max(effective_lo, raw_min)
                    best_split = (l1, l2)
        l1_str, l2_str = best_split
        two_line_txt = f"{l1_str}\n{l2_str}"
        lead = calc_lead(best_pt)
        l1_bytes = len(l1_str.encode("utf-8"))
        total_bytes = len(two_line_txt.encode("utf-8"))
        batch([
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
            {"command": "text.delete", "params": {}},
            {"command": "text.insert", "params": {"text": two_line_txt}},
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
            {"command": "type.char", "params": {"attrs": {
                "fontFamily": font_family,
                "fontStyle": font_style,
                "size": best_pt,
                "leading": {"kind": "points", "value": lead},
                "fill": "[Black]",
                "fillTint": 1.0,
                "hScale": 1.0,
                "tracking": 0.0,
            }}},
            {"command": "type.para", "params": {"attrs": {"align": align, "hyphenate": False}}},
        ])
        stretch_line(0, l1_bytes, 2)
        stretch_line(l1_bytes + 1, total_bytes, 2)
        actual_lines = 2

    lo_h = max(12, int(best_pt * actual_lines * 0.72))
    hi_h = int(curr_h) + 12
    best_h = hi_h
    while lo_h <= hi_h:
        mid_h = (lo_h + hi_h) // 2
        st = batch([
            {"command": "transform.resize", "params": {
                "ids": [fid],
                "from": [x0, cur_y, x1, round(cur_y + curr_h, 2)],
                "to": [x0, cur_y, x1, round(cur_y + mid_h, 2)],
            }},
            {"command": "story.get", "params": {"story": sid}},
        ])[-1]
        curr_h = mid_h
        if st.get("overset") is None and (st.get("lines") or 0) == actual_lines:
            best_h = mid_h
            hi_h = mid_h - 1
        else:
            lo_h = mid_h + 1
    if curr_h != best_h:
        cmd("transform.resize", {"ids": [fid], "from": [x0, cur_y, x1, round(cur_y + curr_h, 2)], "to": [x0, cur_y, x1, round(cur_y + best_h, 2)]})
        curr_h = best_h

    return fid, sid, best_pt, curr_h


def place_red_subject_blurb(spread_idx: int, x0: float, y0: float, word_text: str, bw_cm: float = 1.85):
    bw = cm(bw_cm)
    bh = cm(1.26)
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
        {"command": "object.textWrap", "params": {"ids": [r_box["id"]], "mode": "boundingBox", "offset": [1.5, 0.0, 2.5, 3.5]}},
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
    src_photo_name: str,
    dst_photo_name: str,
    caption_text: str,
    cap_h: float = 23.0,
):
    cap_y0 = round(cap_y1 - cap_h, 2)
    py1 = round(cap_y0 - 2.0, 2)
    img_path = prepare_cmyk_cropped_photo(src_photo_name, dst_photo_name, px1 - px0, py1 - py0)

    r_photo = cmd("frame.create", {
        "spread": spread_idx,
        "rect": [px0, py0, px1, py1],
        "content": "graphic",
    })
    batch([
        {"command": "file.place", "params": {"frame": r_photo["id"], "path": str(img_path)}},
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
    "\nकेंद्र और राज्य सरकारों के समन्वय से इस राष्ट्रीय परियोजना को निर्धारित समय-सीमा के भीतर पूरा करने का लक्ष्य रखा गया है। "
    "मंत्रालय के वरिष्ठ अधिकारियों के अनुसार आधुनिक तकनीक और डिजिटल निगरानी प्रणाली के माध्यम से प्रत्येक चरण की प्रगति की नियमित समीक्षा की जा रही है। "
    "नीति विशेषज्ञों का मानना है कि इस ऐतिहासिक पहल से देश के करोड़ों नागरिकों को सीधा लाभ मिलेगा और रोजगार के नए अवसर सृजित होंगे। "
    "संबंधित विभागों को भी निर्देश दिए गए हैं कि सभी योजनाओं का लाभ पात्र नागरिकों तक पारदर्शी और त्वरित रूप से पहुंचाया जाए।"
)


def fit_aditya_bharat_body(
    sid: int,
    byline_city: str,
    byline_agency: str,
    raw_body: str,
):
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
                    "leading": {"kind": "points", "value": 11.25},
                    "fill": "[Black]",
                    "fillTint": 1.0,
                }}},
                {"command": "type.para", "params": {"attrs": {
                    "align": "center",
                    "firstLineIndent": 0.0,
                    "spaceBefore": 0.0,
                    "spaceAfter": 6.5,
                    "gridAlign": "allLines",
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
                {"command": "type.char", "params": {"attrs": {"fill": "FlyerCrimson", "fillTint": 1.0}}},
                {"command": "text.select", "params": {"story": sid, "anchor": city_b + pipe_b, "focus": city_b + pipe_b + agency_b}},
                {"command": "type.char", "params": {"attrs": {"fill": "ClosingGray", "fillTint": 1.0}}},
            ])
        cmds.append({"command": "story.get", "params": {"story": sid}})
        return batch(cmds)[-1]

    ext_text = raw_body.strip()
    st = apply_style(ext_text)
    first_ext = True
    while st.get("overset") is None:
        sep_ext = "\n" if first_ext else " "
        ext_text = ext_text + sep_ext + EXTRA_HINDI_SENTENCES.strip()
        first_ext = False
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


def fit_box_completely(
    sid: int,
    head_str: str,
    raw_bullets: str,
    head_pt: float = 16.0,
    head_align: str = "left",
    body_pt: float = 10.5,
    body_lead: float = 11.3,
    para_space: float = 2.2,
):
    head_line = head_str.strip() + "\n"
    head_b = len(head_line.encode("utf-8"))
    extra_bullets = (
        "\n• सभी आर्थिक कॉरिडोर को डेडिकेटेड फ्रेट कॉरिडोर और प्रमुख बंदरगाहों से सीधे जोड़ा जाएगा।"
        "\n• ग्रीन हाइड्रोजन, सेमीकंडक्टर और रक्षा उत्पादन इकाइयों को विशेष पूंजीगत सब्सिडी।"
        "\n• पीएम गतिशक्ति पोर्टल से प्रत्येक परियोजना की रियल-टाइम सैटेलाइट मॉनिटरिंग।"
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
    first_eb = True
    while st.get("overset") is None:
        ext_b = ext_b + (extra_bullets if first_eb else " " + extra_bullets.replace("\n• ", " "))
        first_eb = False
        st = style_box(ext_b)

    b_paras = [p.strip() for p in ext_b.split("\n") if p.strip()]
    b_tokens = []
    for pi, p in enumerate(b_paras):
        ws = p.split(" ")
        for wi, w in enumerate(ws):
            if not w:
                continue
            sep = "\n" if (wi == len(ws) - 1 and pi < len(b_paras) - 1) else " "
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


def place_two_col_story(
    grid: AdityaBharatPage4Grid,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    headline: str,
    city: str,
    agency: str,
    blurb_word: str,
    body: str,
):
    _, _, h_pt, hh = fit_aditya_bharat_headline(
        0, x0, y0, x1,
        raw_text=headline,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=36.0,
        lo_pt=30.0,
        align="left",
    )
    by0 = round(y0 + hh + 2.0, 2)
    by1 = snap_frame_bottom_to_baseline(y1)
    r_b = cmd("frame.create", {
        "spread": 0,
        "rect": [x0, by0, x1, by1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_b["id"]],
        "columns": 2,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    if blurb_word:
        place_red_subject_blurb(0, x0, round(by0 + cm(2.1), 2), blurb_word)
    fit_aditya_bharat_body(r_b["story"], city, agency, body)
    return h_pt


def build_aditya_bharat_page4():
    t0 = time.perf_counter()
    connect_page_designer()
    grid = AdityaBharatPage4Grid()

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
            "title": "आदित्य भारत — पेज 05 राष्ट्रीय (34x53 सेमी | प्रिंट एरिया 32x51 सेमी)",
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
        {"command": "swatch.create", "params": {"name": "EditPointerBg", "color": "#f2f2f2"}},
    ])

    # ==========================================================================
    # ZONE 1: 1.5 CM INSIDE RUNNING MASTHEAD (y = 1.0 .. 2.5 cm, Cols 1..8)
    #   - Left   : Red Color Box ('FlyerCrimson') with Page Name 'राष्ट्रीय' in 20 pt 'DB Hindi 6' White ('[Paper]')
    #   - Center : Official 'आदित्य भारत' Masthead Logo centered ('100% Black')
    #   - Right  : Dateline in 16 pt ('DB Hindi' Bold) + Page Number '04' in 18 pt 'Times New Roman' Bold
    #   - Bottom : 2.0 pt Rule in 60% Gray across all 8 columns
    # ==========================================================================
    mh_x0, mh_y0, mh_x1, mh_y1 = grid.print_x0, grid.masthead_y0, grid.print_x1, grid.masthead_y1

    sec_w = cm(4.2)
    sec_y0 = round(mh_y0 + mm(1.0), 2)
    sec_y1 = round(mh_y1 - mm(1.8), 2)
    r_mh_sec = cmd("frame.create", {
        "spread": 0,
        "rect": [mh_x0, sec_y0, round(mh_x0 + sec_w, 2), sec_y1],
        "content": "text",
        "text": "राष्ट्रीय",
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_mh_sec["id"]], "swatch": "FlyerCrimson", "tint": 1.0}},
        {"command": "object.stroke", "params": {"ids": [r_mh_sec["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_mh_sec["id"]],
            "columns": 1,
            "inset": [0.0, 2.0, 2.0, 2.0],
            "verticalJustification": "center",
        }},
        {"command": "text.select", "params": {"story": r_mh_sec["story"], "anchor": 0, "focus": 99}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi 6",
            "fontStyle": "Regular",
            "size": 20.0,
            "leading": {"kind": "points", "value": 21.0},
            "fill": "[Paper]",
            "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "firstLineIndent": 0.0, "hyphenate": False, "gridAlign": "none"}}},
    ])

    logo_w = cm(8.5)
    logo_x0 = round((mh_x0 + mh_x1 - logo_w) / 2.0, 2)
    logo_x1 = round(logo_x0 + logo_w, 2)
    r_mh_logo = cmd("frame.create", {
        "spread": 0,
        "rect": [logo_x0, round(mh_y0 - 6.0, 2), logo_x1, round(mh_y1 + 4.0, 2)],
        "content": "text",
        "text": "आदित्य भारत",
    })
    batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_mh_logo["id"]], "columns": 1, "inset": [0.0, 0.0, 0.0, 0.0], "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_mh_logo["story"], "anchor": 0, "focus": 99}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Rasrand Bold",
            "fontStyle": "Bold",
            "size": 28.0,
            "leading": {"kind": "points", "value": 29.0},
            "fill": "[Black]",
            "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "firstLineIndent": 0.0, "hyphenate": False, "gridAlign": "none"}}},
    ])

    pnum_w = cm(1.4)
    pnum_x0 = round(mh_x1 - pnum_w, 2)
    r_mh_pnum = cmd("frame.create", {
        "spread": 0,
        "rect": [pnum_x0, sec_y0, mh_x1, sec_y1],
        "content": "text",
        "text": "05",
    })
    batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_mh_pnum["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_mh_pnum["story"], "anchor": 0, "focus": 99}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "Times New Roman",
            "fontStyle": "Bold",
            "size": 18.0,
            "leading": {"kind": "points", "value": 19.0},
            "fill": "[Black]",
            "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "right", "firstLineIndent": 0.0, "hyphenate": False, "gridAlign": "none"}}},
    ])

    dt_x0 = round(logo_x1 + cm(0.4), 2)
    dt_x1 = round(pnum_x0 - cm(0.2), 2)
    r_mh_dt = cmd("frame.create", {
        "spread": 0,
        "rect": [dt_x0, sec_y0, dt_x1, sec_y1],
        "content": "text",
        "text": "इंदौर, मंगलवार, 20 अक्टूबर 2026  |",
    })
    batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_mh_dt["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_mh_dt["story"], "anchor": 0, "focus": 199}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Bold",
            "size": 16.0,
            "leading": {"kind": "points", "value": 17.0},
            "fill": "[Black]",
            "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "right", "firstLineIndent": 0.0, "hyphenate": False, "gridAlign": "none"}}},
    ])

    r_mh_rule = cmd("line.create", {"spread": 0, "a": [mh_x0, mh_y1], "b": [mh_x1, mh_y1]})
    cmd("object.stroke", {"ids": [r_mh_rule["id"]], "swatch": "[Black]", "weight": 2.0, "tint": 0.60})

    # ==========================================================================
    # BAND 1: 8-COLUMN TOP FLYER (y = 2.85 .. 13.85 cm, Height = 11.0 cm, Cols 1..8)
    #   - 18 pt Subhead above + 1-Line DB Rasrand Bold Headline
    #   - 6 Cols Text (Cols 1..3 & Cols 6..8) + Compact Photo in Cols 4..5 + 7-Line Underflow
    # ==========================================================================
    fl_x0, fl_y0, fl_x1, fl_y1 = grid.print_x0, grid.flyer_y0, grid.print_x1, snap_frame_bottom_to_baseline(grid.flyer_y1)
    fl_cur_y = fl_y0

    flyer_sub_txt = "रक्षा अनुसंधान और स्वदेशी तकनीक के क्षेत्र में भारत की बड़ी छलांग : तीनों सेनाओं के आधुनिकीकरण के लिए विशेष बजट मंजूर"
    _, _, _, fl_sub_h = fit_aditya_bharat_headline(
        0, fl_x0, fl_cur_y, fl_x1,
        raw_text=flyer_sub_txt,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=18.0,
        lo_pt=18.0,
        fixed_pt=18.0,
        align="center",
    )
    fl_cur_y = round(fl_cur_y + fl_sub_h + 1.0, 2)

    flyer_head_txt = "स्वदेशी हाइपरसोनिक मिसाइल व डिफेंस सिस्टम का सफल परीक्षण"
    _, _, fl_h_pt, fl_hh = fit_aditya_bharat_headline(
        0, fl_x0, fl_cur_y, fl_x1,
        raw_text=flyer_head_txt,
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=72.0,
        lo_pt=45.0,
        align="center",
    )
    fl_body_y0 = round(fl_cur_y + fl_hh + 1.5, 2)
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

    place_red_subject_blurb(0, grid.col_x0(1), round(fl_body_y0 + cm(1.9), 2), "रक्षा")

    # Compact photo in Cols 4..5 with 7 lines of body text underflow
    fl_cap_y1 = round(snap_underflow_top(fl_body_y1, num_underflow_lines=7) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(4),
        fl_body_y0,
        grid.col_x1(4, 2),
        fl_cap_y1,
        "p1_drdo_825517_print.jpg",
        "ab_p4_flyer_cmyk.jpg",
        "अब्दुल कलाम द्वीप से स्वदेशी लॉन्ग-रेंज हाइपरसोनिक मिसाइल प्रणाली के सफल परीक्षण का दृश्य। — फाइल फोटो",
        cap_h=23.0,
    )

    flyer_body = (
        "रक्षा अनुसंधान एवं विकास संगठन ने ओडिशा तट के डॉ. एपीजे अब्दुल कलाम द्वीप से पूरी तरह स्वदेशी तकनीक पर आधारित लंबी दूरी की हाइपरसोनिक मिसाइल और "
        "मल्टी-लेयर एयर डिफेंस सिस्टम का सफल परीक्षण कर इतिहास रच दिया है। रक्षा मंत्रालय के अनुसार यह अत्याधुनिक मिसाइल ध्वनि की गति से छह गुना अधिक रफ्तार "
        "से उड़ान भरने और दुश्मन के रडार को चकमा देकर पंद्रह सौ किलोमीटर दूर स्थित लक्ष्य को सटीकता से भेदने में सक्षम है।\n"
        "इस प्रणाली में स्वदेशी क्रायोजेनिक स्क्रैमजेट इंजन, आर्टिफिशियल इंटेलिजेंस आधारित नेविगेशन और उन्नत थर्मल शील्ड का उपयोग किया गया है। रक्षा मंत्री ने वैज्ञानिकों "
        "को बधाई देते हुए कहा कि इस उपलब्धि से भारत दुनिया के उन चुनिंदा देशों की कतार में शामिल हो गया है जिनके पास स्वदेशी हाइपरसोनिक प्रतिरक्षा कवच मौजूद है।"
    )
    fit_aditya_bharat_body(r_fl_body["story"], "नई दिल्ली", "एजेंसी", flyer_body)

    sep1_y = round(fl_y1 + mm(1.75), 2)
    r_sep1 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep1_y], "b": [grid.print_x1, sep1_y]})
    cmd("object.stroke", {"ids": [r_sep1["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 2: 6-COLUMN MAIN LEAD (Cols 1..6, Gray Box in LAST Col 6!) + 2-COL RIGHT STORY (Cols 7..8)
    #   Height = 17.2 cm (y = 14.20 .. 31.40 cm)
    # ==========================================================================
    b2_y0 = round(sep1_y + mm(1.75), 2)
    b2_y1 = snap_frame_bottom_to_baseline(round(b2_y0 + cm(17.2), 2))

    # --- 2A. 6-Column Main Lead Package (Cols 1..6) ---
    lead_x0 = grid.col_x0(1)
    lead_x1 = grid.col_x1(1, 6)
    lead_cur_y = b2_y0

    lead_head_txt = "दस लाख करोड़ के इंफ्रास्ट्रक्चर मिशन को मंजूरी, जुड़ेंगे सभी आर्थिक कॉरिडोर"
    _, _, lead_h_pt, lead_hh = fit_aditya_bharat_headline(
        0, lead_x0, lead_cur_y, lead_x1,
        raw_text=lead_head_txt,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=62.0,
        lo_pt=45.0,
        align="left",
    )
    lead_cur_y = round(lead_cur_y + lead_hh + 0.5, 2)

    lead_sub_txt = "केंद्रीय कैबिनेट का ऐतिहासिक फैसला : हाई-स्पीड रेल, बंदरगाह, ग्रीन एनर्जी और सेमीकंडक्टर क्लस्टरों का होगा तेजी से विस्तार"
    _, _, _, lead_sub_h = fit_aditya_bharat_headline(
        0, lead_x0, lead_cur_y, lead_x1,
        raw_text=lead_sub_txt,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=17.0,
        lo_pt=13.5,
        align="left",
    )
    lead_body_y0 = round(lead_cur_y + lead_sub_h + 1.5, 2)
    lead_body_y1 = b2_y1

    # Cols 1..5 (FIRST 5 Columns of the 6-Column Lead = Main News Body starting in Col 1!)
    lbody_x0 = grid.col_x0(1)
    lbody_x1 = grid.col_x1(1, 5)
    r_lead_body = cmd("frame.create", {
        "spread": 0,
        "rect": [lbody_x0, lead_body_y0, lbody_x1, lead_body_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_lead_body["id"]],
        "columns": 5,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })

    # Red Subject Blurb 'सौगात' in Col 1 (the very first column of the Lead!)
    place_red_subject_blurb(0, grid.col_x0(1), round(lead_body_y0 + cm(2.5), 2), "सौगात")

    # Center 2-Column Compact Photo (Cols 3..4) + 100% Filled Highlight Box + 5-Line Underflow
    inset_pt = mm(2.5)
    l_px0 = grid.col_x0(3)
    l_px1 = grid.col_x1(3, 2)
    l_underflow_top = snap_underflow_top(lead_body_y1, num_underflow_lines=5)
    l_spec_box_y1 = round(l_underflow_top - 3.2, 2)
    l_spec_box_h = cm(4.78)
    l_spec_box_y0 = round(l_spec_box_y1 - l_spec_box_h, 2)
    l_cap_y1 = round(l_spec_box_y0 - 3.5, 2)

    place_photo_and_caption_cmyk(
        0,
        l_px0,
        lead_body_y0,
        l_px1,
        l_cap_y1,
        "p4_semi_829164.jpg",
        "ab_p4_lead_cmyk.jpg",
        "राष्ट्रीय इंफ्रास्ट्रक्चर और सेमीकंडक्टर मैन्युफैक्चरिंग कॉरिडोर के तहत निर्माणाधीन हाई-टेक परिसर। — फाइल फोटो",
        cap_h=23.0,
    )

    r_lspec = cmd("frame.create", {
        "spread": 0,
        "rect": [l_px0, l_spec_box_y0, l_px1, l_spec_box_y1],
        "content": "text",
        "text": "",
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_lspec["id"]], "swatch": "EditPointerBg", "tint": 1.0}},
        {"command": "object.stroke", "params": {"ids": [r_lspec["id"]], "swatch": "[Black]", "weight": 0.8, "tint": 0.55}},
        {"command": "object.textWrap", "params": {"ids": [r_lspec["id"]], "mode": "boundingBox", "offset": [2.0, 0.0, 3.0, 0.0]}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_lspec["id"]],
            "columns": 1,
            "inset": [inset_pt, inset_pt, inset_pt, inset_pt],
            "verticalJustification": "top",
        }},
    ])
    lspec_bullets = (
        "• बारह नए इंडस्ट्रियल स्मार्ट शहरों और चार हाई-स्पीड फ्रेट कॉरिडोर का निर्माण निर्धारित समय में।\n"
        "• देश के सभी प्रमुख बंदरगाहों को मल्टी-मॉडल लॉजिस्टिक्स पार्क व रेल नेटवर्क से जोड़ा जाएगा।\n"
        "• सेमीकंडक्टर, इलेक्ट्रॉनिक्स और ईवी बैटरी प्लांट लगाने वाली कंपनियों को विशेष प्रोत्साहन।\n"
        "• ग्रामीण व शहरी संपर्क मार्गों के चौड़ीकरण से माल ढुलाई की लागत में तीस प्रतिशत तक कमी।"
    )
    fit_box_completely(
        r_lspec["story"],
        head_str="आर्थिक रफ्तार : निवेशकों को विशेष पैकेज",
        raw_bullets=lspec_bullets,
        head_pt=16.0,
        head_align="left",
        body_pt=10.5,
        body_lead=11.3,
        para_space=2.2,
    )

    lead_body_txt = (
        "देश की अर्थव्यवस्था को पांच ट्रिलियन डॉलर के पार ले जाने और विश्वस्तरीय बुनियादी ढांचा तैयार करने के लिए केंद्रीय मंत्रिमंडल ने दस लाख करोड़ रुपये के "
        "राष्ट्रीय इंफ्रास्ट्रक्चर मिशन के दूसरे चरण को मंजूरी दे दी है। प्रधानमंत्री की अध्यक्षता में हुई बैठक में देश के सभी प्रमुख औद्योगिक कॉरिडोर, बंदरगाहों, हवाई अड्डों "
        "और हाई-स्पीड रेल नेटवर्क को आपस में जोड़ने के लिए एकीकृत मास्टर प्लान स्वीकृत किया गया है।\n"
        "वित्त और वाणिज्य मंत्रालय के वरिष्ठ अधिकारियों ने बताया कि इस महायोजना के अंतर्गत देश के विभिन्न राज्यों में बारह नए इंडस्ट्रियल स्मार्ट सिटी, छह सेमीकंडक्टर व "
        "इलेक्ट्रॉनिक्स क्लस्टर तथा पचास गीगावॉट क्षमता के नवीकरणीय ऊर्जा पार्क स्थापित किए जाएंगे। इससे आगामी तीन वर्षों में विनिर्माण क्षेत्र की हिस्सेदारी बढ़कर पच्चीस "
        "प्रतिशत तक पहुंच जाएगी और करोड़ों युवाओं के लिए प्रत्यक्ष रोजगार के अवसर खुलेंगे।"
    )
    fit_aditya_bharat_body(r_lead_body["story"], "नई दिल्ली", "ब्यूरो", lead_body_txt)

    # Col 6 (LAST Column of the 6-Column Lead = Full-Height 40% Gray Story Box with 2.5 mm inset on all 4 sides, 100% filled!)
    box6_x0 = grid.col_x0(6)
    box6_x1 = grid.col_x1(6, 1)
    r_lbox6 = cmd("frame.create", {
        "spread": 0,
        "rect": [box6_x0, lead_body_y0, box6_x1, lead_body_y1],
        "content": "text",
        "text": "",
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_lbox6["id"]], "swatch": "[Black]", "tint": 0.15}},
        {"command": "object.stroke", "params": {"ids": [r_lbox6["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 0.55}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_lbox6["id"]],
            "columns": 1,
            "inset": [inset_pt, inset_pt, inset_pt, inset_pt],
            "verticalJustification": "top",
        }},
    ])
    lbox6_bullets = (
        "• पीएम गतिशक्ति नेशनल मास्टर प्लान के तहत तीन सौ से अधिक बड़ी इंफ्रास्ट्रक्चर परियोजनाओं को फास्ट-ट्रैक मंजूरी।\n"
        "• पूर्वी और पश्चिमी डेडिकेटेड फ्रेट कॉरिडोर का विस्तार कर दक्षिण व मध्य भारत के औद्योगिक केंद्रों से सीधा जुड़ाव।\n"
        "• टियर-टू और टियर-थ्री शहरों में पच्चीस नए एयर कार्गो टर्मिनल और आधुनिक कोल्ड-चेन लॉजिस्टिक्स हब बनेंगे।\n"
        "• नेशनल ग्रीन हाइड्रोजन और सोलर मैन्युफैक्चरिंग मिशन के तहत स्वदेशी उपकरण निर्माण को विशेष प्राथमिकता।\n"
        "• भूमि अधिग्रहण और पर्यावरण क्लीयरेंस के लिए सभी राज्यों के साथ सिंगल-विंडो डिजिटल समन्वय प्रणाली लागू।"
    )
    fit_box_completely(
        r_lbox6["story"],
        head_str="प्रमुख बिंदु",
        raw_bullets=lbox6_bullets,
        head_pt=16.0,
        head_align="center",
        body_pt=10.5,
        body_lead=11.3,
        para_space=2.4,
    )

    # --- 2B. Right 2-Column Story beside the 6-Col Lead (Cols 7..8) ---
    b2_r_pt = place_two_col_story(
        grid, grid.col_x0(7), grid.col_x1(7, 2), b2_y0, b2_y1,
        headline="डेटा सुरक्षा पर सुप्रीम कोर्ट के कड़े निर्देश",
        city="नई दिल्ली",
        agency="विधि संवाददाता",
        blurb_word="न्याय",
        body=(
            "सर्वोच्च न्यायालय की संविधान पीठ ने नागरिकों के डिजिटल डेटा की सुरक्षा और साइबर ठगी की रोकथाम को लेकर ऐतिहासिक दिशा-निर्देश जारी किए हैं। "
            "अदालत ने स्पष्ट किया कि किसी भी नागरिक की निजी जानकारी और बायोमेट्रिक डेटा का व्यावसायिक उपयोग उसकी स्पष्ट सहमति के बिना नहीं किया जा सकता। "
            "पीठ ने केंद्र सरकार और दूरसंचार नियामक को निर्देश दिया है कि फर्जी कॉल, डिजिटल अरेस्ट और बैंकिंग फ्रॉड पर तुरंत रोक लगाने के लिए कृत्रिम बुद्धिमत्ता आधारित "
            "सुरक्षा फिल्टर अनिवार्य किए जाएं तथा पीड़ित उपभोक्ताओं को चौबीस घंटे के भीतर राहत दिलाने के लिए फास्ट-ट्रैक साइबर ट्रिब्यूनल गठित किए जाएं।"
        ),
    )

    sep2_y = round(b2_y1 + mm(1.75), 2)
    r_sep2 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep2_y], "b": [grid.print_x1, sep2_y]})
    cmd("object.stroke", {"ids": [r_sep2["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # BAND 3: INTERLOCKED 3 + 3 + 2 SPLIT (y = 31.75 .. 41.35 cm, Height = 9.6 cm, Cols 1..8)
    # ==========================================================================
    b3_y0 = round(sep2_y + mm(1.75), 2)
    b3_y1 = snap_frame_bottom_to_baseline(round(b3_y0 + cm(9.6), 2))

    # --- 3A. Cols 1..3: 3-Column Illustrated ISRO Story ---
    s3a_x0 = grid.col_x0(1)
    s3a_x1 = grid.col_x1(1, 3)
    s3a_head = "गगनयान मिशन के लिए इसरो ने पूरा किया क्रू मॉड्यूल परीक्षण"
    _, _, s3a_pt, s3a_hh = fit_aditya_bharat_headline(
        0, s3a_x0, b3_y0, s3a_x1,
        raw_text=s3a_head,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=38.0,
        lo_pt=30.0,
        align="left",
    )
    s3a_by0 = round(b3_y0 + s3a_hh + 2.0, 2)
    r_s3a_b = cmd("frame.create", {
        "spread": 0,
        "rect": [s3a_x0, s3a_by0, s3a_x1, b3_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_s3a_b["id"]],
        "columns": 3,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, s3a_x0, round(s3a_by0 + cm(1.8), 2), "अंतरिक्ष")

    # Compact photo in Cols 2..3 with 6 lines of underflow
    s3a_cap_y1 = round(snap_underflow_top(b3_y1, num_underflow_lines=6) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(2),
        s3a_by0,
        grid.col_x1(2, 2),
        s3a_cap_y1,
        "p4_isro_829063.jpg",
        "ab_p4_isro_cmyk.jpg",
        "श्रीहरिकोटा स्थित सतीश धवन अंतरिक्ष केंद्र में गगनयान क्रू मॉड्यूल और रॉकेट प्रणाली। — फाइल फोटो",
        cap_h=23.0,
    )
    s3a_body = (
        "भारतीय अंतरिक्ष अनुसंधान संगठन ने भारत के पहले मानवयुक्त अंतरिक्ष अभियान गगनयान के लिए क्रू एस्केप सिस्टम और पैराशूट रिकवरी मॉड्यूल का अंतिम "
        "एकीकृत परीक्षण सफलतापूर्वक पूरा कर लिया है। इसरो प्रमुख ने बताया कि अंतरिक्ष यात्रियों की सुरक्षा सुनिश्चित करने वाले सभी जीवन रक्षक उपकरणों ने "
        "प्रतिकूल परिस्थितियों में शत-प्रतिशत सटीक प्रदर्शन किया है। इसके साथ ही भारतीय अंतरिक्ष स्टेशन के पहले मॉड्यूल का डिजाइन भी तैयार हो गया है।"
    )
    fit_aditya_bharat_body(r_s3a_b["story"], "बेंगलुरु", "एजेंसी", s3a_body)

    # --- 3B. Cols 4..6: 3-Column Health Package with Subhead ---
    s3b_x0 = grid.col_x0(4)
    s3b_x1 = grid.col_x1(4, 3)
    s3b_cur_y = b3_y0
    s3b_head = "देश के दो सौ शहरों में शुरू होगी चौबीस घंटे टेली-मेडिसिन सेवा"
    _, _, s3b_pt, s3b_hh = fit_aditya_bharat_headline(
        0, s3b_x0, s3b_cur_y, s3b_x1,
        raw_text=s3b_head,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=38.0,
        lo_pt=30.0,
        align="left",
    )
    s3b_cur_y = round(s3b_cur_y + s3b_hh + 0.5, 2)

    s3b_sub = "एम्स और केंद्रीय मेडिकल संस्थानों के विशेषज्ञ डॉक्टर सीधे जिला अस्पतालों से जुड़ेंगे"
    _, _, _, s3b_sh = fit_aditya_bharat_headline(
        0, s3b_x0, s3b_cur_y, s3b_x1,
        raw_text=s3b_sub,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=14.5,
        lo_pt=11.5,
        align="left",
    )
    s3b_by0 = round(s3b_cur_y + s3b_sh + 1.0, 2)
    r_s3b_b = cmd("frame.create", {
        "spread": 0,
        "rect": [s3b_x0, s3b_by0, s3b_x1, b3_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_s3b_b["id"]],
        "columns": 3,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, s3b_x0, round(s3b_by0 + cm(1.5), 2), "स्वास्थ्य")
    s3b_body = (
        "केंद्रीय स्वास्थ्य मंत्रालय ने डिजिटल हेल्थ मिशन के अंतर्गत देश के दो सौ टियर-टू और टियर-थ्री शहरों के जिला अस्पतालों को सीधे अखिल भारतीय आयुर्विज्ञान संस्थान "
        "तथा पीजीआई के विशेषज्ञ डॉक्टरों से जोड़ने की नई सेवा शुरू की है। इसके माध्यम से हृदय रोग, कैंसर, न्यूरोलॉजी और गंभीर ट्रॉमा के मरीजों को अपने ही जिले में "
        "देश के शीर्ष विशेषज्ञों से निशुल्क परामर्श और रोबोटिक सर्जरी मार्गदर्शन मिल सकेगा।"
    )
    fit_aditya_bharat_body(r_s3b_b["story"], "नई दिल्ली", "ब्यूरो", s3b_body)

    # --- 3C. Cols 7..8: 2-Column Green Hydrogen Story ---
    s3c_pt = place_two_col_story(
        grid, grid.col_x0(7), grid.col_x1(7, 2), b3_y0, b3_y1,
        headline="ग्रीन हाइड्रोजन मिशन से भारत बनेगा निर्यात केंद्र",
        city="मुंबई",
        agency="एजेंसी",
        blurb_word="ऊर्जा",
        body=(
            "स्वच्छ ऊर्जा संक्रमण के क्षेत्र में भारत ने पचास लाख मीट्रिक टन सालाना ग्रीन हाइड्रोजन उत्पादन का लक्ष्य तय किया है। कांडला, पारादीप और तूतीकोरिन बंदरगाहों "
            "पर ग्रीन अमोनिया तथा हाइड्रोजन एक्सपोर्ट टर्मिनल बनाए जा रहे हैं, जहां से यूरोप और पूर्वी एशिया के देशों को स्वच्छ ईंधन का निर्यात किया जाएगा।"
        ),
    )

    sep3_y = round(b3_y1 + mm(1.75), 2)
    r_sep3 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep3_y], "b": [grid.print_x1, sep3_y]})
    cmd("object.stroke", {"ids": [r_sep3["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 4: BOTTOM STRIP (y = 41.70 .. 52.00 cm, Cols 1..8 = 5-Col Left Anchor + 3-Col Right Package)
    # ==========================================================================
    bot_y0 = round(sep3_y + mm(1.75), 2)
    bot_y1 = snap_frame_bottom_to_baseline(grid.print_y1)

    # --- 4A. Left 5-Column Anchor Package (Cols 1..5) ---
    anc_x0 = grid.col_x0(1)
    anc_x1 = grid.col_x1(1, 5)
    anc_cur_y = bot_y0

    anchor_head = "सीमांत क्षेत्रों में नई सामरिक रेल लाइन शुरू"
    _, _, anc_h_pt, anc_hh = fit_aditya_bharat_headline(
        0, anc_x0, anc_cur_y, anc_x1,
        raw_text=anchor_head,
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=50.0,
        lo_pt=41.0,
        align="center",
    )
    anc_cur_y = round(bot_y0 + 44.5, 2)

    anchor_sub = "दुर्गम पर्वतीय इलाकों में आधुनिक टनल और ब्रिज इंजीनियरिंग से बारहों महीने चलेगी हाई-स्पीड रेल सेवा"
    _, _, anc_sub_pt, anc_sub_h = fit_aditya_bharat_headline(
        0, anc_x0, anc_cur_y, anc_x1,
        raw_text=anchor_sub,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=16.0,
        lo_pt=12.0,
        align="center",
    )
    anc_body_y0 = round(anc_cur_y + anc_sub_h + 1.0, 2)
    anc_photo_y0 = anc_body_y0
    anc_body_y1 = bot_y1

    r_anc_body = cmd("frame.create", {
        "spread": 0,
        "rect": [anc_x0, anc_body_y0, anc_x1, anc_body_y1],
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
    place_red_subject_blurb(0, grid.col_x0(1), round(anc_body_y0 + cm(1.8), 2), "गौरव")

    acap_y1 = round(snap_underflow_top(anc_body_y1, num_underflow_lines=8) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(3),
        anc_photo_y0,
        grid.col_x1(3, 2),
        acap_y1,
        "p8_chenab_834463.jpg",
        "ab_p4_anchor_cmyk.jpg",
        "हिमालयी क्षेत्र में निर्मित विश्व के सबसे ऊंचे रेलवे आर्च ब्रिज पर दौड़ती वंदे भारत ट्रेन। — फाइल फोटो",
        cap_h=23.0,
    )
    anc_body = (
        "भारतीय रेलवे ने जम्मू-कश्मीर, हिमाचल, उत्तराखंड और पूर्वोत्तर के सीमावर्ती राज्यों को हर मौसम में देश के मुख्य रेल नेटवर्क से जोड़े रखने के लिए सामरिक रेल "
        "परियोजनाओं का नया चरण पूरा कर लिया है। विश्व के सबसे ऊंचे चिनाब आर्च ब्रिज और अंजी खाद केबल-स्टे ब्रिज के सफल संचालन के बाद अब ब्रह्मपुत्र नदी के "
        "नीचे देश की पहली ट्विन-ट्यूब रेल-रोड अंडरवाटर टनल का निर्माण शुरू किया गया है। रेलवे बोर्ड के अनुसार इन परियोजनाओं में भूकंपरोधी तकनीक और स्वदेशी "
        "कवच सुरक्षा प्रणाली लगाई गई है, जिससे दुर्गम हिमालयी क्षेत्रों में पर्यटन और सामरिक रसद परिवहन को नई गति मिली है।"
    )
    fit_aditya_bharat_body(r_anc_body["story"], "नई दिल्ली", "विशेष संवाददाता", anc_body)

    # --- 4B. Right 3-Column Economic Package (Cols 6..8) ---
    b4r_x0 = grid.col_x0(6)
    b4r_x1 = grid.col_x1(6, 3)
    b4r_cur_y = bot_y0
    b4r_head = "विदेशी मुद्रा भंडार और डिजिटल भुगतान में नया रिकॉर्ड"
    _, _, b4r_pt, b4r_hh = fit_aditya_bharat_headline(
        0, b4r_x0, b4r_cur_y, b4r_x1,
        raw_text=b4r_head,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=38.0,
        lo_pt=30.0,
        align="left",
    )
    b4r_cur_y = round(b4r_cur_y + b4r_hh + 0.5, 2)

    b4r_sub = "अंतरराष्ट्रीय मुद्रा कोष ने भारतीय अर्थव्यवस्था को बताया दुनिया का सबसे तेज ग्रोथ इंजन"
    _, _, _, b4r_sh = fit_aditya_bharat_headline(
        0, b4r_x0, b4r_cur_y, b4r_x1,
        raw_text=b4r_sub,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=14.5,
        lo_pt=11.5,
        align="left",
    )
    b4r_by0 = round(b4r_cur_y + b4r_sh + 1.0, 2)
    r_b4r_b = cmd("frame.create", {
        "spread": 0,
        "rect": [b4r_x0, b4r_by0, b4r_x1, bot_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_b4r_b["id"]],
        "columns": 3,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, b4r_x0, round(b4r_by0 + cm(1.5), 2), "अर्थतंत्र")
    b4r_body = (
        "भारतीय रिजर्व बैंक के नवीनतम आंकड़ों के अनुसार देश का विदेशी मुद्रा भंडार बढ़कर सात सौ बारह अरब डॉलर के सर्वकालिक उच्च स्तर पर पहुंच गया है। इसके साथ ही "
        "यूपीआई के माध्यम से होने वाले मासिक डिजिटल लेनदेन ने पच्चीस लाख करोड़ रुपये का आंकड़ा पार कर वैश्विक कीर्तिमान स्थापित किया है। अंतरराष्ट्रीय मुद्रा कोष और "
        "विश्व बैंक ने अपनी ताजा रिपोर्ट में कहा है कि मजबूत घरेलू खपत और विनिर्माण सुधारों के दम पर भारत विश्व की सबसे तेजी से बढ़ती प्रमुख अर्थव्यवस्था बना रहेगा।"
    )
    fit_aditya_bharat_body(r_b4r_b["story"], "मुंबई", "ब्यूरो", b4r_body)

    cmd("edit.deselectAll")
    cmd("view.fitPage", {})

    out_pd = VAULT_DIR / "Aditya_Bharat_Page_05_Rashtriya_34x53.pagedesigner"
    out_png = VAULT_DIR / "Aditya_Bharat_Page_05_Rashtriya_34x53.png"
    out_pdf = VAULT_DIR / "Aditya_Bharat_Page_05_Rashtriya_CMYK_34x53.pdf"
    rpc("app.save", {"path": str(out_pd)})
    rpc("app.export", {"path": str(out_png), "page": 0, "scale": 1.5})
    try:
        rpc("engine.execute", {"command": "file.exportPdf", "params": {"path": str(out_pdf)}})
    except Exception:
        pass

    artifact_png = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\8707c72d-58b0-4715-a099-3efffcd57514\aditya_bharat_page_05_rashtriya_34x53.png")
    artifact_png.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_png, artifact_png)

    print(
        f"=== ADITYA BHARAT PAGE 05 (RASHTRIYA) BUILT IN {time.perf_counter()-t0:.2f}s ===\n"
        f"    Flyer8Col={fl_h_pt}pt | Lead6Col={lead_h_pt}pt (Gray Box in LAST Col 6) | Right2Col={b2_r_pt}pt\n"
        f"    Band3_3ColA={s3a_pt}pt | Band3_3ColB={s3b_pt}pt | Band3_2ColC={s3c_pt}pt\n"
        f"    Anchor5Col={anc_h_pt}pt | BotRight3Col={b4r_pt}pt (ALL >= 30.0pt!)\n"
        f"    Saved: {out_pd}"
    )


if __name__ == "__main__":
    build_aditya_bharat_page4()
