# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — PAGE 02 ('महानगर') MASTER BROADSHEET BUILDER (34x53 cm | Print Area 32x51 cm)
=============================================================================================================
Strictly implements the official 'Aditya Bharat' Stylesheet & Inside Page 02 Architecture:
  1. Page Size & Grid   : 34.0 cm x 53.0 cm (1-1-1-1 cm outer margins -> Fixed Print Area = 32.0 cm x 51.0 cm, 8 Cols, 4.0 mm Gutter)
  2. Inside Masthead    : 1.5 cm Height (y = 1.0 .. 2.5 cm, Cols 1..8):
       - Left           : Red Color Box ('FlyerCrimson') with Page Name 'महानगर' in 20.0 pt 'DB Hindi 6' White ('[Paper]')
       - Center         : Official 'आदित्य भारत' Masthead Logo centered
       - Right          : Dateline in 16.0 pt ('DB Hindi' Bold) + Page Number '02' in 18.0 pt 'Times New Roman' Bold
       - Bottom Rule    : 2.0 pt Rule in 60% Gray across all 8 columns
  3. Interlocked 4-Band Variety Layout (Kasa Hua Page — Zero White Space, Zero Empty Box Space):
       - Band 1 (11.8cm): 8-Column Top Flyer (18pt Subhead above + 1-Line DB Rasrand Bold Headline + 6 Cols Text + Center 2-Col Photo in Cols 4..5 + 4-Line Underflow)
       - Band 2 (16.8cm): 5-Column Main Lead (Cols 1..5: 2-Line DB Rasrand Bold Headline + Subhead + Center Photo in Cols 3..4 + Caption + 100% Filled Box with 2.5mm inset + 4-Line Underflow)
                          + 3-Column Feature Story with Photo (Cols 6..8: 2-Line Headline + Photo in Cols 7..8 + Caption + 4-Line Underflow)
       - Band 3 (8.9 cm): Left 2-Column Story (Cols 1..2) + Center 4-Column Package (Cols 3..6: 1-Line Headline + Subhead + 4-Col Body) + Right 2-Column Story (Cols 7..8)
       - Band 4 (10.3cm): Bottom-Left 2-Column Story (Cols 1..2) + Bottom-Right 6-Column Anchor Package (Cols 3..8: 45-50pt DB Rasrand Bold Headline + Subhead + Photo in Cols 5..6 + 3-Line Underflow)
  4. Typography & Prepress:
       - All Headlines, Box Headlines & Subheads in 100% K Black ('[Black]') — NO Red Headlines or Red Subheads anywhere!
       - Body Text      : 'DB Hindi' Regular, 11.0 pt / 11.25 pt Leading, Baseline Grid Locked ('allLines'), 100% K Black
       - Captions       : 'DB Hindi 7' Bold, 10.0 pt / 10.2 pt Leading, 100% K Black
       - 3-Tone Byline  : City (100% Black) | Pipe (Red) | Agency (60% Gray) + Gray Rule Below
       - Red Blurb Tag  : 1-Word Subject in 'DB Hindi 6' 22.0 pt White on Red + 3.0 pt Gray Rule Below
       - All Photos     : Smart-cropped & saved in CMYK (300 DPI)
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
        Path(r"E:\RND\HINDI - TEST\Page_Designer_App\saved_pages\photos"),
        Path(r"E:\RND\HINDI - TEST\photos"),
        Path(r"E:\RND\Gujarat_Samachar\editions\19_Oct_2026\photos"),
        Path(r"E:\RND\Gujarat_Samachar_Edition\editions\19_Oct_2026\photos"),
        PHOTOS_DIR,
    ]:
        cand = base / src_name
        if cand.exists():
            src_p = cand
            break
    if src_p is None:
        # Fallback to any available photo in PHOTOS_DIR
        fallbacks = list(PHOTOS_DIR.glob("*.jpg"))
        if fallbacks:
            src_p = fallbacks[0]
        else:
            raise FileNotFoundError(f"Could not find photo {src_name}")

    target_w_px = max(600, int(round(box_w_pt * 300.0 / 72.0)))
    target_h_px = max(400, int(round(box_h_pt * 300.0 / 72.0)))
    with Image.open(src_p) as im:
        im_rgb = im.convert("RGB")
        cropped = ImageOps.fit(im_rgb, (target_w_px, target_h_px), method=Image.Resampling.LANCZOS, centering=(0.5, 0.38))
        cmyk_im = cropped.convert("CMYK")
        cmyk_im.save(dst_p, "JPEG", quality=95, dpi=(300, 300))
    return dst_p


