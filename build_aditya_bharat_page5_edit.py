# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — PAGE 05 (संपादकीय / EDIT PAGE) MASTER BUILDER
===========================================================================
Replicates the approved Gujarat Samachar Hindi Editorial Page layout adapted
strictly to the Aditya Bharat Master Stylesheet:
  1. Page Size           : 34.0 cm Width x 53.0 cm Height (Outer Margins = 1-1-1-1 cm)
  2. Print Area (Fixed)  : 32.0 cm Width x 51.0 cm Height (8 Columns, 4.0 mm Gutter)
  3. Zone 1 (Masthead)   : 1.5 cm Inside Running Masthead (y = 1.0 .. 2.5 cm, Cols 1..8)
                           - Left: Red Color Box ('FlyerCrimson') with 'संपादकीय' in 20 pt 'DB Hindi 6' White
                           - Center: 'आदित्य भारत' Masthead Logo ('28 pt DB Rasrand Bold', 100% Black)
                           - Right: Dateline ('16 pt DB Hindi Bold') + '05' ('18 pt Times New Roman Bold')
                           - Bottom: 2.0 pt Rule in 60% Gray across all 8 columns
  4. All Headlines & Subheads: 100% Black ('[Black]') — NEVER Red!
                           - Headlines: 'DB Rasrand Bold' (>= 30.0 pt, natural hScale=1.0 with right white space)
                           - Subheads: 'DB Hindi' Bold ('[Black]')
  5. Horizontal Split across 32.0 cm Print Width (10.0 cm Left + 2.0 cm Corridor + 20.0 cm Right):
                           - Left 10.0 cm Strip: Top Editorial + 'जीवन मंत्र' (with 5x5 cm Illus) + 3rd Editorial + 'निष्कर्ष'
                           - Center 2.0 cm Corridor: Segmented Vertical Gray Rule at x = 12.0 cm
                           - Right 20.0 cm Opinion Area:
                             * Top: Daily '॥ श्रीमद्भगवद्गीता ॥' Shlok + Arth + Gray Rule
                             * Layer 1: 3-Col Lead Opinion Article (45.5 pt Headline + Author Photo/Byline + 2-Col Illus)
                             * Layer 2: Two Equal Side-by-Side Articles (30.0 pt Headlines + 5x5 cm Illus)
                             * Layer 3: Left Literary Corner (शेर, नज़्म, ग़ज़ल) + Right Framed Satirical Cartoon ('कटाक्ष')
