# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — PAGE 06 (कारोबार / BUSINESS PAGE) MASTER BUILDER
===============================================================================
Builds Page 06 ('कारोबार') with a tightly packed ('कसा हुआ') 9-Story + Market Box
Broadsheet Layout strictly following the locked Aditya Bharat Stylesheet:
  1. Page Size           : 34.0 cm Width x 53.0 cm Height (Outer Margins = 1-1-1-1 cm)
  2. Print Area (Fixed)  : 32.0 cm Width x 51.0 cm Height (8 Columns, 4.0 mm Gutter)
  3. Zone 1 (Masthead)   : 1.5 cm Inside Running Masthead (y = 1.0 .. 2.5 cm, Cols 1..8)
                           - Left: Red Color Box ('FlyerCrimson') with 'कारोबार' in 20 pt 'DB Hindi 6' White
                           - Center: 'आदित्य भारत' Masthead Logo ('28 pt DB Rasrand Bold', 100% Black)
                           - Right: Dateline ('16 pt DB Hindi Bold') + '06' ('18 pt Times New Roman Bold')
                           - Bottom: 2.0 pt Rule in 60% Gray across all 8 columns
  4. All Headlines & Subheads: 100% Black ('[Black]') — NEVER Red!
                           - All 9 Story Headlines >= 30.0 pt ('DB Rasrand Bold')
  5. Lead Full-Height Gray Box in LAST Column of Lead (Col 5 of 5-Col Lead), NEVER in Col 1!
  6. Compact Photos (3.2 - 4.0 cm tall) with generous body text underflow.
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


class AdityaBharatPage6Grid:
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
    import os
    pd_candidates = [
        Path(os.environ.get("PAGEDESIGNER_EXE", "")) if os.environ.get("PAGEDESIGNER_EXE") else None,
        VAULT_DIR / "Page_Designer_Software" / "pagedesigner.exe",
        VAULT_DIR.parent / "Page_Designer_Software" / "pagedesigner.exe",
        Path(r"E:\RND\Gujarat_Samachar\Page_Designer_Software\pagedesigner.exe"),
        Path(r"E:\RND\open page layout software\pagedesigner.exe"),
    ]
    pd_exe = next((p for p in pd_candidates if p and p.exists()), pd_candidates[3])
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
    if os.environ.get("AB_SKIP_SAVE") == "1":
        if method in ("app.save", "app.export"):
            return None
        if method == "engine.execute" and isinstance(params, dict) and params.get("command") == "file.exportPdf":
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
        search_lo = 9.5 if font_family != "DB Rasrand Bold" else min(lo_pt, 15.0)
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


