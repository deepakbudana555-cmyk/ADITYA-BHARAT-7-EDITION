# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — PAGE 07 (खेल संसार / SPORTS PAGE) MASTER BUILDER
===============================================================================
Builds Page 07 ('खेल संसार') with an energetic 12-Story Broadsheet Sports Layout
featuring ONE proper large 3-Column centerpiece action photo in the Main Lead +
compact secondary photos, strictly following the Aditya Bharat Stylesheet:
  1. Page Size           : 34.0 cm Width x 53.0 cm Height (Outer Margins = 1-1-1-1 cm)
  2. Print Area (Fixed)  : 32.0 cm Width x 51.0 cm Height (8 Columns, 4.0 mm Gutter)
  3. Zone 1 (Masthead)   : 1.5 cm Inside Running Masthead (y = 1.0 .. 2.5 cm, Cols 1..8)
                           - Left: Red Color Box ('FlyerCrimson') with 'खेल संसार' in 20 pt 'DB Hindi 6' White
                           - Center: 'आदित्य भारत' Masthead Logo ('28 pt DB Rasrand Bold', 100% Black)
                           - Right: Dateline ('16 pt DB Hindi Bold') + '07' ('18 pt Times New Roman Bold')
                           - Bottom: 2.0 pt Rule in 60% Gray across all 8 columns
  4. Total News Stories  : 12 Sports News Stories (>= 11 required), ALL Headlines >= 30.0 pt ('100% Black')
  5. Main Sports Lead    : 5-Column Lead (Cols 1..5) with ONE proper large 3-Column action photo (Cols 2..4,
                           5.6 cm tall, 6-line underflow) + Full-Height 40% Gray Box in LAST Col 5 ('मैच के बिंदु').
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


def prepare_cmyk_cropped_photo(src_name: str, dst_name: str, box_w_pt: float, box_h_pt: float, centering: tuple = (0.5, 0.32)) -> Path:
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
        im_rgb = im_rgb.crop((int(iw * 0.03), int(ih * 0.03), int(iw * 0.97), int(ih * 0.97)))
        cropped = ImageOps.fit(im_rgb, (target_w_px, target_h_px), method=Image.Resampling.LANCZOS, centering=centering)
        cmyk_im = cropped.convert("CMYK")
        cmyk_im.save(dst_p, "JPEG", quality=95, dpi=(300, 300))
    return dst_p


class AdityaBharatPage7Grid:
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

        self.masthead_y0 = self.print_y0
        self.masthead_h_cm = 1.5
        self.masthead_y1 = round(self.masthead_y0 + cm(self.masthead_h_cm), 2)

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


def place_red_subject_blurb(spread_idx: int, x0: float, y0: float, word_text: str, bw_cm: float = 1.82):
    bw = cm(bw_cm)
    bh = cm(1.22)
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
        {"command": "object.textWrap", "params": {"ids": [r_box["id"]], "mode": "boundingBox", "offset": [1.5, 0.0, 2.5, 3.2]}},
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
            "size": 20.0,
            "leading": {"kind": "points", "value": 20.5},
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
                "size": 18.5,
                "leading": {"kind": "points", "value": 19.0},
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
    cap_h: float = 22.0,
    centering: tuple = (0.5, 0.30),
):
    cap_y0 = round(cap_y1 - cap_h, 2)
    py1 = round(cap_y0 - 2.0, 2)
    img_path = prepare_cmyk_cropped_photo(src_photo_name, dst_photo_name, px1 - px0, py1 - py0, centering=centering)

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


EXTRA_SPORTS_SENTENCES = (
    "\nटीम प्रबंधन और मुख्य कोच के अनुसार आगामी अंतरराष्ट्रीय मुकाबलों को ध्यान में रखते हुए खिलाड़ियों की फिटनेस, वर्कलोड मैनेजमेंट "
    "और तकनीकी अभ्यास पर विशेष ध्यान दिया जा रहा है। खेल विशेषज्ञों का मानना है कि युवा प्रतिभाओं और अनुभवी खिलाड़ियों के इस संतुलित "
    "संयोजन से भारतीय दल विदेशी मैदानों पर भी अपना दबदबा कायम रखेगा। राष्ट्रीय खेल प्राधिकरण और संबंधित खेल संघों ने भी खिलाड़ियों को "
    "विश्वस्तरीय प्रशिक्षण सुविधाएं उपलब्ध कराने के लिए विशेष कार्ययोजना लागू की है।"
)


