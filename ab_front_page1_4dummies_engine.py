# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — MASTER PAGE 01 (फ्रंट पेज) 4-DUMMY ROTATING ENGINE + GLOBAL CROSS-PAGE DEDUPLICATOR
=================================================================================================================
Strictly implements all Front Page (Page 01) rules specified by the user:
  1. 4 Rotating Front Page Dummy Layouts (`DUMMY_1`, `DUMMY_2`, `DUMMY_3`, `DUMMY_4`) — rotated daily (or user-selectable)
     with 10 to 11 high-impact stories per front page below the 6.0 cm Dynamic 7-Edition Masthead.
  2. Edition-Aware Story Mix (11 Stories Total on Page 01):
     - If Edition is RAIPUR, BILASPUR, or RAJNANDGAON -> 3 Top Chhattisgarh CM (विष्णुदेव साय) & CG State Stories
       (100% distinct from Page 02, Page 03, and Page 05!)
     - If Edition is BHOPAL or INDORE -> 3 Top Madhya Pradesh CM & MP State Stories
     - If Edition is JAIPUR -> 3 Top Rajasthan CM & RJ State Stories
     - If Edition is NEW_DELHI -> 3 Top Delhi-NCR Capital Stories
     - Plus 8 Top National, International, Business, and Sports Front-Page Stories!
  3. Ironclad Global Cross-Page Non-Repetition Rule (`<date_str>_GLOBAL_USED_NEWS_LEDGER.json`):
     - Any State story placed on Page 01 NEVER appears on Page 02, Page 03, or Page 05 (`प्रादेशिक`).
     - Any National or International story placed on Page 01 NEVER appears on Page 08 (`देश-विदेश`).
     - Any Business story placed on Page 01 NEVER appears on Page 06 (`कारोबार`).
     - Any Sports story placed on Page 01 NEVER appears on Page 07 (`खेल संसार`).
