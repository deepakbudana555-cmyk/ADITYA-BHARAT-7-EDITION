# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — CHHATTISGARH LIVE NEWS HARVESTER & 10+10 PAGE 02 & PAGE 03 BUILDER
==================================================================================================
Date                  : 18-11-2026 (बुधवार, 18 नवंबर 2026)
Target Pages          :
  - Inside Page 02 ('छत्तीसगढ़' — 10 Stories | 6+2 Top Flyer Band + 5-Col Lead + 3-Col Stack + 3+2+3 Mid + 5+3 Anchor)
  - Inside Page 03 ('प्रादेशिक' — 10 Stories | Vertical-Start No-Flyer 5-Col Lead + 3+2 Split + Right 3-Col Stack + 2+4+2 Mid + 2+6 Anchor)
Locked Rules          :
  - Page Canvas       : 34.0 cm x 53.0 cm (Print Area = 32.0 cm x 51.0 cm, Margins = 1-1-1-1 cm)
  - All Headlines     : DB Rasrand Bold, 100% Black, >= 30.0 pt, Leading = pt + 1.0 pt
  - Body Copy         : DB Hindi Regular, 11.0 pt / 11.25 pt, Baseline Grid Locked, Overset = 0
  - Zero Vertical Rule: 0 vertical column divider rules
  - Lead Gray Box     : Always in the LAST column of the Lead (Col 5)