def fit_aditya_bharat_body(
    sid: int,
    city_name: str,
    agency_name: str,
    raw_body: str,
    first_line_indent: float = 8.0,
):
    city_part = f"{city_name.strip()} " if city_name else ""
    pipe_part = "| " if (city_name or agency_name) else ""
    agency_part = f"{agency_name.strip()}\n" if (city_name or agency_name) else ""
    byline_prefix = city_part + pipe_part + agency_part

    city_b = len(city_part.encode("utf-8"))
    pipe_b = len(pipe_part.encode("utf-8"))
    byline_total_b = len(byline_prefix.encode("utf-8"))

    def apply_style(body_str: str):
        full_txt = byline_prefix + body_str
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
                "firstLineIndent": first_line_indent,
                "leftIndent": 0.0,
                "rightIndent": 0.0,
                "spaceBefore": 0.0,
                "spaceAfter": 0.0,
                "hyphenate": False,
                "gridAlign": "allLines",
                "ruleBelow": {"on": False},
            }}},
        ]
        first_nl = body_str.find("\n")
        first_p_end = byline_total_b + (len(body_str[:first_nl].encode("utf-8")) if first_nl > 0 else len(body_str.encode("utf-8")))
        if first_p_end > byline_total_b:
            cmds.extend([
                {"command": "text.select", "params": {"story": sid, "anchor": byline_total_b, "focus": first_p_end}},
                {"command": "type.para", "params": {"attrs": {"firstLineIndent": 0.0}}},
            ])

        if byline_total_b > 1:
            cmds.extend([
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": byline_total_b - 1}},
                {"command": "type.char", "params": {"attrs": {
                    "fontFamily": "DB Hindi",
                    "fontStyle": "Bold",
                    "size": 11.0,
                    "leading": {"kind": "points", "value": 11.25},
                }}},
                {"command": "type.para", "params": {"attrs": {
                    "align": "left",
                    "firstLineIndent": 0.0,
                    "spaceBefore": 0.0,
                    "spaceAfter": 5.5,
                    "gridAlign": "none",
                    "ruleBelow": {
                        "on": True,
                        "weight": 0.85,
                        "color": "ClosingGray",
                        "tint": 1.0,
                        "columnWidth": True,
                        "offset": 3.0,
                    },
                }}},
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": city_b}},
                {"command": "type.char", "params": {"attrs": {"fill": "[Black]", "fillTint": 1.0}}},
                {"command": "text.select", "params": {"story": sid, "anchor": city_b, "focus": city_b + pipe_b}},
                {"command": "type.char", "params": {"attrs": {"fill": "FlyerCrimson", "fillTint": 1.0}}},
                {"command": "text.select", "params": {"story": sid, "anchor": city_b + pipe_b, "focus": byline_total_b - 1}},
                {"command": "type.char", "params": {"attrs": {"fill": "ClosingGray", "fillTint": 1.0}}},
            ])
        cmds.append({"command": "story.get", "params": {"story": sid}})
        return batch(cmds)[-1]

    ext_text = raw_body.strip()
    st = apply_style(ext_text)
    first_ext = True
    while st.get("overset") is None:
        ext_text = ext_text + (EXTRA_SPORTS_SENTENCES if first_ext else " " + EXTRA_SPORTS_SENTENCES.lstrip())
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
    head_align: str = "center",
    body_pt: float = 10.5,
    body_lead: float = 11.3,
    para_space: float = 2.2,
):
    head_prefix = f"{head_str.strip()}\n"
    head_b = len(head_prefix.encode("utf-8"))
    head_lead = round(head_pt + 1.0, 2)

    extra_bullets = (
        "\n• भारतीय तेज गेंदबाजों ने दोनों पारियों में कुल चौदह विकेट झटककर विपक्षी बल्लेबाजी की कमर तोड़ी।"
        "\n• विश्व टेस्ट चैंपियनशिप की अंक तालिका में भारत अड़सठ प्रतिशत अंकों के साथ शीर्ष स्थान पर मजबूत।"
        "\n• अगली बॉर्डर-गावस्कर टेस्ट सीरीज के लिए अठारह सदस्यीय भारतीय टीम की घोषणा इसी सप्ताह।"
    )

    def style_box(b_str: str):
        full_txt = head_prefix + b_str
        cmds = [
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
            {"command": "text.delete", "params": {}},
            {"command": "text.insert", "params": {"text": full_txt}},
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
                "leading": {"kind": "points", "value": head_lead},
                "fill": "[Black]",
                "fillTint": 1.0,
            }}},
            {"command": "type.para", "params": {"attrs": {
                "align": head_align,
                "spaceAfter": 4.2,
                "ruleBelow": {
                    "on": True,
                    "weight": 1.0,
                    "color": "[Black]",
                    "tint": 0.75,
                    "columnWidth": True,
                    "offset": 2.2,
                },
            }}},
            {"command": "story.get", "params": {"story": sid}},
        ]
        return batch(cmds)[-1]

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


