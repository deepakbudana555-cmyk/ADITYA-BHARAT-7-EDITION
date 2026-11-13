# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — PAGE 03 ('प्रादेशिक') VERTICAL-TOP MASTER BROADSHEET BUILDER (34x53 cm | Print Area 32x51 cm)
=============================================================================================================================
Strictly implements the official 'Aditya Bharat' Stylesheet & Page 03 Vertical-Start Architecture:
  1. Page Size & Grid   : 34.0 cm x 53.0 cm (1-1-1-1 cm outer margins -> Fixed Print Area = 32.0 cm x 51.0 cm, 8 Cols, 4.0 mm Gutter)
  2. Inside Masthead    : 1.5 cm Height (y = 1.0 .. 2.5 cm, Cols 1..8):
       - Left           : Red Color Box ('FlyerCrimson') with Page Name 'प्रादेशिक' in 20.0 pt 'DB Hindi 6' White ('[Paper]')
       - Center         : Official 'आदित्य भारत' Masthead Logo centered ('100% Black')
       - Right          : Dateline in 16.0 pt ('DB Hindi' Bold) + Page Number '03' in 18.0 pt 'Times New Roman' Bold
       - Bottom Rule    : 2.0 pt Rule in 60% Gray across all 8 columns
  3. Vertical-First Interlocked Layout (NO 8-Col Flyer — Starts at Top with 5-Col Vertical Lead + 3-Col Right Vertical Stack):
       - LEFT VERTICAL ZONE (Cols 1..5, y = 2.85 .. 41.35 cm):
           * Top 5-Col Lead Package (Cols 1..5, y = 2.85 .. 22.85 cm, Height = 20.0 cm):
             2-Line DB Rasrand Bold Headline + 18pt Subhead + Col 1 Full-Height 40% Gray Box (2.5mm inset, 100% filled) +
             4-Col Body (Cols 2..5) + Red Blurb 'निवेश' + Center Photo in Cols 3..4 + Caption + 100% Filled Highlight Box + 4-Line Underflow.
           * Mid-Upper Split (Cols 1..5, y = 23.20 .. 33.40 cm, Height = 10.2 cm):
             Cols 1..3 (3-Col Illustrated Story with Photo in Cols 2..3 + 3-Line Underflow) + Cols 4..5 (2-Col Story with Red Blurb 'रफ्तार').
           * Mid-Lower Split (Cols 1..5, y = 33.75 .. 41.35 cm, Height = 7.6 cm):
             Cols 1..2 (2-Col Story) + Cols 3..5 (3-Col Story with Subhead & Red Blurb 'स्वास्थ्य').
       - RIGHT VERTICAL ZONE (Cols 6..8, y = 2.85 .. 41.35 cm):
           * Right-Top 3-Col Feature (Cols 6..8, y = 2.85 .. 17.55 cm):
             2-Line Headline + Subhead + Photo in Cols 7..8 + Caption + 4-Line Underflow.
           * Right-Mid 3-Col Feature (Cols 6..8, y = 17.90 .. 30.10 cm):
             2-Line Headline + Photo in Cols 6..7 + Caption + 3-Line Underflow + Col 8 Full Body.
           * Right-Lower 3-Col Package (Cols 6..8, y = 30.45 .. 41.35 cm):
             2-Line Headline + Red Blurb 'ऊर्जा' in Col 6 + 100% Filled Highlight Box in Cols 7..8 + 3-Line Underflow.
       - BOTTOM STRIP (Cols 1..8, y = 41.70 .. 52.00 cm, Height = 10.3 cm):
           * Bottom-Left 2-Col Story (Cols 1..2) + Bottom-Right 6-Col Anchor Package (Cols 3..8, 45-50pt Headline + Subhead + Photo in Cols 5..6 + 3-Line Underflow).
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
        cropped = ImageOps.fit(im_rgb, (target_w_px, target_h_px), method=Image.Resampling.LANCZOS, centering=(0.5, 0.38))
        cmyk_im = cropped.convert("CMYK")
        cmyk_im.save(dst_p, "JPEG", quality=95, dpi=(300, 300))
    return dst_p