class AdityaBharatPage2Grid:
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

        # Zone 1: 1.5 cm Inside Masthead (y = 1.0 .. 2.5 cm)
        self.masthead_h_cm = 1.5
        self.masthead_y0 = self.print_y0
        self.masthead_y1 = round(self.masthead_y0 + cm(self.masthead_h_cm), 2)

        # Band 1: Top 8-Column Flyer (y = 2.85 .. 14.65 cm, Height = 11.8 cm)
        self.flyer_y0 = round(self.masthead_y1 + mm(3.5), 2)
        self.flyer_h_cm = 11.8
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
    lo_pt: float = 30.0,
    fixed_pt: float = None,
    align: str = "left",
    leading_add_pt: float = 1.0,
):
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

    def max_pt_for_line(line_str: str, h_scale: float = 1.0) -> float:
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
                "hScale": h_scale,
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
        search_lo = min(lo_pt, 15.0)
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

    def stretch_line(byte_a: int, byte_b: int, max_total_lines: int, min_scale_pct: int = 86):
        lo_s, hi_s = min_scale_pct, 114
        best_s = min_scale_pct
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
        # Do not over-stretch short lines beyond 108% unless needed, and never shrink below 100% if 100% already fits!
        if best_s > 108:
            st_100 = batch([
                {"command": "text.select", "params": {"story": sid, "anchor": byte_a, "focus": byte_b}},
                {"command": "type.char", "params": {"attrs": {"hScale": 1.0}}},
                {"command": "story.get", "params": {"story": sid}},
            ])[-1]
            if (st_100.get("lines") or 0) <= max_total_lines and st_100.get("overset") is None:
                best_s = min(best_s, 106)
        batch([
            {"command": "text.select", "params": {"story": sid, "anchor": byte_a, "focus": byte_b}},
            {"command": "type.char", "params": {"attrs": {"hScale": round(best_s / 100.0, 3)}}},
        ])

    words = clean_text.split(" ")
    n = len(words)
    if target_lines <= 1 or n < 2:
        effective_lo = lo_pt if font_family != "DB Rasrand Bold" else max(lo_pt, 28.0)
        raw_pt = max_pt_for_line(clean_text, h_scale=1.0)
        init_hscale = 1.0
        if raw_pt >= effective_lo:
            best_pt = min(hi_pt, raw_pt)
        else:
            # Try condensed headline width (hScale=0.88) so long 1-line headlines never wrap onto a 2nd orphan line!
            cond_pt = max_pt_for_line(clean_text, h_scale=0.88)
            best_pt = min(hi_pt, cond_pt)
            init_hscale = 0.88
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
                "hScale": init_hscale,
                "tracking": 0.0,
            }}},
            {"command": "type.para", "params": {"attrs": {"align": align, "hyphenate": False}}},
        ])
        stretch_line(0, 99999, 1, min_scale_pct=86 if init_hscale < 1.0 else 96)
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
        effective_lo = lo_pt if font_family != "DB Rasrand Bold" else max(lo_pt, 28.0)
        best_raw_min = effective_lo
        if fixed_pt is None:
            # Evaluate top 6 most balanced character-length splits
            for _, l1, l2 in candidates[:6]:
                pt1 = max_pt_for_line(l1, h_scale=1.0)
                pt2 = max_pt_for_line(l2, h_scale=1.0)
                raw_min = min(pt1, pt2, hi_pt)
                score = raw_min - 0.45 * abs(pt1 - pt2)
                if score > best_score:
                    best_score = score
                    best_raw_min = raw_min
                    best_split = (l1, l2)
            l1_str, l2_str = best_split
            init_hscale = 1.0
            if best_raw_min >= effective_lo:
                best_pt = best_raw_min
            else:
                # Use condensed hScale=0.88 and strictly fit within 1 line per half so it NEVER breaks onto a 3rd line!
                cpt1 = max_pt_for_line(l1_str, h_scale=0.88)
                cpt2 = max_pt_for_line(l2_str, h_scale=0.88)
                best_pt = min(cpt1, cpt2, hi_pt)
                init_hscale = 0.88
        else:
            best_pt = fixed_pt
            l1_str, l2_str = best_split
            init_hscale = 1.0

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
                "hScale": init_hscale,
                "tracking": 0.0,
            }}},
            {"command": "type.para", "params": {"attrs": {"align": align, "hyphenate": False}}},
        ])
        min_sc = 86 if init_hscale < 1.0 else 96
        stretch_line(0, l1_bytes, 2, min_scale_pct=min_sc)
        stretch_line(l1_bytes + 1, total_bytes, 2, min_scale_pct=min_sc)
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