def place_multi_col_story(
    grid: AdityaBharatPage7Grid,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    cols: int,
    headline: str,
    city: str,
    agency: str,
    blurb_word: str,
    body: str,
    target_lines: int = 2,
    hi_pt: float = 38.0,
    lo_pt: float = 30.0,
):
    _, _, h_pt, hh = fit_aditya_bharat_headline(
        0, x0, y0, x1,
        raw_text=headline,
        target_lines=target_lines,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=hi_pt,
        lo_pt=lo_pt,
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
        "columns": cols,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    if blurb_word:
        place_red_subject_blurb(0, x0, round(by0 + cm(1.65), 2), blurb_word)
    fit_aditya_bharat_body(r_b["story"], city, agency, body)
    return h_pt


def build_aditya_bharat_page7_sports():
    t0 = time.perf_counter()
    connect_page_designer()
    grid = AdityaBharatPage7Grid()

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
            "title": "आदित्य भारत — पेज 07 खेल संसार (34x53 सेमी | 12 खबरें + 1 बड़ा एक्शन फोटो)",
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
    # ==========================================================================
    mh_x0, mh_y0, mh_x1, mh_y1 = grid.print_x0, grid.masthead_y0, grid.print_x1, grid.masthead_y1

    sec_w = cm(4.4)
    sec_y0 = round(mh_y0 + mm(1.0), 2)
    sec_y1 = round(mh_y1 - mm(1.8), 2)
    r_mh_sec = cmd("frame.create", {
        "spread": 0,
        "rect": [mh_x0, sec_y0, round(mh_x0 + sec_w, 2), sec_y1],
        "content": "text",
        "text": "खेल संसार",
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
        "text": "07",
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
    # TOP ZONE (STORIES 1 TO 6, y = 2.85 .. 27.60 cm, Height = 24.75 cm):
    #   - Left 5 Cols (Cols 1..5):
    #       * Story 1 (y = 2.85 .. 19.65 cm): 5-Col Main Sports Lead at Top
    #         with ONE PROPER LARGE 3-COL ACTION PHOTO (Cols 2..4) + Gray Box in Col 5!
    #       * Story 2 (Cols 1..3) + Story 3 (Cols 4..5) below Lead (y = 20.00 .. 27.60 cm)
    #   - Right 3 Cols (Cols 6..8):
    #       * Story 4 (Top Illustrated 3-Col Story, y = 2.85 .. 13.05 cm)
    #       * Story 5 (Mid 3-Col Story, y = 13.40 .. 20.30 cm)
    #       * Story 6 (Lower 3-Col Story, y = 20.65 .. 27.60 cm)
    # ==========================================================================
    top_y0 = round(mh_y1 + mm(3.5), 2)
    top_zone_y1 = snap_frame_bottom_to_baseline(round(top_y0 + cm(24.75), 2))
    lead_y1 = snap_frame_bottom_to_baseline(round(top_y0 + cm(16.8), 2))

    # --- Story 1: Top-Left 5-Column Main Sports Lead (Cols 1..5) ---
    lead_x0 = grid.col_x0(1)
    lead_x1 = grid.col_x1(1, 5)
    lead_cur_y = top_y0

    lead_head_txt = "रोहित और बुमराह के दम पर भारत ने जीती ऐतिहासिक टेस्ट सीरीज"
    _, _, s1_pt, lead_hh = fit_aditya_bharat_headline(
        0, lead_x0, lead_cur_y, lead_x1,
        raw_text=lead_head_txt,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=58.0,
        lo_pt=44.0,
        align="left",
    )
    lead_cur_y = round(lead_cur_y + lead_hh + 0.5, 2)

    lead_sub_txt = "विश्व टेस्ट चैंपियनशिप फाइनल की राह आसान : घरेलू मैदान पर लगातार अठारहवीं टेस्ट श्रृंखला जीतकर बनाया विश्व रिकॉर्ड"
    _, _, _, lead_sub_h = fit_aditya_bharat_headline(
        0, lead_x0, lead_cur_y, lead_x1,
        raw_text=lead_sub_txt,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=15.5,
        lo_pt=12.0,
        align="left",
    )
    lead_body_y0 = round(lead_cur_y + lead_sub_h + 1.5, 2)
    lead_body_y1 = lead_y1

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
    place_red_subject_blurb(0, grid.col_x0(1), round(lead_body_y0 + cm(1.9), 2), "विजय")

    # ONE PROPER LARGE SPORTS ACTION PHOTO: 3 Columns Wide (Cols 2..4) x ~5.8 cm Tall with 7-line underflow!
    l_cap_y1 = round(snap_underflow_top(lead_body_y1, num_underflow_lines=7) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(2),
        lead_body_y0,
        grid.col_x1(2, 3),
        l_cap_y1,
        "p7_sports_839305_print.jpg",
        "ab_p7_lead_action_3col_cmyk.jpg",
        "निर्णायक टेस्ट मुकाबले में शानदार जीत के बाद जश्न मनाते भारतीय खिलाड़ी और दर्शक। — फाइल फोटो",
        cap_h=22.0,
        centering=(0.5, 0.25),
    )
    lead_body_txt = (
        "कप्तान रोहित शर्मा के आक्रामक शतक और जसप्रीत बुमराह व रविचंद्रन अश्विन की घातक गेंदबाजी के दम पर भारतीय क्रिकेट टीम ने निर्णायक टेस्ट मैच में "
        "शानदार जीत दर्ज करते हुए श्रृंखला तीन-शून्य से अपने नाम कर ली। इस ऐतिहासिक जीत के साथ ही भारत ने विश्व टेस्ट चैंपियनशिप की अंक तालिका में "
        "शीर्ष स्थान पर अपनी स्थिति और मजबूत कर ली है।\n"
        "चौथे दिन के खेल में भारतीय गेंदबाजों ने लंच से पहले ही विपक्षी टीम के शेष सात विकेट झटककर मैच को एकतरफा बना दिया। जसप्रीत बुमराह को "
        "उनकी सटीक यॉर्कर और स्विंग गेंदबाजी के लिए प्लेयर ऑफ द मैच चुना गया।"
    )
    fit_aditya_bharat_body(r_lead_body["story"], "मुंबई", "विशेष संवाददाता", lead_body_txt)

    # Col 5 (LAST Column of the 5-Column Lead = Full-Height 40% Gray Score/Highlights Box, 100% filled!)
    inset_pt = mm(2.5)
    box5_x0 = grid.col_x0(5)
    box5_x1 = grid.col_x1(5, 1)
    r_lbox5 = cmd("frame.create", {
        "spread": 0,
        "rect": [box5_x0, lead_body_y0, box5_x1, lead_body_y1],
        "content": "text",
        "text": "",
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_lbox5["id"]], "swatch": "[Black]", "tint": 0.15}},
        {"command": "object.stroke", "params": {"ids": [r_lbox5["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 0.55}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_lbox5["id"]],
            "columns": 1,
            "inset": [inset_pt, inset_pt, inset_pt, inset_pt],
            "verticalJustification": "top",
        }},
    ])
    lbox5_bullets = (
        "• भारत पहली पारी : 448/7 घोषित (रोहित 118, पंत 86, गिल 74 रन)।\n"
        "• जसप्रीत बुमराह ने मैच में कुल नौ विकेट और अश्विन ने सात विकेट झटके।\n"
        "• घरेलू धरती पर भारत की यह लगातार अठारहवीं टेस्ट सीरीज विजय।\n"
        "• डब्ल्यूटीसी अंक तालिका में भारत 68.52 प्रतिशत अंकों के साथ नंबर एक पर।"
    )
    fit_box_completely(
        r_lbox5["story"],
        head_str="मैच के बिंदु",
        raw_bullets=lbox5_bullets,
        head_pt=16.0,
        head_align="center",
        body_pt=10.5,
        body_lead=11.3,
        para_space=2.2,
    )

    l_sub_sep_y = round(lead_y1 + mm(1.75), 2)
    r_lsub_sep = cmd("line.create", {"spread": 0, "a": [lead_x0, l_sub_sep_y], "b": [lead_x1, l_sub_sep_y]})
    cmd("object.stroke", {"ids": [r_lsub_sep["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 0.9})

    # --- Stories 2 & 3: Below Main Lead in Cols 1..5 (3-Col + 2-Col Split) ---
    l_bot_y0 = round(l_sub_sep_y + mm(1.75), 2)
    l_bot_y1 = top_zone_y1

    s2_pt = place_multi_col_story(
        grid, grid.col_x0(1), grid.col_x1(1, 3), l_bot_y0, l_bot_y1, cols=3,
        headline="एशियाई चैंपियंस ट्रॉफी में भारतीय हॉकी टीम की लगातार चौथी जीत",
        city="राजगीर",
        agency="खेल संवाददाता",
        blurb_word="हॉकी",
        body=(
            "पेनल्टी कॉर्नर विशेषज्ञ हरमनप्रीत सिंह के दो गोलों की मदद से भारतीय हॉकी टीम ने एशियाई चैंपियंस ट्रॉफी के मुकाबले में दक्षिण कोरिया को "
            "चार-एक से हराकर सेमीफाइनल में अपना स्थान पक्का कर लिया है।"
        ),
        hi_pt=36.0,
        lo_pt=30.0,
    )

    s3_pt = place_multi_col_story(
        grid, grid.col_x0(4), grid.col_x1(4, 2), l_bot_y0, l_bot_y1, cols=2,
        headline="विश्व शतरंज में डी गुकेश ने बनाई एकल बढ़त",
        city="चेन्नई",
        agency="एजेंसी",
        blurb_word="शतरंज",
        body=(
            "भारतीय ग्रैंडमास्टर डी गुकेश ने विश्व शतरंज चैंपियनशिप की छठी बाजी में शानदार रणनीतिक कौशल दिखाते हुए अपने प्रतिद्वंद्वी को पराजित कर "
            "अंक तालिका में महत्वपूर्ण एकल बढ़त हासिल कर ली है।"
        ),
        hi_pt=35.0,
        lo_pt=30.0,
    )

    # --- Stories 4, 5, 6: Right 3-Column Vertical Wing (Cols 6..8, 3 Stacked Stories) ---
    r3_x0 = grid.col_x0(6)
    r3_x1 = grid.col_x1(6, 3)
    r_s4_y1 = snap_frame_bottom_to_baseline(round(top_y0 + cm(10.2), 2))

    # Story 4: Top Illustrated 3-Col Story in Cols 6..8
    s4_head = "ऑस्ट्रेलिया टेस्ट सीरीज के लिए टीम इंडिया का विशेष शिविर शुरू"
    _, _, s4_pt, s4_hh = fit_aditya_bharat_headline(
        0, r3_x0, top_y0, r3_x1,
        raw_text=s4_head,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=36.0,
        lo_pt=30.0,
        align="left",
    )
    s4_by0 = round(top_y0 + s4_hh + 2.0, 2)
    r_s4_b = cmd("frame.create", {
        "spread": 0,
        "rect": [r3_x0, s4_by0, r3_x1, r_s4_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_s4_b["id"]],
        "columns": 3,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, r3_x0, round(s4_by0 + cm(1.6), 2), "क्रिकेट")

    s4_cap_y1 = round(snap_underflow_top(r_s4_y1, num_underflow_lines=5) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(7),
        s4_by0,
        grid.col_x1(7, 2),
        s4_cap_y1,
        "p8_wiki_rohit_sharma_horiz_print.jpg",
        "ab_p7_flyer_rohit_cmyk.jpg",
        "अभ्यास सत्र के दौरान भारतीय कप्तान रोहित शर्मा। — फाइल फोटो",
        cap_h=22.0,
    )
    s4_body = (
        "आगामी बॉर्डर-गावस्कर ट्रॉफी और चैंपियंस ट्रॉफी के लिए भारतीय क्रिकेट कंट्रोल बोर्ड ने विशेष तैयारी शिविर शुरू कर दिया है। कप्तान रोहित शर्मा "
        "और कोचिंग स्टाफ ने तेज उछाल वाली पिचों पर बल्लेबाजी तथा नई गेंद से स्विंग गेंदबाजी के लिए युवा खिलाड़ियों के साथ विशेष सत्र आयोजित किया।"
    )
    fit_aditya_bharat_body(r_s4_b["story"], "मुंबई", "खेल ब्यूरो", s4_body)

    r3_sep1_y = round(r_s4_y1 + mm(1.75), 2)
    r_r3_sep1 = cmd("line.create", {"spread": 0, "a": [r3_x0, r3_sep1_y], "b": [r3_x1, r3_sep1_y]})
    cmd("object.stroke", {"ids": [r_r3_sep1["id"]], "swatch": "[Black]", "weight": 0.65, "tint": 0.85})

    # Story 5: Mid 3-Col Story in Cols 6..8
    r_s5_y0 = round(r3_sep1_y + mm(1.75), 2)
    r_s5_y1 = snap_frame_bottom_to_baseline(round(r_s5_y0 + cm(6.8), 2))
    s5_pt = place_multi_col_story(
        grid, r3_x0, r3_x1, r_s5_y0, r_s5_y1, cols=3,
        headline="डायमंड लीग के नए सीजन के लिए नीरज चोपड़ा ने शुरू की तैयारी",
        city="पटियाला",
        agency="एजेंसी",
        blurb_word="भालाफेंक",
        body=(
            "ओलंपिक पदक विजेता स्टार भालाफेंक खिलाड़ी नीरज चोपड़ा ने आगामी विश्व एथलेटिक्स चैंपियनशिप और डायमंड लीग सीजन में नब्बे मीटर का "
            "लक्ष्य हासिल करने के लिए यूरोपीय कोच के साथ विशेष बायो-मैकेनिक्स प्रशिक्षण शुरू कर दिया है।"
        ),
        hi_pt=36.0,
        lo_pt=30.0,
    )

    r3_sep2_y = round(r_s5_y1 + mm(1.75), 2)
    r_r3_sep2 = cmd("line.create", {"spread": 0, "a": [r3_x0, r3_sep2_y], "b": [r3_x1, r3_sep2_y]})
    cmd("object.stroke", {"ids": [r_r3_sep2["id"]], "swatch": "[Black]", "weight": 0.65, "tint": 0.85})

    # Story 6: Lower 3-Col Story in Cols 6..8
    r_s6_y0 = round(r3_sep2_y + mm(1.75), 2)
    s6_pt = place_multi_col_story(
        grid, r3_x0, r3_x1, r_s6_y0, top_zone_y1, cols=3,
        headline="महिला क्रिकेट सीरीज के लिए हरमनप्रीत की टीम तैयार",
        city="मुंबई",
        agency="एजेंसी",
        blurb_word="महिला",
        body=(
            "भारतीय महिला क्रिकेट टीम की कप्तान हरमनप्रीत कौर और उपकप्तान स्मृति मंधाना ने आगामी घरेलू एकदिवसीय तथा टी-ट्वेंटी श्रृंखला में "
            "युवा महिला स्पिनरों को मैच जिताऊ एक्स-फैक्टर बताया है।"
        ),
        hi_pt=36.0,
        lo_pt=30.0,
    )

    sep2_y = round(top_zone_y1 + mm(1.75), 2)
    r_sep2 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep2_y], "b": [grid.print_x1, sep2_y]})
    cmd("object.stroke", {"ids": [r_sep2["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # BAND 3 (STORIES 7, 8, 9): 2 + 3 + 3 INTERLOCKED SPLIT (y = 27.95 .. 36.65 cm, Height = 8.7 cm)
    # ==========================================================================
    b3_y0 = round(sep2_y + mm(1.75), 2)
    b3_y1 = snap_frame_bottom_to_baseline(round(b3_y0 + cm(8.7), 2))

    # --- Story 7: Cols 1..2 Tennis Story ---
    s7_pt = place_multi_col_story(
        grid, grid.col_x0(1), grid.col_x1(1, 2), b3_y0, b3_y1, cols=2,
        headline="डेविस कप के लिए भारतीय टीम घोषित",
        city="नई दिल्ली",
        agency="ब्यूरो",
        blurb_word="टेनिस",
        body=(
            "अखिल भारतीय टेनिस संघ ने आगामी डेविस कप विश्व ग्रुप मुकाबले के लिए सुमित नागल और रोहन बोपन्ना की अगुवाई में पांच सदस्यीय भारतीय "
            "टीम की घोषणा कर दी है।"
        ),
        hi_pt=35.0,
        lo_pt=30.0,
    )

    # --- Story 8: Cols 3..5 Illustrated Athletics/Kabaddi Story ---
    s8_x0 = grid.col_x0(3)
    s8_x1 = grid.col_x1(3, 3)
    s8_head = "राष्ट्रीय खेलों और प्रो-कबड्डी में युवा खिलाड़ियों का जलवा"
    _, _, s8_pt, s8_hh = fit_aditya_bharat_headline(
        0, s8_x0, b3_y0, s8_x1,
        raw_text=s8_head,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=36.0,
        lo_pt=30.0,
        align="left",
    )
    s8_by0 = round(b3_y0 + s8_hh + 2.0, 2)
    r_s8_b = cmd("frame.create", {
        "spread": 0,
        "rect": [s8_x0, s8_by0, s8_x1, b3_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_s8_b["id"]],
        "columns": 3,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, s8_x0, round(s8_by0 + cm(1.6), 2), "कबड्डी")

    s8_cap_y1 = round(snap_underflow_top(b3_y1, num_underflow_lines=5) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(4),
        s8_by0,
        grid.col_x1(4, 2),
        s8_cap_y1,
        "p8_hockey_834679_print.jpg",
        "ab_p7_s6_action_cmyk.jpg",
        "मैदान पर अंक जुटाने के लिए संघर्ष करते युवा खिलाड़ी। — फाइल फोटो",
        cap_h=22.0,
    )
    s8_body = (
        "प्रो-कबड्डी लीग के ग्यारहवें सीजन और राष्ट्रीय खेल प्रतियोगिताओं में छोटे शहरों से निकले युवा रेडर्स तथा डिफेंडरों ने अपने दमदार खेल से "
        "चयनकर्ताओं का ध्यान खींचा है। पुनेरी पलटन और जयपुर पिंक पैंथर्स ने अपने-अपने मुकाबले जीतकर शीर्ष चार में जगह बनाई।"
    )
    fit_aditya_bharat_body(r_s8_b["story"], "हैदराबाद", "एजेंसी", s8_body)

    # --- Story 9: Cols 6..8 Badminton Story ---
    s9_pt = place_multi_col_story(
        grid, grid.col_x0(6), grid.col_x1(6, 3), b3_y0, b3_y1, cols=3,
        headline="बैडमिंटन ओपन में लक्ष्य सेन और सिंधु क्वार्टर फाइनल में पहुंचे",
        city="नई दिल्ली",
        agency="एजेंसी",
        blurb_word="बैडमिंटन",
        body=(
            "भारत के स्टार शटलर लक्ष्य सेन और दो बार की ओलंपिक पदक विजेता पीवी सिंधु ने सीधे गेमों में अपने मुकाबले जीतकर बीडब्ल्यूएफ सुपर-750 "
            "बैडमिंटन टूर्नामेंट के क्वार्टर फाइनल में प्रवेश कर लिया है। युगल वर्ग में सात्विक-चिराग की जोड़ी भी जीती।"
        ),
        hi_pt=36.0,
        lo_pt=30.0,
    )

    sep3_y = round(b3_y1 + mm(1.75), 2)
    r_sep3 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep3_y], "b": [grid.print_x1, sep3_y]})
    cmd("object.stroke", {"ids": [r_sep3["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # BAND 4 (STORIES 10 & 11): 4 + 4 SPLIT (y = 37.00 .. 43.70 cm, Height = 6.7 cm)
    # ==========================================================================
    b4_y0 = round(sep3_y + mm(1.75), 2)
    b4_y1 = snap_frame_bottom_to_baseline(round(b4_y0 + cm(6.7), 2))

    # --- Story 10: Cols 1..4 Football / ISL Story ---
    s10_pt = place_multi_col_story(
        grid, grid.col_x0(1), grid.col_x1(1, 4), b4_y0, b4_y1, cols=4,
        headline="सुपर लीग में मोहन बागान व मुंबई की जीत",
        city="कोलकाता",
        agency="खेल डेस्क",
        blurb_word="फुटबॉल",
        body=(
            "इंडियन सुपर लीग फुटबॉल टूर्नामेंट में गत विजेता मोहन बागान सुपर जायंट और मुंबई सिटी एफसी ने अपने-अपने घरेलू मुकाबलों में "
            "शानदार जीत दर्ज कर अंक तालिका के शीर्ष दो स्थानों पर कब्जा जमा लिया है।"
        ),
        target_lines=1,
        hi_pt=38.0,
        lo_pt=30.0,
    )

    # --- Story 11: Cols 5..8 Shooting World Cup Story ---
    s11_pt = place_multi_col_story(
        grid, grid.col_x0(5), grid.col_x1(5, 4), b4_y0, b4_y1, cols=4,
        headline="निशानेबाजी विश्व कप में मनु भाकर को स्वर्ण",
        city="नई दिल्ली",
        agency="एजेंसी",
        blurb_word="शूटिंग",
        body=(
            "अंतरराष्ट्रीय निशानेबाजी महासंघ विश्व कप फाइनल में ओलंपिक पदक विजेता मनु भाकर और युवा निशानेबाजों ने दस मीटर एयर पिस्टल तथा "
            "राइफल स्पर्धाओं में तीन स्वर्ण समेत कुल छह पदक जीतकर भारत को पदक तालिका में शीर्ष पर पहुंचा दिया।"
        ),
        target_lines=1,
        hi_pt=38.0,
        lo_pt=30.0,
    )

    sep4_y = round(b4_y1 + mm(1.75), 2)
    r_sep4 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep4_y], "b": [grid.print_x1, sep4_y]})
    cmd("object.stroke", {"ids": [r_sep4["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 5 (STORY 12 + SPORTS DIARY BOX): LEFT 2-COL SPORTS DIARY BOX (Cols 1..2)
    #   + RIGHT 6-COL GRAND RANJI TROPHY ANCHOR (Cols 3..8)
    # ==========================================================================
    bot_y0 = round(sep4_y + mm(1.75), 2)
    bot_y1 = snap_frame_bottom_to_baseline(grid.print_y1)

    # --- Left 2-Column Sports Digest Box (Cols 1..2, 100% filled) ---
    sd_x0 = grid.col_x0(1)
    sd_x1 = grid.col_x1(1, 2)
    r_sd_box = cmd("frame.create", {
        "spread": 0,
        "rect": [sd_x0, bot_y0, sd_x1, bot_y1],
        "content": "text",
        "text": "",
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_sd_box["id"]], "swatch": "[Black]", "tint": 0.14}},
        {"command": "object.stroke", "params": {"ids": [r_sd_box["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 0.65}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_sd_box["id"]],
            "columns": 1,
            "inset": [inset_pt, inset_pt, inset_pt, inset_pt],
            "verticalJustification": "top",
        }},
    ])
    sd_bullets = (
        "• विश्व तीरंदाजी में भारतीय महिला रिकर्व टीम ने कोरिया को हराकर स्वर्ण जीता।\n"
        "• एशियाई अंडर-23 कुश्ती चैंपियनशिप में अमन सहरावत और अंतिम पंघाल को स्वर्ण पदक।\n"
        "• खेलो इंडिया यूथ गेम्स के लिए इंदौर और भोपाल में चार नए सिंथेटिक ट्रैक तैयार।\n"
        "• राष्ट्रीय तैराकी प्रतियोगिता में कर्नाटक और महाराष्ट्र के तैराकों ने बनाए तीन नए रिकॉर्ड।"
    )
    fit_box_completely(
        r_sd_box["story"],
        head_str="खेल डायरी : पदक और परिणाम",
        raw_bullets=sd_bullets,
        head_pt=16.5,
        head_align="center",
        body_pt=10.5,
        body_lead=11.3,
        para_space=2.2,
    )

    # --- Story 12: Right 6-Column Bottom Sports Anchor (Cols 3..8) ---
    anc_x0 = grid.col_x0(3)
    anc_x1 = grid.col_x1(3, 6)
    anc_cur_y = bot_y0

    anchor_head = "रणजी ट्रॉफी में मध्यप्रदेश और मुंबई की शानदार जीत"
    _, _, s12_pt, anc_hh = fit_aditya_bharat_headline(
        0, anc_x0, anc_cur_y, anc_x1,
        raw_text=anchor_head,
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=50.0,
        lo_pt=40.0,
        align="center",
    )
    anc_cur_y = round(bot_y0 + anc_hh + 1.0, 2)

    anchor_sub = "होलकर स्टेडियम में मध्यप्रदेश के बल्लेबाजों का दबदबा : पारी और पैंतीस रनों से जीता मुकाबला"
    _, _, _, anc_sub_h = fit_aditya_bharat_headline(
        0, anc_x0, anc_cur_y, anc_x1,
        raw_text=anchor_sub,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=15.0,
        lo_pt=12.0,
        align="center",
    )
    anc_body_y0 = round(anc_cur_y + anc_sub_h + 1.0, 2)
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
    place_red_subject_blurb(0, grid.col_x0(3), round(anc_body_y0 + cm(1.55), 2), "रणजी")

    acap_y1 = round(snap_underflow_top(anc_body_y1, num_underflow_lines=5) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(5),
        anc_body_y0,
        grid.col_x1(5, 2),
        acap_y1,
        "p8_stadium_834769_print.jpg",
        "ab_p7_anchor_stadium_cmyk.jpg",
        "रणजी ट्रॉफी मुकाबले के दौरान स्टेडियम का दृश्य। — फाइल फोटो",
        cap_h=22.0,
    )
    anc_body = (
        "रणजी ट्रॉफी एलीट ग्रुप मुकाबले में मध्यप्रदेश ने इंदौर के होलकर स्टेडियम में शानदार प्रदर्शन करते हुए विपक्षी टीम को पारी और पैंतीस रनों से "
        "पराजित कर पूरे सात अंक हासिल किए। उधर मुंबई ने भी अपने घरेलू मैदान पर अजिंक्य रहाणे और श्रेयस अय्यर के शतकों की बदौलत बड़ी जीत दर्ज की।"
    )
    fit_aditya_bharat_body(r_anc_body["story"], "इंदौर", "खेल संवाददाता", anc_body)

    cmd("edit.deselectAll")
    cmd("view.fitPage", {})

    out_pd = VAULT_DIR / "Aditya_Bharat_Page_07_Khel_Sansar_34x53.pagedesigner"
    out_png = VAULT_DIR / "Aditya_Bharat_Page_07_Khel_Sansar_34x53.png"
    out_pdf = VAULT_DIR / "Aditya_Bharat_Page_07_Khel_Sansar_CMYK_34x53.pdf"
    rpc("app.save", {"path": str(out_pd)})
    rpc("app.export", {"path": str(out_png), "page": 0, "scale": 1.5})
    try:
        rpc("engine.execute", {"command": "file.exportPdf", "params": {"path": str(out_pdf)}})
    except Exception:
        pass

    artifact_png = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\8707c72d-58b0-4715-a099-3efffcd57514\aditya_bharat_page_07_khel_sansar_34x53.png")
    artifact_png.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_png, artifact_png)

    all_pts = [s1_pt, s2_pt, s3_pt, s4_pt, s5_pt, s6_pt, s7_pt, s8_pt, s9_pt, s10_pt, s11_pt, s12_pt]
    print(
        f"=== ADITYA BHARAT PAGE 07 (KHEL SANSAR - 12 STORIES + 1 PROPER 3-COL ACTION PHOTO) BUILT IN {time.perf_counter()-t0:.2f}s ===\n"
        f"    12 Story Headline Pts: {all_pts} (Min={min(all_pts)}pt >= 30.0pt!)"
    )


if __name__ == "__main__":
    build_aditya_bharat_page7_sports()
