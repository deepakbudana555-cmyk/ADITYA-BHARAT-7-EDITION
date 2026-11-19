# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — 5-IN-1 ADVANCED AUTOMATION EXTENSIONS ENGINE
==========================================================================
1. Live Browser Story / Headline / Subhead / Body / Photo / Caption Override Engine
2. Live IANS Hindi Agency & 4-City Local News Pool Connector + 1-Click Swap / Auto-Fill
3. Dynamic Commercial Display Ad Reflow Engine (Quarter-Page, Half-Page, Strip, Skybus)
4. Cutout / Transparent PNG Silhouette Contour Text-Wrap Engine (WrapMode::Contour)
5. No-Code Visual Drag-and-Drop Custom Layout Dummy Builder -> Live Page Designer Draw
"""

import ast
import base64
import importlib.util
import json
import os
import shutil
import sys
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.stdout.reconfigure(encoding="utf-8")

VAULT_DIR = Path(__file__).resolve().parent
ROOT_DIR = VAULT_DIR.parent
PHOTOS_DIR = VAULT_DIR / "photos"
CUTOUTS_DIR = PHOTOS_DIR / "cutouts"
CUSTOM_ADS_DIR = PHOTOS_DIR / "ads"
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
CUTOUTS_DIR.mkdir(parents=True, exist_ok=True)
CUSTOM_ADS_DIR.mkdir(parents=True, exist_ok=True)

OVERRIDES_JSON = VAULT_DIR / "aditya_bharat_live_overrides.json"
CUSTOM_LAYOUTS_JSON = VAULT_DIR / "aditya_bharat_custom_layouts.json"

CM_TO_PT = 72.0 / 2.54
MM_TO_PT = CM_TO_PT / 10.0


def cm(val: float) -> float:
    return round(val * CM_TO_PT, 2)


def mm(val: float) -> float:
    return round(val * MM_TO_PT, 2)


# ==============================================================================
# COMMERCIAL AD PRESETS (In cm within the 32x51 cm Print Area: x=Cols 1..8, y=1..52 cm)
# ==============================================================================
AD_PRESETS = {
    "none": {
        "id": "none",
        "name_hi": "कोई विज्ञापन नहीं (100% संपादकीय खबरें)",
        "col": 1,
        "span": 0,
        "y0_cm": 52.0,
        "h_cm": 0.0,
    },
    "quarter_br": {
        "id": "quarter_br",
        "name_hi": "क्वार्टर पेज विज्ञापन (Quarter Page: दाएं नीचे 4 Col × 15 cm)",
        "col": 5,
        "span": 4,
        "y0_cm": 37.0,
        "h_cm": 15.0,
    },
    "bottom_strip": {
        "id": "bottom_strip",
        "name_hi": "बॉटम स्ट्रिप विज्ञापन (Full Bottom Strip: 8 Col × 10.5 cm)",
        "col": 1,
        "span": 8,
        "y0_cm": 41.5,
        "h_cm": 10.5,
    },
    "half_page": {
        "id": "half_page",
        "name_hi": "हाफ पेज विज्ञापन (Half Page Lower: 8 Col × 22.0 cm)",
        "col": 1,
        "span": 8,
        "y0_cm": 30.0,
        "h_cm": 22.0,
    },
    "skybus_right": {
        "id": "skybus_right",
        "name_hi": "वर्टिकल स्काईबस विज्ञापन (Right Skybus: दाएं 2 Col × 22.0 cm)",
        "col": 7,
        "span": 2,
        "y0_cm": 30.0,
        "h_cm": 22.0,
    },
}

PAGE_SCRIPT_MAP = {
    "page_01": "build_aditya_bharat_page1.py",
    "page_01_opt2": "build_aditya_bharat_page1_option2.py",
    "page_02": "build_aditya_bharat_page2.py",
    "page_03": "build_aditya_bharat_page3.py",
    "page_04": "build_aditya_bharat_page5_edit.py",
    "page_05": "build_aditya_bharat_page4.py",
    "page_06": "build_aditya_bharat_page6_business.py",
    "page_07": "build_aditya_bharat_page7_sports.py",
    "page_08": "build_aditya_bharat_page8_desh_videsh.py",
}


def load_overrides() -> dict:
    if OVERRIDES_JSON.exists():
        try:
            return json.loads(OVERRIDES_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"pages": {}, "ads": {}, "photos": {}}


def save_overrides(data: dict):
    OVERRIDES_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ==============================================================================
# PART 1: AST & RUNTIME SLOT EXTRACTOR FOR ALL 8 PAGES
# ==============================================================================
def extract_default_slots_from_script(page_id: str) -> dict:
    """Parses the builder script AST (or Chhattisgarh 10+10 manifest for page_02/page_03) to extract every story and photo slot."""
    if page_id in ("page_02", "page_03"):
        import ab_chhattisgarh_10x2_engine as cg_eng
        cg_data = cg_eng.harvest_chhattisgarh_news_for_date("18-11-2026")
        target_p = 2 if page_id == "page_02" else 3
        p_stories = [s for s in cg_data["stories"] if s["page"] == target_p]
        stories = []
        photos = []
        for idx, s in enumerate(p_stories):
            stories.append({
                "slot_index": idx,
                "headline": s["headline"],
                "subhead": s.get("subhead") or s.get("kicker") or "",
                "city": s["city"],
                "agency": s["agency"],
                "blurb": s["blurb"],
                "body": s["body"],
            })
            if s.get("photo"):
                photos.append({
                    "photo_index": len(photos),
                    "src_photo": s["photo"],
                    "dst_photo": s["photo"],
                    "caption": s.get("caption") or "",
                    "wrap_mode": "boundingBox",
                })
        ov = load_overrides()
        ad_cfg = ov.get("ads", {}).get(page_id, {"preset": "none"})
        return {"page_id": page_id, "stories": stories, "photos": photos, "ad_config": ad_cfg}

    script_name = PAGE_SCRIPT_MAP.get(page_id, "build_aditya_bharat_page1.py")
    script_path = VAULT_DIR / script_name
    if not script_path.exists():
        return {"stories": [], "photos": []}

    src = script_path.read_text(encoding="utf-8")
    tree = ast.parse(src)

    # Map variable assignments (strings) in the main build function
    var_map = {}
    stories = []
    photos = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            vname = node.targets[0].id
            try:
                val = ast.literal_eval(node.value)
                if isinstance(val, str):
                    var_map[vname] = val
            except Exception:
                pass

    def _resolve(node_val):
        if node_val is None:
            return ""
        try:
            v = ast.literal_eval(node_val)
            return str(v) if isinstance(v, (str, int, float)) else ""
        except Exception:
            if isinstance(node_val, ast.Name):
                return var_map.get(node_val.id, "")
            return ""

    # Walk statements in source line order to pair headlines, bodies, and photos
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            calls.append((getattr(node, "lineno", 0), node.func.id, node))
    calls.sort(key=lambda x: x[0])

    pending_head = None
    pending_sub = None
    pending_blurb = ""

    for lineno, fname, call in calls:
        kw = {k.arg: k.value for k in call.keywords if k.arg}
        if fname in ("fit_aditya_bharat_headline", "place_edit_page_headline_with_whitespace"):
            raw_txt = _resolve(kw.get("raw_text") or (call.args[4] if len(call.args) > 4 else None))
            ff = _resolve(kw.get("font_family"))
            if "Rasrand" in ff or not pending_head:
                if pending_head and not raw_txt.startswith(pending_head[:10]):
                    pending_head = raw_txt
                elif not pending_head:
                    pending_head = raw_txt
            else:
                pending_sub = raw_txt

        elif fname == "place_red_subject_blurb":
            if len(call.args) >= 4:
                pending_blurb = _resolve(call.args[3])
            elif "word" in kw:
                pending_blurb = _resolve(kw["word"])

        elif fname in ("fit_aditya_bharat_body", "fit_hindi_body_11pt_1125_leading"):
            if fname == "fit_hindi_body_11pt_1125_leading":
                city = "संपादकीय डेस्क"
                agency = "आदित्य भारत"
                body = _resolve(call.args[1] if len(call.args) > 1 else kw.get("raw_text"))
            else:
                city = _resolve(call.args[1] if len(call.args) > 1 else kw.get("city"))
                agency = _resolve(call.args[2] if len(call.args) > 2 else kw.get("agency"))
                body = _resolve(call.args[3] if len(call.args) > 3 else kw.get("raw_body"))
            idx = len(stories)
            stories.append({
                "slot_index": idx,
                "headline": pending_head or f"समाचार शीर्षक #{idx + 1}",
                "subhead": pending_sub or "",
                "city": city or "नई दिल्ली",
                "agency": agency or "एजेंसी",
                "blurb": pending_blurb or "",
                "body": body,
            })
            pending_head = None
            pending_sub = None
            pending_blurb = ""

        elif fname in ("place_multi_col_story", "place_compact_story", "place_story_block"):
            head = _resolve(kw.get("headline") or (call.args[6] if len(call.args) > 6 else None))
            city = _resolve(kw.get("city") or (call.args[7] if len(call.args) > 7 else None))
            agency = _resolve(kw.get("agency") or (call.args[8] if len(call.args) > 8 else None))
            blurb = _resolve(kw.get("blurb_word") or (call.args[9] if len(call.args) > 9 else None))
            body = _resolve(kw.get("body") or (call.args[10] if len(call.args) > 10 else None))
            if head or body:
                idx = len(stories)
                stories.append({
                    "slot_index": idx,
                    "headline": head or f"समाचार शीर्षक #{idx + 1}",
                    "subhead": _resolve(kw.get("subhead")),
                    "city": city or "इंदौर",
                    "agency": agency or "ब्यूरो",
                    "blurb": blurb or "",
                    "body": body,
                })

        elif fname == "place_photo_and_caption_cmyk":
            if len(call.args) >= 8:
                src_p = _resolve(call.args[5])
                dst_p = _resolve(call.args[6])
                cap_t = _resolve(call.args[7])
            else:
                src_p = _resolve(call.args[5] if len(call.args) > 5 else kw.get("photo_filename"))
                dst_p = src_p
                cap_t = _resolve(call.args[6] if len(call.args) > 6 else kw.get("caption_text"))
            p_idx = len(photos)
            photos.append({
                "photo_index": p_idx,
                "src_photo": src_p,
                "dst_photo": dst_p,
                "caption": cap_t,
                "wrap_mode": "boundingBox",
            })
        elif fname == "prepare_cmyk_edit_photo":
            src_p = _resolve(call.args[0] if len(call.args) > 0 else kw.get("src_name"))
            dst_p = _resolve(call.args[1] if len(call.args) > 1 else kw.get("dst_name"))
            p_idx = len(photos)
            photos.append({
                "photo_index": p_idx,
                "src_photo": src_p,
                "dst_photo": dst_p,
                "caption": f"संपादकीय चित्र #{p_idx + 1}",
                "wrap_mode": "boundingBox",
            })

    # Merge any saved user overrides on top
    ov = load_overrides()
    page_ov = ov.get("pages", {}).get(page_id, {})
    story_ov = page_ov.get("stories", {})
    photo_ov = page_ov.get("photos", {})

    for s in stories:
        k = str(s["slot_index"])
        if k in story_ov:
            s.update(story_ov[k])

    for p in photos:
        k = str(p["photo_index"])
        if k in photo_ov:
            p.update(photo_ov[k])

    ad_cfg = ov.get("ads", {}).get(page_id, {
        "preset": "none",
        "advertiser": "आदित्य भारत विशेष उत्सव ऑफर",
        "headline": "त्योहारी सीजन में स्वदेशी उत्पादों पर विशेष छूट और आकर्षक उपहार योजना",
        "subtext": "अधिकृत शोरूम एवं सभी प्रमुख विक्रेताओं के यहाँ उपलब्ध • संपर्क : 1800-123-4567",
        "image_file": "",
    })

    return {
        "page_id": page_id,
        "stories": stories,
        "photos": photos,
        "ad_config": ad_cfg,
    }


# ==============================================================================
# PART 2: LIVE IANS HINDI AGENCY & 4-CITY LOCAL VAULT CONNECTOR
# ==============================================================================
def scan_ians_agency_pool(limit: int = 80) -> list:
    """Scans Chhattisgarh 18-11-2026 live harvested stories + local_hindi_daily_vault across all dates."""
    items = []
    try:
        import ab_chhattisgarh_10x2_engine as cg_eng
        cg_data = cg_eng.harvest_chhattisgarh_news_for_date("18-11-2026")
        for s in cg_data.get("stories", []):
            items.append({
                "wire_id": f"CG_18NOV_P{s['page']}_S{s['slot']}",
                "date": "18-11-2026",
                "category": "CHHATTISGARH",
                "recommended_page": s["page"],
                "headline": s["headline"],
                "subhead": s.get("subhead") or s.get("kicker") or "",
                "city": s["city"],
                "agency": s["agency"],
                "body": s["body"],
                "caption": s.get("caption") or "",
                "jpg_path": str(PHOTOS_DIR / s["photo"]) if s.get("photo") else "",
                "has_photo": bool(s.get("photo")),
            })
    except Exception:
        pass
    vault_root = ROOT_DIR / "local_hindi_daily_vault"
    if not vault_root.exists():
        return items

    date_dirs = sorted([d for d in vault_root.iterdir() if d.is_dir()], key=lambda x: x.name, reverse=True)
    for ddir in date_dirs:
        raw_pool = ddir / "01_AGENCY_RAW_POOL"
        if not raw_pool.exists():
            continue
        for jf in sorted(raw_pool.rglob("*.json")):
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
                head = (data.get("headline") or "").strip()
                body = (data.get("body") or "").replace("\r", "\n").strip()
                if not head or len(body) < 60:
                    continue
                byline_raw = data.get("byline") or "नई दिल्ली | आईएएनएस"
                if "|" in byline_raw:
                    parts = [p.strip() for p in byline_raw.split("|", 1)]
                    agency, city = parts[0], parts[1]
                else:
                    city, agency = "नई दिल्ली", "आईएएनएस"

                pfiles = data.get("photoFiles") or {}
                jpg_path = pfiles.get("local300DpiJpgPath") or data.get("srcJpg") or ""
                has_photo = bool(jpg_path and Path(jpg_path).exists())

                items.append({
                    "wire_id": data.get("wireId") or jf.stem,
                    "date": ddir.name,
                    "category": data.get("category") or jf.parent.parent.name,
                    "recommended_page": data.get("recommendedPage") or 1,
                    "headline": head,
                    "subhead": (data.get("subhead") or "")[:140],
                    "city": city,
                    "agency": agency,
                    "body": body,
                    "caption": data.get("caption") or f"{head}। — फोटो : आईएएनएस",
                    "jpg_path": jpg_path if has_photo else "",
                    "has_photo": has_photo,
                })
                if len(items) >= limit:
                    return items
            except Exception:
                continue
    return items


# ==============================================================================
# PART 4: CUTOUT / TRANSPARENT PNG SILHOUETTE GENERATOR FOR CONTOUR TEXT-WRAP
# ==============================================================================
_REMBG_SESSION = None


def _get_rembg_session():
    global _REMBG_SESSION
    if _REMBG_SESSION is None:
        from rembg import new_session
        _REMBG_SESSION = new_session("u2net")
    return _REMBG_SESSION


def create_silhouette_cutout_png(
    src_img_path: Path,
    dst_png_path: Path,
    frame_w_pt: float,
    frame_h_pt: float,
) -> Path:
    """
    Creates a 100% real AI background-removed RGBA transparent PNG cutout (`rembg` U2-Net)
    so Page Designer's native `WrapMode::Contour` (`extractAlphaContour` at alpha > 24)
    traces the actual human silhouette (head, hair, neck, shoulders, arms/medal) and wraps
    Hindi text lines smoothly around the person with zero background!
    """
    dst_png_path.parent.mkdir(parents=True, exist_ok=True)
    target_w_px = max(280, int(round(frame_w_pt * 4.0)))
    target_h_px = max(340, int(round(frame_h_pt * 4.0)))

    with Image.open(src_img_path) as im:
        has_real_alpha = False
        if im.mode == "RGBA":
            extrema = im.getchannel("A").getextrema()
            if extrema and extrema[0] < 50 and extrema[1] > 200:
                has_real_alpha = True

        if has_real_alpha:
            clean_im = im.copy()
        else:
            import numpy as np
            import cv2
            from scipy import ndimage
            from rembg import remove

            rgb_im = im.convert("RGB")
            out_rgba = remove(rgb_im, session=_get_rembg_session())
            arr = np.array(out_rgba)
            alpha = arr[:, :, 3]
            h, w = alpha.shape

            # Special shoulder preservation for high-contrast B&W studio portraits with dark suit coats
            src_name_l = src_img_path.name.lower()
            if "film_actor" in src_name_l or "amitabh" in src_name_l:
                yy, xx = np.mgrid[0:h, 0:w]
                left_slope_y = h * (0.715 + 0.175 * np.power(np.maximum(0.0, (0.31 * w - xx) / (0.31 * w)), 1.15))
                right_slope_y = h * (0.555 + 0.225 * np.power(np.maximum(0.0, (xx - 0.70 * w) / (0.30 * w)), 1.15))
                suit_zone = ((xx <= w * 0.50) & (yy > left_slope_y)) | ((xx > w * 0.50) & (yy > right_slope_y))
                alpha = np.where(suit_zone, 255, alpha).astype(np.uint8)

            # Keep only the largest foreground connected component so background bystanders disappear
            mask = alpha > 110
            labeled, num_features = ndimage.label(mask)
            if num_features > 1:
                sizes = ndimage.sum(mask, labeled, range(1, num_features + 1))
                largest_label = int(np.argmax(sizes)) + 1
                keep = ndimage.binary_dilation(labeled == largest_label, iterations=2)
                alpha = np.where(keep, alpha, 0).astype(np.uint8)

            alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
            alpha = np.where(alpha < 85, 0, alpha).astype(np.uint8)
            arr[:, :, 3] = alpha
            clean_im = Image.fromarray(arr, "RGBA")

        bbox = clean_im.getchannel("A").getbbox()
        if bbox:
            clean_im = clean_im.crop(bbox)

        # Compose onto a bottom-grounded transparent canvas matching (target_w_px, target_h_px)
        # so the person's head/shoulders are never clipped and rest grounded on the bottom edge!
        cw, ch = clean_im.size
        avail_w = int(round(target_w_px * 0.94))
        avail_h = int(round(target_h_px * 0.96))
        scale = min(avail_w / max(1, cw), avail_h / max(1, ch))
        new_w = max(1, int(round(cw * scale)))
        new_h = max(1, int(round(ch * scale)))
        subject_resized = clean_im.resize((new_w, new_h), Image.Resampling.LANCZOS)

        canvas = Image.new("RGBA", (target_w_px, target_h_px), (0, 0, 0, 0))
        paste_x = (target_w_px - new_w) // 2
        paste_y = target_h_px - new_h
        canvas.paste(subject_resized, (paste_x, paste_y), subject_resized)
        canvas.save(dst_png_path, "PNG")
    return dst_png_path


# ==============================================================================
# PART 1 + 3 + 4 SMART RUNTIME RUNNER (Injects Overrides, Cutout Contour Wrap & Ad Reflow)
# ==============================================================================
def run_smart_page_builder(page_id: str) -> dict:
    """
    Loads the target page's Python builder module in-memory, hooks its headline/body/photo/frame
    functions to apply:
      1. User / IANS Story & Photo Overrides
      2. Cutout Silhouette Contour Text-Wrap (WrapMode::Contour)
      3. Dynamic Commercial Display Ad Grid Reflow (shrinks/suppresses overlapping editorial frames
         and draws the Commercial Ad Box cleanly in Page Designer)
    """
    t0 = time.perf_counter()
    if page_id == "page_02":
        import ab_chhattisgarh_10x2_engine as cg_eng
        r = cg_eng.build_chhattisgarh_page2_10stories()
        return {"ok": True, "page_id": page_id, "elapsed_sec": round(time.perf_counter() - t0, 2), "ad_preset": "none", "details": r}
    if page_id == "page_03":
        import ab_chhattisgarh_10x2_engine as cg_eng
        r = cg_eng.build_chhattisgarh_page3_10stories()
        return {"ok": True, "page_id": page_id, "elapsed_sec": round(time.perf_counter() - t0, 2), "ad_preset": "none", "details": r}
    script_name = PAGE_SCRIPT_MAP.get(page_id, "build_aditya_bharat_page1.py")
    script_path = VAULT_DIR / script_name

    ov = load_overrides()
    page_ov = ov.get("pages", {}).get(page_id, {})
    story_ov = page_ov.get("stories", {})
    photo_ov = page_ov.get("photos", {})
    ad_cfg = ov.get("ads", {}).get(page_id, {"preset": "none"})
    ad_preset_id = ad_cfg.get("preset", "none")
    ad_preset = AD_PRESETS.get(ad_preset_id, AD_PRESETS["none"])

    # Compute Ad Bounding Box in points if an ad is active
    ad_rect_pt = None
    if ad_preset_id != "none" and ad_preset["span"] > 0:
        col_w_pt = round((cm(32.0) - 7 * mm(4.0)) / 8.0, 2)
        gut_pt = mm(4.0)
        ax0 = round(cm(1.0) + (ad_preset["col"] - 1) * (col_w_pt + gut_pt), 2)
        ax1 = round(ax0 + ad_preset["span"] * col_w_pt + (ad_preset["span"] - 1) * gut_pt, 2)
        ay0 = cm(ad_preset["y0_cm"])
        ay1 = cm(ad_preset["y0_cm"] + ad_preset["h_cm"])
        ad_rect_pt = (ax0, ay0, ax1, ay1)

    spec = importlib.util.spec_from_file_location(f"ab_dyn_{page_id}", str(script_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    orig_cmd = mod.cmd
    orig_batch = mod.batch
    orig_fit_head = getattr(mod, "fit_aditya_bharat_headline", None) or getattr(mod, "place_edit_page_headline_with_whitespace", None)
    orig_fit_body = getattr(mod, "fit_aditya_bharat_body", None)
    orig_fit_edit_body = getattr(mod, "fit_hindi_body_11pt_1125_leading", None)
    orig_place_photo = getattr(mod, "place_photo_and_caption_cmyk", None)
    orig_place_blurb = getattr(mod, "place_red_subject_blurb", None)
    orig_rpc = mod.rpc

    state = {
        "body_idx": 0,
        "photo_idx": 0,
        "head_call_queue": [],
        "suppressed_frame_ids": set(),
        "suppressed_stories": set(),
        "ad_drawn": False,
    }

    def _rects_overlap(r1, r2):
        # r = [x0, y0, x1, y1]
        return not (r1[2] <= r2[0] + 4.0 or r1[0] >= r2[2] - 4.0 or r1[3] <= r2[1] + 4.0 or r1[1] >= r2[3] - 4.0)

    def _reflow_rect_for_ad(rect):
        """
        Dynamic Ad-Grid Reflow:
        If a frame overlaps `ad_rect_pt`:
        - If the frame starts above the ad (`y0 < ay0 - 85 pt`), shrink its bottom `y1` to sit cleanly above the ad (`ay0 - 8 pt`)!
        - If the frame starts to the left of the ad (`x0 < ax0 - 50 pt`) and spans into the ad, narrow its right edge `x1` to `ax0 - 11.34 pt`!
        - Otherwise, if the frame lies inside the ad zone, move it off-canvas / suppress it so the Commercial Ad has 100% clean space!
        """
        if not ad_rect_pt or not isinstance(rect, list) or len(rect) != 4:
            return rect, False, None
        x0, y0, x1, y1 = rect
        ax0, ay0, ax1, ay1 = ad_rect_pt
        if not _rects_overlap(rect, ad_rect_pt):
            return rect, False, None

        # Never touch the top masthead (y1 <= cm(7.2))
        if y1 <= cm(7.2):
            return rect, False, None

        # Case 1: Frame starts well above the ad -> vertically reflow (shorten bottom edge)
        if y0 < ay0 - cm(3.2):
            new_y1 = round(ay0 - mm(3.5), 2)
            col_w_pt = round((cm(32.0) - 7 * mm(4.0)) / 8.0, 2)
            new_cols = max(1, int(round((x1 - x0) / (col_w_pt + mm(4.0)))))
            return [x0, y0, x1, new_y1], False, new_cols

        # Case 2: Frame starts to the left of a right-side ad (e.g. Quarter Page or Skybus) -> horizontally reflow (narrow right edge)
        if x0 < ax0 - cm(2.5) and ax0 > cm(1.5):
            new_x1 = round(ax0 - mm(4.0), 2)
            col_w_pt = round((cm(32.0) - 7 * mm(4.0)) / 8.0, 2)
            new_cols = max(1, int(round((new_x1 - x0 + mm(4.0)) / (col_w_pt + mm(4.0)))))
            return [x0, y0, new_x1, y1], False, new_cols

        # Case 3: Frame is completely inside the ad zone -> suppress it
        return [-500.0, -500.0, -400.0, -400.0], True, 1

    last_reflow_cols = {"val": None}

    def hooked_cmd(command: str, params: dict = None):
        p = dict(params or {})
        if ad_rect_pt:
            if command == "frame.create" and "rect" in p:
                new_rect, suppressed, new_cols = _reflow_rect_for_ad(p["rect"])
                p["rect"] = new_rect
                last_reflow_cols["val"] = new_cols
                res = orig_cmd(command, p)
                if suppressed and isinstance(res, dict):
                    state["suppressed_frame_ids"].add(res.get("id"))
                    if res.get("story") is not None:
                        state["suppressed_stories"].add(res.get("story"))
                    try:
                        orig_cmd("item.delete", {"ids": [res["id"]]})
                    except Exception:
                        pass
                return res
            elif command == "object.textFrameOptions" and last_reflow_cols["val"] is not None:
                if "columns" in p and p["columns"] > last_reflow_cols["val"]:
                    p["columns"] = last_reflow_cols["val"]
                last_reflow_cols["val"] = None
            elif command == "line.create" and "a" in p and "b" in p:
                a, b = p["a"], p["b"]
                lrect = [min(a[0], b[0]), min(a[1], b[1]) - 2, max(a[0], b[0]), max(a[1], b[1]) + 2]
                if _rects_overlap(lrect, ad_rect_pt) and max(a[1], b[1]) > cm(7.2):
                    ax0, ay0, ax1, ay1 = ad_rect_pt
                    if a[0] < ax0 - cm(2.5) and ax0 > cm(1.5):
                        p["b"] = [round(ax0 - mm(4.0), 2), b[1]]
                    else:
                        return {"id": -1}
        return orig_cmd(command, p)

    mod.cmd = hooked_cmd

    if orig_place_blurb:
        def hooked_blurb(spread_idx: int, x0: float, y0: float, word: str, *a, **kw):
            if ad_rect_pt and _rects_overlap([x0, y0, x0 + 80, y0 + 30], ad_rect_pt):
                return -1
            b_idx = str(state["body_idx"])
            if b_idx in story_ov and story_ov[b_idx].get("blurb"):
                word = story_ov[b_idx]["blurb"]
            return orig_place_blurb(spread_idx, x0, y0, word, *a, **kw)
        mod.place_red_subject_blurb = hooked_blurb

    if orig_fit_head:
        def hooked_fit_head(spread_idx: int, x0: float, y0: float, x1: float, raw_text: str, *a, **kw):
            if ad_rect_pt:
                new_r, suppressed, _ = _reflow_rect_for_ad([x0, y0, x1, y0 + 45.0])
                if suppressed:
                    return -1, -1, 30.0, 0.0
                x0, y0, x1 = new_r[0], new_r[1], new_r[2]
            ff = kw.get("font_family", "DB Rasrand Bold")
            b_idx = str(state["body_idx"])
            if b_idx in story_ov:
                if "Rasrand" in ff and story_ov[b_idx].get("headline"):
                    raw_text = story_ov[b_idx]["headline"]
                elif "Rasrand" not in ff and story_ov[b_idx].get("subhead"):
                    raw_text = story_ov[b_idx]["subhead"]
            return orig_fit_head(spread_idx, x0, y0, x1, raw_text, *a, **kw)
        if hasattr(mod, "fit_aditya_bharat_headline"):
            mod.fit_aditya_bharat_headline = hooked_fit_head
        if hasattr(mod, "place_edit_page_headline_with_whitespace"):
            mod.place_edit_page_headline_with_whitespace = hooked_fit_head

    if orig_fit_body:
        def hooked_fit_body(sid: int, city: str, agency: str, raw_body: str, *a, **kw):
            idx = state["body_idx"]
            state["body_idx"] += 1
            if sid in state["suppressed_stories"]:
                return 0
            k = str(idx)
            if k in story_ov:
                city = story_ov[k].get("city") or city
                agency = story_ov[k].get("agency") or agency
                raw_body = story_ov[k].get("body") or raw_body
            return orig_fit_body(sid, city, agency, raw_body, *a, **kw)
        mod.fit_aditya_bharat_body = hooked_fit_body

    if orig_fit_edit_body:
        def hooked_fit_edit_body(sid: int, raw_text: str, *a, **kw):
            idx = state["body_idx"]
            state["body_idx"] += 1
            if sid in state["suppressed_stories"]:
                return 0
            k = str(idx)
            if k in story_ov and story_ov[k].get("body"):
                raw_text = story_ov[k]["body"]
            return orig_fit_edit_body(sid, raw_text, *a, **kw)
        mod.fit_hindi_body_11pt_1125_leading = hooked_fit_edit_body

    if orig_place_photo:
        def hooked_place_photo(spread_idx: int, px0: float, py0: float, px1: float, cap_y1: float, *rest, **kw):
            p_idx = state["photo_idx"]
            state["photo_idx"] += 1
            if ad_rect_pt:
                new_r, suppressed, _ = _reflow_rect_for_ad([px0, py0, px1, cap_y1])
                if suppressed or (new_r[3] - new_r[1]) < 45.0:
                    return -1, -1
                px0, py0, px1, cap_y1 = new_r[0], new_r[1], new_r[2], new_r[3]

            # Support both 7-arg (photo_filename, caption_text) and 8-arg (src_name, dst_name, caption_text)
            if len(rest) >= 3:
                src_photo_name, dst_photo_name, caption_text = rest[0], rest[1], rest[2]
                is_8arg = True
            else:
                src_photo_name = rest[0] if len(rest) > 0 else kw.get("photo_filename", "")
                dst_photo_name = src_photo_name
                caption_text = rest[1] if len(rest) > 1 else kw.get("caption_text", "")
                is_8arg = False
            cap_h = kw.get("cap_h", rest[3] if len(rest) > 3 else 22.0)

            pk = str(p_idx)
            wrap_mode = "boundingBox"
            if pk in photo_ov:
                src_photo_name = photo_ov[pk].get("src_photo") or src_photo_name
                if not is_8arg:
                    dst_photo_name = src_photo_name
                caption_text = photo_ov[pk].get("caption") or caption_text
                wrap_mode = photo_ov[pk].get("wrap_mode") or "boundingBox"

            if wrap_mode == "contour":
                cap_y0 = round(cap_y1 - cap_h, 2)
                py1 = round(cap_y0 - 2.0, 2)
                if hasattr(mod, "prepare_cmyk_cropped_photo"):
                    img_p = mod.prepare_cmyk_cropped_photo(src_photo_name, dst_photo_name, px1 - px0, py1 - py0)
                else:
                    img_p = PHOTOS_DIR / src_photo_name
                cutout_png = CUTOUTS_DIR / (Path(dst_photo_name).stem + "_cutout.png")
                create_silhouette_cutout_png(img_p, cutout_png, px1 - px0, py1 - py0)

                r_photo = orig_cmd("frame.create", {
                    "spread": spread_idx,
                    "rect": [px0, py0, px1, py1],
                    "content": "graphic",
                })
                orig_batch([
                    {"command": "file.place", "params": {"frame": r_photo["id"], "path": str(cutout_png)}},
                    {"command": "object.fit", "params": {"ids": [r_photo["id"]], "mode": "fillProportionally"}},
                    {"command": "object.stroke", "params": {"ids": [r_photo["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
                    {"command": "object.textWrap", "params": {"ids": [r_photo["id"]], "mode": "contour", "offset": 6.5}},
                ])
                r_cap = orig_cmd("frame.create", {
                    "spread": spread_idx,
                    "rect": [px0, cap_y0, px1, cap_y1],
                    "content": "text",
                    "text": caption_text,
                })
                orig_batch([
                    {"command": "object.fill", "params": {"ids": [r_cap["id"]], "swatch": "[Paper]", "tint": 0.9}},
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
                    {"command": "type.para", "params": {"attrs": {"align": "left", "firstLineIndent": 0.0, "hyphenate": False, "gridAlign": "none"}}},
                ])
                return r_photo["id"], r_cap["id"]

            if is_8arg:
                return orig_place_photo(spread_idx, px0, py0, px1, cap_y1, src_photo_name, dst_photo_name, caption_text, cap_h=cap_h)
            return orig_place_photo(spread_idx, px0, py0, px1, cap_y1, src_photo_name, caption_text, cap_h=cap_h)

        mod.place_photo_and_caption_cmyk = hooked_place_photo

    def _draw_commercial_ad_on_page():
        if not ad_rect_pt or state["ad_drawn"]:
            return
        state["ad_drawn"] = True
        ax0, ay0, ax1, ay1 = ad_rect_pt
        # Outer Commercial Ad Container Frame
        r_ad_bg = orig_cmd("frame.create", {
            "spread": 0,
            "rect": [ax0, ay0, ax1, ay1],
            "content": "text",
            "text": "",
        })
        orig_batch([
            {"command": "object.fill", "params": {"ids": [r_ad_bg["id"]], "swatch": "EditPointerBg", "tint": 1.0}},
            {"command": "object.stroke", "params": {"ids": [r_ad_bg["id"]], "swatch": "FlyerCrimson", "weight": 2.2, "tint": 1.0}},
            {"command": "object.textWrap", "params": {"ids": [r_ad_bg["id"]], "mode": "boundingBox", "offset": [4.0, 4.0, 4.0, 4.0]}},
        ])
        # Top "विज्ञापन • ADVERTISEMENT" Ribbon
        rib_h = 18.0
        r_rib = orig_cmd("frame.create", {
            "spread": 0,
            "rect": [ax0, ay0, ax1, round(ay0 + rib_h, 2)],
            "content": "text",
            "text": "विज्ञापन  •  COMMERCIAL DISPLAY ADVERTISEMENT",
        })
        orig_batch([
            {"command": "object.fill", "params": {"ids": [r_rib["id"]], "swatch": "FlyerCrimson", "tint": 1.0}},
            {"command": "object.textFrameOptions", "params": {"ids": [r_rib["id"]], "columns": 1, "verticalJustification": "center"}},
            {"command": "text.select", "params": {"story": r_rib["story"], "anchor": 0, "focus": 999}},
            {"command": "type.char", "params": {"attrs": {
                "fontFamily": "DB Hindi",
                "fontStyle": "Bold",
                "size": 10.5,
                "leading": {"kind": "points", "value": 11.5},
                "fill": "[Paper]",
                "fillTint": 1.0,
            }}},
            {"command": "type.para", "params": {"attrs": {"align": "center", "firstLineIndent": 0.0}}},
        ])

        img_file = (ad_cfg.get("image_file") or "").strip()
        if img_file and (CUSTOM_ADS_DIR / img_file).exists():
            r_ad_img = orig_cmd("frame.create", {
                "spread": 0,
                "rect": [round(ax0 + 3.0, 2), round(ay0 + rib_h + 2.0, 2), round(ax1 - 3.0, 2), round(ay1 - 3.0, 2)],
                "content": "graphic",
            })
            orig_batch([
                {"command": "file.place", "params": {"frame": r_ad_img["id"], "path": str(CUSTOM_ADS_DIR / img_file)}},
                {"command": "object.fit", "params": {"ids": [r_ad_img["id"]], "mode": "fillProportionally"}},
            ])
        else:
            adv_name = ad_cfg.get("advertiser") or "आदित्य भारत विशेष उत्सव ऑफर"
            adv_head = ad_cfg.get("headline") or "त्योहारी सीजन में स्वदेशी उत्पादों पर विशेष छूट और आकर्षक उपहार योजना"
            adv_sub = ad_cfg.get("subtext") or "अधिकृत शोरूम एवं सभी प्रमुख विक्रेताओं के यहाँ उपलब्ध • संपर्क : 1800-123-4567"
            ad_text = f"{adv_name}\n{adv_head}\n{adv_sub}"
            r_ad_txt = orig_cmd("frame.create", {
                "spread": 0,
                "rect": [round(ax0 + 10.0, 2), round(ay0 + rib_h + 8.0, 2), round(ax1 - 10.0, 2), round(ay1 - 8.0, 2)],
                "content": "text",
                "text": ad_text,
            })
            b1 = len((adv_name + "\n").encode("utf-8"))
            b2 = b1 + len((adv_head + "\n").encode("utf-8"))
            orig_batch([
                {"command": "object.textFrameOptions", "params": {"ids": [r_ad_txt["id"]], "columns": 1, "verticalJustification": "center"}},
                {"command": "text.select", "params": {"story": r_ad_txt["story"], "anchor": 0, "focus": 9999}},
                {"command": "type.para", "params": {"attrs": {"align": "center", "firstLineIndent": 0.0, "spaceAfter": 8.0}}},
                {"command": "text.select", "params": {"story": r_ad_txt["story"], "anchor": 0, "focus": b1 - 1}},
                {"command": "type.char", "params": {"attrs": {"fontFamily": "DB Hindi 6", "fontStyle": "Regular", "size": 22.0, "leading": {"kind": "points", "value": 24.0}, "fill": "FlyerCrimson"}}},
                {"command": "text.select", "params": {"story": r_ad_txt["story"], "anchor": b1, "focus": b2 - 1}},
                {"command": "type.char", "params": {"attrs": {"fontFamily": "DB Rasrand Bold", "fontStyle": "Bold", "size": 34.0, "leading": {"kind": "points", "value": 36.0}, "fill": "[Black]"}}},
                {"command": "text.select", "params": {"story": r_ad_txt["story"], "anchor": b2, "focus": 9999}},
                {"command": "type.char", "params": {"attrs": {"fontFamily": "DB Hindi", "fontStyle": "Bold", "size": 14.0, "leading": {"kind": "points", "value": 16.0}, "fill": "[Black]"}}},
            ])

    def hooked_rpc(method: str, params: dict = None):
        if method == "app.save" and not state["ad_drawn"]:
            _draw_commercial_ad_on_page()
            orig_cmd("edit.deselectAll", {})
            orig_cmd("view.fitPage", {})
        return orig_rpc(method, params)

    mod.rpc = hooked_rpc

    # Find and invoke the main build_aditya_bharat_page* function
    main_fn = None
    for attr_name in dir(mod):
        if attr_name.startswith("build_aditya_bharat_page"):
            main_fn = getattr(mod, attr_name)
            break
    if not main_fn:
        raise RuntimeError(f"Could not find build function in {script_name}")

    main_fn()
    return {
        "ok": True,
        "page_id": page_id,
        "elapsed_sec": round(time.perf_counter() - t0, 2),
        "ad_preset": ad_preset_id,
    }


# ==============================================================================
# PART 5: NO-CODE VISUAL DRAG-AND-DROP CUSTOM DUMMY BUILDER -> PAGE DESIGNER
# ==============================================================================
def build_custom_dummy_page_in_pd(layout_data: dict) -> dict:
    """
    Takes a user-designed 8-column visual dummy layout from the Browser UI and
    draws it live in Page Designer (34x53 cm, 32x51 cm Print Area, DB Rasrand Bold >= 30pt,
    DB Hindi 11/11.25pt, 3-tone byline, red blurbs, cutouts, commercial ads)
    and exports Aditya_Bharat_Custom_Page_34x53.pagedesigner / .png / .pdf!
    """
    t0 = time.perf_counter()
    spec = importlib.util.spec_from_file_location("ab_base_p8", str(VAULT_DIR / "build_aditya_bharat_page8_desh_videsh.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    mod.connect_page_designer()
    grid = mod.AdityaBharatPage8Grid()

    for _ in range(8):
        try:
            mod.cmd("file.close", {"save": False})
        except Exception:
            break

    page_title = layout_data.get("page_title") or "विशेष पृष्ठ"
    folio_num = layout_data.get("folio") or "09"
    blocks = layout_data.get("blocks") or []

    mod.batch([
        {"command": "file.new", "params": {
            "width": grid.width_pt,
            "height": grid.height_pt,
            "pages": 1,
            "facingPages": False,
            "columns": grid.cols,
            "gutter": grid.gutter_pt,
            "margins": grid.margin_x_pt,
            "title": f"आदित्य भारत — कस्टम पेज ({page_title} | 34x53 सेमी)",
        }},
        {"command": "document.preferences", "params": {
            "baselineGrid": {"start": grid.margin_y_pt, "increment": 11.25, "relativeTo": "topOfPage"}
        }},
        {"command": "swatch.create", "params": {"name": "FlyerCrimson", "color": "#c4121a"}},
        {"command": "swatch.create", "params": {"name": "ClosingGray", "color": "#808285"}},
        {"command": "swatch.create", "params": {"name": "EditPointerBg", "color": "#f2f2f2"}},
    ])

    # Draw 1.5 cm Inside Running Masthead
    mh_x0, mh_y0, mh_x1, mh_y1 = grid.print_x0, grid.masthead_y0, grid.print_x1, grid.masthead_y1
    sec_w = cm(4.4)
    sec_y0 = round(mh_y0 + mm(1.0), 2)
    sec_y1 = round(mh_y1 - mm(1.8), 2)
    r_sec = mod.cmd("frame.create", {"spread": 0, "rect": [mh_x0, sec_y0, round(mh_x0 + sec_w, 2), sec_y1], "content": "text", "text": page_title})
    mod.batch([
        {"command": "object.fill", "params": {"ids": [r_sec["id"]], "swatch": "FlyerCrimson", "tint": 1.0}},
        {"command": "object.textFrameOptions", "params": {"ids": [r_sec["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_sec["story"], "anchor": 0, "focus": 99}},
        {"command": "type.char", "params": {"attrs": {"fontFamily": "DB Hindi 6", "fontStyle": "Regular", "size": 20.0, "leading": {"kind": "points", "value": 21.0}, "fill": "[Paper]"}}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "firstLineIndent": 0.0}}},
    ])
    logo_w = cm(8.5)
    logo_x0 = round((mh_x0 + mh_x1 - logo_w) / 2.0, 2)
    logo_x1 = round(logo_x0 + logo_w, 2)
    r_logo = mod.cmd("frame.create", {"spread": 0, "rect": [logo_x0, round(mh_y0 - 6.0, 2), logo_x1, round(mh_y1 + 4.0, 2)], "content": "text", "text": "आदित्य भारत"})
    mod.batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_logo["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_logo["story"], "anchor": 0, "focus": 99}},
        {"command": "type.char", "params": {"attrs": {"fontFamily": "DB Rasrand Bold", "fontStyle": "Bold", "size": 28.0, "leading": {"kind": "points", "value": 29.0}, "fill": "[Black]"}}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "firstLineIndent": 0.0}}},
    ])
    pnum_w = cm(1.4)
    pnum_x0 = round(mh_x1 - pnum_w, 2)
    r_pnum = mod.cmd("frame.create", {"spread": 0, "rect": [pnum_x0, sec_y0, mh_x1, sec_y1], "content": "text", "text": str(folio_num)})
    mod.batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_pnum["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_pnum["story"], "anchor": 0, "focus": 99}},
        {"command": "type.char", "params": {"attrs": {"fontFamily": "Times New Roman", "fontStyle": "Bold", "size": 18.0, "leading": {"kind": "points", "value": 19.0}, "fill": "[Black]"}}},
        {"command": "type.para", "params": {"attrs": {"align": "right", "firstLineIndent": 0.0}}},
    ])
    dt_x0 = round(logo_x1 + cm(0.4), 2)
    dt_x1 = round(pnum_x0 - cm(0.2), 2)
    r_dt = mod.cmd("frame.create", {"spread": 0, "rect": [dt_x0, sec_y0, dt_x1, sec_y1], "content": "text", "text": "इंदौर, मंगलवार, 20 अक्टूबर 2026  |"})
    mod.batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_dt["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_dt["story"], "anchor": 0, "focus": 199}},
        {"command": "type.char", "params": {"attrs": {"fontFamily": "DB Hindi", "fontStyle": "Bold", "size": 16.0, "leading": {"kind": "points", "value": 17.0}, "fill": "[Black]"}}},
        {"command": "type.para", "params": {"attrs": {"align": "right", "firstLineIndent": 0.0}}},
    ])
    r_mrule = mod.cmd("line.create", {"spread": 0, "a": [mh_x0, mh_y1], "b": [mh_x1, mh_y1]})
    mod.cmd("object.stroke", {"ids": [r_mrule["id"]], "swatch": "[Black]", "weight": 2.0, "tint": 0.60})

    default_body = (
        "भारतीय अर्थव्यवस्था, बुनियादी ढांचे और आधुनिक तकनीक के समन्वय से देश के प्रमुख औद्योगिक और शैक्षणिक केंद्रों में विकास की नई रफ्तार देखने को मिल रही है। "
        "केंद्र और राज्य सरकारों की संयुक्त कार्ययोजना के अंतर्गत स्वच्छ ऊर्जा, डिजिटल सेवा और ग्रामीण संपर्क मार्गों का व्यापक विस्तार किया जा रहा है। "
        "प्रशासनिक सुधारों और आधुनिक निगरानी प्रणाली के लागू होने से आम नागरिकों को त्वरित और पारदर्शी सेवाएं उपलब्ध हो रही हैं।"
    )
    sample_photos = [
        "p1_def_825931.jpg",
        "p8_isro_834820_print.jpg",
        "p4_unsc_828955_print.jpg",
        "p9_antarctica_penguin.jpg",
    ]

    for b_idx, b in enumerate(blocks):
        col = max(1, min(8, int(b.get("col", 1))))
        span = max(1, min(9 - col, int(b.get("span", 3))))
        y0_cm = max(2.8, float(b.get("y0", 2.85)))
        h_cm = max(4.0, float(b.get("h", 10.0)))
        kind = b.get("kind", "story")
        head_txt = (b.get("headline") or b.get("title") or f"विशेष समाचार शीर्षक संख्या {b_idx + 1}").strip()
        sub_txt = (b.get("subhead") or "").strip()
        city_txt = (b.get("city") or "इंदौर").strip()
        agency_txt = (b.get("agency") or "सिटी रिपोर्टर").strip()
        blurb_txt = (b.get("blurb") or "").strip()
        body_txt = (b.get("body") or default_body).strip()
        photo_src = b.get("photo") or sample_photos[b_idx % len(sample_photos)]

        x0 = grid.col_x0(col)
        x1 = grid.col_x1(col, span)
        y0 = cm(y0_cm)
        y1 = mod.snap_frame_bottom_to_baseline(cm(min(52.0, y0_cm + h_cm)))

        # Optional top horizontal separator rule if requested on block
        if b.get("top_rule"):
            ry = round(y0 - mm(1.75), 2)
            r_lr = mod.cmd("line.create", {"spread": 0, "a": [x0, ry], "b": [x1, ry]})
            mod.cmd("object.stroke", {"ids": [r_lr["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

        if kind == "commercial_ad":
            r_ad = mod.cmd("frame.create", {"spread": 0, "rect": [x0, y0, x1, y1], "content": "text", "text": f"विज्ञापन (ADVERTISEMENT)\n{head_txt}\n{sub_txt}"})
            mod.batch([
                {"command": "object.fill", "params": {"ids": [r_ad["id"]], "swatch": "EditPointerBg", "tint": 1.0}},
                {"command": "object.stroke", "params": {"ids": [r_ad["id"]], "swatch": "FlyerCrimson", "weight": 2.0, "tint": 1.0}},
                {"command": "object.textFrameOptions", "params": {"ids": [r_ad["id"]], "columns": 1, "verticalJustification": "center"}},
                {"command": "text.select", "params": {"story": r_ad["story"], "anchor": 0, "focus": 999}},
                {"command": "type.char", "params": {"attrs": {"fontFamily": "DB Rasrand Bold", "fontStyle": "Bold", "size": 28.0, "leading": {"kind": "points", "value": 30.0}, "fill": "[Black]"}}},
                {"command": "type.para", "params": {"attrs": {"align": "center", "firstLineIndent": 0.0}}},
            ])
            continue

        if kind == "gray_box":
            inset_pt = mm(2.5)
            r_gb = mod.cmd("frame.create", {"spread": 0, "rect": [x0, y0, x1, y1], "content": "text", "text": ""})
            mod.batch([
                {"command": "object.fill", "params": {"ids": [r_gb["id"]], "swatch": "[Black]", "tint": 0.15}},
                {"command": "object.stroke", "params": {"ids": [r_gb["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 0.55}},
                {"command": "object.textFrameOptions", "params": {"ids": [r_gb["id"]], "columns": 1, "inset": [inset_pt, inset_pt, inset_pt, inset_pt], "verticalJustification": "top"}},
            ])
            mod.fit_box_completely(r_gb["story"], head_str=head_txt[:32], raw_bullets=f"• {body_txt}")
            continue

        if kind == "photo_feature_box":
            # Bordered Photo Feature Box (like Cols 1..5 in Reference Page 02)
            r_box_bg = mod.cmd("frame.create", {"spread": 0, "rect": [x0, y0, x1, y1], "content": "text", "text": ""})
            mod.batch([
                {"command": "object.fill", "params": {"ids": [r_box_bg["id"]], "swatch": "[Paper]", "tint": 1.0}},
                {"command": "object.stroke", "params": {"ids": [r_box_bg["id"]], "swatch": "ClosingGray", "weight": 0.85, "tint": 0.8}},
            ])
            pad = mm(3.0)
            _, _, _, hh = mod.fit_aditya_bharat_headline(
                0, round(x0 + pad, 2), round(y0 + pad, 2), round(x1 - pad, 2),
                raw_text=head_txt, target_lines=1,
                font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]",
                hi_pt=32.0, lo_pt=19.0, align="center",
            )
            py0 = round(y0 + pad + hh + 3.0, 2)
            cap_txt = sub_txt or f"{head_txt}। — फाइल फोटो"
            mod.place_photo_and_caption_cmyk(
                0, round(x0 + pad, 2), py0, round(x1 - pad, 2), round(y1 - pad, 2),
                photo_src, f"ab_custom_pf_{b_idx}.jpg", cap_txt, cap_h=20.0,
            )
            continue

        if kind == "tall_story_sidebar" and span == 3:
            # 3-Column Tall Story with Kicker + 2-Line Headline + Cols 1..2 Body + Col 3 Shaded Sidebar Box with Photo
            cur_y = y0
            if sub_txt:
                _, _, _, sh = mod.fit_aditya_bharat_headline(
                    0, x0, cur_y, x1, raw_text=sub_txt, target_lines=1,
                    font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]",
                    hi_pt=14.5, lo_pt=11.5, align="left",
                )
                cur_y = round(cur_y + sh + 1.0, 2)
            _, _, _, hh = mod.fit_aditya_bharat_headline(
                0, x0, cur_y, x1, raw_text=head_txt, target_lines=2,
                font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]",
                hi_pt=44.0, lo_pt=32.0, align="left",
            )
            cur_y = round(cur_y + hh + 2.0, 2)
            r_b = mod.cmd("frame.create", {"spread": 0, "rect": [x0, cur_y, x1, y1], "content": "text", "text": ""})
            mod.cmd("object.textFrameOptions", {"ids": [r_b["id"]], "columns": 3, "gutter": grid.gutter_pt, "verticalJustification": "top", "columnRule": False})

            # Place Right-Col Shaded Sidebar Box flush with cur_y so no stray line appears above it
            sb_col = col + 2
            sb_x0 = grid.col_x0(sb_col)
            sb_x1 = grid.col_x1(sb_col, 1)
            sb_y0 = cur_y
            sb_y1 = round(mod.snap_underflow_top(y1, num_underflow_lines=8) - 3.2, 2)
            if sb_y1 > sb_y0 + cm(6.0):
                inset_pt = mm(2.2)
                r_sb = mod.cmd("frame.create", {"spread": 0, "rect": [sb_x0, sb_y0, sb_x1, sb_y1], "content": "text", "text": ""})
                mod.batch([
                    {"command": "object.fill", "params": {"ids": [r_sb["id"]], "swatch": "[Black]", "tint": 0.14}},
                    {"command": "object.stroke", "params": {"ids": [r_sb["id"]], "swatch": "[Black]", "weight": 0.65, "tint": 0.45}},
                    {"command": "object.textFrameOptions", "params": {"ids": [r_sb["id"]], "columns": 1, "inset": [inset_pt, inset_pt, inset_pt, inset_pt], "verticalJustification": "top"}},
                    {"command": "object.textWrap", "params": {"ids": [r_sb["id"]], "mode": "boundingBox", "offset": [4.0, 0.0, 3.0, 0.0]}},
                ])
                mod.fit_box_completely(r_sb["story"], head_str=blurb_txt or "संवाद", raw_bullets="• स्वच्छता सर्वेक्षण और मेट्रो फीडर मार्गों की नियमित समीक्षा।\n• नागरिकों की शिकायतों के त्वरित निराकरण हेतु वार्ड स्तर पर शिविर।")
            mod.fit_aditya_bharat_body(r_b["story"], city_txt, agency_txt, body_txt)
            continue

        if kind in ("flyer", "lead", "anchor", "story_photo", "cutout_story") and span >= 3:
            cur_y = y0
            # If subhead_pos == 'above' (or story_photo with sub_txt kicker), place kicker above headline!
            sub_above = (b.get("subhead_pos") == "above") or (kind == "story_photo" and bool(sub_txt))
            if sub_above and sub_txt:
                _, _, _, sh = mod.fit_aditya_bharat_headline(
                    0, x0, cur_y, x1, raw_text=sub_txt, target_lines=1,
                    font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]",
                    hi_pt=15.0, lo_pt=11.5, align="center" if kind in ("flyer", "anchor") else "left",
                )
                cur_y = round(cur_y + sh + 1.0, 2)

            target_lines = int(b.get("head_lines") or (1 if (kind in ("flyer", "anchor") and span >= 5) else 2))
            hi_pt = 58.0 if kind in ("flyer", "lead") else (48.0 if kind == "anchor" else 38.0)
            _, _, _, hh = mod.fit_aditya_bharat_headline(
                0, x0, cur_y, x1, raw_text=head_txt, target_lines=target_lines,
                font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]",
                hi_pt=hi_pt, lo_pt=30.0, align="center" if kind in ("flyer", "anchor") else "left",
            )
            cur_y = round(cur_y + hh + 1.5, 2)

            if not sub_above and sub_txt and kind in ("flyer", "lead", "anchor"):
                _, _, _, sh = mod.fit_aditya_bharat_headline(
                    0, x0, cur_y, x1, raw_text=sub_txt, target_lines=1,
                    font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]",
                    hi_pt=15.5, lo_pt=12.0, align="center" if kind in ("flyer", "anchor") else "left",
                )
                cur_y = round(cur_y + sh + 1.5, 2)

            r_b = mod.cmd("frame.create", {"spread": 0, "rect": [x0, cur_y, x1, y1], "content": "text", "text": ""})
            mod.cmd("object.textFrameOptions", {"ids": [r_b["id"]], "columns": span, "gutter": grid.gutter_pt, "verticalJustification": "top", "columnRule": False})
            if blurb_txt:
                mod.place_red_subject_blurb(0, x0, round(cur_y + cm(1.55), 2), blurb_txt)

            p_col = int(b.get("photo_col") or (col + max(1, (span - 2) // 2)))
            p_span = int(b.get("photo_span") or (3 if span >= 6 else (1 if span == 3 else 2)))
            px0 = grid.col_x0(p_col)
            px1 = grid.col_x1(p_col, p_span)
            uf_lines = int(b.get("underflow_lines") or 4)
            cap_y1 = round(mod.snap_underflow_top(y1, num_underflow_lines=uf_lines) - 3.2, 2)
            if cap_y1 > cur_y + 52.0:
                if kind == "cutout_story":
                    img_p = mod.prepare_cmyk_cropped_photo(photo_src, f"ab_custom_{b_idx}.jpg", px1 - px0, cap_y1 - cur_y)
                    cut_png = CUTOUTS_DIR / f"ab_custom_{b_idx}_cutout.png"
                    create_silhouette_cutout_png(img_p, cut_png, px1 - px0, cap_y1 - cur_y)
                    r_ph = mod.cmd("frame.create", {"spread": 0, "rect": [px0, cur_y, px1, cap_y1], "content": "graphic"})
                    mod.batch([
                        {"command": "file.place", "params": {"frame": r_ph["id"], "path": str(cut_png)}},
                        {"command": "object.fit", "params": {"ids": [r_ph["id"]], "mode": "fillProportionally"}},
                        {"command": "object.textWrap", "params": {"ids": [r_ph["id"]], "mode": "contour", "offset": 6.5}},
                    ])
                else:
                    mod.place_photo_and_caption_cmyk(0, px0, cur_y, px1, cap_y1, photo_src, f"ab_custom_{b_idx}.jpg", f"{head_txt}। — फाइल फोटो", cap_h=20.0)

            mod.fit_aditya_bharat_body(r_b["story"], city_txt, agency_txt, body_txt)
        else:
            cur_y = y0
            if sub_txt:
                _, _, _, sh = mod.fit_aditya_bharat_headline(
                    0, x0, cur_y, x1, raw_text=sub_txt, target_lines=1,
                    font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]",
                    hi_pt=13.5, lo_pt=11.0, align="left",
                )
                cur_y = round(cur_y + sh + 1.0, 2)
            mod.place_multi_col_story(
                grid, x0, x1, cur_y, y1, cols=span,
                headline=head_txt, city=city_txt, agency=agency_txt,
                blurb_word=blurb_txt, body=body_txt, target_lines=int(b.get("head_lines") or 2), hi_pt=36.0, lo_pt=30.0,
            )

    mod.cmd("edit.deselectAll", {})
    mod.cmd("view.fitPage", {})

    out_pd = VAULT_DIR / "Aditya_Bharat_Custom_Page_34x53.pagedesigner"
    out_png = VAULT_DIR / "Aditya_Bharat_Custom_Page_34x53.png"
    out_pdf = VAULT_DIR / "Aditya_Bharat_Custom_Page_CMYK_34x53.pdf"
    mod.rpc("app.save", {"path": str(out_pd)})
    mod.rpc("app.export", {"path": str(out_png), "page": 0, "scale": 1.5})
    try:
        mod.rpc("engine.execute", {"command": "file.exportPdf", "params": {"path": str(out_pdf)}})
    except Exception:
        pass
    mod.rpc("ui.focus", {})
    return {
        "ok": True,
        "elapsed_sec": round(time.perf_counter() - t0, 2),
        "pd_file": out_pd.name,
        "png_file": out_png.name,
        "pdf_file": out_pdf.name,
    }
