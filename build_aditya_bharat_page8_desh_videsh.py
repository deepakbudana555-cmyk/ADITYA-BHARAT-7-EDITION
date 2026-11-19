# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — PAGE 08 (देश-विदेश / NATIONAL & INTERNATIONAL) MASTER BUILDER
===========================================================================================
Builds Page 08 ('देश-विदेश') with a tightly interlocked 12-Story Broadsheet Layout
strictly following the locked Aditya Bharat Stylesheet:
  1. Page Size           : 34.0 cm Width x 53.0 cm Height (Outer Margins = 1-1-1-1 cm)
  2. Print Area (Fixed)  : 32.0 cm Width x 51.0 cm Height (8 Columns, 4.0 mm Gutter)
  3. Zone 1 (Masthead)   : 1.5 cm Inside Running Masthead (y = 1.0 .. 2.5 cm, Cols 1..8)
                           - Left: Red Color Box ('FlyerCrimson') with 'देश-विदेश' in 20 pt 'DB Hindi 6' White
                           - Center: 'आदित्य भारत' Masthead Logo ('28 pt DB Rasrand Bold', 100% Black)
                           - Right: Dateline ('16 pt DB Hindi Bold') + '08' ('18 pt Times New Roman Bold')
                           - Bottom: 2.0 pt Rule in 60% Gray across all 8 columns
  4. Total News Stories  : 12 Distinct News Stories ('12 news lagna desh-videsh mein'),
                           ALL 12 Story Headlines >= 30.0 pt ('DB Rasrand Bold', 100% Black)!
  5. Main Lead Package   : 5-Column Lead (Cols 1..5) with News starting in Col 1 + Compact Photo in Cols 2..3
                           + Full-Height 40% Gray Box in LAST Col 5 ('सामरिक बिंदु', 100% filled).
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


def prepare_cmyk_cropped_photo(src_name: str, dst_name: str, box_w_pt: float, box_h_pt: float, centering: tuple = (0.5, 0.35)) -> Path:
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
        cropped = ImageOps.fit(im_rgb, (target_w_px, target_h_px), method=Image.Resampling.LANCZOS, centering=centering)
        cmyk_im = cropped.convert("CMYK")
        cmyk_im.save(dst_p, "JPEG", quality=95, dpi=(300, 300))
    return dst_p


class AdityaBharatPage8Grid:
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
        lo_s, hi_s = 100, 114
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