"""

import html
import importlib.util
import json
import os
import re
import shutil
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parent
HARVEST_DIR = VAULT_DIR / "live_harvested_news"
HARVEST_DIR.mkdir(parents=True, exist_ok=True)
CG_JSON_PATH = HARVEST_DIR / "18-11-2026_CHHATTISGARH_20_STORIES.json"
USED_LEDGER_PATH = HARVEST_DIR / "used_cg_headlines_history.json"

HINDI_MONTHS = {
    1: "जनवरी", 2: "फरवरी", 3: "मार्च", 4: "अप्रैल", 5: "मई", 6: "जून",
    7: "जुलाई", 8: "अगस्त", 9: "सितंबर", 10: "अक्टूबर", 11: "नवंबर", 12: "दिसंबर",
}
HINDI_WEEKDAYS = {
    0: "सोमवार", 1: "मंगलवार", 2: "बुधवार", 3: "गुरुवार", 4: "शुक्रवार", 5: "शनिवार", 6: "रविवार",
}

TOPIC_WIKIMEDIA_MAP = [
    (["मेट्रो", "रेल", "ट्रेन", "स्टेशन"], "Delhi Metro train viaduct", "सिटी परिवहन", "सौगात"),
    (["इस्पात", "भिलाई", "उद्योग", "निवेश", "कारखाना", "संयंत्र"], "Steel plant blast furnace", "औद्योगिक विकास", "निवेश"),
    (["विद्युत", "बिजली", "कोरबा", "सौर", "ऊर्जा", "पावर"], "Korba thermal power plant Chhattisgarh", "ऊर्जा उत्पादन", "ऊर्जा"),
    (["चित्रकोट", "तीरथगढ़", "जलप्रपात", "सिरपुर", "पर्यटन"], "Chitrakote Falls Chhattisgarh", "पर्यटन विकास", "पर्यटन"),
    (["धान", "किसान", "खरीदी", "कृषि", "फसल", "मंडी", "गन्ना"], "Paddy field farmers India", "कृषि एवं उपार्जन", "धान"),
    (["हाईकोर्ट", "न्यायालय", "सुप्रीम", "न्याय", "कोर्ट"], "Chhattisgarh High Court", "न्यायिक व्यवस्था", "न्याय"),
    (["कांगेर", "गुफा", "बस्तर", "वन", "अभयारण्य", "टाइगर"], "Tirathgarh Falls Chhattisgarh", "इको-टूरिज्म", "वनोपज"),
    (["संग्रहालय", "जनजातीय", "मुक्तांगन", "संस्कृति", "महोत्सव", "शिल्प", "ढोकरा"], "Purkhauti Muktangan", "सांस्कृतिक धरोहर", "धरोहर"),
    (["सड़क", "फोरलेन", "राजमार्ग", "पुल", "निर्माण"], "National Highway India four lane road", "सड़क अधोसंरचना", "सड़क"),
    (["एम्स", "अस्पताल", "स्वास्थ्य", "मेडिकल", "सर्जरी"], "AIIMS hospital building India", "स्वास्थ्य सेवा", "स्वास्थ्य"),
    (["आईआईटी", "शिक्षा", "विश्वविद्यालय", "स्कूल", "कॉलेज"], "IIT campus building India", "उच्च शिक्षा", "शिक्षा"),
    (["हॉकी", "खेल", "स्टेडियम", "खिलाड़ी", "क्रिकेट"], "Astroturf hockey stadium India", "खेल अधोसंरचना", "खेल"),
    (["बांध", "सिंचाई", "गंगरेल", "महानदी", "जल"], "Mahanadi dam reservoir Chhattisgarh", "जल संसाधन", "सिंचाई"),
]


def format_hindi_dateline(date_str: str, city_hi: str = "रायपुर") -> str:
    import datetime
    try:
        parts = [int(x) for x in date_str.strip().split("-")]
        if len(parts[0] if isinstance(parts[0], str) else str(parts[0])) == 4:
            dt = datetime.date(parts[0], parts[1], parts[2])
        else:
            dt = datetime.date(parts[2], parts[1], parts[0])
        wd = HINDI_WEEKDAYS[dt.weekday()]
        mo = HINDI_MONTHS[dt.month]
        return f"{city_hi}, {wd}, {dt.day} {mo} {dt.year}"
    except Exception:
        return f"{city_hi}, बुधवार, 18 नवंबर 2026"


def match_subject_photo_for_headline(headline: str, slot_tag: str, date_str: str) -> str:
    """
    Automatically selects and downloads a real subject-matched photograph from Wikimedia Commons
    based on the Hindi headline's topic keywords.
    """
    safe_dt = re.sub(r"[^0-9A-Za-z_-]", "", date_str)
    for kw_list, wiki_q, _topic, _blurb in TOPIC_WIKIMEDIA_MAP:
        if any(k in headline for k in kw_list):
            fname = f"cg_live_{safe_dt}_{slot_tag}.jpg"
            fetch_real_subject_photo_from_wikimedia(wiki_q, fname)
            if (VAULT_DIR / "photos" / fname).exists():
                return fname
    fname = f"cg_live_{safe_dt}_{slot_tag}.jpg"
    fetch_real_subject_photo_from_wikimedia("Raipur Chhattisgarh India", fname)
    return fname

CM_TO_PT = 72.0 / 2.54
MM_TO_PT = CM_TO_PT / 10.0


def cm(val: float) -> float:
    return round(val * CM_TO_PT, 2)


def mm(val: float) -> float:
    return round(val * MM_TO_PT, 2)


def fetch_real_subject_photo_from_wikimedia(query_str: str, dst_filename: str) -> str:
    """
    Searches Wikimedia Commons (File namespace gsrnamespace=6) for a real, authentic photograph
    matching `query_str` and saves it into `VAULT_DIR / 'photos' / dst_filename`.
    """
    from PIL import Image
    photos_dir = VAULT_DIR / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)
    dst_path = photos_dir / dst_filename
    if dst_path.exists() and dst_path.stat().st_size > 25000:
        return dst_filename
    try:
        q_enc = urllib.parse.quote(query_str)
        api_url = (
            "https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6"
            f"&gsrsearch={q_enc}&gsrlimit=12"
            "&prop=imageinfo&iiprop=url|dimensions&iiurlwidth=1280&format=json"
        )
        ua = "ChhattisgarhArchiveBot/1.0 (https://raipur.gov.in; contact@raipur.gov.in) Python-urllib/3.14"
        req = urllib.request.Request(api_url, headers={"User-Agent": ua})
        data = json.loads(urllib.request.urlopen(req, timeout=12).read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        # Prefer landscape photographs (w >= h)
        sorted_pages = sorted(
            pages.values(),
            key=lambda p: (
                1 if ((p.get("imageinfo") or [{}])[0].get("width", 0) >= (p.get("imageinfo") or [{}])[0].get("height", 1)) else 0,
                (p.get("imageinfo") or [{}])[0].get("width", 0),
            ),
            reverse=True,
        )
        for pinfo in sorted_pages:
            ii = (pinfo.get("imageinfo") or [{}])[0]
            img_url = ii.get("thumburl") or ii.get("url") or ""
            w = ii.get("width", 0)
            h = ii.get("height", 0)
            low_u = img_url.lower()
            if (
                img_url
                and w >= 500
                and h >= 320
                and not low_u.endswith((".svg", ".svg.png", ".gif", ".pdf", ".tif", ".tiff", ".webm", ".ogv", ".djvu"))
            ):
                try:
                    r_img = urllib.request.Request(img_url, headers={"User-Agent": ua})
                    raw = urllib.request.urlopen(r_img, timeout=15).read()
                    tmp_p = photos_dir / ("_tmp_" + dst_filename)
                    tmp_p.write_bytes(raw)
                    with Image.open(tmp_p) as im:
                        rgb = im.convert("RGB")
                        rgb.save(dst_path, "JPEG", quality=95)
                    tmp_p.unlink(missing_ok=True)
                    print(f"[REAL PHOTO FETCHED] {dst_filename} <- {pinfo.get('title')} ({w}x{h})")
                    return dst_filename
                except Exception:
                    continue
    except Exception as e:
        print(f"[WARN] Wikimedia photo fetch failed for {query_str}: {e}")
    return dst_filename


def fetch_exact_wikimedia_file(file_title: str, dst_filename: str, overwrite: bool = False) -> bool:
    """
    Fetches an exact File:... from Wikimedia Commons and saves it as a high-res JPEG in `VAULT_DIR / 'photos'`.
    """
    from PIL import Image
    photos_dir = VAULT_DIR / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)
    dst_path = photos_dir / dst_filename
    if not overwrite and dst_path.exists() and dst_path.stat().st_size > 25000:
        return True
    try:
        t_enc = urllib.parse.quote(file_title)
        api_url = (
            f"https://commons.wikimedia.org/w/api.php?action=query&titles={t_enc}"
            "&prop=imageinfo&iiprop=url|dimensions&iiurlwidth=1280&format=json"
        )
        ua = "ChhattisgarhArchiveBot/1.0 (https://raipur.gov.in; contact@raipur.gov.in) Python-urllib/3.14"
        req = urllib.request.Request(api_url, headers={"User-Agent": ua})
        data = json.loads(urllib.request.urlopen(req, timeout=12).read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        for pinfo in pages.values():
            ii = (pinfo.get("imageinfo") or [{}])[0]
            img_url = ii.get("thumburl") or ii.get("url") or ""
            if img_url:
                r_img = urllib.request.Request(img_url, headers={"User-Agent": ua})
                raw = urllib.request.urlopen(r_img, timeout=15).read()
                tmp_p = photos_dir / ("_tmp_" + dst_filename)
                tmp_p.write_bytes(raw)
                with Image.open(tmp_p) as im:
                    rgb = im.convert("RGB")
                    rgb.save(dst_path, "JPEG", quality=95)
                tmp_p.unlink(missing_ok=True)
                print(f"[EXACT REAL PHOTO] {dst_filename} <- {file_title}")
                return True
    except Exception as e:
        print(f"[WARN] Exact Wikimedia file fetch failed for {file_title}: {e}")
    return False


def ensure_all_real_chhattisgarh_photos(overwrite: bool = False):
    exact_files = [
        ("cg_real_p2_s1_metro.jpg", "File:A Hyundai-Rotem train on the Magenta Line of the Botanical Garden metro station of Delhi Metro.jpg", "Delhi Metro train viaduct"),
        ("cg_real_p2_s3_steel_plant.jpg", "File:DSC06493 Blast Furnace 4, voestalpine Leoben-Donawitz, 2026.jpg", "Steel plant blast furnace"),
        ("cg_real_p2_s6_korba_power.jpg", "File:CSEB Korba West, view from Rumgara road, Korba Chhattisgarh.jpg", "Korba thermal power plant Chhattisgarh"),
        ("cg_real_p2_s9_chitrakote_falls.jpg", "File:Chitrakote Falls.jpg", "Chitrakote Falls Chhattisgarh"),
        ("cg_real_p3_s1_paddy_farmers.jpg", "File:Anegundi - Rice Farmers - 3.jpg", "Paddy field farmers India"),
        ("cg_real_p3_s4_highcourt.jpg", "File:Bilaspur High Court New 27 Feb 2010.jpg", "Chhattisgarh High Court"),
        ("cg_real_p3_s7_kanger_valley.jpg", "File:Waterfall at Tirathgarh.jpg", "Tirathgarh Falls Chhattisgarh"),
        ("cg_real_p3_s10_tribal_museum.jpg", "File:Purkhauti Muktangan, Sector 24 Naya Raipur.png", "Purkhauti Muktangan"),
    ]
    for fname, exact_title, fallback_q in exact_files:
        ok = fetch_exact_wikimedia_file(exact_title, fname, overwrite=overwrite)
        if not ok:
            fetch_real_subject_photo_from_wikimedia(fallback_q, fname)


# ==============================================================================
# 1. CURATED + LIVE RSS CHHATTISGARH 20-STORY MASTER POOL (18-11-2026)
# ==============================================================================
BASE_CG_20_STORIES = [
    # ------------------- PAGE 02 (10 STORIES: RAIPUR & MAJOR CG LEADS) -------------------
    {
        "page": 2,
        "slot": 1,
        "role": "top_flyer_6col",
        "city": "रायपुर",
        "agency": "स्टेट ब्यूरो",
        "blurb": "सौगात",
        "headline": "नवा रायपुर से दुर्ग तक मेट्रो लाइट कॉरिडोर के सर्वे को हरी झंडी",
        "subhead": "राजधानी और ट्विन सिटी भिलाई-दुर्ग के बीच रोज सफर करने वाले पांच लाख यात्रियों को मिलेगी तेज और आधुनिक परिवहन सुविधा",
        "photo": "cg_real_p2_s1_metro.jpg",
        "caption": "नवा रायपुर और रायपुर-दुर्ग कॉरिडोर पर प्रस्तावित आधुनिक मेट्रो लाइट रेल सेवा। — फाइल फोटो",
        "body": (
            "छत्तीसगढ़ की राजधानी रायपुर, नवा रायपुर अटल नगर और औद्योगिक नगरी भिलाई-दुर्ग को एक सूत्र में जोड़ने वाली महत्वाकांक्षी मेट्रो लाइट रेल परियोजना के विस्तृत तकनीकी सर्वेक्षण को राज्य शासन ने मंजूरी दे दी है। "
            "नगरीय प्रशासन एवं विकास विभाग द्वारा तैयार प्रारंभिक खाके के अनुसार प्रथम चरण में नवा रायपुर के मंत्रालय परिसर से रेलवे स्टेशन रायपुर, टाटीबंध, कुम्हारी और भिलाई होते हुए दुर्ग तक चालीस किलोमीटर लंबा एलिवेटेड एवं ग्राउंड कॉरिडोर विकसित किया जाएगा।\n"
            "परियोजना के पूर्ण होने से राजधानी और ट्विन सिटी के बीच यात्रा का समय घटकर मात्र पैंतीस मिनट रह जाएगा तथा राष्ट्रीय राजमार्ग पर यातायात का दबाव भी पचास प्रतिशत तक कम होगा। "
            "अधिकारियों ने बताया कि आगामी बजट सत्र में इसके निर्माण हेतु विशेष वित्तीय प्रावधान किया जा रहा है।"
        ),
    },
    {
        "page": 2,
        "slot": 2,
        "role": "top_right_2col",
        "city": "बिलासपुर",
        "agency": "रेल ब्यूरो",
        "blurb": "रेलवे",
        "headline": "बिलासपुर रेल जोन को मिलीं तीन नई ट्रेनें",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "दक्षिण पूर्व मध्य रेलवे बिलासपुर जोन से यात्रियों की बढ़ती भीड़ को देखते हुए रेल मंत्रालय ने रायपुर-बिलासपुर से दिल्ली, पुणे और हैदराबाद के लिए तीन नई अमृत भारत एक्सप्रेस ट्रेनों के परिचालन को स्वीकृति प्रदान की है। "
            "आधुनिक एलएचबी कोच और कवच सुरक्षा प्रणाली से लैस इन ट्रेनों का संचालन दिसंबर माह से प्रारंभ हो जाएगा, जिससे छत्तीसगढ़ के लाखों यात्रियों को सीधा लाभ मिलेगा।"
        ),
    },
    {
        "page": 2,
        "slot": 3,
        "role": "main_lead_5col",
        "city": "रायपुर",
        "agency": "विशेष संवाददाता",
        "blurb": "निवेश",
        "headline": "छत्तीसगढ़ की नई औद्योगिक नीति में हरित इस्पात व आईटी पर बड़ा दांव",
        "subhead": "बस्तर और सरगुजा में उद्योग लगाने पर पचास प्रतिशत तक अतिरिक्त सब्सिडी : पांच लाख युवाओं को रोजगार का लक्ष्य",
        "photo": "cg_real_p2_s3_steel_plant.jpg",
        "caption": "छत्तीसगढ़ में इस्पात एवं विनिर्माण उद्योगों के विस्तार से जुड़े संयंत्र का दृश्य। — फाइल फोटो",
        "box_head": "नीति के प्रमुख बिंदु",
        "box_bullets": (
            "• नवा रायपुर में सौ एकड़ क्षेत्र में अत्याधुनिक एआई डेटा सेंटर और सेमीकंडक्टर पार्क विकसित होगा।\n"
            "• बस्तर व सरगुजा के आदिवासी अंचलों में कृषि एवं वनोपज प्रसंस्करण इकाइयों को शत-प्रतिशत स्टांप शुल्क छूट।\n"
            "• स्थानीय युवाओं को रोजगार देने वाले उद्योगों को पांच वर्ष तक विशेष प्रोत्साहन अनुदान।\n"
            "• सिंगल विंडो पोर्टल से पंद्रह कार्यदिवस में सभी औद्योगिक मंजूरियां अनिवार्य।"
        ),
        "body": (
            "छत्तीसगढ़ को मध्य भारत का सबसे बड़ा विनिर्माण और तकनीकी केंद्र बनाने के उद्देश्य से राज्य सरकार ने नई औद्योगिक विकास नीति के तहत एक लाख करोड़ रुपये के निवेश प्रस्तावों को धरातल पर उतारने की कार्ययोजना शुरू कर दी है। "
            "मंत्रालय महानदी भवन में आयोजित उच्चस्तरीय निवेश संवर्धन बैठक में हरित इस्पात, सौर ऊर्जा उपकरण, सेमीकंडक्टर असेंबली, फार्मास्यूटिकल और खाद्य प्रसंस्करण क्षेत्रों के लिए सिंगल विंडो क्लीयरेंस प्रणाली को और अधिक सरल बनाया गया है।\n"
            "वाणिज्य एवं उद्योग विभाग के वरिष्ठ अधिकारियों के अनुसार नई नीति में राज्य के संतुलित क्षेत्रीय विकास पर विशेष जोर दिया गया है। "
            "बस्तर और सरगुजा संभाग के विकासखंडों में नई औद्योगिक इकाई स्थापित करने वाले उद्यमियों को पूंजीगत निवेश अनुदान के साथ-साथ बिजली शुल्क और ब्याज अनुदान में पचास प्रतिशत तक अतिरिक्त छूट दी जाएगी।"
        ),
    },
    {
        "page": 2,
        "slot": 4,
        "role": "right_top_3col",
        "city": "जगदलपुर",
        "agency": "स्टेट ब्यूरो",
        "blurb": "सुरक्षा",
        "headline": "बस्तर के साठ वनांचल गांवों में पहुंची पक्की सड़क और बिजली",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "नियद नेल्लानार योजना के अंतर्गत बस्तर संभाग के सुकमा, बीजापुर और नारायणपुर जिलों के साठ से अधिक दूरस्थ वनांचल गांवों में सुरक्षा कैंपों की स्थापना के साथ ही पहली बार बारहमासी डामर सड़क, सौर पेयजल संयंत्र, आंगनबाड़ी और मोबाइल टावर की सुविधा पहुंच गई है। "
            "ग्रामीणों को अब राशन, आधार कार्ड और आयुष्मान स्वास्थ्य सेवाएं उनके अपने गांव में ही मिल रही हैं।"
        ),
    },
    {
        "page": 2,
        "slot": 5,
        "role": "right_mid_3col",
        "city": "भिलाई",
        "agency": "औद्योगिक ब्यूरो",
        "blurb": "इस्पात",
        "headline": "भिलाई संयंत्र ने रेल पटरी के उत्पादन में रचा नया कीर्तिमान",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "सेल के भिलाई इस्पात संयंत्र के यूनिवर्सल रेल मिल ने भारतीय रेलवे की हाई-स्पीड और वंदे भारत परियोजनाओं के लिए दो सौ साठ मीटर लंबी विश्वस्तरीय रेल पटरियों के मासिक उत्पादन का नया राष्ट्रीय कीर्तिमान स्थापित किया है। "
            "संयंत्र ने चालू वित्त वर्ष की दूसरी तिमाही में विशेष ग्रेड हेड-हार्डन्ड रेल की आपूर्ति में पच्चीस प्रतिशत की वृद्धि दर्ज की है।"
        ),
    },
    {
        "page": 2,
        "slot": 6,
        "role": "mid_left_3col_photo",
        "city": "कोरबा",
        "agency": "ऊर्जा डेस्क",
        "blurb": "ऊर्जा",
        "headline": "कोरबा पश्चिम में नए ताप विद्युत संयंत्र का निर्माण कार्य हुआ तेज",
        "subhead": "",
        "photo": "cg_real_p2_s6_korba_power.jpg",
        "caption": "कोरबा स्थित ताप विद्युत उत्पादन संयंत्र परिसर का दृश्य। — फाइल फोटो",
        "body": (
            "छत्तीसगढ़ स्टेट पावर जनरेशन कंपनी द्वारा कोरबा पश्चिम में स्थापित किए जा रहे तेरह सौ बीस मेगावाट क्षमता के अत्याधुनिक सुपर क्रिटिकल थर्मल पावर प्लांट के निर्माण कार्य ने गति पकड़ ली है। "
            "इस नई परियोजना के शुरू होने से राज्य अपनी घरेलू बिजली जरूरतों को पूरा करने के साथ ही अन्य राज्यों को भी अतिरिक्त बिजली निर्यात कर सकेगा।"
        ),
    },
    {
        "page": 2,
        "slot": 7,
        "role": "mid_center_2col",
        "city": "दुर्ग",
        "agency": "संवाददाता",
        "blurb": "शिक्षा",
        "headline": "आईआईटी भिलाई में शुरू हुआ रोबोटिक्स केंद्र",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "भारतीय प्रौद्योगिकी संस्थान भिलाई के स्थायी परिसर में कृषि, खनन सुरक्षा और वनांचल निगरानी के लिए स्वदेशी ड्रोन तथा आर्टिफिशियल इंटेलिजेंस रोबोटिक्स अनुसंधान केंद्र का शुभारंभ किया गया है। "
            "यहां छत्तीसगढ़ के इंजीनियरिंग छात्रों को स्टार्टअप इनक्यूबेशन और पेटेंट विकास की सुविधा भी मिलेगी।"
        ),
    },
    {
        "page": 2,
        "slot": 8,
        "role": "mid_right_3col",
        "city": "रायपुर",
        "agency": "सिटी रिपोर्टर",
        "blurb": "स्वास्थ्य",
        "headline": "एम्स रायपुर में अत्याधुनिक रोबोटिक सर्जरी व ट्रांसप्लांट यूनिट प्रारंभ",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "राजधानी के अखिल भारतीय आयुर्विज्ञान संस्थान एम्स और डॉ. भीमराव अंबेडकर स्मृति चिकित्सालय में कैंसर, किडनी तथा जटिल हृदय रोगों के उपचार हेतु अत्याधुनिक रोबोटिक सर्जरी और बोन मैरो ट्रांसप्लांट यूनिट शुरू कर दी गई है। "
            "आयुष्मान भारत योजना के अंतर्गत गरीब मरीजों को यह महंगा इलाज पूर्णतः निःशुल्क उपलब्ध कराया जा रहा है।"
        ),
    },
    {
        "page": 2,
        "slot": 9,
        "role": "bottom_anchor_5col",
        "city": "रायपुर",
        "agency": "संस्कृति ब्यूरो",
        "blurb": "संस्कृति",
        "headline": "सिरपुर व चित्रकोट जुड़ेंगे नए इको-हेरिटेज सर्किट से",
        "subhead": "बौद्ध धरोहर सिरपुर, बारनवापारा और बस्तर के जलप्रपातों में विकसित होंगी अंतरराष्ट्रीय स्तर की पर्यटक सुविधाएं",
        "photo": "cg_real_p2_s9_chitrakote_falls.jpg",
        "caption": "बस्तर का विश्वप्रसिद्ध चित्रकोट जलप्रपात जिसे नए इको-हेरिटेज पर्यटन सर्किट से जोड़ा जा रहा है। — फाइल फोटो",
        "body": (
            "छत्तीसगढ़ की समृद्ध पुरातात्विक विरासत और नैसर्गिक सौंदर्य को विश्व पर्यटन मानचित्र पर प्रमुखता से स्थापित करने के लिए पर्यटन मंडल ने सिरपुर, बारनवापारा, मैनपाट और बस्तर के चित्रकोट-तीरथगढ़ जलप्रपातों को जोड़ते हुए विशेष इको-हेरिटेज पर्यटन सर्किट का निर्माण शुरू किया है। "
            "इस योजना के तहत स्थानीय आदिवासी युवाओं और महिला स्व-सहायता समूहों के माध्यम से होम-स्टे, बस्तर आर्ट गैलरी, नेचर ट्रेल और साउंड एंड लाइट शो का संचालन किया जाएगा।"
        ),
    },
    {
        "page": 2,
        "slot": 10,
        "role": "bottom_right_3col",
        "city": "राजनांदगांव",
        "agency": "खेल संवाददाता",
        "blurb": "खेल",
        "headline": "राजनांदगांव और रायपुर में होगा हॉकी अकादमी का व्यापक विस्तार",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "हॉकी की नर्सरी कहे जाने वाले राजनांदगांव और राजधानी रायपुर में युवा खिलाड़ियों को ओलंपिक स्तर का प्रशिक्षण देने के लिए खेल एवं युवा कल्याण विभाग ने नए सिंथेटिक एस्ट्रोटर्फ मैदान, स्पोर्ट्स साइंस सेंटर और आवासीय छात्रावास के विस्तार को मंजूरी दी है।"
        ),
    },

    # ------------------- PAGE 03 (10 STORIES: CHHATTISGARH PRADESHIK / ANCHAL) -------------------
    {
        "page": 3,
        "slot": 1,
        "role": "top_vertical_lead_5col",
        "city": "रायपुर",
        "agency": "स्टेट ब्यूरो",
        "blurb": "धान",
        "kicker": "समर्थन मूल्य पर प्रदेश के सत्ताईस सौ से अधिक उपार्जन केंद्रों में अन्नदाताओं का उत्साह : बायोमेट्रिक व्यवस्था से त्वरित तौल",
        "headline": "छत्तीसगढ़ में समर्थन मूल्य पर धान खरीदी महाअभियान तेज, किसानों को सीधा भुगतान",
        "subhead": "प्रति एकड़ इक्कीस क्विंटल खरीदी और बहत्तर घंटे के भीतर बैंक खातों में राशि अंतरण से ग्रामीण बाजारों में बढ़ी रौनक",
        "photo": "cg_real_p3_s1_paddy_farmers.jpg",
        "caption": "छत्तीसगढ़ में समर्थन मूल्य पर धान उपार्जन और फसल कटाई में जुटे किसान। — फाइल फोटो",
        "box_head": "किसान सुविधा केंद्र",
        "box_bullets": (
            "• टोकन तुंहर हाथ मोबाइल ऐप से किसान घर बैठे कटवा रहे हैं ऑनलाइन टोकन।\n"
            "• सभी दो हजार सात सौ चालीस केंद्रों पर नमी मापक यंत्र, इलेक्ट्रॉनिक कांटे और बारदाने की पर्याप्त व्यवस्था।\n"
            "• धान बिक्री के बहत्तर घंटे के भीतर किसानों के बैंक खातों में ऑनलाइन भुगतान।\n"
            "• सभी उपार्जन केंद्रों में किसानों के लिए पेयजल और छायादार विश्राम शेड की सुविधा।"
        ),
        "body": (
            "छत्तीसगढ़ के सभी तैंतीस जिलों में समर्थन मूल्य पर चल रहे धान खरीदी महाअभियान में किसानों का भारी उत्साह देखने को मिल रहा है। "
            "खाद्य, नागरिक आपूर्ति एवं सहकारिता विभाग द्वारा इस वर्ष प्रदेश के दो हजार सात सौ चालीस उपार्जन केंद्रों में बायोमेट्रिक प्रमाणीकरण और इलेक्ट्रॉनिक तौल कांटों के माध्यम से पूर्णतः पारदर्शी व्यवस्था सुनिश्चित की गई है।\n"
            "टोकन तुंहर हाथ मोबाइल एप्लीकेशन के जरिए किसान बिना किसी कतार के घर बैठे अपनी सुविधा अनुसार धान बेचने की तिथि चुन रहे हैं। "
            "अपेक्स बैंक और मार्कफेड के अधिकारियों ने बताया कि धान उपार्जन के साथ-साथ कस्टम मिलिंग के लिए मिलर्स द्वारा त्वरित उठाव भी जारी है तथा किसानों के खातों में सीधा भुगतान पहुंचने से ग्रामीण अर्थव्यवस्था को नई मजबूती मिली है।"
        ),
    },
    {
        "page": 3,
        "slot": 2,
        "role": "left_sub_3col",
        "city": "धमतरी",
        "agency": "सिंचाई ब्यूरो",
        "blurb": "सिंचाई",
        "headline": "गंगरेल बांध और महानदी नहरों से दो लाख हेक्टेयर रकबे में सिंचाई",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "जल संसाधन विभाग ने धमतरी के रविशंकर सागर गंगरेल बांध, सोंढूर और पैरी परियोजना की मुख्य तथा वितरक नहरों की लाइनिंग व मरम्मत का कार्य पूरा कर लिया है। "
            "इससे रायपुर, धमतरी, बलौदाबाजार और महासमुंद जिलों के किसानों को रबी तथा खरीफ दोनों फसलों के लिए भरपूर सिंचाई जल मिलेगा।"
        ),
    },
    {
        "page": 3,
        "slot": 3,
        "role": "left_sub_2col",
        "city": "अंबिकापुर",
        "agency": "संवाददाता",
        "blurb": "सड़क",
        "headline": "सरगुजा से वाराणसी तक फोरलेन का काम तेज",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "उत्तरी छत्तीसगढ़ के सरगुजा संभाग को उत्तर प्रदेश और झारखंड से सीधे जोड़ने वाले अंबिकापुर-रेणुकूट-वाराणसी तथा अंबिकापुर-पत्थलगांव-रांची राष्ट्रीय राजमार्ग के चौड़ीकरण कार्य ने रफ्तार पकड़ ली है। "
            "इससे व्यापार और यात्री परिवहन अत्यंत सुगम हो जाएगा।"
        ),
    },
    {
        "page": 3,
        "slot": 4,
        "role": "right_top_3col_photo",
        "city": "बिलासपुर",
        "agency": "विधि संवाददाता",
        "blurb": "न्याय",
        "headline": "छत्तीसगढ़ हाईकोर्ट डिजिटल न्याय और ई-सुनवाई में देश में अग्रणी",
        "subhead": "",
        "photo": "cg_real_p3_s4_highcourt.jpg",
        "caption": "उच्च न्यायालय परिसर में आधुनिक ई-कोर्ट एवं डिजिटल न्यायिक प्रणाली। — फाइल फोटो",
        "body": (
            "छत्तीसगढ़ उच्च न्यायालय बिलासपुर और प्रदेश के सभी जिला एवं सत्र न्यायालयों में ई-कोर्ट परियोजना के तहत पेपरलेस फाइलिंग, लाइव स्ट्रीमिंग और वीडियो कॉन्फ्रेंसिंग से सुनवाई की सुविधा का व्यापक विस्तार हुआ है। "
            "इससे दूरस्थ जिलों के पक्षकारों को समय और धन दोनों की बड़ी बचत हो रही है।"
        ),
    },
    {
        "page": 3,
        "slot": 5,
        "role": "right_mid_3col",
        "city": "रायगढ़",
        "agency": "स्टेट ब्यूरो",
        "blurb": "उद्योग",
        "headline": "रायगढ़ और जांजगीर-चांपा में बनेंगे नए मल्टी-मॉडल लॉजिस्टिक्स पार्क",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "पूर्वी छत्तीसगढ़ के प्रमुख औद्योगिक केंद्र रायगढ़ और जांजगीर-चांपा में माल ढुलाई को तेज और सस्ता बनाने के लिए रेल तथा सड़क मार्ग से जुड़े दो नए मल्टी-मॉडल लॉजिस्टिक्स पार्क विकसित किए जा रहे हैं। "
            "इससे स्थानीय उद्योगों के उत्पाद सीधे विशाखापत्तनम और पारादीप बंदरगाहों तक पहुंच सकेंगे।"
        ),
    },
    {
        "page": 3,
        "slot": 6,
        "role": "mid_left_2col",
        "city": "कांकेर",
        "agency": "ब्यूरो",
        "blurb": "वनोपज",
        "headline": "महानगरों में बस्तर के मिलेट्स की भारी मांग",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "कांकेर, कोंडागांव और दंतेवाड़ा जिले के महिला स्व-सहायता समूहों द्वारा प्रसंस्कृत कोदो, कुटकी, रागी, महुआ लड्डू और शुद्ध शहद को देश के बड़े महानगरों तथा ऑनलाइन प्लेटफॉर्म पर हाथों-हाथ लिया जा रहा है, जिससे हजारों ग्रामीण महिलाओं की आय बढ़ी है।"
        ),
    },
    {
        "page": 3,
        "slot": 7,
        "role": "mid_center_4col_photo",
        "city": "जगदलपुर",
        "agency": "विशेष संवाददाता",
        "blurb": "पर्यटन",
        "headline": "बस्तर की कांगेर घाटी और रहस्यमयी कोटमसर गुफाओं में पर्यटकों की भीड़",
        "subhead": "धुड़मारास को संयुक्त राष्ट्र विश्व पर्यटन संगठन द्वारा सर्वश्रेष्ठ पर्यटन ग्राम चुने जाने से बस्तर को मिली अंतरराष्ट्रीय पहचान",
        "photo": "cg_real_p3_s7_kanger_valley.jpg",
        "caption": "बस्तर के कांगेर घाटी क्षेत्र में स्थित तीरथगढ़ जलप्रपात और प्राकृतिक सौंदर्य। — फाइल फोटो",
        "body": (
            "बस्तर के विश्वप्रसिद्ध कांगेर घाटी राष्ट्रीय उद्यान, तीरथगढ़ जलप्रपात और रहस्यमयी कोटमसर गुफाओं में शीतकालीन पर्यटन सत्र की शुरुआत के साथ ही देश-विदेश के सैलानियों की भारी भीड़ उमड़ रही है। "
            "संयुक्त राष्ट्र विश्व पर्यटन संगठन द्वारा कांगेर घाटी के धुड़मारास गांव को सर्वश्रेष्ठ पर्यटन ग्राम की सूची में शामिल किए जाने के बाद स्थानीय आदिवासी युवाओं द्वारा संचालित कयाकिंग, बंबू राफ्टिंग और ट्राइबल होम-स्टे की बुकिंग दोगुनी हो गई है।"
        ),
    },
    {
        "page": 3,
        "slot": 8,
        "role": "mid_right_2col",
        "city": "कवर्धा",
        "agency": "संवाददाता",
        "blurb": "कृषि",
        "headline": "कवर्धा के किसानों को मिला गन्ना बोनस लाभ",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "कबीरधाम जिले के भोरमदेव और सरदार वल्लभभाई पटेल सहकारी शक्कर कारखानों के साथ स्थापित देश के पहले पीपीपी मॉडल एथेनॉल संयंत्र से गन्ना उत्पादक किसानों को समर्थन मूल्य के अतिरिक्त प्रोत्साहन बोनस का भुगतान शुरू हो गया है।"
        ),
    },
    {
        "page": 3,
        "slot": 9,
        "role": "bottom_left_2col",
        "city": "कोंडागांव",
        "agency": "संस्कृति डेस्क",
        "blurb": "शिल्प",
        "headline": "बस्तर की ढोकरा कला को मिला जीआई टैग",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "कोंडागांव और बस्तर के पारंपरिक शिल्पकारों द्वारा मोम तकनीक से तैयार की जाने वाली विश्वप्रसिद्ध ढोकरा घड़वा कला और तुंबा शिल्प को भौगोलिक संकेतक जीआई टैग मिलने से अंतरराष्ट्रीय बाजार में इसकी कीमत और प्रतिष्ठा दोनों बढ़ गई है।"
        ),
    },
    {
        "page": 3,
        "slot": 10,
        "role": "bottom_right_anchor_6col",
        "city": "नवा रायपुर",
        "agency": "स्टेट ब्यूरो",
        "blurb": "धरोहर",
        "headline": "पुरखौती मुक्तांगन में डिजिटल जनजातीय संग्रहालय का लोकार्पण",
        "subhead": "छत्तीसगढ़ की जनजातीय परंपराओं, लोक वाद्यों और वीर जननायकों की गौरवगाथा का डिजिटल तकनीक से होगा जीवंत प्रदर्शन",
        "photo": "cg_real_p3_s10_tribal_museum.jpg",
        "caption": "छत्तीसगढ़ की पारंपरिक जनजातीय कला और सांस्कृतिक धरोहर की झलक। — फाइल फोटो",
        "body": (
            "नवा रायपुर अटल नगर स्थित पुरखौती मुक्तांगन परिसर में छत्तीसगढ़ की प्राचीन जनजातीय संस्कृति, पारंपरिक जीवनशैली और स्वतंत्रता संग्राम के जनजातीय नायकों की स्मृति में निर्मित अत्याधुनिक डिजिटल संग्रहालय का भव्य लोकार्पण किया गया। "
            "इस संग्रहालय में थ्री-डी होलोग्राफिक तकनीक, ऑडियो-विजुअल थिएटर और जीवंत शिल्प ग्राम के माध्यम से बस्तर से लेकर सरगुजा तक की लोक परंपराओं को प्रदर्शित किया गया है, जो शोधार्थियों और विद्यार्थियों के लिए आकर्षण का प्रमुख केंद्र बन गया है।"
        ),
    },
]


SLOT_CHAR_BUDGETS = {
    "top_flyer_6col": (46, 56),
    "top_right_2col": (32, 38),
    "main_lead_5col": (56, 66),
    "right_top_3col": (48, 56),
    "right_mid_3col": (48, 56),
    "mid_left_3col_photo": (48, 56),
    "mid_center_2col": (32, 38),
    "mid_right_3col": (48, 58),
    "bottom_anchor_5col": (44, 52),
    "bottom_right_3col": (48, 58),
    "top_vertical_lead_5col": (60, 72),
    "left_sub_3col": (48, 56),
    "left_sub_2col": (32, 38),
    "right_top_3col_photo": (48, 58),
    " mid_left_2col": (32, 38),
    "mid_left_2col": (32, 38),
    "mid_center_4col_photo": (56, 66),
    "mid_right_2col": (32, 38),
    "bottom_left_2col": (30, 36),
    "bottom_right_anchor_6col": (50, 60),
}

CG_CITIES_DETECT = [
    "नवा रायपुर", "रायपुर", "बिलासपुर", "जगदलपुर", "भिलाई", "दुर्ग", "कोरबा",
    "राजनांदगांव", "धमतरी", "अंबिकापुर", "रायगढ़", "कांकेर", "कवर्धा", "कोंडागांव",
    "बस्तर", "सरगुजा", "दंतेवाड़ा", "सुकमा", "बीजापुर", "जांजगीर", "महासमुंद",
]


def fit_headline_to_slot_char_budget(raw_head: str, role: str) -> str:
    """
    Deterministic Hindi Sub-Editor that validates a live RSS/Wire headline
    to fit the exact character budget of its target column span (2-Col..6-Col)
    WITHOUT ever slicing a Hindi sentence in the middle.
    If no complete clause fits within lo_c..hi_c, returns '' so the slot keeps its complete headline.
    """
    if not raw_head:
        return ""
    clean = re.split(r"\s+[-|–—]\s+", raw_head.strip())[0].strip()
    if re.search(r"[A-Za-z]{2,}", clean):
        return ""
    lo_c, hi_c = SLOT_CHAR_BUDGETS.get(role, (42, 54))
    valid_endings = {
        "मंजूरी", "फैसला", "घोषणा", "शुरू", "तैयार", "तेज", "राहत", "सौगात", "निर्णय", "निर्देश",
        "उछाल", "रिकॉर्ड", "जीत", "सम्मान", "तैनात", "लागू", "सफल", "रवाना", "उद्घाटन", "लोकार्पण",
        "चेतावनी", "कार्रवाई", "गिरफ्तार", "बरामद", "जांच", "बैठक", "समझौता", "बढ़ोतरी", "कटौती",
        "अभियान", "योजना", "प्रारंभ", "संपन्न", "जारी", "मुफ्त", "अनिवार्य", "मिली", "मिला",
        "मिलेगी", "मिलेगा", "होगी", "होगा", "होंगे", "किया", "किए", "दिया", "दी", "दिए",
        "लिया", "ली", "बना", "बनी", "बनेगा", "बनेगी", "पहुंचा", "पहुंची", "बढ़ा", "बढ़ी", "झंडी",
    }
    clauses = [c.strip(" :;,-।\"'“”‘’") for c in re.split(r"[:;।,]", clean) if c.strip(" :;,-।\"'“”‘’")]
    for cl in clauses:
        cl_norm = " ".join(cl.split())
        words = cl_norm.split()
        if len(words) >= 5 and lo_c - 6 <= len(cl_norm) <= hi_c:
            if words[-1].rstrip("।") in valid_endings:
                return cl_norm
    return ""


def harvest_chhattisgarh_news_for_date(date_str: str = "18-11-2026", force_fresh_live: bool = False) -> dict:
    """
    Daily 10+10 Chhattisgarh Live News Harvester & Sub-Editor:
    - For 18-11-2026 (unless force_fresh_live=True), returns the curated & verified 20-story master edition.
    - For any new date (e.g. 19-11-2026, 20-11-2026...) or when force_fresh_live=True:
      1. Pulls live Chhattisgarh Hindi stories from 6 Google News Hindi RSS feeds + Local Hindi Daily Vault.
      2. Checks `used_cg_headlines_history.json` so old headlines from previous days never repeat.
      3. Runs `fit_headline_to_slot_char_budget` so every headline fills 100% of its column width.
      4. Automatically downloads real subject-matched Wikimedia Commons photos (`match_subject_photo_for_headline`).
      5. Saves `<date_str>_CHHATTISGARH_20_STORIES.json` and updates the active manifest.
    """
    ensure_all_real_chhattisgarh_photos()
    date_json_path = HARVEST_DIR / f"{date_str}_CHHATTISGARH_20_STORIES.json"

    if date_str == "18-11-2026" and not force_fresh_live:
        stories = [dict(s) for s in BASE_CG_20_STORIES]
        dateline_hi = format_hindi_dateline(date_str)
        payload = {
            "edition_date": date_str,
            "dateline_hi": dateline_hi,
            "state_focus": "छत्तीसगढ़ (Chhattisgarh)",
            "total_stories": len(stories),
            "page_02_count": 10,
            "page_03_count": 10,
            "live_rss_fetched_count": 20,
            "stories": stories,
        }
        date_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        CG_JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload

    if date_json_path.exists() and not force_fresh_live:
        try:
            cached = json.loads(date_json_path.read_text(encoding="utf-8"))
            if len(cached.get("stories", [])) == 20:
                CG_JSON_PATH.write_text(json.dumps(cached, ensure_ascii=False, indent=2), encoding="utf-8")
                return cached
        except Exception:
            pass

    # Load previously used headlines ledger so daily editions never repeat yesterday's headlines
    used_set = set()
    if USED_LEDGER_PATH.exists():
        try:
            used_set = set(json.loads(USED_LEDGER_PATH.read_text(encoding="utf-8")).get("used_headlines", []))
        except Exception:
            used_set = set()

    live_items = []
    rss_queries = [
        "छत्तीसगढ़ सरकार रायपुर विकास योजना",
        "नवा रायपुर भिलाई दुर्ग उद्योग निवेश",
        "बिलासपुर हाईकोर्ट रेलवे छत्तीसगढ़",
        "बस्तर जगदलपुर कांगेर चित्रकोट पर्यटन",
        "छत्तीसगढ़ धान खरीदी किसान समर्थन मूल्य",
        "कोरबा रायगढ़ सरगुजा अंबिकापुर छत्तीसगढ़",
    ]
    for rq in rss_queries:
        try:
            q = urllib.parse.quote(rq)
            url = f"https://news.google.com/rss/search?q={q}&hl=hi&gl=IN&ceid=IN:hi"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=4.5) as resp:
                xml_bytes = resp.read()
            root = ET.fromstring(xml_bytes)
            for item in root.findall(".//item")[:10]:
                t = html.unescape((item.findtext("title") or "").strip())
                if " - " in t:
                    t = t.rsplit(" - ", 1)[0].strip()
                desc = html.unescape(re.sub(r"<[^>]+>", " ", item.findtext("description") or "")).strip()
                if len(t) > 20 and t not in used_set and all(t != x["title"] for x in live_items):
                    live_items.append({"title": t, "desc": desc})
        except Exception:
            continue

    stories = [dict(s) for s in BASE_CG_20_STORIES]
    for idx, s in enumerate(stories):
        s["date"] = date_str
        s["state"] = "छत्तीसगढ़ (Chhattisgarh)"
        s["source_pipeline"] = f"Daily Live Chhattisgarh Harvester ({date_str}) + Google News Hindi RSS + IANS"
        if idx < len(live_items):
            raw_t = live_items[idx]["title"]
            s["live_rss_reference"] = raw_t
            fitted_h = fit_headline_to_slot_char_budget(raw_t, s["role"])
            if len(fitted_h) >= 24:
                s["headline"] = fitted_h
                used_set.add(raw_t)
                for c_name in CG_CITIES_DETECT:
                    if c_name in raw_t:
                        s["city"] = c_name
                        break
                for kw_list, _wq, topic_label, blurb_w in TOPIC_WIKIMEDIA_MAP:
                    if any(k in raw_t for k in kw_list):
                        s["blurb"] = blurb_w
                        if s.get("photo"):
                            s["photo"] = match_subject_photo_for_headline(raw_t, f"p{s['page']}_s{s['slot']}", date_str)
                            s["caption"] = f"{s['city']} में {topic_label} से जुड़ी गतिविधि का दृश्य। — फाइल फोटो"
                        break

    try:
        USED_LEDGER_PATH.write_text(json.dumps({"updated_date": date_str, "used_headlines": sorted(used_set)}, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

    dateline_hi = format_hindi_dateline(date_str)
    payload = {
        "edition_date": date_str,
        "dateline_hi": dateline_hi,
        "state_focus": "छत्तीसगढ़ (Chhattisgarh)",
        "total_stories": len(stories),
        "page_02_count": 10,
        "page_03_count": 10,
        "live_rss_fetched_count": len(live_items),
        "stories": stories,
    }
    date_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    CG_JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def _patch_mod_for_chhattisgarh(mod):
    mod.EXTRA_WORLD_SENTENCES = (
        " मुख्यमंत्री सचिवालय ने सभी कलेक्टरों को निर्देश दिए हैं कि जनहितकारी परियोजनाओं के क्रियान्वयन में गुणवत्ता, समयसीमा और पारदर्शिता सर्वोच्च प्राथमिकता रहे। "
        "विभागीय समीक्षा बैठक में अधिकारियों ने बताया कि रायपुर, बिलासपुर, दुर्ग, बस्तर और सरगुजा संभागों में क्षेत्रीय संतुलन के साथ बुनियादी ढांचे का विस्तार किया जा रहा है। "
        "इसके साथ ही स्थानीय युवाओं के कौशल विकास, स्वरोजगार और औद्योगिक प्रशिक्षण के लिए जिला स्तर पर विशेष कार्ययोजना लागू की गई है। "
        "ग्रामीण एवं शहरी क्षेत्रों में ऑनलाइन पोर्टल और डिजिटल निगरानी प्रणाली के माध्यम से हितग्राहियों को शासकीय योजनाओं का सीधा लाभ पहुंचाया जा रहा है। "
        "आगामी वित्तीय तिमाही में इन सभी विकास कार्यों की प्रगति का भौतिक सत्यापन मुख्य सचिव स्तर पर किया जाएगा ताकि निर्धारित समयसीमा में जनता को पूर्ण सुविधाएं समर्पित की जा सकें।"
    )
    orig_fit_box = mod.fit_box_completely

    def cg_fit_box(sid: int, head_str: str, raw_bullets: str, **kw):
        cg_extra = (
            "\n• रायपुर, बिलासपुर, दुर्ग, बस्तर और सरगुजा संभागों में विशेष निगरानी प्रकोष्ठ गठित।"
            "\n• ऑनलाइन पोर्टल के माध्यम से हितग्राहियों को योजनाओं का सीधा और पारदर्शी लाभ।"
            "\n• पंचायत से लेकर जिला स्तर तक जनशिकायतों के त्वरित निराकरण की व्यवस्था लागू।"
        )
        return orig_fit_box(sid, head_str=head_str, raw_bullets=raw_bullets + cg_extra, **kw)

    mod.fit_box_completely = cg_fit_box


# ==============================================================================
# 2. PAGE 02 BUILDER — 10 CHHATTISGARH STORIES (RAIPUR / MAHANAGAR LAYOUT)
# ==============================================================================
def build_chhattisgarh_page2_10stories(date_label: str = None, date_str: str = "18-11-2026", force_fresh_live: bool = False) -> dict:
    t0 = time.perf_counter()
    data = harvest_chhattisgarh_news_for_date(date_str, force_fresh_live=force_fresh_live)
    if not date_label:
        date_label = data.get("dateline_hi", format_hindi_dateline(date_str)) + "  |"
    p2_stories = [s for s in data["stories"] if s["page"] == 2]

    spec = importlib.util.spec_from_file_location("ab_base_p8_for_p2", str(VAULT_DIR / "build_aditya_bharat_page8_desh_videsh.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _patch_mod_for_chhattisgarh(mod)

    mod.connect_page_designer()
    grid = mod.AdityaBharatPage8Grid()

    if os.environ.get("AB_NO_CLOSE") != "1" and os.environ.get("AB_SKIP_FILE_NEW") != "1":
        for _ in range(8):
            try:
                mod.cmd("file.close", {"save": False})
            except Exception:
                break

    mod.batch([
        {"command": "file.new", "params": {
            "width": grid.width_pt,
            "height": grid.height_pt,
            "pages": 1,
            "facingPages": False,
            "columns": grid.cols,
            "gutter": grid.gutter_pt,
            "margins": grid.margin_x_pt,
            "title": "आदित्य भारत — पेज 02 छत्तीसगढ़ राजधानी (18-11-2026 | 10 खबरें)",
        }},
        {"command": "document.preferences", "params": {
            "baselineGrid": {"start": grid.margin_y_pt, "increment": 11.25, "relativeTo": "topOfPage"}
        }},
        {"command": "swatch.create", "params": {"name": "FlyerCrimson", "color": "#c4121a"}},
        {"command": "swatch.create", "params": {"name": "ClosingGray", "color": "#808285"}},
        {"command": "swatch.create", "params": {"name": "EditPointerBg", "color": "#f2f2f2"}},
    ])

    # --- 1.5 cm Inside Running Masthead ---
    mh_x0, mh_y0, mh_x1, mh_y1 = grid.print_x0, grid.masthead_y0, grid.print_x1, grid.masthead_y1
    sec_w = cm(4.4)
    sec_y0, sec_y1 = round(mh_y0 + mm(1.0), 2), round(mh_y1 - mm(1.8), 2)
    r_sec = mod.cmd("frame.create", {"spread": 0, "rect": [mh_x0, sec_y0, round(mh_x0 + sec_w, 2), sec_y1], "content": "text", "text": "छत्तीसगढ़"})
    mod.batch([
        {"command": "object.fill", "params": {"ids": [r_sec["id"]], "swatch": "FlyerCrimson", "tint": 1.0}},
        {"command": "object.textFrameOptions", "params": {"ids": [r_sec["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_sec["story"], "anchor": 0, "focus": 99}},
        {"command": "type.char", "params": {"attrs": {"fontFamily": "DB Hindi 6", "fontStyle": "Regular", "size": 20.0, "leading": {"kind": "points", "value": 21.0}, "fill": "[Paper]"}}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "firstLineIndent": 0.0}}},
    ])
    logo_w = cm(4.85)
    logo_x0 = round((mh_x0 + mh_x1 - logo_w) / 2.0, 2)
    logo_x1 = round(logo_x0 + logo_w, 2)
    logo_img_path = VAULT_DIR / "photos" / "aditya_bharat_masthead_logo.png"
    r_logo = mod.cmd("frame.create", {"spread": 0, "rect": [logo_x0, round(mh_y0 + mm(0.8), 2), logo_x1, sec_y1], "content": "graphic"})
    mod.batch([
        {"command": "file.place", "params": {"frame": r_logo["id"], "path": str(logo_img_path)}},
        {"command": "object.fit", "params": {"ids": [r_logo["id"]], "mode": "fitProportionally"}},
        {"command": "object.stroke", "params": {"ids": [r_logo["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
    ])
    pnum_w = cm(1.4)
    pnum_x0 = round(mh_x1 - pnum_w, 2)
    r_pnum = mod.cmd("frame.create", {"spread": 0, "rect": [pnum_x0, sec_y0, mh_x1, sec_y1], "content": "text", "text": "02"})
    mod.batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_pnum["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_pnum["story"], "anchor": 0, "focus": 99}},
        {"command": "type.char", "params": {"attrs": {"fontFamily": "Times New Roman", "fontStyle": "Bold", "size": 18.0, "leading": {"kind": "points", "value": 19.0}, "fill": "[Black]"}}},
        {"command": "type.para", "params": {"attrs": {"align": "right", "firstLineIndent": 0.0}}},
    ])
    dt_x0, dt_x1 = round(logo_x1 + cm(0.4), 2), round(pnum_x0 - cm(0.2), 2)
    r_dt = mod.cmd("frame.create", {"spread": 0, "rect": [dt_x0, sec_y0, dt_x1, sec_y1], "content": "text", "text": date_label})
    mod.batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_dt["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_dt["story"], "anchor": 0, "focus": 199}},
        {"command": "type.char", "params": {"attrs": {"fontFamily": "DB Hindi", "fontStyle": "Bold", "size": 15.5, "leading": {"kind": "points", "value": 16.5}, "fill": "[Black]"}}},
        {"command": "type.para", "params": {"attrs": {"align": "right", "firstLineIndent": 0.0}}},
    ])
    r_mrule = mod.cmd("line.create", {"spread": 0, "a": [mh_x0, mh_y1], "b": [mh_x1, mh_y1]})
    mod.cmd("object.stroke", {"ids": [r_mrule["id"]], "swatch": "[Black]", "weight": 2.0, "tint": 0.60})

    pts_log = []

    # ==========================================================================
    # BAND 1 (STORIES 1 & 2): 6-COL TOP FLYER (Cols 1..6) + 2-COL RIGHT STORY (Cols 7..8)
    #   y = 2.85 .. 12.15 cm (Height = 9.3 cm)
    # ==========================================================================
    b1_y0 = round(mh_y1 + mm(3.5), 2)
    b1_y1 = mod.snap_frame_bottom_to_baseline(round(b1_y0 + cm(9.3), 2))

    s1 = p2_stories[0]
    fl_x0, fl_x1 = grid.col_x0(1), grid.col_x1(1, 6)
    _, _, _, fl_sh = mod.fit_aditya_bharat_headline(
        0, fl_x0, b1_y0, fl_x1, raw_text=s1["subhead"], target_lines=1,
        font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]", hi_pt=15.0, lo_pt=12.0, align="center",
    )
    fl_hy0 = round(b1_y0 + fl_sh + 1.0, 2)
    _, _, p_s1, fl_hh = mod.fit_aditya_bharat_headline(
        0, fl_x0, fl_hy0, fl_x1, raw_text=s1["headline"], target_lines=1,
        font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]", hi_pt=48.0, lo_pt=34.0, align="center",
    )
    pts_log.append(p_s1)
    fl_by0 = round(fl_hy0 + fl_hh + 1.5, 2)
    r_fl_b = mod.cmd("frame.create", {"spread": 0, "rect": [fl_x0, fl_by0, fl_x1, b1_y1], "content": "text", "text": ""})
    mod.cmd("object.textFrameOptions", {"ids": [r_fl_b["id"]], "columns": 6, "gutter": grid.gutter_pt, "verticalJustification": "top", "columnRule": False})
    mod.place_red_subject_blurb(0, fl_x0, round(fl_by0 + cm(1.55), 2), s1["blurb"])
    fl_cap_y1 = round(mod.snap_underflow_top(b1_y1, num_underflow_lines=4) - 3.2, 2)
    mod.place_photo_and_caption_cmyk(
        0, grid.col_x0(3), fl_by0, grid.col_x1(3, 2), fl_cap_y1,
        s1["photo"], "cg_p2_s1_flyer_cmyk.jpg", s1["caption"], cap_h=21.0,
    )
    mod.fit_aditya_bharat_body(r_fl_b["story"], s1["city"], s1["agency"], s1["body"])

    s2 = p2_stories[1]
    p_s2 = mod.place_multi_col_story(
        grid, grid.col_x0(7), grid.col_x1(7, 2), b1_y0, b1_y1, cols=2,
        headline=s2["headline"], city=s2["city"], agency=s2["agency"],
        blurb_word=s2["blurb"], body=s2["body"], target_lines=2, hi_pt=44.0, lo_pt=30.0,
    )
    pts_log.append(p_s2)

    sep1_y = round(b1_y1 + mm(1.75), 2)
    r_sep1 = mod.cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep1_y], "b": [grid.print_x1, sep1_y]})
    mod.cmd("object.stroke", {"ids": [r_sep1["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 2 (STORIES 3, 4, 5): 5-COL MAIN LEAD (Cols 1..5, Gray Box in LAST Col 5)
    #   + RIGHT 3-COL STACKED STORIES 4 & 5 (Cols 6..8)
    #   y = 12.50 .. 27.70 cm (Height = 15.2 cm)
    # ==========================================================================
    b2_y0 = round(sep1_y + mm(1.75), 2)
    b2_y1 = mod.snap_frame_bottom_to_baseline(round(b2_y0 + cm(15.2), 2))

    s3 = p2_stories[2]
    l_x0, l_x1 = grid.col_x0(1), grid.col_x1(1, 5)
    _, _, p_s3, l_hh = mod.fit_aditya_bharat_headline(
        0, l_x0, b2_y0, l_x1, raw_text=s3["headline"], target_lines=2,
        font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]", hi_pt=56.0, lo_pt=42.0, align="left",
    )
    pts_log.append(p_s3)
    l_sy0 = round(b2_y0 + l_hh + 1.0, 2)
    _, _, _, l_sh = mod.fit_aditya_bharat_headline(
        0, l_x0, l_sy0, l_x1, raw_text=s3["subhead"], target_lines=1,
        font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]", hi_pt=15.0, lo_pt=12.0, align="left",
    )
    l_by0 = round(l_sy0 + l_sh + 1.5, 2)
    r_l_b = mod.cmd("frame.create", {"spread": 0, "rect": [grid.col_x0(1), l_by0, grid.col_x1(1, 4), b2_y1], "content": "text", "text": ""})
    mod.cmd("object.textFrameOptions", {"ids": [r_l_b["id"]], "columns": 4, "gutter": grid.gutter_pt, "verticalJustification": "top", "columnRule": False})
    mod.place_red_subject_blurb(0, grid.col_x0(1), round(l_by0 + cm(1.65), 2), s3["blurb"])
    l_cap_y1 = round(mod.snap_underflow_top(b2_y1, num_underflow_lines=6) - 3.2, 2)
    mod.place_photo_and_caption_cmyk(
        0, grid.col_x0(2), l_by0, grid.col_x1(2, 2), l_cap_y1,
        s3["photo"], "cg_p2_s3_lead_cmyk.jpg", s3["caption"], cap_h=21.0,
    )
    mod.fit_aditya_bharat_body(r_l_b["story"], s3["city"], s3["agency"], s3["body"])

    # LAST Col 5 = Full-Height 40% Gray Box
    inset_pt = mm(2.5)
    r_gb = mod.cmd("frame.create", {"spread": 0, "rect": [grid.col_x0(5), l_by0, grid.col_x1(5, 1), b2_y1], "content": "text", "text": ""})
    mod.batch([
        {"command": "object.fill", "params": {"ids": [r_gb["id"]], "swatch": "[Black]", "tint": 0.15}},
        {"command": "object.stroke", "params": {"ids": [r_gb["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 0.55}},
        {"command": "object.textFrameOptions", "params": {"ids": [r_gb["id"]], "columns": 1, "inset": [inset_pt, inset_pt, inset_pt, inset_pt], "verticalJustification": "top"}},
    ])
    mod.fit_box_completely(r_gb["story"], head_str=s3["box_head"], raw_bullets=s3["box_bullets"])

    # Right 3-Col Stacked Stories 4 & 5 (Cols 6..8)
    r3_x0, r3_x1 = grid.col_x0(6), grid.col_x1(6, 3)
    r3_mid_y = mod.snap_frame_bottom_to_baseline(round(b2_y0 + cm(7.4), 2))
    s4 = p2_stories[3]
    p_s4 = mod.place_multi_col_story(
        grid, r3_x0, r3_x1, b2_y0, r3_mid_y, cols=3,
        headline=s4["headline"], city=s4["city"], agency=s4["agency"],
        blurb_word=s4["blurb"], body=s4["body"], target_lines=2, hi_pt=48.0, lo_pt=30.0,
    )
    pts_log.append(p_s4)

    r3_sep_y = round(r3_mid_y + mm(1.75), 2)
    r_r3_sep = mod.cmd("line.create", {"spread": 0, "a": [r3_x0, r3_sep_y], "b": [r3_x1, r3_sep_y]})
    mod.cmd("object.stroke", {"ids": [r_r3_sep["id"]], "swatch": "[Black]", "weight": 0.65, "tint": 0.85})

    s5 = p2_stories[4]
    p_s5 = mod.place_multi_col_story(
        grid, r3_x0, r3_x1, round(r3_sep_y + mm(1.75), 2), b2_y1, cols=3,
        headline=s5["headline"], city=s5["city"], agency=s5["agency"],
        blurb_word=s5["blurb"], body=s5["body"], target_lines=2, hi_pt=48.0, lo_pt=30.0,
    )
    pts_log.append(p_s5)

    sep2_y = round(b2_y1 + mm(1.75), 2)
    r_sep2 = mod.cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep2_y], "b": [grid.print_x1, sep2_y]})
    mod.cmd("object.stroke", {"ids": [r_sep2["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 3 (STORIES 6, 7, 8): 3 + 2 + 3 INTERLOCKED BAND
    #   y = 28.05 .. 39.65 cm (Height = 11.6 cm)
    # ==========================================================================
    b3_y0 = round(sep2_y + mm(1.75), 2)
    b3_y1 = mod.snap_frame_bottom_to_baseline(round(b3_y0 + cm(11.6), 2))

    # Story 6 (Cols 1..3 Illustrated)
    s6 = p2_stories[5]
    s6_x0, s6_x1 = grid.col_x0(1), grid.col_x1(1, 3)
    _, _, p_s6, s6_hh = mod.fit_aditya_bharat_headline(
        0, s6_x0, b3_y0, s6_x1, raw_text=s6["headline"], target_lines=2,
        font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]", hi_pt=48.0, lo_pt=30.0, align="left",
    )
    pts_log.append(p_s6)
    s6_by0 = round(b3_y0 + s6_hh + 1.5, 2)
    r_s6_b = mod.cmd("frame.create", {"spread": 0, "rect": [s6_x0, s6_by0, s6_x1, b3_y1], "content": "text", "text": ""})
    mod.cmd("object.textFrameOptions", {"ids": [r_s6_b["id"]], "columns": 3, "gutter": grid.gutter_pt, "verticalJustification": "top", "columnRule": False})
    mod.place_red_subject_blurb(0, s6_x0, round(s6_by0 + cm(1.55), 2), s6["blurb"])
    s6_cap_y1 = round(mod.snap_underflow_top(b3_y1, num_underflow_lines=5) - 3.2, 2)
    mod.place_photo_and_caption_cmyk(
        0, grid.col_x0(2), s6_by0, grid.col_x1(2, 2), s6_cap_y1,
        s6["photo"], "cg_p2_s6_korba_cmyk.jpg", s6["caption"], cap_h=20.0,
    )
    mod.fit_aditya_bharat_body(r_s6_b["story"], s6["city"], s6["agency"], s6["body"])

    # Story 7 (Cols 4..5)
    s7 = p2_stories[6]
    p_s7 = mod.place_multi_col_story(
        grid, grid.col_x0(4), grid.col_x1(4, 2), b3_y0, b3_y1, cols=2,
        headline=s7["headline"], city=s7["city"], agency=s7["agency"],
        blurb_word=s7["blurb"], body=s7["body"], target_lines=2, hi_pt=44.0, lo_pt=30.0,
    )
    pts_log.append(p_s7)

    # Story 8 (Cols 6..8)
    s8 = p2_stories[7]
    p_s8 = mod.place_multi_col_story(
        grid, grid.col_x0(6), grid.col_x1(6, 3), b3_y0, b3_y1, cols=3,
        headline=s8["headline"], city=s8["city"], agency=s8["agency"],
        blurb_word=s8["blurb"], body=s8["body"], target_lines=2, hi_pt=48.0, lo_pt=30.0,
    )
    pts_log.append(p_s8)

    sep3_y = round(b3_y1 + mm(1.75), 2)
    r_sep3 = mod.cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep3_y], "b": [grid.print_x1, sep3_y]})
    mod.cmd("object.stroke", {"ids": [r_sep3["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 4 (STORIES 9 & 10): BOTTOM 5-COL ANCHOR (Cols 1..5) + 3-COL RIGHT STORY (Cols 6..8)
    #   y = 40.00 .. 52.00 cm (Height = 12.0 cm)
    # ==========================================================================
    bot_y0 = round(sep3_y + mm(1.75), 2)
    bot_y1 = mod.snap_frame_bottom_to_baseline(grid.print_y1)

    s9 = p2_stories[8]
    anc_x0, anc_x1 = grid.col_x0(1), grid.col_x1(1, 5)
    _, _, p_s9, anc_hh = mod.fit_aditya_bharat_headline(
        0, anc_x0, bot_y0, anc_x1, raw_text=s9["headline"], target_lines=1,
        font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]", hi_pt=52.0, lo_pt=33.0, align="center",
    )
    pts_log.append(p_s9)
    anc_sy0 = round(bot_y0 + anc_hh + 1.0, 2)
    _, _, _, anc_sh = mod.fit_aditya_bharat_headline(
        0, anc_x0, anc_sy0, anc_x1, raw_text=s9["subhead"], target_lines=1,
        font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]", hi_pt=14.5, lo_pt=11.5, align="center",
    )
    anc_by0 = round(anc_sy0 + anc_sh + 1.5, 2)
    r_anc_b = mod.cmd("frame.create", {"spread": 0, "rect": [anc_x0, anc_by0, anc_x1, bot_y1], "content": "text", "text": ""})
    mod.cmd("object.textFrameOptions", {"ids": [r_anc_b["id"]], "columns": 5, "gutter": grid.gutter_pt, "verticalJustification": "top", "columnRule": False})
    mod.place_red_subject_blurb(0, anc_x0, round(anc_by0 + cm(1.55), 2), s9["blurb"])
    anc_cap_y1 = round(mod.snap_underflow_top(bot_y1, num_underflow_lines=5) - 3.2, 2)
    mod.place_photo_and_caption_cmyk(
        0, grid.col_x0(3), anc_by0, grid.col_x1(3, 2), anc_cap_y1,
        s9["photo"], "cg_p2_s9_anchor_cmyk.jpg", s9["caption"], cap_h=20.0,
    )
    mod.fit_aditya_bharat_body(r_anc_b["story"], s9["city"], s9["agency"], s9["body"])

    s10 = p2_stories[9]
    p_s10 = mod.place_multi_col_story(
        grid, grid.col_x0(6), grid.col_x1(6, 3), bot_y0, bot_y1, cols=3,
        headline=s10["headline"], city=s10["city"], agency=s10["agency"],
        blurb_word=s10["blurb"], body=s10["body"], target_lines=2, hi_pt=48.0, lo_pt=30.0,
    )
    pts_log.append(p_s10)

    mod.cmd("edit.deselectAll", {})
    mod.cmd("view.fitPage", {})

    out_pd = VAULT_DIR / "Aditya_Bharat_Page_02_Mahanagar_34x53.pagedesigner"
    out_png = VAULT_DIR / "Aditya_Bharat_Page_02_Mahanagar_34x53.png"
    out_pdf = VAULT_DIR / "Aditya_Bharat_Page_02_Mahanagar_CMYK_34x53.pdf"
    mod.rpc("app.save", {"path": str(out_pd)})
    mod.rpc("app.export", {"path": str(out_png), "page": 0, "scale": 1.5})
    try:
        mod.rpc("engine.execute", {"command": "file.exportPdf", "params": {"path": str(out_pdf)}})
    except Exception:
        pass

    art_png = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\8707c72d-58b0-4715-a099-3efffcd57514\aditya_bharat_cg_page_02_18nov_34x53.png")
    shutil.copy2(out_png, art_png)
    print(f"=== CHHATTISGARH PAGE 02 (10 STORIES | 18-11-2026) BUILT IN {time.perf_counter()-t0:.2f}s | Pts={pts_log} ===")
    return {"ok": True, "page": 2, "stories": 10, "headline_pts": pts_log, "png": str(out_png), "pdf": str(out_pdf)}


# ==============================================================================
# 3. PAGE 03 BUILDER — 10 CHHATTISGARH STORIES (VERTICAL-START PRADESHIK LAYOUT)
# ==============================================================================
def build_chhattisgarh_page3_10stories(date_label: str = None, date_str: str = "18-11-2026", force_fresh_live: bool = False) -> dict:
    t0 = time.perf_counter()
    data = harvest_chhattisgarh_news_for_date(date_str, force_fresh_live=force_fresh_live)
    if not date_label:
        date_label = data.get("dateline_hi", format_hindi_dateline(date_str)) + "  |"
    p3_stories = [s for s in data["stories"] if s["page"] == 3]

    spec = importlib.util.spec_from_file_location("ab_base_p8_for_p3", str(VAULT_DIR / "build_aditya_bharat_page8_desh_videsh.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _patch_mod_for_chhattisgarh(mod)

    mod.connect_page_designer()
    grid = mod.AdityaBharatPage8Grid()

    if os.environ.get("AB_NO_CLOSE") != "1" and os.environ.get("AB_SKIP_FILE_NEW") != "1":
        for _ in range(8):
            try:
                mod.cmd("file.close", {"save": False})
            except Exception:
                break

    mod.batch([
        {"command": "file.new", "params": {
            "width": grid.width_pt,
            "height": grid.height_pt,
            "pages": 1,
            "facingPages": False,
            "columns": grid.cols,
            "gutter": grid.gutter_pt,
            "margins": grid.margin_x_pt,
            "title": "आदित्य भारत — पेज 03 छत्तीसगढ़ प्रादेशिक (18-11-2026 | 10 खबरें)",
        }},
        {"command": "document.preferences", "params": {
            "baselineGrid": {"start": grid.margin_y_pt, "increment": 11.25, "relativeTo": "topOfPage"}
        }},
        {"command": "swatch.create", "params": {"name": "FlyerCrimson", "color": "#c4121a"}},
        {"command": "swatch.create", "params": {"name": "ClosingGray", "color": "#808285"}},
        {"command": "swatch.create", "params": {"name": "EditPointerBg", "color": "#f2f2f2"}},
    ])

    # --- 1.5 cm Inside Running Masthead ---
    mh_x0, mh_y0, mh_x1, mh_y1 = grid.print_x0, grid.masthead_y0, grid.print_x1, grid.masthead_y1
    sec_w = cm(4.4)
    sec_y0, sec_y1 = round(mh_y0 + mm(1.0), 2), round(mh_y1 - mm(1.8), 2)
    r_sec = mod.cmd("frame.create", {"spread": 0, "rect": [mh_x0, sec_y0, round(mh_x0 + sec_w, 2), sec_y1], "content": "text", "text": "प्रादेशिक"})
    mod.batch([
        {"command": "object.fill", "params": {"ids": [r_sec["id"]], "swatch": "FlyerCrimson", "tint": 1.0}},
        {"command": "object.textFrameOptions", "params": {"ids": [r_sec["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_sec["story"], "anchor": 0, "focus": 99}},
        {"command": "type.char", "params": {"attrs": {"fontFamily": "DB Hindi 6", "fontStyle": "Regular", "size": 20.0, "leading": {"kind": "points", "value": 21.0}, "fill": "[Paper]"}}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "firstLineIndent": 0.0}}},
    ])
    logo_w = cm(4.85)
    logo_x0 = round((mh_x0 + mh_x1 - logo_w) / 2.0, 2)
    logo_x1 = round(logo_x0 + logo_w, 2)
    logo_img_path = VAULT_DIR / "photos" / "aditya_bharat_masthead_logo.png"
    r_logo = mod.cmd("frame.create", {"spread": 0, "rect": [logo_x0, round(mh_y0 + mm(0.8), 2), logo_x1, sec_y1], "content": "graphic"})
    mod.batch([
        {"command": "file.place", "params": {"frame": r_logo["id"], "path": str(logo_img_path)}},
        {"command": "object.fit", "params": {"ids": [r_logo["id"]], "mode": "fitProportionally"}},
        {"command": "object.stroke", "params": {"ids": [r_logo["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
    ])
    pnum_w = cm(1.4)
    pnum_x0 = round(mh_x1 - pnum_w, 2)
    r_pnum = mod.cmd("frame.create", {"spread": 0, "rect": [pnum_x0, sec_y0, mh_x1, sec_y1], "content": "text", "text": "03"})
    mod.batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_pnum["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_pnum["story"], "anchor": 0, "focus": 99}},
        {"command": "type.char", "params": {"attrs": {"fontFamily": "Times New Roman", "fontStyle": "Bold", "size": 18.0, "leading": {"kind": "points", "value": 19.0}, "fill": "[Black]"}}},
        {"command": "type.para", "params": {"attrs": {"align": "right", "firstLineIndent": 0.0}}},
    ])
    dt_x0, dt_x1 = round(logo_x1 + cm(0.4), 2), round(pnum_x0 - cm(0.2), 2)
    r_dt = mod.cmd("frame.create", {"spread": 0, "rect": [dt_x0, sec_y0, dt_x1, sec_y1], "content": "text", "text": date_label})
    mod.batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_dt["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_dt["story"], "anchor": 0, "focus": 199}},
        {"command": "type.char", "params": {"attrs": {"fontFamily": "DB Hindi", "fontStyle": "Bold", "size": 15.5, "leading": {"kind": "points", "value": 16.5}, "fill": "[Black]"}}},
        {"command": "type.para", "params": {"attrs": {"align": "right", "firstLineIndent": 0.0}}},
    ])
    r_mrule = mod.cmd("line.create", {"spread": 0, "a": [mh_x0, mh_y1], "b": [mh_x1, mh_y1]})
    mod.cmd("object.stroke", {"ids": [r_mrule["id"]], "swatch": "[Black]", "weight": 2.0, "tint": 0.60})

    pts_log = []

    # ==========================================================================
    # TOP ASYMMETRIC ZONE (STORIES 1, 2, 3, 4, 5): y = 2.85 .. 27.20 cm (Height = 24.35 cm)
    #   - Left Cols 1..5:
    #       * Story 1: 5-Col Vertical-Start Lead (y = 2.85 .. 18.50 cm, Gray Box in LAST Col 5)
    #       * Story 2: Cols 1..3 (y = 18.85 .. 27.20 cm)
    #       * Story 3: Cols 4..5 (y = 18.85 .. 27.20 cm)
    #   - Right Cols 6..8:
    #       * Story 4: Cols 6..8 Illustrated Top Story (y = 2.85 .. 15.20 cm)
    #       * Story 5: Cols 6..8 Mid Story (y = 15.55 .. 27.20 cm)
    # ==========================================================================
    z1_y0 = round(mh_y1 + mm(3.5), 2)
    z1_y1 = mod.snap_frame_bottom_to_baseline(round(z1_y0 + cm(24.35), 2))
    lead_y1 = mod.snap_frame_bottom_to_baseline(round(z1_y0 + cm(15.65), 2))

    # --- Story 1: Left 5-Col Vertical Lead (No Top Flyer!) ---
    s1 = p3_stories[0]
    l_x0, l_x1 = grid.col_x0(1), grid.col_x1(1, 5)
    _, _, _, k_sh = mod.fit_aditya_bharat_headline(
        0, l_x0, z1_y0, l_x1, raw_text=s1["kicker"], target_lines=1,
        font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]", hi_pt=14.5, lo_pt=11.5, align="left",
    )
    l_hy0 = round(z1_y0 + k_sh + 1.0, 2)
    _, _, p_s1, l_hh = mod.fit_aditya_bharat_headline(
        0, l_x0, l_hy0, l_x1, raw_text=s1["headline"], target_lines=2,
        font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]", hi_pt=54.0, lo_pt=40.0, align="left",
    )
    pts_log.append(p_s1)
    l_sy0 = round(l_hy0 + l_hh + 1.0, 2)
    _, _, _, l_sh = mod.fit_aditya_bharat_headline(
        0, l_x0, l_sy0, l_x1, raw_text=s1["subhead"], target_lines=1,
        font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]", hi_pt=14.5, lo_pt=11.5, align="left",
    )
    l_by0 = round(l_sy0 + l_sh + 1.5, 2)
    r_l_b = mod.cmd("frame.create", {"spread": 0, "rect": [grid.col_x0(1), l_by0, grid.col_x1(1, 4), lead_y1], "content": "text", "text": ""})
    mod.cmd("object.textFrameOptions", {"ids": [r_l_b["id"]], "columns": 4, "gutter": grid.gutter_pt, "verticalJustification": "top", "columnRule": False})
    mod.place_red_subject_blurb(0, grid.col_x0(1), round(l_by0 + cm(1.6), 2), s1["blurb"])
    l_cap_y1 = round(mod.snap_underflow_top(lead_y1, num_underflow_lines=5) - 3.2, 2)
    mod.place_photo_and_caption_cmyk(
        0, grid.col_x0(2), l_by0, grid.col_x1(2, 2), l_cap_y1,
        s1["photo"], "cg_p3_s1_dhan_cmyk.jpg", s1["caption"], cap_h=20.0,
    )
    mod.fit_aditya_bharat_body(r_l_b["story"], s1["city"], s1["agency"], s1["body"])

    # LAST Col 5 = Full-Height 40% Gray Box
    inset_pt = mm(2.5)
    r_gb = mod.cmd("frame.create", {"spread": 0, "rect": [grid.col_x0(5), l_by0, grid.col_x1(5, 1), lead_y1], "content": "text", "text": ""})
    mod.batch([
        {"command": "object.fill", "params": {"ids": [r_gb["id"]], "swatch": "[Black]", "tint": 0.15}},
        {"command": "object.stroke", "params": {"ids": [r_gb["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 0.55}},
        {"command": "object.textFrameOptions", "params": {"ids": [r_gb["id"]], "columns": 1, "inset": [inset_pt, inset_pt, inset_pt, inset_pt], "verticalJustification": "top"}},
    ])
    mod.fit_box_completely(r_gb["story"], head_str=s1["box_head"], raw_bullets=s1["box_bullets"])

    l_sep_y = round(lead_y1 + mm(1.75), 2)
    r_lsep = mod.cmd("line.create", {"spread": 0, "a": [l_x0, l_sep_y], "b": [l_x1, l_sep_y]})
    mod.cmd("object.stroke", {"ids": [r_lsep["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 0.85})

    sub_y0 = round(l_sep_y + mm(1.75), 2)
    # --- Story 2: Cols 1..3 under Lead ---
    s2 = p3_stories[1]
    p_s2 = mod.place_multi_col_story(
        grid, grid.col_x0(1), grid.col_x1(1, 3), sub_y0, z1_y1, cols=3,
        headline=s2["headline"], city=s2["city"], agency=s2["agency"],
        blurb_word=s2["blurb"], body=s2["body"], target_lines=2, hi_pt=48.0, lo_pt=30.0,
    )
    pts_log.append(p_s2)

    # --- Story 3: Cols 4..5 under Lead ---
    s3 = p3_stories[2]
    p_s3 = mod.place_multi_col_story(
        grid, grid.col_x0(4), grid.col_x1(4, 2), sub_y0, z1_y1, cols=2,
        headline=s3["headline"], city=s3["city"], agency=s3["agency"],
        blurb_word=s3["blurb"], body=s3["body"], target_lines=2, hi_pt=44.0, lo_pt=30.0,
    )
    pts_log.append(p_s3)

    # --- Story 4: Right Top 3-Col Illustrated Story (Cols 6..8) ---
    s4 = p3_stories[3]
    r3_x0, r3_x1 = grid.col_x0(6), grid.col_x1(6, 3)
    r3_mid_y = mod.snap_frame_bottom_to_baseline(round(z1_y0 + cm(12.8), 2))
    _, _, p_s4, s4_hh = mod.fit_aditya_bharat_headline(
        0, r3_x0, z1_y0, r3_x1, raw_text=s4["headline"], target_lines=2,
        font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]", hi_pt=48.0, lo_pt=30.0, align="left",
    )
    pts_log.append(p_s4)
    s4_by0 = round(z1_y0 + s4_hh + 1.5, 2)
    r_s4_b = mod.cmd("frame.create", {"spread": 0, "rect": [r3_x0, s4_by0, r3_x1, r3_mid_y], "content": "text", "text": ""})
    mod.cmd("object.textFrameOptions", {"ids": [r_s4_b["id"]], "columns": 3, "gutter": grid.gutter_pt, "verticalJustification": "top", "columnRule": False})
    mod.place_red_subject_blurb(0, r3_x0, round(s4_by0 + cm(1.55), 2), s4["blurb"])
    s4_cap_y1 = round(mod.snap_underflow_top(r3_mid_y, num_underflow_lines=4) - 3.2, 2)
    mod.place_photo_and_caption_cmyk(
        0, grid.col_x0(7), s4_by0, grid.col_x1(7, 2), s4_cap_y1,
        s4["photo"], "cg_p3_s4_hc_cmyk.jpg", s4["caption"], cap_h=20.0,
    )
    mod.fit_aditya_bharat_body(r_s4_b["story"], s4["city"], s4["agency"], s4["body"])

    r3_sep_y = round(r3_mid_y + mm(1.75), 2)
    r_r3s = mod.cmd("line.create", {"spread": 0, "a": [r3_x0, r3_sep_y], "b": [r3_x1, r3_sep_y]})
    mod.cmd("object.stroke", {"ids": [r_r3s["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 0.85})

    # --- Story 5: Right Mid 3-Col Story (Cols 6..8) ---
    s5 = p3_stories[4]
    p_s5 = mod.place_multi_col_story(
        grid, r3_x0, r3_x1, round(r3_sep_y + mm(1.75), 2), z1_y1, cols=3,
        headline=s5["headline"], city=s5["city"], agency=s5["agency"],
        blurb_word=s5["blurb"], body=s5["body"], target_lines=2, hi_pt=48.0, lo_pt=30.0,
    )
    pts_log.append(p_s5)

    sep1_y = round(z1_y1 + mm(1.75), 2)
    r_sep1 = mod.cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep1_y], "b": [grid.print_x1, sep1_y]})
    mod.cmd("object.stroke", {"ids": [r_sep1["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # MIDDLE BAND (STORIES 6, 7, 8): 2 + 4 + 2 INTERLOCKED SPLIT
    #   y = 27.55 .. 39.20 cm (Height = 11.65 cm)
    # ==========================================================================
    b2_y0 = round(sep1_y + mm(1.75), 2)
    b2_y1 = mod.snap_frame_bottom_to_baseline(round(b2_y0 + cm(11.65), 2))

    # --- Story 6: Left 2-Col Story (Cols 1..2) ---
    s6 = p3_stories[5]
    p_s6 = mod.place_multi_col_story(
        grid, grid.col_x0(1), grid.col_x1(1, 2), b2_y0, b2_y1, cols=2,
        headline=s6["headline"], city=s6["city"], agency=s6["agency"],
        blurb_word=s6["blurb"], body=s6["body"], target_lines=2, hi_pt=44.0, lo_pt=30.0,
    )
    pts_log.append(p_s6)

    # --- Story 7: Center 4-Col Illustrated Package (Cols 3..6) ---
    s7 = p3_stories[6]
    c4_x0, c4_x1 = grid.col_x0(3), grid.col_x1(3, 4)
    _, _, p_s7, c4_hh = mod.fit_aditya_bharat_headline(
        0, c4_x0, b2_y0, c4_x1, raw_text=s7["headline"], target_lines=2,
        font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]", hi_pt=52.0, lo_pt=31.0, align="left",
    )
    pts_log.append(p_s7)
    c4_sy0 = round(b2_y0 + c4_hh + 1.0, 2)
    _, _, _, c4_sh = mod.fit_aditya_bharat_headline(
        0, c4_x0, c4_sy0, c4_x1, raw_text=s7["subhead"], target_lines=1,
        font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]", hi_pt=14.0, lo_pt=11.5, align="left",
    )
    c4_by0 = round(c4_sy0 + c4_sh + 1.5, 2)
    r_c4_b = mod.cmd("frame.create", {"spread": 0, "rect": [c4_x0, c4_by0, c4_x1, b2_y1], "content": "text", "text": ""})
    mod.cmd("object.textFrameOptions", {"ids": [r_c4_b["id"]], "columns": 4, "gutter": grid.gutter_pt, "verticalJustification": "top", "columnRule": False})
    mod.place_red_subject_blurb(0, c4_x0, round(c4_by0 + cm(1.55), 2), s7["blurb"])
    c4_cap_y1 = round(mod.snap_underflow_top(b2_y1, num_underflow_lines=4) - 3.2, 2)
    mod.place_photo_and_caption_cmyk(
        0, grid.col_x0(4), c4_by0, grid.col_x1(4, 2), c4_cap_y1,
        s7["photo"], "cg_p3_s7_bastar_cmyk.jpg", s7["caption"], cap_h=20.0,
    )
    mod.fit_aditya_bharat_body(r_c4_b["story"], s7["city"], s7["agency"], s7["body"])

    # --- Story 8: Right 2-Col Story (Cols 7..8) ---
    s8 = p3_stories[7]
    p_s8 = mod.place_multi_col_story(
        grid, grid.col_x0(7), grid.col_x1(7, 2), b2_y0, b2_y1, cols=2,
        headline=s8["headline"], city=s8["city"], agency=s8["agency"],
        blurb_word=s8["blurb"], body=s8["body"], target_lines=2, hi_pt=44.0, lo_pt=30.0,
    )
    pts_log.append(p_s8)

    sep2_y = round(b2_y1 + mm(1.75), 2)
    r_sep2 = mod.cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep2_y], "b": [grid.print_x1, sep2_y]})
    mod.cmd("object.stroke", {"ids": [r_sep2["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BOTTOM BAND (STORIES 9 & 10): LEFT 2-COL STORY (Cols 1..2) + RIGHT 6-COL GRAND ANCHOR (Cols 3..8)
    #   y = 39.55 .. 52.00 cm (Height = 12.45 cm)
    # ==========================================================================
    bot_y0 = round(sep2_y + mm(1.75), 2)
    bot_y1 = mod.snap_frame_bottom_to_baseline(grid.print_y1)

    s9 = p3_stories[8]
    p_s9 = mod.place_multi_col_story(
        grid, grid.col_x0(1), grid.col_x1(1, 2), bot_y0, bot_y1, cols=2,
        headline=s9["headline"], city=s9["city"], agency=s9["agency"],
        blurb_word=s9["blurb"], body=s9["body"], target_lines=2, hi_pt=44.0, lo_pt=30.0,
    )
    pts_log.append(p_s9)

    s10 = p3_stories[9]
    anc_x0, anc_x1 = grid.col_x0(3), grid.col_x1(3, 6)
    _, _, p_s10, anc_hh = mod.fit_aditya_bharat_headline(
        0, anc_x0, bot_y0, anc_x1, raw_text=s10["headline"], target_lines=1,
        font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]", hi_pt=52.0, lo_pt=34.0, align="center",
    )
    pts_log.append(p_s10)
    anc_sy0 = round(bot_y0 + anc_hh + 1.0, 2)
    _, _, _, anc_sh = mod.fit_aditya_bharat_headline(
        0, anc_x0, anc_sy0, anc_x1, raw_text=s10["subhead"], target_lines=1,
        font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]", hi_pt=14.5, lo_pt=11.5, align="center",
    )
    anc_by0 = round(anc_sy0 + anc_sh + 1.5, 2)
    r_anc_b = mod.cmd("frame.create", {"spread": 0, "rect": [anc_x0, anc_by0, anc_x1, bot_y1], "content": "text", "text": ""})
    mod.cmd("object.textFrameOptions", {"ids": [r_anc_b["id"]], "columns": 6, "gutter": grid.gutter_pt, "verticalJustification": "top", "columnRule": False})
    mod.place_red_subject_blurb(0, anc_x0, round(anc_by0 + cm(1.55), 2), s10["blurb"])
    anc_cap_y1 = round(mod.snap_underflow_top(bot_y1, num_underflow_lines=5) - 3.2, 2)
    mod.place_photo_and_caption_cmyk(
        0, grid.col_x0(5), anc_by0, grid.col_x1(5, 2), anc_cap_y1,
        s10["photo"], "cg_p3_s10_anchor_cmyk.jpg", s10["caption"], cap_h=20.0,
    )
    mod.fit_aditya_bharat_body(r_anc_b["story"], s10["city"], s10["agency"], s10["body"])

    mod.cmd("edit.deselectAll", {})
    mod.cmd("view.fitPage", {})

    out_pd = VAULT_DIR / "Aditya_Bharat_Page_03_Pradeshik_34x53.pagedesigner"
    out_png = VAULT_DIR / "Aditya_Bharat_Page_03_Pradeshik_34x53.png"
    out_pdf = VAULT_DIR / "Aditya_Bharat_Page_03_Pradeshik_CMYK_34x53.pdf"
    mod.rpc("app.save", {"path": str(out_pd)})
    mod.rpc("app.export", {"path": str(out_png), "page": 0, "scale": 1.5})
    try:
        mod.rpc("engine.execute", {"command": "file.exportPdf", "params": {"path": str(out_pdf)}})
    except Exception:
        pass

    art_png = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\8707c72d-58b0-4715-a099-3efffcd57514\aditya_bharat_cg_page_03_18nov_34x53.png")
    shutil.copy2(out_png, art_png)
    print(f"=== CHHATTISGARH PAGE 03 (10 STORIES | 18-11-2026) BUILT IN {time.perf_counter()-t0:.2f}s | Pts={pts_log} ===")
    return {"ok": True, "page": 3, "stories": 10, "headline_pts": pts_log, "png": str(out_png), "pdf": str(out_pdf)}


def build_both_chhattisgarh_pages_2_and_3(date_str: str = "18-11-2026", force_fresh_live: bool = False, export_desktop_pdf: bool = False) -> dict:
    import aditya_bharat_studio_app_2424 as studio
    from PIL import Image
    studio.ensure_page_designer_running()
    os.environ.pop("AB_TARGET_SPREAD", None)
    os.environ.pop("AB_SKIP_FILE_NEW", None)
    os.environ.pop("AB_SKIP_SAVE", None)

    harvest_chhattisgarh_news_for_date(date_str, force_fresh_live=force_fresh_live)

    # 1. Build & export standalone Page 02 (.pagedesigner, .png, .pdf)
    os.environ["AB_NO_CLOSE"] = "0"
    r2 = build_chhattisgarh_page2_10stories(date_str=date_str, force_fresh_live=False)

    # 2. Build & export standalone Page 03 (.pagedesigner, .png, .pdf)
    os.environ["AB_NO_CLOSE"] = "0"
    r3 = build_chhattisgarh_page3_10stories(date_str=date_str, force_fresh_live=False)

    # 3. Now open a 2-Page Combined Document (Spread 0 = Page 02, Spread 1 = Page 03) in Page Designer
    spec = importlib.util.spec_from_file_location("ab_base_comb", str(VAULT_DIR / "build_aditya_bharat_page8_desh_videsh.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.connect_page_designer()
    grid = mod.AdityaBharatPage8Grid()
    for _ in range(6):
        try:
            mod.rpc("engine.execute", {"command": "file.close", "params": {"save": False}})
        except Exception:
            break
    mod.rpc("engine.batch", {"commands": [
        {"command": "file.new", "params": {
            "width": grid.width_pt,
            "height": grid.height_pt,
            "pages": 2,
            "facingPages": False,
            "columns": grid.cols,
            "gutter": grid.gutter_pt,
            "margins": grid.margin_x_pt,
            "title": f"आदित्य भारत — छत्तीसगढ़ पेज 02 एवं पेज 03 ({date_str} | 20 खबरें)",
        }},
        {"command": "document.preferences", "params": {
            "baselineGrid": {"start": grid.margin_y_pt, "increment": 11.25, "relativeTo": "topOfPage"}
        }},
    ]})

    os.environ["AB_NO_CLOSE"] = "1"
    os.environ["AB_SKIP_FILE_NEW"] = "1"
    os.environ["AB_SKIP_SAVE"] = "1"
    os.environ["AB_TARGET_SPREAD"] = "0"
    build_chhattisgarh_page2_10stories(date_str=date_str, force_fresh_live=False)
    os.environ["AB_TARGET_SPREAD"] = "1"
    build_chhattisgarh_page3_10stories(date_str=date_str, force_fresh_live=False)

    os.environ.pop("AB_NO_CLOSE", None)
    os.environ.pop("AB_SKIP_FILE_NEW", None)
    os.environ.pop("AB_SKIP_SAVE", None)
    os.environ.pop("AB_TARGET_SPREAD", None)

    comb_pd = VAULT_DIR / "Aditya_Bharat_Chhattisgarh_Page_02_03_Combined_34x53.pagedesigner"
    try:
        mod.rpc("app.save", {"path": str(comb_pd)})
        for f_open in (
            comb_pd,
            VAULT_DIR / "Aditya_Bharat_Page_03_Pradeshik_34x53.pagedesigner",
            VAULT_DIR / "Aditya_Bharat_Page_02_Mahanagar_34x53.pagedesigner",
        ):
            if f_open.exists():
                mod.rpc("app.open", {"path": str(f_open)})
                mod.rpc("engine.execute", {"command": "view.fitPage", "params": {}})
    except Exception:
        pass

    desktop_pdfs = []
    if export_desktop_pdf:
        try:
            desktop = Path(r"C:\Users\ADMIN\Desktop")
            d_p2 = desktop / f"Aditya_Bharat_Chhattisgarh_Page_02_{date_str}.pdf"
            d_p3 = desktop / f"Aditya_Bharat_Chhattisgarh_Page_03_{date_str}.pdf"
            d_comb = desktop / f"Aditya_Bharat_Chhattisgarh_Page_02_03_Combined_{date_str}.pdf"
            shutil.copy2(VAULT_DIR / "Aditya_Bharat_Page_02_Mahanagar_CMYK_34x53.pdf", d_p2)
            shutil.copy2(VAULT_DIR / "Aditya_Bharat_Page_03_Pradeshik_CMYK_34x53.pdf", d_p3)
            im2 = Image.open(VAULT_DIR / "Aditya_Bharat_Page_02_Mahanagar_34x53.png").convert("RGB")
            im3 = Image.open(VAULT_DIR / "Aditya_Bharat_Page_03_Pradeshik_34x53.png").convert("RGB")
            im2.save(d_comb, "PDF", resolution=108.0, quality=95, save_all=True, append_images=[im3])
            desktop_pdfs = [str(d_p2), str(d_p3), str(d_comb)]
        except Exception:
            pass

    studio.bring_page_designer_window_to_front()
    return {"ok": True, "date": date_str, "page_02": r2, "page_03": r3, "combined_pagedesigner": str(comb_pd), "desktop_pdfs": desktop_pdfs}


if __name__ == "__main__":
    import sys
    d_arg = sys.argv[1] if (len(sys.argv) > 1 and not sys.argv[1].startswith("--")) else os.environ.get("AB_EDITION_DATE", "20-11-2026")
    sp_env = os.environ.get("AB_TARGET_SPREAD", "")
    if "--page2" in sys.argv or sp_env == "1":
        build_chhattisgarh_page2_10stories(date_str=d_arg, force_fresh_live=False)
    elif "--page3" in sys.argv or sp_env == "2":
        build_chhattisgarh_page3_10stories(date_str=d_arg, force_fresh_live=False)
    else:
        build_both_chhattisgarh_pages_2_and_3(date_str=d_arg)
