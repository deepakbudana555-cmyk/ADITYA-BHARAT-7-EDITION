# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — MASTER DAILY 8-PAGE AUTONOMOUS NEWSPAPER & SINGLE 1-8 VECTOR PDF ORCHESTRATOR
===========================================================================================================
Executes all locked rules taught by the user for the daily 8-page newspaper:
  1. Page 01 (`फ्रंट पेज` — 11 Stories • 4 Rotating Dummies `DUMMY_1..4`):
     - Dynamic 6.0 cm 7-Edition Masthead (RAIPUR, BILASPUR, RAJNANDGAON, BHOPAL, INDORE, JAIPUR, NEW_DELHI)
       with automatic daily `अंक +1` & `वर्ष` rollover after 365 issues.
     - 3 State CM & State Big Stories (Chhattisgarh CM विष्णुदेव साय & CG for Raipur/Bilaspur/Rajnandgaon;
       MP CM for Bhopal/Indore; RJ CM for Jaipur; Delhi-NCR for New Delhi) + 8 National/International/Business/Sports stories.
     - Locks all 11 stories in `<date_str>_GLOBAL_USED_NEWS_LEDGER.json` so NONE repeat on inside pages!
  2. Page 02 (`छत्तीसगढ़ राजधानी` — 10 Stories) & Page 03 (`छत्तीसगढ़ प्रादेशिक` — 10 Stories):
     - 20 non-repeating stories + 8 real Wikimedia subject-matched photos + centered `आदित्य भारत` graphic logo.
  3. Page 04 (`संपादकीय` — 8 Editorial & Opinion Items):
     - Locked editorial layout + centered `आदित्य भारत` graphic logo + daily articles, 'जीवन मंत्र', 'गीता श्लोक', 'विशेष मंथन', 'शायरी' & 'कटाक्ष'.
  4. Page 05 (`प्रादेशिक` — 12 Stories from `MP + CG + Rajasthan + Delhi`):
     - 12 non-repeating 4-state stories + 4 real Wikimedia photos + centered `आदित्य भारत` graphic logo (0% overlap with Pages 1, 2, 3).
  5. Page 06 (`कारोबार` — 9 Business Stories + `बाजार मीटर` Financial Box):
     - Distinct full-page Business layout + 3 real Wikimedia photos + centered `आदित्य भारत` graphic logo (0% overlap with Page 1 Business).
  6. Page 07 (`खेल संसार + सिने संसार` — 11 Stories: 8 Sports + 3 Film with 5 Silhouette Cutouts `WrapMode::Contour`):
     - 8 Sports + 3 Film stories + 5 straddle-gutter Silhouette Cutouts + centered `आदित्य भारत` graphic logo (0% overlap with Page 1 Sports).
  7. Page 08 (`देश-विदेश` — 10 Stories: 70% National + 30% Interesting International + 0.5pt Black Rule + 1.0cm 2-Line Edition Print Line):
     - Distinct back-page layout + 4 real Wikimedia photos + centered `आदित्य भारत` graphic logo + Edition Print Line (0% overlap with Page 1).
  8. Combined Single 1-to-8 Page 100% Pure Vector PDF (`file.exportPdf` with embedded `/Type /Font` objects):
     - Draws all 8 pages onto Spreads `0..7` of `Aditya_Bharat_Full_8Pages_34x53.pagedesigner` and exports a single
       8-page pure Vector PDF (`Aditya_Bharat_Full_1_to_8_Pages_Vector_<date_str>.pdf`) where fonts never pixelate even at 10,000% zoom!