"""

import json
import math
import os
import shutil
import socket
import subprocess
import sys
import time
import unicodedata
from pathlib import Path
from PIL import Image, ImageChops, ImageOps

sys.stdout.reconfigure(encoding="utf-8")

VAULT_DIR = Path(__file__).resolve().parent
PHOTOS_DIR = VAULT_DIR / "photos"
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
SRC_EDIT_PHOTOS = Path(r"E:\RND\HINDI - TEST\Page_Designer_App\saved_pages\photos")

PORT = 47123
CM_TO_PT = 72.0 / 2.54
MM_TO_PT = CM_TO_PT / 10.0


def cm(val: float) -> float:
    return round(val * CM_TO_PT, 2)


def mm(val: float) -> float:
    return round(val * MM_TO_PT, 2)


def snap_underflow_top(body_y1: float, num_underflow_lines: int = 4) -> float:
    k_last = int((body_y1 - 4.35 - 28.35) // 11.25)
    k_first_underflow = k_last - (num_underflow_lines - 1)
    first_underflow_baseline_y = 28.35 + k_first_underflow * 11.25
    return round(first_underflow_baseline_y - 9.65, 2)


def snap_top_lines_bottom(body_y0: float, num_blocked_lines: int = 3) -> float:
    k_first = int(math.ceil((body_y0 + 8.80 - 28.35) / 11.25))
    k_unblocked = k_first + num_blocked_lines
    unblocked_baseline_y = 28.35 + k_unblocked * 11.25
    return round(unblocked_baseline_y - 9.65, 2)


def snap_frame_bottom_to_baseline(raw_y1: float) -> float:
    k = int(round((raw_y1 - 4.55 - 28.35) / 11.25))
    return round(28.35 + k * 11.25 + 4.55, 2)


def extract_first_devanagari_cluster(text: str) -> tuple[str, str]:
    s = text.lstrip()
    if not s:
        return "", ""
    n = len(s)
    i = 1
    while i < n:
        ch = s[i]
        if ch == "\u094d":
            i += 1
            if i < n and not s[i].isspace():
                i += 1
            continue
        cat = unicodedata.category(ch)
        if (
            cat in ("Mn", "Mc")
            or ("\u0900" <= ch <= "\u0903")
            or ("\u093a" <= ch <= "\u094f")
            or ("\u0951" <= ch <= "\u0957")
            or ("\u0962" <= ch <= "\u0963")
        ):
            i += 1
            continue
        break
    return s[:i], s[i:]


def prepare_cmyk_edit_photo(
    src_name: str,
    dst_name: str,
    box_w_pt: float,
    box_h_pt: float,
    crop_mode: str = "cover",
    trim_white: bool = False,
    centering: tuple = (0.5, 0.5),
) -> Path:
    dst_p = PHOTOS_DIR / dst_name
    src_p = None
    for base in [
        SRC_EDIT_PHOTOS,
        Path(r"E:\RND\HINDI - TEST\photos"),
        Path(r"E:\RND\Gujarat_Samachar\editions\19_Oct_2026\photos"),
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
            raise FileNotFoundError(f"Could not find {src_name}")

    target_w_px = max(400, int(round(box_w_pt * 300.0 / 72.0)))
    target_h_px = max(400, int(round(box_h_pt * 300.0 / 72.0)))
    with Image.open(src_p) as im:
        im_rgb = im.convert("RGB")
        if trim_white:
            bg_white = Image.new("RGB", im_rgb.size, (255, 255, 255))
            diff = ImageChops.difference(im_rgb, bg_white).convert("L")
            diff = diff.point(lambda p: 255 if p > 18 else 0)
            bbox = diff.getbbox()
            if bbox:
                pad = 12
                x0 = max(0, bbox[0] - pad)
                y0 = max(0, bbox[1] - pad)
                x1 = min(im_rgb.width, bbox[2] + pad)
                y1 = min(im_rgb.height, bbox[3] + pad)
                im_rgb = im_rgb.crop((x0, y0, x1, y1))

        if crop_mode == "contain":
            bg = Image.new("RGB", (target_w_px, target_h_px), (255, 255, 255))
            im_copy = im_rgb.copy()
            im_copy.thumbnail((target_w_px, target_h_px), Image.Resampling.LANCZOS)
            ox = (target_w_px - im_copy.width) // 2
            oy = (target_h_px - im_copy.height) // 2
            bg.paste(im_copy, (ox, oy))
            bg.convert("CMYK").save(dst_p, "JPEG", quality=95, dpi=(300, 300))
        else:
            cropped = ImageOps.fit(im_rgb, (target_w_px, target_h_px), method=Image.Resampling.LANCZOS, centering=centering)
            cropped.convert("CMYK").save(dst_p, "JPEG", quality=95, dpi=(300, 300))
    return dst_p


class AdityaBharatPage5EditGrid:
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

        self.print_x0 = self.margin_x_pt
        self.print_y0 = self.margin_y_pt
        self.print_x1 = round(self.margin_x_pt + self.print_w_pt, 2)
        self.print_y1 = round(self.margin_y_pt + self.print_h_pt, 2)

        # Zone 1: 1.5 cm Inside Running Masthead (y = 1.0 .. 2.5 cm)
        self.masthead_h_cm = 1.5
        self.masthead_y0 = self.print_y0
        self.masthead_y1 = round(self.masthead_y0 + cm(self.masthead_h_cm), 2)
        self.content_y0 = round(self.masthead_y1 + mm(3.5), 2)

        # Horizontal Split (10.0 cm Left Strip + 2.0 cm Center Corridor + 20.0 cm Right Opinion Area = 32.0 cm)
        self.left_x0 = self.print_x0
        self.left_x1 = round(self.left_x0 + cm(10.0), 2)
        self.div_x = round(self.left_x1 + cm(1.0), 2)
        self.right_x0 = round(self.left_x1 + cm(2.0), 2)
        self.right_x1 = self.print_x1


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


def place_edit_page_headline_with_whitespace(
    spread_idx: int,
    x0: float,
    cur_y: float,
    x1: float,
    raw_text: str,
    target_lines: int,
    fixed_pt: float,
    font_family: str = "DB Rasrand Bold",
    font_style: str = "Bold",
    fill_swatch: str = "[Black]",
    align: str = "center",
):
    fill_swatch = "[Black]"
    if font_family == "DB Rasrand Bold":
        fixed_pt = max(fixed_pt, 30.0)
    temp_h = cm(6.0)
    lead = round(fixed_pt + 1.0, 2)
    r = cmd("frame.create", {
        "spread": spread_idx,
        "rect": [x0, cur_y, x1, cur_y + temp_h],
        "content": "text",
        "text": raw_text,
    })
    fid, sid = r["id"], r["story"]

    batch([
        {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": font_family,
            "fontStyle": font_style,
            "size": fixed_pt,
            "leading": {"kind": "points", "value": lead},
            "fill": "[Black]",
            "fillTint": 1.0,
            "hScale": 1.0,
            "tracking": 0.0,
        }}},
        {"command": "type.para", "params": {"attrs": {"align": align, "hyphenate": False, "gridAlign": "none"}}},
    ])

    curr_h = temp_h
    st_init = cmd("story.get", {"story": sid})
    rendered_lines = st_init.get("lines") or target_lines
    lo_h = max(14, int(fixed_pt * rendered_lines * 0.78))
    hi_h = max(lo_h + 24, int((fixed_pt + 2.0) * rendered_lines + 36))
    best_h = hi_h
    while lo_h <= hi_h:
        mid_h = (lo_h + hi_h) // 2
        st = batch([
            {"command": "transform.resize", "params": {"ids": [fid], "from": [x0, cur_y, x1, cur_y + curr_h], "to": [x0, cur_y, x1, cur_y + mid_h]}},
            {"command": "story.get", "params": {"story": sid}},
        ])[-1]
        curr_h = mid_h
        if (st.get("lines") or 0) <= rendered_lines and st.get("overset") is None:
            best_h = mid_h
            hi_h = mid_h - 1
        else:
            lo_h = mid_h + 1
    if curr_h != best_h:
        cmd("transform.resize", {"ids": [fid], "from": [x0, cur_y, x1, cur_y + curr_h], "to": [x0, cur_y, x1, cur_y + best_h]})
        curr_h = best_h

    return fid, sid, fixed_pt, curr_h


EXTRA_EDIT_SENTENCES = (
    "\nलोकतांत्रिक व्यवस्था और सामाजिक सरोकारों के बीच संतुलन बनाए रखने के लिए यह आवश्यक है कि नीतियों का क्रियान्वयन धरातल पर पूरी पारदर्शिता और संवेदनशीलता के साथ हो। "
    "जब समाज का अंतिम व्यक्ति विकास की मुख्यधारा से जुड़ता है, तभी राष्ट्र की प्रगति स्थायी और सार्थक रूप लेती है। "
    "आधुनिक युग की चुनौतियों का सामना करने के लिए हमें अपनी सांस्कृतिक जड़ों और वैज्ञानिक दृष्टिकोण दोनों को साथ लेकर आगे बढ़ना होगा। "
    "नागरिकों की सक्रिय भागीदारी, संस्थागत जवाबदेही और दूरदर्शी नेतृत्व ही किसी भी देश को वैश्विक पटल पर नई ऊंचाइयों तक पहुंचाने का सबसे सशक्त माध्यम बनते हैं।"
)


def place_drop_cap_box(x0: float, body_y0: float, dc_text: str) -> None:
    k_first = int(math.ceil((body_y0 + 8.80 - 28.35) / 11.25))
    first_base_y = 28.35 + k_first * 11.25
    dc_y0 = round(first_base_y - 10.5, 2)
    dc_y1 = round(snap_top_lines_bottom(body_y0, num_blocked_lines=3) - 0.5, 2)

    base_chars = sum(1 for c in dc_text if unicodedata.category(c) not in ("Mn", "Cf"))
    dc_w = max(28.0, round(18.0 + base_chars * 10.5, 2))
    dc_x1 = round(x0 + dc_w, 2)

    r_dc = cmd("frame.create", {
        "spread": 0,
        "rect": [x0, dc_y0, dc_x1, dc_y1],
        "content": "text",
        "text": dc_text,
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_dc["id"]], "swatch": "[None]", "tint": 0.0}},
        {"command": "object.stroke", "params": {"ids": [r_dc["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
        {"command": "object.textWrap", "params": {"ids": [r_dc["id"]], "mode": "boundingBox", "offset": [0.0, 0.0, 1.0, 2.5]}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_dc["id"]],
            "columns": 1,
            "inset": [0.0, 0.0, 0.0, 0.0],
            "verticalJustification": "center",
        }},
        {"command": "text.select", "params": {"story": r_dc["story"], "anchor": 0, "focus": 99}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Bold",
            "size": 25.0,
            "leading": {"kind": "points", "value": 25.5},
            "fill": "[Black]",
            "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {
            "align": "center",
            "firstLineIndent": 0.0,
            "gridAlign": "none",
            "hyphenate": False,
        }}},
    ])


def fit_hindi_body_11pt_1125_leading(
    sid: int,
    intro_text: str,
    byline_text: str,
    raw_body: str,
    first_line_indent: float = 8.0,
    intro_size: float = 13.0,
    intro_lead: float = 13.8,
):
    intro_prefix = f"{intro_text.strip()}\n" if intro_text else ""
    byline_prefix = f"{byline_text.strip()}\n" if byline_text else ""
    intro_bytes = len(intro_prefix.encode("utf-8"))
    byline_bytes = len(byline_prefix.encode("utf-8"))

    def apply_style(body_str: str):
        full_txt = intro_prefix + byline_prefix + body_str
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
                "spaceBefore": 0.0,
                "spaceAfter": 0.0,
                "hyphenate": False,
                "gridAlign": "allLines",
                "ruleBelow": {"on": False},
            }}},
        ]
        first_body_nl = body_str.find("\n")
        first_body_end = intro_bytes + byline_bytes + (len(body_str[:first_body_nl].encode("utf-8")) if first_body_nl > 0 else len(body_str.encode("utf-8")))
        if first_body_end > intro_bytes + byline_bytes:
            cmds.extend([
                {"command": "text.select", "params": {"story": sid, "anchor": intro_bytes + byline_bytes, "focus": first_body_end}},
                {"command": "type.para", "params": {"attrs": {"firstLineIndent": 0.0}}},
            ])

        if intro_bytes > 1:
            cmds.extend([
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": intro_bytes - 1}},
                {"command": "type.char", "params": {"attrs": {
                    "fontFamily": "DB Hindi",
                    "fontStyle": "Bold",
                    "size": intro_size,
                    "leading": {"kind": "points", "value": intro_lead},
                    "fill": "[Black]",
                    "fillTint": 1.0,
                }}},
                {"command": "type.para", "params": {"attrs": {
                    "align": "leftJustified",
                    "firstLineIndent": 0.0,
                    "spaceBefore": 0.0,
                    "spaceAfter": 7.0,
                    "gridAlign": "none",
                    "ruleBelow": {
                        "on": True,
                        "weight": 1.5,
                        "color": "ClosingGray",
                        "tint": 1.0,
                        "columnWidth": True,
                        "offset": 4.0,
                    },
                }}},
            ])
        if byline_bytes > 1:
            b0 = intro_bytes
            b1 = intro_bytes + byline_bytes - 1
            cmds.extend([
                {"command": "text.select", "params": {"story": sid, "anchor": b0, "focus": b1}},
                {"command": "type.char", "params": {"attrs": {
                    "fontFamily": "DB Hindi",
                    "fontStyle": "Bold",
                    "size": 10.5,
                    "leading": {"kind": "points", "value": 11.25},
                    "fill": "[Black]",
                    "fillTint": 1.0,
                }}},
                {"command": "type.para", "params": {"attrs": {
                    "align": "left",
                    "firstLineIndent": 0.0,
                    "spaceBefore": 0.0,
                    "spaceAfter": 0.0,
                    "gridAlign": "allLines",
                    "ruleBelow": {"on": False},
                }}},
            ])
        cmds.append({"command": "story.get", "params": {"story": sid}})
        return batch(cmds)[-1]

    ext_text = raw_body.strip()
    st = apply_style(ext_text)
    first_ext = True
    while st.get("overset") is None:
        ext_text = ext_text + (EXTRA_EDIT_SENTENCES if first_ext else " " + EXTRA_EDIT_SENTENCES.lstrip())
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


def build_aditya_bharat_page5_edit():
    t0 = time.perf_counter()
    connect_page_designer()
    grid = AdityaBharatPage5EditGrid()

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
            "title": "आदित्य भारत — पेज 04 संपादकीय (34x53 सेमी | प्रिंट एरिया 32x51 सेमी)",
        }},
        {"command": "document.preferences", "params": {
            "baselineGrid": {
                "start": grid.margin_y_pt,
                "increment": 11.25,
                "relativeTo": "topOfPage",
            }
        }},
        {"command": "swatch.create", "params": {"name": "FlyerCrimson", "color": "#c4121a"}},
        {"command": "swatch.create", "params": {"name": "EditPointerBg", "color": "#f2f2f2"}},
        {"command": "swatch.create", "params": {"name": "SoftGrayBg", "color": "#f4f4f4"}},
        {"command": "swatch.create", "params": {"name": "ClosingGray", "color": "#808285"}},
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
        "text": "संपादकीय",
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
        "text": "04",
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
    # PART A: LEFT 10.0 CM EDITORIAL STRIP (x = 1.0 cm .. 11.0 cm)
    # ==========================================================================
    lx0, lx1 = grid.left_x0, grid.left_x1
    l_cur_y = grid.content_y0

    # --- A1: Top Main Editorial (>= 30.0 pt DB Rasrand Bold, 100% Black) ---
    edit1_head = "ग्रामीण अर्थव्यवस्था को\nनई रफ्तार देने का समय"
    _, _, ed1_h_pt, ed1_hh = place_edit_page_headline_with_whitespace(
        0, lx0, l_cur_y, lx1,
        raw_text=edit1_head,
        target_lines=2,
        fixed_pt=32.0,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        align="center",
    )
    ed1_body_y0 = round(l_cur_y + ed1_hh + 1.0, 2)
    ed1_body_y1 = snap_frame_bottom_to_baseline(cm(16.85))

    edit1_raw = (
        "संतुलित और समावेशी आर्थिक विकास की असली कसौटी यही है कि देश के गांवों, कस्बों और अन्नदाताओं की झोली में "
        "समृद्धि की कितनी किरणें पहुंचती हैं। हाल के वर्षों में बुनियादी ढांचे, राजमार्गों और डिजिटल भुगतान के विस्तार ने "
        "ग्रामीण भारत की आकांक्षाओं को एक नया आकाश दिया है, परंतु कृषि उपज के उचित मूल्य और स्थानीय स्तर पर रोजगार "
        "सृजन की चुनौती अब भी नीति-निर्माताओं से ठोस समाधान मांगती है।\n"
        "दस राज्यों में आधुनिक एग्री-एक्सपोर्ट जोन और पांच सौ फूड प्रोसेसिंग क्लस्टर स्थापित करने की पहल इसी दिशा में एक "
        "दूरगामी कदम है। जब किसान केवल कच्चा अनाज बेचने के बजाय प्रसंस्कृत खाद्य उत्पादों की मूल्य-श्रृंखला का सीधा "
        "हिस्सा बनेगा, तभी उसकी आय में स्थायी वृद्धि संभव हो सकेगी।\n"
        "इसके साथ ही ग्रामीण युवाओं को आधुनिक कृषि तकनीक, सौर ऊर्जा आधारित कोल्ड स्टोरेज और सहकारी विपणन से जोड़ना "
        "अनिवार्य है। यदि जिला स्तर पर ही भंडारण और निर्यात की सुगम व्यवस्था खड़ी हो जाए, तो न केवल फसल की बर्बादी "
        "रुकेगी बल्कि गांवों से महानगरों की ओर होने वाला मजबूरी का पलायन भी थमेगा।"
    )
    ed1_dc, ed1_rem = extract_first_devanagari_cluster(edit1_raw)

    r_ed1_body = cmd("frame.create", {
        "spread": 0,
        "rect": [lx0, ed1_body_y0, lx1, ed1_body_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_ed1_body["id"]],
        "columns": 1,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_drop_cap_box(lx0, ed1_body_y0, ed1_dc)
    fit_hindi_body_11pt_1125_leading(r_ed1_body["story"], "", "", ed1_rem)

    # --- A2: Gap + 2.0 pt Horizontal Gray Rule ---
    ed1_rule_y = round(ed1_body_y1 + mm(4.5), 2)
    r_ed1_rule = cmd("line.create", {"spread": 0, "a": [lx0, ed1_rule_y], "b": [lx1, ed1_rule_y]})
    cmd("object.stroke", {"ids": [r_ed1_rule["id"]], "swatch": "ClosingGray", "weight": 2.0, "tint": 1.0})

    # --- A3: 'जीवन मंत्र' Column (Reverse Header + 30 pt Headline + Drop Cap + 5x5 cm Left Illus) ---
    jm_y0 = round(ed1_body_y1 + mm(8.5), 2)
    jm_hdr_h = cm(0.75)
    jm_hdr_y1 = round(jm_y0 + jm_hdr_h, 2)

    r_jm_hdr = cmd("frame.create", {
        "spread": 0,
        "rect": [lx0, jm_y0, lx1, jm_hdr_y1],
        "content": "text",
        "text": "जीवन मंत्र  •  आत्मचिंतन एवं प्रेरणा",
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_jm_hdr["id"]], "swatch": "FlyerCrimson", "tint": 1.0}},
        {"command": "object.stroke", "params": {"ids": [r_jm_hdr["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_jm_hdr["id"]],
            "columns": 1,
            "inset": [0.0, 8.0, 0.0, 8.0],
            "verticalJustification": "center",
        }},
        {"command": "text.select", "params": {"story": r_jm_hdr["story"], "anchor": 0, "focus": 999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Bold",
            "size": 14.5,
            "leading": {"kind": "points", "value": 15.0},
            "fill": "[Paper]",
            "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "hyphenate": False, "gridAlign": "none"}}},
    ])

    jm_head_y0 = round(jm_hdr_y1 + 4.0, 2)
    jm_head = "धैर्य और आत्मबल से ही\nछंटता है संघर्षों का अंधकार"
    _, _, jm_h_pt, jm_hh = place_edit_page_headline_with_whitespace(
        0, lx0, jm_head_y0, lx1,
        raw_text=jm_head,
        target_lines=2,
        fixed_pt=30.0,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        align="center",
    )
    jm_body_y0 = round(jm_head_y0 + jm_hh + 1.0, 2)
    jm_body_y1 = snap_frame_bottom_to_baseline(cm(41.80))

    r_jm_body = cmd("frame.create", {
        "spread": 0,
        "rect": [lx0, jm_body_y0, lx1, jm_body_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_jm_body["id"]],
        "columns": 1,
        "verticalJustification": "top",
        "columnRule": False,
    })

    jm_raw = (
        "जीवन की यात्रा केवल फूलों की सेज नहीं है, बल्कि यह उन अनगिनत उतार-चढ़ावों की पाठशाला है जहां हर चुनौती "
        "मनुष्य के भीतर छिपे सामर्थ्य को तराशने आती है। अक्सर हम बाहरी परिस्थितियों के प्रतिकूल होते ही विचलित हो "
        "उठते हैं और अपने लक्ष्य से भटकने लगते हैं, जबकि इतिहास साक्षी है कि महान उपलब्धियां उन्हीं के हिस्से में "
        "आई हैं जिन्होंने तूफानों के बीच भी अपने मन के दीप को बुझने नहीं दिया।\n"
        "जिस प्रकार विशाल वटवृक्ष अपनी गहरी जड़ों के बल पर भीषण आंधियों का सामना करता है और उगता हुआ सूर्य "
        "अंधकार की घनी चादर को चीरकर संसार को आलोकित करता है, ठीक उसी प्रकार हमारे भीतर का सकारात्मक संकल्प "
        "कठिन से कठिन समय को भी अवसर में बदलने की शक्ति रखता है। जब हम अपनी तुलना दूसरों से करना छोड़कर स्वयं "
        "को प्रतिदिन थोड़ा बेहतर बनाने का अभ्यास शुरू करते हैं, तो मन का भय स्वतः समाप्त होने लगता है।\n"
        "सच्ची शांति और सफलता बाहरी शोरगुल में नहीं, अपितु आत्मअनुशासन, करुणा और निरंतर कर्मठता में निवास करती है। "
        "हर सुबह हमें एक नया पन्ना देती है; यदि हम बीते कल की असफलताओं का बोझ उतारकर उत्साह और कृतज्ञता के साथ "
        "पहला कदम बढ़ाएं, तो कोई भी शिखर अजेय नहीं रह जाता।"
    )
    jm_dc, jm_rem = extract_first_devanagari_cluster(jm_raw)
    place_drop_cap_box(lx0, jm_body_y0, jm_dc)

    jm_illus_y0 = round(snap_top_lines_bottom(jm_body_y0, num_blocked_lines=5) + 2.0, 2)
    jm_illus_w = cm(4.8)
    jm_illus_h = cm(4.8)
    jm_illus_x0 = lx0
    jm_illus_x1 = round(lx0 + jm_illus_w, 2)
    jm_illus_y1 = round(jm_illus_y0 + jm_illus_h, 2)
    jm_target_bot_wrap = snap_top_lines_bottom(jm_body_y0, num_blocked_lines=17)
    jm_bot_off = max(1.5, round(jm_target_bot_wrap - jm_illus_y1, 2))

    jm_illus_path = prepare_cmyk_edit_photo("p4_jeevan_mantra_illus.jpg", "ab_p5_jm_cmyk.jpg", jm_illus_w, jm_illus_h)
    r_jm_illus = cmd("frame.create", {
        "spread": 0,
        "rect": [jm_illus_x0, jm_illus_y0, jm_illus_x1, jm_illus_y1],
        "content": "graphic",
    })
    batch([
        {"command": "file.place", "params": {"frame": r_jm_illus["id"], "path": str(jm_illus_path)}},
        {"command": "object.fit", "params": {"ids": [r_jm_illus["id"]], "mode": "fillProportionally"}},
        {"command": "object.stroke", "params": {"ids": [r_jm_illus["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0}},
        {"command": "object.textWrap", "params": {"ids": [r_jm_illus["id"]], "mode": "boundingBox", "offset": [1.5, 0.0, jm_bot_off, 6.0]}},
    ])
    fit_hindi_body_11pt_1125_leading(r_jm_body["story"], "", "", jm_rem)

    # --- A4: Gap + 2.0 pt Gray Rule + 3rd Editorial Item + Bottom 2-Line Bold 'निष्कर्ष' ---
    jm_rule_y = round(jm_body_y1 + mm(3.5), 2)
    r_jm_rule = cmd("line.create", {"spread": 0, "a": [lx0, jm_rule_y], "b": [lx1, jm_rule_y]})
    cmd("object.stroke", {"ids": [r_jm_rule["id"]], "swatch": "ClosingGray", "weight": 2.0, "tint": 1.0})

    ed3_y0 = round(jm_rule_y + mm(3.5), 2)
    ed3_head = "नागरिक अनुशासन से ही\nसंवरेगा शहरों का भविष्य"
    _, _, ed3_h_pt, ed3_hh = place_edit_page_headline_with_whitespace(
        0, lx0, ed3_y0, lx1,
        raw_text=ed3_head,
        target_lines=2,
        fixed_pt=30.0,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        align="center",
    )
    ed3_body_y0 = round(ed3_y0 + ed3_hh + 1.0, 2)

    nishkarsh_h = cm(1.30)
    nishkarsh_y1 = snap_frame_bottom_to_baseline(grid.print_y1)
    nishkarsh_y0 = round(nishkarsh_y1 - nishkarsh_h, 2)
    ed3_body_y1 = snap_frame_bottom_to_baseline(round(nishkarsh_y0 - mm(3.5), 2))

    ed3_raw = (
        "आधुनिक महानगरों में फ्लाईओवर, मेट्रो और स्मार्ट लाइटिंग का जाल बिछाना जितना जरूरी है, उतना ही आवश्यक है "
        "सार्वजनिक संपत्ति और पर्यावरण के प्रति नागरिकों की अपनी जिम्मेदारी का बोध। केवल सरकारी अभियानों या जुर्माने "
        "के डर से कोई भी शहर लंबे समय तक स्वच्छ और सुव्यवस्थित नहीं रह सकता।\n"
        "जब हर परिवार कचरा प्रबंधन, जल संरक्षण और यातायात नियमों के पालन को अपने दैनिक आचरण का अभिन्न हिस्सा "
        "बनाएगा, तभी हमारे नगर वास्तव में विश्वस्तरीय और आने वाली पीढ़ियों के लिए सुरक्षित बन सकेंगे।"
    )
    ed3_dc, ed3_rem = extract_first_devanagari_cluster(ed3_raw)

    r_ed3_body = cmd("frame.create", {
        "spread": 0,
        "rect": [lx0, ed3_body_y0, lx1, ed3_body_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_ed3_body["id"]],
        "columns": 1,
        "verticalJustification": "top",
        "columnRule": False,
    })
    place_drop_cap_box(lx0, ed3_body_y0, ed3_dc)
    fit_hindi_body_11pt_1125_leading(r_ed3_body["story"], "", "", ed3_rem)

    nish_rule_y = round(nishkarsh_y0 - 2.0, 2)
    r_nish_rule = cmd("line.create", {"spread": 0, "a": [lx0, nish_rule_y], "b": [lx1, nish_rule_y]})
    cmd("object.stroke", {"ids": [r_nish_rule["id"]], "swatch": "[Black]", "weight": 1.5, "tint": 0.75})

    nish_text = (
        "निष्कर्ष : नीतिगत सुधारों की सार्थकता तभी सिद्ध होती है जब शासन की संवेदनशीलता "
        "और नागरिकों का कर्तव्य-बोध मिलकर राष्ट्र निर्माण की धुरी बनें।"
    )
    r_nish = cmd("frame.create", {
        "spread": 0,
        "rect": [lx0, nishkarsh_y0, lx1, nishkarsh_y1],
        "content": "text",
        "text": nish_text,
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_nish["id"]], "swatch": "EditPointerBg", "tint": 1.0}},
        {"command": "object.stroke", "params": {"ids": [r_nish["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 0.6}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_nish["id"]],
            "columns": 1,
            "inset": [3.0, 6.0, 3.0, 6.0],
            "verticalJustification": "center",
        }},
        {"command": "text.select", "params": {"story": r_nish["story"], "anchor": 0, "focus": 999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Bold",
            "size": 11.4,
            "leading": {"kind": "points", "value": 12.8},
            "fill": "[Black]",
            "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {
            "align": "leftJustified",
            "firstLineIndent": 0.0,
            "gridAlign": "none",
            "hyphenate": False,
        }}},
    ])

    # ==========================================================================
    # PART B: RIGHT 20.0 CM MAIN OPINION AREA (x = 13.0 cm .. 33.0 cm)
    # ==========================================================================
    rx0, rx1 = grid.right_x0, grid.right_x1
    bot_y1 = snap_frame_bottom_to_baseline(grid.print_y1)

    # --- TOP OF RIGHT 20 CM ZONE: DAILY "श्रीमद्भगवद्गीता" SHLOK + GRAY RULE BELOW ARTH ---
    geeta_y0 = grid.content_y0
    geeta_cx = round((rx0 + rx1) / 2.0, 2)

    title_w = cm(6.40)
    title_h = cm(0.95)
    title_x0 = round(geeta_cx - title_w / 2.0, 2)
    title_x1 = round(geeta_cx + title_w / 2.0, 2)
    title_y0 = geeta_y0
    title_y1 = round(title_y0 + title_h, 2)

    r_geeta_title = cmd("frame.create", {
        "spread": 0,
        "rect": [title_x0, title_y0, title_x1, title_y1],
        "content": "text",
        "text": "॥ श्रीमद्भगवद्गीता ॥",
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_geeta_title["id"]], "swatch": "[None]", "tint": 0.0}},
        {"command": "object.stroke", "params": {"ids": [r_geeta_title["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_geeta_title["id"]],
            "columns": 1,
            "verticalJustification": "center",
        }},
        {"command": "text.select", "params": {"story": r_geeta_title["story"], "anchor": 0, "focus": 999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Rasrand Bold",
            "fontStyle": "Bold",
            "size": 22.0,
            "leading": {"kind": "points", "value": 23.0},
            "fill": "[Black]",
            "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "hyphenate": False, "gridAlign": "none"}}},
    ])

    flw_w = cm(2.00)
    flw_h = cm(1.30)
    flw_y0 = round(title_y0 - mm(1.0), 2)
    flw_y1 = round(flw_y0 + flw_h, 2)
    flw_path = prepare_cmyk_edit_photo(
        "p4_geeta_flower_vector.jpg",
        "ab_p5_geeta_flower_cmyk.jpg",
        flw_w,
        flw_h,
        crop_mode="contain",
        trim_white=True,
    )

    flw_l_x1 = round(title_x0 - mm(1.0), 2)
    flw_l_x0 = round(flw_l_x1 - flw_w, 2)
    r_flw_l = cmd("frame.create", {"spread": 0, "rect": [flw_l_x0, flw_y0, flw_l_x1, flw_y1], "content": "graphic"})
    flw_r_x0 = round(title_x1 + mm(1.0), 2)
    flw_r_x1 = round(flw_r_x0 + flw_w, 2)
    r_flw_r = cmd("frame.create", {"spread": 0, "rect": [flw_r_x0, flw_y0, flw_r_x1, flw_y1], "content": "graphic"})
    batch([
        {"command": "file.place", "params": {"frame": r_flw_l["id"], "path": str(flw_path)}},
        {"command": "object.fit", "params": {"ids": [r_flw_l["id"]], "mode": "fillProportionally"}},
        {"command": "object.stroke", "params": {"ids": [r_flw_l["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
        {"command": "file.place", "params": {"frame": r_flw_r["id"], "path": str(flw_path)}},
        {"command": "object.fit", "params": {"ids": [r_flw_r["id"]], "mode": "fillProportionally"}},
        {"command": "object.stroke", "params": {"ids": [r_flw_r["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
    ])

    shlok_box_y0 = round(title_y1 + 1.5, 2)
    shlok_box_y1 = round(shlok_box_y0 + cm(2.15), 2)
    sanskrit_shlok = "“कर्मण्येवाधिकारस्ते मा फलेषु कदाचन। मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥”\n"
    hindi_arth = (
        "अर्थ : मनुष्य का अधिकार केवल कर्म करने में है, उसके फल में कदापि नहीं। इसलिए फल की आसक्ति "
        "छोड़कर अपने कर्तव्य-कर्म का निष्ठापूर्वक पालन करना ही सच्चा जीवन-धर्म है।"
    )
    geeta_full_text = sanskrit_shlok + hindi_arth
    shlok_b = len(sanskrit_shlok.encode("utf-8"))
    arth_lbl_b = shlok_b + len("अर्थ : ".encode("utf-8"))

    r_geeta_body = cmd("frame.create", {
        "spread": 0,
        "rect": [round(rx0 + cm(0.4), 2), shlok_box_y0, round(rx1 - cm(0.4), 2), shlok_box_y1],
        "content": "text",
        "text": geeta_full_text,
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_geeta_body["id"]], "swatch": "[None]", "tint": 0.0}},
        {"command": "object.stroke", "params": {"ids": [r_geeta_body["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_geeta_body["id"]],
            "columns": 1,
            "inset": [0.0, 4.0, 0.0, 4.0],
            "verticalJustification": "center",
        }},
        {"command": "text.select", "params": {"story": r_geeta_body["story"], "anchor": 0, "focus": 9999}},
        {"command": "type.para", "params": {
            "attrs": {
                "align": "center",
                "firstLineIndent": 0.0,
                "spaceBefore": 0.0,
                "spaceAfter": 3.5,
                "gridAlign": "none",
                "hyphenate": False,
            }
        }},
        {"command": "text.select", "params": {"story": r_geeta_body["story"], "anchor": 0, "focus": shlok_b - 1}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Bold",
            "size": 16.0,
            "leading": {"kind": "points", "value": 18.0},
            "fill": "[Black]",
            "fillTint": 1.0,
        }}},
        {"command": "text.select", "params": {"story": r_geeta_body["story"], "anchor": shlok_b, "focus": 9999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Regular",
            "size": 14.0,
            "leading": {"kind": "points", "value": 15.8},
            "fill": "[Black]",
            "fillTint": 1.0,
        }}},
        {"command": "text.select", "params": {"story": r_geeta_body["story"], "anchor": shlok_b, "focus": arth_lbl_b}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Bold",
            "size": 14.0,
            "leading": {"kind": "points", "value": 15.8},
            "fill": "[Black]",
            "fillTint": 1.0,
        }}},
    ])

    geeta_rule_y = round(shlok_box_y1 + mm(2.0), 2)
    r_geeta_sep = cmd("line.create", {"spread": 0, "a": [rx0, geeta_rule_y], "b": [rx1, geeta_rule_y]})
    cmd("object.stroke", {"ids": [r_geeta_sep["id"]], "swatch": "ClosingGray", "weight": 1.5, "tint": 1.0})

    # --- LAYER 1: 3-COLUMN LEAD OPINION ARTICLE ---
    r_cur_y = round(geeta_rule_y + mm(2.5), 2)

    lead_subhead = "विशेष मंथन  •  वैश्विक अनिश्चितता के दौर में भारत की तकनीकी छलांग"
    _, _, _, l_sub_h = place_edit_page_headline_with_whitespace(
        0, rx0, r_cur_y, rx1,
        raw_text=lead_subhead,
        target_lines=1,
        fixed_pt=14.0,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        align="center",
    )
    r_cur_y = round(r_cur_y + l_sub_h + 0.5, 2)

    lead_headline = "डिजिटल नवाचार और हरित उद्योग से\nबनेगा विकसित भारत का नया मॉडल"
    _, _, lead_h_pt, lead_hh = place_edit_page_headline_with_whitespace(
        0, rx0, r_cur_y, rx1,
        raw_text=lead_headline,
        target_lines=2,
        fixed_pt=45.5,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        align="center",
    )
    lead_body_y0 = round(r_cur_y + lead_hh + 1.0, 2)
    lead_body_y1 = snap_frame_bottom_to_baseline(cm(26.75))

    r_lead_body = cmd("frame.create", {
        "spread": 0,
        "rect": [rx0, lead_body_y0, rx1, lead_body_y1],
        "content": "text",
        "text": "",
    })
    cmd("object.textFrameOptions", {
        "ids": [r_lead_body["id"]],
        "columns": 3,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })

    r_col_w = ((rx1 - rx0) - 2 * grid.gutter_pt) / 3.0
    r_col1_x0 = rx0
    r_col1_x1 = round(r_col1_x0 + r_col_w, 2)
    r_col2_x0 = round(r_col1_x1 + grid.gutter_pt, 2)

    auth_w = cm(2.60)
    auth_h = cm(2.90)
    auth_x0 = r_col1_x0
    auth_x1 = round(auth_x0 + auth_w, 2)
    auth_y0 = lead_body_y0
    auth_y1 = round(auth_y0 + auth_h, 2)
    auth_wrap_target_y1 = snap_top_lines_bottom(lead_body_y0, num_blocked_lines=8)
    auth_bot_off = max(2.0, round(auth_wrap_target_y1 - auth_y1, 2))

    auth_img_path = prepare_cmyk_edit_photo("p4_author_photo.jpg", "ab_p5_author_cmyk.jpg", auth_w, auth_h, crop_mode="cover")
    r_auth_ph = cmd("frame.create", {
        "spread": 0,
        "rect": [auth_x0, auth_y0, auth_x1, auth_y1],
        "content": "graphic",
    })
    batch([
        {"command": "file.place", "params": {"frame": r_auth_ph["id"], "path": str(auth_img_path)}},
        {"command": "object.fit", "params": {"ids": [r_auth_ph["id"]], "mode": "fillProportionally"}},
        {"command": "object.stroke", "params": {"ids": [r_auth_ph["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0}},
        {"command": "object.textWrap", "params": {"ids": [r_auth_ph["id"]], "mode": "boundingBox", "offset": [0.0, 0.0, auth_bot_off, 4.0]}},
    ])

    by_x0 = round(auth_x1 + 5.5, 2)
    by_x1 = r_col1_x1
    by_y0 = auth_y0
    by_y1 = auth_y1
    auth_name_line = "डॉ. राजीव रंजन\n"
    auth_desig_line = "वरिष्ठ आर्थिक एवं\nनीति विश्लेषक,\nनई दिल्ली"
    auth_full_txt = auth_name_line + auth_desig_line
    name_b = len(auth_name_line.encode("utf-8"))

    r_auth_byline = cmd("frame.create", {
        "spread": 0,
        "rect": [by_x0, by_y0, by_x1, by_y1],
        "content": "text",
        "text": auth_full_txt,
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_auth_byline["id"]], "swatch": "[None]", "tint": 0.0}},
        {"command": "object.stroke", "params": {"ids": [r_auth_byline["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
        {"command": "object.textWrap", "params": {"ids": [r_auth_byline["id"]], "mode": "boundingBox", "offset": [0.0, 0.0, auth_bot_off, 0.0]}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_auth_byline["id"]],
            "columns": 1,
            "inset": [2.0, 2.0, 2.0, 0.0],
            "verticalJustification": "center",
        }},
        {"command": "text.select", "params": {"story": r_auth_byline["story"], "anchor": 0, "focus": 999}},
        {"command": "type.para", "params": {"attrs": {"align": "left", "firstLineIndent": 0.0, "spaceBefore": 0.0, "spaceAfter": 2.5, "gridAlign": "none", "hyphenate": False}}},
        {"command": "text.select", "params": {"story": r_auth_byline["story"], "anchor": 0, "focus": name_b - 1}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Bold",
            "size": 13.0,
            "leading": {"kind": "points", "value": 14.5},
            "fill": "[Black]",
            "fillTint": 1.0,
        }}},
        {"command": "text.select", "params": {"story": r_auth_byline["story"], "anchor": name_b, "focus": 999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Bold",
            "size": 11.0,
            "leading": {"kind": "points", "value": 12.2},
            "fill": "[Black]",
            "fillTint": 0.65,
        }}},
    ])

    auth_rule_y = round(auth_y1 + 2.5, 2)
    r_auth_rule = cmd("line.create", {"spread": 0, "a": [r_col1_x0, auth_rule_y], "b": [r_col1_x1, auth_rule_y]})
    cmd("object.stroke", {"ids": [r_auth_rule["id"]], "swatch": "ClosingGray", "weight": 1.0, "tint": 0.85})

    l_illus_x0 = r_col2_x0
    l_illus_x1 = rx1
    l_illus_y0 = lead_body_y0
    l_illus_h = cm(7.5)
    l_illus_y1 = round(l_illus_y0 + l_illus_h, 2)

    l_cap_h = 14.0
    l_cap_y0 = round(l_illus_y1 + 2.0, 2)
    l_cap_y1 = round(l_cap_y0 + l_cap_h, 2)
    l_target_wrap_y1 = snap_top_lines_bottom(lead_body_y0, num_blocked_lines=21)
    l_cap_bot_off = max(2.0, round(l_target_wrap_y1 - l_cap_y1, 2))

    lead_illus_path = prepare_cmyk_edit_photo(
        "p4_lead_illus.jpg",
        "ab_p5_lead_illus_cmyk.jpg",
        l_illus_x1 - l_illus_x0,
        l_illus_y1 - l_illus_y0,
        crop_mode="cover",
        centering=(0.5, 0.85),
    )
    r_lead_illus = cmd("frame.create", {
        "spread": 0,
        "rect": [l_illus_x0, l_illus_y0, l_illus_x1, l_illus_y1],
        "content": "graphic",
    })
    batch([
        {"command": "file.place", "params": {"frame": r_lead_illus["id"], "path": str(lead_illus_path)}},
        {"command": "object.fit", "params": {"ids": [r_lead_illus["id"]], "mode": "fillProportionally"}},
        {"command": "object.stroke", "params": {"ids": [r_lead_illus["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0}},
        {"command": "object.textWrap", "params": {"ids": [r_lead_illus["id"]], "mode": "boundingBox", "offset": [0.0, 0.0, 2.0, 0.0]}},
    ])

    r_lead_cap = cmd("frame.create", {
        "spread": 0,
        "rect": [l_illus_x0, l_cap_y0, l_illus_x1, l_cap_y1],
        "content": "text",
        "text": "तकनीकी आत्मनिर्भरता और औद्योगिक प्रगति के संगम से उभरती नई भारतीय अर्थव्यवस्था। — इलस्ट्रेशन",
    })
    batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_lead_cap["id"]], "columns": 1, "verticalJustification": "top"}},
        {"command": "object.textWrap", "params": {"ids": [r_lead_cap["id"]], "mode": "boundingBox", "offset": [0.0, 0.0, l_cap_bot_off, 0.0]}},
        {"command": "text.select", "params": {"story": r_lead_cap["story"], "anchor": 0, "focus": 999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi 7", "fontStyle": "Bold", "size": 10.0,
            "leading": {"kind": "points", "value": 10.2}, "fill": "[Black]", "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "left", "firstLineIndent": 0.0, "hyphenate": False}}},
    ])

    lead_8line_intro = (
        "इक्कीसवीं सदी के तीसरे दशक में जब वैश्विक आपूर्ति श्रृंखलाएं और पारंपरिक आर्थिक शक्तियां गहरे "
        "बदलाव के दौर से गुजर रही हैं, तब भारत के सामने डिजिटल पब्लिक इंफ्रास्ट्रक्चर, सेमीकंडक्टर विनिर्माण और "
        "हरित ऊर्जा के बल पर विश्व का नया विकास इंजन बनने का ऐतिहासिक अवसर उपस्थित है।"
    )
    lead_body_copy = (
        "बीते एक दशक में भारत ने जिस गति से डिजिटल पहचान, तात्कालिक भुगतान प्रणाली और डेटा सशक्तिकरण का लोकतांत्रिक "
        "ढांचा खड़ा किया है, उसने पूरी दुनिया के अर्थशास्त्रियों को चकित किया है। आज गांव के छोटे दुकानदार से लेकर "
        "महानगर के बड़े उद्यमी तक एक ही डिजिटल राजमार्ग से जुड़े हैं। किंतु केवल सेवा क्षेत्र और उपभोक्ता बाजार के "
        "भरोसे कोई भी विशाल राष्ट्र लंबे समय तक उच्च विकास दर कायम नहीं रख सकता; इसके लिए विनिर्माण और अनुसंधान "
        "की मजबूत नींव अनिवार्य है।\n"
        "इसी आवश्यकता को समझते हुए देश में हाई-स्पीड इंडस्ट्रियल कॉरिडोर, सेमीकंडक्टर फाउंड्री, रक्षा उत्पादन और "
        "ग्रीन हाइड्रोजन मिशन को सर्वोच्च प्राथमिकता दी जा रही है। जब हमारे बंदरगाहों, रेल गलियारों और औद्योगिक "
        "क्लस्टरों के बीच माल ढुलाई की लागत घटेगी, तभी भारतीय उत्पाद अंतरराष्ट्रीय बाजार में चीन और वियतनाम जैसे "
        "देशों से सीधी प्रतिस्पर्धा कर पाएंगे।\n"
        "दूसरी महत्वपूर्ण कड़ी हमारे विश्वविद्यालयों और औद्योगिक इकाइयों के बीच सीधा संवाद स्थापित करने की है। कृत्रिम "
        "बुद्धिमत्ता, रोबोटिक्स, अंतरिक्ष प्रौद्योगिकी और जैव-तकनीक के क्षेत्र में भारतीय युवा स्टार्टअप्स ने सिद्ध कर "
        "दिया है कि यदि उन्हें प्रयोगशालाओं और जोखिम पूंजी का सही संबल मिले, तो वे कम लागत में विश्वस्तरीय स्वदेशी "
        "समाधान तैयार कर सकते हैं।"
    )
    fit_hindi_body_11pt_1125_leading(
        r_lead_body["story"],
        lead_8line_intro,
        "",
        lead_body_copy,
        intro_size=12.2,
        intro_lead=13.0,
    )

    r_sep1_y = round(lead_body_y1 + mm(2.5), 2)
    r_sep1 = cmd("line.create", {"spread": 0, "a": [rx0, r_sep1_y], "b": [rx1, r_sep1_y]})
    cmd("object.stroke", {"ids": [r_sep1["id"]], "swatch": "ClosingGray", "weight": 1.5, "tint": 1.0})

    # ==========================================================================
    # PART B — LAYER 2: TWO EQUAL SIDE-BY-SIDE ARTICLES (30.0 pt Headlines!)
    # ==========================================================================
    l2_y0 = round(r_sep1_y + mm(2.5), 2)
    l2_y1 = snap_frame_bottom_to_baseline(cm(41.80))

    mid_gap_w = cm(0.80)
    mid_art_w = round(((rx1 - rx0) - mid_gap_w) / 2.0, 2)
    mid_l_x0 = rx0
    mid_l_x1 = round(mid_l_x0 + mid_art_w, 2)
    mid_div_x = round(mid_l_x1 + mid_gap_w / 2.0, 2)
    mid_r_x0 = round(mid_l_x1 + mid_gap_w, 2)
    mid_r_x1 = rx1

    def build_equal_middle_article(
        ax0: float,
        ax1: float,
        ay0: float,
        ay1: float,
        subhead_str: str,
        headline_str: str,
        intro_str: str,
        byline_str: str,
        body_str: str,
        illus_src: str,
        illus_dst: str,
    ):
        cy = ay0
        _, _, _, sh_h = place_edit_page_headline_with_whitespace(
            0, ax0, cy, ax1,
            raw_text=subhead_str,
            target_lines=1,
            fixed_pt=12.6,
            font_family="DB Hindi",
            font_style="Bold",
            fill_swatch="[Black]",
            align="center",
        )
        cy = round(cy + sh_h + 0.5, 2)
        _, _, h_pt, hh = place_edit_page_headline_with_whitespace(
            0, ax0, cy, ax1,
            raw_text=headline_str,
            target_lines=2,
            fixed_pt=30.0,
            font_family="DB Rasrand Bold",
            font_style="Bold",
            fill_swatch="[Black]",
            align="center",
        )
        aby0 = round(cy + hh + 2.0, 2)
        aby1 = ay1

        r_ab = cmd("frame.create", {
            "spread": 0,
            "rect": [ax0, aby0, ax1, aby1],
            "content": "text",
            "text": "",
        })
        cmd("object.textFrameOptions", {
            "ids": [r_ab["id"]],
            "columns": 2,
            "gutter": grid.gutter_pt,
            "verticalJustification": "top",
            "columnRule": False,
        })

        il_w = cm(4.6)
        il_h = cm(4.6)
        il_x1 = ax1
        il_x0 = round(il_x1 - il_w, 2)
        il_y0 = aby0
        il_y1 = round(il_y0 + il_h, 2)
        il_target_wrap_y1 = snap_top_lines_bottom(aby0, num_blocked_lines=12)
        il_bot_off = max(1.5, round(il_target_wrap_y1 - il_y1, 2))

        il_path = prepare_cmyk_edit_photo(illus_src, illus_dst, il_w, il_h)
        r_il = cmd("frame.create", {
            "spread": 0,
            "rect": [il_x0, il_y0, il_x1, il_y1],
            "content": "graphic",
        })
        batch([
            {"command": "file.place", "params": {"frame": r_il["id"], "path": str(il_path)}},
            {"command": "object.fit", "params": {"ids": [r_il["id"]], "mode": "fillProportionally"}},
            {"command": "object.stroke", "params": {"ids": [r_il["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0}},
            {"command": "object.textWrap", "params": {"ids": [r_il["id"]], "mode": "boundingBox", "offset": [0.0, 5.0, il_bot_off, 0.0]}},
        ])

        fit_hindi_body_11pt_1125_leading(
            r_ab["story"],
            intro_str,
            byline_str,
            body_str,
            intro_size=12.0,
            intro_lead=12.8,
        )
        return h_pt

    m1_pt = build_equal_middle_article(
        mid_l_x0, mid_l_x1, l2_y0, l2_y1,
        subhead_str="पर्यावरण सरोकार  •  प्रकृति और शहरीकरण",
        headline_str="शहरों में हरित क्षेत्रों और\nजल स्रोतों को बचाने की पहल",
        intro_str="शहरी विकास की दौड़ में यदि झीलों, तालाबों और हरित पट्टियों की अनदेखी हुई तो जलवायु संकट गहराएगा।",
        byline_str="पंकज चतुर्वेदी | पर्यावरण चिंतक",
        body_str=(
            "देश के छोटे-बड़े शहरों में जिस तेजी से कंक्रीट के जंगल फैल रहे हैं, उसने स्थानीय पारिस्थितिकी तंत्र के "
            "सामने गंभीर प्रश्न खड़े कर दिए हैं। दो दशक पहले तक प्रत्येक नगर के चारों ओर पारंपरिक तालाबों, बाग-बगीचों "
            "और बरसाती नालों की एक प्राकृतिक श्रृंखला हुआ करती थी, जो मानसून के अतिरिक्त जल को सोखकर भूजल स्तर "
            "को रिचार्ज करती थी।\n"
            "आज अनियोजित निर्माण के कारण थोड़ी सी वर्षा होते ही महानगरों में जलभराव की स्थिति बन जाती है और गर्मियों "
            "में पेयजल का संकट खड़ा हो जाता है। आधुनिक टाउन प्लानिंग में स्पंज सिटी और अर्बन फॉरेस्ट की अवधारणा को "
            "अनिवार्य रूप से लागू करना होगा ताकि विकास और प्रकृति एक-दूसरे के पूरक बन सकें।"
        ),
        illus_src="p4_mid_left_illus.jpg",
        illus_dst="ab_p5_mid_left_cmyk.jpg",
    )

    m2_pt = build_equal_middle_article(
        mid_r_x0, mid_r_x1, l2_y0, l2_y1,
        subhead_str="शिक्षा एवं भविष्य  •  बदलते कौशल के आयाम",
        headline_str="एआई के दौर में रचनात्मक\nसोच जगाए हमारी शिक्षा",
        intro_str="नई राष्ट्रीय शिक्षा नीति के तहत स्कूलों और कॉलेजों में शोध, तर्कशक्ति और मानवीय मूल्यों का संगम आवश्यक है।",
        byline_str="प्रो. मीनाक्षी सुंदरम | शिक्षाविद",
        body_str=(
            "कृत्रिम बुद्धिमत्ता और स्वचालित तकनीक ने ज्ञान प्राप्त करने और कामकाज करने के पारंपरिक तरीकों को पूरी "
            "तरह बदल दिया है। जब सूचनाओं का विशाल भंडार एक क्लिक पर उपलब्ध हो, तब परीक्षाओं में केवल तथ्यों को "
            "याद रखने की क्षमता पर्याप्त नहीं रह जाती। आज के विद्यार्थियों को प्रश्न पूछने, समस्याओं का मौलिक समाधान "
            "खोजने और तकनीक का नैतिक उपयोग करने का प्रशिक्षण देना सबसे बड़ी जरूरत है।\n"
            "मातृभाषा में तकनीकी और व्यावसायिक शिक्षा उपलब्ध कराने की पहल ने छोटे शहरों और ग्रामीण पृष्ठभूमि के "
            "प्रतिभाशाली छात्रों के लिए नए द्वार खोले हैं। यदि हमारे शिक्षण संस्थान पुस्तकीय ज्ञान के साथ प्रायोगिक "
            "कौशल और संवेदनशीलता को जोड़ें, तो भारत की युवा शक्ति विश्व का नेतृत्व करेगी।"
        ),
        illus_src="p4_mid_right_illus.jpg",
        illus_dst="ab_p5_mid_right_cmyk.jpg",
    )

    r_sep2_y = round(l2_y1 + mm(2.5), 2)
    r_sep2 = cmd("line.create", {"spread": 0, "a": [rx0, r_sep2_y], "b": [rx1, r_sep2_y]})
    cmd("object.stroke", {"ids": [r_sep2["id"]], "swatch": "ClosingGray", "weight": 1.5, "tint": 1.0})

    # ==========================================================================
    # PART B — LAYER 3: LITERARY CORNER (शेर, नज़्म, ग़ज़ल) + FRAMED CARTOON BOX
    # ==========================================================================
    l3_y0 = round(r_sep2_y + mm(2.5), 2)
    l3_top_y1 = bot_y1

    cartoon_w = cm(12.0)
    cartoon_x1 = rx1
    cartoon_x0 = round(cartoon_x1 - cartoon_w, 2)

    shayar_x0 = rx0
    shayar_x1 = round(cartoon_x0 - cm(0.80), 2)

    sh_hdr_h = cm(0.70)
    sh_hdr_y1 = round(l3_y0 + sh_hdr_h, 2)
    r_sh_hdr = cmd("frame.create", {
        "spread": 0,
        "rect": [shayar_x0, l3_y0, shayar_x1, sh_hdr_y1],
        "content": "text",
        "text": "अदब और चिंतन  •  शेर, नज़्म व ग़ज़ल",
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_sh_hdr["id"]], "swatch": "FlyerCrimson", "tint": 1.0}},
        {"command": "object.stroke", "params": {"ids": [r_sh_hdr["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_sh_hdr["id"]],
            "columns": 1,
            "inset": [0.0, 6.0, 0.0, 6.0],
            "verticalJustification": "center",
        }},
        {"command": "text.select", "params": {"story": r_sh_hdr["story"], "anchor": 0, "focus": 999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Bold",
            "size": 13.5,
            "leading": {"kind": "points", "value": 14.0},
            "fill": "[Paper]",
            "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "hyphenate": False, "gridAlign": "none"}}},
    ])

    literary_items = [
        (
            "१. आज का शेर\n",
            "“सफ़र में धूप तो होगी जो चल सको तो चलो,\nसभी हैं भीड़ में तुम भी निकल सको तो चलो।”\n",
            "अर्थ : जीवन पथ पर कठिनाइयां स्वाभाविक हैं; भीड़ का हिस्सा बनने के बजाय जो संघर्षों को स्वीकार कर आगे बढ़ता है, वही अपनी पहचान बनाता है।"
        ),
        (
            "२. नज़्म की पंक्तियाँ\n",
            "“अंधेरी रात के सीने में इक चराग़ जला,\nहवा के ज़ोर से लड़ने का हौसला तो मिला।”\n",
            "अर्थ : विपरीत परिस्थितियों से घबराने के बजाय उम्मीद का एक छोटा प्रयास भी बड़े से बड़े संकट के सामने टिके रहने का आत्मबल जगाता है।"
        ),
        (
            "३. ग़ज़ल का शेर\n",
            "“कौन कहता है आसमां में सुराख़ नहीं हो सकता,\nएक पत्थर तो तबीयत से उछालो यारो।”\n",
            "अर्थ : दुष्यंत कुमार की ये पंक्तियां संदेश देती हैं कि यदि पूरे संकल्प और निष्ठा से प्रयास किया जाए, तो असंभव दिखने वाला लक्ष्य भी साधा जा सकता है।"
        ),
    ]

    sh_avail_y0 = round(sh_hdr_y1 + 3.0, 2)
    sh_avail_h = l3_top_y1 - sh_avail_y0
    slot_h = sh_avail_h / len(literary_items)

    for idx, (tag_str, verse_str, arth_str) in enumerate(literary_items):
        iy0 = round(sh_avail_y0 + idx * slot_h + (1.5 if idx > 0 else 0.0), 2)
        iy1 = round(sh_avail_y0 + (idx + 1) * slot_h - (2.0 if idx < len(literary_items) - 1 else 0.0), 2)
        full_item = tag_str + verse_str + arth_str
        verse_b = len((tag_str + verse_str).encode("utf-8"))
        arth_lbl_b = verse_b + len("अर्थ : ".encode("utf-8"))

        r_it = cmd("frame.create", {
            "spread": 0,
            "rect": [shayar_x0, iy0, shayar_x1, iy1],
            "content": "text",
            "text": full_item,
        })
        batch([
            {"command": "object.textFrameOptions", "params": {
                "ids": [r_it["id"]],
                "columns": 1,
                "verticalJustification": "center",
            }},
            {"command": "text.select", "params": {"story": r_it["story"], "anchor": 0, "focus": 9999}},
            {"command": "type.char", "params": {"attrs": {
                "fontFamily": "DB Hindi",
                "fontStyle": "Regular",
                "size": 10.5,
                "leading": {"kind": "points", "value": 11.4},
                "fill": "[Black]",
                "fillTint": 1.0,
            }}},
            {"command": "type.para", "params": {"attrs": {
                "align": "leftJustified",
                "firstLineIndent": 0.0,
                "spaceAfter": 1.5,
                "gridAlign": "none",
                "hyphenate": False,
            }}},
            {"command": "text.select", "params": {"story": r_it["story"], "anchor": 0, "focus": verse_b - 1}},
            {"command": "type.char", "params": {"attrs": {
                "fontFamily": "DB Hindi",
                "fontStyle": "Bold",
                "size": 10.6,
                "leading": {"kind": "points", "value": 11.6},
                "fill": "[Black]",
                "fillTint": 1.0,
            }}},
            {"command": "text.select", "params": {"story": r_it["story"], "anchor": verse_b, "focus": arth_lbl_b}},
            {"command": "type.char", "params": {"attrs": {"fontStyle": "Bold", "fill": "[Black]", "fillTint": 1.0}}},
        ])
        if idx < len(literary_items) - 1:
            ry = round(sh_avail_y0 + (idx + 1) * slot_h, 2)
            r_ln = cmd("line.create", {"spread": 0, "a": [shayar_x0, ry], "b": [shayar_x1, ry]})
            cmd("object.stroke", {"ids": [r_ln["id"]], "swatch": "ClosingGray", "weight": 0.85, "tint": 0.8})

    # --- 3B: Bottom-Right 3-Column Standalone Framed B&W Satirical Cartoon Box ---
    r_cbox_outer = cmd("frame.create", {
        "spread": 0,
        "rect": [cartoon_x0, l3_y0, cartoon_x1, l3_top_y1],
        "content": "text",
        "text": "",
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_cbox_outer["id"]], "swatch": "[Paper]", "tint": 1.0}},
        {"command": "object.stroke", "params": {"ids": [r_cbox_outer["id"]], "swatch": "[Black]", "weight": 1.6, "tint": 1.0}},
    ])

    c_hdr_h = cm(0.70)
    c_hdr_y1 = round(l3_y0 + c_hdr_h, 2)
    r_cbox_hdr = cmd("frame.create", {
        "spread": 0,
        "rect": [cartoon_x0, l3_y0, cartoon_x1, c_hdr_y1],
        "content": "text",
        "text": "कटाक्ष  •  तीखे तेवर  (व्यंग्य कोना)",
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_cbox_hdr["id"]], "swatch": "[Black]", "tint": 1.0}},
        {"command": "object.stroke", "params": {"ids": [r_cbox_hdr["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_cbox_hdr["id"]],
            "columns": 1,
            "inset": [0.0, 8.0, 0.0, 8.0],
            "verticalJustification": "center",
        }},
        {"command": "text.select", "params": {"story": r_cbox_hdr["story"], "anchor": 0, "focus": 999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Bold",
            "size": 14.0,
            "leading": {"kind": "points", "value": 14.5},
            "fill": "[Paper]",
            "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "hyphenate": False, "gridAlign": "none"}}},
    ])

    c_cap_h = cm(1.15)
    c_cap_y0 = round(l3_top_y1 - c_cap_h - 2.5, 2)
    c_cap_y1 = round(l3_top_y1 - 2.5, 2)
    c_img_x0 = round(cartoon_x0 + 4.0, 2)
    c_img_x1 = round(cartoon_x1 - 4.0, 2)
    c_img_y0 = round(c_hdr_y1 + 3.0, 2)
    c_img_y1 = round(c_cap_y0 - 2.5, 2)

    cartoon_cropped = prepare_cmyk_edit_photo(
        "p4_cartoon_bw.jpg",
        "ab_p5_cartoon_cmyk.jpg",
        c_img_x1 - c_img_x0,
        c_img_y1 - c_img_y0,
        crop_mode="contain",
        trim_white=True,
    )
    r_c_img = cmd("frame.create", {
        "spread": 0,
        "rect": [c_img_x0, c_img_y0, c_img_x1, c_img_y1],
        "content": "graphic",
    })
    batch([
        {"command": "file.place", "params": {"frame": r_c_img["id"], "path": str(cartoon_cropped)}},
        {"command": "object.fit", "params": {"ids": [r_c_img["id"]], "mode": "fillProportionally"}},
        {"command": "object.stroke", "params": {"ids": [r_c_img["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
    ])

    cartoon_punchline = (
        "“भाई साहब, ऑनलाइन सेल के धमाकों से तो किसी तरह बच गए, "
        "मगर महंगाई के इस रॉकेट से आम आदमी के बजट की छतरी कैसे बचेगी!”"
    )
    r_c_cap = cmd("frame.create", {
        "spread": 0,
        "rect": [c_img_x0, c_cap_y0, c_img_x1, c_cap_y1],
        "content": "text",
        "text": cartoon_punchline,
    })
    batch([
        {"command": "object.fill", "params": {"ids": [r_c_cap["id"]], "swatch": "SoftGrayBg", "tint": 1.0}},
        {"command": "object.stroke", "params": {"ids": [r_c_cap["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_c_cap["id"]],
            "columns": 1,
            "inset": [2.0, 6.0, 2.0, 6.0],
            "verticalJustification": "center",
        }},
        {"command": "text.select", "params": {"story": r_c_cap["story"], "anchor": 0, "focus": 999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi 7",
            "fontStyle": "Bold",
            "size": 10.0,
            "leading": {"kind": "points", "value": 10.2},
            "fill": "[Black]",
            "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "hyphenate": False, "gridAlign": "none"}}},
    ])

    cmd("edit.deselectAll")
    cmd("view.fitPage", {})

    out_pd = VAULT_DIR / "Aditya_Bharat_Page_04_Sampadakiya_34x53.pagedesigner"
    out_png = VAULT_DIR / "Aditya_Bharat_Page_04_Sampadakiya_34x53.png"
    out_pdf = VAULT_DIR / "Aditya_Bharat_Page_04_Sampadakiya_CMYK_34x53.pdf"
    rpc("app.save", {"path": str(out_pd)})
    rpc("app.export", {"path": str(out_png), "page": 0, "scale": 1.5})
    try:
        rpc("app.export", {"path": str(out_pdf), "page": 0})
    except Exception:
        pass

    artifact_png = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\8707c72d-58b0-4715-a099-3efffcd57514\aditya_bharat_page_04_sampadakiya_34x53.png")
    artifact_png.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_png, artifact_png)

    print(
        f"=== ADITYA BHARAT PAGE 04 (SAMPADAKIYA) BUILT IN {time.perf_counter()-t0:.2f}s ===\n"
        f"    Edit1={ed1_h_pt}pt | JeevanMantra={jm_h_pt}pt | Edit3={ed3_h_pt}pt\n"
        f"    LeadOpinion={lead_h_pt}pt | MidLeft={m1_pt}pt | MidRight={m2_pt}pt (ALL >= 30.0pt!)"
    )


if __name__ == "__main__":
    build_aditya_bharat_page5_edit()