def place_red_subject_blurb(spread_idx: int, x0: float, y0: float, word_text: str, bw_cm: float = 1.82):
    bw = cm(bw_cm)
    bh = cm(1.24)
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
            "size": 21.0,
            "leading": {"kind": "points", "value": 21.5},
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
                "size": 20.0,
                "leading": {"kind": "points", "value": 20.5},
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
    "\nवाणिज्य और वित्त मंत्रालय के वरिष्ठ अधिकारियों के अनुसार इस तिमाही में औद्योगिक उत्पादन, घरेलू खपत और निर्यात के मोर्चे पर "
    "सकारात्मक रुझान दर्ज किए गए हैं। आर्थिक विशेषज्ञों का मानना है कि बुनियादी ढांचे में बढ़ते सरकारी निवेश और सरल कर प्रणाली से "
    "भारतीय कॉरपोरेट जगत और सूक्ष्म, लघु व मध्यम उद्यमों को वैश्विक बाजार में नई प्रतिस्पर्धात्मक बढ़त हासिल होगी। "
    "बैंकिंग क्षेत्र की मजबूत बैलेंस शीट और डिजिटल भुगतान के विस्तार ने भी कारोबार की गति को नई मजबूती प्रदान की है।"
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
        ext_text = ext_text + (EXTRA_HINDI_SENTENCES if first_ext else " " + EXTRA_HINDI_SENTENCES.lstrip())
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
    head_prefix = f"{head_str.strip()}\n"
    head_b = len(head_prefix.encode("utf-8"))
    head_lead = round(head_pt + 1.0, 2)

    extra_bullets = (
        "\n• घरेलू और अंतरराष्ट्रीय निवेशकों के लिए सिंगल-विंडो डिजिटल मंजूरी प्रणाली को और तेज किया गया।"
        "\n• सूक्ष्म, लघु और मध्यम उद्यमों को सस्ती कार्यशील पूंजी व निर्यात क्रेडिट गारंटी का सीधा लाभ मिलेगा।"
        "\n• हरित ऊर्जा, सेमीकंडक्टर और लॉजिस्टिक्स पार्कों में लाखों युवाओं के लिए प्रत्यक्ष रोजगार के अवसर खुलेंगे।"
        "\n• बैंकिंग और फिनटेक सेक्टर में साइबर सुरक्षा व त्वरित निपटान मानकों को वैश्विक स्तर पर उन्नत किया गया।"
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
    grid: AdityaBharatPage6Grid,
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
    hi_pt: float = 36.0,
    lo_pt: float = 30.0,
):
    _, _, h_pt, hh = fit_aditya_bharat_headline(
        0, x0, y0, x1,
        raw_text=headline,
        target_lines=2,
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
        place_red_subject_blurb(0, x0, round(by0 + cm(1.85), 2), blurb_word)
    fit_aditya_bharat_body(r_b["story"], city, agency, body)
    return h_pt


def build_aditya_bharat_page6_business():
    t0 = time.perf_counter()
    connect_page_designer()
    grid = AdityaBharatPage6Grid()

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
            "title": "आदित्य भारत — पेज 06 कारोबार (34x53 सेमी | प्रिंट एरिया 32x51 सेमी)",
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

    sec_w = cm(4.2)
    sec_y0 = round(mh_y0 + mm(1.0), 2)
    sec_y1 = round(mh_y1 - mm(1.8), 2)
    r_mh_sec = cmd("frame.create", {
        "spread": 0,
        "rect": [mh_x0, sec_y0, round(mh_x0 + sec_w, 2), sec_y1],
        "content": "text",
        "text": "कारोबार",
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

    logo_w = cm(4.85)
    logo_x0 = round((mh_x0 + mh_x1 - logo_w) / 2.0, 2)
    logo_x1 = round(logo_x0 + logo_w, 2)
    logo_img_path = PHOTOS_DIR / "aditya_bharat_masthead_logo.png"
    r_mh_logo = cmd("frame.create", {
        "spread": 0,
        "rect": [logo_x0, round(mh_y0 + mm(0.8), 2), logo_x1, sec_y1],
        "content": "graphic",
    })
    batch([
        {"command": "file.place", "params": {"frame": r_mh_logo["id"], "path": str(logo_img_path)}},
        {"command": "object.fit", "params": {"ids": [r_mh_logo["id"]], "mode": "fitProportionally"}},
        {"command": "object.stroke", "params": {"ids": [r_mh_logo["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
    ])

    pnum_w = cm(1.4)
    pnum_x0 = round(mh_x1 - pnum_w, 2)
    r_mh_pnum = cmd("frame.create", {
        "spread": 0,
        "rect": [pnum_x0, sec_y0, mh_x1, sec_y1],
        "content": "text",
        "text": "06",
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

    import os
    import datetime as _dt
    ed_code = os.environ.get("AB_EDITION", "RAIPUR").strip().upper()
    city_map = {
        "RAIPUR": "रायपुर",
        "NEW_DELHI": "नई दिल्ली",
        "BILASPUR": "बिलासपुर",
        "BHOPAL": "भोपाल",
        "JAIPUR": "जयपुर",
        "INDORE": "इंदौर",
        "RAJNANDGAON": "राजनांदगांव",
    }
    city_hi = city_map.get(ed_code, "रायपुर")
    date_env = os.environ.get("AB_EDITION_DATE", "19-11-2026").strip()
    try:
        dt_obj = _dt.datetime.strptime(date_env, "%d-%m-%Y").date()
    except Exception:
        dt_obj = _dt.date(2026, 11, 19)
    hi_weekdays = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
    hi_months = {
        1: "जनवरी", 2: "फरवरी", 3: "मार्च", 4: "अप्रैल", 5: "मई", 6: "जून",
        7: "जुलाई", 8: "अगस्त", 9: "सितंबर", 10: "अक्टूबर", 11: "नवंबर", 12: "दिसंबर",
    }
    dynamic_dateline = f"{city_hi}, {hi_weekdays[dt_obj.weekday()]}, {dt_obj.day} {hi_months[dt_obj.month]} {dt_obj.year}  |"

    p6_data = {}
    p6_json_env = os.environ.get("AB_P6_JSON_PATH", "").strip()
    if p6_json_env and Path(p6_json_env).exists():
        try:
            p6_data = json.loads(Path(p6_json_env).read_text(encoding="utf-8"))
        except Exception:
            p6_data = {}
    else:
        cand_json = VAULT_DIR / "daily_harvester_cache" / f"{date_env}_KAROBAR_PAGE6_STORIES.json"
        if cand_json.exists():
            try:
                p6_data = json.loads(cand_json.read_text(encoding="utf-8"))
            except Exception:
                p6_data = {}
    if p6_data.get("dateline_override"):
        dynamic_dateline = p6_data["dateline_override"]

    dt_x0 = round(logo_x1 + cm(0.4), 2)
    dt_x1 = round(pnum_x0 - cm(0.2), 2)
    r_mh_dt = cmd("frame.create", {
        "spread": 0,
        "rect": [dt_x0, sec_y0, dt_x1, sec_y1],
        "content": "text",
        "text": dynamic_dateline,
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
    # BAND 1: 2-COL MARKET DIGEST BOX (Cols 1..2) + 6-COLUMN BUSINESS FLYER (Cols 3..8)
    #   y = 2.85 .. 13.45 cm (Height = 10.6 cm)
    # ==========================================================================
    b1_y0 = round(mh_y1 + mm(3.5), 2)
    b1_y1 = snap_frame_bottom_to_baseline(round(b1_y0 + cm(10.6), 2))

    # --- 1A. Left 2-Col Market & Bullion Digest Box (Cols 1..2, 100% filled) ---
    inset_pt = mm(2.5)
    mkt_x0 = grid.col_x0(1)
    mkt_x1 = grid.col_x1(1, 2)
    r_mkt_box = cmd("frame.create", {
        "spread": 0,
        "rect": [mkt_x0, b1_y0, mkt_x1, b1_y1],
        "content": "text",
        "text": "",
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_mkt_box["id"]], "swatch": "[Black]", "tint": 0.14}},
        {"command": "object.stroke", "params": {"ids": [r_mkt_box["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 0.65}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_mkt_box["id"]],
            "columns": 1,
            "inset": [inset_pt, inset_pt, inset_pt, inset_pt],
            "verticalJustification": "top",
        }},
    ])
    mkt_bullets = p6_data.get("market_meter_bullets") or (
        "• बीएसई सेंसेक्स : 84,620 अंक (+645 अंक उछाल), निफ्टी पच्चीस हजार आठ सौ के पार बंद।\n"
        "• सर्राफा बाजार (इंदौर/मुंबई) : सोना 24 कैरेट 78,450 रुपये प्रति दस ग्राम, चांदी 94,200 रुपये प्रति किलो।\n"
        "• विदेशी मुद्रा विनिमय : डॉलर के मुकाबले रुपया बारह पैसे मजबूत होकर 83.82 के स्तर पर टिका।\n"
        "• अंतरराष्ट्रीय कच्चा तेल : ब्रेंट क्रूड नरम पड़कर चौहत्तर डॉलर प्रति बैरल पर आया, आयात बिल में राहत।\n"
        "• विदेशी संस्थागत निवेशक : भारतीय शेयर बाजार में बारह हजार करोड़ रुपये की शुद्ध लिवाली।"
    )
    fit_box_completely(
        r_mkt_box["story"],
        head_str=p6_data.get("market_meter_title") or "बाजार मीटर : सेंसेक्स और सर्राफा",
        raw_bullets=mkt_bullets,
        head_pt=17.5,
        head_align="center",
        body_pt=10.5,
        body_lead=11.3,
        para_space=2.5,
    )

    # --- 1B. Right 6-Col Business Flyer (Cols 3..8) ---
    fl_x0 = grid.col_x0(3)
    fl_x1 = grid.col_x1(3, 6)
    fl_cur_y = b1_y0

    s1 = p6_data.get("s1_flyer") or {}
    flyer_sub_txt = s1.get("subhead") or "मेक इन इंडिया और पीएलआई योजना का असर : इलेक्ट्रॉनिक्स व ऑटो पार्ट्स की वैश्विक मांग बढ़ी"
    _, _, _, fl_sub_h = fit_aditya_bharat_headline(
        0, fl_x0, fl_cur_y, fl_x1,
        raw_text=flyer_sub_txt,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=16.5,
        lo_pt=14.0,
        align="center",
    )
    fl_cur_y = round(fl_cur_y + fl_sub_h + 1.0, 2)

    flyer_head_txt = s1.get("headline") or "सेमीकंडक्टर व ऑटो निर्यात में भारत की बड़ी छलांग"
    _, _, fl_h_pt, fl_hh = fit_aditya_bharat_headline(
        0, fl_x0, fl_cur_y, fl_x1,
        raw_text=flyer_head_txt,
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=56.0,
        lo_pt=40.0,
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
        "columns": 6,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, grid.col_x0(3), round(fl_body_y0 + cm(1.8), 2), s1.get("blurb") or "उछाल")

    fl_cap_y1 = round(snap_underflow_top(fl_body_y1, num_underflow_lines=7) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(5),
        fl_body_y0,
        grid.col_x1(5, 2),
        fl_cap_y1,
        s1.get("photo") or "p6_auto_831643_print.jpg",
        "ab_p6_flyer_auto_cmyk.jpg",
        s1.get("caption") or "आधुनिक ऑटोमोबाइल और इलेक्ट्रॉनिक्स विनिर्माण संयंत्र में तैयार होते निर्यात वाहन। — फाइल फोटो",
        cap_h=23.0,
    )
    fl_body_txt = s1.get("body") or (
        "प्रोडक्शन लिंक्ड इंसेंटिव योजना और स्वदेशी सप्लाई चेन के विस्तार से चालू वित्त वर्ष की पहली छमाही में भारत के इंजीनियरिंग, ऑटोमोबाइल और "
        "इलेक्ट्रॉनिक्स निर्यात ने पैंसठ अरब डॉलर का नया कीर्तिमान छू लिया है। वाणिज्य मंत्रालय के आंकड़ों के अनुसार यूरोप, पश्चिम एशिया और लैटिन अमेरिकी "
        "बाजारों में भारतीय यात्री वाहनों तथा स्मार्टफोन उपकरणों की मांग में अड़तीस प्रतिशत की तेज वृद्धि दर्ज की गई है।"
    )
    fit_aditya_bharat_body(r_fl_body["story"], s1.get("city") or "नई दिल्ली", s1.get("agency") or "ब्यूरो", fl_body_txt)

    sep1_y = round(b1_y1 + mm(1.75), 2)
    r_sep1 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep1_y], "b": [grid.print_x1, sep1_y]})
    cmd("object.stroke", {"ids": [r_sep1["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 2: LEFT 3-COL STACK (Cols 1..3) + RIGHT 5-COL MAIN BUSINESS LEAD (Cols 4..8, Gray Box in LAST Col 8!)
    #   y = 13.80 .. 29.80 cm (Height = 16.0 cm)
    # ==========================================================================
    b2_y0 = round(sep1_y + mm(1.75), 2)
    b2_y1 = snap_frame_bottom_to_baseline(round(b2_y0 + cm(16.0), 2))

    # --- 2A. Left 3-Column Stacked Stories (Cols 1..3: 2 Stories) ---
    r3_x0 = grid.col_x0(1)
    r3_x1 = grid.col_x1(1, 3)
    r3_mid_y = snap_frame_bottom_to_baseline(round(b2_y0 + cm(7.8), 2))

    s2 = p6_data.get("s2_left_top") or {}
    s2_top_pt = place_multi_col_story(
        grid, r3_x0, r3_x1, b2_y0, r3_mid_y, cols=3,
        headline=s2.get("headline") or "डिजिटल बैंकिंग से छोटे उद्यमों को बिना गारंटी मिलेगा तुरंत ऋण",
        city=s2.get("city") or "मुंबई",
        agency=s2.get("agency") or "ब्यूरो",
        blurb_word=s2.get("blurb") or "बैंकिंग",
        body=s2.get("body") or (
            "भारतीय रिजर्व बैंक और सार्वजनिक क्षेत्र के बैंकों ने यूपीआई लेनदेन के इतिहास के आधार पर छोटे दुकानदारों तथा सूक्ष्म उद्यमों को "
            "दस लाख रुपये तक का बिना गारंटी कार्यशील पूंजी ऋण मात्र पंद्रह मिनट में स्वीकृत करने का नया डिजिटल प्लेटफॉर्म शुरू किया है।"
        ),
        hi_pt=38.0,
        lo_pt=30.0,
    )

    r3_sep_y = round(r3_mid_y + mm(1.75), 2)
    r_r3_sep = cmd("line.create", {"spread": 0, "a": [r3_x0, r3_sep_y], "b": [r3_x1, r3_sep_y]})
    cmd("object.stroke", {"ids": [r_r3_sep["id"]], "swatch": "[Black]", "weight": 0.65, "tint": 0.85})

    s3 = p6_data.get("s3_left_bot") or {}
    s2_bot_pt = place_multi_col_story(
        grid, r3_x0, r3_x1, round(r3_sep_y + mm(1.75), 2), b2_y1, cols=3,
        headline=s3.get("headline") or "इलेक्ट्रिक वाहन और लिथियम बैटरी प्लांट में पांच अरब डॉलर का निवेश",
        city=s3.get("city") or "अहमदाबाद",
        agency=s3.get("agency") or "एजेंसी",
        blurb_word=s3.get("blurb") or "निवेश",
        body=s3.get("body") or (
            "स्वच्छ परिवहन को बढ़ावा देने के लिए देश की प्रमुख ऑटोमोबाइल कंपनियों ने गुजरात, मध्य प्रदेश और महाराष्ट्र में चार नई गीगा-बैटरी "
            "फैक्ट्रियां स्थापित करने की घोषणा की है। इससे इलेक्ट्रिक वाहनों की कीमतों में बीस प्रतिशत तक की कमी आएगी।"
        ),
        hi_pt=38.0,
        lo_pt=30.0,
    )

    # --- 2B. Right 5-Column Main Business Lead (Cols 4..8, Gray Box in LAST Col 8!) ---
    lead_x0 = grid.col_x0(4)
    lead_x1 = grid.col_x1(4, 5)
    lead_cur_y = b2_y0

    s4 = p6_data.get("s4_lead") or {}
    lead_head_txt = s4.get("headline") or "जीएसटी संग्रह दो लाख करोड़ के पार, विनिर्माण क्षेत्र में नया उछाल"
    _, _, lead_h_pt, lead_hh = fit_aditya_bharat_headline(
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

    lead_sub_txt = s4.get("subhead") or "त्योहारी सीजन और औद्योगिक मांग से राजकोषीय घाटे में कमी : राज्यों को समय से पहले मिली कर हिस्सेदारी"
    _, _, _, lead_sub_h = fit_aditya_bharat_headline(
        0, lead_x0, lead_cur_y, lead_x1,
        raw_text=lead_sub_txt,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=16.0,
        lo_pt=12.5,
        align="left",
    )
    lead_body_y0 = round(lead_cur_y + lead_sub_h + 1.5, 2)
    lead_body_y1 = b2_y1

    # Cols 4..7 (First 4 Columns of the Right 5-Col Lead = News Body starting in Col 4!)
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
    place_red_subject_blurb(0, grid.col_x0(4), round(lead_body_y0 + cm(2.1), 2), s4.get("blurb") or "रिकॉर्ड")

    # Compact photo in Cols 5..6 + 8-line underflow
    l_cap_y1 = round(snap_underflow_top(lead_body_y1, num_underflow_lines=8) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(5),
        lead_body_y0,
        grid.col_x1(5, 2),
        l_cap_y1,
        s4.get("photo") or "p6_gst_831886_print.jpg",
        "ab_p6_lead_gst_cmyk.jpg",
        s4.get("caption") or "नई दिल्ली स्थित केंद्रीय वित्त मंत्रालय परिसर में जीएसटी परिषद की उच्चस्तरीय बैठक। — फाइल फोटो",
        cap_h=23.0,
    )
    lead_body_txt = s4.get("body") or (
        "त्योहारी सीजन की मजबूत उपभोक्ता मांग और ई-इन्वॉयसिंग प्रणाली की सख्ती के चलते देश का मासिक वस्तु एवं सेवा कर संग्रह दो लाख बारह हजार करोड़ "
        "रुपये के ऐतिहासिक स्तर पर पहुंच गया है। वित्त मंत्रालय द्वारा जारी आंकड़ों के अनुसार पिछले वर्ष की समान अवधि की तुलना में कर संग्रह में चौदह "
        "प्रतिशत की वृद्धि दर्ज की गई है।\n"
        "महाराष्ट्र, गुजरात, कर्नाटक, तमिलनाडु और मध्य प्रदेश ने औद्योगिक कर संग्रह में सर्वाधिक योगदान दिया है। केंद्र सरकार ने राज्यों को उनके हिस्से के "
        "अस्सी हजार करोड़ रुपये की किस्त भी तुरंत जारी कर दी है, जिससे राज्य स्तर पर सड़क, सिंचाई और औद्योगिक पार्कों के निर्माण को नई गति मिलेगी।"
    )
    fit_aditya_bharat_body(r_lead_body["story"], s4.get("city") or "नई दिल्ली", s4.get("agency") or "विशेष संवाददाता", lead_body_txt)

    # Col 8 (LAST Column of the Right 5-Column Lead = Full-Height 40% Gray Box, 100% filled!)
    box5_x0 = grid.col_x0(8)
    box5_x1 = grid.col_x1(8, 1)
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
    lbox5_bullets = s4.get("box_bullets") or (
        "• छोटे व्यापारियों के लिए जीएसटी रिटर्न दाखिल करने की प्रक्रिया को पूरी तरह स्वचालित बनाया गया।\n"
        "• निर्यातकों को सात कार्यदिवस के भीतर आईजीएसटी रिफंड सीधे बैंक खाते में मिलेगा।\n"
        "• स्वास्थ्य बीमा और कृषि उपकरणों पर कर की दरों को तर्कसंगत बनाने पर बनी सहमति।\n"
        "• फर्जी बिलिंग रोकने के लिए एआई आधारित डेटा एनालिटिक्स प्रणाली देश भर में लागू।"
    )
    fit_box_completely(
        r_lbox5["story"],
        head_str=s4.get("box_title") or "प्रमुख बिंदु",
        raw_bullets=lbox5_bullets,
        head_pt=16.0,
        head_align="center",
        body_pt=10.5,
        body_lead=11.3,
        para_space=2.3,
    )

    sep2_y = round(b2_y1 + mm(1.75), 2)
    r_sep2 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep2_y], "b": [grid.print_x1, sep2_y]})
    cmd("object.stroke", {"ids": [r_sep2["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # BAND 3: 4 INTERLOCKED 2-COLUMN BUSINESS STORIES (y = 30.15 .. 41.35 cm, Cols 1..8 = 2+2+2+2)
    # ==========================================================================
    b3_y0 = round(sep2_y + mm(1.75), 2)
    b3_y1 = snap_frame_bottom_to_baseline(round(b3_y0 + cm(11.2), 2))

    raw_b3 = p6_data.get("band3_stories")
    if raw_b3 and len(raw_b3) == 4:
        b3_stories = [
            (
                1 + 2 * i, 2,
                it.get("headline", ""),
                it.get("city", "नई दिल्ली"),
                it.get("agency", "ब्यूरो"),
                it.get("blurb", "व्यापार"),
                it.get("body", ""),
            )
            for i, it in enumerate(raw_b3)
        ]
    else:
        b3_stories = [
            (
                1, 2,
                "त्योहारी मांग से सर्राफा बाजार में भारी रौनक",
                "इंदौर", "व्यापार संवाददाता", "सर्राफा",
                "धनतेरस और दीपावली से पहले इंदौर, भोपाल और जयपुर के सर्राफा बाजारों में हल्के वजन के सोने के आभूषणों तथा चांदी के सिक्कों की अग्रिम बुकिंग में चालीस प्रतिशत की वृद्धि दर्ज की गई है।",
            ),
            (
                3, 2,
                "भारतीय एआई स्टार्टअप ने जुटाया रिकॉर्ड फंड",
                "बेंगलुरु", "एजेंसी", "टेक",
                "कृत्रिम बुद्धिमत्ता, फिनटेक और डीप-टेक सेक्टर के भारतीय स्टार्टअप्स ने तीसरी तिमाही में वैश्विक वेंचर कैपिटल फंडों से चार अरब डॉलर की नई पूंजी जुटाकर एशिया में शीर्ष स्थान हासिल किया है।",
            ),
            (
                5, 2,
                "छोटे शहरों में आवासीय प्रॉपर्टी की बिक्री बढ़ी",
                "भोपाल", "ब्यूरो", "प्रॉपर्टी",
                "इंदौर, भोपाल, रायपुर और सूरत जैसे उभरते शहरों में मेट्रो विस्तार और आईटी पार्कों के चलते किफायती तथा प्रीमियम अपार्टमेंट की बिक्री में पच्चीस फीसदी का उछाल आया है।",
            ),
            (
                7, 2,
                "कृषि व खाद्य निर्यात से किसानों की आय बढ़ी",
                "नई दिल्ली", "एजेंसी", "निर्यात",
                "बासमती चावल, मसालों, सोया उत्पादों और जैविक फलों के निर्यात में भारत ने मध्य-पूर्व तथा यूरोपीय बाजारों में नए अनुबंध किए हैं, जिसका सीधा लाभ करोड़ों किसानों को मिल रहा है।",
            ),
        ]

    b3_pts = []
    for idx, (c_start, c_span, h_txt, c_txt, a_txt, bl_txt, b_txt) in enumerate(b3_stories):
        sx0 = grid.col_x0(c_start)
        sx1 = grid.col_x1(c_start, c_span)
        pt_v = place_multi_col_story(
            grid, sx0, sx1, b3_y0, b3_y1, cols=c_span,
            headline=h_txt, city=c_txt, agency=a_txt, blurb_word=bl_txt, body=b_txt,
            hi_pt=36.0, lo_pt=30.0,
        )
        b3_pts.append(pt_v)

    sep3_y = round(b3_y1 + mm(1.75), 2)
    r_sep3 = cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep3_y], "b": [grid.print_x1, sep3_y]})
    cmd("object.stroke", {"ids": [r_sep3["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 4: BOTTOM STRIP (y = 41.70 .. 52.00 cm, Cols 1..8 = 5-Col Anchor + 3-Col Right Package)
    # ==========================================================================
    bot_y0 = round(sep3_y + mm(1.75), 2)
    bot_y1 = snap_frame_bottom_to_baseline(grid.print_y1)

    # --- 4A. Left 5-Column Business Anchor (Cols 1..5) ---
    anc_x0 = grid.col_x0(1)
    anc_x1 = grid.col_x1(1, 5)
    anc_cur_y = bot_y0

    s9 = p6_data.get("s9_anchor") or {}
    anchor_head = s9.get("headline") or "दलाल स्ट्रीट में विदेशी निवेशकों की लिवाली"
    _, _, anc_h_pt, anc_hh = fit_aditya_bharat_headline(
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
    anc_cur_y = round(bot_y0 + 44.5, 2)

    anchor_sub = s9.get("subhead") or "मजबूत तिमाही नतीजों और घरेलू म्यूचुअल फंडों के निवेश से भारतीय शेयर बाजार ने छुआ नया शिखर"
    _, _, anc_sub_pt, anc_sub_h = fit_aditya_bharat_headline(
        0, anc_x0, anc_cur_y, anc_x1,
        raw_text=anchor_sub,
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=15.5,
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
        "columns": 5,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_red_subject_blurb(0, grid.col_x0(1), round(anc_body_y0 + cm(1.8), 2), s9.get("blurb") or "बाजार")

    acap_y1 = round(snap_underflow_top(anc_body_y1, num_underflow_lines=8) - 3.2, 2)
    place_photo_and_caption_cmyk(
        0,
        grid.col_x0(3),
        anc_body_y0,
        grid.col_x1(3, 2),
        acap_y1,
        s9.get("photo") or "p6_bse_832092_print.jpg",
        "ab_p6_anchor_bse_cmyk.jpg",
        s9.get("caption") or "मुंबई स्थित बॉम्बे स्टॉक एक्सचेंज परिसर में तेजी के संकेतों के साथ स्क्रीन। — फाइल फोटो",
        cap_h=23.0,
    )
    anc_body = s9.get("body") or (
        "भारतीय कंपनियों के शानदार तिमाही नतीजों और खुदरा महंगाई में आई नरमी के बाद विदेशी संस्थागत निवेशकों ने भारतीय शेयर बाजार में एक बार फिर "
        "बड़े पैमाने पर खरीदारी शुरू कर दी है। इसके साथ ही घरेलू खुदरा निवेशकों द्वारा एसआईपी के जरिए हर महीने बाईस हजार करोड़ रुपये से अधिक का "
        "निवेश आने से बाजार को अभूतपूर्व स्थिरता मिली है। बैंकिंग, आईटी, फार्मा और कैपिटल गुड्स शेयरों में सबसे अधिक तेजी देखी जा रही है।"
    )
    fit_aditya_bharat_body(r_anc_body["story"], s9.get("city") or "मुंबई", s9.get("agency") or "आर्थिक ब्यूरो", anc_body)

    # --- 4B. Right 3-Column Green Energy Corporate Package (Cols 6..8) ---
    b4r_x0 = grid.col_x0(6)
    b4r_x1 = grid.col_x1(6, 3)
    b4r_cur_y = bot_y0
    s10 = p6_data.get("s10_bot_right") or {}
    b4r_head = s10.get("headline") or "सोलर उपकरण और हरित ऊर्जा में आत्मनिर्भर बनेगा भारत"
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

    b4r_sub = s10.get("subhead") or "पचास गीगावॉट के नए सोलर सेल व टरबाइन विनिर्माण क्लस्टरों में उत्पादन शुरू"
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
    place_red_subject_blurb(0, b4r_x0, round(b4r_by0 + cm(1.5), 2), s10.get("blurb") or "ऊर्जा")
    b4r_body = s10.get("body") or (
        "नवीकरणीय ऊर्जा क्षेत्र में आयात पर निर्भरता समाप्त करने के लिए देश में सोलर मॉड्यूल, पवन ऊर्जा टरबाइन और इलेक्ट्रोलाइजर निर्माण के पंद्रह "
        "बड़े औद्योगिक क्लस्टर शुरू हो गए हैं। इससे न केवल बिजली उत्पादन की लागत घटेगी बल्कि भारत स्वच्छ ऊर्जा उपकरणों का प्रमुख निर्यातक भी बनेगा।"
    )
    fit_aditya_bharat_body(r_b4r_b["story"], s10.get("city") or "नई दिल्ली", s10.get("agency") or "ब्यूरो", b4r_body)

    cmd("edit.deselectAll")
    cmd("view.fitPage", {})

    out_pd = VAULT_DIR / "Aditya_Bharat_Page_06_Karobar_34x53.pagedesigner"
    out_png = VAULT_DIR / "Aditya_Bharat_Page_06_Karobar_34x53.png"
    out_pdf = VAULT_DIR / "Aditya_Bharat_Page_06_Karobar_CMYK_34x53.pdf"
    rpc("app.save", {"path": str(out_pd)})
    rpc("app.export", {"path": str(out_png), "page": 0, "scale": 1.5})
    try:
        rpc("engine.execute", {"command": "file.exportPdf", "params": {"path": str(out_pdf)}})
    except Exception:
        pass

    artifact_png = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\8707c72d-58b0-4715-a099-3efffcd57514\aditya_bharat_page_06_karobar_34x53.png")
    artifact_png.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_png, artifact_png)

    print(
        f"=== ADITYA BHARAT PAGE 06 (KAROBAR - 9 STORIES + MARKET BOX) BUILT IN {time.perf_counter()-t0:.2f}s ===\n"
        f"    Flyer6Col={fl_h_pt}pt | Lead5Col={lead_h_pt}pt (Gray Box in LAST Col 5) | R3_Top={s2_top_pt}pt | R3_Bot={s2_bot_pt}pt\n"
        f"    Band3_4x2Col={b3_pts} | Anchor5Col={anc_h_pt}pt | BotRight3Col={b4r_pt}pt"
    )


if __name__ == "__main__":
    build_aditya_bharat_page6_business()