def place_red_subject_blurb(spread_idx: int, x0: float, y0: float, word_text: str):
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
    "\nकेंद्र और राज्य सरकारों के समन्वय से इस महानगर विकास योजना को निर्धारित समय-सीमा के भीतर पूरा करने का लक्ष्य रखा गया है। "
    "शहरी विकास विभाग के वरिष्ठ अधिकारियों के अनुसार आधुनिक तकनीक और डिजिटल निगरानी प्रणाली के माध्यम से प्रत्येक चरण की प्रगति की समीक्षा की जा रही है। "
    "शहरी योजनाकारों और विशेषज्ञों का मानना है कि इस ऐतिहासिक पहल से महानगर के लाखों नागरिकों को सीधा लाभ मिलेगा और सुगम आवागमन के नए अवसर सृजित होंगे। "
    "स्थानीय प्रशासन और नगर निगम को भी निर्देश दिए गए हैं कि आम नागरिकों को सभी नागरिक सेवाएं पारदर्शी और त्वरित रूप से उपलब्ध कराई जाएं।"
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
        "\n• प्रत्येक वार्ड में चौबीस घंटे डिजिटल टेली-मेडिसिन और निशुल्क दवा वितरण केंद्र सक्रिय।"
        "\n• गंभीर मरीजों के लिए एयर एंबुलेंस और ग्रीन कॉरिडोर की विशेष आपातकालीन व्यवस्था।"
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