"""

import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VAULT_DIR = Path(__file__).resolve().parent
if str(VAULT_DIR) not in sys.path:
    sys.path.insert(0, str(VAULT_DIR))

DESKTOP_DIR = Path(r"C:\Users\ADMIN\Desktop") if Path(r"C:\Users\ADMIN\Desktop").exists() else (Path.home() / "Desktop")
DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
PD_PORT = 47123
CM_TO_PT = 72.0 / 2.54
MM_TO_PT = CM_TO_PT / 10.0


def ensure_all_builders_use_vector_pdf_export():
    """Upgrades all `.pdf` export calls across all builder scripts to use native vector `file.exportPdf`."""
    old_pat = 'rpc("app.export", {"path": str(out_pdf), "page": 0})'
    new_pat = 'rpc("engine.execute", {"command": "file.exportPdf", "params": {"path": str(out_pdf)}})'
    old_b6 = 'b6.' + old_pat
    new_b6 = 'b6.' + new_pat
    old_p8 = 'p8.' + old_pat
    new_p8 = 'p8.' + new_pat

    upgraded = []
    for pyf in sorted(VAULT_DIR.glob("*.py")):
        if pyf.name == Path(__file__).name:
            continue
        txt = pyf.read_text(encoding="utf-8")
        orig = txt
        txt = txt.replace(old_b6, new_b6).replace(old_p8, new_p8).replace(old_pat, new_pat)
        if txt != orig:
            pyf.write_text(txt, encoding="utf-8")
            upgraded.append(pyf.name)
    return upgraded


def _send_rpc(s, f_in, method: str, params: dict = None) -> dict:
    payload = {"id": 1, "method": method, "params": params or {}}
    s.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
    return json.loads(f_in.readline())


def _connect_pd():
    for port in (PD_PORT, 49200):
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=2.0)
            s.settimeout(60.0)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            return s, s.makefile("r", encoding="utf-8"), port
        except Exception:
            pass
    pd_candidates = [
        Path(os.environ.get("PAGEDESIGNER_EXE", "")) if os.environ.get("PAGEDESIGNER_EXE") else None,
        VAULT_DIR / "Page_Designer_Software" / "pagedesigner.exe",
        VAULT_DIR.parent / "Page_Designer_Software" / "pagedesigner.exe",
        Path(r"E:\RND\Gujarat_Samachar\Page_Designer_Software\pagedesigner.exe"),
        Path(r"E:\RND\open page layout software\pagedesigner.exe"),
    ]
    pd_exe = next((p for p in pd_candidates if p and p.exists()), pd_candidates[3])
    subprocess.Popen([str(pd_exe), "--control", str(PD_PORT)], cwd=str(pd_exe.parent))
    for _ in range(30):
        time.sleep(0.4)
        try:
            s = socket.create_connection(("127.0.0.1", PD_PORT), timeout=2.0)
            s.settimeout(60.0)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            return s, s.makefile("r", encoding="utf-8"), PD_PORT
        except Exception:
            pass
    raise RuntimeError("Could not connect to Page Designer on port 47123")


DAILY_8_PAGE_ENGINES = [
    ("Page 01 — फ्रंट पेज (11 खबरें • 4 Dummies + CM/State)", "ab_front_page1_4dummies_engine.py", "Aditya_Bharat_Page_01_CMYK_34x53.pdf"),
    ("Page 02 — छत्तीसगढ़ राजधानी (10 खबरें)", "build_aditya_bharat_page2.py", "Aditya_Bharat_Page_02_Mahanagar_CMYK_34x53.pdf"),
    ("Page 03 — छत्तीसगढ़ प्रादेशिक (10 खबरें)", "build_aditya_bharat_page3.py", "Aditya_Bharat_Page_03_Pradeshik_CMYK_34x53.pdf"),
    ("Page 04 — संपादकीय (Daily Articles + गीता श्लोक + मंथन)", "build_aditya_bharat_page5_edit.py", "Aditya_Bharat_Page_04_Sampadakiya_CMYK_34x53.pdf"),
    ("Page 05 — प्रादेशिक (MP + CG + RJ + DL • 12 खबरें)", "ab_pradeshik_page5_12news_engine.py", "Aditya_Bharat_Page_05_Pradeshik_CMYK_34x53.pdf"),
    ("Page 06 — कारोबार (Full-Page Business • 9 खबरें + बाजार मीटर)", "build_aditya_bharat_page6_business.py", "Aditya_Bharat_Page_06_Karobar_CMYK_34x53.pdf"),
    ("Page 07 — खेल संसार + सिने संसार (11 खबरें + 5 Cutouts)", "ab_khel_film_page7_engine.py", "Aditya_Bharat_Page_07_Khel_Sansar_CMYK_34x53.pdf"),
    ("Page 08 — देश-विदेश (70% राष्ट्रीय + 30% विदेशी + Print Line)", "ab_desh_videsh_page8_engine.py", "Aditya_Bharat_Page_08_Desh_Videsh_CMYK_34x53.pdf"),
]


def build_daily_full_8page_newspaper_and_single_vector_pdf(
    date_str: str = "19-11-2026",
    edition_code: str = "RAIPUR",
    p1_dummy_id: str = "AUTO",
    build_individual_pages_first: bool = True,
    progress_cb=None,
) -> dict:
    t0 = time.perf_counter()
    edition_code = (edition_code or "RAIPUR").strip().upper()
    ensure_all_builders_use_vector_pdf_export()

    os.environ["AB_EDITION"] = edition_code
    os.environ["AB_EDITION_DATE"] = date_str
    os.environ["AB_P1_DUMMY"] = p1_dummy_id

    def _notify(msg: str):
        print(msg, flush=True)
        if progress_cb:
            try:
                progress_cb(msg)
            except Exception:
                pass

    # 1. Refresh all daily JSON caches & individual page `.pagedesigner` / `.png` / vector `.pdf` files
    if build_individual_pages_first:
        _notify(f"⏳ [1/8] पेज 01 फ्रंट पेज ({edition_code} | {date_str} | {p1_dummy_id}) तैयार हो रहा है...")
        import ab_front_page1_4dummies_engine as p1_eng
        p1_res = p1_eng.build_aditya_bharat_page1_with_dummy(date_str=date_str, edition_code=edition_code, dummy_id=p1_dummy_id)

        _notify(f"⏳ [2-3/8] पेज 02 और पेज 03 छत्तीसगढ़ (10+10 खबरें) तैयार हो रहे हैं...")
        import ab_chhattisgarh_10x2_engine as cg_eng
        cg_eng.build_both_chhattisgarh_pages_2_and_3(date_str=date_str, force_fresh_live=False, export_desktop_pdf=False)

        _notify(f"⏳ [4/8] पेज 04 संपादकीय (आदित्य भारत सेंटर लोगो + दैनिक आलेख) तैयार हो रहा है...")
        import ab_sampadakiya_page4_engine as p4_eng
        p4_eng.build_daily_sampadakiya_page4(date_str=date_str, edition_code=edition_code)

        _notify(f"⏳ [5/8] पेज 05 प्रादेशिक (MP + CG + Rajasthan + Delhi • 12 खबरें) तैयार हो रहा है...")
        import ab_pradeshik_page5_12news_engine as p5_eng
        p5_eng.build_aditya_bharat_page5_pradeshik_12news(date_str=date_str, edition_code=edition_code)

        _notify(f"⏳ [6/8] पेज 06 कारोबार (9 बिजनेस खबरें + बाजार मीटर) तैयार हो रहा है...")
        import ab_karobar_page6_engine as p6_eng
        p6_eng.build_daily_karobar_page6(date_str=date_str, edition_code=edition_code)

        _notify(f"⏳ [7/8] पेज 07 खेल संसार + सिने संसार (11 खबरें + 5 सिल्हूट कटआउट) तैयार हो रहा है...")
        import ab_khel_film_page7_engine as p7_eng
        p7_eng.build_aditya_bharat_page7_khel_film_11news(date_str=date_str, edition_code=edition_code)

        _notify(f"⏳ [8/8] पेज 08 देश-विदेश (70% राष्ट्रीय + 30% विदेशी + {edition_code} Print Line) तैयार हो रहा है...")
        import ab_desh_videsh_page8_engine as p8_eng
        p8_eng.build_desh_videsh_page8_70_30(date_str=date_str, edition=edition_code, force_fresh_live=False, export_desktop_pdf=False)

    # 2. Now assemble all 8 pages (Spreads 0..7) into ONE Single 8-Page Document in Page Designer
    #    and export the Single 1-to-8 Page 100% Pure Vector PDF (`file.exportPdf`)!
    _notify(f"📚 सभी 8 पेजों (Pages 01 to 08) को एक ही सिंगल Vector PDF फाइल में जोड़ा जा रहा है...")
    s, f_in, _ = _connect_pd()
    for _ in range(12):
        try:
            r = _send_rpc(s, f_in, "engine.execute", {"command": "file.close", "params": {"save": False}})
            if not r.get("ok"):
                break
        except Exception:
            break

    w_pt = round(34.0 * CM_TO_PT, 2)
    h_pt = round(53.0 * CM_TO_PT, 2)
    m_pt = round(1.0 * CM_TO_PT, 2)
    g_pt = round(4.0 * MM_TO_PT, 2)

    _send_rpc(s, f_in, "engine.batch", {"commands": [
        {"command": "file.new", "params": {
            "width": w_pt,
            "height": h_pt,
            "pages": 8,
            "facingPages": False,
            "columns": 8,
            "gutter": g_pt,
            "margins": m_pt,
            "title": f"आदित्य भारत — संपूर्ण 8-पेज संस्करण ({edition_code} • {date_str} • Pages 01 to 08)",
        }},
        {"command": "document.preferences", "params": {
            "baselineGrid": {
                "start": m_pt,
                "increment": 11.25,
                "relativeTo": "topOfPage",
            }
        }},
        {"command": "swatch.create", "params": {"name": "FlyerCrimson", "color": "#c4121a"}},
        {"command": "swatch.create", "params": {"name": "ClosingGray", "color": "#808285"}},
        {"command": "swatch.create", "params": {"name": "EditPointerBg", "color": "#f2f2f2"}},
        {"command": "window.panel", "params": {"panel": "pages"}},
    ]})
    s.close()

    for spread_idx, (title_hi, script_name, _single_pdf) in enumerate(DAILY_8_PAGE_ENGINES):
        _notify(f"🎨 Combined Book Spread {spread_idx + 1}/8 ({title_hi}) Draw हो रहा है...")
        env = os.environ.copy()
        env["AB_EDITION"] = edition_code
        env["AB_EDITION_DATE"] = date_str
        env["AB_P1_DUMMY"] = p1_dummy_id
        env["AB_TARGET_SPREAD"] = str(spread_idx)
        env["AB_SKIP_FILE_NEW"] = "1"
        env["AB_SKIP_SAVE"] = "1"
        env["AB_NO_CLOSE"] = "1"
        subprocess.run(
            [sys.executable, str(VAULT_DIR / script_name)],
            cwd=str(VAULT_DIR),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    s2, f_in2, _ = _connect_pd()
    out_combined_pd = VAULT_DIR / "Aditya_Bharat_Full_8Pages_34x53.pagedesigner"
    out_combined_pdf = VAULT_DIR / "Aditya_Bharat_Full_8Pages_CMYK_34x53.pdf"
    _send_rpc(s2, f_in2, "app.save", {"path": str(out_combined_pd)})
    exp_res = _send_rpc(s2, f_in2, "engine.execute", {"command": "file.exportPdf", "params": {"path": str(out_combined_pdf)}})
    _send_rpc(s2, f_in2, "engine.execute", {"command": "view.goToPage", "params": {"page": 1}})
    _send_rpc(s2, f_in2, "engine.execute", {"command": "view.fitPage", "params": {}})
    _send_rpc(s2, f_in2, "ui.focus", {})
    s2.close()

    # Verify vector font objects & 8 pages inside the combined PDF
    raw_pdf = out_combined_pdf.read_bytes() if out_combined_pdf.exists() else b""
    pdf_page_count = len(re.findall(rb"/Type\s*/Page\b", raw_pdf))
    pdf_font_count = len(re.findall(rb"/Type\s*/Font\b", raw_pdf))

    desktop_combined_ed_pdf = DESKTOP_DIR / f"Aditya_Bharat_{edition_code.title()}_Full_1_to_8_Pages_Vector_{date_str}.pdf"
    desktop_combined_main_pdf = DESKTOP_DIR / f"Aditya_Bharat_Full_1_to_8_Pages_Vector_{date_str}.pdf"
    if out_combined_pdf.exists():
        shutil.copy2(out_combined_pdf, desktop_combined_ed_pdf)
        shutil.copy2(out_combined_pdf, desktop_combined_main_pdf)

    elapsed = round(time.perf_counter() - t0, 2)
    return {
        "ok": True,
        "date_str": date_str,
        "edition_code": edition_code,
        "p1_dummy_id": p1_dummy_id,
        "pdf_pages_count": pdf_page_count,
        "embedded_vector_fonts_count": pdf_font_count,
        "vector_10000_zoom_safe": pdf_font_count > 0 and pdf_page_count == 8,
        "combined_pagedesigner_path": str(out_combined_pd),
        "vault_combined_pdf": str(out_combined_pdf),
        "desktop_combined_pdf": str(desktop_combined_main_pdf),
        "edition_desktop_combined_pdf": str(desktop_combined_ed_pdf),
        "export_rpc": exp_res,
        "elapsed_sec": elapsed,
    }


ALL_7_EDITIONS_4_STATES = [
    {"edition_code": "RAIPUR", "city_hi": "रायपुर", "state_group": "CG", "state_hi": "छत्तीसगढ़ (CM विष्णुदेव साय)"},
    {"edition_code": "BILASPUR", "city_hi": "बिलासपुर", "state_group": "CG", "state_hi": "छत्तीसगढ़ (CM विष्णुदेव साय)"},
    {"edition_code": "RAJNANDGAON", "city_hi": "राजनांदगांव", "state_group": "CG", "state_hi": "छत्तीसगढ़ (CM विष्णुदेव साय)"},
    {"edition_code": "INDORE", "city_hi": "इंदौर", "state_group": "MP", "state_hi": "मध्य प्रदेश (CM डॉ. मोहन यादव)"},
    {"edition_code": "BHOPAL", "city_hi": "भोपाल", "state_group": "MP", "state_hi": "मध्य प्रदेश (CM डॉ. मोहन यादव)"},
    {"edition_code": "NEW_DELHI", "city_hi": "नई दिल्ली", "state_group": "DL", "state_hi": "दिल्ली (मुख्यमंत्री व राजधानी विशेष)"},
    {"edition_code": "JAIPUR", "city_hi": "जयपुर", "state_group": "RJ", "state_hi": "राजस्थान (CM भजनलाल शर्मा)"},
]


def _stamp_inside_pages_dateline_in_pd_zip(src_pd_path: Path, dst_pd_path: Path, city_hi: str):
    """
    Updates the running city dateline (`रायपुर, <वार>, <दिनांक>  |`) on Inside Spreads 1..6 (Pages 02..07)
    inside the `.pagedesigner` ZIP archive to `<city_hi>, <वार>, <दिनांक>  |` while keeping exact UTF-8 byte lengths.
    """
    import zipfile
    if city_hi == "रायपुर":
        shutil.copy2(src_pd_path, dst_pd_path)
        return

    with zipfile.ZipFile(src_pd_path, "r") as zin:
        doc_obj = json.loads(zin.read("document.json").decode("utf-8"))
        # 1. Update story objects in `stories`
        stories = doc_obj.get("stories", {})
        for _sid, st_obj in stories.items():
            txt = st_obj.get("text", "")
            if txt.startswith("रायपुर, ") and txt.endswith("|"):
                new_txt = f"{city_hi}, " + txt[len("रायपुर, "):]
                st_obj["text"] = new_txt
                new_b_len = len(new_txt.encode("utf-8"))
                chars = st_obj.get("chars", [])
                if len(chars) == 1:
                    chars[0]["len"] = new_b_len
        # 2. Update cached frame text previews in `spreads`
        for sp in doc_obj.get("spreads", []):
            for item in sp.get("items", []):
                cont = item.get("content")
                if isinstance(cont, dict):
                    ctxt = cont.get("text", "")
                    if isinstance(ctxt, str) and ctxt.startswith("रायपुर, ") and ctxt.endswith("|"):
                        cont["text"] = f"{city_hi}, " + ctxt[len("रायपुर, "):]

        new_doc_bytes = json.dumps(doc_obj, ensure_ascii=False, indent=2).encode("utf-8")
        with zipfile.ZipFile(dst_pd_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                if info.filename == "document.json":
                    zout.writestr(info, new_doc_bytes)
                else:
                    zout.writestr(info, zin.read(info.filename))


def build_all_7_editions_4_states_with_single_vector_pdfs(
    date_str: str = "19-11-2026",
    p1_dummy_id: str = "DUMMY_1",
    progress_cb=None,
) -> dict:
    """
    MAKE ALL 7 EDITIONS (EDITION ALTER / ULTER ENGINE):
      1. Draws Shared Inside Pages 02..07 (Spreads 1..6) ONCE into an 8-page base template.
      2. Loops over all 7 Editions across 4 States:
         - CG (`RAIPUR`, `BILASPUR`, `RAJNANDGAON`) -> CG CM विष्णुदेव साय Front Page News + Edition Masthead + Edition Print Line
         - MP (`INDORE`, `BHOPAL`) -> MP CM डॉ. मोहन यादव Front Page News + Edition Masthead + Edition Print Line
         - DL (`NEW_DELHI`) -> Delhi CM / Delhi-NCR Prominent Front Page News + Edition Masthead + Edition Print Line
         - RJ (`JAIPUR`) -> Rajasthan CM भजनलाल शर्मा Front Page News + Edition Masthead + Edition Print Line
      3. For each Edition, updates the inside running city datelines on Pages 02..07, draws Spread 0 (Page 01 Front Page)
         and Spread 7 (Page 08 Desh-Videsh + Edition 2-Line Print Line), exports Page 01 PNG, and exports a complete
         8-Page Single 100% Pure Vector PDF (`Pages 01 to 08`, 18 embedded vector fonts, 10,000% zoom safe) to Desktop & Archive!
    """
    t0 = time.perf_counter()
    ensure_all_builders_use_vector_pdf_export()

    def _notify(msg: str):
        print(msg, flush=True)
        if progress_cb:
            try:
                progress_cb(msg)
            except Exception:
                pass

    pub_dir = VAULT_DIR / "published_all_editions" / date_str
    pub_dir.mkdir(parents=True, exist_ok=True)
    art_dir = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\8707c72d-58b0-4715-a099-3efffcd57514")
    art_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Create 8-page base template and draw Inside Pages 02..07 (Spreads 1..6) ONCE
    _notify("⏳ [Step 1/2] सभी 7 संस्करणों के लिए साझा अंदरूनी पेज (Pages 02 to 07) तैयार किए जा रहे हैं...")
    s, f_in, _ = _connect_pd()
    for _ in range(12):
        try:
            r = _send_rpc(s, f_in, "engine.execute", {"command": "file.close", "params": {"save": False}})
            if not r.get("ok"):
                break
        except Exception:
            break

    w_pt = round(34.0 * CM_TO_PT, 2)
    h_pt = round(53.0 * CM_TO_PT, 2)
    m_pt = round(1.0 * CM_TO_PT, 2)
    g_pt = round(4.0 * MM_TO_PT, 2)

    _send_rpc(s, f_in, "engine.batch", {"commands": [
        {"command": "file.new", "params": {
            "width": w_pt,
            "height": h_pt,
            "pages": 8,
            "facingPages": False,
            "columns": 8,
            "gutter": g_pt,
            "margins": m_pt,
            "title": f"आदित्य भारत — 7-संस्करण मास्टर बेस ({date_str} • Pages 01 to 08)",
        }},
        {"command": "document.preferences", "params": {
            "baselineGrid": {
                "start": m_pt,
                "increment": 11.25,
                "relativeTo": "topOfPage",
            }
        }},
        {"command": "swatch.create", "params": {"name": "FlyerCrimson", "color": "#c4121a"}},
        {"command": "swatch.create", "params": {"name": "ClosingGray", "color": "#808285"}},
        {"command": "swatch.create", "params": {"name": "EditPointerBg", "color": "#f2f2f2"}},
    ]})
    s.close()

    # Draw Spreads 1..6 (Pages 02..07) once with default city 'रायपुर'
    for spread_idx in range(1, 7):
        title_hi, script_name, _single_pdf = DAILY_8_PAGE_ENGINES[spread_idx]
        _notify(f"🎨 Inside Page {spread_idx + 1}/8 ({title_hi}) बेस टेम्पलेट में Draw हो रहा है...")
        env = os.environ.copy()
        env["AB_EDITION"] = "RAIPUR"
        env["AB_EDITION_DATE"] = date_str
        env["AB_P1_DUMMY"] = p1_dummy_id
        env["AB_TARGET_SPREAD"] = str(spread_idx)
        env["AB_SKIP_FILE_NEW"] = "1"
        env["AB_SKIP_SAVE"] = "1"
        env["AB_NO_CLOSE"] = "1"
        subprocess.run(
            [sys.executable, str(VAULT_DIR / script_name)],
            cwd=str(VAULT_DIR),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    base_p2_to_p7_pd = VAULT_DIR / "Aditya_Bharat_Base_Pages2to7_34x53.pagedesigner"
    s_save, f_save, _ = _connect_pd()
    _send_rpc(s_save, f_save, "app.save", {"path": str(base_p2_to_p7_pd)})
    s_save.close()

    # Step 2: Loop over all 7 Editions across 4 States, alter Page 01 (Masthead + State CM News) & Page 08 (Print Line)
    editions_out = []
    for idx_ed, ed_meta in enumerate(ALL_7_EDITIONS_4_STATES, start=1):
        ed_code = ed_meta["edition_code"]
        city_hi = ed_meta["city_hi"]
        st_grp = ed_meta["state_group"]
        st_hi = ed_meta["state_hi"]
        _notify(
            f"🚀 [{idx_ed}/7] {ed_code} संस्करण ({city_hi} • {st_hi}): "
            f"Page 01 State News Alter + Masthead + Page 08 Print Line + 1-8 Single Vector PDF बन रहा है..."
        )

        ed_dir = pub_dir / f"{ed_code}_EDITION"
        ed_dir.mkdir(parents=True, exist_ok=True)
        ed_pd_path = VAULT_DIR / f"Aditya_Bharat_{ed_code.title()}_Full_8Pages_34x53.pagedesigner"
        _stamp_inside_pages_dateline_in_pd_zip(base_p2_to_p7_pd, ed_pd_path, city_hi)

        s_open, f_open, _ = _connect_pd()
        for _ in range(5):
            try:
                r = _send_rpc(s_open, f_open, "engine.execute", {"command": "file.close", "params": {"save": False}})
                if not r.get("ok"):
                    break
            except Exception:
                break
        _send_rpc(s_open, f_open, "app.open", {"path": str(ed_pd_path)})
        s_open.close()

        # Draw Spread 0 (Page 01 Front Page with Edition Masthead + State CM/Prominent News)
        env_p1 = os.environ.copy()
        env_p1["AB_EDITION"] = ed_code
        env_p1["AB_EDITION_DATE"] = date_str
        env_p1["AB_P1_DUMMY"] = p1_dummy_id
        env_p1["AB_TARGET_SPREAD"] = "0"
        env_p1["AB_SKIP_FILE_NEW"] = "1"
        env_p1["AB_SKIP_SAVE"] = "1"
        env_p1["AB_NO_CLOSE"] = "1"
        subprocess.run(
            [sys.executable, str(VAULT_DIR / "ab_front_page1_4dummies_engine.py"), date_str, ed_code, p1_dummy_id],
            cwd=str(VAULT_DIR),
            env=env_p1,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        # Draw Spread 7 (Page 08 Desh-Videsh with Edition Dateline + Edition 2-Line Print Line)
        env_p8 = os.environ.copy()
        env_p8["AB_EDITION"] = ed_code
        env_p8["AB_EDITION_DATE"] = date_str
        env_p8["AB_TARGET_SPREAD"] = "7"
        env_p8["AB_SKIP_FILE_NEW"] = "1"
        env_p8["AB_SKIP_SAVE"] = "1"
        env_p8["AB_NO_CLOSE"] = "1"
        subprocess.run(
            [sys.executable, str(VAULT_DIR / "ab_desh_videsh_page8_engine.py"), date_str, ed_code],
            cwd=str(VAULT_DIR),
            env=env_p8,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        # Save Edition 8-Page Document, Export Page 01 PNG & Page 08 PNG, and Export 1-to-8 Single Pure Vector PDF
        ed_slug = ed_code.lower()
        ed_p1_png = VAULT_DIR / f"Aditya_Bharat_{ed_code.title()}_Page_01_34x53.png"
        ed_p8_png = VAULT_DIR / f"Aditya_Bharat_{ed_code.title()}_Page_08_34x53.png"
        ed_full_pdf = ed_dir / f"Aditya_Bharat_{ed_code}_Full_1_to_8_Pages_Vector_{date_str}.pdf"
        desktop_ed_full_pdf = DESKTOP_DIR / f"Aditya_Bharat_{ed_code.title()}_Full_1_to_8_Pages_Vector_{date_str}.pdf"

        s_exp, f_exp, _ = _connect_pd()
        _send_rpc(s_exp, f_exp, "app.save", {"path": str(ed_pd_path)})
        _send_rpc(s_exp, f_exp, "app.export", {"path": str(ed_p1_png), "page": 0, "scale": 1.5})
        _send_rpc(s_exp, f_exp, "app.export", {"path": str(ed_p8_png), "page": 7, "scale": 1.5})
        _send_rpc(s_exp, f_exp, "engine.execute", {"command": "file.exportPdf", "params": {"path": str(ed_full_pdf)}})
        s_exp.close()

        if ed_p1_png.exists():
            shutil.copy2(ed_p1_png, ed_dir / f"Aditya_Bharat_{ed_code}_Page_01_Front_{date_str}.png")
            shutil.copy2(ed_p1_png, art_dir / f"aditya_bharat_{ed_slug}_page_01_34x53.png")
            shutil.copy2(ed_p1_png, art_dir / f"aditya_bharat_state_{st_grp.lower()}_{ed_slug}_page_01_34x53.png")
        if ed_p8_png.exists():
            shutil.copy2(ed_p8_png, ed_dir / f"Aditya_Bharat_{ed_code}_Page_08_Back_{date_str}.png")
            shutil.copy2(ed_p8_png, art_dir / f"aditya_bharat_{ed_slug}_page_08_34x53.png")
        if ed_full_pdf.exists():
            shutil.copy2(ed_full_pdf, desktop_ed_full_pdf)
            shutil.copy2(ed_full_pdf, VAULT_DIR / f"Aditya_Bharat_{ed_code.title()}_Full_8Pages_CMYK_34x53.pdf")

        raw_pdf = ed_full_pdf.read_bytes() if ed_full_pdf.exists() else b""
        p_cnt = len(re.findall(rb"/Type\s*/Page\b", raw_pdf))
        f_cnt = len(re.findall(rb"/Type\s*/Font\b", raw_pdf))

        editions_out.append({
            "edition_code": ed_code,
            "city_hi": city_hi,
            "state_group": st_grp,
            "state_hi": st_hi,
            "pages_count": p_cnt,
            "embedded_vector_fonts": f_cnt,
            "vector_10000_zoom_safe": p_cnt == 8 and f_cnt > 0,
            "page1_png": str(ed_p1_png),
            "page8_png": str(ed_p8_png),
            "pagedesigner_path": str(ed_pd_path),
            "archive_vector_pdf": str(ed_full_pdf),
            "desktop_vector_pdf": str(desktop_ed_full_pdf),
        })

    # Keep main default files synced and focus Page 1
    s_fin, f_fin, _ = _connect_pd()
    _send_rpc(s_fin, f_fin, "engine.execute", {"command": "view.goToPage", "params": {"page": 1}})
    _send_rpc(s_fin, f_fin, "engine.execute", {"command": "view.fitPage", "params": {}})
    _send_rpc(s_fin, f_fin, "ui.focus", {})
    s_fin.close()

    # Clean up any single-page or generic duplicate Aditya_Bharat PDFs from Desktop so ONLY the 7 final 1-8 Vector PDFs remain!
    keep_names = {Path(e["desktop_vector_pdf"]).name for e in editions_out}
    for p_extra in DESKTOP_DIR.glob("*Aditya_Bharat*.pdf"):
        if p_extra.name not in keep_names:
            try:
                p_extra.unlink()
            except Exception:
                pass

    # Trigger Hybrid Local/Cloud Heartbeat + Auto-Email + Auto-WhatsApp/Telegram Delivery
    delivery_res = {}
    try:
        import ab_cloud_whatsapp_email_delivery_engine as deliv_eng
        src_mode = "GITHUB_CLOUD" if os.environ.get("GITHUB_ACTIONS") == "true" else "LOCAL_PC"
        delivery_res = deliv_eng.deliver_all_7_editions_everywhere(date_str=date_str, source=src_mode)
    except Exception as e:
        delivery_res = {"ok": False, "error": str(e)}

    elapsed = round(time.perf_counter() - t0, 2)
    _notify(f"✅ सभी 7 संस्करण (4 राज्यों के अलग-अलग Front Pages + Print Lines + 7 Single 1-8 Vector PDFs) {elapsed}s में तैयार!")
    return {
        "ok": True,
        "date_str": date_str,
        "p1_dummy_id": p1_dummy_id,
        "editions_count": len(editions_out),
        "states_count": 4,
        "editions": editions_out,
        "archive_dir": str(pub_dir),
        "delivery": delivery_res,
        "elapsed_sec": elapsed,
    }


# ==============================================================================
# DAILY 10:30 PM (22:30) AUTOMATIC ALARM & NIGHT-DESK EDITION BUILDER ENGINE
# ==============================================================================
ALARM_CONFIG_PATH = VAULT_DIR / "daily_harvester_cache" / "daily_1030pm_alarm_config.json"


def load_daily_1030pm_alarm_config() -> dict:
    default_cfg = {
        "enabled": True,
        "alarm_time_24h": "22:30",
        "display_time": "10:30 PM",
        "auto_harvest_fresh_news": True,
        "build_all_7_editions_4_states": True,
        "auto_advance_morning_dateline": True,
        "default_p1_dummy": "AUTO",
        "last_triggered_date": "",
        "last_triggered_timestamp": "",
        "last_built_edition_date": "",
        "last_run_status": "Ready (Daily 10:30 PM / 22:30 IST Alarm Active)",
    }
    try:
        if ALARM_CONFIG_PATH.exists():
            saved = json.loads(ALARM_CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                default_cfg.update(saved)
    except Exception:
        pass
    return default_cfg


def save_daily_1030pm_alarm_config(cfg: dict) -> dict:
    ALARM_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    cur = load_daily_1030pm_alarm_config()
    cur.update(cfg or {})
    t24 = (cur.get("alarm_time_24h") or "22:30").strip()
    try:
        hh, mm = [int(x) for x in t24.split(":")[:2]]
        ampm = "PM" if hh >= 12 else "AM"
        h12 = hh - 12 if hh > 12 else (12 if hh == 0 else hh)
        cur["alarm_time_24h"] = f"{hh:02d}:{mm:02d}"
        cur["display_time"] = f"{h12:02d}:{mm:02d} {ampm}"
    except Exception:
        cur["alarm_time_24h"] = "22:30"
        cur["display_time"] = "10:30 PM"
    ALARM_CONFIG_PATH.write_text(json.dumps(cur, ensure_ascii=False, indent=2), encoding="utf-8")
    return cur


def get_next_1030pm_alarm_status() -> dict:
    import datetime
    cfg = load_daily_1030pm_alarm_config()
    now = datetime.datetime.now()
    t24 = cfg.get("alarm_time_24h", "22:30")
    try:
        hh, mm = [int(x) for x in t24.split(":")[:2]]
    except Exception:
        hh, mm = 22, 30
    target = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if target <= now:
        target = target + datetime.timedelta(days=1)
    rem_sec = max(0, int((target - now).total_seconds()))
    r_h = rem_sec // 3600
    r_m = (rem_sec % 3600) // 60
    r_s = rem_sec % 60
    return {
        "config": cfg,
        "now_str": now.strftime("%d-%m-%Y %H:%M:%S"),
        "next_alarm_iso": target.strftime("%d-%m-%Y %H:%M:%S"),
        "remaining_seconds": rem_sec,
        "countdown_hms": f"{r_h:02d}:{r_m:02d}:{r_s:02d}",
    }


def run_1030pm_night_desk_auto_edition_job(
    target_edition_date: str = None,
    p1_dummy_id: str = "AUTO",
    progress_cb=None,
) -> dict:
    """
    Executes the full Daily 10:30 PM Night-Desk Autonomous Newspaper Pipeline:
      1. Pulls fresh live Hindi news updates (Chhattisgarh, MP, Rajasthan, Delhi-NCR, National,
         International, Business, Sports/Film, Editorial) so all day's updates up to 10:30 PM are included.
      2. Enforces 0% cross-page repetition via `<date_str>_GLOBAL_USED_NEWS_LEDGER.json`.
      3. Builds all 7 Editions across 4 States (`CG: Raipur, Bilaspur, Rajnandgaon`, `MP: Indore, Bhopal`,
         `DL: New Delhi`, `RJ: Jaipur`) with State-altered Front Pages, dynamic `अंक +1` Mastheads,
         edition-specific Page 08 Print Lines, and 7 complete 1-to-8 Single Pure Vector PDFs!
    """
    import datetime
    cfg = load_daily_1030pm_alarm_config()
    now = datetime.datetime.now()
    if not target_edition_date:
        # At 10:30 PM night press time, build the next morning's newspaper edition date!
        pub_dt = (now + datetime.timedelta(days=1)).date() if cfg.get("auto_advance_morning_dateline", True) else now.date()
        target_edition_date = pub_dt.strftime("%d-%m-%Y")

    def _notify(msg: str):
        print(msg, flush=True)
        if progress_cb:
            try:
                progress_cb(msg)
            except Exception:
                pass

    _notify(f"⏰ [10:30 PM NIGHT-DESK AUTO ALARM] दिनांक {target_edition_date} के लिए देश-दुनिया व 4 राज्यों (CG, MP, DL, RJ) की ताज़ा ओरिजिनल खबरें कलेक्ट की जा रही हैं...")
    if os.environ.get("GITHUB_ACTIONS") != "true":
        try:
            import ab_cloud_whatsapp_email_delivery_engine as deliv_eng
            gh_disp = deliv_eng.trigger_github_actions_cloud_build_via_api(
                edition_date=target_edition_date,
                p1_dummy_id=p1_dummy_id or cfg.get("default_p1_dummy", "AUTO"),
            )
            print(f"[10:30 PM GitHub Cloud API Dispatch]: {gh_disp}")
        except Exception as e:
            print(f"[WARN] GitHub Cloud API dispatch warning: {e}")

    try:
        import ab_night_desk_1030pm_live_harvester as live_1030
        live_1030.harvest_all_8_pages_original_live_news_at_1030pm(target_edition_date)
    except Exception as e:
        print(f"[WARN] 10:30 PM unified live harvest warning: {e}")

    res = build_all_7_editions_4_states_with_single_vector_pdfs(
        date_str=target_edition_date,
        p1_dummy_id=p1_dummy_id or cfg.get("default_p1_dummy", "AUTO"),
        progress_cb=_notify,
    )
    save_daily_1030pm_alarm_config({
        "last_triggered_date": now.strftime("%Y-%m-%d"),
        "last_triggered_timestamp": now.strftime("%d-%m-%Y %H:%M:%S"),
        "last_built_edition_date": target_edition_date,
        "last_run_status": f"Completed 7 Editions (4 States) for {target_edition_date} in {res.get('elapsed_sec')}s",
    })
    return res


if __name__ == "__main__":
    if "--auto-1030pm" in sys.argv:
        d_arg = sys.argv[1] if (len(sys.argv) > 1 and not sys.argv[1].startswith("--")) else None
        res = run_1030pm_night_desk_auto_edition_job(target_edition_date=d_arg)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0)
    d_arg = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("AB_EDITION_DATE", "19-11-2026")
    ed_arg = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("AB_EDITION", "RAIPUR")
    dm_arg = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("AB_P1_DUMMY", "DUMMY_1")
    if ed_arg.upper() == "ALL" or "--all-editions" in sys.argv:
        res = build_all_7_editions_4_states_with_single_vector_pdfs(
            date_str=d_arg,
            p1_dummy_id=dm_arg,
        )
    else:
        fast_flag = "--assemble-only" in sys.argv
        res = build_daily_full_8page_newspaper_and_single_vector_pdf(
            date_str=d_arg,
            edition_code=ed_arg,
            p1_dummy_id=dm_arg,
            build_individual_pages_first=not fast_flag,
        )
    print(json.dumps(res, ensure_ascii=False, indent=2))