class AdityaBharatPage3Grid:
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

        # Top Content Start (y = 2.85 cm)
        self.top_y0 = round(self.masthead_y1 + mm(3.5), 2)

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
    lo_pt: float = 13.0,
    fixed_pt: float = None,
    align: str = "left",
    leading_add_pt: float = 1.0,
):
    # Strictly enforce 100% Black ('[Black]') on all headlines & subheads
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
        effective_lo = lo_pt if font_family != "DB Rasrand Bold" else max(lo_pt, 30.0)
        lo = int(round(effective_lo * 2))
        hi = int(round(hi_pt * 2))
        best = effective_lo
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
        best_pt = fixed_pt if fixed_pt is not None else lo_pt
        if fixed_pt is None:
            for _, l1, l2 in candidates[:5]:
                pt1 = max_pt_for_line(l1)
                pt2 = max_pt_for_line(l2)
                raw_min = min(pt1, pt2, hi_pt)
                score = raw_min - 0.6 * abs(pt1 - pt2)
                if score > best_score:
                    best_score = score
                    best_pt = max(lo_pt, raw_min)
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
    "\nराज्य शासन और औद्योगिक विकास निगम के समन्वय से इस प्रादेशिक परियोजना को निर्धारित समय-सीमा के भीतर पूरा करने का लक्ष्य रखा गया है। "
    "वरिष्ठ अधिकारियों के अनुसार आधुनिक तकनीक और डिजिटल निगरानी प्रणाली के माध्यम से प्रत्येक चरण की प्रगति की नियमित समीक्षा की जा रही है। "
    "आर्थिक विशेषज्ञों का मानना है कि इस पहल से प्रदेश के लाखों युवाओं और किसानों को सीधा लाभ मिलेगा तथा स्थानीय स्तर पर रोजगार के नए अवसर सृजित होंगे। "
    "जिला प्रशासन और संबंधित विभागों को भी निर्देश दिए गए हैं कि सभी योजनाओं का लाभ पात्र नागरिकों तक पारदर्शी और त्वरित रूप से पहुंचाया जाए।"
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
        "\n• औद्योगिक कॉरिडोर के दोनों ओर समर्पित लॉजिस्टिक्स पार्क, वेयरहाउस और कंटेनर डिपो का निर्माण तेज।"
        "\n• स्थानीय युवाओं के कौशल विकास के लिए प्रत्येक औद्योगिक क्षेत्र में आधुनिक प्रशिक्षण केंद्र स्थापित।"
        "\n• चौबीस घंटे निर्बाध हरित बिजली और औद्योगिक जल आपूर्ति के लिए विशेष सब-स्टेशन व पाइपलाइन नेटवर्क।"
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
    grid: AdityaBharatPage3Grid,
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