def place_two_col_story(
    grid: AdityaBharatPage2Grid,
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
        hi_pt=30.0,
        lo_pt=22.0,
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
        place_red_subject_blurb(0, x0, round(by0 + cm(2.2), 2), blurb_word)
    fit_aditya_bharat_body(r_b["story"], city, agency, body)


def build_aditya_bharat_page2():
    t0 = time.perf_counter()
    connect_page_designer()
    grid = AdityaBharatPage2Grid()

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
            "title": "आदित्य भारत — पेज 02 महानगर (34x53 सेमी | प्रिंट एरिया 32x51 सेमी)",
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
    #   - Left   : Red Color Box ('FlyerCrimson') with Page Name 'महानगर' in 20 pt 'DB Hindi 6' White ('[Paper]')
    #   - Center : Official 'आदित्य भारत' Masthead Logo centered
    #   - Right  : Dateline in 16 pt ('DB Hindi' Bold) + Page Number '02' in 18 pt 'Times New Roman' Bold
    #   - Bottom : 2.0 pt Rule in 60% Gray across all 8 columns
    # ==========================================================================
    mh_x0, mh_y0, mh_x1, mh_y1 = grid.print_x0, grid.masthead_y0, grid.print_x1, grid.masthead_y1

    # 1A. Left Red Box with Page Name ('महानगर') in 20 pt DB Hindi 6 White
    sec_w = cm(4.2)
    sec_y0 = round(mh_y0 + mm(1.0), 2)
    sec_y1 = round(mh_y1 - mm(1.8), 2)
    r_mh_sec = cmd("frame.create", {
        "spread": 0,
        "rect": [mh_x0, sec_y0, round(mh_x0 + sec_w, 2), sec_y1],
        "content": "text",
        "text": "महानगर",
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

    # 1B. Center Masthead Logo ('आदित्य भारत')
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

    # 1C. Right Page Number ('02') in 18 pt Times New Roman Bold
    pnum_w = cm(1.4)
    pnum_x0 = round(mh_x1 - pnum_w, 2)
    r_mh_pnum = cmd("frame.create", {
        "spread": 0,
        "rect": [pnum_x0, sec_y0, mh_x1, sec_y1],
        "content": "text",
        "text": "02",
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

    # 1D. Right Dateline in 16 pt DB Hindi Bold (to the left of Page Number '02')
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
        {"command": "text.select", "params": {"story": r_mh_dt["story"], "anchor": 0, "focus": 999}},
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

    # 1E. Bottom 2.0 pt Rule in 60% Gray across all 8 columns
    r_mh_rule = cmd("line.create", {"spread": 0, "a": [mh_x0, mh_y1], "b": [mh_x1, mh_y1]})
    cmd("object.stroke", {"ids": [r_mh_rule["id"]], "swatch": "[Black]", "weight": 2.0, "tint": 0.60})

    # ==========================================================================
    # BAND 1: TOP 8-COLUMN FLYER PACKAGE (y = 2.85 .. 14.65 cm, Height = 11.8 cm)
    # ==========================================================================
    fl_x0, fl_y0, fl_x1, fl_y1 = grid.print_x0, grid.flyer_y0, grid.print_x1, snap_frame_bottom_to_baseline(grid.flyer_y1)
    cur_y = fl_y0

    flyer_sub = "पैंतालीस हजार करोड़ की परियोजना को मिली हरी झंडी : चौबीस महीने में पूरा होगा छह सिग्नल-फ्री कॉरिडोर का निर्माण"
    _, _, _, fl_sub_h = fit_aditya_bharat_headline(
        0, fl_x0, cur_y, fl_x1,
        raw_text=flyer_sub,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=18.0,
        lo_pt=18.0,
        align="center",
        fixed_pt=18.0,
    )
    cur_y = round(cur_y + fl_sub_h + 1.5, 2)

    flyer_head = "महानगर में बनेंगे नए छह एलिवेटेड कॉरिडोर"
    _, _, fl_h_pt, fl_hh = fit_aditya_bharat_headline(
        0, fl_x0, cur_y, fl_x1,
        raw_text=flyer_head,
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=66.0,
        lo_pt=52.0,
        align="center",
    )
    cur_y = round(cur_y + fl_hh + 3.0, 2)

    fl_body_y0 = cur_y
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

    fcap_y1 = round(snap_underflow_top(fl_body_y1, num_underflow_lines=4) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(4),
        fl_body_y0,
        grid.col_x1(4, 2),
        fcap_y1,
        "p2_flyover_823231.jpg",
        "ab_p2_flyer_cmyk.jpg",
        "महानगर के व्यस्त चौराहों को जोड़ने वाले छह-लेन सिग्नल-फ्री एलिवेटेड कॉरिडोर का मॉडल। — फाइल फोटो",
        cap_h=23.0,
    )
    place_red_subject_blurb(0, grid.col_x0(1), round(fl_body_y0 + cm(2.6), 2), "सौगात")

    fl_body = (
        "महानगर के करोड़ों नागरिकों को रोजाना लगने वाले ट्रैफिक जाम से स्थायी राहत दिलाने के लिए लोक निर्माण विभाग और राष्ट्रीय राजमार्ग प्राधिकरण ने "
        "पैंतालीस हजार करोड़ रुपये की महायोजना तैयार की है। इस परियोजना के अंतर्गत रिंग रोड, आउटर रिंग रोड और अंतरराष्ट्रीय हवाई अड्डे को जोड़ने वाले "
        "छह प्रमुख मार्गों पर डबल-डेकर एलिवेटेड फ्लाईओवर बनाए जाएंगे। "
        "शहरी विकास मंत्रालय के वरिष्ठ अधिकारियों ने बताया कि इन सभी एलिवेटेड कॉरिडोर के ऊपर मेट्रो लाइन और नीचे छह लेन का हाई-स्पीड एक्सप्रेसवे "
        "संचालित होगा। इससे पूर्व से पश्चिम और उत्तर से दक्षिण महानगर की यात्रा करने वाले वाहन चालकों का यात्रा समय साठ मिनट से घटकर मात्र बीस मिनट रह जाएगा। "
        "परियोजना के प्रथम चरण में तीन प्रमुख कॉरिडोर का निर्माण कार्य आगामी माह से शुरू किया जाएगा। निर्माण के दौरान पर्यावरण संरक्षण का विशेष ध्यान रखते हुए "
        "प्री-कास्ट सेगमेंट तकनीक का उपयोग किया जाएगा ताकि सड़कों पर धूल प्रदूषण न हो और आम यातायात भी बाधित न हो। "
        "विशेषज्ञों के अनुसार इन छह नए कॉरिडोर के चालू होने से प्रतिदिन पंद्रह लाख लीटर ईंधन की बचत होगी और महानगर के प्रदूषण स्तर में पच्चीस प्रतिशत तक की "
        "गिरावट दर्ज की जाएगी। प्रत्येक कॉरिडोर पर इंटेलिजेंट ट्रैफिक मैनेजमेंट सिस्टम, ऑटोमैटिक स्पीड कैमरे, सोलर लाइटिंग और रेनवाटर हार्वेस्टिंग संयंत्र लगाए जाएंगे।"
    )
    fit_aditya_bharat_body(r_fl_body["story"], "इंदौर", "ब्यूरो", fl_body)

    sep1_y = round(fl_y1 + mm(1.75), 2)
    r_sep1 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep1_y], "b": [grid.print_x1, sep1_y]})
    cmd("object.stroke", {"ids": [r_sep1["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # BAND 2: UPPER-MIDDLE BAND (Height = 16.8 cm)
    #   - Left Cols 1..5 (5 Columns) : Main Mahanagar Lead Story (with Photo in Cols 3..4 + 100% Filled Box + 4-Line Underflow)
    #   - Right Cols 6..8 (3 Columns): 3-Column Feature Story with Photo (Cols 7..8 Photo + 4-Line Underflow)
    # ==========================================================================
    b2_y0 = round(sep1_y + mm(1.75), 2)
    b2_y1 = snap_frame_bottom_to_baseline(round(b2_y0 + cm(16.8), 2))

    # --- 2A. Left 5-Column Main Lead Story (Cols 1..5) ---
    lead_x0 = grid.col_x0(1)
    lead_x1 = grid.col_x1(1, 5)
    lead_cur_y = b2_y0

    lead_head = "सरकारी अस्पतालों में मिलेंगी रोबोटिक सर्जरी और निशुल्क जांच सुविधाएं"
    _, _, lead_h_pt, lead_hh = fit_aditya_bharat_headline(
        0, lead_x0, lead_cur_y, lead_x1,
        raw_text=lead_head,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=50.0,
        lo_pt=38.0,
        align="left",
    )
    lead_cur_y = round(lead_cur_y + lead_hh + 1.0, 2)

    lead_sub = "पांच हजार नए आईसीयू बेड और चौबीस घंटे सुपर-स्पेशियलिटी ट्रॉमा सेंटर शुरू : डिजिटल हेल्थ ग्रिड से जुड़े सभी अस्पताल"
    _, _, _, lead_sub_h = fit_aditya_bharat_headline(
        0, lead_x0, lead_cur_y, lead_x1,
        raw_text=lead_sub,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=17.0,
        lo_pt=12.5,
        align="left",
    )
    lead_cur_y = round(lead_cur_y + lead_sub_h + 3.0, 2)

    lead_body_y0 = lead_cur_y
    lead_body_y1 = b2_y1

    r_lead_body = cmd("frame.create", {
        "spread": 0,
        "rect": [lead_x0, lead_body_y0, lead_x1, lead_body_y1],
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

    lpx0 = grid.col_x0(3)
    lpx1 = grid.col_x1(3, 2)
    lpy0 = lead_body_y0

    spec_box_y1 = round(snap_underflow_top(lead_body_y1, num_underflow_lines=4) - 3.0, 2)
    spec_box_h = cm(4.78)
    spec_box_y0 = round(spec_box_y1 - spec_box_h, 2)
    lcap_y1 = round(spec_box_y0 - 4.0, 2)

    place_photo_and_caption_cmyk(
        0, lpx0, lpy0, lpx1, lcap_y1,
        "p2_hospital_823061.jpg",
        "ab_p2_lead_cmyk.jpg",
        "महानगर के नए सुपर-स्पेशियलिटी अस्पताल परिसर में स्थापित अत्याधुनिक चिकित्सा इकाई। — फाइल फोटो",
        cap_h=23.0,
    )

    inset_2_5mm = mm(2.5)
    r_spec_box = cmd("frame.create", {
        "spread": 0,
        "rect": [lpx0, spec_box_y0, lpx1, spec_box_y1],
        "content": "text",
        "text": "",
    })
    spec_body = (
        "• सभी सरकारी अस्पतालों में एमआरआई, सीटी स्कैन और तीन सौ प्रकार की पैथोलॉजी जांच पूरी तरह निशुल्क।\n"
        "• ओपीडी में लंबी कतारों से मुक्ति के लिए क्यूआर कोड आधारित ऑनलाइन अपॉइंटमेंट और ई-पर्ची प्रणाली।\n"
        "• हृदय, कैंसर और किडनी ट्रांसप्लांट के मरीजों के लिए पांच लाख रुपये तक की तत्काल कैशलेस सहायता।\n"
        "• प्रत्येक जोन में चौबीस घंटे पचास नई एडवांस लाइफ सपोर्ट एंबुलेंस और मोबाइल क्लिनिक तैनात।"
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
    fit_box_completely(r_spec_box["story"], "स्वास्थ्य मिशन : मरीजों को तुरंत राहत", spec_body, head_pt=16.0, head_align="left", body_pt=10.5, body_lead=11.3, para_space=2.2)

    place_red_subject_blurb(0, grid.col_x0(1), round(lead_body_y0 + cm(3.0), 2), "राहत")

    lead_body = (
        "महानगर के आम नागरिकों को निजी अस्पतालों के महंगे इलाज से राहत दिलाने के लिए स्वास्थ्य विभाग ने सार्वजनिक चिकित्सा ढांचे में बड़ा बदलाव "
        "किया है। आगामी माह से राजधानी और प्रमुख महानगरों के पच्चीस बड़े सरकारी अस्पतालों में अत्याधुनिक रोबोटिक सर्जरी, डिजिटल कैथ लैब और ऑर्गन "
        "ट्रांसप्लांट यूनिट पूरी तरह निशुल्क शुरू की जा रही हैं। "
        "स्वास्थ्य सचिव ने बताया कि इन अस्पतालों में पांच हजार नए वेंटिलेटर युक्त आईसीयू बेड जोड़े गए हैं और प्रत्येक अस्पताल को केंद्रीयकृत डिजिटल "
        "हेल्थ ग्रिड से जोड़ा गया है। इससे मरीज किसी भी सरकारी अस्पताल या मोहल्ला क्लिनिक में अपने हेल्थ कार्ड के माध्यम से पुरानी जांच रिपोर्ट और दवाइयों "
        "का विवरण तुरंत प्राप्त कर सकेंगे। "
        "आपातकालीन मरीजों को गोल्डन आवर के भीतर उपचार उपलब्ध कराने के लिए प्रमुख राजमार्गों और घनी आबादी वाले इलाकों के पास दस नए चौबीस घंटे सक्रिय "
        "सुपर-स्पेशियलिटी ट्रॉमा सेंटर स्थापित किए गए हैं। इसके साथ ही वरिष्ठ नागरिकों और गर्भवती महिलाओं के लिए घर बैठे सैंपल कलेक्शन और निशुल्क दवा "
        "वितरण की सुविधा भी शुरू की गई है।"
    )
    fit_aditya_bharat_body(r_lead_body["story"], "भोपाल", "ब्यूरो", lead_body)

    # --- 2B. Right 3-Column Feature Story with Photo (Cols 6..8) ---
    s3_x0 = grid.col_x0(6)
    s3_x1 = grid.col_x1(6, 3)
    s3_cur_y = b2_y0

    s3_head = "रिवरफ्रंट और हरित पार्क कॉरिडोर से संवरेगा महानगर का स्वरूप"
    _, _, s3_h_pt, s3_hh = fit_aditya_bharat_headline(
        0, s3_x0, s3_cur_y, s3_x1,
        raw_text=s3_head,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=38.0,
        lo_pt=28.0,
        align="left",
    )
    s3_body_y0 = round(s3_cur_y + s3_hh + 2.5, 2)
    s3_body_y1 = b2_y1

    r_s3_body = cmd("frame.create", {
        "spread": 0,
        "rect": [s3_x0, s3_body_y0, s3_x1, s3_body_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_s3_body["id"]],
        "columns": 3,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })

    s3_cap_y1 = round(snap_underflow_top(s3_body_y1, num_underflow_lines=4) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(7),
        s3_body_y0,
        grid.col_x1(7, 2),
        s3_cap_y1,
        "p2_clean_823430.jpg",
        "ab_p2_riverfront_cmyk.jpg",
        "महानगर में विकसित किए गए आधुनिक हरित पथ और स्वच्छता अभियान का दृश्य। — फाइल फोटो",
        cap_h=23.0,
    )

    s3_body = (
        "नदी के दोनों किनारों पर बाईस किलोमीटर लंबा इको-फ्रेंडली रिवरफ्रंट और सौ नए हरित पार्क विकसित किए जा रहे हैं। महानगर के पर्यावरण को स्वच्छ "
        "और सुंदर बनाने के लिए नगर निगम व विकास प्राधिकरण ने नदी संरक्षण तथा हरित कॉरिडोर परियोजना का दूसरा चरण शुरू कर दिया है। इस योजना के तहत नदी "
        "में गिरने वाले सभी नालों को बारह नए सीवेज ट्रीटमेंट प्लांट से जोड़ा गया है ताकि केवल शुद्ध जल ही नदी में प्रवाहित हो। "
        "दोनों किनारों पर पैदल ट्रैक, साइकिल लेन, ओपन एम्फीथिएटर और औषधीय पौधों के उद्यान बनाए जा रहे हैं। इसके अतिरिक्त महानगर के सभी वार्डों में "
        "जीरो-वेस्ट मॉडल लागू कर गीले और सूखे कचरे से हरित ऊर्जा बनाने के संयंत्र स्थापित किए गए हैं, जिससे शहर की स्वच्छता रैंकिंग में बड़ा सुधार हुआ है।"
    )
    fit_aditya_bharat_body(r_s3_body["story"], "अहमदाबाद", "ब्यूरो", s3_body)

    sep2_y = round(b2_y1 + mm(1.75), 2)
    r_sep2 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep2_y], "b": [grid.print_x1, sep2_y]})
    cmd("object.stroke", {"ids": [r_sep2["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # BAND 3: LOWER-MIDDLE BAND (Height = 8.9 cm, Cols 1..8 = 2 + 4 + 2)
    # ==========================================================================
    b3_y0 = round(sep2_y + mm(1.75), 2)
    b3_y1 = snap_frame_bottom_to_baseline(round(b3_y0 + cm(8.9), 2))

    # --- 3A. Left 2-Column Story (Cols 1..2) ---
    place_two_col_story(
        grid, grid.col_x0(1), grid.col_x1(1, 2), b3_y0, b3_y1,
        headline="पांच सौ सरकारी स्कूलों में खुलेंगी रोबोटिक्स लैब",
        city="इंदौर",
        agency="संवाददाता",
        blurb_word="शिक्षा",
        body=(
            "नई शिक्षा नीति के तहत महानगर के पांच सौ सरकारी स्कूलों को मॉडल स्कूल के रूप में अपग्रेड किया जा रहा है। इन विद्यालयों में कक्षा छठी से ही "
            "छात्रों को रोबोटिक्स, थ्री-डी प्रिंटिंग, कोडिंग, डेटा साइंस और अंतरिक्ष विज्ञान का व्यावहारिक प्रशिक्षण दिया जाएगा। शिक्षा विभाग ने इसके "
            "लिए आईआईटी के विशेषज्ञों के साथ समझौता किया है और दो हजार शिक्षकों का विशेष प्रशिक्षण भी पूरा कर लिया गया है।"
        ),
    )

    # --- 3B. Center 4-Column Story Package (Cols 3..6) ---
    c4_x0 = grid.col_x0(3)
    c4_x1 = grid.col_x1(3, 4)
    c4_cur_y = b3_y0

    c4_head = "हर कॉलोनी में चौबीस घंटे मिलेगा स्वच्छ पेयजल"
    _, _, c4_h_pt, c4_hh = fit_aditya_bharat_headline(
        0, c4_x0, c4_cur_y, c4_x1,
        raw_text=c4_head,
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=42.0,
        lo_pt=28.0,
        align="center",
    )
    c4_cur_y = round(c4_cur_y + c4_hh + 1.0, 2)

    c4_sub = "तीन हजार किलोमीटर नई पाइपलाइन और स्मार्ट वाटर मीटर लगाने का कार्य शुरू : जल बोर्ड ने जारी किया एक्शन प्लान"
    _, _, _, c4_sub_h = fit_aditya_bharat_headline(
        0, c4_x0, c4_cur_y, c4_x1,
        raw_text=c4_sub,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=15.5,
        lo_pt=12.0,
        align="center",
    )
    c4_body_y0 = round(c4_cur_y + c4_sub_h + 2.5, 2)

    r_c4_body = cmd("frame.create", {
        "spread": 0,
        "rect": [c4_x0, c4_body_y0, c4_x1, b3_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_c4_body["id"]],
        "columns": 4,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, c4_x0, round(c4_body_y0 + cm(1.8), 2), "योजना")
    c4_body = (
        "पेयजल संकट को जड़ से समाप्त करने के लिए जल बोर्ड ने आठ हजार करोड़ की नई महायोजना शुरू की है। महानगर की बाहरी कॉलोनियों और नव-विकसित "
        "आवासीय सेक्टरों में गर्मियों के दौरान होने वाली पेयजल किल्लत को दूर करने के लिए तीन हजार किलोमीटर लंबी नई डक्टाइल आयरन पाइपलाइन बिछाई जा रही है। "
        "इसके साथ ही चार नए वाटर ट्रीटमेंट प्लांट और पचास उच्च क्षमता वाले भूमिगत जलाशयों का निर्माण किया जा रहा है। "
        "जल बोर्ड के मुख्य अभियंता के अनुसार स्काडा तकनीक से लैस स्मार्ट कंट्रोल रूम के माध्यम से पानी के प्रेशर और लीकेज की रियल-टाइम निगरानी की जाएगी, "
        "जिससे चालीस प्रतिशत बर्बाद होने वाले पानी की बचत होगी और हर घर को निर्बाध रूप से शुद्ध पेयजल उपलब्ध होगा।"
    )
    fit_aditya_bharat_body(r_c4_body["story"], "रायपुर", "ब्यूरो", c4_body)

    # --- 3C. Right 2-Column Story (Cols 7..8) ---
    place_two_col_story(
        grid, grid.col_x0(7), grid.col_x1(7, 2), b3_y0, b3_y1,
        headline="प्रमुख बाजारों में बनेंगे स्मार्ट पार्किंग कॉम्प्लेक्स",
        city="भोपाल",
        agency="एजेंसी",
        blurb_word="",
        body=(
            "महानगर के प्रमुख व्यावसायिक केंद्रों और भीड़भाड़ वाले बाजारों में खरीदारों की सुविधा के लिए नगर निगम पचास नए ऑटोमेटेड मल्टी-लेवल कार पार्किंग "
            "कॉम्प्लेक्स तैयार कर रहा है। इनमें एक साथ पच्चीस हजार से अधिक चारपहिया और दोपहिया वाहन खड़े किए जा सकेंगे। नागरिक मोबाइल ऐप के माध्यम से घर "
            "से निकलने से पहले ही पार्किंग स्लॉट बुक कर सकेंगे और फास्टैग से स्वतः शुल्क कटौती की सुविधा मिलेगी।"
        ),
    )

    sep3_y = round(b3_y1 + mm(1.75), 2)
    r_sep3 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep3_y], "b": [grid.print_x1, sep3_y]})
    cmd("object.stroke", {"ids": [r_sep3["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # BAND 4: BOTTOM ANCHOR BAND (Cols 1..2 Two-Col Story + Cols 3..8 Six-Col Anchor Package)
    # ==========================================================================
    bot_y0 = round(sep3_y + mm(1.75), 2)
    bot_y1 = snap_frame_bottom_to_baseline(grid.print_y1)

    place_two_col_story(
        grid, grid.col_x0(1), grid.col_x1(1, 2), bot_y0, bot_y1,
        headline="धरोहर कॉरिडोर से पर्यटन को मिली रफ्तार",
        city="रायपुर",
        agency="एजेंसी",
        blurb_word="धरोहर",
        body=(
            "विरासत संरक्षण योजना के तहत महानगर के ऐतिहासिक स्मारकों, राजवाड़ा परिसरों और प्राचीन मंदिर मार्गों को हेरिटेज वॉक कॉरिडोर के रूप में विकसित "
            "किया गया है। आकर्षक फसाड लाइटिंग, लोक कला वीथिका और हस्तशिल्प बाजार खुलने से स्थानीय कलाकारों को रोजगार के नए अवसर मिले हैं। पर्यटन विभाग ने "
            "विदेशी और घरेलू सैलानियों के लिए इलेक्ट्रिक हेरिटेज बस सेवा और बहुभाषी ऑडियो गाइड ऐप भी शुरू किया है।"
        ),
    )

    anc_x0 = grid.col_x0(3)
    anc_x1 = grid.col_x1(3, 6)
    anc_cur_y = bot_y0

    anchor_head = "नए आईटी हब से पांच लाख युवाओं को रोजगार"
    _, _, anc_h_pt, anc_hh = fit_aditya_bharat_headline(
        0, anc_x0, anc_cur_y, anc_x1,
        raw_text=anchor_head,
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=50.0,
        lo_pt=45.0,
        align="center",
    )
    anc_cur_y = round(anc_cur_y + anc_hh + 1.0, 2)

    anchor_sub = "महानगरों के चारों ओर विकसित हो रहे ग्लोबल कैपेबिलिटी सेंटर : बहुराष्ट्रीय टेक्नोलॉजी कंपनियों ने शुरू किया रिकॉर्ड निवेश"
    _, _, _, anc_sub_h = fit_aditya_bharat_headline(
        0, anc_x0, anc_cur_y, anc_x1,
        raw_text=anchor_sub,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=16.5,
        lo_pt=12.5,
        align="center",
    )
    anc_body_y0 = round(anc_cur_y + anc_sub_h + 3.0, 2)
    anc_body_y1 = bot_y1

    r_anc_body = cmd("frame.create", {
        "spread": 0,
        "rect": [anc_x0, anc_body_y0, anc_x1, anc_body_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_anc_body["id"]],
        "columns": 6,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })

    acap_y1 = round(snap_underflow_top(anc_body_y1, num_underflow_lines=3) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(5),
        anc_body_y0,
        grid.col_x1(5, 2),
        acap_y1,
        "p2_itpark_823939.jpg",
        "ab_p2_anchor_cmyk.jpg",
        "महानगर के नए साइबर कॉरिडोर में निर्मित आधुनिक ग्रीन टेक्नोलॉजी परिसर। — फाइल फोटो",
        cap_h=23.0,
    )

    anc_body = (
        "देश के प्रमुख महानगरों को वैश्विक सॉफ्टवेयर, क्लाउड कंप्यूटिंग और फिनटेक नवाचार का केंद्र बनाने के लिए तीन नए इंटीग्रेटेड आईटी व साइबर पार्क "
        "विकसित किए जा रहे हैं। इस योजना के अंतर्गत विश्व की सौ से अधिक फॉर्च्यून कंपनियों ने अपने ग्लोबल कैपेबिलिटी और अनुसंधान केंद्र स्थापित करने के "
        "लिए भूमि आवंटन प्राप्त कर लिया है। उद्योग विभाग के अनुसार इन परिसरों में प्लग-एंड-प्ले ऑफिस स्पेस, हाई-स्पीड ऑप्टिकल फाइबर नेटवर्क, ग्रीन डेटा "
        "सेंटर और स्टार्टअप इनक्यूबेशन हब बनाए गए हैं। इससे स्थानीय इंजीनियरिंग कॉलेजों के युवाओं को अपने ही शहर में अंतरराष्ट्रीय स्तर के पैकेज पर काम "
        "करने का अवसर मिलेगा। विशेषज्ञों का मानना है कि टियर-वन और टियर-टू महानगरों में आईटी कॉरिडोर के विस्तार से रियल एस्टेट, हॉस्पिटैलिटी और सेवा क्षेत्र "
        "की अर्थव्यवस्था में भी सालाना दो लाख करोड़ रुपये की अतिरिक्त वृद्धि होगी।"
    )
    fit_aditya_bharat_body(r_anc_body["story"], "इंदौर", "ब्यूरो", anc_body)

    cmd("edit.deselectAll")
    cmd("view.fitPage", {})

    out_pd = VAULT_DIR / "Aditya_Bharat_Page_02_Mahanagar_34x53.pagedesigner"
    out_png = VAULT_DIR / "Aditya_Bharat_Page_02_Mahanagar_34x53.png"
    out_pdf = VAULT_DIR / "Aditya_Bharat_Page_02_Mahanagar_CMYK_34x53.pdf"
    rpc("app.save", {"path": str(out_pd)})
    rpc("app.export", {"path": str(out_png), "page": 0, "scale": 1.5})
    try:
        rpc("engine.execute", {"command": "file.exportPdf", "params": {"path": str(out_pdf)}})
    except Exception:
        pass

    artifact_png = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\8707c72d-58b0-4715-a099-3efffcd57514\aditya_bharat_page_02_mahanagar_34x53.png")
    artifact_png.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_png, artifact_png)

    print(
        f"=== ADITYA BHARAT PAGE 02 (MAHANAGAR) BUILT IN {time.perf_counter()-t0:.2f}s ===\n"
        f"    FlyerHead={fl_h_pt}pt | Lead5Col={lead_h_pt}pt | Story3Col={s3_h_pt}pt | Story4Col={c4_h_pt}pt | Anchor6Col={anc_h_pt}pt\n"
        f"    Saved: {out_pd}"
    )


if __name__ == "__main__":
    build_aditya_bharat_page2()