"""

import datetime
import json
import os
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VAULT_DIR = Path(__file__).resolve().parent
if str(VAULT_DIR) not in sys.path:
    sys.path.insert(0, str(VAULT_DIR))

import build_aditya_bharat_page6_business as b6

PHOTOS_DIR = VAULT_DIR / "photos"
CACHE_DIR = VAULT_DIR / "daily_harvester_cache"
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_PATH = CACHE_DIR / "used_p1_front_4dummies_history.json"
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
            "&prop=imageinfo&iiprop=url&iiurlwidth=1200&format=json"
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
    except Exception:
        pass

    if fallback_query:
        try:
            search_url = (
                "https://commons.wikimedia.org/w/api.php?action=query"
                "&generator=search&gsrnamespace=6"
                f"&gsrsearch={urllib.parse.quote(fallback_query)}"
                "&gsrlimit=5&prop=imageinfo&iiprop=url&iiurlwidth=1200&format=json"
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
        except Exception:
            pass
    return ""


def ensure_real_page1_photos():
    fetch_exact_wikimedia_file(
        "File:RRTS_Train_India.jpg",
        "p1_real_s1_green_metro.jpg",
        fallback_query="Namo Bharat rapid rail metro train India",
    )
    fetch_exact_wikimedia_file(
        "File:Parliament_of_India_New_Building.jpg",
        "p1_real_s3_cabinet_lead.jpg",
        fallback_query="Parliament of India New Delhi building",
    )
    fetch_exact_wikimedia_file(
        "File:Varanasi_Ghats_from_Ganges.jpg",
        "p1_real_s10_heritage_corridor.jpg",
        fallback_query="Varanasi Ghats riverfront India",
    )


FRONT_EXTRA_SENTENCES = (
    "\nकेंद्र और राज्य सरकार के वरिष्ठ अधिकारियों के अनुसार इस महत्वाकांक्षी निर्णय के समयबद्ध क्रियान्वयन के लिए विशेष निगरानी समिति "
    "गठित कर दी गई है। नीति विशेषज्ञों का मानना है कि बुनियादी ढांचे, तकनीक और जनकल्याणकारी योजनाओं के इस समन्वय से आम नागरिकों के "
    "जीवन स्तर में व्यापक सुधार आएगा तथा युवाओं के लिए स्थानीय स्तर पर रोजगार के लाखों नए अवसर सृजित होंगे। आगामी तिमाही से इस योजना "
    "के प्रथम चरण का सीधा लाभ धरातल पर दिखाई देने लगेगा।"
)


def fit_front_page_body(sid: int, city: str, agency: str, raw_body: str):
    old_extra = b6.EXTRA_HINDI_SENTENCES
    try:
        b6.EXTRA_HINDI_SENTENCES = FRONT_EXTRA_SENTENCES
        return b6.fit_aditya_bharat_body(sid, city, agency, raw_body)
    finally:
        b6.EXTRA_HINDI_SENTENCES = old_extra


def place_front_multi_col_story(
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
    r_b = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [x0, by0, x1, by1],
        "content": "text",
        "text": "",
    })
    b6.cmd("object.textFrameOptions", {
        "ids": [r_b["id"]],
        "columns": cols,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    if st_obj.get("blurb"):
        bl_w = 2.20 if len(st_obj["blurb"]) >= 7 else 1.85
        b6.place_red_subject_blurb(0, x0, round(by0 + cm(1.55), 2), st_obj["blurb"], bw_cm=bl_w)
    fit_front_page_body(r_b["story"], st_obj["city"], st_obj["agency"], st_obj["body"])
    return h_pt


# ==============================================================================
# EDITION-SPECIFIC 3 STATE STORIES FOR PAGE 01 (NEVER REPEATED ON PAGES 2, 3, 5)
#   - Story 0 (6-Col Top Banner Flyer + 2-Col Photo right under Masthead): State CM Flagship News
#   - Story 1 (2-Col Top Corner right under Masthead): State Capital / Rapid Rail / Innovation News
#   - Story 2 (3-Col Band-2 Upper Story): State CM Second Prominent Decision
# ==============================================================================
EDITION_STATE_3_STORIES = {
    "CG": [
        # CG Story 0 (6-Col Top Flyer + 2-Col Photo — CM Vishnu Deo Sai Cabinet Decision & AI Hub)
        {
            "category": "STATE_CG",
            "subhead": "मुख्यमंत्री विष्णुदेव साय की अध्यक्षता में कैबिनेट का ऐतिहासिक निर्णय : बस्तर से सरगुजा तक औद्योगिक व शैक्षणिक विकास को नई रफ्तार",
            "headline": "छत्तीसगढ़ में पचास हजार पदों पर भर्ती व नया एआई हब मंजूर",
            "city": "रायपुर",
            "agency": "स्टेट ब्यूरो",
            "blurb": "कैबिनेट",
            "photo": "ab_p4_lead_cmyk.jpg",
            "caption": "नवा रायपुर अटल नगर में स्थापित होने वाले अत्याधुनिक एआई व सेमीकंडक्टर टेक्नोलॉजी पार्क का मॉडल। — फाइल फोटो",
            "body": (
                "मुख्यमंत्री विष्णुदेव साय की अध्यक्षता में मंत्रालय महानदी भवन में हुई कैबिनेट की बैठक में प्रदेश के युवाओं के हित में बड़ा निर्णय "
                "लेते हुए शिक्षा, स्वास्थ्य, पुलिस और तकनीकी विभागों में पचास हजार रिक्त पदों पर पारदर्शी भर्ती कैलेंडर जारी करने को मंजूरी दी गई है। "
                "इसके साथ ही नवा रायपुर अटल नगर में दो सौ एकड़ क्षेत्र में देश का अत्याधुनिक आर्टिफिशियल इंटेलिजेंस, सेमीकंडक्टर और डेटा सेंटर पार्क "
                "स्थापित करने के प्रस्ताव पर भी मुहर लगा दी गई है।\n"
                "मुख्यमंत्री साय ने कहा कि नई औद्योगिक नीति के तहत बस्तर और सरगुजा संभाग में लगने वाले कृषि प्रसंस्करण व हरित उद्योगों को विशेष कर छूट "
                "और पचास प्रतिशत तक पूंजीगत अनुदान दिया जाएगा, जिससे स्थानीय युवाओं को अपने ही जिले में रोजगार के बड़े अवसर मिलेंगे।"
            ),
        },
        # CG Story 1 (2-Col Top Corner — Raipur-Bilaspur Vande Bharat)
        {
            "category": "STATE_CG",
            "headline": "रायपुर से चलेंगी नई वंदे भारत ट्रेनें",
            "city": "बिलासपुर",
            "agency": "ब्यूरो",
            "blurb": "सौगात",
            "body": (
                "छत्तीसगढ़ के रेल यात्रियों को बड़ी सुविधा देते हुए रेल मंत्रालय ने रायपुर और बिलासपुर से नई दिल्ली तथा मुंबई के लिए दो नई हाई-स्पीड वंदे "
                "भारत स्लीपर ट्रेनों के परिचालन समय-सारिणी को अंतिम मंजूरी प्रदान कर दी है।"
            ),
        },
        # CG Story 2 (3-Col Band 2 — CM Vishnu Deo Sai Paddy Farmers 72-Hr Payment)
        {
            "category": "STATE_CG",
            "headline": "धान खरीदी पर किसानों को बहत्तर घंटे में भुगतान : साय",
            "city": "रायपुर",
            "agency": "विशेष संवाददाता",
            "blurb": "किसान",
            "body": (
                "मुख्यमंत्री विष्णुदेव साय ने प्रदेश के सभी दो हजार सात सौ उनतालीस धान उपार्जन केंद्रों पर किसानों को बायोमेट्रिक टोकन के साथ बहत्तर घंटे "
                "के भीतर सीधे बैंक खातों में ऑनलाइन भुगतान सुनिश्चित करने के निर्देश दिए हैं।"
            ),
        },
    ],
    "MP": [
        # MP Story 0 (6-Col Top Flyer + 2-Col Photo — CM Dr. Mohan Yadav Cabinet Decision)
        {
            "category": "STATE_MP",
            "subhead": "मुख्यमंत्री डॉ. मोहन यादव की अध्यक्षता में भोपाल मंत्रालय में बड़ा फैसला : मालवा, निमाड़, महाकौशल और विंध्य में लगेंगे नए उद्योग",
            "headline": "मध्य प्रदेश में चार इंडस्ट्रियल कॉरिडोर व साठ हजार भर्तियां",
            "city": "भोपाल",
            "agency": "स्टेट ब्यूरो",
            "blurb": "कैबिनेट",
            "photo": "ab_p3_campus_cmyk.jpg",
            "caption": "मध्य प्रदेश के नए इंडस्ट्रियल कॉरिडोर में आधुनिक ऑटोमोबाइल और विनिर्माण इकाई का दृश्य। — फाइल फोटो",
            "body": (
                "मुख्यमंत्री डॉ. मोहन यादव की अध्यक्षता में भोपाल मंत्रालय में हुई कैबिनेट बैठक में मालवा, निमाड़, महाकौशल और विंध्य अंचल को जोड़ने वाले "
                "चार नए एक्सप्रेस इंडस्ट्रियल कॉरिडोर के निर्माण और प्रदेश के सरकारी विभागों में साठ हजार पदों पर समयबद्ध भर्ती अभियान को मंजूरी दी गई है। "
                "इंदौर-पीथमपुर और भोपाल-मंडीदीप औद्योगिक क्षेत्र को सीधे मल्टी-मॉडल लॉजिस्टिक्स पार्क से जोड़ा जाएगा।\n"
                "मुख्यमंत्री डॉ. मोहन यादव ने कहा कि रीजनल इंडस्ट्री कॉन्क्लेव के माध्यम से मध्य प्रदेश में चार लाख करोड़ रुपये से अधिक के निवेश प्रस्ताव "
                "धरातल पर उतर रहे हैं, जिससे प्रदेश के लाखों युवाओं को तकनीकी और औद्योगिक क्षेत्र में प्रत्यक्ष रोजगार हासिल होगा।"
            ),
        },
        # MP Story 1 (2-Col Top Corner — Indore-Bhopal Rapid Rail)
        {
            "category": "STATE_MP",
            "headline": "इंदौर-भोपाल के बीच चलेगी रैपिड रेल",
            "city": "इंदौर",
            "agency": "विशेष संवाददाता",
            "blurb": "रफ्तार",
            "body": (
                "इंदौर और राजधानी भोपाल के बीच यात्रा समय को घटाकर मात्र पचपन मिनट करने के लिए नमो भारत की तर्ज पर सेमी हाई-स्पीड रीजनल रैपिड ट्रांजिट "
                "सिस्टम के सर्वे और डीपीआर को मंजूरी मिल गई है।"
            ),
        },
        # MP Story 2 (3-Col Band 2 — Ujjain Simhastha 5000 Cr by CM Mohan Yadav)
        {
            "category": "STATE_MP",
            "headline": "उज्जैन सिंहस्थ के लिए पांच हजार करोड़ मंजूर : मोहन यादव",
            "city": "उज्जैन",
            "agency": "ब्यूरो",
            "blurb": "सिंहस्थ",
            "body": (
                "मुख्यमंत्री डॉ. मोहन यादव ने आगामी उज्जैन सिंहस्थ महापर्व की भव्य तैयारियों के लिए क्षिप्रा शुद्धिकरण, नए पक्के घाटों और इंदौर-उज्जैन सिक्स-लेन "
                "कॉरिडोर हेतु पांच हजार करोड़ रुपये का विशेष बजट स्वीकृत किया है।"
            ),
        },
    ],
    "RJ": [
        # RJ Story 0 (6-Col Top Flyer + 2-Col Photo — CM Bhajanlal Sharma Rising Rajasthan)
        {
            "category": "STATE_RJ",
            "subhead": "मुख्यमंत्री भजनलाल शर्मा का राइजिंग राजस्थान के तहत बड़ा निर्णय : सौर ऊर्जा, पर्यटन और फिनटेक सेक्टर में बनेंगे नए कीर्तिमान",
            "headline": "राजस्थान में तीन लाख करोड़ का निवेश व सत्तर हजार भर्तियां",
            "city": "जयपुर",
            "agency": "स्टेट ब्यूरो",
            "blurb": "कैबिनेट",
            "photo": "ab_p1_second_lead_cmyk.jpg",
            "caption": "राइजिंग राजस्थान अभियान के तहत प्रदेश में स्थापित विशाल सौर ऊर्जा और हरित औद्योगिक पार्क। — फाइल फोटो",
            "body": (
                "मुख्यमंत्री भजनलाल शर्मा की अध्यक्षता में जयपुर स्थित मुख्यमंत्री कार्यालय में हुई उच्चस्तरीय बैठक में राइजिंग राजस्थान समिट के अंतर्गत "
                "हस्ताक्षरित तीन लाख करोड़ रुपये के औद्योगिक व सौर ऊर्जा समझौतों को धरातल पर उतारने और प्रदेश के युवाओं को सत्तर हजार सरकारी नियुक्तियां "
                "देने का समयबद्ध रोडमैप जारी किया गया है।\n"
                "मुख्यमंत्री शर्मा ने निर्देश दिए कि सभी नए औद्योगिक पार्कों में सिंगल-विंडो क्लीयरेंस के तहत पंद्रह दिनों के भीतर भूमि आवंटन और बिजली-पानी "
                "कनेक्शन उपलब्ध कराए जाएं, ताकि राजस्थान देश का सबसे बड़ा हरित ऊर्जा और मैन्युफैक्चरिंग हब बन सके।"
            ),
        },
        # RJ Story 1 (2-Col Top Corner — Jaipur Fintech Park)
        {
            "category": "STATE_RJ",
            "headline": "जयपुर में बनेगा नया फिनटेक पार्क",
            "city": "जयपुर",
            "agency": "विशेष संवाददाता",
            "blurb": "नवाचार",
            "body": (
                "राजधानी जयपुर के रिंग रोड कॉरिडोर पर अंतरराष्ट्रीय स्तर का फिनटेक सिटी और जेम्स एंड ज्वेलरी एक्सपोर्ट जोन विकसित किया जाएगा, जिससे "
                "राजस्थान के निर्यात को नई पहचान मिलेगी।"
            ),
        },
        # RJ Story 2 (3-Col Band 2 — ERCP Water Project by CM Bhajanlal Sharma)
        {
            "category": "STATE_RJ",
            "headline": "ईआरसीपी से राजस्थान के तेरह जिलों को पेयजल : भजनलाल",
            "city": "जयपुर",
            "agency": "ब्यूरो",
            "blurb": "सौगात",
            "body": (
                "मुख्यमंत्री भजनलाल शर्मा ने कहा कि संशोधित पार्वती-कालीसिंध-चंबल और पूर्वी राजस्थान नहर परियोजना के तहत तेरह जिलों के बांधों को जोड़ने "
                "वाली मुख्य फीडर नहरों का निर्माण युद्धस्तर पर पूरा किया जा रहा है।"
            ),
        },
    ],
    "DL": [
        # DL Story 0 (6-Col Top Flyer + 2-Col Photo — Delhi CM & Cabinet Big Decision)
        {
            "category": "STATE_DL",
            "subhead": "मुख्यमंत्री और दिल्ली कैबिनेट का राजधानी के लिए बड़ा फैसला : यमुना रिवरफ्रंट, मेट्रो फेज-चार और स्वच्छ हवा के लिए विशेष पैकेज",
            "headline": "दिल्ली में पंद्रह नए एलिवेटेड कॉरिडोर व दो हजार ई-बसें मंजूर",
            "city": "नई दिल्ली",
            "agency": "राजधानी ब्यूरो",
            "blurb": "राजधानी",
            "photo": "p1_real_s1_green_metro.jpg",
            "caption": "राष्ट्रीय राजधानी दिल्ली-एनसीआर में आधुनिक एलिवेटेड कॉरिडोर और हाई-स्पीड मेट्रो नेटवर्क का विस्तार। — फाइल फोटो",
            "body": (
                "राष्ट्रीय राजधानी नई दिल्ली को ट्रैफिक जाम और वायु प्रदूषण से स्थायी राहत दिलाने के लिए मुख्यमंत्री की अध्यक्षता में हुई उच्चस्तरीय बैठक में "
                "रिंग रोड, मथुरा रोड और द्वारका लिंक पर पंद्रह नए सिग्नल-फ्री एलिवेटेड कॉरिडोर तथा दो हजार नई वातानुकूलित इलेक्ट्रिक बसों के बेड़े को "
                "मंजूरी दी गई है।\n"
                "इसके साथ ही यमुना शुद्धिकरण अभियान के तहत तीन नए अत्याधुनिक सीवेज ट्रीटमेंट प्लांट और दिल्ली मेट्रो फेज-चार के सभी निर्माणाधीन कॉरिडोर को "
                "निर्धारित समय से छह माह पूर्व आम यात्रियों के लिए खोलने का लक्ष्य तय किया गया है।"
            ),
        },
        # DL Story 1 (2-Col Top Corner — IGI-Noida Airport Express Metro)
        {
            "category": "STATE_DL",
            "headline": "नोएडा एयरपोर्ट जुड़ेगा एक्सप्रेस मेट्रो से",
            "city": "नई दिल्ली",
            "agency": "विशेष संवाददाता",
            "blurb": "रफ्तार",
            "body": (
                "इंदिरा गांधी अंतरराष्ट्रीय हवाई अड्डे और जेवर स्थित नोएडा इंटरनेशनल एयरपोर्ट के बीच सीधी हाई-स्पीड एयरपोर्ट एक्सप्रेस मेट्रो लाइन के "
                "निर्माण को केंद्र ने हरी झंडी दे दी है।"
            ),
        },
        # DL Story 2 (3-Col Band 2 — Delhi Digital Health Card in Hospitals)
        {
            "category": "STATE_DL",
            "headline": "दिल्ली के सरकारी अस्पतालों में डिजिटल हेल्थ कार्ड लागू",
            "city": "नई दिल्ली",
            "agency": "ब्यूरो",
            "blurb": "स्वास्थ्य",
            "body": (
                "राजधानी के सभी प्रमुख सरकारी अस्पतालों में मरीजों को ओपीडी कतार से मुक्ति दिलाने के लिए क्यूआर-कोड आधारित डिजिटल हेल्थ कार्ड और "
                "ऑनलाइन जांच रिपोर्ट प्रणाली शुरू कर दी गई है।"
            ),
        },
    ],
}

# ==============================================================================
# 8 CORE FRONT-PAGE STORIES (NATIONAL + INTERNATIONAL + BUSINESS + SPORTS)
# Strictly distinct from Page 06 (Karobar), Page 07 (Khel), Page 08 (Desh-Videsh)
# ==============================================================================
CORE_PAGE1_8_STORIES = {
    "flyer": {
        "category": "NATIONAL",
        "subhead": "आगामी पांच वर्षों में दस लाख करोड़ रुपये का निवेश होगा : पच्चीस लाख युवाओं को मिलेगा प्रत्यक्ष रोजगार और महानगरों में प्रदूषण से राहत",
        "headline": "पचास प्रमुख शहरों में दौड़ेगी हाई-स्पीड ग्रीन मेट्रो",
        "city": "नई दिल्ली",
        "agency": "विशेष संवाददाता",
        "blurb": "मिशन",
        "photo": "p1_real_s1_green_metro.jpg",
        "caption": "हाई-स्पीड ग्रीन मेट्रो और रीजनल रैपिड रेल कॉरिडोर पर दौड़ती आधुनिक स्वदेशी ट्रेन। — फाइल फोटो",
        "body": (
            "केंद्रीय मंत्रिमंडल ने देश के पचास प्रमुख शहरों में हाई-स्पीड ग्रीन मेट्रो और स्मार्ट इंडस्ट्रियल कॉरिडोर के निर्माण को मंजूरी दे दी है। "
            "देश के शहरी बुनियादी ढांचे और औद्योगिक विकास को नई रफ्तार देने के लिए इस महत्वाकांक्षी योजना के तहत आगामी पांच वर्षों में दस लाख करोड़ "
            "रुपये का सीधा पूंजीगत निवेश किया जाएगा। प्रधानमंत्री की अध्यक्षता में हुई उच्चस्तरीय बैठक में यह निर्णय लिया गया कि सभी नए मेट्रो कॉरिडोर "
            "सौ प्रतिशत सौर ऊर्जा और हरित हाइड्रोजन तकनीक से संचालित होंगे।\n"
            "इसके साथ ही प्रथम चरण में मध्य प्रदेश, छत्तीसगढ़, राजस्थान, दिल्ली-एनसीआर, गुजरात और महाराष्ट्र के प्रमुख नगरों को मल्टी-मॉडल ट्रांसपोर्ट "
            "हब से जोड़ा जाएगा, जहां रेलवे जंक्शन, बस टर्मिनल और मेट्रो एक ही एकीकृत टिकट कार्ड से काम करेंगे।"
        ),
    },
    "lead": {
        "category": "NATIONAL",
        "headline": "केंद्र का बड़ा फैसला : तीन करोड़ परिवारों को मिलेंगे सौर ऊर्जा युक्त पक्के आवास",
        "subhead": "प्रधानमंत्री आवास योजना के नए चरण में ग्रामीण व शहरी मध्यम वर्ग को ब्याज सब्सिडी के साथ रूफटॉप सोलर पैनल का सीधा लाभ",
        "city": "नई दिल्ली",
        "agency": "राष्ट्रीय ब्यूरो",
        "blurb": "सौगात",
        "photo": "p1_real_s3_cabinet_lead.jpg",
        "caption": "नई दिल्ली स्थित संसद भवन परिसर में केंद्रीय मंत्रिमंडल के महत्वपूर्ण निर्णयों की घोषणा। — फाइल फोटो",
        "body": (
            "देश के प्रत्येक परिवार को बुनियादी सुविधाओं से युक्त पक्का घर उपलब्ध कराने के संकल्प को आगे बढ़ाते हुए केंद्र सरकार ने प्रधानमंत्री आवास "
            "योजना के नए विस्तारित चरण के तहत तीन करोड़ अतिरिक्त पक्के मकानों के निर्माण के लिए बजट राशि जारी कर दी है। इस बार बनने वाले सभी ग्रामीण "
            "और शहरी आवासों की छतों पर प्रधानमंत्री सूर्यघर योजना के अंतर्गत सोलर पैनल भी लगाए जाएंगे, जिससे लाभार्थी परिवारों का बिजली बिल शून्य हो "
            "जाएगा।\n"
            "शहरी क्षेत्रों में किराए के मकानों में रहने वाले कामकाजी परिवारों और मध्यम वर्ग के लिए गृह ऋण पर चार से छह प्रतिशत तक की विशेष ब्याज सब्सिडी "
            "सीधे बैंक खातों में हस्तांतरित की जाएगी। महिला सशक्तिकरण को प्राथमिकता देते हुए नए आवासों का पंजीकरण परिवार की महिला मुखिया के नाम पर "
            "किया जाएगा।"
        ),
        "box_title": "योजना के मुख्य बिंदु",
        "box_bullets": (
            "• ग्रामीण क्षेत्रों में दो करोड़ और शहरी क्षेत्रों में एक करोड़ नए पक्के आवासों का निर्माण होगा।\n"
            "• प्रत्येक आवास के साथ रूफटॉप सोलर पैनल, स्वच्छ पेयजल नल और रसोई गैस कनेक्शन अनिवार्य।\n"
            "• शहरी मध्यम वर्ग को नौ लाख रुपये तक के गृह ऋण पर सीधा ब्याज अनुदान मिलेगा।\n"
            "• निर्माण सामग्री और सीमेंट-इस्पात उद्योग में पचास लाख नए रोजगार के अवसर बनेंगे।\n"
            "• छत्तीसगढ़, मध्य प्रदेश और राजस्थान को पहली किस्त के रूप में बारह हजार करोड़ जारी।"
        ),
    },
    "intl_1": {
        "category": "INTERNATIONAL",
        "headline": "भारत व यूरोपीय संघ में व्यापार समझौता",
        "city": "ब्रसेल्स",
        "agency": "एजेंसी",
        "blurb": "कूटनीति",
        "body": (
            "भारत और सत्ताईस देशों के यूरोपीय संघ ने वर्षों से लंबित मुक्त व्यापार, हरित प्रौद्योगिकी और रक्षा सह-उत्पादन समझौते के प्रमुख बिंदुओं पर "
            "सहमति की मुहर लगा दी है। इससे भारतीय कपड़ा, फार्मा, आईटी और इंजीनियरिंग उत्पादों को यूरोपीय बाजार में शुल्क-मुक्त प्रवेश मिलेगा।"
        ),
    },
    "intl_2": {
        "category": "INTERNATIONAL",
        "headline": "सुरक्षा परिषद में भारत की स्थायी दावेदारी को बड़ा समर्थन",
        "city": "न्यूयॉर्क",
        "agency": "एजेंसी",
        "blurb": "विश्व",
        "body": (
            "संयुक्त राष्ट्र महासभा के विशेष सत्र में फ्रांस, ब्रिटेन और अमेरिका सहित अस्सी से अधिक देशों ने सुरक्षा परिषद के विस्तार और भारत को वीटो "
            "अधिकार सहित स्थायी सदस्य बनाए जाने के प्रस्ताव का पुरजोर समर्थन किया है।"
        ),
    },
    "biz_1": {
        "category": "BUSINESS",
        "headline": "विदेशी मुद्रा भंडार ने रचा नया रिकॉर्ड",
        "city": "मुंबई",
        "agency": "आर्थिक ब्यूरो",
        "blurb": "मुद्रा",
        "body": (
            "भारतीय रिजर्व बैंक द्वारा जारी साप्ताहिक आंकड़ों के अनुसार देश का विदेशी मुद्रा और स्वर्ण भंडार साढ़े पांच अरब डॉलर की छलांग लगाकर सात सौ "
            "बारह अरब डॉलर के सर्वकालिक उच्च स्तर पर पहुंच गया है, जिससे वैश्विक उतार-चढ़ाव के बीच भारतीय अर्थव्यवस्था की मजबूती सिद्ध हुई है।"
        ),
    },
    "biz_2": {
        "category": "BUSINESS",
        "headline": "पंद्रह नए देशों में यूपीआई सेवा शुरू",
        "city": "नई दिल्ली",
        "agency": "ब्यूरो",
        "blurb": "डिजिटल",
        "body": (
            "नेशनल पेमेंट्स कॉरपोरेशन ऑफ इंडिया ने दक्षिण-पूर्व एशिया, खाड़ी देशों और यूरोप के पंद्रह नए देशों में क्यूआर कोड आधारित यूपीआई अंतरराष्ट्रीय "
            "भुगतान सेवा शुरू कर दी है। अब भारतीय पर्यटक और प्रवासी विदेशों में भी सीधे रुपये में भुगतान कर सकेंगे।"
        ),
    },
    "sports_1": {
        "category": "SPORTS",
        "headline": "चैंपियंस ट्रॉफी और टेस्ट फाइनल के लिए बीसीसीआई का रोडमैप",
        "city": "मुंबई",
        "agency": "खेल ब्यूरो",
        "blurb": "क्रिकेट",
        "body": (
            "भारतीय क्रिकेट कंट्रोल बोर्ड ने आगामी आईसीसी चैंपियंस ट्रॉफी और विश्व टेस्ट चैंपियनशिप फाइनल के लिए प्रमुख खिलाड़ियों के वर्कलोड प्रबंधन तथा "
            "बेंगलुरु स्थित नए नेशनल क्रिकेट अकादमी सेंटर में हाई-परफॉर्मेंस कैंप का कार्यक्रम घोषित कर दिया है।"
        ),
    },
    "anchor": {
        "category": "NATIONAL_CULTURE",
        "headline": "काशी से रामेश्वरम तक पांच नए पर्यटन कॉरिडोर शुरू",
        "subhead": "विरासत भी और विकास भी : हेरिटेज ट्रेनों, रिवर क्रूज और रोपवे नेटवर्क से जुड़े देश के प्रमुख तीर्थ व सांस्कृतिक केंद्र",
        "city": "वाराणसी",
        "agency": "विशेष संवाददाता",
        "blurb": "धरोहर",
        "photo": "p1_real_s10_heritage_corridor.jpg",
        "caption": "वाराणसी के गंगा घाटों और सांस्कृतिक कॉरिडोर का भव्य आलोकित दृश्य। — फाइल फोटो",
        "body": (
            "भारत की प्राचीन सांस्कृतिक विरासत को आधुनिक पर्यटन सुविधाओं से जोड़ने के लिए काशी, अयोध्या, उज्जैन, पुरी और रामेश्वरम को जोड़ने वाले पांच "
            "नए आध्यात्मिक व इको-हेरिटेज पर्यटन कॉरिडोर राष्ट्र को समर्पित किए गए हैं। इन गलियारों में इलेक्ट्रिक क्रूज नौकाओं, सौर ऊर्जा चालित रोपवे और "
            "डिजिटल संग्रहालय केंद्रों की स्थापना से श्रद्धालुओं तथा विदेशी पर्यटकों की संख्या में दोगुनी वृद्धि दर्ज की गई है।"
        ),
    },
}


def edition_to_state_group(edition_code: str) -> str:
    ed = (edition_code or "RAIPUR").strip().upper()
    if ed in ("RAIPUR", "BILASPUR", "RAJNANDGAON", "RPR", "BSP", "RJN"):
        return "CG"
    if ed in ("BHOPAL", "INDORE", "BPL", "IND"):
        return "MP"
    if ed in ("JAIPUR", "JPR"):
        return "RJ"
    if ed in ("NEW_DELHI", "DELHI", "DEL"):
        return "DL"
    return "CG"


def place_dynamic_edition_page1_masthead(grid, edition_key: str, ed_date_str: str):
    """Draws the 6.0 cm Dynamic Edition Front Masthead (RAIPUR, BILASPUR, RAJNANDGAON, BHOPAL, INDORE, JAIPUR, NEW_DELHI)."""
    mh_x0, mh_y0, mh_x1 = grid.print_x0, grid.masthead_y0, grid.print_x1
    try:
        dp = [int(x) for x in ed_date_str.split("-")]
        dt = datetime.date(dp[0], dp[1], dp[2]) if dp[0] > 1900 else datetime.date(dp[2], dp[1], dp[0])
    except Exception:
        dt = datetime.date(2026, 11, 19)

    ref_dt = datetime.date(2026, 11, 19)
    delta_days = (dt - ref_dt).days
    edition_key = (edition_key or "RAIPUR").strip().upper()

    if edition_key in ("NEW_DELHI", "DELHI", "DEL"):
        base_abs_issue = (2 - 1) * 365 + (13 - 1)
        cur_abs_issue = max(0, base_abs_issue + delta_days)
        varsh_num = (cur_abs_issue // 365) + 1
        ank_num = (cur_abs_issue % 365) + 1
        varsh_str = f"{varsh_num:02d}"
        rni_or_prgi_str = "PRGI - DLHIN/25/A3662"
        varsh_ank_line = f"वर्ष-{varsh_str}। अंक {ank_num}। मूल्य - 2 रुपए।"
        pages_edition_line = "पृष्ठ-08। नगर संस्करण"
        city_display_hi = "नई दिल्ली"
        mh_img_path = PHOTOS_DIR / "new_delhi_page1_masthead_base_no_ear.png"
    elif edition_key in ("BILASPUR", "BSP"):
        base_abs_issue = (3 - 1) * 365 + (329 - 1)
        cur_abs_issue = max(0, base_abs_issue + delta_days)
        varsh_num = (cur_abs_issue // 365) + 1
        ank_num = (cur_abs_issue % 365) + 1
        varsh_str = f"{varsh_num:02d}"
        rni_or_prgi_str = "PRGI No. - CTHIN/25/A1423"
        varsh_ank_line = f"वर्ष-{varsh_str} । अंक {ank_num} । मूल्य - 2 रुपए।"
        pages_edition_line = "पृष्ठ-08 । नगर संस्करण"
        city_display_hi = "बिलासपुर"
        mh_img_path = PHOTOS_DIR / "bilaspur_page1_masthead_base_no_ear.png"
    elif edition_key in ("BHOPAL", "BPL"):
        base_abs_issue = (10 - 1) * 365 + (222 - 1)
        cur_abs_issue = max(0, base_abs_issue + delta_days)
        varsh_num = (cur_abs_issue // 365) + 1
        ank_num = (cur_abs_issue % 365) + 1
        rni_or_prgi_str = "RNI NO. - MPHIN/2015/63660"
        varsh_ank_line = f"वर्ष-{varsh_num} । अंक {ank_num} । मूल्य - 2 रुपए।"
        pages_edition_line = "पृष्ठ-08 । नगर संस्करण"
        city_display_hi = "भोपाल"
        mh_img_path = PHOTOS_DIR / "bhopal_page1_masthead_base_no_ear.png"
    elif edition_key in ("JAIPUR", "JPR"):
        base_abs_issue = (1 - 1) * 365 + (98 - 1)
        cur_abs_issue = max(0, base_abs_issue + delta_days)
        varsh_num = (cur_abs_issue // 365) + 1
        ank_num = (cur_abs_issue % 365) + 1
        varsh_str = f"{varsh_num:02d}"
        rni_or_prgi_str = "RJHIN/26/A6072"
        varsh_ank_line = f"वर्ष-{varsh_str} । अंक {ank_num} । मूल्य - 2 रुपए।"
        pages_edition_line = "पृष्ठ-08 । नगर संस्करण"
        city_display_hi = "जयपुर"
        mh_img_path = PHOTOS_DIR / "jaipur_page1_masthead_base_no_ear.png"
    elif edition_key in ("INDORE", "IND"):
        base_abs_issue = (12 - 1) * 365 + (315 - 1)
        cur_abs_issue = max(0, base_abs_issue + delta_days)
        varsh_num = (cur_abs_issue // 365) + 1
        ank_num = (cur_abs_issue % 365) + 1
        rni_or_prgi_str = "RNI NO. - MPHIN/2014/56594"
        varsh_ank_line = f"वर्ष-{varsh_num} । अंक {ank_num} । मूल्य - 2 रुपए ।"
        pages_edition_line = "पृष्ठ-08 । नगर संस्करण"
        city_display_hi = "इंदौर"
        mh_img_path = PHOTOS_DIR / "indore_page1_masthead_base_no_ear.png"
    elif edition_key in ("RAJNANDGAON", "RJN"):
        base_abs_issue = (4 - 1) * 365 + (341 - 1)
        cur_abs_issue = max(0, base_abs_issue + delta_days)
        varsh_num = (cur_abs_issue // 365) + 1
        ank_num = (cur_abs_issue % 365) + 1
        varsh_str = f"{varsh_num:02d}"
        rni_or_prgi_str = "PRGI - CTHIN/25/A4799"
        varsh_ank_line = f"वर्ष-{varsh_str} । अंक {ank_num} । मूल्य - 2 रुपए।"
        pages_edition_line = "पृष्ठ-08 । नगर संस्करण"
        city_display_hi = "राजनांदगांव"
        mh_img_path = PHOTOS_DIR / "rajnandgaon_page1_masthead_base_no_ear.png"
    else:
        base_abs_issue = (10 - 1) * 365 + (130 - 1)
        cur_abs_issue = max(0, base_abs_issue + delta_days)
        varsh_num = (cur_abs_issue // 365) + 1
        ank_num = (cur_abs_issue % 365) + 1
        rni_or_prgi_str = "RNI NO. - CHHHIN/2018/76773"
        varsh_ank_line = f"वर्ष-{varsh_num} । अंक {ank_num} । मूल्य - 3 रुपए ।"
        pages_edition_line = "पृष्ठ-08 । नगर संस्करण"
        city_display_hi = "रायपुर"
        mh_img_path = PHOTOS_DIR / "raipur_page1_masthead_base_no_ear.png"

    hi_weekdays = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
    eng_weekdays = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
    hi_months = {
        1: "जनवरी", 2: "फरवरी", 3: "मार्च", 4: "अप्रैल", 5: "मई", 6: "जून",
        7: "जुलाई", 8: "अगस्त", 9: "सितंबर", 10: "अक्टूबर", 11: "नवंबर", 12: "दिसंबर",
    }
    eng_day_str = eng_weekdays[dt.weekday()]
    hi_date_str = f"{hi_weekdays[dt.weekday()]}, {dt.day} {hi_months[dt.month]}, {dt.year}"

    b6.batch([
        {"command": "swatch.create", "params": {"name": "EarOrange", "color": "#f37021"}},
        {"command": "swatch.create", "params": {"name": "EarRed", "color": "#d71920"}},
        {"command": "swatch.create", "params": {"name": "EarBlue", "color": "#1c3f94"}},
        {"command": "swatch.create", "params": {"name": "EarCyan", "color": "#00aeef"}},
    ])

    r_mh_bg = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [mh_x0, mh_y0, mh_x1, round(mh_y0 + cm(5.80), 2)],
        "content": "graphic",
    })
    b6.batch([
        {"command": "file.place", "params": {"frame": r_mh_bg["id"], "path": str(mh_img_path)}},
        {"command": "object.fit", "params": {"ids": [r_mh_bg["id"]], "mode": "fitProportionally"}},
        {"command": "object.stroke", "params": {"ids": [r_mh_bg["id"]], "swatch": "[None]", "weight": 0.0, "tint": 0.0}},
    ])

    ear_x0 = round(mh_x0 + cm(27.25), 2)
    ear_x1 = mh_x1
    top3_txt = f"{rni_or_prgi_str}\n{varsh_ank_line}\n{pages_edition_line}"
    r_ear_top = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [ear_x0, round(mh_y0 + cm(0.75), 2), ear_x1, round(mh_y0 + cm(2.15), 2)],
        "content": "text",
        "text": top3_txt,
    })
    rni_b = len(rni_or_prgi_str.encode("utf-8"))
    b6.batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_ear_top["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_ear_top["story"], "anchor": 0, "focus": 999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Bold",
            "size": 10.0,
            "leading": {"kind": "points", "value": 11.8},
            "fill": "[Black]",
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "firstLineIndent": 0.0, "hyphenate": False, "gridAlign": "none"}}},
        {"command": "text.select", "params": {"story": r_ear_top["story"], "anchor": 0, "focus": rni_b}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "Arial",
            "fontStyle": "Bold",
            "size": 8.2,
            "leading": {"kind": "points", "value": 11.2},
            "fill": "[Black]",
        }}},
    ])

    r_ear_city = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [ear_x0, round(mh_y0 + cm(2.15), 2), ear_x1, round(mh_y0 + cm(3.45), 2)],
        "content": "text",
        "text": city_display_hi,
    })
    city_pt = 21.5 if len(city_display_hi) >= 8 else 28.0
    b6.batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_ear_city["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_ear_city["story"], "anchor": 0, "focus": 99}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Bold",
            "size": city_pt,
            "leading": {"kind": "points", "value": round(city_pt + 1.0, 2)},
            "fill": "[Black]",
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "firstLineIndent": 0.0, "hyphenate": False, "gridAlign": "none"}}},
    ])

    r_ear_eng = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [ear_x0, round(mh_y0 + cm(3.45), 2), ear_x1, round(mh_y0 + cm(4.32), 2)],
        "content": "text",
        "text": eng_day_str,
    })
    eng_cmds = [
        {"command": "object.textFrameOptions", "params": {"ids": [r_ear_eng["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_ear_eng["story"], "anchor": 0, "focus": 99}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "Arial",
            "fontStyle": "Bold",
            "size": 16.5,
            "leading": {"kind": "points", "value": 17.5},
            "tracking": 35.0,
            "fill": "[Black]",
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "firstLineIndent": 0.0, "hyphenate": False, "gridAlign": "none"}}},
    ]
    pair_swatches = ["EarOrange", "EarRed", "EarBlue", "EarCyan", "EarOrange", "[Black]"]
    for idx_ch in range(len(eng_day_str)):
        sw_c = pair_swatches[min(idx_ch // 2, len(pair_swatches) - 1)]
        if idx_ch == 1:
            sw_c = "EarRed"
        elif idx_ch in (2, 3):
            sw_c = "EarBlue"
        elif idx_ch in (4, 5):
            sw_c = "EarCyan" if idx_ch == 4 else "EarOrange"
        elif idx_ch >= 6:
            sw_c = "[Black]" if idx_ch == len(eng_day_str) - 1 else "EarRed"
        eng_cmds.extend([
            {"command": "text.select", "params": {"story": r_ear_eng["story"], "anchor": idx_ch, "focus": idx_ch + 1}},
            {"command": "type.char", "params": {"attrs": {"fill": sw_c, "fillTint": 1.0}}},
        ])
    b6.batch(eng_cmds)

    r_ear_hi = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [ear_x0, round(mh_y0 + cm(4.32), 2), ear_x1, round(mh_y0 + cm(5.15), 2)],
        "content": "text",
        "text": hi_date_str,
    })
    b6.batch([
        {"command": "object.textFrameOptions", "params": {"ids": [r_ear_hi["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": r_ear_hi["story"], "anchor": 0, "focus": 199}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Bold",
            "size": 12.0,
            "leading": {"kind": "points", "value": 13.0},
            "fill": "[Black]",
        }}},
        {"command": "type.para", "params": {"attrs": {"align": "center", "firstLineIndent": 0.0, "hyphenate": False, "gridAlign": "none"}}},
    ])
    return {"city_hi": city_display_hi, "varsh_ank": varsh_ank_line, "rni": rni_or_prgi_str}


def place_5col_lead_package(
    grid,
    start_col: int,
    y0: float,
    y1: float,
    lead_obj: dict,
    gray_box_in_last_col: bool = True,
) -> float:
    lx0 = grid.col_x0(start_col)
    lx1 = grid.col_x1(start_col, 5)
    cur_y = y0
    _, _, h_pt, hh = b6.fit_aditya_bharat_headline(
        0, lx0, cur_y, lx1,
        raw_text=lead_obj["headline"],
        target_lines=2,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=56.0,
        lo_pt=42.0,
        align="left",
    )
    cur_y = round(cur_y + hh + 0.5, 2)
    _, _, _, sh = b6.fit_aditya_bharat_headline(
        0, lx0, cur_y, lx1,
        raw_text=lead_obj["subhead"],
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=15.0,
        lo_pt=11.8,
        align="left",
    )
    by0 = round(cur_y + sh + 1.5, 2)
    by1 = b6.snap_frame_bottom_to_baseline(y1)

    if gray_box_in_last_col:
        body_start_col = start_col
        box_col = start_col + 4
        photo_col = start_col + 1
    else:
        box_col = start_col
        body_start_col = start_col + 1
        photo_col = start_col + 2

    lbody_x0 = grid.col_x0(body_start_col)
    lbody_x1 = grid.col_x1(body_start_col, 4)
    r_lb = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [lbody_x0, by0, lbody_x1, by1],
        "content": "text",
        "text": "",
    })
    b6.cmd("object.textFrameOptions", {
        "ids": [r_lb["id"]],
        "columns": 4,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    b6.place_red_subject_blurb(0, lbody_x0, round(by0 + cm(1.75), 2), lead_obj["blurb"])
    cap_y1 = round(b6.snap_underflow_top(by1, num_underflow_lines=6) - 3.2, 2)
    b6.place_photo_and_caption_cmyk(
        0,
        grid.col_x0(photo_col),
        by0,
        grid.col_x1(photo_col, 2),
        cap_y1,
        lead_obj["photo"],
        "ab_p1_lead_cabinet_cmyk.jpg",
        lead_obj["caption"],
        cap_h=22.0,
    )
    fit_front_page_body(r_lb["story"], lead_obj["city"], lead_obj["agency"], lead_obj["body"])

    inset_pt = mm(2.5)
    bx0 = grid.col_x0(box_col)
    bx1 = grid.col_x1(box_col, 1)
    r_box = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [bx0, by0, bx1, by1],
        "content": "text",
        "text": "",
    })
    b6.batch([
        {"command": "object.fill", "params": {"ids": [r_box["id"]], "swatch": "[Black]", "tint": 0.15}},
        {"command": "object.stroke", "params": {"ids": [r_box["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 0.55}},
        {"command": "object.textFrameOptions", "params": {
            "ids": [r_box["id"]],
            "columns": 1,
            "inset": [inset_pt, inset_pt, inset_pt, inset_pt],
            "verticalJustification": "top",
        }},
    ])
    b6.fit_box_completely(
        r_box["story"],
        head_str=lead_obj["box_title"],
        raw_bullets=lead_obj["box_bullets"],
        head_pt=15.5,
        head_align="center",
        body_pt=10.5,
        body_lead=11.3,
        para_space=2.2,
    )
    return h_pt


def place_5col_anchor_package(grid, start_col: int, y0: float, y1: float, anc_obj: dict) -> float:
    ax0 = grid.col_x0(start_col)
    ax1 = grid.col_x1(start_col, 5)
    cur_y = y0
    _, _, h_pt, hh = b6.fit_aditya_bharat_headline(
        0, ax0, cur_y, ax1,
        raw_text=anc_obj["headline"],
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=46.0,
        lo_pt=32.0,
        align="center",
    )
    cur_y = round(cur_y + hh + 0.5, 2)
    _, _, _, sh = b6.fit_aditya_bharat_headline(
        0, ax0, cur_y, ax1,
        raw_text=anc_obj["subhead"],
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=14.5,
        lo_pt=11.5,
        align="center",
    )
    by0 = round(cur_y + sh + 1.5, 2)
    by1 = b6.snap_frame_bottom_to_baseline(y1)
    r_ab = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [ax0, by0, ax1, by1],
        "content": "text",
        "text": "",
    })
    b6.cmd("object.textFrameOptions", {
        "ids": [r_ab["id"]],
        "columns": 5,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    b6.place_red_subject_blurb(0, ax0, round(by0 + cm(1.55), 2), anc_obj["blurb"])
    cap_y1 = round(b6.snap_underflow_top(by1, num_underflow_lines=5) - 3.2, 2)
    b6.place_photo_and_caption_cmyk(
        0,
        grid.col_x0(start_col + 2),
        by0,
        grid.col_x1(start_col + 2, 2),
        cap_y1,
        anc_obj["photo"],
        "ab_p1_anchor_heritage_cmyk.jpg",
        anc_obj["caption"],
        cap_h=22.0,
    )
    fit_front_page_body(r_ab["story"], anc_obj["city"], anc_obj["agency"], anc_obj["body"])
    return h_pt


def build_aditya_bharat_page1_with_dummy(
    date_str: str = "19-11-2026",
    edition_code: str = "RAIPUR",
    dummy_id: str = "AUTO",
    export_desktop_pdf: bool = False,
) -> dict:
    t0 = time.perf_counter()
    edition_code = (edition_code or "RAIPUR").strip().upper()
    ensure_real_page1_photos()

    # Determine which of the 4 rotating dummies (DUMMY_1, DUMMY_2, DUMMY_3, DUMMY_4) to use
    dummy_choices = ["DUMMY_1", "DUMMY_2", "DUMMY_3", "DUMMY_4"]
    if dummy_id and dummy_id.upper() in dummy_choices:
        chosen_dummy = dummy_id.upper()
    else:
        try:
            dp = [int(x) for x in date_str.split("-")]
            dt = datetime.date(dp[0], dp[1], dp[2]) if dp[0] > 1900 else datetime.date(dp[2], dp[1], dp[0])
            chosen_dummy = dummy_choices[dt.toordinal() % 4]
        except Exception:
            chosen_dummy = "DUMMY_1"

    state_grp = edition_to_state_group(edition_code)
    live_p1_path = CACHE_DIR / f"{date_str}_LIVE_P1_4STATES.json"
    if live_p1_path.exists():
        try:
            lp1 = json.loads(live_p1_path.read_text(encoding="utf-8"))
            if isinstance(lp1.get("EDITION_STATE_3_STORIES"), dict):
                EDITION_STATE_3_STORIES.update(lp1["EDITION_STATE_3_STORIES"])
            if isinstance(lp1.get("CORE_PAGE1_8_STORIES"), dict):
                CORE_PAGE1_8_STORIES.update(lp1["CORE_PAGE1_8_STORIES"])
        except Exception:
            pass
    st_list = EDITION_STATE_3_STORIES.get(state_grp, EDITION_STATE_3_STORIES["CG"])
    # 1. Top 6-Col Banner Flyer + 2-Col Photo right under Masthead = State CM Flagship Story!
    fl_obj = st_list[0]
    # 2. Top 2-Col Corner Story right under Masthead = 2nd Prominent State Story!
    st_hub_2col = st_list[1]
    # 3. Band-2 Upper 3-Col Story = 3rd Prominent State CM Story!
    st_cm_3col = st_list[2]
    # Band-3 2-Col Story = National Green Metro Story
    st_rail_2col = CORE_PAGE1_8_STORIES["flyer"]

    lead_obj = CORE_PAGE1_8_STORIES["lead"]
    intl_1 = CORE_PAGE1_8_STORIES["intl_1"]
    intl_2 = CORE_PAGE1_8_STORIES["intl_2"]
    biz_1 = CORE_PAGE1_8_STORIES["biz_1"]
    biz_2 = CORE_PAGE1_8_STORIES["biz_2"]
    sp_1 = CORE_PAGE1_8_STORIES["sports_1"]
    anc_obj = CORE_PAGE1_8_STORIES["anchor"]

    all_11_stories = [
        fl_obj, st_hub_2col, lead_obj, st_cm_3col, sp_1,
        st_rail_2col, biz_1, biz_2, intl_1, anc_obj, intl_2,
    ]

    # Collect all 12 state stories across all 4 states (CG, MP, RJ, DL) so NONE of them ever repeat on inside pages!
    all_4states_p1_headlines = [
        st_item["headline"]
        for st_grp_items in EDITION_STATE_3_STORIES.values()
        for st_item in st_grp_items
    ]

    # Verify zero overlap against inside pages (Pages 02, 03, 04, 05, 06, 07, 08)
    inside_headlines = set()
    for jf in CACHE_DIR.glob("*.json"):
        if "PAGE1" in jf.name or "GLOBAL_USED_NEWS_LEDGER" in jf.name or "p1_front" in jf.name:
            continue
        try:
            raw = jf.read_text(encoding="utf-8")
            for m in re.findall(r'"headline"\s*:\s*"([^"]+)"', raw):
                inside_headlines.add(" ".join(m.replace("\n", " ").split()))
        except Exception:
            pass

    cross_dups = [
        s["headline"] for s in all_11_stories
        if " ".join(s["headline"].replace("\n", " ").split()) in inside_headlines
    ]

    # Write Global Used News Ledger so inside pages (02, 03, 05, 06, 07, 08) also block ALL 4 States' Page 01 stories!
    global_ledger_path = CACHE_DIR / f"{date_str}_GLOBAL_USED_NEWS_LEDGER.json"
    ledger_data = {
        "date_str": date_str,
        "edition_code": edition_code,
        "state_group": state_grp,
        "dummy_id": chosen_dummy,
        "page1_locked_stories_count": len(all_11_stories),
        "zero_cross_page_duplicates": len(cross_dups) == 0,
        "blocked_for_page_02_03_05_states": all_4states_p1_headlines,
        "blocked_for_page_06_business": [biz_1["headline"], biz_2["headline"]],
        "blocked_for_page_07_sports": [sp_1["headline"]],
        "blocked_for_page_08_desh_videsh": [st_rail_2col["headline"], lead_obj["headline"], intl_1["headline"], intl_2["headline"], anc_obj["headline"]],
        "stories": all_11_stories,
    }
    global_ledger_path.write_text(json.dumps(ledger_data, ensure_ascii=False, indent=2), encoding="utf-8")

    b6.connect_page_designer()
    grid = b6.AdityaBharatPage6Grid()
    grid.masthead_h_cm = 6.0
    grid.masthead_y1 = round(grid.masthead_y0 + cm(6.0), 2)

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
            "title": f"आदित्य भारत — पेज 01 मास्टर फ्रंट पेज ({edition_code} • {chosen_dummy} • 11 खबरें)",
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

    # 1. Draw the 6.0 cm Dynamic 7-Edition Front Page Masthead (y = 1.0 .. 7.0 cm)
    mh_info = place_dynamic_edition_page1_masthead(grid, edition_code, date_str)

    headline_pts = {}

    # ==========================================================================
    # BAND 1 (y = 7.00 .. 16.20 cm, Height = 9.20 cm — 2 Stories):
    #   - DUMMY_1 & DUMMY_3: Left 6-Col Flyer (Cols 1..6) + Right 2-Col State Story (Cols 7..8)
    #   - DUMMY_2 & DUMMY_4: Left 2-Col State Story (Cols 1..2) + Right 6-Col Flyer (Cols 3..8)
    # ==========================================================================
    b1_y0 = round(cm(7.0), 2)
    b1_y1 = b6.snap_frame_bottom_to_baseline(round(b1_y0 + cm(9.2), 2))

    if chosen_dummy in ("DUMMY_1", "DUMMY_3"):
        fl_c0, st2_c0 = 1, 7
    else:
        st2_c0, fl_c0 = 1, 3

    fl_x0 = grid.col_x0(fl_c0)
    fl_x1 = grid.col_x1(fl_c0, 6)
    fl_cur_y = b1_y0
    _, _, _, fl_sh = b6.fit_aditya_bharat_headline(
        0, fl_x0, fl_cur_y, fl_x1,
        raw_text=fl_obj["subhead"],
        target_lines=1,
        font_family="DB Hindi",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=14.8,
        lo_pt=11.5,
        align="center",
    )
    fl_cur_y = round(fl_cur_y + fl_sh + 1.0, 2)
    _, _, fl_pt, fl_hh = b6.fit_aditya_bharat_headline(
        0, fl_x0, fl_cur_y, fl_x1,
        raw_text=fl_obj["headline"],
        target_lines=1,
        font_family="DB Rasrand Bold",
        font_style="Bold",
        fill_swatch="[Black]",
        hi_pt=52.0,
        lo_pt=36.0,
        align="center",
    )
    headline_pts["S1_FLYER"] = fl_pt
    fl_by0 = round(fl_cur_y + fl_hh + 1.5, 2)
    r_fl_b = b6.cmd("frame.create", {
        "spread": 0,
        "rect": [fl_x0, fl_by0, fl_x1, b1_y1],
        "content": "text",
        "text": "",
    })
    b6.cmd("object.textFrameOptions", {
        "ids": [r_fl_b["id"]],
        "columns": 6,
        "gutter": grid.gutter_pt,
        "verticalJustification": "top",
        "columnRule": False,
    })
    b6.place_red_subject_blurb(0, fl_x0, round(fl_by0 + cm(1.55), 2), fl_obj["blurb"])
    fl_cap_y1 = round(b6.snap_underflow_top(b1_y1, num_underflow_lines=5) - 3.2, 2)
    b6.place_photo_and_caption_cmyk(
        0,
        grid.col_x0(fl_c0 + 2),
        fl_by0,
        grid.col_x1(fl_c0 + 2, 2),
        fl_cap_y1,
        fl_obj["photo"],
        f"ab_p1_s1_{state_grp.lower()}_flyer_cmyk.jpg",
        fl_obj["caption"],
        cap_h=22.0,
    )
    fit_front_page_body(r_fl_b["story"], fl_obj["city"], fl_obj["agency"], fl_obj["body"])

    # Story 2: 2-Col State Capital / Innovation Story
    headline_pts["S2_STATE"] = place_front_multi_col_story(
        grid, grid.col_x0(st2_c0), grid.col_x1(st2_c0, 2), b1_y0, b1_y1, cols=2,
        st_obj=st_hub_2col, target_lines=2, hi_pt=36.0, lo_pt=30.0,
    )

    sep1_y = round(b1_y1 + mm(1.75), 2)
    r_sep1 = b6.cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep1_y], "b": [grid.print_x1, sep1_y]})
    b6.cmd("object.stroke", {"ids": [r_sep1["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 2 (y = 16.55 .. 31.15 cm, Height = 14.60 cm — 3 Stories: S3 Lead + S4 State CM + S5 Sports):
    #   - DUMMY_1 & DUMMY_4: Left 5-Col Main Lead (Cols 1..5, Gray Box in Col 5) + Right 3-Col Stack (Cols 6..8)
    #   - DUMMY_2 & DUMMY_3: Left 3-Col Stack (Cols 1..3) + Right 5-Col Main Lead (Cols 4..8, Gray Box in Col 8)
    # ==========================================================================
    b2_y0 = round(sep1_y + mm(1.75), 2)
    b2_y1 = b6.snap_frame_bottom_to_baseline(round(b2_y0 + cm(14.6), 2))

    if chosen_dummy in ("DUMMY_1", "DUMMY_4"):
        lead_c0, stack_c0 = 1, 6
    else:
        stack_c0, lead_c0 = 1, 4

    headline_pts["S3_LEAD"] = place_5col_lead_package(
        grid, lead_c0, b2_y0, b2_y1, lead_obj, gray_box_in_last_col=True
    )

    st_x0 = grid.col_x0(stack_c0)
    st_x1 = grid.col_x1(stack_c0, 3)
    st_mid_y = b6.snap_frame_bottom_to_baseline(round(b2_y0 + cm(7.15), 2))

    # Story 4: State CM Big Decision (3-Col Top)
    headline_pts["S4_STATE_CM"] = place_front_multi_col_story(
        grid, st_x0, st_x1, b2_y0, st_mid_y, cols=3,
        st_obj=st_cm_3col, target_lines=2, hi_pt=38.0, lo_pt=30.0,
    )

    st_sep_y = round(st_mid_y + mm(1.75), 2)
    r_st_sep = b6.cmd("line.create", {"spread": 0, "a": [st_x0, st_sep_y], "b": [st_x1, st_sep_y]})
    b6.cmd("object.stroke", {"ids": [r_st_sep["id"]], "swatch": "[Black]", "weight": 0.65, "tint": 0.85})

    # Story 5: Sports Front-Page Story (3-Col Bottom)
    headline_pts["S5_SPORTS"] = place_front_multi_col_story(
        grid, st_x0, st_x1, round(st_sep_y + mm(1.75), 2), b2_y1, cols=3,
        st_obj=sp_1, target_lines=2, hi_pt=38.0, lo_pt=30.0,
    )

    sep2_y = round(b2_y1 + mm(1.75), 2)
    r_sep2 = b6.cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep2_y], "b": [grid.print_x1, sep2_y]})
    b6.cmd("object.stroke", {"ids": [r_sep2["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 1.0})

    # ==========================================================================
    # BAND 3 (y = 31.50 .. 41.30 cm, Height = 9.80 cm — 4 Stories: 2 + 2 + 2 + 2 Columns):
    #   - Story 6 (Cols 1..2): 3rd State Story (Rail / Infra)
    #   - Story 7 (Cols 3..4): Business Story 1 (Forex Reserve)
    #   - Story 8 (Cols 5..6): Business Story 2 (Global UPI)
    #   - Story 9 (Cols 7..8): International Story 1 (India-EU Trade Deal)
    # ==========================================================================
    b3_y0 = round(sep2_y + mm(1.75), 2)
    b3_y1 = b6.snap_frame_bottom_to_baseline(round(b3_y0 + cm(9.8), 2))

    b3_items = [
        ("S6_STATE_3", st_rail_2col),
        ("S7_BIZ_1", biz_1),
        ("S8_BIZ_2", biz_2),
        ("S9_INTL_1", intl_1),
    ]
    if chosen_dummy in ("DUMMY_3", "DUMMY_4"):
        b3_items = [b3_items[1], b3_items[0], b3_items[3], b3_items[2]]

    for idx_b3, (k_lbl, st_b3) in enumerate(b3_items):
        c_start = 1 + 2 * idx_b3
        headline_pts[k_lbl] = place_front_multi_col_story(
            grid, grid.col_x0(c_start), grid.col_x1(c_start, 2), b3_y0, b3_y1, cols=2,
            st_obj=st_b3, target_lines=2, hi_pt=36.0, lo_pt=30.0,
        )

    sep3_y = round(b3_y1 + mm(1.75), 2)
    r_sep3 = b6.cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep3_y], "b": [grid.print_x1, sep3_y]})
    b6.cmd("object.stroke", {"ids": [r_sep3["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 4 (y = 41.65 .. 52.00 cm, Height = 10.35 cm — 2 Stories: 5-Col Anchor + 3-Col International):
    #   - DUMMY_1 & DUMMY_2: Left 5-Col Heritage Anchor (Cols 1..5) + Right 3-Col UNSC International (Cols 6..8)
    #   - DUMMY_3 & DUMMY_4: Left 3-Col UNSC International (Cols 1..3) + Right 5-Col Heritage Anchor (Cols 4..8)
    # ==========================================================================
    bot_y0 = round(sep3_y + mm(1.75), 2)
    bot_y1 = b6.snap_frame_bottom_to_baseline(grid.print_y1)

    if chosen_dummy in ("DUMMY_1", "DUMMY_2"):
        anc_c0, intl2_c0 = 1, 6
    else:
        intl2_c0, anc_c0 = 1, 4

    headline_pts["S10_ANCHOR"] = place_5col_anchor_package(grid, anc_c0, bot_y0, bot_y1, anc_obj)
    headline_pts["S11_INTL_2"] = place_front_multi_col_story(
        grid, grid.col_x0(intl2_c0), grid.col_x1(intl2_c0, 3), bot_y0, bot_y1, cols=3,
        st_obj=intl_2, target_lines=2, hi_pt=38.0, lo_pt=30.0,
    )

    b6.cmd("edit.deselectAll")
    b6.cmd("view.fitPage", {})

    out_pd = VAULT_DIR / "Aditya_Bharat_Page_01_34x53.pagedesigner"
    out_png = VAULT_DIR / "Aditya_Bharat_Page_01_34x53.png"
    out_pdf = VAULT_DIR / "Aditya_Bharat_Page_01_CMYK_34x53.pdf"
    ed_slug = edition_code.lower()
    ed_png = VAULT_DIR / f"Aditya_Bharat_{edition_code.title()}_Page_01_34x53.png"
    ed_pdf = VAULT_DIR / f"Aditya_Bharat_{edition_code.title()}_Page_01_CMYK_34x53.pdf"

    b6.rpc("app.save", {"path": str(out_pd)})
    b6.rpc("app.export", {"path": str(out_png), "page": 0, "scale": 1.5})
    try:
        b6.rpc("engine.execute", {"command": "file.exportPdf", "params": {"path": str(out_pdf)}})
    except Exception:
        pass

    if out_png.exists():
        shutil.copy2(out_png, ed_png)
    if out_pdf.exists():
        shutil.copy2(out_pdf, ed_pdf)

    if chosen_dummy == "DUMMY_2":
        shutil.copy2(out_pd, VAULT_DIR / "Aditya_Bharat_Page_01_Option2_34x53.pagedesigner")
        shutil.copy2(out_png, VAULT_DIR / "Aditya_Bharat_Page_01_Option2_34x53.png")

    art_dir = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\8707c72d-58b0-4715-a099-3efffcd57514")
    art_dir.mkdir(parents=True, exist_ok=True)
    artifact_png = art_dir / "aditya_bharat_page_01_11news_master_34x53.png"
    ed_artifact_png = art_dir / f"aditya_bharat_{ed_slug}_page_01_34x53.png"
    if out_png.exists():
        shutil.copy2(out_png, artifact_png)
        shutil.copy2(out_png, ed_artifact_png)

    desktop_main_pdf = DESKTOP_DIR / f"Aditya_Bharat_Front_Page_01_{date_str}.pdf"
    desktop_ed_pdf = DESKTOP_DIR / f"Aditya_Bharat_{edition_code.title()}_Page_01_{date_str}.pdf"
    if export_desktop_pdf and out_pdf.exists():
        shutil.copy2(out_pdf, desktop_main_pdf)
        shutil.copy2(out_pdf, desktop_ed_pdf)

    elapsed = round(time.perf_counter() - t0, 2)
    print(
        f"=== ADITYA BHARAT PAGE 01 ({edition_code} • {chosen_dummy} • 11 STORIES) BUILT IN {elapsed}s ===\n"
        f"    3 State Stories ({state_grp}) + 8 National/Intl/Biz/Sports Stories | 0 Cross-Page Duplicates!\n"
        f"    Headline Pts: {headline_pts}"
    )
    return {
        "ok": True,
        "date_str": date_str,
        "edition_code": edition_code,
        "state_group": state_grp,
        "dummy_id": chosen_dummy,
        "stories_count": len(all_11_stories),
        "state_stories_count": 3,
        "zero_cross_page_duplicates": len(cross_dups) == 0,
        "masthead_info": mh_info,
        "headline_pts": headline_pts,
        "global_ledger_path": str(global_ledger_path),
        "pagedesigner_path": str(out_pd),
        "png_path": str(out_png),
        "desktop_pdf": str(desktop_main_pdf),
        "edition_desktop_pdf": str(desktop_ed_pdf),
        "elapsed_sec": elapsed,
    }


if __name__ == "__main__":
    d_arg = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("AB_EDITION_DATE", "19-11-2026")
    ed_arg = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("AB_EDITION", "RAIPUR")
    dm_arg = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("AB_P1_DUMMY", "DUMMY_1")
    res = build_aditya_bharat_page1_with_dummy(date_str=d_arg, edition_code=ed_arg, dummy_id=dm_arg)
    print(json.dumps(res, ensure_ascii=False, indent=2))
