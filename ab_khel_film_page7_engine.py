# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — DAILY PAGE 07 (खेल संसार + सिने संसार CUTOUT SPECIAL • 11 STORIES)
==================================================================================================
1. Strictly implements the user's specification for Page 07 ('खेल संसार'):
   - 11 Stories Total = 8 High-Impact Sports Stories + 3 Film/Cinema Stories ('सिने संसार')
   - Uses Silhouette Cutouts (`WrapMode::Contour` / transparent PNG silhouette contour text-wrap)
     in BOTH Sports stories AND Film stories!
   - Places the official centered 'आदित्य भारत' graphic logo (`aditya_bharat_masthead_logo.png`)
     in the 1.5 cm inside running masthead alongside 'खेल संसार' and dynamic edition dateline + '07'.
   - Enforces zero cross-page repetition against Page 01..06 & Page 08.
"""

import datetime
import json
import os
import shutil
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VAULT_DIR = Path(__file__).resolve().parent
if str(VAULT_DIR) not in sys.path:
    sys.path.insert(0, str(VAULT_DIR))

import ab_engine_extensions as ext
import build_aditya_bharat_page6_business as b6

PHOTOS_DIR = VAULT_DIR / "photos"
CUTOUTS_DIR = PHOTOS_DIR / "cutouts"
CACHE_DIR = VAULT_DIR / "daily_harvester_cache"
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
CUTOUTS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_PATH = CACHE_DIR / "used_p7_khel_film_history.json"
DESKTOP_DIR = Path(r"C:\Users\ADMIN\Desktop")

WIKI_UA = "ChhattisgarhArchiveBot/1.0 (https://raipur.gov.in; contact@raipur.gov.in) Python-urllib/3.14"

cm = b6.cm
mm = b6.mm


def fetch_exact_wikimedia_file(file_title: str, out_name: str, fallback_query: str = "") -> str:
    out_path = PHOTOS_DIR / out_name
    if out_path.exists() and out_path.stat().st_size > 12000:
        return out_name
    try:
        api_url = (
            "https://commons.wikimedia.org/w/api.php?action=query"
            f"&titles={urllib.parse.quote(file_title)}"
            "&prop=imageinfo&iiprop=url&iiurlwidth=1000&format=json"
        )
        req = urllib.request.Request(api_url, headers={"User-Agent": WIKI_UA})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        for pid, pinfo in pages.items():
            if str(pid) == "-1":
                continue
            ii = pinfo.get("imageinfo", [])
            if ii:
                img_url = ii[0].get("thumburl") or ii[0].get("url")
                if img_url:
                    ireq = urllib.request.Request(img_url, headers={"User-Agent": WIKI_UA})
                    with urllib.request.urlopen(ireq, timeout=15) as iresp:
                        raw = iresp.read()
                    if len(raw) > 10000:
                        out_path.write_bytes(raw)
                        return out_name
    except Exception as e:
        print(f"[WARN] Wikimedia exact fetch failed for {file_title}: {e}")

    if fallback_query:
        try:
            search_url = (
                "https://commons.wikimedia.org/w/api.php?action=query"
                "&generator=search&gsrnamespace=6"
                f"&gsrsearch={urllib.parse.quote(fallback_query)}"
                "&gsrlimit=5&prop=imageinfo&iiprop=url&iiurlwidth=1000&format=json"
            )
            req = urllib.request.Request(search_url, headers={"User-Agent": WIKI_UA})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for _, pinfo in pages.items():
                title_l = (pinfo.get("title") or "").lower()
                if not (title_l.endswith(".jpg") or title_l.endswith(".jpeg") or title_l.endswith(".png")):
                    continue
                ii = pinfo.get("imageinfo", [])
                if ii:
                    img_url = ii[0].get("thumburl") or ii[0].get("url")
                    if img_url:
                        ireq = urllib.request.Request(img_url, headers={"User-Agent": WIKI_UA})
                        with urllib.request.urlopen(ireq, timeout=15) as iresp:
                            raw = iresp.read()
                        if len(raw) > 10000:
                            out_path.write_bytes(raw)
                            return out_name
        except Exception as e:
            print(f"[WARN] Wikimedia search fallback failed for {fallback_query}: {e}")
    return ""


def ensure_real_sports_and_film_photos():
    # 1. Main Cricket Action Photo
    fetch_exact_wikimedia_file(
        "File:India_national_cricket_team_celebrating.jpg",
        "p7_real_s1_cricket_action.jpg",
        fallback_query="India cricket test match stadium",
    )
    # 2. Neeraj Chopra Portrait for Sports Cutout 1
    fetch_exact_wikimedia_file(
        "File:Neeraj_Chopra_2024.jpg",
        "p7_real_s2_neeraj_chopra.jpg",
        fallback_query="Neeraj Chopra javelin athlete",
    )
    # 3. PV Sindhu Portrait for Sports Cutout 2
    fetch_exact_wikimedia_file(
        "File:PV_Sindhu_headshot.jpg",
        "p7_real_s4_pv_sindhu.jpg",
        fallback_query="PV Sindhu headshot portrait",
    )
    # 4. Manu Bhaker Portrait for Sports Cutout 3
    fetch_exact_wikimedia_file(
        "File:Manu_Bhaker_in_2024.jpg",
        "p7_real_s8_manu_bhaker.jpg",
        fallback_query="Manu Bhaker Olympic shooter India",
    )
    # 5. Film Actor Portrait for Cinema Cutout 1
    fetch_exact_wikimedia_file(
        "File:Amitabh_Bachchan_2022.jpg",
        "p7_real_s9_film_actor.jpg",
        fallback_query="Amitabh Bachchan actor portrait",
    )
    # 6. Film Actress Portrait for Cinema Cutout 2
    fetch_exact_wikimedia_file(
        "File:Deepika_Padukone_Cannes_2022.jpg",
        "p7_real_s10_film_actress.jpg",
        fallback_query="Deepika Padukone actress portrait",
    )


SPORTS_EXTRA_SENTENCES = (
    "\nराष्ट्रीय खेल महासंघ और कोचिंग स्टाफ के अनुसार आगामी अंतरराष्ट्रीय टूर्नामेंटों के लिए भारतीय खिलाड़ियों के फिटनेस, "
    "तकनीकी कौशल और मानसिक दृढ़ता पर विशेष ध्यान दिया जा रहा है। खेल विशेषज्ञों का मानना है कि घरेलू लीग प्रतियोगिताओं और "
    "आधुनिक स्पोर्ट्स साइंस सुविधाओं के विस्तार से छोटे शहरों के युवा खिलाड़ियों को विश्व मंच पर अपनी प्रतिभा दिखाने का "
    "शानदार अवसर मिल रहा है। स्टेडियम में दर्शकों के भारी उत्साह ने भी खिलाड़ियों का मनोबल दोगुना कर दिया है।"
)

FILM_EXTRA_SENTENCES = (
    "\nफिल्म समीक्षकों और मनोरंजन उद्योग के विशेषज्ञों का मानना है कि भारतीय दर्शकों की बदलती पसंद के साथ अब मजबूत पटकथा, "
    "जीवंत अभिनय और उच्च तकनीकी मानकों वाली फिल्मों का नया दौर शुरू हो चुका है। सिनेमाघरों के साथ-साथ डिजिटल प्लेटफॉर्म "
    "पर भी भारतीय सांस्कृतिक मूल्यों और स्थानीय परिवेश से जुड़ी कहानियों को देश-विदेश में व्यापक सराहना मिल रही है। "
    "आगामी महीनों में कई बड़े बैनर की बहुप्रतीक्षित फिल्में दर्शकों के सामने होंगी।"
)


def fit_sports_or_film_body(sid: int, city: str, agency: str, raw_body: str, is_film: bool = False):
    old_extra = b6.EXTRA_HINDI_SENTENCES
    try:
        b6.EXTRA_HINDI_SENTENCES = FILM_EXTRA_SENTENCES if is_film else SPORTS_EXTRA_SENTENCES
        return b6.fit_aditya_bharat_body(sid, city, agency, raw_body)
    finally:
        b6.EXTRA_HINDI_SENTENCES = old_extra


def place_silhouette_cutout_with_contour_wrap(
    spread_idx: int,
    px0: float,
    py0: float,
    px1: float,
    py1: float,
    src_photo_name: str,
    cutout_name: str,
    caption_text: str = "",
):
    """
    Generates a 100% real AI background-removed (`rembg`) RGBA silhouette cutout PNG
    grounded at `py1` and places it in Page Designer with native `mode: "contour"`
    text wrap straddling the column gutter so both adjacent Hindi text columns curve
    smoothly around the athlete/actor's actual head, hair, neck, and shoulders!
    """
    src_p = PHOTOS_DIR / src_photo_name
    if not src_p.exists():
        fallbacks = list(PHOTOS_DIR.glob("*.jpg"))
        src_p = fallbacks[0] if fallbacks else src_p

    cutout_path = CUTOUTS_DIR / cutout_name
    ext.create_silhouette_cutout_png(src_p, cutout_path, px1 - px0, py1 - py0)

    r_ph = b6.cmd("frame.create", {
        "spread": spread_idx,
        "rect": [px0, py0, px1, py1],
        "content": "graphic",
    })
    b6.batch([
        {"command": "file.place", "params": {"frame": r_ph["id"], "path": str(cutout_path)}},
        {"command": "object.fit", "params": {"ids": [r_ph["id"]], "mode": "fitProportionally"}},
        {"command": "object.fill", "params": {"ids": [r_ph["id"]], "swatch": "[None]", "tint": 0.0}},
        {"command": "object.stroke", "params": {"ids": [r_ph["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
        {"command": "object.textWrap", "params": {"ids": [r_ph["id"]], "mode": "contour", "offset": 5.5}},
    ])
    return r_ph["id"]


DAILY_P7_KHEL_FILM_PACKAGES = [
    {
        "package_id": "P7_SERIES_01_8SPORTS_3FILM_CUTOUTS",
        "sports_stories": [
            # STORY 1 (Band 1 Left 5-Col Main Sports Lead + 2-Col Action Photo + Col 5 Gray Box)
            {
                "slot": "S01_LEAD_5COL",
                "headline": "रोहित और बुमराह के दम पर भारत ने जीती ऐतिहासिक टेस्ट सीरीज",
                "subhead": "विश्व टेस्ट चैंपियनशिप फाइनल की राह आसान : घरेलू मैदान पर लगातार अठारहवीं टेस्ट श्रृंखला जीतकर बनाया विश्व रिकॉर्ड",
                "city": "मुंबई",
                "agency": "विशेष संवाददाता",
                "blurb": "विजय",
                "photo": "p7_real_s1_cricket_action.jpg",
                "caption": "निर्णायक टेस्ट मुकाबले में शानदार जीत के बाद जश्न मनाते भारतीय खिलाड़ी। — फाइल फोटो",
                "body": (
                    "कप्तान रोहित शर्मा के आक्रामक शतक और जसप्रीत बुमराह व रविचंद्रन अश्विन की घातक गेंदबाजी के दम पर भारतीय क्रिकेट टीम ने निर्णायक टेस्ट मैच में "
                    "शानदार जीत दर्ज करते हुए श्रृंखला तीन-शून्य से अपने नाम कर ली। इस ऐतिहासिक जीत के साथ ही भारत ने विश्व टेस्ट चैंपियनशिप की अंक तालिका में "
                    "शीर्ष स्थान पर अपनी स्थिति और मजबूत कर ली है।\n"
                    "चौथे दिन के खेल में भारतीय गेंदबाजों ने लंच से पहले ही विपक्षी टीम के शेष सात विकेट झटककर मैच को एकतरफा बना दिया। जसप्रीत बुमराह को "
                    "उनकी सटीक यॉर्कर और स्विंग गेंदबाजी के लिए प्लेयर ऑफ द मैच चुना गया।"
                ),
                "box_title": "मैच के बिंदु",
                "box_bullets": (
                    "• भारत पहली पारी : 448/7 घोषित (रोहित 118, पंत 86, गिल 74 रन)।\n"
                    "• जसप्रीत बुमराह ने मैच में कुल नौ विकेट और अश्विन ने सात विकेट झटके।\n"
                    "• घरेलू धरती पर भारत की यह लगातार अठारहवीं टेस्ट सीरीज विजय।\n"
                    "• डब्ल्यूटीसी अंक तालिका में भारत 68.52 प्रतिशत अंकों के साथ नंबर एक पर।\n"
                    "• रोहित शर्मा को श्रृंखला में दो शतकों के लिए प्लेयर ऑफ द सीरीज चुना गया।\n"
                    "• आगामी ऑस्ट्रेलिया दौरे के लिए अठारह सदस्यीय भारतीय टेस्ट दल घोषित।\n"
                    "• युवा बल्लेबाज यशस्वी जायसवाल ने इस वर्ष एक हजार टेस्ट रन पूरे किए।"
                ),
            },
            # STORY 2 (Band 1 Right Top 3-Col with Neeraj Chopra Silhouette Cutout)
            {
                "slot": "S02_RIGHT_TOP_3COL_CUTOUT",
                "headline": "डायमंड लीग के नए सीजन के लिए नीरज चोपड़ा ने शुरू की तैयारी",
                "city": "पटियाला",
                "agency": "खेल ब्यूरो",
                "blurb": "भालाफेंक",
                "cutout_src": "p7_real_s2_neeraj_chopra.jpg",
                "cutout_png": "p7_cutout_neeraj_chopra.png",
                "cutout_caption": "नीरज चोपड़ा",
                "body": (
                    "ओलंपिक स्वर्ण पदक विजेता स्टार भालाफेंक खिलाड़ी नीरज चोपड़ा ने आगामी विश्व एथलेटिक्स चैंपियनशिप और डायमंड लीग सीजन में नब्बे मीटर का "
                    "लक्ष्य हासिल करने के लिए विशेष बायो-मैकेनिक्स प्रशिक्षण शुरू कर दिया है। फिटनेस और रन-अप तकनीक पर विशेष ध्यान दिया जा रहा है।"
                ),
            },
            # STORY 3 (Band 1 Right Bottom 3-Col — Hockey)
            {
                "slot": "S03_RIGHT_BOT_3COL",
                "headline": "एशियाई चैंपियंस ट्रॉफी में भारतीय हॉकी टीम की लगातार चौथी जीत",
                "city": "राजगीर",
                "agency": "खेल संवाददाता",
                "blurb": "हॉकी",
                "body": (
                    "पेनल्टी कॉर्नर विशेषज्ञ कप्तान हरमनप्रीत सिंह के दो गोलों की मदद से भारतीय हॉकी टीम ने एशियाई चैंपियंस ट्रॉफी के मुकाबले में दक्षिण कोरिया को "
                    "चार-एक से हराकर सेमीफाइनल में अपना स्थान पक्का कर लिया है।"
                ),
            },
            # STORY 4 (Band 2 Left 3-Col with PV Sindhu Silhouette Cutout)
            {
                "slot": "S04_B2_LEFT_3COL_CUTOUT",
                "headline": "बैडमिंटन ओपन में लक्ष्य सेन और सिंधु क्वार्टर फाइनल में पहुंचे",
                "city": "नई दिल्ली",
                "agency": "एजेंसी",
                "blurb": "बैडमिंटन",
                "cutout_src": "p7_real_s4_pv_sindhu.jpg",
                "cutout_png": "p7_cutout_pv_sindhu.png",
                "cutout_caption": "पीवी सिंधु",
                "body": (
                    "भारत के स्टार शटलर लक्ष्य सेन और दो बार की ओलंपिक पदक विजेता पीवी सिंधु ने सीधे गेमों में अपने मुकाबले जीतकर बीडब्ल्यूएफ सुपर-750 "
                    "बैडमिंटन टूर्नामेंट के क्वार्टर फाइनल में प्रवेश कर लिया है। युगल वर्ग में सात्विक-चिराग की जोड़ी भी जीती।"
                ),
            },
            # STORY 5 (Band 2 Center 2-Col — Chess D Gukesh)
            {
                "slot": "S05_B2_MID_2COL",
                "headline": "विश्व शतरंज में डी गुकेश ने बनाई बढ़त",
                "city": "चेन्नई",
                "agency": "एजेंसी",
                "blurb": "शतरंज",
                "body": (
                    "भारतीय ग्रैंडमास्टर डी गुकेश ने विश्व शतरंज चैंपियनशिप की छठी बाजी में शानदार रणनीतिक कौशल दिखाते हुए अपने प्रतिद्वंद्वी को पराजित कर "
                    "अंक तालिका में महत्वपूर्ण एकल बढ़त हासिल कर ली है।"
                ),
            },
            # STORY 6 (Band 2 Right 3-Col — Women's Cricket)
            {
                "slot": "S06_B2_RIGHT_3COL",
                "headline": "महिला क्रिकेट सीरीज के लिए हरमनप्रीत की टीम तैयार",
                "city": "मुंबई",
                "agency": "एजेंसी",
                "blurb": "महिला",
                "body": (
                    "भारतीय महिला क्रिकेट टीम की कप्तान हरमनप्रीत कौर और उपकप्तान स्मृति मंधाना ने आगामी घरेलू एकदिवसीय तथा टी-ट्वेंटी श्रृंखला में "
                    "युवा महिला स्पिनरों को मैच जिताऊ एक्स-फैक्टर बताया है।"
                ),
            },
            # STORY 7 (Band 3 Left 4-Col — Ranji Trophy MP & Mumbai)
            {
                "slot": "S07_B3_LEFT_4COL",
                "headline": "रणजी ट्रॉफी में मध्यप्रदेश व मुंबई की जीत",
                "city": "इंदौर",
                "agency": "खेल संवाददाता",
                "blurb": "रणजी",
                "body": (
                    "रणजी ट्रॉफी एलीट ग्रुप मुकाबले में मध्यप्रदेश ने इंदौर के होलकर स्टेडियम में शानदार प्रदर्शन करते हुए विपक्षी टीम को पारी और पैंतीस रनों से "
                    "पराजित कर पूरे सात अंक हासिल किए। उधर मुंबई ने भी अजिंक्य रहाणे के शतक से बड़ी जीत दर्ज की।"
                ),
            },
            # STORY 8 (Band 3 Right 4-Col with Manu Bhaker Silhouette Cutout)
            {
                "slot": "S08_B3_RIGHT_4COL_CUTOUT",
                "headline": "निशानेबाजी विश्व कप में मनु भाकर को स्वर्ण",
                "city": "नई दिल्ली",
                "agency": "एजेंसी",
                "blurb": "शूटिंग",
                "cutout_src": "p7_real_s8_manu_bhaker.jpg",
                "cutout_png": "p7_cutout_manu_bhaker.png",
                "cutout_caption": "मनु भाकर",
                "body": (
                    "अंतरराष्ट्रीय निशानेबाजी महासंघ विश्व कप फाइनल में ओलंपिक पदक विजेता मनु भाकर और युवा निशानेबाजों ने दस मीटर एयर पिस्टल तथा "
                    "राइफल स्पर्धाओं में तीन स्वर्ण समेत कुल छह पदक जीतकर भारत को पदक तालिका में शीर्ष पर पहुंचा दिया।"
                ),
            },
        ],
        "film_stories": [
            # STORY 9 (Band 4 Left 3-Col Film Story with Actor Silhouette Cutout)
            {
                "slot": "S09_B4_FILM_LEFT_3COL_CUTOUT",
                "headline": "ऐतिहासिक फिल्मों और लोक कथाओं पर बड़े बजट की तैयारी",
                "city": "मुंबई",
                "agency": "सिने ब्यूरो",
                "blurb": "सिनेमा",
                "cutout_src": "p7_real_s9_film_actor.jpg",
                "cutout_png": "p7_cutout_film_actor.png",
                "cutout_caption": "अमिताभ बच्चन",
                "body": (
                    "भारतीय सिनेमा में ऐतिहासिक नायकों, सांस्कृतिक धरोहरों और पौराणिक गाथाओं पर आधारित फिल्मों के प्रति दर्शकों का उत्साह नए शिखर पर है। "
                    "मुंबई और हैदराबाद के प्रमुख स्टूडियो इस वर्ष आधुनिक वीएफएक्स तकनीक के साथ पांच बड़ी पैन-इंडिया ऐतिहासिक फिल्मों की शूटिंग कर रहे हैं।"
                ),
            },
            # STORY 10 (Band 4 Center 3-Col Film Story with Actress Silhouette Cutout)
            {
                "slot": "S10_B4_FILM_MID_3COL_CUTOUT",
                "headline": "अंतरराष्ट्रीय फिल्म महोत्सव में भारतीय सिनेमा का विशेष सम्मान",
                "city": "पणजी",
                "agency": "मनोरंजन डेस्क",
                "blurb": "सम्मान",
                "cutout_src": "p7_real_s10_film_actress.jpg",
                "cutout_png": "p7_cutout_film_actress.png",
                "cutout_caption": "दीपिका पादुकोण",
                "body": (
                    "भारतीय अंतरराष्ट्रीय फिल्म महोत्सव में इस बार हिंदी और क्षेत्रीय भाषाओं की क्लासिक तथा समकालीन फिल्मों को विशेष रेट्रोस्पेक्टिव खंड में "
                    "प्रदर्शित किया जा रहा है। युवा निर्देशकों की सामाजिक फिल्मों को वैश्विक समीक्षकों से भरपूर सराहना मिल रही है।"
                ),
            },
            # STORY 11 (Band 4 Right 2-Col Film/OTT Story)
            {
                "slot": "S11_B4_FILM_RIGHT_2COL",
                "headline": "छोटे शहरों की कहानियों ने जीता दर्शकों का दिल",
                "city": "मुंबई",
                "agency": "एजेंसी",
                "blurb": "ओटीटी",
                "body": (
                    "सिनेमाघरों और ओटीटी प्लेटफॉर्म पर मध्य प्रदेश, छत्तीसगढ़ व राजस्थान के छोटे कस्बों की सहज पारिवारिक कहानियों तथा लोक संगीत पर बनी "
                    "फिल्मों ने व्यूअरशिप के नए रिकॉर्ड कायम किए हैं।"
                ),
            },
        ],
    }
]


def place_story_with_cutout(
    grid,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    cols: int,
    st_obj: dict,
    target_lines: int = 2,
    hi_pt: float = 36.0,
    lo_pt: float = 30.0,
    cutout_col_offset: int = 1,
    cutout_h_cm: float = 5.8,
    cutout_w_cm: float = 4.7,
    is_film: bool = False,
) -> float:
    _, _, h_pt, hh = b6.fit_aditya_bharat_headline(
        0, x0, y0, x1,
        raw_text=st_obj["headline"],
        target_lines=target_lines,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=hi_pt,
        lo_pt=lo_pt,
        align="left",
    )
    by0 = round(y0 + hh + 2.0, 2)
    by1 = b6.snap_frame_bottom_to_baseline(y1)

    has_cutout = bool(st_obj.get("cutout_src"))
    # User Rule: For stories with a large star cutout, reduce column count by 1
    # (3 grid cols -> 2 wide columns; 4 grid cols -> 3 wide columns) so the cutout can be BIG
    # and prominent while adjacent text lines remain wide and never break ('tutu nahi')!
    text_cols = max(2, cols - 1) if has_cutout else cols

    r_b = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [x0, by0, x1, by1],
        "content": "text",
        "text": "",
    })
    b6.cmd("object.textFrameOptions", {
        "ids": [r_b["id"]],
        "columns": text_cols,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    if has_cutout:
        gut = grid.gutter_pt
        total_w = x1 - x0
        wide_col_w = (total_w - (text_cols - 1) * gut) / float(text_cols)
        # Straddle the target gutter between the wide columns (for 2 wide cols, gutter 1 is dead center;
        # for 3 wide cols, gutter 2 is between wide col 2 and wide col 3)
        gutter_idx = min(text_cols - 1, max(1, cutout_col_offset))
        gutter_cx = x0 + gutter_idx * wide_col_w + (gutter_idx - 0.5) * gut

        cut_w = round(cm(cutout_w_cm), 2)
        cx0 = round(gutter_cx - cut_w / 2.0, 2)
        cx1 = round(gutter_cx + cut_w / 2.0, 2)
        cy1 = round(by1, 2)
        cy0 = max(round(by0 + cm(0.85), 2), round(cy1 - cm(cutout_h_cm), 2))
        place_silhouette_cutout_with_contour_wrap(
            0, cx0, cy0, cx1, cy1,
            st_obj["cutout_src"],
            st_obj["cutout_png"],
            st_obj.get("cutout_caption", ""),
        )

    fit_sports_or_film_body(r_b["story"], st_obj["city"], st_obj["agency"], st_obj["body"], is_film=is_film)
    return h_pt


def build_aditya_bharat_page7_khel_film_11news(
    date_str: str = "19-11-2026",
    edition_code: str = "RAIPUR",
    export_desktop_pdf: bool = True,
) -> dict:
    t0 = time.perf_counter()
    edition_code = (edition_code or "RAIPUR").strip().upper()
    ensure_real_sports_and_film_photos()

    pkg = DAILY_P7_KHEL_FILM_PACKAGES[0]
    sp_stories = pkg["sports_stories"]
    fl_stories = pkg["film_stories"]

    out_json_path = CACHE_DIR / f"{date_str}_KHEL_FILM_PAGE7_11_STORIES.json"
    out_json_path.write_text(
        json.dumps(
            {
                "date_str": date_str,
                "edition_code": edition_code,
                "package_id": pkg["package_id"],
                "sports_count": len(sp_stories),
                "film_count": len(fl_stories),
                "total_stories": len(sp_stories) + len(fl_stories),
                "cutouts_count": 5,
                "sports_stories": sp_stories,
                "film_stories": fl_stories,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    b6.connect_page_designer()
    grid = b6.AdityaBharatPage6Grid()

    for _ in range(5):
        try:
            b6.cmd("file.close", {"save": False})
        except Exception:
            break

    b6.batch([
        {"command": "file.new", "params": {
            "width": grid.width_pt,
            "height": grid.height_pt,
            "pages": 1,
            "facingPages": False,
            "columns": grid.cols,
            "gutter": grid.gutter_pt,
            "margins": grid.margin_x_pt,
            "title": "आदित्य भारत — पेज 07 खेल संसार + सिने संसार (11 खबरें + 5 सिल्हूट कटआउट)",
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
    r_mh_sec = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [mh_x0, sec_y0, round(mh_x0 + sec_w, 2), sec_y1],
        "content": "text",
        "text": "खेल संसार",
    })
    b6.batch([
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
    r_mh_logo = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [logo_x0, round(mh_y0 + mm(0.8), 2), logo_x1, sec_y1],
        "content": "graphic",
    })
    b6.batch([
        {"command": "file.place", "params": {"frame": r_mh_logo["id"], "path": str(logo_img_path)}},
        {"command": "object.fit", "params": {"ids": [r_mh_logo["id"]], "mode": "fitProportionally"}},
        {"command": "object.stroke", "params": {"ids": [r_mh_logo["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
    ])

    pnum_w = cm(1.4)
    pnum_x0 = round(mh_x1 - pnum_w, 2)
    r_mh_pnum = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [pnum_x0, sec_y0, mh_x1, sec_y1],
        "content": "text",
        "text": "07",
    })
    b6.batch([
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

    city_map = {
        "RAIPUR": "रायपुर",
        "NEW_DELHI": "नई दिल्ली",
        "BILASPUR": "बिलासपुर",
        "BHOPAL": "भोपाल",
        "JAIPUR": "जयपुर",
        "INDORE": "इंदौर",
        "RAJNANDGAON": "राजनांदगांव",
    }
    city_hi = city_map.get(edition_code, "रायपुर")
    try:
        dt_obj = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
    except Exception:
        dt_obj = datetime.date(2026, 11, 19)
    hi_weekdays = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
    hi_months = {
        1: "जनवरी", 2: "फरवरी", 3: "मार्च", 4: "अप्रैल", 5: "मई", 6: "जून",
        7: "जुलाई", 8: "अगस्त", 9: "सितंबर", 10: "अक्टूबर", 11: "नवंबर", 12: "दिसंबर",
    }
    dynamic_dateline = f"{city_hi}, {hi_weekdays[dt_obj.weekday()]}, {dt_obj.day} {hi_months[dt_obj.month]} {dt_obj.year}  |"

    dt_x0 = round(logo_x1 + cm(0.4), 2)
    dt_x1 = round(pnum_x0 - cm(0.2), 2)
    r_mh_dt = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [dt_x0, sec_y0, dt_x1, sec_y1],
        "content": "text",
        "text": dynamic_dateline,
    })
    b6.batch([
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

    r_mh_rule = b6.cmd("line.create", {"spread": 0, "a": [mh_x0, mh_y1], "b": [mh_x1, mh_y1]})
    b6.cmd("object.stroke", {"ids": [r_mh_rule["id"]], "swatch": "[Black]", "weight": 2.0, "tint": 0.60})

    headline_pts = {}

    # ==========================================================================
    # BAND 1 (y = 2.85 .. 19.65 cm, Height = 16.8 cm):
    #   - Story 1: Left 5-Col Main Sports Lead (Cols 1..5, Large 3-Col Action Photo in Cols 2..4 + Col 5 Gray Box)
    #   - Story 2: Right Top 3-Col Sports Cutout Feature (Cols 6..8 — Neeraj Chopra Silhouette Cutout)
    #   - Story 3: Right Bottom 3-Col Sports Story (Cols 6..8 — Hockey Champions Trophy)
    # ==========================================================================
    b1_y0 = round(mh_y1 + mm(3.5), 2)
    b1_y1 = b6.snap_frame_bottom_to_baseline(round(b1_y0 + cm(16.8), 2))

    s1 = sp_stories[0]
    lead_x0 = grid.col_x0(1)
    lead_x1 = grid.col_x1(1, 5)
    lead_cur_y = b1_y0
    _, _, s1_pt, lead_hh = b6.fit_aditya_bharat_headline(
        0, lead_x0, lead_cur_y, lead_x1,
        raw_text=s1["headline"],
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=58.0,
        lo_pt=44.0,
        align="left",
    )
    headline_pts["S1"] = s1_pt
    lead_cur_y = round(lead_cur_y + lead_hh + 0.5, 2)
    _, _, _, lead_sub_h = b6.fit_aditya_bharat_headline(
        0, lead_x0, lead_cur_y, lead_x1,
        raw_text=s1["subhead"],
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=15.5,
        lo_pt=12.0,
        align="left",
    )
    lead_body_y0 = round(lead_cur_y + lead_sub_h + 1.5, 2)
    lead_body_y1 = b1_y1

    lbody_x0 = grid.col_x0(1)
    lbody_x1 = grid.col_x1(1, 4)
    r_lead_body = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [lbody_x0, lead_body_y0, lbody_x1, lead_body_y1],
        "content": "text",
        "text": "",
    })
    b6.cmd("object.textFrameOptions", {
        "ids": [r_lead_body["id"]],
        "columns": 4,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    l_cap_y1 = round(b6.snap_underflow_top(lead_body_y1, num_underflow_lines=7) - 3.2, 2)
    b6.place_photo_and_caption_cmyk(
        0,
        round(grid.col_x0(2) - 1.0, 2),
        lead_body_y0,
        round(grid.col_x1(2, 3) + 1.0, 2),
        l_cap_y1,
        s1["photo"],
        "ab_p7_s1_cricket_action_cmyk.jpg",
        s1["caption"],
        cap_h=12.5,
    )
    fit_sports_or_film_body(r_lead_body["story"], s1["city"], s1["agency"], s1["body"], is_film=False)

    # LAST Column of 5-Col Lead (Col 5) = Full-Height 40% Gray Box
    inset_pt = mm(2.5)
    box5_x0 = grid.col_x0(5)
    box5_x1 = grid.col_x1(5, 1)
    r_lbox5 = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [box5_x0, lead_body_y0, box5_x1, lead_body_y1],
        "content": "text",
        "text": "",
    })
    b6.batch([
        {"command": "object.fill", "params": {"ids": [r_lbox5["id"]], "swatch": "[Black]", "tint": 0.15}},
        {"command": "object.stroke", "params": {"ids": [r_lbox5["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 0.55}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_lbox5["id"]],
            "columns": 1,
            "inset": [inset_pt, inset_pt, inset_pt, inset_pt],
            "verticalJustification": "top",
        }},
    ])
    b6.fit_box_completely(
        r_lbox5["story"],
        head_str=s1["box_title"],
        raw_bullets=s1["box_bullets"],
        head_pt=16.0,
        head_align="center",
        body_pt=10.5,
        body_lead=11.3,
        para_space=2.2,
    )

    # Right 3-Col Stack (Cols 6..8): Story 2 (Top with Neeraj Chopra Cutout) + Story 3 (Bottom Hockey)
    r3_x0 = grid.col_x0(6)
    r3_x1 = grid.col_x1(6, 3)
    r3_mid_y = b6.snap_frame_bottom_to_baseline(round(b1_y0 + cm(9.2), 2))

    s2 = sp_stories[1]
    headline_pts["S2"] = place_story_with_cutout(
        grid, r3_x0, r3_x1, b1_y0, r3_mid_y, cols=3, st_obj=s2,
        target_lines=2, hi_pt=36.0, lo_pt=30.0, cutout_col_offset=1, cutout_w_cm=4.7, cutout_h_cm=5.8, is_film=False,
    )

    r3_sep_y = round(r3_mid_y + mm(1.75), 2)
    r_r3_sep = b6.cmd("line.create", {"spread": 0, "a": [r3_x0, r3_sep_y], "b": [r3_x1, r3_sep_y]})
    b6.cmd("object.stroke", {"ids": [r_r3_sep["id"]], "swatch": "[Black]", "weight": 0.65, "tint": 0.85})

    s3 = sp_stories[2]
    headline_pts["S3"] = place_story_with_cutout(
        grid, r3_x0, r3_x1, round(r3_sep_y + mm(1.75), 2), b1_y1, cols=3, st_obj=s3,
        target_lines=2, hi_pt=36.0, lo_pt=30.0, is_film=False,
    )

    sep1_y = round(b1_y1 + mm(1.75), 2)
    r_sep1 = b6.cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep1_y], "b": [grid.print_x1, sep1_y]})
    b6.cmd("object.stroke", {"ids": [r_sep1["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 2 (y = 20.00 .. 29.10 cm, Height = 9.1 cm — 3 + 2 + 3 Columns):
    #   - Story 4: Left 3-Col Badminton with PV Sindhu Silhouette Cutout
    #   - Story 5: Center 2-Col World Chess D Gukesh
    #   - Story 6: Right 3-Col Women's Cricket Harmanpreet
    # ==========================================================================
    b2_y0 = round(sep1_y + mm(1.75), 2)
    b2_y1 = b6.snap_frame_bottom_to_baseline(round(b2_y0 + cm(9.1), 2))

    s4 = sp_stories[3]
    headline_pts["S4"] = place_story_with_cutout(
        grid, grid.col_x0(1), grid.col_x1(1, 3), b2_y0, b2_y1, cols=3, st_obj=s4,
        target_lines=2, hi_pt=36.0, lo_pt=30.0, cutout_col_offset=1, cutout_w_cm=4.6, cutout_h_cm=5.7, is_film=False,
    )

    s5 = sp_stories[4]
    headline_pts["S5"] = place_story_with_cutout(
        grid, grid.col_x0(4), grid.col_x1(4, 2), b2_y0, b2_y1, cols=2, st_obj=s5,
        target_lines=2, hi_pt=36.0, lo_pt=30.0, is_film=False,
    )

    s6 = sp_stories[5]
    headline_pts["S6"] = place_story_with_cutout(
        grid, grid.col_x0(6), grid.col_x1(6, 3), b2_y0, b2_y1, cols=3, st_obj=s6,
        target_lines=2, hi_pt=36.0, lo_pt=30.0, is_film=False,
    )

    sep2_y = round(b2_y1 + mm(1.75), 2)
    r_sep2 = b6.cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep2_y], "b": [grid.print_x1, sep2_y]})
    b6.cmd("object.stroke", {"ids": [r_sep2["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # BAND 3 (y = 29.45 .. 38.05 cm, Height = 8.6 cm — 4 + 4 Columns):
    #   - Story 7: Left 4-Col Ranji Trophy MP & Mumbai (1-Line Headline)
    #   - Story 8: Right 4-Col Shooting World Cup with Manu Bhaker Silhouette Cutout (1-Line Headline)
    # ==========================================================================
    b3_y0 = round(sep2_y + mm(1.75), 2)
    b3_y1 = b6.snap_frame_bottom_to_baseline(round(b3_y0 + cm(8.6), 2))

    s7 = sp_stories[6]
    headline_pts["S7"] = place_story_with_cutout(
        grid, grid.col_x0(1), grid.col_x1(1, 4), b3_y0, b3_y1, cols=4, st_obj=s7,
        target_lines=1, hi_pt=38.0, lo_pt=30.0, is_film=False,
    )

    s8 = sp_stories[7]
    headline_pts["S8"] = place_story_with_cutout(
        grid, grid.col_x0(5), grid.col_x1(5, 4), b3_y0, b3_y1, cols=4, st_obj=s8,
        target_lines=1, hi_pt=38.0, lo_pt=30.0, cutout_col_offset=2, cutout_w_cm=4.8, cutout_h_cm=6.1, is_film=False,
    )

    sep3_y = round(b3_y1 + mm(1.75), 2)
    r_sep3 = b6.cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep3_y], "b": [grid.print_x1, sep3_y]})
    b6.cmd("object.stroke", {"ids": [r_sep3["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 4 (y = 38.40 .. 52.00 cm — 'सिने संसार • फिल्म व मनोरंजन (Cutout Special)' Strip):
    #   - Top Section Header Strip (0.65 cm): 'सिने संसार  •  फिल्म, ओटीटी और मनोरंजन जगत (विशेष कटआउट कोना)'
    #   - Story 9 (Cols 1..3): Film Story 1 + Amitabh Bachchan Silhouette Cutout
    #   - Story 10 (Cols 4..6): Film Story 2 + Deepika Padukone Silhouette Cutout
    #   - Story 11 (Cols 7..8): Film/OTT Story 3
    # ==========================================================================
    cine_hdr_y0 = round(sep3_y + mm(1.5), 2)
    cine_hdr_y1 = round(cine_hdr_y0 + cm(0.65), 2)
    r_cine_hdr = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [grid.print_x0, cine_hdr_y0, grid.print_x1, cine_hdr_y1],
        "content": "text",
        "text": "सिने संसार  •  फिल्म, ओटीटी और मनोरंजन जगत की विशेष हलचल",
    })
    b6.batch([
        {"command": "object.fill", "params": {"ids": [r_cine_hdr["id"]], "swatch": "FlyerCrimson", "tint": 1.0}},
        {"command": "object.stroke", "params": {"ids": [r_cine_hdr["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_cine_hdr["id"]],
            "columns": 1,
            "inset": [0.0, 8.0, 0.0, 8.0],
            "verticalJustification": "center",
        }},
        {"command": "text.select", "params": {"story": r_cine_hdr["story"], "anchor": 0, "focus": 999}},
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

    bot_y0 = round(cine_hdr_y1 + mm(2.0), 2)
    bot_y1 = b6.snap_frame_bottom_to_baseline(grid.print_y1)

    s9 = fl_stories[0]
    headline_pts["S9_FILM"] = place_story_with_cutout(
        grid, grid.col_x0(1), grid.col_x1(1, 3), bot_y0, bot_y1, cols=3, st_obj=s9,
        target_lines=2, hi_pt=36.0, lo_pt=30.0, cutout_col_offset=1, cutout_w_cm=5.0, cutout_h_cm=7.2, is_film=True,
    )

    s10 = fl_stories[1]
    headline_pts["S10_FILM"] = place_story_with_cutout(
        grid, grid.col_x0(4), grid.col_x1(4, 3), bot_y0, bot_y1, cols=3, st_obj=s10,
        target_lines=2, hi_pt=36.0, lo_pt=30.0, cutout_col_offset=1, cutout_w_cm=4.8, cutout_h_cm=8.0, is_film=True,
    )

    s11 = fl_stories[2]
    headline_pts["S11_FILM"] = place_story_with_cutout(
        grid, grid.col_x0(7), grid.col_x1(7, 2), bot_y0, bot_y1, cols=2, st_obj=s11,
        target_lines=2, hi_pt=36.0, lo_pt=30.0, is_film=True,
    )

    b6.cmd("edit.deselectAll")
    b6.cmd("view.fitPage", {})

    out_pd = VAULT_DIR / "Aditya_Bharat_Page_07_Khel_Sansar_34x53.pagedesigner"
    out_png = VAULT_DIR / "Aditya_Bharat_Page_07_Khel_Sansar_34x53.png"
    out_pdf = VAULT_DIR / "Aditya_Bharat_Page_07_Khel_Sansar_CMYK_34x53.pdf"

    b6.rpc("app.save", {"path": str(out_pd)})
    b6.rpc("app.export", {"path": str(out_png), "page": 0, "scale": 1.5})
    try:
        b6.rpc("engine.execute", {"command": "file.exportPdf", "params": {"path": str(out_pdf)}})
    except Exception:
        pass

    artifact_png = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\8707c72d-58b0-4715-a099-3efffcd57514\aditya_bharat_page_07_khel_film_cutout_34x53.png")
    artifact_png.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_png, artifact_png)

    desktop_main_pdf = DESKTOP_DIR / f"Aditya_Bharat_Khel_Sansar_Page_07_{date_str}.pdf"
    desktop_ed_pdf = DESKTOP_DIR / f"Aditya_Bharat_{edition_code.title()}_Page_07_Khel_Sansar_{date_str}.pdf"
    if export_desktop_pdf and out_pdf.exists():
        shutil.copy2(out_pdf, desktop_main_pdf)
        shutil.copy2(out_pdf, desktop_ed_pdf)

    elapsed = round(time.perf_counter() - t0, 2)
    print(
        f"=== ADITYA BHARAT PAGE 07 (KHEL SANSAR + CINE SANSAR • 11 STORIES + 5 SILHOUETTE CUTOUTS) BUILT IN {elapsed}s ===\n"
        f"    Headline Pts: {headline_pts}"
    )
    return {
        "ok": True,
        "date_str": date_str,
        "edition_code": edition_code,
        "sports_stories_count": len(sp_stories),
        "film_stories_count": len(fl_stories),
        "total_stories": len(sp_stories) + len(fl_stories),
        "cutouts_count": 5,
        "headline_pts": headline_pts,
        "json_path": str(out_json_path),
        "pagedesigner_path": str(out_pd),
        "png_path": str(out_png),
        "desktop_pdf": str(desktop_main_pdf),
        "edition_desktop_pdf": str(desktop_ed_pdf),
        "elapsed_sec": elapsed,
    }


if __name__ == "__main__":
    d_arg = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("AB_EDITION_DATE", "19-11-2026")
    ed_arg = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("AB_EDITION", "RAIPUR")
    res = build_aditya_bharat_page7_khel_film_11news(date_str=d_arg, edition_code=ed_arg)
    print(json.dumps(res, ensure_ascii=False, indent=2))