def build_aditya_bharat_page3():
    t0 = time.perf_counter()
    connect_page_designer()
    grid = AdityaBharatPage3Grid()

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
            "title": "आदित्य भारत — पेज 03 प्रादेशिक (34x53 सेमी | प्रिंट एरिया 32x51 सेमी)",
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
    #   - Left   : Red Color Box ('FlyerCrimson') with Page Name 'प्रादेशिक' in 20 pt 'DB Hindi 6' White ('[Paper]')
    #   - Center : Official 'आदित्य भारत' Masthead Logo centered ('100% Black')
    #   - Right  : Dateline in 16 pt ('DB Hindi' Bold) + Page Number '03' in 18 pt 'Times New Roman' Bold
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
        "text": "प्रादेशिक",
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
        "text": "03",
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
    # VERTICAL SPLIT GEOMETRY (y = 2.85 .. 41.35 cm):
    #   - Left Vertical Zone  : Cols 1..5 (Starts at top with 5-Col Vertical Lead!)
    #   - Right Vertical Zone : Cols 6..8 (3-Col Vertical Stack from top to y = 41.35 cm)
    # ==========================================================================
    top_y0 = grid.top_y0
    vzone_y1 = snap_frame_bottom_to_baseline(round(top_y0 + cm(38.5), 2))

    # ==========================================================================
    # LEFT VERTICAL ZONE — PART 1: TOP 5-COLUMN LEAD PACKAGE (Cols 1..5, Height = 20.0 cm)
    # ==========================================================================
    lead_x0 = grid.col_x0(1)
    lead_x1 = grid.col_x1(1, 5)
    lead_y0 = top_y0
    lead_y1 = snap_frame_bottom_to_baseline(round(lead_y0 + cm(20.0), 2))
    lead_cur_y = lead_y0

    # 18 pt Subhead above 5-Col Top Lead Headline
    lead_top_sub = "पीथमपुर-देवास-उज्जैन इंडस्ट्रियल कॉरिडोर को मिली रफ्तार : पचास हजार करोड़ के निवेश प्रस्तावों को कैबिनेट की मंजूरी"
    _, _, _, lsub_h = fit_aditya_bharat_headline(
        0, lead_x0, lead_cur_y, lead_x1,
        raw_text=lead_top_sub,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=18.0,
        lo_pt=14.0,
        align="left",
    )
    lead_cur_y = round(lead_cur_y + lsub_h + 0.5, 2)

    lead_head_txt = "प्रदेश में बनेंगे पांच नए इंडस्ट्रियल और लॉजिस्टिक्स हब, दो लाख को रोजगार"
    _, _, lead_h_pt, lead_hh = fit_aditya_bharat_headline(
        0, lead_x0, lead_cur_y, lead_x1,
        raw_text=lead_head_txt,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=58.0,
        lo_pt=42.0,
        align="left",
    )
    lead_body_y0 = round(lead_cur_y + lead_hh + 1.0, 2)
    lead_body_y1 = lead_y1
    inset_pt = mm(2.5)

    # Cols 1..4 (4-Column Body Frame for Top 5-Col Lead starting in Col 1)
    lbody_x0 = grid.col_x0(1)
    lbody_x1 = grid.col_x1(1, 4)
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

    # Red Subject Blurb 'निवेश' in Col 1
    place_red_subject_blurb(0, grid.col_x0(1), round(lead_body_y0 + cm(3.1), 2), "निवेश")

    # Center 2-Column Photo (Cols 2..3) + 100% Filled Highlight Box + 8-Line Underflow (compact photo!)
    l_px0 = grid.col_x0(2)
    l_px1 = grid.col_x1(2, 2)
    l_underflow_top = snap_underflow_top(lead_body_y1, num_underflow_lines=8)
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
        "p3_pithampur_828149.jpg",
        "ab_p3_lead_cmyk.jpg",
        "पीथमपुर औद्योगिक क्षेत्र में स्थापित आधुनिक ऑटोमोबाइल और इलेक्ट्रिक व्हीकल निर्माण इकाई। — फाइल फोटो",
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
        "• एमएसएमई और स्टार्टअप इकाइयों को बिना गारंटी सस्ती ब्याज दर पर कार्यशील पूंजी ऋण की सुविधा।\n"
        "• महिला उद्यमियों द्वारा स्थापित उद्योगों को बिजली शुल्क और स्टांप ड्यूटी में शत-प्रतिशत छूट।\n"
        "• निर्यात आधारित इकाइयों के लिए एयर कार्गो और ड्राई पोर्ट टर्मिनल पर विशेष माल भाड़ा सब्सिडी।\n"
        "• प्रत्येक औद्योगिक पार्क में चौबीस घंटे हाई-स्पीड फाइबर नेटवर्क और कॉमन एफ्लुएंट ट्रीटमेंट प्लांट।"
    )
    fit_box_completely(
        r_lspec["story"],
        head_str="उद्योग नीति : सिंगल-विंडो से तुरंत मंजूरी",
        raw_bullets=lspec_bullets,
        head_pt=16.0,
        head_align="left",
        body_pt=10.5,
        body_lead=11.3,
        para_space=2.2,
    )

    lead_body_txt = (
        "प्रदेश को देश का अग्रणी मैन्युफैक्चरिंग और लॉजिस्टिक्स केंद्र बनाने के लिए राज्य कैबिनेट ने पांच नए इंटीग्रेटेड इंडस्ट्रियल कॉरिडोर विकसित "
        "करने के प्रस्ताव को मंजूरी दे दी है। इस महत्वाकांक्षी योजना के तहत इंदौर-पीथमपुर, देवास-उज्जैन, भोपाल-मंडीदीप, रतलाम-जावरा और रायपुर-दुर्ग औद्योगिक "
        "क्षेत्रों में दस हजार एकड़ से अधिक भूमि पर नए क्लस्टर तैयार किए जाएंगे। उद्योग विभाग के प्रमुख सचिव ने बताया कि हाल ही में संपन्न इन्वेस्टर्स समिट "
        "में प्राप्त पचास हजार करोड़ रुपये के निवेश प्रस्तावों को धरातल पर उतारने के लिए भूमि आवंटन की प्रक्रिया शुरू कर दी गई है।\n"
        "इस औद्योगिक विस्तार से ऑटोमोबाइल, इलेक्ट्रिक व्हीकल, ग्रीन एनर्जी, फार्मास्यूटिकल्स, टेक्सटाइल और खाद्य प्रसंस्करण क्षेत्रों में दो लाख से अधिक "
        "युवाओं को प्रत्यक्ष व अप्रत्यक्ष रोजगार मिलेगा। सभी नए औद्योगिक पार्कों में प्लग-एंड-प्ले फैक्ट्री शेड, डेडिकेटेड पावर फीडर और आधुनिक वेयरहाउसिंग सुविधाएं होंगी।"
    )
    fit_aditya_bharat_body(r_lead_body["story"], "भोपाल", "ब्यूरो", lead_body_txt)

    # Col 5 (LAST Column of the 5-Col Lead) Full-Height Story Box (40% Gray tint, 2.5 mm inset on all 4 sides, 100% filled)
    box5_x0 = grid.col_x0(5)
    box5_x1 = grid.col_x1(5, 1)
    r_lbox = cmd("frame.create", {
        "spread": 0,
        "rect": [box5_x0, lead_body_y0, box5_x1, lead_body_y1],
        "content": "text",
        "text": "",
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_lbox["id"]], "swatch": "[Black]", "tint": 0.15}},
        {"command": "object.stroke", "params": {"ids": [r_lbox["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 0.55}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_lbox["id"]],
            "columns": 1,
            "inset": [inset_pt, inset_pt, inset_pt, inset_pt],
            "verticalJustification": "top",
        }},
    ])
    lbox_bullets = (
        "• पीथमपुर, देवास, रतलाम, मंडीदीप और रायपुर के पास विकसित होंगे अत्याधुनिक मल्टी-मॉडल लॉजिस्टिक्स पार्क।\n"
        "• इलेक्ट्रिक व्हीकल, सेमीकंडक्टर, फार्मा और फूड प्रोसेसिंग इकाइयों को भूमि आवंटन में पचास प्रतिशत छूट।\n"
        "• सभी औद्योगिक क्लस्टरों को सीधे दिल्ली-मुंबई और मध्य भारत एक्सप्रेस-वे के फ्रेट कॉरिडोर से जोड़ा जाएगा।\n"
        "• स्थानीय युवाओं को उद्योगों की मांग के अनुरूप प्रशिक्षण देने के लिए दस नए स्किल डेवलपमेंट सेंटर बनेंगे।\n"
        "• निवेशकों को पंद्रह दिनों के भीतर सभी मंजूरियां देने के लिए सिंगल-विंडो पोर्टल का नया संस्करण लागू।\n"
        "• प्रत्येक औद्योगिक क्षेत्र में चौबीस घंटे हरित बिजली, डेडिकेटेड जल आपूर्ति और कॉमन ट्रीटमेंट प्लांट की सुविधा।\n"
        "• महिला उद्यमियों और स्टार्टअप इकाइयों को स्टांप ड्यूटी व बिजली शुल्क में विशेष सरकारी रियायत।"
    )
    fit_box_completely(
        r_lbox["story"],
        head_str="पैकेज की खास बातें",
        raw_bullets=lbox_bullets,
        head_pt=16.0,
        head_align="center",
        body_pt=10.5,
        body_lead=11.3,
        para_space=2.4,
    )

    # Horizontal rule across Cols 1..5 below Top 5-Col Lead
    lsep1_y = round(lead_y1 + mm(1.75), 2)
    r_lsep1 = cmd("line.create", {"spread": 0, "a": [lead_x0, lsep1_y], "b": [lead_x1, lsep1_y]})
    cmd("object.stroke", {"ids": [r_lsep1["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # LEFT VERTICAL ZONE — PART 2: MID-UPPER SPLIT (Cols 1..5 = 3 Col + 2 Col, Height = 10.2 cm)
    # ==========================================================================
    m1_y0 = round(lsep1_y + mm(1.75), 2)
    m1_y1 = snap_frame_bottom_to_baseline(round(m1_y0 + cm(10.2), 2))

    # --- Cols 1..3: 3-Column Illustrated Irrigation Story ---
    m1a_x0 = grid.col_x0(1)
    m1a_x1 = grid.col_x1(1, 3)
    m1a_head = "नर्मदा-क्षिप्रा लिंक से आठ लाख हेक्टेयर में पहुंचेगा सिंचाई जल"
    _, _, m1a_pt, m1a_hh = fit_aditya_bharat_headline(
        0, m1a_x0, m1_y0, m1a_x1,
        raw_text=m1a_head,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=38.0,
        lo_pt=30.0,
        align="left",
    )
    m1a_by0 = round(m1_y0 + m1a_hh + 2.0, 2)
    r_m1a_b = cmd("frame.create", {
        "spread": 0,
        "rect": [m1a_x0, m1a_by0, m1a_x1, m1_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_m1a_b["id"]],
        "columns": 3,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, m1a_x0, round(m1a_by0 + cm(2.1), 2), "सिंचाई")

    m1a_cap_y1 = round(snap_underflow_top(m1_y1, num_underflow_lines=7) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(2),
        m1a_by0,
        grid.col_x1(2, 2),
        m1a_cap_y1,
        "p5_kenbetwa_830631.jpg",
        "ab_p3_irrigation_cmyk.jpg",
        "नर्मदा-क्षिप्रा लिंक परियोजना के तहत निर्मित मुख्य पंपिंग स्टेशन और नहर नेटवर्क। — फाइल फोटो",
        cap_h=23.0,
    )
    m1a_body = (
        "मालवा और चंबल अंचल के किसानों को बारहों महीने सिंचाई सुविधा उपलब्ध कराने के लिए नर्मदा-क्षिप्रा-चंबल नदी जोड़ो परियोजना के तीसरे चरण का कार्य "
        "तेजी से पूरा किया जा रहा है। जल संसाधन विभाग के अनुसार प्रेशराइज्ड पाइपलाइन और माइक्रो इरिगेशन नेटवर्क के जरिए आठ लाख हेक्टेयर कृषि भूमि को "
        "सीधे सिंचाई का पानी मिलेगा। इससे तीन हजार से अधिक गांवों में भू-जल स्तर में भी स्थायी सुधार होगा और रबी व खरीफ फसलों का उत्पादन दोगुना हो सकेगा।"
    )
    fit_aditya_bharat_body(r_m1a_b["story"], "इंदौर", "संवाददाता", m1a_body)

    # --- Cols 4..5: 2-Column Story ---
    m1b_pt = place_two_col_story(
        grid, grid.col_x0(4), grid.col_x1(4, 2), m1_y0, m1_y1,
        headline="उज्जैन-इंदौर कॉरिडोर पर दौड़ेंगी नई इलेक्ट्रिक बसें",
        city="उज्जैन",
        agency="संवाददाता",
        blurb_word="रफ्तार",
        body=(
            "आगामी सिंहस्थ और बढ़ते यात्री यातायात को देखते हुए उज्जैन-इंदौर सिक्स-लेन ग्रीन कॉरिडोर का निर्माण युद्धस्तर पर जारी है। सड़क विकास निगम ने "
            "इस मार्ग पर जून माह से सौ वातानुकूलित इलेक्ट्रिक इंटरसिटी बसें चलाने की तैयारी पूरी कर ली है। प्रत्येक दस किलोमीटर पर फास्ट चार्जिंग स्टेशन, "
            "स्मार्ट बस स्टॉप और यात्रियों के लिए आधुनिक जनसुविधा केंद्र बनाए जा रहे हैं। इससे दोनों शहरों के बीच यात्रा का समय घटकर केवल पैंतालीस मिनट रह जाएगा।"
        ),
    )

    # Horizontal rule across Cols 1..5 below Mid-Upper Split
    lsep2_y = round(m1_y1 + mm(1.75), 2)
    r_lsep2 = cmd("line.create", {"spread": 0, "a": [lead_x0, lsep2_y], "b": [lead_x1, lsep2_y]})
    cmd("object.stroke", {"ids": [r_lsep2["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # LEFT VERTICAL ZONE — PART 3: MID-LOWER SPLIT (Cols 1..5 = 2 Col + 3 Col, up to vzone_y1)
    # ==========================================================================
    m2_y0 = round(lsep2_y + mm(1.75), 2)
    m2_y1 = vzone_y1

    # --- Cols 1..2: 2-Column Story ---
    m2a_pt = place_two_col_story(
        grid, grid.col_x0(1), grid.col_x1(1, 2), m2_y0, m2_y1,
        headline="समर्थन मूल्य पर उपज खरीदी को स्लॉट बुकिंग",
        city="रायपुर",
        agency="ब्यूरो",
        blurb_word="",
        body=(
            "प्रदेश की सभी कृषि उपज मंडियों में समर्थन मूल्य पर गेहूं, चना और सरसों की खरीदी प्रक्रिया को सुगम बनाने के लिए ऑनलाइन स्लॉट बुकिंग अनिवार्य कर दी गई है। "
            "किसानों को अपनी उपज बेचने के लिए कतार में इंतजार नहीं करना पड़ेगा और अड़तालीस घंटे में भुगतान सीधे बैंक खातों में पहुंचेगा।"
        ),
    )

    # --- Cols 3..5: 3-Column Story Package with Subhead ---
    m2b_x0 = grid.col_x0(3)
    m2b_x1 = grid.col_x1(3, 3)
    m2b_cur_y = m2_y0
    m2b_head = "सभी जिला अस्पतालों में बनेंगे आधुनिक टेली-आईसीयू वार्ड"
    _, _, m2b_pt, m2b_hh = fit_aditya_bharat_headline(
        0, m2b_x0, m2b_cur_y, m2b_x1,
        raw_text=m2b_head,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=38.0,
        lo_pt=30.0,
        align="left",
    )
    m2b_cur_y = round(m2_y0 + m2b_hh + 0.5, 2)

    m2b_sub = "मेडिकल कॉलेजों के विशेषज्ञ डॉक्टर चौबीस घंटे करेंगे गंभीर मरीजों की निगरानी"
    _, _, _, m2b_sh = fit_aditya_bharat_headline(
        0, m2b_x0, m2b_cur_y, m2b_x1,
        raw_text=m2b_sub,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=14.5,
        lo_pt=11.5,
        align="left",
    )
    m2b_by0 = round(m2b_cur_y + m2b_sh + 1.0, 2)
    r_m2b_b = cmd("frame.create", {
        "spread": 0,
        "rect": [m2b_x0, m2b_by0, m2b_x1, m2_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_m2b_b["id"]],
        "columns": 3,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, m2b_x0, round(m2b_by0 + cm(1.1), 2), "स्वास्थ्य")
    m2b_body = (
        "ग्रामीण और कस्बाई क्षेत्रों के गंभीर मरीजों को बड़े शहरों के सुपर-स्पेशियलिटी अस्पतालों जैसा उपचार उपलब्ध कराने के लिए प्रदेश के सभी जिला चिकित्सालयों "
        "में दस-दस बेड के अत्याधुनिक टेली-आईसीयू वार्ड स्थापित किए जा रहे हैं। इन वार्डों को हाई-स्पीड फाइबर नेटवर्क के जरिए सीधे शासकीय मेडिकल कॉलेजों के "
        "सेंट्रल कमांड सेंटर से जोड़ा गया है। वरिष्ठ विशेषज्ञ चिकित्सक चौबीस घंटे मरीजों के वाइटल पैरामीटर्स की लाइव निगरानी कर तुरंत इलाज निर्देशित करेंगे।"
    )
    fit_aditya_bharat_body(r_m2b_b["story"], "भोपाल", "एजेंसी", m2b_body)

    # ==========================================================================
    # RIGHT VERTICAL ZONE (Cols 6..8, y = 2.85 .. 41.35 cm — 3 Vertical Stacked Packages)
    # ==========================================================================
    rx0 = grid.col_x0(6)
    rx1 = grid.col_x1(6, 3)

    # --- RIGHT 1: Top 3-Col Illustrated Second Lead (y = 2.85 .. 17.55 cm, Height = 14.7 cm) ---
    r1_y0 = top_y0
    r1_y1 = snap_frame_bottom_to_baseline(round(r1_y0 + cm(14.7), 2))
    r1_cur_y = r1_y0

    r1_head = "छह नए एक्सप्रेस-वे से जुड़ेंगे प्रमुख औद्योगिक व पर्यटन केंद्र"
    _, _, r1_pt, r1_hh = fit_aditya_bharat_headline(
        0, rx0, r1_cur_y, rx1,
        raw_text=r1_head,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=38.0,
        lo_pt=30.0,
        align="left",
    )
    r1_cur_y = round(r1_cur_y + r1_hh + 0.5, 2)

    r1_sub = "भोपाल-इंदौर-जबलपुर के बीच माल ढुलाई और यात्रा का समय घटकर रह जाएगा आधा"
    _, _, _, r1_sh = fit_aditya_bharat_headline(
        0, rx0, r1_cur_y, rx1,
        raw_text=r1_sub,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=14.5,
        lo_pt=11.5,
        align="left",
    )
    r1_by0 = round(r1_cur_y + r1_sh + 1.0, 2)

    r_r1_b = cmd("frame.create", {
        "spread": 0,
        "rect": [rx0, r1_by0, rx1, r1_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_r1_b["id"]],
        "columns": 3,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })

    r1_cap_y1 = round(snap_underflow_top(r1_y1, num_underflow_lines=12) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(7),
        r1_by0,
        grid.col_x1(7, 2),
        r1_cap_y1,
        "p3_highway_827755.jpg",
        "ab_p3_highway_cmyk.jpg",
        "प्रदेश में नवनिर्मित सिक्स-लेन एक्सेस-कंट्रोल्ड एक्सप्रेस-वे कॉरिडोर का विहंगम दृश्य। — फाइल फोटो",
        cap_h=23.0,
    )
    r1_body = (
        "प्रदेश के सभी प्रमुख संभागों, औद्योगिक क्लस्टर्स और पर्यटन स्थलों को तेज गति के सड़क नेटवर्क से जोड़ने के लिए छह नए एक्सेस-कंट्रोल्ड ग्रीनफील्ड एक्सप्रेस-वे "
        "का निर्माण किया जा रहा है। लोक निर्माण विभाग और राष्ट्रीय राजमार्ग प्राधिकरण के संयुक्त तत्वावधान में तीन हजार किलोमीटर लंबे इन राजमार्गों पर एक लाख करोड़ "
        "रुपये से अधिक खर्च किए जाएंगे। इन एक्सप्रेस-वे के दोनों ओर लॉजिस्टिक्स हब, कृषि प्रसंस्करण केंद्र, सोलर चार्जिंग प्लाजा और ट्रॉमा केयर सेंटर भी विकसित "
        "किए जा रहे हैं। अधिकारियों के अनुसार अगले अठारह महीनों में पहले चरण का निर्माण पूरा होने पर माल ढुलाई और यात्री परिवहन का समय आधा रह जाएगा।"
    )
    fit_aditya_bharat_body(r_r1_b["story"], "रायपुर", "ब्यूरो", r1_body)

    rsep1_y = round(r1_y1 + mm(1.75), 2)
    r_rsep1 = cmd("line.create", {"spread": 0, "a": [rx0, rsep1_y], "b": [rx1, rsep1_y]})
    cmd("object.stroke", {"ids": [r_rsep1["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # --- RIGHT 2: Mid 3-Col Illustrated University/AI Package (y = 17.90 .. 30.10 cm, Height = 12.2 cm) ---
    r2_y0 = round(rsep1_y + mm(1.75), 2)
    r2_y1 = snap_frame_bottom_to_baseline(round(r2_y0 + cm(12.2), 2))
    r2_cur_y = r2_y0

    r2_head = "पंद्रह विश्वविद्यालयों में शुरू होंगे सेमीकंडक्टर व एआई कोर्स"
    _, _, r2_pt, r2_hh = fit_aditya_bharat_headline(
        0, rx0, r2_cur_y, rx1,
        raw_text=r2_head,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=38.0,
        lo_pt=30.0,
        align="left",
    )
    r2_by0 = round(r2_cur_y + r2_hh + 2.0, 2)

    r_r2_b = cmd("frame.create", {
        "spread": 0,
        "rect": [rx0, r2_by0, rx1, r2_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_r2_b["id"]],
        "columns": 3,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, grid.col_x0(6), round(r2_by0 + cm(2.1), 2), "शिक्षा")

    # Compact photo in Cols 7..8 so Col 6 starts at top with 3-Tone Byline + 9-line underflow
    r2_cap_y1 = round(snap_underflow_top(r2_y1, num_underflow_lines=9) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(7),
        r2_by0,
        grid.col_x1(7, 2),
        r2_cap_y1,
        "p3_campus_827441_print.jpg",
        "ab_p3_campus_cmyk.jpg",
        "विश्वविद्यालय परिसर में स्थापित अत्याधुनिक सेमीकंडक्टर डिजाइन और रोबोटिक्स प्रयोगशाला। — फाइल फोटो",
        cap_h=23.0,
    )
    r2_body = (
        "नए शैक्षणिक सत्र से प्रदेश के पंद्रह शासकीय विश्वविद्यालयों और इंजीनियरिंग महाविद्यालयों में सेमीकंडक्टर चिप डिजाइन, आर्टिफिशियल इंटेलिजेंस, क्वांटम कंप्यूटिंग "
        "तथा ग्रीन हाइड्रोजन टेक्नोलॉजी के नए बीटेक व एमटेक पाठ्यक्रम शुरू किए जा रहे हैं। उच्च शिक्षा विभाग ने इसके लिए देश की प्रमुख टेक्नोलॉजी कंपनियों और "
        "आईआईटी के साथ विशेष अनुबंध किया है। प्रत्येक परिसर में पचास करोड़ की लागत से सेंटर ऑफ एक्सीलेंस स्थापित किया गया है।"
    )
    fit_aditya_bharat_body(r_r2_b["story"], "अहमदाबाद", "ब्यूरो", r2_body)

    rsep2_y = round(r2_y1 + mm(1.75), 2)
    r_rsep2 = cmd("line.create", {"spread": 0, "a": [rx0, rsep2_y], "b": [rx1, rsep2_y]})
    cmd("object.stroke", {"ids": [r_rsep2["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # --- RIGHT 3: Lower 3-Col Solar & Rural Package + 100% Filled Highlight Box (up to vzone_y1) ---
    r3_y0 = round(rsep2_y + mm(1.75), 2)
    r3_y1 = vzone_y1
    r3_cur_y = r3_y0

    r3_head = "ग्राम पंचायतों में सौर ऊर्जा से चलेंगे सभी पेयजल पंप"
    _, _, r3_pt, r3_hh = fit_aditya_bharat_headline(
        0, rx0, r3_cur_y, rx1,
        raw_text=r3_head,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=38.0,
        lo_pt=30.0,
        align="left",
    )
    r3_by0 = round(r3_cur_y + r3_hh + 2.0, 2)

    r_r3_b = cmd("frame.create", {
        "spread": 0,
        "rect": [rx0, r3_by0, rx1, r3_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_r3_b["id"]],
        "columns": 3,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, grid.col_x0(6), round(r3_by0 + cm(1.8), 2), "ऊर्जा")

    # 100% Filled Highlight Box in Cols 7..8 at top of r3_by0 with 4 lines underflow below
    r3_box_y1 = round(snap_underflow_top(r3_y1, num_underflow_lines=4) - 3.2, 2)
    r_r3_box = cmd("frame.create", {
        "spread": 0,
        "rect": [grid.col_x0(7), r3_by0, grid.col_x1(7, 2), r3_box_y1],
        "content": "text",
        "text": "",
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_r3_box["id"]], "swatch": "EditPointerBg", "tint": 1.0}},
        {"command": "object.stroke", "params": {"ids": [r_r3_box["id"]], "swatch": "[Black]", "weight": 0.8, "tint": 0.55}},
        {"command": "object.textWrap", "params": {"ids": [r_r3_box["id"]], "mode": "boundingBox", "offset": [0.0, 0.0, 3.0, 0.0]}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_r3_box["id"]],
            "columns": 1,
            "inset": [inset_pt, inset_pt, inset_pt, inset_pt],
            "verticalJustification": "top",
        }},
    ])
    r3_bullets = (
        "• एक लाख किसानों को सोलर पंप लगाने पर सत्तर प्रतिशत तक सरकारी अनुदान सीधे खाते में।\n"
        "• अतिरिक्त सौर बिजली ग्रिड को बेचकर ग्राम पंचायतें और किसान कमा सकेंगे सालाना अतिरिक्त आय।\n"
        "• ग्राम स्तर पर सोलर टेक्नीशियन तैयार करने के लिए पांच हजार युवाओं का विशेष कौशल प्रशिक्षण।\n"
        "• सभी ग्रामीण पेयजल योजनाओं में स्मार्ट मीटर और ऑटोमैटिक सोलर पंप कंट्रोलर अनिवार्य रूप से लागू।"
    )
    fit_box_completely(
        r_r3_box["story"],
        head_str="सौर मिशन : किसानों को मुफ्त बिजली",
        raw_bullets=r3_bullets,
        head_pt=16.0,
        head_align="left",
        body_pt=10.5,
        body_lead=11.3,
        para_space=2.2,
    )

    r3_body = (
        "प्रदेश की सभी ग्राम पंचायतों को ऊर्जा के क्षेत्र में आत्मनिर्भर बनाने के लिए नल-जल योजनाओं और कृषि सिंचाई पंपों को सौर ऊर्जा फीडरों से जोड़ा जा रहा है। "
        "नवीकरणीय ऊर्जा विभाग के अनुसार इस अभियान से पंचायतों के बिजली बिल में अस्सी प्रतिशत तक की कमी आएगी और किसानों को दिन के समय भी सिंचाई के लिए "
        "निर्बाध बिजली उपलब्ध होगी।"
    )
    fit_aditya_bharat_body(r_r3_b["story"], "इंदौर", "ब्यूरो", r3_body)

    # Full-width horizontal separator rule across all 8 columns above Bottom Strip
    sep_bot_y = round(vzone_y1 + mm(1.75), 2)
    r_sep_bot = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep_bot_y], "b": [grid.print_x1, sep_bot_y]})
    cmd("object.stroke", {"ids": [r_sep_bot["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BOTTOM STRIP (Cols 1..8, y = 41.70 .. 52.00 cm):
    #   - Left  : 2-Column Industrial Story (Cols 1..2)
    #   - Right : 6-Column Heritage & Eco-Tourism Anchor Package (Cols 3..8)
    # ==========================================================================
    bot_y0 = round(sep_bot_y + mm(1.75), 2)
    bot_y1 = snap_frame_bottom_to_baseline(grid.print_y1)

    bot2_pt = place_two_col_story(
        grid, grid.col_x0(1), grid.col_x1(1, 2), bot_y0, bot_y1,
        headline="देवास और धार में बनेंगे दो नए टेक्सटाइल पार्क",
        city="देवास",
        agency="संवाददाता",
        blurb_word="उद्योग",
        body=(
            "कपास उत्पादक किसानों को उनकी उपज का बेहतर दाम दिलाने और रेडीमेड गारमेंट उद्योग को बढ़ावा देने के लिए देवास तथा धार जिले में दो नए इंटीग्रेटेड "
            "टेक्सटाइल व अपैरल पार्क स्थापित किए जा रहे हैं। औद्योगिक विकास निगम ने इसके लिए तीन सौ एकड़ भूमि का आवंटन पूरा कर लिया है। यहां स्पिनिंग, वीविंग, "
            "डाइंग और गारमेंट एक्सपोर्ट की सौ से अधिक आधुनिक इकाइयां लगेंगी, जिनसे पच्चीस हजार महिलाओं व युवाओं को स्थानीय स्तर पर रोजगार मिलेगा।"
        ),
    )

    anc_x0 = grid.col_x0(3)
    anc_x1 = grid.col_x1(3, 6)
    anc_cur_y = bot_y0

    anchor_head = "दस ऐतिहासिक किलों में शुरू होगा हेरिटेज टूरिज्म"
    _, _, anc_h_pt, anc_hh = fit_aditya_bharat_headline(
        0, anc_x0, anc_cur_y, anc_x1,
        raw_text=anchor_head,
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=50.0,
        lo_pt=44.0,
        align="center",
    )
    anc_cur_y = round(bot_y0 + 44.5, 2)

    anchor_sub = "मांडू, ओरछा, पचमढ़ी और कान्हा के लिए हेलीकॉप्टर शटल सेवा व नाइट सफारी का नया मास्टर प्लान तैयार"
    _, _, anc_sub_pt, anc_sub_h = fit_aditya_bharat_headline(
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
    anc_body_y0 = round(anc_cur_y + 16.5, 2)
    anc_photo_y0 = round(anc_cur_y + anc_sub_h + 1.0, 2)
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
    place_red_subject_blurb(0, grid.col_x0(3), round(anc_body_y0 + cm(1.8), 2), "पर्यटन")

    acap_y1 = round(snap_underflow_top(anc_body_y1, num_underflow_lines=8) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(5),
        anc_photo_y0,
        grid.col_x1(5, 2),
        acap_y1,
        "p3_dewas_827606.jpg",
        "ab_p3_anchor_cmyk.jpg",
        "प्रदेश के ऐतिहासिक धरोहर एवं प्राकृतिक पर्यटन कॉरिडोर में विकसित नया पर्यटक परिसर। — फाइल फोटो",
        cap_h=23.0,
    )

    anc_body = (
        "प्रदेश की समृद्ध ऐतिहासिक धरोहरों और वन्यजीव अभयारण्यों को अंतरराष्ट्रीय पर्यटन मानचित्र पर प्रमुखता से स्थापित करने के लिए पर्यटन बोर्ड ने नया इको-हेरिटेज "
        "मास्टर प्लान लागू किया है। इसके तहत मांडू, ओरछा, ग्वालियर, महेश्वर, पचमढ़ी, कान्हा और बांधवगढ़ सहित दस प्रमुख पर्यटन केंद्रों को हेलीकॉप्टर शटल सेवा तथा "
        "लग्जरी टेंट सिटी से जोड़ा जा रहा है। ऐतिहासिक किलों और महलों में थ्री-डी प्रोजेक्शन मैपिंग के जरिए लाइट एंड साउंड शो शुरू किए गए हैं। "
        "इसके साथ ही ग्रामीण पर्यटन को प्रोत्साहित करने के लिए अभयारण्यों के आसपास के सौ गांवों में स्थानीय संस्कृति पर आधारित होम-स्टे विकसित किए गए हैं, "
        "जिससे ग्रामीण युवाओं और हस्तशिल्प कारीगरों को वर्षभर स्थायी रोजगार प्राप्त हो रहा है।"
    )
    fit_aditya_bharat_body(r_anc_body["story"], "भोपाल", "ब्यूरो", anc_body)

    cmd("edit.deselectAll")
    cmd("view.fitPage", {})

    out_pd = VAULT_DIR / "Aditya_Bharat_Page_03_Pradeshik_34x53.pagedesigner"
    out_png = VAULT_DIR / "Aditya_Bharat_Page_03_Pradeshik_34x53.png"
    out_pdf = VAULT_DIR / "Aditya_Bharat_Page_03_Pradeshik_CMYK_34x53.pdf"
    rpc("app.save", {"path": str(out_pd)})
    rpc("app.export", {"path": str(out_png), "page": 0, "scale": 1.5})
    try:
        rpc("app.export", {"path": str(out_pdf), "page": 0})
    except Exception:
        pass

    artifact_png = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\8707c72d-58b0-4715-a099-3efffcd57514\aditya_bharat_page_03_pradeshik_34x53.png")
    artifact_png.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_png, artifact_png)

    print(
        f"=== ADITYA BHARAT PAGE 03 (PRADESHIK - VERTICAL START) BUILT IN {time.perf_counter()-t0:.2f}s ===\n"
        f"    TopLead5Col={lead_h_pt}pt | RightTop3Col={r1_pt}pt | RightMid3Col={r2_pt}pt | RightLow3Col={r3_pt}pt\n"
        f"    MidLeft3Col={m1a_pt}pt | MidRight2Col={m1b_pt}pt | LowLeft2Col={m2a_pt}pt | LowMid3Col={m2b_pt}pt\n"
        f"    BotLeft2Col={bot2_pt}pt | Anchor6Col={anc_h_pt}pt (ALL >= 30.0pt!)\n"
        f"    Saved: {out_pd}"
    )


if __name__ == "__main__":
    build_aditya_bharat_page3()