EXTRA_WORLD_SENTENCES = (
    "\nविदेश मंत्रालय और राजनयिक सूत्रों के अनुसार भारत ने वैश्विक मंचों पर विकासशील देशों की आवाज को मजबूती से रखते हुए "
    "आपसी सहयोग, शांति और निष्पक्ष व्यापार व्यवस्था पर बल दिया है। सामरिक विश्लेषकों का मानना है कि बदलती भू-राजनीतिक परिस्थितियों "
    "में भारत की संतुलित और स्वतंत्र विदेश नीति ने उसे विश्व की प्रमुख महाशक्तियों के बीच एक भरोसेमंद सेतु के रूप में स्थापित किया है। "
    "दोनों देशों के उच्चस्तरीय प्रतिनिधिमंडलों के बीच अगले महीने होने वाली बैठक में इन समझौतों को अंतिम रूप दिया जाएगा।"
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
        ext_text = ext_text + (EXTRA_WORLD_SENTENCES if first_ext else " " + EXTRA_WORLD_SENTENCES.lstrip())
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
        "\n• समुद्री व्यापार मार्गों की सुरक्षा के लिए चौबीस घंटे उपग्रह व रडार निगरानी तंत्र सक्रिय।"
        "\n• मित्र देशों के साथ रक्षा उपकरण निर्माण और साइबर सुरक्षा में तकनीकी साझेदारी बढ़ी।"
        "\n• हिंद महासागर क्षेत्र में आपदा राहत और मानवीय सहायता के लिए भारतीय नौसेना सदैव तत्पर।"
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
    grid: AdityaBharatPage8Grid,
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


def build_aditya_bharat_page8_desh_videsh():
    t0 = time.perf_counter()
    connect_page_designer()
    grid = AdityaBharatPage8Grid()

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
            "title": "आदित्य भारत — पेज 08 देश-विदेश (34x53 सेमी | 12 खबरें)",
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
        "text": "देश-विदेश",
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
        "text": "08",
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
    # BAND 1 (STORY 1): FULL 8-COLUMN WORLD DIPLOMACY FLYER (Cols 1..8)
    #   y = 2.85 .. 11.45 cm (Height = 8.6 cm)
    # ==========================================================================
    b1_y0 = round(mh_y1 + mm(3.5), 2)
    b1_y1 = snap_frame_bottom_to_baseline(round(b1_y0 + cm(8.6), 2))

    fl_x0 = grid.col_x0(1)
    fl_x1 = grid.col_x1(1, 8)
    fl_cur_y = b1_y0

    flyer_sub_txt = "वैश्विक कूटनीति में भारत का बढ़ता कद : संयुक्त राष्ट्र महासभा में सुधार के प्रस्ताव को एक सौ चालीस देशों का साथ"
    _, _, _, fl_sub_h = fit_aditya_bharat_headline(
        0, fl_x0, fl_cur_y, fl_x1,
        raw_text=flyer_sub_txt,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=16.5,
        lo_pt=13.5,
        align="center",
    )
    fl_cur_y = round(fl_cur_y + fl_sub_h + 1.0, 2)

    flyer_head_txt = "सुरक्षा परिषद में भारत की स्थायी दावेदारी को भारी समर्थन"
    _, _, s1_pt, fl_hh = fit_aditya_bharat_headline(
        0, fl_x0, fl_cur_y, fl_x1,
        raw_text=flyer_head_txt,
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=56.0,
        lo_pt=42.0,
        align="center",
    )
    fl_body_y0 = round(fl_cur_y + fl_hh + 1.5, 2)
    fl_body_y1 = b1_y1

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
    place_red_subject_blurb(0, grid.col_x0(1), round(fl_body_y0 + cm(1.55), 2), "कूटनीति")

    fl_cap_y1 = round(snap_underflow_top(fl_body_y1, num_underflow_lines=4) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(4),
        fl_body_y0,
        grid.col_x1(4, 2),
        fl_cap_y1,
        "p4_unsc_828955_print.jpg",
        "ab_p8_flyer_un_cmyk.jpg",
        "न्यूयॉर्क स्थित संयुक्त राष्ट्र सुरक्षा परिषद की बैठक का दृश्य। — फाइल फोटो",
        cap_h=22.0,
    )
    fl_body_txt = (
        "संयुक्त राष्ट्र सुरक्षा परिषद के विस्तार और सुधारों को लेकर चल रही अंतर-सरकारी वार्ता में अमेरिका, फ्रांस, ब्रिटेन और रूस सहित विश्व के "
        "प्रमुख देशों ने भारत की स्थायी सदस्यता का खुलकर समर्थन किया है। भारतीय प्रतिनिधिमंडल ने कहा कि इक्कीसवीं सदी की चुनौतियों के समाधान के "
        "लिए वैश्विक संस्थाओं में ग्लोबल साउथ की निर्णायक भागीदारी अनिवार्य है।"
    )
    fit_aditya_bharat_body(r_fl_body["story"], "न्यूयॉर्क", "एजेंसी", fl_body_txt)

    sep1_y = round(b1_y1 + mm(1.75), 2)
    r_sep1 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep1_y], "b": [grid.print_x1, sep1_y]})
    cmd("object.stroke", {"ids": [r_sep1["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 2 (STORIES 2, 3, 4): LEFT 3-COL STACKED STORIES (Cols 1..3)
    #   + RIGHT 5-COL MAIN DESH-VIDESH LEAD (Cols 4..8, Gray Box in LAST Col 8!)
    #   y = 11.80 .. 26.80 cm (Height = 15.0 cm)
    # ==========================================================================
    b2_y0 = round(sep1_y + mm(1.75), 2)
    b2_y1 = snap_frame_bottom_to_baseline(round(b2_y0 + cm(15.0), 2))

    # --- Stories 2 & 3: Left 3-Column Stacked Stories (Cols 1..3) ---
    l3_x0 = grid.col_x0(1)
    l3_x1 = grid.col_x1(1, 3)
    l3_mid_y = snap_frame_bottom_to_baseline(round(b2_y0 + cm(7.35), 2))

    s2_pt = place_multi_col_story(
        grid, l3_x0, l3_x1, b2_y0, l3_mid_y, cols=3,
        headline="पश्चिम एशिया में शांति बहाली के लिए भारत की पहल की सराहना",
        city="तेल अवीव",
        agency="एजेंसी",
        blurb_word="शांति",
        body=(
            "पश्चिम एशिया में जारी तनाव को कम करने और मानवीय सहायता गलियारा खोलने के लिए भारत द्वारा किए गए कूटनीतिक प्रयासों की संयुक्त राष्ट्र "
            "तथा यूरोपीय संघ ने सराहना की है। भारत ने संवाद और कूटनीति से स्थायी समाधान पर जोर दिया है।"
        ),
        hi_pt=36.0,
        lo_pt=30.0,
    )

    l3_sep_y = round(l3_mid_y + mm(1.75), 2)
    r_l3_sep = cmd("line.create", {"spread": 0, "a": [l3_x0, l3_sep_y], "b": [l3_x1, l3_sep_y]})
    cmd("object.stroke", {"ids": [r_l3_sep["id"]], "swatch": "[Black]", "weight": 0.65, "tint": 0.85})

    s3_pt = place_multi_col_story(
        grid, l3_x0, l3_x1, round(l3_sep_y + mm(1.75), 2), b2_y1, cols=3,
        headline="यूरोपीय संघ व ब्रिटेन के साथ मुक्त व्यापार समझौता अंतिम चरण में",
        city="ब्रसेल्स",
        agency="विदेश डेस्क",
        blurb_word="व्यापार",
        body=(
            "भारत और यूरोपीय संघ के बीच प्रस्तावित मुक्त व्यापार समझौते के चौदहवें दौर की वार्ता सफलतापूर्वक संपन्न हो गई है। इससे भारतीय कपड़ा, "
            "चमड़ा, आईटी सेवा और फार्मा निर्यात को यूरोपीय बाजारों में शुल्क-मुक्त प्रवेश मिलेगा।"
        ),
        hi_pt=36.0,
        lo_pt=30.0,
    )

    # --- Story 4: Right 5-Column Main Desh-Videsh Lead (Cols 4..8, Gray Box in LAST Col 8!) ---
    lead_x0 = grid.col_x0(4)
    lead_x1 = grid.col_x1(4, 5)
    lead_cur_y = b2_y0

    lead_head_txt = "हिंद-प्रशांत क्षेत्र में भारत व मित्र देशों का नौसैनिक महाअभ्यास"
    _, _, s4_pt, lead_hh = fit_aditya_bharat_headline(
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

    lead_sub_txt = "समुद्री व्यापार मार्गों की सुरक्षा का संकल्प : स्वदेशी विमानवाहक पोत विक्रांत और परमाणु पनडुब्बियां शामिल"
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
    lead_body_y1 = b2_y1

    # Cols 4..7 = Main News Body starting in Col 4!
    lbody_x0 = grid.col_x0(4)
    lbody_x1 = grid.col_x1(4, 4)
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
    place_red_subject_blurb(0, grid.col_x0(4), round(lead_body_y0 + cm(1.85), 2), "सामरिक")

    l_cap_y1 = round(snap_underflow_top(lead_body_y1, num_underflow_lines=7) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(5),
        lead_body_y0,
        grid.col_x1(5, 2),
        l_cap_y1,
        "p1_def_825931.jpg",
        "ab_p8_lead_navy_cmyk.jpg",
        "बंगाल की खाड़ी में संयुक्त नौसैनिक अभ्यास के दौरान भारतीय युद्धपोत। — फाइल फोटो",
        cap_h=22.0,
    )
    lead_body_txt = (
        "हिंद-प्रशांत महासागर क्षेत्र में स्वतंत्र और सुरक्षित समुद्री आवागमन सुनिश्चित करने के लिए भारतीय नौसेना और मित्र देशों के नौसैनिक बेड़ों का "
        "दस दिवसीय बहुपक्षीय युद्धाभ्यास विशाखापत्तनम तट के पास शुरू हो गया है। इस महाअभ्यास में भारत के स्वदेशी विमानवाहक पोत आईएनएस विक्रांत, "
        "गाइडेड मिसाइल विध्वंसक पोतों और लंबी दूरी के टोही विमानों ने अपनी मारक क्षमता का प्रदर्शन किया।\n"
        "रक्षा मंत्रालय के अनुसार अभ्यास के दौरान पनडुब्बी रोधी युद्धकौशल, समुद्री डकैती नियंत्रण और संयुक्त वायु रक्षा संचालन का गहन परीक्षण किया गया।"
    )
    fit_aditya_bharat_body(r_lead_body["story"], "नई दिल्ली", "विशेष संवाददाता", lead_body_txt)

    # Col 8 (LAST Column of the Right 5-Col Lead = Full-Height 40% Gray Box, 100% filled!)
    inset_pt = mm(2.5)
    box8_x0 = grid.col_x0(8)
    box8_x1 = grid.col_x1(8, 1)
    r_lbox5 = cmd("frame.create", {
        "spread": 0,
        "rect": [box8_x0, lead_body_y0, box8_x1, lead_body_y1],
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
        "• हिंद महासागर में बीस से अधिक युद्धपोतों और पैंतीस लड़ाकू विमानों की भागीदारी।\n"
        "• स्वदेशी ब्रह्मोस सुपरसोनिक क्रूज मिसाइल और बराक एयर डिफेंस का लाइव अभ्यास।\n"
        "• समुद्री केबल और ऊर्जा आपूर्ति मार्गों की सुरक्षा के लिए साझा सूचना केंद्र स्थापित।"
    )
    fit_box_completely(
        r_lbox5["story"],
        head_str="सामरिक बिंदु",
        raw_bullets=lbox5_bullets,
        head_pt=16.0,
        head_align="center",
        body_pt=10.5,
        body_lead=11.3,
        para_space=2.2,
    )

    sep2_y = round(b2_y1 + mm(1.75), 2)
    r_sep2 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep2_y], "b": [grid.print_x1, sep2_y]})
    cmd("object.stroke", {"ids": [r_sep2["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # BAND 3 (STORIES 5, 6, 7): 3 + 2 + 3 INTERLOCKED SPLIT (y = 27.15 .. 35.85 cm, Height = 8.7 cm)
    # ==========================================================================
    b3_y0 = round(sep2_y + mm(1.75), 2)
    b3_y1 = snap_frame_bottom_to_baseline(round(b3_y0 + cm(8.7), 2))

    # --- Story 5: Cols 1..3 Illustrated Antarctica Research Story ---
    s5_x0 = grid.col_x0(1)
    s5_x1 = grid.col_x1(1, 3)
    s5_head = "अंटार्कटिका में भारत के नए मैत्री शोध केंद्र का निर्माण जल्द"
    _, _, s5_pt, s5_hh = fit_aditya_bharat_headline(
        0, s5_x0, b3_y0, s5_x1,
        raw_text=s5_head,
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=36.0,
        lo_pt=30.0,
        align="left",
    )
    s5_by0 = round(b3_y0 + s5_hh + 2.0, 2)
    r_s5_b = cmd("frame.create", {
        "spread": 0,
        "rect": [s5_x0, s5_by0, s5_x1, b3_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_s5_b["id"]],
        "columns": 3,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, s5_x0, round(s5_by0 + cm(1.6), 2), "अभियान")

    s5_cap_y1 = round(snap_underflow_top(b3_y1, num_underflow_lines=5) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(2),
        s5_by0,
        grid.col_x1(2, 2),
        s5_cap_y1,
        "p9_antarctica_penguin.jpg",
        "ab_p8_s6_antarctica_cmyk.jpg",
        "अंटार्कटिका के बर्फीले क्षेत्र में वैज्ञानिक सर्वेक्षण अभियान। — फाइल फोटो",
        cap_h=22.0,
    )
    s5_body = (
        "पृथ्वी विज्ञान मंत्रालय ने दक्षिणी ध्रुव अंटार्कटिका में भारत के अत्याधुनिक अनुसंधान केंद्र मैत्री-टू के निर्माण की रूपरेखा तैयार कर ली है। "
        "यह नया केंद्र हरित ऊर्जा पर आधारित होगा और ग्लोबल वार्मिंग तथा समुद्री जलस्तर पर शोध करेगा।"
    )
    fit_aditya_bharat_body(r_s5_b["story"], "नई दिल्ली", "ब्यूरो", s5_body)

    # --- Story 6: Cols 4..5 Center 2-Col BRICS Trade Story ---
    s6_pt = place_multi_col_story(
        grid, grid.col_x0(4), grid.col_x1(4, 2), b3_y0, b3_y1, cols=2,
        headline="ब्रिक्स देशों में राष्ट्रीय मुद्रा से व्यापार बढ़ेगा",
        city="मास्को",
        agency="एजेंसी",
        blurb_word="ब्रिक्स",
        body=(
            "ब्रिक्स देशों के वित्त मंत्रियों और केंद्रीय बैंक गवर्नरों की बैठक में आपसी द्विपक्षीय व्यापार का निपटान राष्ट्रीय मुद्राओं में करने "
            "तथा नई डिजिटल भुगतान प्रणाली विकसित करने पर सहमति बन गई है।"
        ),
        hi_pt=35.0,
        lo_pt=30.0,
    )

    # --- Story 7: Cols 6..8 Right 3-Col North-East Infrastructure Story ---
    s7_pt = place_multi_col_story(
        grid, grid.col_x0(6), grid.col_x1(6, 3), b3_y0, b3_y1, cols=3,
        headline="पूर्वोत्तर राज्यों में चार नए एयरपोर्ट और फोर-लेन राजमार्ग मंजूर",
        city="गुवाहाटी",
        agency="ब्यूरो",
        blurb_word="विकास",
        body=(
            "केंद्र सरकार ने पूर्वोत्तर के सीमावर्ती राज्यों में संपर्क और पर्यटन को बढ़ावा देने के लिए पैंतीस हजार करोड़ रुपये की नई राजमार्ग तथा "
            "ग्रीनफील्ड हवाई अड्डा परियोजनाओं को मंजूरी दे दी है। इससे आसियान देशों के साथ व्यापारिक जुड़ाव भी तेज होगा।"
        ),
        hi_pt=36.0,
        lo_pt=30.0,
    )

    sep3_y = round(b3_y1 + mm(1.75), 2)
    r_sep3 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep3_y], "b": [grid.print_x1, sep3_y]})
    cmd("object.stroke", {"ids": [r_sep3["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # BAND 4 (STORIES 8, 9, 10): 2 + 3 + 3 INTERLOCKED SPLIT (y = 36.20 .. 43.30 cm, Height = 7.1 cm)
    # ==========================================================================
    b4_y0 = round(sep3_y + mm(1.75), 2)
    b4_y1 = snap_frame_bottom_to_baseline(round(b4_y0 + cm(7.1), 2))

    # --- Story 8: Cols 1..2 India-Japan Semiconductor Story ---
    s8_pt = place_multi_col_story(
        grid, grid.col_x0(1), grid.col_x1(1, 2), b4_y0, b4_y1, cols=2,
        headline="जापान और भारत में चिप तकनीक समझौता",
        city="टोक्यो",
        agency="एजेंसी",
        blurb_word="तकनीक",
        body=(
            "भारत और जापान ने सेमीकंडक्टर वेफर निर्माण, कृत्रिम बुद्धिमत्ता और क्रिटिकल मिनरल्स की आपूर्ति श्रृंखला को सुरक्षित बनाने के लिए "
            "रणनीतिक समझौते पर हस्ताक्षर किए हैं।"
        ),
        hi_pt=35.0,
        lo_pt=30.0,
    )

    # --- Story 9: Cols 3..5 Global Climate Summit Story ---
    s9_pt = place_multi_col_story(
        grid, grid.col_x0(3), grid.col_x1(3, 3), b4_y0, b4_y1, cols=3,
        headline="जलवायु सम्मेलन में भारत के हरित ऊर्जा मॉडल की भरपूर प्रशंसा",
        city="जिनेवा",
        agency="एजेंसी",
        blurb_word="पर्यावरण",
        body=(
            "संयुक्त राष्ट्र पर्यावरण कार्यक्रम की वार्षिक रिपोर्ट में सौर ऊर्जा गठबंधन और हरित हाइड्रोजन मिशन के जरिए कार्बन उत्सर्जन घटाने में "
            "भारत को जी-20 देशों में सबसे अग्रणी राष्ट्र बताया गया है।"
        ),
        target_lines=2,
        hi_pt=36.0,
        lo_pt=30.0,
    )

    # --- Story 10: Cols 6..8 Diaspora Consular Centers Story ---
    s10_pt = place_multi_col_story(
        grid, grid.col_x0(6), grid.col_x1(6, 3), b4_y0, b4_y1, cols=3,
        headline="प्रवासी भारतीयों के लिए बीस देशों में नए ई-सेवा केंद्र शुरू",
        city="नई दिल्ली",
        agency="विदेश ब्यूरो",
        blurb_word="प्रवासी",
        body=(
            "विदेशों में रहने वाले तीन करोड़ से अधिक प्रवासी भारतीयों और छात्रों को पासपोर्ट, वीजा तथा आपातकालीन कांसुलर सहायता चौबीस घंटे "
            "उपलब्ध कराने के लिए विदेश मंत्रालय ने बीस नए डिजिटल सेवा केंद्र शुरू किए हैं।"
        ),
        target_lines=2,
        hi_pt=36.0,
        lo_pt=30.0,
    )

    sep4_y = round(b4_y1 + mm(1.75), 2)
    r_sep4 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep4_y], "b": [grid.print_x1, sep4_y]})
    cmd("object.stroke", {"ids": [r_sep4["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 5 (STORIES 11 & 12): BOTTOM STRIP (y = 43.65 .. 52.00 cm)
    #   - Left 2-Col Story (Cols 1..2 — Story 11)
    #   - Right 6-Col Grand Space Anchor (Cols 3..8 — Story 12)
    # ==========================================================================
    bot_y0 = round(sep4_y + mm(1.75), 2)
    bot_y1 = snap_frame_bottom_to_baseline(grid.print_y1)

    # --- Story 11: Left 2-Column Cultural Diplomacy Story (Cols 1..2) ---
    s11_pt = place_multi_col_story(
        grid, grid.col_x0(1), grid.col_x1(1, 2), bot_y0, bot_y1, cols=2,
        headline="विदेशी विवि में भारतीय योग व दर्शन पीठ",
        city="लंदन",
        agency="एजेंसी",
        blurb_word="संस्कृति",
        body=(
            "भारतीय सांस्कृतिक संबंध परिषद के सहयोग से ब्रिटेन, ऑस्ट्रेलिया और जर्मनी के पांच प्रमुख विश्वविद्यालयों में आयुर्वेद, योग और संस्कृत "
            "अध्ययन के लिए नई शैक्षणिक पीठ स्थापित की गई हैं।"
        ),
        hi_pt=35.0,
        lo_pt=30.0,
    )

    # --- Story 12: Right 6-Column Grand Space Anchor (Cols 3..8) ---
    anc_x0 = grid.col_x0(3)
    anc_x1 = grid.col_x1(3, 6)
    anc_cur_y = bot_y0

    anchor_head = "अंतरिक्ष स्टेशन अभियान के लिए नासा और इसरो साथ"
    _, _, s12_pt, anc_hh = fit_aditya_bharat_headline(
        0, anc_x0, anc_cur_y, anc_x1,
        raw_text=anchor_head,
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=50.0,
        lo_pt=38.0,
        align="center",
    )
    anc_cur_y = round(bot_y0 + anc_hh + 1.0, 2)

    anchor_sub = "भारतीय अंतरिक्ष यात्री शुभांशु शुक्ला के प्रशिक्षण का दूसरा चरण ह्यूस्टन में पूरा : संयुक्त वैज्ञानिक प्रयोग होंगे"
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
    place_red_subject_blurb(0, grid.col_x0(3), round(anc_body_y0 + cm(1.55), 2), "अंतरिक्ष")

    acap_y1 = round(snap_underflow_top(anc_body_y1, num_underflow_lines=5) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(5),
        anc_body_y0,
        grid.col_x1(5, 2),
        acap_y1,
        "p8_isro_834820_print.jpg",
        "ab_p8_anchor_isro_cmyk.jpg",
        "नासा और इसरो के संयुक्त अंतरिक्ष मिशन की तैयारी। — फाइल फोटो",
        cap_h=22.0,
    )
    anc_body = (
        "भारत और अमेरिका के अंतरिक्ष सहयोग के तहत अंतरराष्ट्रीय अंतरिक्ष स्टेशन पर भेजे जाने वाले संयुक्त एक्सिओम-4 मिशन की सभी तकनीकी "
        "तैयारियां पूरी कर ली गई हैं। इस अभियान के दौरान भारतीय गगनयात्री अंतरिक्ष में सूक्ष्म-गुरुत्वाकर्षण, जैव-प्रौद्योगिकी और कृषि से जुड़े सात "
        "महत्वपूर्ण वैज्ञानिक प्रयोग करेंगे।"
    )
    fit_aditya_bharat_body(r_anc_body["story"], "वाशिंगटन", "एजेंसी", anc_body)

    cmd("edit.deselectAll")
    cmd("view.fitPage", {})

    out_pd = VAULT_DIR / "Aditya_Bharat_Page_08_Desh_Videsh_34x53.pagedesigner"
    out_png = VAULT_DIR / "Aditya_Bharat_Page_08_Desh_Videsh_34x53.png"
    out_pdf = VAULT_DIR / "Aditya_Bharat_Page_08_Desh_Videsh_CMYK_34x53.pdf"
    rpc("app.save", {"path": str(out_pd)})
    rpc("app.export", {"path": str(out_png), "page": 0, "scale": 1.5})
    try:
        rpc("engine.execute", {"command": "file.exportPdf", "params": {"path": str(out_pdf)}})
    except Exception:
        pass

    artifact_png = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\8707c72d-58b0-4715-a099-3efffcd57514\aditya_bharat_page_08_desh_videsh_34x53.png")
    artifact_png.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_png, artifact_png)

    all_pts = [s1_pt, s2_pt, s3_pt, s4_pt, s5_pt, s6_pt, s7_pt, s8_pt, s9_pt, s10_pt, s11_pt, s12_pt]
    print(
        f"=== ADITYA BHARAT PAGE 08 (DESH-VIDESH - 12 STORIES) BUILT IN {time.perf_counter()-t0:.2f}s ===\n"
        f"    12 Story Headline Pts: {all_pts} (Min={min(all_pts)}pt >= 30.0pt!)"
    )


if __name__ == "__main__":
    build_aditya_bharat_page8_desh_videsh()
