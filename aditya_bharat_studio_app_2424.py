# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — 8-PAGE MASTER SYSTEM, DUMMY BLUEPRINT & 5-IN-1 AUTOMATION STUDIO
==============================================================================================
Dedicated Non-Clashing Port : http://127.0.0.1:2424  (http://localhost:2424)
Page Designer TCP RPC Port  : 47123 (auto-launches pagedesigner.exe & brings window to front)
Vault Directory             : E:\RND\ADB HINDI EDITION\ADITYA_BHARAT_DESIGN_VAULT

Includes all 5 Advanced Capabilities:
  1. Live Browser Story / Headline / Subhead / Body / Photo Editor
  2. Live IANS Hindi Agency & 4-City Local Pool Connector (Swap Slot & 1-Click Page Auto-Fill)
  3. Dynamic Commercial Display Ad Grid Reflow Engine (Quarter-Page, Half-Page, Strip, Skybus)
  4. Cutout / Transparent PNG Silhouette Contour Text-Wrap Engine (WrapMode::Contour)
  5. No-Code Visual Drag-and-Drop Custom Layout Dummy Builder -> Live Page Designer Draw
"""

import base64
import ctypes
import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VAULT_DIR = Path(__file__).resolve().parent
if str(VAULT_DIR) not in sys.path:
    sys.path.insert(0, str(VAULT_DIR))

import ab_engine_extensions as ext
import ab_chhattisgarh_10x2_engine as cg_eng
import pd_cross_platform as pd_cp

STUDIO_PORT = 2424
PD_RPC_PORT = 47123

BUILD_LOCK = threading.Lock()
BUILD_STATUS = {
    "running": False,
    "current_task": "",
    "last_log": "आदित्य भारत 8-पेज सुपर-स्टूडियो तैयार है (Port 2424)। सभी 5 नए ऑटोमेशन मॉड्यूल (Live Editor, IANS Wire, Ad Reflow, Cutout Contour Wrap, और Visual Dummy Builder) सक्रिय हैं!",
    "last_updated": time.strftime("%H:%M:%S"),
}

PAGE_Catalog = [
    {
        "id": "page_01",
        "folio": "01",
        "title_hi": "पेज 01 — फ्रंट पेज (11 खबरें • 4 Rotating Dummies + CM/State + Global Non-Repeat)",
        "section_hi": "मुख्य पृष्ठ",
        "script": "ab_front_page1_4dummies_engine.py",
        "pd_file": "Aditya_Bharat_Page_01_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_01_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_01_CMYK_34x53.pdf",
        "stories_count": 11,
        "min_head_pt": "30.5 pt",
        "max_head_pt": "52.0 pt",
        "layout_tag": "6cm 7-Edition मास्टहेड + 4 रोटेटिंग डमी (DUMMY 1..4) + 3 राज्य/CM खबरें + 8 राष्ट्रीय/विदेश/कारोबार/खेल खबरें (अंदर के पेजों पर 0% रिपीटेशन)",
        "summary_hi": "पेज 01 ('फ्रंट पेज' — 11 खबरें • 4 रोटेटिंग डमी टेम्पलेट): रायपुर/बिलासपुर/राजनांदगांव संस्करण होने पर छत्तीसगढ़ के मुख्यमंत्री व राज्य की 3 बड़ी खबरें (भोपाल/इंदौर पर म.प्र., जयपुर पर राजस्थान, दिल्ली पर एनसीआर की 3 खबरें) + 8 राष्ट्रीय, अंतरराष्ट्रीय, कारोबार व खेल खबरें। पेज 01 पर लगी कोई भी खबर पेज 02–03, पेज 05 (प्रादेशिक), पेज 06 (कारोबार), पेज 07 (खेल) या पेज 08 (देश-विदेश) पर कभी रिपीट नहीं होती!",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 6.0, "kind": "masthead_front", "title": "ZONE 1: 6.0 cm डायनामिक 7-संस्करण मास्टहेड (दैनिक आदित्य भारत • वर्ष/अंक +1 ऑटो-रोलओवर)", "meta": "Cols 1..8 | 32.0 × 6.0 cm | रायपुर / नई दिल्ली / बिलासपुर / भोपाल / जयपुर / इंदौर / राजनांदगांव"},
            {"col": 1, "span": 6, "y0": 7.0, "h": 9.2, "kind": "flyer", "title": "STORY 1 (6-Col National Flyer): पचास प्रमुख शहरों में दौड़ेगी हाई-स्पीड ग्रीन मेट्रो", "meta": "Cols 1..6 | 9.2 cm | 48.0pt Headline + Cols 3..4 Photo", "slot_idx": 0},
            {"col": 7, "span": 2, "y0": 7.0, "h": 9.2, "kind": "story", "title": "STORY 2 (State #1 • 2-Col): नवा रायपुर में बनेगा देश का एआई हब", "meta": "Cols 7..8 | 9.2 cm | 36.0pt Headline", "slot_idx": 1},
            {"col": 1, "span": 4, "y0": 16.55, "h": 14.6, "kind": "lead", "title": "STORY 3 (5-Col Main Lead): केंद्र का बड़ा फैसला : तीन करोड़ परिवारों को मिलेंगे सौर ऊर्जा युक्त पक्के आवास", "meta": "Cols 1..4 Body + Cols 2..3 Photo | 47.5pt Headline", "slot_idx": 2},
            {"col": 5, "span": 1, "y0": 19.2, "h": 11.95, "kind": "gray_box", "title": "योजना के मुख्य बिंदु (Col 5)", "meta": "5-Col लीड के आखिरी Col 5 में फुल-हाइट 40% Gray Box"},
            {"col": 6, "span": 3, "y0": 16.55, "h": 7.15, "kind": "story", "title": "STORY 4 (State CM #2 • 3-Col): साय कैबिनेट का फैसला : छत्तीसगढ़ में पचास हजार पदों पर समयबद्ध भर्ती", "meta": "Cols 6..8 | 7.15 cm | 30.5pt Headline", "slot_idx": 3},
            {"col": 6, "span": 3, "y0": 24.05, "h": 7.1, "kind": "story", "title": "STORY 5 (Sports • 3-Col): चैंपियंस ट्रॉफी और टेस्ट फाइनल के लिए बीसीसीआई का रोडमैप", "meta": "Cols 6..8 | 7.1 cm | 35.0pt Headline", "slot_idx": 4},
            {"col": 1, "span": 2, "y0": 31.5, "h": 9.8, "kind": "story", "title": "STORY 6 (State #3 • 2-Col): रायपुर से चलेंगी नई वंदे भारत ट्रेनें", "meta": "Cols 1..2 | 9.8 cm | 36.0pt Headline", "slot_idx": 5},
            {"col": 3, "span": 2, "y0": 31.5, "h": 9.8, "kind": "story", "title": "STORY 7 (Business #1 • 2-Col): विदेशी मुद्रा भंडार ने रचा नया रिकॉर्ड", "meta": "Cols 3..4 | 9.8 cm | 36.0pt Headline", "slot_idx": 6},
            {"col": 5, "span": 2, "y0": 31.5, "h": 9.8, "kind": "story", "title": "STORY 8 (Business #2 • 2-Col): पंद्रह नए देशों में यूपीआई सेवा शुरू", "meta": "Cols 5..6 | 9.8 cm | 36.0pt Headline", "slot_idx": 7},
            {"col": 7, "span": 2, "y0": 31.5, "h": 9.8, "kind": "story", "title": "STORY 9 (International #1 • 2-Col): भारत व यूरोपीय संघ में व्यापार समझौता", "meta": "Cols 7..8 | 9.8 cm | 36.0pt Headline", "slot_idx": 8},
            {"col": 1, "span": 5, "y0": 41.65, "h": 10.35, "kind": "anchor", "title": "STORY 10 (5-Col Heritage Anchor): काशी से रामेश्वरम तक पांच नए पर्यटन कॉरिडोर शुरू", "meta": "Cols 1..5 | 10.35 cm | 36.0pt Headline + Cols 3..4 Photo", "slot_idx": 9},
            {"col": 6, "span": 3, "y0": 41.65, "h": 10.35, "kind": "story", "title": "STORY 11 (International #2 • 3-Col): सुरक्षा परिषद में भारत की स्थायी दावेदारी को बड़ा समर्थन", "meta": "Cols 6..8 | 10.35 cm | 37.0pt Headline", "slot_idx": 10}
        ]
    },
    {
        "id": "page_01_opt2",
        "folio": "01-B",
        "title_hi": "पेज 01 — फ्रंट पेज (Option 2 Variant)",
        "section_hi": "मुख्य पृष्ठ (विकल्प 2)",
        "script": "build_aditya_bharat_page1_option2.py",
        "pd_file": "Aditya_Bharat_Page_01_Option2_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_01_Option2_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_01_Option2_CMYK_34x53.pdf",
        "stories_count": 7,
        "min_head_pt": "34.0 pt",
        "max_head_pt": "74.0 pt",
        "layout_tag": "फ्रंट पेज विकल्प-2 (6cm मास्टहेड + 8-Col फ्लायर + अल्टरनेट लीड)",
        "summary_hi": "फ्रंट पेज का दूसरा वैकल्पिक मास्टर लेआउट — 6.0 cm मास्टहेड, 8-कॉलम फ्लायर, 5-कॉलम लीड और 1+5+2 बॉटम एंकर।",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 6.0, "kind": "masthead_front", "title": "ZONE 1: फ्रंट पेज मास्टहेड स्पेस (Option 2)", "meta": "Cols 1..8 | 32.0 × 6.0 cm"},
            {"col": 1, "span": 8, "y0": 7.0, "h": 12.5, "kind": "flyer", "title": "STORY 1: 8-कॉलम टॉप फ्लायर पैकेज", "meta": "Cols 1..8 | 12.5 cm | 18pt Subhead + 64pt Headline + Cols 4..5 Photo", "slot_idx": 0},
            {"col": 1, "span": 1, "y0": 19.8, "h": 21.85, "kind": "gray_box", "title": "40% Gray लीड बॉक्स", "meta": "Col 1 | 21.85 cm | 2.5mm इनसेट"},
            {"col": 2, "span": 4, "y0": 19.8, "h": 21.85, "kind": "lead", "title": "STORY 2: 5-कॉलम मेन लीड (Option 2 Package)", "meta": "Cols 1..5 | 21.85 cm | 74pt Headline + Photo + Box", "slot_idx": 1},
            {"col": 6, "span": 3, "y0": 19.8, "h": 11.2, "kind": "story_photo", "title": "STORY 3: दाएं 3-कॉलम सेकंड लीड", "meta": "Cols 6..8 | 11.2 cm | 42pt Headline + Photo", "slot_idx": 2},
            {"col": 6, "span": 2, "y0": 31.3, "h": 10.35, "kind": "story", "title": "STORY 4: 2-Col खबर", "meta": "Cols 6..7 | 10.35 cm | 36pt Headline", "slot_idx": 3},
            {"col": 8, "span": 1, "y0": 31.3, "h": 10.35, "kind": "story", "title": "STORY 5: 1-Col खबर", "meta": "Col 8 | 10.35 cm | 34pt Headline", "slot_idx": 4},
            {"col": 1, "span": 1, "y0": 42.0, "h": 10.0, "kind": "story", "title": "STORY 6: 1-Col खबर", "meta": "Col 1 | 10.0 cm | 34pt Headline", "slot_idx": 5},
            {"col": 2, "span": 5, "y0": 42.0, "h": 10.0, "kind": "anchor", "title": "STORY 7: बॉटम 5-कॉलम सेंटर एंकर", "meta": "Cols 2..6 | 10.0 cm | 48pt Headline + Photo", "slot_idx": 6},
            {"col": 7, "span": 2, "y0": 42.0, "h": 10.0, "kind": "story", "title": "STORY 8: दाएं 2-Col खबर", "meta": "Cols 7..8 | 10.0 cm | 36pt Headline", "slot_idx": 7}
        ]
    },
    {
        "id": "page_02",
        "folio": "02",
        "title_hi": "पेज 02 — छत्तीसगढ़ राजधानी (18-11-2026 • 10 खबरें)",
        "section_hi": "छत्तीसगढ़",
        "script": "ab_chhattisgarh_10x2_engine.py",
        "pd_file": "Aditya_Bharat_Page_02_Mahanagar_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_02_Mahanagar_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_02_Mahanagar_CMYK_34x53.pdf",
        "stories_count": 10,
        "min_head_pt": "30.0 pt",
        "max_head_pt": "53.5 pt",
        "layout_tag": "6+2 टॉप फ्लायर बैंड + 5-Col लीड (Col 5 में Gray Box) + दाएं 3-Col स्टैक + 3+2+3 मिड + 5+3 एंकर (10 खबरें)",
        "summary_hi": "18-11-2026 छत्तीसगढ़ विशेष (10 खबरें): ऊपर 6-कॉलम मेट्रो लाइट फ्लायर + 2-कॉलम बिलासपुर रेल खबर, बीच में 5-कॉलम नई औद्योगिक नीति लीड (आखिरी Col 5 में Gray Box) + दाएं बस्तर व भिलाई की 2 खबरें, नीचे 3+2+3 (कोरबा, दुर्ग, एम्स रायपुर) और बॉटम में 5+3 सिरपुर इको-हेरिटेज एंकर व राजनांदगांव हॉकी खबर।",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 1.5, "kind": "masthead_inside", "title": "1.5 cm रनिंग मास्टहेड : [छत्तीसगढ़] | आदित्य भारत | रायपुर, बुधवार, 18 नवंबर 2026 | 02", "meta": "Cols 1..8 | 1.5 cm | नीचे 2.0pt 60% Gray Rule"},
            {"col": 1, "span": 6, "y0": 2.85, "h": 9.3, "kind": "flyer", "title": "STORY 1: नवा रायपुर से दुर्ग तक मेट्रो लाइट कॉरिडोर के सर्वे को हरी झंडी (6-Col Flyer)", "meta": "Cols 1..6 | 9.3 cm | 37.5pt Headline + Cols 3..4 Photo", "slot_idx": 0},
            {"col": 7, "span": 2, "y0": 2.85, "h": 9.3, "kind": "story", "title": "STORY 2: बिलासपुर जोन को मिलीं तीन नई ट्रेनें (2-Col)", "meta": "Cols 7..8 | 9.3 cm | 36.0pt Headline", "slot_idx": 1},
            {"col": 1, "span": 4, "y0": 12.5, "h": 15.2, "kind": "lead", "title": "STORY 3: छत्तीसगढ़ की नई औद्योगिक नीति में हरित इस्पात व आईटी पर बड़ा दांव (5-Col Lead)", "meta": "Cols 1..4 Body + Cols 2..3 Photo | 53.5pt Headline", "slot_idx": 2},
            {"col": 5, "span": 1, "y0": 15.2, "h": 12.5, "kind": "gray_box", "title": "नीति के प्रमुख बिंदु (Col 5)", "meta": "आखिरी Col 5 में फुल-हाइट 40% Gray Box"},
            {"col": 6, "span": 3, "y0": 12.5, "h": 7.4, "kind": "story", "title": "STORY 4: बस्तर के साठ गांवों में पहुंची पक्की सड़क व बिजली (3-Col)", "meta": "Cols 6..8 | 7.4 cm | 36.0pt Headline", "slot_idx": 3},
            {"col": 6, "span": 3, "y0": 20.25, "h": 7.45, "kind": "story", "title": "STORY 5: भिलाई संयंत्र ने रेल पटरी उत्पादन में रचा इतिहास (3-Col)", "meta": "Cols 6..8 | 7.45 cm | 36.0pt Headline", "slot_idx": 4},
            {"col": 1, "span": 3, "y0": 28.05, "h": 11.6, "kind": "story_photo", "title": "STORY 6: कोरबा में नए ताप विद्युत संयंत्र का निर्माण तेज (3-Col Photo)", "meta": "Cols 1..3 | 11.6 cm | 36.0pt Headline + Photo", "slot_idx": 5},
            {"col": 4, "span": 2, "y0": 28.05, "h": 11.6, "kind": "story", "title": "STORY 7: आईआईटी भिलाई में नया रोबोटिक्स केंद्र शुरू (2-Col)", "meta": "Cols 4..5 | 11.6 cm | 30.0pt Headline", "slot_idx": 6},
            {"col": 6, "span": 3, "y0": 28.05, "h": 11.6, "kind": "story", "title": "STORY 8: एम्स रायपुर में रोबोटिक सर्जरी यूनिट प्रारंभ (3-Col)", "meta": "Cols 6..8 | 11.6 cm | 36.0pt Headline", "slot_idx": 7},
            {"col": 1, "span": 5, "y0": 40.0, "h": 12.0, "kind": "anchor", "title": "STORY 9: सिरपुर व चित्रकोट जुड़ेंगे इको-हेरिटेज सर्किट से (5-Col Anchor)", "meta": "Cols 1..5 | 12.0 cm | 40.5pt Headline + Cols 3..4 Photo", "slot_idx": 8},
            {"col": 6, "span": 3, "y0": 40.0, "h": 12.0, "kind": "story", "title": "STORY 10: राजनांदगांव व रायपुर में हॉकी अकादमी का विस्तार (3-Col)", "meta": "Cols 6..8 | 12.0 cm | 36.0pt Headline", "slot_idx": 9}
        ]
    },
    {
        "id": "page_03",
        "folio": "03",
        "title_hi": "पेज 03 — छत्तीसगढ़ प्रादेशिक (18-11-2026 • 10 खबरें)",
        "section_hi": "प्रादेशिक",
        "script": "ab_chhattisgarh_10x2_engine.py",
        "pd_file": "Aditya_Bharat_Page_03_Pradeshik_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_03_Pradeshik_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_03_Pradeshik_CMYK_34x53.pdf",
        "stories_count": 10,
        "min_head_pt": "30.0 pt",
        "max_head_pt": "48.5 pt",
        "layout_tag": "No-Flyer Vertical Start: बाएं 5-Col धान खरीदी लीड (Col 5 में Gray Box) + 3+2 सब-बैंड + दाएं 3-Col स्टैक + 2+4+2 मिड + 2+6 एंकर (10 खबरें)",
        "summary_hi": "18-11-2026 छत्तीसगढ़ प्रादेशिक (10 खबरें): ऊपर फ्लायर के बिना सीधा बाएं 5-कॉलम धान खरीदी वर्टिकल लीड (आखिरी Col 5 में किसान सुविधा बॉक्स), नीचे धमतरी व सरगुजा की 3+2 खबरें, दाएं बिलासपुर हाईकोर्ट व रायगढ़ की 2 खबरें, बीच में 2+4+2 (कांकेर, कांगेर घाटी पर्यटन, कवर्धा) और नीचे 2+6 (बस्तर ढोकरा शिल्प + पुरखौती मुक्तांगन ग्रैंड एंकर)।",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 1.5, "kind": "masthead_inside", "title": "1.5 cm रनिंग मास्टहेड : [प्रादेशिक] | आदित्य भारत | रायपुर, बुधवार, 18 नवंबर 2026 | 03", "meta": "Cols 1..8 | 1.5 cm | नीचे 2.0pt 60% Gray Rule"},
            {"col": 1, "span": 4, "y0": 2.85, "h": 15.65, "kind": "lead", "title": "STORY 1: छत्तीसगढ़ में धान खरीदी महाअभियान तेज, किसानों को सीधा भुगतान (5-Col Vertical Lead)", "meta": "Cols 1..4 Body + Cols 2..3 Photo | 48.5pt Headline", "slot_idx": 0},
            {"col": 5, "span": 1, "y0": 5.5, "h": 13.0, "kind": "gray_box", "title": "किसान सुविधा केंद्र (Col 5)", "meta": "आखिरी Col 5 में फुल-हाइट 40% Gray Box"},
            {"col": 1, "span": 3, "y0": 18.85, "h": 8.35, "kind": "story", "title": "STORY 2: गंगरेल और महानदी नहरों से दो लाख हेक्टेयर सिंचाई (3-Col)", "meta": "Cols 1..3 | 8.35 cm | 34.0pt Headline", "slot_idx": 1},
            {"col": 4, "span": 2, "y0": 18.85, "h": 8.35, "kind": "story", "title": "STORY 3: सरगुजा-वाराणसी फोर-लेन सड़क का निर्माण तेज (2-Col)", "meta": "Cols 4..5 | 8.35 cm | 31.0pt Headline", "slot_idx": 2},
            {"col": 6, "span": 3, "y0": 2.85, "h": 12.8, "kind": "story_photo", "title": "STORY 4: छत्तीसगढ़ हाईकोर्ट डिजिटल ई-सुनवाई में देश में अग्रणी (3-Col Photo)", "meta": "Cols 6..8 | 12.8 cm | 36.0pt Headline + Photo", "slot_idx": 3},
            {"col": 6, "span": 3, "y0": 16.0, "h": 11.2, "kind": "story", "title": "STORY 5: रायगढ़ व जांजगीर में नए मल्टी-मॉडल लॉजिस्टिक्स हब (3-Col)", "meta": "Cols 6..8 | 11.2 cm | 35.0pt Headline", "slot_idx": 4},
            {"col": 1, "span": 2, "y0": 27.55, "h": 11.65, "kind": "story", "title": "STORY 6: बस्तर के मिलेट्स उत्पादों की महानगरों में भारी मांग (2-Col)", "meta": "Cols 1..2 | 11.65 cm | 33.0pt Headline", "slot_idx": 5},
            {"col": 3, "span": 4, "y0": 27.55, "h": 11.65, "kind": "story_photo", "title": "STORY 7: कांगेर घाटी और कोटमसर गुफाओं में पर्यटकों की भीड़ (4-Col Package)", "meta": "Cols 3..6 | 11.65 cm | 38.0pt Headline + Cols 4..5 Photo", "slot_idx": 6},
            {"col": 7, "span": 2, "y0": 27.55, "h": 11.65, "kind": "story", "title": "STORY 8: कवर्धा के गन्ना किसानों को एथेनॉल संयंत्र से बोनस (2-Col)", "meta": "Cols 7..8 | 11.65 cm | 33.0pt Headline", "slot_idx": 7},
            {"col": 1, "span": 2, "y0": 39.55, "h": 12.45, "kind": "story", "title": "STORY 9: बस्तर के ढोकरा व लौह शिल्प को मिला जीआई टैग (2-Col)", "meta": "Cols 1..2 | 12.45 cm | 33.0pt Headline", "slot_idx": 8},
            {"col": 3, "span": 6, "y0": 39.55, "h": 12.45, "kind": "anchor", "title": "STORY 10: पुरखौती मुक्तांगन में जनजातीय संस्कृति संग्रहालय का लोकार्पण (6-Col Anchor)", "meta": "Cols 3..8 | 12.45 cm | 42.0pt Headline + Cols 5..6 Photo", "slot_idx": 9}
        ]
    },
    {
        "id": "page_04",
        "folio": "04",
        "title_hi": "पेज 04 — संपादकीय (Daily Editorial, जीवन मंत्र, गीता श्लोक, मंथन व कटाक्ष)",
        "section_hi": "संपादकीय",
        "script": "ab_sampadakiya_page4_engine.py",
        "pd_file": "Aditya_Bharat_Page_04_Sampadakiya_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_04_Sampadakiya_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_04_Sampadakiya_CMYK_34x53.pdf",
        "stories_count": 8,
        "min_head_pt": "30.0 pt",
        "max_head_pt": "45.5 pt",
        "layout_tag": "सेंटर ग्राफिक लोगो मास्टहेड + बाएं 10cm संपादकीय/जीवन मंत्र/निष्कर्ष + दाएं 20cm गीता श्लोक/3-Col मंथन लीड/2 आलेख/शायरी व कटाक्ष कार्टून",
        "summary_hi": "पेज 04 ('संपादकीय') — ऊपर 1.5 cm रनिंग मास्टहेड के सेंटर में आधिकारिक 'आदित्य भारत' ग्राफिक लोगो; बाएं 10.0 cm स्ट्रिप में मुख्य संपादकीय 1, 'जीवन मंत्र', तीसरा संपादकीय और नीचे 'निष्कर्ष' बॉक्स; दाएं 20.0 cm क्षेत्र में '॥ श्रीमद्भगवद्गीता ॥' श्लोक व अर्थ, 3-कॉलम लीड आलेख ('विशेष मंथन' + लेखक फोटो + इलस्ट्रेशन), बीच में 2 बराबर वैचारिक आलेख, और नीचे 'अदब और चिंतन (शेर, नज़्म व ग़ज़ल)' तथा 'कटाक्ष • तीखे तेवर (व्यंग्य कोना)' कार्टून बॉक्स।",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 1.5, "kind": "masthead_inside", "title": "1.5 cm रनिंग मास्टहेड : [संपादकीय] | आदित्य भारत (Centered Graphic Logo) | रायपुर, गुरुवार, 19 नवंबर 2026 | 04", "meta": "Cols 1..8 | 1.5 cm | सेंटर में आदित्य भारत ग्राफिक लोगो | नीचे 2.0pt 60% Gray Rule"},
            {"col": 1, "span": 2, "y0": 2.85, "h": 14.0, "kind": "editorial", "title": "EDITORIAL 1: मुख्य संपादकीय (32pt DB Rasrand Bold + Drop Cap)", "meta": "Left 10.0 cm Strip | 32.0pt Headline", "slot_idx": 0},
            {"col": 1, "span": 2, "y0": 17.3, "h": 24.5, "kind": "editorial", "title": "COLUMN 2: 'जीवन मंत्र • आत्मचिंतन एवं प्रेरणा' (30pt Headline + 4.8×4.8cm Illus)", "meta": "Left 10.0 cm Strip | Red Header + Drop Cap + Photo", "slot_idx": 1},
            {"col": 1, "span": 2, "y0": 42.1, "h": 9.9, "kind": "editorial", "title": "EDITORIAL 3 + निष्कर्ष बॉक्स (30pt Headline + Bottom Gray Pointer Box)", "meta": "Left 10.0 cm Strip | नीचे 2-लाइन बोल्ड 'निष्कर्ष'", "slot_idx": 2},
            {"col": 3, "span": 6, "y0": 2.85, "h": 3.4, "kind": "gray_box", "title": "॥ श्रीमद्भगवद्गीता ॥ (दैनिक संस्कृत श्लोक + हिंदी अर्थ)", "meta": "Right 20.0 cm Top | दोनों ओर कमल अलंकरण + श्लोक व अर्थ"},
            {"col": 3, "span": 6, "y0": 6.5, "h": 20.25, "kind": "lead", "title": "LEAD OPINION 4: 'विशेष मंथन' — 3-कॉलम मुख्य वैचारिक आलेख (45.5pt Headline + लेखक फोटो + इलस्ट्रेशन)", "meta": "Right 20.0 cm Layer 1 | 45.5pt DB Rasrand Bold + Author Byline + 2-Col Photo", "slot_idx": 3},
            {"col": 3, "span": 3, "y0": 27.1, "h": 14.7, "kind": "story_photo", "title": "OPINION 5 (Mid-Left): पर्यावरण/आर्थिक सरोकार आलेख (30pt Headline + 4.6×4.6cm Photo)", "meta": "Right 20.0 cm Layer 2 Left | 2-Col Text + Photo", "slot_idx": 4},
            {"col": 6, "span": 3, "y0": 27.1, "h": 14.7, "kind": "story_photo", "title": "OPINION 6 (Mid-Right): शिक्षा एवं भविष्य आलेख (30pt Headline + 4.6×4.6cm Photo)", "meta": "Right 20.0 cm Layer 2 Right | 2-Col Text + Photo", "slot_idx": 5},
            {"col": 3, "span": 2, "y0": 42.1, "h": 9.9, "kind": "anchor", "title": "LITERARY 7: 'अदब और चिंतन • शेर, नज़्म व ग़ज़ल' (अर्थ सहित)", "meta": "Right 20.0 cm Layer 3 Left | १. आज का शेर, २. नज़्म, ३. ग़ज़ल"},
            {"col": 5, "span": 4, "y0": 42.1, "h": 9.9, "kind": "anchor", "title": "CARTOON 8: 'कटाक्ष • तीखे तेवर (व्यंग्य कोना)' (12cm Framed Cartoon Box)", "meta": "Right 20.0 cm Layer 3 Right | व्यंग्य कार्टून + पंचलाइन"}
        ]
    },
    {
        "id": "page_05",
        "folio": "05",
        "title_hi": "पेज 05 — प्रादेशिक (MP + CG + Rajasthan + Delhi • 12 खबरें)",
        "section_hi": "प्रादेशिक",
        "script": "ab_pradeshik_page5_12news_engine.py",
        "pd_file": "Aditya_Bharat_Page_05_Rashtriya_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_05_Rashtriya_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_05_Rashtriya_CMYK_34x53.pdf",
        "stories_count": 12,
        "min_head_pt": "31.0 pt",
        "max_head_pt": "52.5 pt",
        "layout_tag": "सेंटर लोगो मास्टहेड + Band 1 (3+5 दिल्ली फ्लायर) + Band 2 (5-Col MP लीड व Col 5 में चार राज्यों की झलक + 3-Col स्टैक) + Band 3 (2+2+2+2) + Band 4 (3+3+2 • कुल 12 खबरें)",
        "summary_hi": "पेज 05 ('प्रादेशिक') — मध्य प्रदेश, छत्तीसगढ़, राजस्थान और नई दिल्ली की 12 प्रमुख व नॉन-रिपीटिंग खबरें (पेज 2-3 या किसी अन्य पेज से 0% रिपीटेशन): बैंड 1 में बाएं 3-कॉलम जयपुर-दिल्ली ई-बस कॉरिडोर व दाएं 5-कॉलम दिल्ली यमुना रिवरफ्रंट/मेट्रो फ्लायर; बैंड 2 में बाएं 5-कॉलम मध्य प्रदेश केन-बेतवा व नर्मदा लिंक मुख्य लीड (आखिरी Col 5 में 'चार राज्यों की झलक' ग्रे बॉक्स) तथा दाएं अंबिकापुर रेल व जैसलमेर सोलर पार्क की 2 खबरें; बैंड 3 में 2+2+2+2 की 4 खबरें (उज्जैन/ओरछा, बस्तर कोसा/काजू, एम्स दिल्ली, उदयपुर/कोटा); और बैंड 4 में 3+3+2 (जबलपुर ग्रीन बस, जयपुर हेरिटेज पर्यटन एंकर, और शासकीय स्कूलों में रोबोटिक्स लैब)।",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 1.5, "kind": "masthead_inside", "title": "1.5 cm रनिंग मास्टहेड : [प्रादेशिक] | आदित्य भारत (Centered Graphic Logo) | रायपुर, गुरुवार, 19 नवंबर 2026 | 05", "meta": "Cols 1..8 | 1.5 cm | सेंटर में आदित्य भारत ग्राफिक लोगो | नीचे 2.0pt 60% Gray Rule"},
            {"col": 1, "span": 3, "y0": 2.85, "h": 9.3, "kind": "story", "title": "STORY 1 (RJ • 3-Col): जयपुर-दिल्ली हाईवे पर इलेक्ट्रिक बस कॉरिडोर व चार्जिंग हब शुरू", "meta": "Cols 1..3 | 9.3 cm | 34.0pt Headline", "slot_idx": 0},
            {"col": 4, "span": 5, "y0": 2.85, "h": 9.3, "kind": "flyer", "title": "STORY 2 (DL • 5-Col Flyer): यमुना रिवरफ्रंट व दिल्ली मेट्रो विस्तार को मंजूरी", "meta": "Cols 4..8 | 9.3 cm | 40.5pt Headline + Cols 6..7 Photo", "slot_idx": 1},
            {"col": 1, "span": 4, "y0": 12.5, "h": 15.1, "kind": "lead", "title": "STORY 3 (MP • 5-Col Main Lead): मध्य प्रदेश में केन-बेतवा और नर्मदा लिंक से बदलेगी बुंदेलखंड की तस्वीर", "meta": "Cols 1..4 Body + Cols 2..3 Photo | 52.5pt Headline", "slot_idx": 2},
            {"col": 5, "span": 1, "y0": 15.2, "h": 12.4, "kind": "gray_box", "title": "चार राज्यों की झलक (Col 5)", "meta": "5-Col लीड के आखिरी Col 5 में फुल-हाइट 40% Gray Box"},
            {"col": 6, "span": 3, "y0": 12.5, "h": 7.35, "kind": "story", "title": "STORY 4 (CG • 3-Col): अंबिकापुर से बरवाडीह नई रेल लाइन के भूमि अधिग्रहण को हरी झंडी", "meta": "Cols 6..8 | 7.35 cm | 31.0pt Headline", "slot_idx": 3},
            {"col": 6, "span": 3, "y0": 20.2, "h": 7.4, "kind": "story", "title": "STORY 5 (RJ • 3-Col): थार मरुस्थल में दुनिया का सबसे बड़ा हाइब्रिड सोलर-विंड पार्क तैयार", "meta": "Cols 6..8 | 7.4 cm | 33.0pt Headline", "slot_idx": 4},
            {"col": 1, "span": 2, "y0": 27.95, "h": 11.6, "kind": "story", "title": "STORY 6 (MP • 2-Col): महाकाल लोक की तर्ज पर संवरेगा ओरछा", "meta": "Cols 1..2 | 11.6 cm | 33.0pt Headline", "slot_idx": 5},
            {"col": 3, "span": 2, "y0": 27.95, "h": 11.6, "kind": "story", "title": "STORY 7 (CG • 2-Col): बस्तर के काजू व कोसा सिल्क की मांग", "meta": "Cols 3..4 | 11.6 cm | 34.5pt Headline", "slot_idx": 6},
            {"col": 5, "span": 2, "y0": 27.95, "h": 11.6, "kind": "story", "title": "STORY 8 (DL • 2-Col): एम्स दिल्ली में नया कैंसर उपचार केंद्र", "meta": "Cols 5..6 | 11.6 cm | 36.0pt Headline", "slot_idx": 7},
            {"col": 7, "span": 2, "y0": 27.95, "h": 11.6, "kind": "story", "title": "STORY 9 (RJ • 2-Col): उदयपुर व कोटा में नए पर्यटन केंद्र", "meta": "Cols 7..8 | 11.6 cm | 36.0pt Headline", "slot_idx": 8},
            {"col": 1, "span": 3, "y0": 39.9, "h": 12.1, "kind": "story_photo", "title": "STORY 10 (MP • 3-Col Photo): जबलपुर और ग्वालियर में ग्रीन हाइड्रोजन बसों का संचालन प्रारंभ", "meta": "Cols 1..3 | 12.1 cm | 34.0pt Headline + Col 2 Photo", "slot_idx": 9},
            {"col": 4, "span": 3, "y0": 39.9, "h": 12.1, "kind": "anchor", "title": "STORY 11 (RJ • 3-Col Heritage Anchor): राजस्थान के किलों और झीलों में हेरिटेज पर्यटन ने तोड़ा रिकॉर्ड", "meta": "Cols 4..6 | 12.1 cm | 36.5pt Headline + Col 5 Photo", "slot_idx": 10},
            {"col": 7, "span": 2, "y0": 39.9, "h": 12.1, "kind": "story", "title": "STORY 12 (CG/DL • 2-Col): शासकीय स्कूलों में नई रोबोटिक्स लैब", "meta": "Cols 7..8 | 12.1 cm | 36.0pt Headline", "slot_idx": 11}
        ]
    },
    {
        "id": "page_06",
        "folio": "06",
        "title_hi": "पेज 06 — कारोबार (Full-Page Business News • 9 खबरें + बाजार मीटर)",
        "section_hi": "कारोबार",
        "script": "ab_karobar_page6_engine.py",
        "pd_file": "Aditya_Bharat_Page_06_Karobar_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_06_Karobar_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_06_Karobar_CMYK_34x53.pdf",
        "stories_count": 9,
        "min_head_pt": "30.5 pt",
        "max_head_pt": "58.0 pt",
        "layout_tag": "सेंटर लोगो मास्टहेड + Band 1 (2-Col बाजार मीटर + 6-Col फ्लायर) + Band 2 (3-Col स्टैक + 5-Col लीड व Col 8 में प्रमुख बिंदु) + Band 3 (2+2+2+2) + Band 4 (5+3 एंकर)",
        "summary_hi": "पेज 06 ('कारोबार') का विशेष फुल-पेज बिज़नेस लेआउट — ऊपर 1.5 cm रनिंग मास्टहेड में 'कारोबार' + सेंटर में 'आदित्य भारत' ग्राफिक लोगो; बैंड 1 में बाएं 2-कॉलम 'बाजार मीटर : सेंसेक्स और सर्राफा' बॉक्स व दाएं 6-कॉलम ऑटो/सेमीकंडक्टर निर्यात फ्लायर; बैंड 2 में बाएं 3-कॉलम में 2 बैंकिंग व ईवी निवेश खबरें तथा दाएं 5-कॉलम जीएसटी मुख्य लीड (आखिरी Col 8 में 'प्रमुख बिंदु' ग्रे बॉक्स); बैंड 3 में 2+2+2+2 की 4 सेक्टर खबरें (सर्राफा, एआई स्टार्टअप, प्रॉपर्टी, कृषि निर्यात); और बैंड 4 में 5+3 शेयर बाजार बीएसई एंकर व हरित ऊर्जा पैकेज।",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 1.5, "kind": "masthead_inside", "title": "1.5 cm रनिंग मास्टहेड : [कारोबार] | आदित्य भारत (Centered Graphic Logo) | रायपुर, गुरुवार, 19 नवंबर 2026 | 06", "meta": "Cols 1..8 | 1.5 cm | सेंटर में आदित्य भारत ग्राफिक लोगो | नीचे 2.0pt 60% Gray Rule"},
            {"col": 1, "span": 2, "y0": 2.85, "h": 10.6, "kind": "gray_box", "title": "बाजार मीटर : सेंसेक्स और सर्राफा", "meta": "Cols 1..2 | 10.6 cm | सेंसेक्स, निफ्टी, सोना 24K, चांदी, रुपया, ब्रेंट क्रूड, FII"},
            {"col": 3, "span": 6, "y0": 2.85, "h": 10.6, "kind": "flyer", "title": "STORY 1 (6-Col Flyer): सेमीकंडक्टर व ऑटो निर्यात में भारत की बड़ी छलांग", "meta": "Cols 3..8 | 10.6 cm | 44.5pt Headline + Cols 5..6 Photo", "slot_idx": 0},
            {"col": 1, "span": 3, "y0": 13.8, "h": 7.8, "kind": "story", "title": "STORY 2 (Left Top 3-Col): डिजिटल बैंकिंग से छोटे उद्यमों को बिना गारंटी तुरंत ऋण", "meta": "Cols 1..3 | 7.8 cm | 34.5pt Headline", "slot_idx": 1},
            {"col": 1, "span": 3, "y0": 21.95, "h": 7.85, "kind": "story", "title": "STORY 3 (Left Bot 3-Col): इलेक्ट्रिक वाहन और लिथियम बैटरी प्लांट में पांच अरब डॉलर निवेश", "meta": "Cols 1..3 | 7.85 cm | 31.5pt Headline", "slot_idx": 2},
            {"col": 4, "span": 4, "y0": 13.8, "h": 16.0, "kind": "lead", "title": "STORY 4 (5-Col Main Business Lead): जीएसटी संग्रह दो लाख करोड़ के पार, विनिर्माण क्षेत्र में नया उछाल", "meta": "Cols 4..7 Body + Cols 5..6 Photo | 58.0pt Headline", "slot_idx": 3},
            {"col": 8, "span": 1, "y0": 16.5, "h": 13.3, "kind": "gray_box", "title": "प्रमुख बिंदु (Col 8)", "meta": "5-Col लीड के आखिरी Col 8 में फुल-हाइट 40% Gray Box"},
            {"col": 1, "span": 2, "y0": 30.15, "h": 11.2, "kind": "story", "title": "STORY 5 (2-Col): त्योहारी मांग से सर्राफा बाजार में बढ़ी रौनक", "meta": "Cols 1..2 | 11.2 cm | 32.0pt Headline", "slot_idx": 4},
            {"col": 3, "span": 2, "y0": 30.15, "h": 11.2, "kind": "story", "title": "STORY 6 (2-Col): भारतीय एआई स्टार्टअप ने जुटाया रिकॉर्ड फंड", "meta": "Cols 3..4 | 11.2 cm | 30.5pt Headline", "slot_idx": 5},
            {"col": 5, "span": 2, "y0": 30.15, "h": 11.2, "kind": "story", "title": "STORY 7 (2-Col): छोटे शहरों में आवासीय प्रॉपर्टी की बिक्री बढ़ी", "meta": "Cols 5..6 | 11.2 cm | 32.5pt Headline", "slot_idx": 6},
            {"col": 7, "span": 2, "y0": 30.15, "h": 11.2, "kind": "story", "title": "STORY 8 (2-Col): कृषि व खाद्य निर्यात से किसानों की आय बढ़ी", "meta": "Cols 7..8 | 11.2 cm | 33.0pt Headline", "slot_idx": 7},
            {"col": 1, "span": 5, "y0": 41.7, "h": 10.3, "kind": "anchor", "title": "STORY 9 (5-Col Anchor): दलाल स्ट्रीट में विदेशी निवेशकों की लिवाली", "meta": "Cols 1..5 | 10.3 cm | 45.0pt Headline + Cols 3..4 BSE Photo", "slot_idx": 8},
            {"col": 6, "span": 3, "y0": 41.7, "h": 10.3, "kind": "story", "title": "STORY 10 (3-Col): सोलर उपकरण और हरित ऊर्जा में आत्मनिर्भर बनेगा नया भारत", "meta": "Cols 6..8 | 10.3 cm | 35.0pt Headline", "slot_idx": 8}
        ]
    },
    {
        "id": "page_07",
        "folio": "07",
        "title_hi": "पेज 07 — खेल संसार + सिने संसार (8 खेल + 3 फिल्म खबरें • 5 सिल्हूट कटआउट)",
        "section_hi": "खेल संसार",
        "script": "ab_khel_film_page7_engine.py",
        "pd_file": "Aditya_Bharat_Page_07_Khel_Sansar_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_07_Khel_Sansar_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_07_Khel_Sansar_CMYK_34x53.pdf",
        "stories_count": 11,
        "min_head_pt": "31.5 pt",
        "max_head_pt": "55.5 pt",
        "layout_tag": "सेंटर लोगो मास्टहेड + 8 खेल खबरें (3-Col क्रिकेट लीड फोटो + नीरज चोपड़ा/पीवी सिंधु/मनु भाकर सिल्हूट कटआउट) + नीचे 'सिने संसार' की 3 फिल्म खबरें (2 फिल्म स्टार कटआउट)",
        "summary_hi": "पेज 07 ('खेल संसार + सिने संसार') — कुल 11 खबरें (8 खेल + 3 फिल्म/मनोरंजन) और 5 सिल्हूट कटआउट (`WrapMode::Contour`): ऊपर 5-कॉलम क्रिकेट टेस्ट सीरीज लीड (3-कॉलम एक्शन फोटो + आखिरी Col 5 में 'मैच के बिंदु' ग्रे बॉक्स), दाएं नीरज चोपड़ा कटआउट व हॉकी खबर; बीच में पीवी सिंधु बैडमिंटन कटआउट, डी गुकेश शतरंज व हरमनप्रीत महिला क्रिकेट; नीचे रणजी ट्रॉफी व मनु भाकर शूटिंग कटआउट; और बॉटम में 'सिने संसार' बैनर के नीचे 3 फिल्म/ओटीटी खबरें (अमिताभ बच्चन व दीपिका पादुकोण सिल्हूट कटआउट के साथ)।",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 1.5, "kind": "masthead_inside", "title": "1.5 cm रनिंग मास्टहेड : [खेल संसार] | आदित्य भारत (Centered Graphic Logo) | रायपुर, गुरुवार, 19 नवंबर 2026 | 07", "meta": "Cols 1..8 | 1.5 cm | सेंटर में आदित्य भारत ग्राफिक लोगो | नीचे 2.0pt 60% Gray Rule"},
            {"col": 1, "span": 4, "y0": 2.85, "h": 16.8, "kind": "lead", "title": "STORY 1 (5-Col Cricket Lead): रोहित और बुमराह के दम पर भारत ने जीती ऐतिहासिक टेस्ट सीरीज", "meta": "Cols 1..4 Body + Cols 2..4 Action Photo | 55.5pt Headline", "slot_idx": 0},
            {"col": 5, "span": 1, "y0": 5.5, "h": 14.15, "kind": "gray_box", "title": "मैच के बिंदु (Col 5)", "meta": "5-Col लीड के आखिरी Col 5 में फुल-हाइट 40% Gray Box"},
            {"col": 6, "span": 3, "y0": 2.85, "h": 9.2, "kind": "story_photo", "title": "STORY 2 (3-Col Cutout): डायमंड लीग के नए सीजन के लिए नीरज चोपड़ा ने शुरू की तैयारी", "meta": "Cols 6..8 | 33.0pt Headline + नीरज चोपड़ा Silhouette Cutout", "slot_idx": 1},
            {"col": 6, "span": 3, "y0": 12.4, "h": 7.25, "kind": "story", "title": "STORY 3 (3-Col Hockey): एशियाई चैंपियंस ट्रॉफी में भारतीय हॉकी टीम की लगातार चौथी जीत", "meta": "Cols 6..8 | 33.5pt Headline", "slot_idx": 2},
            {"col": 1, "span": 3, "y0": 20.0, "h": 9.1, "kind": "story_photo", "title": "STORY 4 (3-Col Cutout): बैडमिंटन ओपन में लक्ष्य सेन और सिंधु क्वार्टर फाइनल में पहुंचे", "meta": "Cols 1..3 | 34.0pt Headline + पीवी सिंधु Silhouette Cutout", "slot_idx": 3},
            {"col": 4, "span": 2, "y0": 20.0, "h": 9.1, "kind": "story", "title": "STORY 5 (2-Col Chess): विश्व शतरंज में डी गुकेश ने बनाई बढ़त", "meta": "Cols 4..5 | 36.0pt Headline", "slot_idx": 4},
            {"col": 6, "span": 3, "y0": 20.0, "h": 9.1, "kind": "story", "title": "STORY 6 (3-Col Women Cricket): महिला क्रिकेट सीरीज के लिए हरमनप्रीत की टीम तैयार", "meta": "Cols 6..8 | 36.0pt Headline", "slot_idx": 5},
            {"col": 1, "span": 4, "y0": 29.45, "h": 8.6, "kind": "story", "title": "STORY 7 (4-Col Ranji): रणजी ट्रॉफी में मध्यप्रदेश व मुंबई की जीत", "meta": "Cols 1..4 | 37.5pt Headline", "slot_idx": 6},
            {"col": 5, "span": 4, "y0": 29.45, "h": 8.6, "kind": "story_photo", "title": "STORY 8 (4-Col Cutout): निशानेबाजी विश्व कप में मनु भाकर को स्वर्ण", "meta": "Cols 5..8 | 34.0pt Headline + मनु भाकर Silhouette Cutout", "slot_idx": 7},
            {"col": 1, "span": 3, "y0": 38.4, "h": 13.6, "kind": "anchor", "title": "STORY 9 (Film Cutout 1): ऐतिहासिक फिल्मों और लोक कथाओं पर बड़े बजट की तैयारी", "meta": "Cols 1..3 | 36.0pt Headline + अमिताभ बच्चन Silhouette Cutout", "slot_idx": 8},
            {"col": 4, "span": 3, "y0": 38.4, "h": 13.6, "kind": "anchor", "title": "STORY 10 (Film Cutout 2): अंतरराष्ट्रीय फिल्म महोत्सव में भारतीय सिनेमा का विशेष सम्मान", "meta": "Cols 4..6 | 33.0pt Headline + दीपिका पादुकोण Silhouette Cutout", "slot_idx": 9},
            {"col": 7, "span": 2, "y0": 38.4, "h": 13.6, "kind": "story", "title": "STORY 11 (Film/OTT 3): छोटे शहरों की कहानियों ने जीता दर्शकों का दिल", "meta": "Cols 7..8 | 31.5pt Headline", "slot_idx": 10}
        ]
    },
    {
        "id": "page_08",
        "folio": "08",
        "title_hi": "पेज 08 — देश-विदेश (Back Page — 12 Stories)",
        "section_hi": "देश-विदेश",
        "script": "build_aditya_bharat_page8_desh_videsh.py",
        "pd_file": "Aditya_Bharat_Page_08_Desh_Videsh_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_08_Desh_Videsh_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_08_Desh_Videsh_CMYK_34x53.pdf",
        "stories_count": 12,
        "min_head_pt": "32.0 pt",
        "max_head_pt": "58.0 pt",
        "layout_tag": "8-Col कूटनीति फ्लायर + बाएं 5-Col सामरिक लीड + दाएं 3-Col फीचर + 4+2 / 2+4 + 4+4 + 3+5 एंकर",
        "summary_hi": "अंतिम पृष्ठ पेज 08 ('देश-विदेश') पर 12 खबरों का खास लेआउट — ऊपर 8-कॉलम यूएन सुरक्षा परिषद फ्लायर, बाएं 5-कॉलम हिंद-प्रशांत नौसैनिक लीड (आखिरी Col 5 में 'सामरिक बिंदु' Gray Box) + दाएं Cols 6..8 में लंबा 3-कॉलम फीचर, मिड में 4+2 / 2+4 इंटरलॉक, नीचे 4+4 और बॉटम में 3+5 नासा-इसरो ग्रैंड स्पेस एंकर!",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 1.5, "kind": "masthead_inside", "title": "1.5 cm रनिंग मास्टहेड : [देश-विदेश] | आदित्य भारत | इंदौर, मंगलवार | 08", "meta": "Cols 1..8 | 1.5 cm | नीचे 2.0pt 60% Gray Rule"},
            {"col": 1, "span": 8, "y0": 2.85, "h": 8.6, "kind": "flyer", "title": "STORY 1: 8-कॉलम वर्ल्ड डिप्लोमेसी टॉप फ्लायर", "meta": "Cols 1..8 | 8.6 cm | 53.5pt Headline + Cols 4..5 UN Photo", "slot_idx": 0},
            {"col": 1, "span": 4, "y0": 11.8, "h": 15.0, "kind": "lead", "title": "STORY 2: बाएं 5-कॉलम सामरिक लीड (हिंद-प्रशांत नौसैनिक महाअभ्यास)", "meta": "Cols 1..4 Body + Cols 2..3 Navy Photo | 58.0pt Headline", "slot_idx": 1},
            {"col": 5, "span": 1, "y0": 14.5, "h": 12.3, "kind": "gray_box", "title": "सामरिक बिंदु (Col 5)", "meta": "लीड के आखिरी Col 5 में फुल-हाइट 40% Gray Box"},
            {"col": 6, "span": 3, "y0": 11.8, "h": 24.0, "kind": "story_photo", "title": "STORY 3: दाएं 3-कॉलम लंबा विशेष फीचर (अंटार्कटिका मैत्री-टू शोध केंद्र)", "meta": "Cols 6..8 | 24.0 cm | 36.0pt Headline + Antarctica Photo", "slot_idx": 2},
            {"col": 1, "span": 4, "y0": 27.15, "h": 8.7, "kind": "story", "title": "STORY 4: बाएं 4-Col पूर्वोत्तर 4 नए एयरपोर्ट व राजमार्ग", "meta": "Cols 1..4 | 8.7 cm | 35.0pt Headline", "slot_idx": 3},
            {"col": 5, "span": 1, "y0": 27.15, "h": 8.7, "kind": "story", "title": "STORY 5: ब्रिक्स मुद्रा व्यापार", "meta": "Col 5 | 8.7 cm | 34.0pt Headline", "slot_idx": 4},
            {"col": 1, "span": 4, "y0": 36.2, "h": 7.1, "kind": "story", "title": "STORY 6: भारत-जापान चिप समझौता व हरित ऊर्जा मॉडल (4-Col)", "meta": "Cols 1..4 | 7.1 cm | 33.0pt Headline", "slot_idx": 5},
            {"col": 5, "span": 4, "y0": 36.2, "h": 7.1, "kind": "story", "title": "STORY 7: प्रवासी भारतीयों के लिए 20 देशों में ई-सेवा केंद्र (4-Col)", "meta": "Cols 5..8 | 7.1 cm | 36.0pt Headline", "slot_idx": 6},
            {"col": 1, "span": 3, "y0": 43.65, "h": 8.35, "kind": "story", "title": "STORY 8: बाएं 3-Col विदेशी विवि में योग व दर्शन पीठ", "meta": "Cols 1..3 | 8.35 cm | 33.0pt Headline", "slot_idx": 7},
            {"col": 4, "span": 5, "y0": 43.65, "h": 8.35, "kind": "anchor", "title": "STORY 9: दाएं 5-कॉलम ग्रैंड स्पेस एंकर (नासा-इसरो मिशन)", "meta": "Cols 4..8 | 8.35 cm | 42.0pt Headline + ISRO Photo", "slot_idx": 8}
        ]
    }
]


def bring_page_designer_window_to_front():
    return pd_cp.focus_pagedesigner_window()


def check_page_designer_alive() -> dict:
    for port in (PD_RPC_PORT, 49200):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.6) as _s:
                return {"alive": True, "port": port}
        except Exception:
            pass
    return {"alive": False, "port": PD_RPC_PORT}


def ensure_page_designer_running() -> int:
    pd_cp.launch_pagedesigner("127.0.0.1", PD_RPC_PORT)
    pd_cp.focus_pagedesigner_window()
    st = check_page_designer_alive()
    if st["alive"]:
        return st["port"]
    raise RuntimeError("Page Designer (pagedesigner.exe) शुरू नहीं हो सका।")


def _rpc_call(s, f_in, method: str, params: dict = None) -> dict:
    payload = {"id": 1, "method": method, "params": params or {}}
    s.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
    return json.loads(f_in.readline())


def open_saved_file_in_page_designer(pd_filename: str, close_others: bool = True) -> dict:
    target = VAULT_DIR / pd_filename
    if not target.exists():
        return {"ok": False, "error": f"फाइल नहीं मिली: {target}"}
    port = ensure_page_designer_running()
    with socket.create_connection(("127.0.0.1", port), timeout=15.0) as s:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        f_in = s.makefile("r", encoding="utf-8")
        if close_others:
            for _ in range(12):
                try:
                    r_c = _rpc_call(s, f_in, "engine.execute", {"command": "file.close", "params": {"save": False}})
                    if not r_c.get("ok"):
                        break
                except Exception:
                    break
        resp = _rpc_call(s, f_in, "app.open", {"path": str(target)})
        _rpc_call(s, f_in, "engine.execute", {"command": "view.fitPage", "params": {}})
        _rpc_call(s, f_in, "ui.focus", {})
    bring_page_designer_window_to_front()
    return {"ok": True, "port": port, "file": str(target), "rpc": resp}


def open_all_8_pages_in_page_designer(mode: str = "book") -> dict:
    port = ensure_page_designer_running()
    combined_pd = VAULT_DIR / "Aditya_Bharat_Full_8Pages_34x53.pagedesigner"
    if mode == "book" and combined_pd.exists():
        with socket.create_connection(("127.0.0.1", port), timeout=20.0) as s:
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            f_in = s.makefile("r", encoding="utf-8")
            for _ in range(12):
                try:
                    r_c = _rpc_call(s, f_in, "engine.execute", {"command": "file.close", "params": {"save": False}})
                    if not r_c.get("ok"):
                        break
                except Exception:
                    break
            resp = _rpc_call(s, f_in, "app.open", {"path": str(combined_pd)})
            _rpc_call(s, f_in, "engine.execute", {"command": "window.panel", "params": {"panel": "pages"}})
            _rpc_call(s, f_in, "engine.execute", {"command": "view.goToPage", "params": {"page": 1}})
            _rpc_call(s, f_in, "engine.execute", {"command": "view.fitPage", "params": {}})
            _rpc_call(s, f_in, "ui.focus", {})
        bring_page_designer_window_to_front()
        return {"ok": True, "mode": "book", "file": str(combined_pd), "rpc": resp}

    eight_files = [
        "Aditya_Bharat_Page_01_34x53.pagedesigner",
        "Aditya_Bharat_Page_02_Mahanagar_34x53.pagedesigner",
        "Aditya_Bharat_Page_03_Pradeshik_34x53.pagedesigner",
        "Aditya_Bharat_Page_04_Sampadakiya_34x53.pagedesigner",
        "Aditya_Bharat_Page_05_Rashtriya_34x53.pagedesigner",
        "Aditya_Bharat_Page_06_Karobar_34x53.pagedesigner",
        "Aditya_Bharat_Page_07_Khel_Sansar_34x53.pagedesigner",
        "Aditya_Bharat_Page_08_Desh_Videsh_34x53.pagedesigner",
    ]
    opened = []
    with socket.create_connection(("127.0.0.1", port), timeout=25.0) as s:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        f_in = s.makefile("r", encoding="utf-8")
        for _ in range(12):
            try:
                r_c = _rpc_call(s, f_in, "engine.execute", {"command": "file.close", "params": {"save": False}})
                if not r_c.get("ok"):
                    break
            except Exception:
                break
        for fn in eight_files:
            p = VAULT_DIR / fn
            if p.exists():
                _rpc_call(s, f_in, "app.open", {"path": str(p)})
                _rpc_call(s, f_in, "engine.execute", {"command": "view.fitPage", "params": {}})
                opened.append(fn)
        _rpc_call(s, f_in, "engine.execute", {"command": "file.activate", "params": {"index": 0}})
        _rpc_call(s, f_in, "engine.execute", {"command": "view.fitPage", "params": {}})
        _rpc_call(s, f_in, "ui.focus", {})
    bring_page_designer_window_to_front()
    return {"ok": True, "mode": "tabs", "opened": opened}


def run_builder_script_async(page_ids: list, keep_tabs: bool = False, combined_book: bool = False):
    def _worker():
        with BUILD_LOCK:
            BUILD_STATUS["running"] = True
            logs = []
            try:
                port = ensure_page_designer_running()
                if combined_book:
                    BUILD_STATUS["current_task"] = "Page Designer में एक ही फाइल के अंदर पूरे 8 पेज (Pages 1 to 8) Draw हो रहे हैं..."
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    proc = subprocess.run(
                        [sys.executable, str(VAULT_DIR / "build_aditya_bharat_full_8pages.py"), "--combined"],
                        cwd=str(VAULT_DIR),
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                    )
                    out_txt = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
                    logs.append(out_txt.strip())
                    BUILD_STATUS["last_log"] = "\n\n".join(logs)
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    bring_page_designer_window_to_front()
                    return

                if len(page_ids) > 1 and not keep_tabs:
                    with socket.create_connection(("127.0.0.1", port), timeout=10.0) as s:
                        f_in = s.makefile("r", encoding="utf-8")
                        for _ in range(12):
                            try:
                                r_c = _rpc_call(s, f_in, "engine.execute", {"command": "file.close", "params": {"save": False}})
                                if not r_c.get("ok"):
                                    break
                            except Exception:
                                break

                for idx_p, pid in enumerate(page_ids):
                    item = next((x for x in PAGE_Catalog if x["id"] == pid), None)
                    if not item:
                        continue
                    BUILD_STATUS["current_task"] = f"Smart Runner: {item['title_hi']} (Live Edits + Ad Reflow + Cutout Wrap) Draw हो रहा है ({idx_p + 1}/{len(page_ids)})..."
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    if len(page_ids) > 1 or keep_tabs:
                        os.environ["AB_NO_CLOSE"] = "1"
                    else:
                        os.environ.pop("AB_NO_CLOSE", None)
                    res_run = ext.run_smart_page_builder(pid)
                    logs.append(f"[{item['title_hi']} — {res_run['elapsed_sec']}s | Ad={res_run['ad_preset']}] सफलतापूर्वक Page Designer में Draw और Export हो गया!")
                    BUILD_STATUS["last_log"] = "\n\n".join(logs)
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

                with socket.create_connection(("127.0.0.1", port), timeout=10.0) as s:
                    f_in = s.makefile("r", encoding="utf-8")
                    _rpc_call(s, f_in, "engine.execute", {"command": "view.fitPage", "params": {}})
                    _rpc_call(s, f_in, "ui.focus", {})
                bring_page_designer_window_to_front()
            except Exception as e:
                logs.append(f"ERROR: {e}")
                BUILD_STATUS["last_log"] = "\n\n".join(logs)
            finally:
                BUILD_STATUS["running"] = False
                BUILD_STATUS["current_task"] = ""
                BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

    t = threading.Thread(target=_worker, daemon=True)
    t.start()


HTML_PAGE = r"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>आदित्य भारत (Aditya Bharat) — 8-Page Master System & 5-in-1 Super Studio (Port 2424)</title>
<style>
  :root {
    --bg: #f4f5f7;
    --panel: #ffffff;
    --panel2: #f8fafc;
    --border: #d1d5db;
    --crimson: #c4121a;
    --crimson-light: #c4121a;
    --text: #111827;
    --muted: #4b5563;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: 'Segoe UI', 'Nirmala UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
  }
  header {
    background: #ffffff;
    border-bottom: 2px solid var(--crimson);
    padding: 10px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    position: sticky;
    top: 0;
    z-index: 100;
    flex-wrap: wrap;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }
  .brand { display: flex; align-items: center; gap: 12px; }
  .brand-badge {
    background: var(--crimson);
    color: #fff;
    font-weight: 800;
    font-size: 19px;
    padding: 7px 13px;
    border-radius: 5px;
  }
  .brand-title h1 { margin: 0; font-size: 18px; font-weight: 800; color: #111827; }
  .brand-title p { margin: 2px 0 0 0; font-size: 11.5px; color: var(--muted); }
  .header-actions { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }
  .pd-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 11.5px;
    font-weight: 700;
    background: #f8fafc;
    color: #111827;
    border: 1px solid var(--border);
  }
  .dot { width: 9px; height: 9px; border-radius: 50%; background: #16a34a; }
  .dot.off { background: #dc2626; }
  .btn {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.12s ease;
    text-decoration: none;
    background: #ffffff;
    color: #1f2937;
  }
  .btn:hover { background: #f1f5f9; border-color: #94a3b8; }
  .btn-crimson { background: var(--crimson); color: #ffffff; border-color: var(--crimson); }
  .btn-crimson:hover { background: #a30f15; color: #ffffff; border-color: #a30f15; }
  .btn-emerald, .btn-blue, .btn-purple, .btn-dark, .btn-gold {
    background: #ffffff;
    color: #1f2937;
    border: 1px solid #cbd5e1;
  }
  .btn-emerald:hover, .btn-blue:hover, .btn-purple:hover, .btn-dark:hover, .btn-gold:hover {
    background: #f1f5f9;
    border-color: #64748b;
  }

  .top-tabs {
    display: flex;
    gap: 7px;
    padding: 9px 18px;
    background: #ffffff;
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
  }
  .tab-btn {
    background: #f8fafc;
    color: #374151;
    border: 1px solid var(--border);
    padding: 8px 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
  }
  .tab-btn:hover { background: #f1f5f9; }
  .tab-btn.active {
    background: #111827;
    color: #ffffff;
    border-color: #111827;
  }

  .status-banner {
    background: #f8fafc;
    border-bottom: 1px solid var(--border);
    padding: 7px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 12.5px;
    color: #111827;
  }
  .status-banner .task { color: #111827; font-weight: 700; }

  .workspace {
    display: grid;
    grid-template-columns: 280px 1fr;
    min-height: calc(100vh - 140px);
  }
  .sidebar {
    background: var(--panel);
    border-right: 1px solid var(--border);
    padding: 11px;
    display: flex;
    flex-direction: column;
    gap: 7px;
  }
  .sidebar h3 {
    margin: 2px 0 4px 0;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--muted);
  }
  .page-item {
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 7px;
    padding: 8px 10px;
    cursor: pointer;
    transition: all 0.12s ease;
  }
  .page-item:hover { border-color: #9ca3af; background: #f9fafb; }
  .page-item.active {
    border-color: #111827;
    background: #f8fafc;
    box-shadow: inset 3.5px 0 0 var(--crimson);
  }
  .page-item-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 800;
    font-size: 13px;
    color: #111827;
  }
  .folio-tag {
    background: #111827;
    color: #fff;
    font-size: 10.5px;
    padding: 2px 6px;
    border-radius: 4px;
  }
  .page-item-sub { font-size: 10.5px; color: var(--muted); margin-top: 3px; line-height: 1.25; }
  .page-item-quick { display: flex; gap: 5px; margin-top: 6px; }
  .mini-btn {
    flex: 1;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 4px 5px;
    font-size: 10.5px;
    font-weight: 700;
    background: #ffffff !important;
    color: #1f2937 !important;
    cursor: pointer;
    text-align: center;
  }
  .mini-btn:hover { background: #f1f5f9 !important; border-color: #64748b; }

  .main-area { padding: 15px 18px; overflow-y: auto; }
  .page-header-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 13px 16px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
  }
  .page-header-info h2 { margin: 0 0 4px 0; font-size: 18px; color: #111827; }
  .page-header-info p { margin: 0; font-size: 12.5px; color: #4b5563; max-width: 760px; }
  .spec-badges { display: flex; gap: 7px; margin-top: 7px; flex-wrap: wrap; }
  .spec-badge {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    padding: 3px 9px;
    border-radius: 5px;
    font-size: 11.5px;
    color: #1f2937;
  }

  .dual-stage {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    align-items: start;
  }
  @media (max-width: 1280px) { .dual-stage { grid-template-columns: 1fr; } }
  .stage-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 13px;
  }
  .stage-card-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 9px;
    padding-bottom: 7px;
    border-bottom: 1px solid var(--border);
  }
  .stage-card-head h3 { margin: 0; font-size: 14.5px; color: #111827; }

  .dummy-sheet-outer {
    width: 100%;
    max-width: 540px;
    margin: 0 auto;
    aspect-ratio: 34 / 53;
    background: #ffffff;
    border: 1.5px solid #64748b;
    border-radius: 3px;
    position: relative;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    padding: 2.94% 2.94%;
  }
  .dummy-print-area {
    width: 100%;
    height: 100%;
    position: relative;
    border: 1px dashed #cbd5e1;
    background-image: repeating-linear-gradient(
      to right,
      rgba(226, 232, 240, 0.5) 0%,
      rgba(226, 232, 240, 0.5) 11.328%,
      transparent 11.328%,
      transparent 12.578%
    );
  }
  .col-ruler {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 4px;
    margin-bottom: 6px;
    max-width: 540px;
    margin-left: auto;
    margin-right: auto;
  }
  .col-ruler span {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    color: #334155;
    font-size: 10.5px;
    font-weight: 700;
    text-align: center;
    padding: 2px 0;
    border-radius: 4px;
  }
  .dummy-block {
    position: absolute;
    border-radius: 2px;
    padding: 4px 5px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.12s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: #ffffff;
    border: 1.2px solid #475569;
  }
  .dummy-block:hover { z-index: 20; outline: 2px solid var(--crimson); background: #fef2f2; }
  .dummy-block .db-title { font-size: 10px; font-weight: 800; line-height: 1.18; color: #111827; }
  .dummy-block .db-meta {
    font-size: 8.5px;
    font-weight: 600;
    line-height: 1.12;
    color: #475569;
    background: #f1f5f9;
    padding: 1px 4px;
    border-radius: 2px;
  }
  .kind-masthead_front, .kind-masthead_inside {
    background: #111827;
    border: 1.5px solid #111827;
  }
  .kind-masthead_front .db-title, .kind-masthead_front .db-meta,
  .kind-masthead_inside .db-title, .kind-masthead_inside .db-meta {
    color: #ffffff;
    background: transparent;
  }
  .kind-flyer, .kind-lead, .kind-anchor, .kind-story_photo, .kind-story, .kind-editorial, .kind-cutout_story, .kind-photo_feature_box, .kind-tall_story_sidebar {
    background: #ffffff;
    border: 1.2px solid #334155;
  }
  .kind-gray_box {
    background: #e2e8f0;
    border: 1.5px solid #475569;
  }
  .kind-commercial_ad {
    background: #f8fafc;
    border: 2px dashed var(--crimson);
    z-index: 15;
  }

  .rendered-preview-wrap { text-align: center; }
  .rendered-preview-wrap img {
    width: 100%;
    max-width: 540px;
    border-radius: 3px;
    border: 1.5px solid #64748b;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    cursor: zoom-in;
  }

  /* EDITOR FORMS */
  .editor-grid {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 16px;
    margin-top: 16px;
  }
  @media (max-width: 1200px) { .editor-grid { grid-template-columns: 1fr; } }
  .form-row { margin-bottom: 10px; }
  .form-row label { display: block; font-size: 12px; font-weight: 700; color: #374151; margin-bottom: 4px; }
  .form-row input, .form-row select, .form-row textarea {
    width: 100%;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    color: #111827;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 13px;
    font-family: inherit;
  }
  .form-row textarea { min-height: 92px; resize: vertical; }
  .slot-pills { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
  .slot-pill {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    color: #374151;
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
  }
  .slot-pill.active { background: #111827; color: #fff; border-color: #111827; }

  .wall-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
    gap: 16px;
  }
  .wall-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 9px;
  }
  .sys-table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 13px; }
  .sys-table th, .sys-table td { border: 1px solid var(--border); padding: 8px 11px; text-align: left; }
  .sys-table th { background: #f1f5f9; color: #111827; }
  pre.log-box {
    background: #f8fafc;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px;
    color: #111827;
    font-size: 12.5px;
    max-height: 500px;
    overflow: auto;
    white-space: pre-wrap;
  }
</style>
</head>
<body>

<header>
  <div class="brand">
    <div class="brand-badge">आदित्य भारत</div>
    <div class="brand-title">
      <h1>आदित्य भारत — 8-Page Master System & 5-in-1 Super Studio (`Port 2424`)</h1>
      <p>Live Browser Editor • IANS Hindi Wire • Commercial Ad Reflow • Cutout Contour Wrap • Visual Drag-Drop Dummy Builder</p>
    </div>
  </div>
  <div class="header-actions">
    <div class="pd-pill">
      <span class="dot" id="pdDot"></span>
      <span id="pdStatusText">Page Designer जाँच रहे हैं...</span>
    </div>
    <div style="display:inline-flex; align-items:center; gap:5px; background:#f8fafc; border:1px solid #cbd5e1; border-radius:6px; padding:3px 7px;">
      <span style="font-size:11.5px; font-weight:700; color:#111827;">🏙️ संस्करण:</span>
      <select id="abEditionSelect" style="padding:4px 6px; font-size:12px; font-weight:700; border:1px solid #cbd5e1; border-radius:4px; background:#ffffff; color:#111827;">
        <option value="RAIPUR">रायपुर (RNI: CHHHIN/2018/76773)</option>
        <option value="NEW_DELHI">नई दिल्ली (PRGI: DLHIN/25/A3662)</option>
        <option value="BILASPUR">बिलासपुर (PRGI: CTHIN/25/A1423)</option>
        <option value="BHOPAL">भोपाल (RNI: MPHIN/2015/63660)</option>
        <option value="JAIPUR">जयपुर (PRGI: RJHIN/26/A6072)</option>
        <option value="INDORE">इंदौर (RNI: MPHIN/2014/56594)</option>
        <option value="RAJNANDGAON">राजनांदगांव (PRGI: CTHIN/25/A4799)</option>
      </select>
      <span style="font-size:11.5px; font-weight:700; color:#111827;">📅 तारीख:</span>
      <input type="text" id="cgDailyDateInput" value="19-11-2026" style="width:94px; padding:4px 6px; font-size:12px; font-weight:700; border:1px solid #cbd5e1; border-radius:4px;">
      <select id="abPage1DummySelect" style="padding:4px 6px; font-size:11.5px; font-weight:700; border:1px solid #cbd5e1; border-radius:4px; background:#ffffff; color:#111827;">
        <option value="AUTO">🔄 Page 1: Auto-Rotate Dummy (1..4)</option>
        <option value="DUMMY_1" selected>📐 Page 1: Dummy 1 (6+2 Flyer + Left Lead)</option>
        <option value="DUMMY_2">📐 Page 1: Dummy 2 (2+6 Flyer + Right Lead)</option>
        <option value="DUMMY_3">📐 Page 1: Dummy 3 (6+2 Flyer + Right Lead + Right Anchor)</option>
        <option value="DUMMY_4">📐 Page 1: Dummy 4 (2+6 Flyer + Left Lead + Right Anchor)</option>
      </select>
      <button class="btn btn-crimson" style="padding:5px 10px;" onclick="buildFrontPage1()">📰 Page 01 फ्रंट पेज (11 खबरें • CM/State + Non-Repeat)</button>
      <button class="btn btn-crimson" style="padding:5px 10px;" onclick="buildChhattisgarhPages2And3(false)">🌾 Page 02–03 (10+10 खबरें) + PDF</button>
      <button class="btn btn-purple" style="padding:5px 10px;" onclick="buildSampadakiyaPage4(false)">✒️ Page 04 संपादकीय (Daily Articles + Logo)</button>
      <button class="btn btn-blue" style="padding:5px 10px;" onclick="buildPradeshikPage5()">🗺️ Page 05 प्रादेशिक (MP+CG+RJ+DL • 12 खबरें)</button>
      <button class="btn btn-emerald" style="padding:5px 10px;" onclick="buildKarobarPage6(false)">📈 Page 06 कारोबार (Full Business + Logo)</button>
      <button class="btn btn-gold" style="padding:5px 10px;" onclick="buildKhelFilmPage7()">🏏🎬 Page 07 खेल + फिल्म (11 खबरें + 5 Cutouts)</button>
      <button class="btn btn-dark" style="padding:5px 10px;" onclick="buildDeshVideshPage8(false)">🌍 Page 08 देश-विदेश (70% राष्ट्रीय + 30% वि. + Print Line)</button>
      <button class="btn btn-purple" style="padding:5px 11px; font-weight:800;" onclick="buildFull8PageDailyEdition(false)">🚀 संपूर्ण 8 पेज (1–8) + Single Vector PDF बनाएं</button>
      <button class="btn btn-crimson" style="padding:5px 11px; font-weight:800;" onclick="buildAll7Editions4States()">🌐 MAKE ALL 7 EDITIONS (4-State Front Page Alter + 7 Print Lines + 7 Single 1–8 Vector PDFs)</button>
      <button class="btn btn-gold" style="padding:5px 11px; font-weight:800;" onclick="sendAll7EditionsToMailAndWhatsapp()">📧📲 Send All 7 Editions (WhatsApp + Email)</button>
      <a class="btn btn-dark" style="padding:5px 10px;" href="https://github.com/deepakbudana555-cmyk/ADITYA-BHARAT-7-EDITION" target="_blank">☁️ GitHub Cloud (`ADITYA-BHARAT-7-EDITION`) ↗</a>
      <a class="btn btn-emerald" style="padding:5px 10px;" href="/vault/Aditya_Bharat_Full_8Pages_CMYK_34x53.pdf" target="_blank">📄 1–8 Single Vector PDF (10,000% Zoom)</a>
      <button class="btn btn-dark" style="padding:5px 10px;" onclick="buildChhattisgarhPages2And3(true)">📡 नई ताज़ा खबरें खींचें (Live RSS)</button>
    </div>
    <button class="btn btn-dark" onclick="openSavedFile('Aditya_Bharat_8Pages_Dummy_34x53.pagedesigner', false)">📐 8-Page Dummy खोलें</button>
    <button class="btn btn-emerald" onclick="openAllPages('book')">📚 सभी 8 पेज (1 Book में) खोलें</button>
    <button class="btn btn-blue" onclick="openAllPages('tabs')">🗂️ सभी 8 पेज (8 Tabs में) खोलें</button>
    <button class="btn btn-purple" onclick="drawAllCombinedBook()">🚀 पूरे 8 पेज (1 Book में) Draw करें</button>
  </div>
</header>

<div class="top-tabs">
  <button class="tab-btn active" id="tabBtn_studio" onclick="switchTab('studio')">1. 📐 पेज Dummy + 📝 Live Editor + ✂️ Cutout + 📢 Ad Reflow</button>
  <button class="tab-btn" id="tabBtn_ians" onclick="switchTab('ians')">2. 📡 Live IANS एजेंसी व 4-सिटी न्यूज़ पूल (Auto-Fill)</button>
  <button class="tab-btn" id="tabBtn_custom" onclick="switchTab('custom')">3. 🧩 Visual Drag-Drop नया लेआउट बिल्डर (No-Code Builder)</button>
  <button class="tab-btn" id="tabBtn_wall" onclick="switchTab('wall')">4. 🗺️ एक साथ सभी 8 पेजों की Dummy & Preview Wall</button>
  <button class="tab-btn" id="tabBtn_system" onclick="switchTab('system')">5. 📏 मास्टर स्टाइलशीट व नियम</button>
  <button class="tab-btn" id="tabBtn_logs" onclick="switchTab('logs')">6. 🖥️ Live Page Designer RPC Logs</button>
</div>

<div class="status-banner" style="flex-wrap:wrap; gap:10px;">
  <div>
    <strong>Live इंजन स्टेटस:</strong>
    <span class="task" id="bannerTask">तैयार (Ready)</span>
  </div>
  <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; background:#fff7ed; border:1px solid #fdba74; padding:4px 10px; border-radius:6px;">
    <strong style="color:#9a3412;">⏰ Daily 10:30 PM ऑटो-एडिशन अलार्म:</strong>
    <span id="alarm1030Badge" style="background:#16a34a; color:#fff; font-weight:800; font-size:11.5px; padding:2px 8px; border-radius:4px;">ON • 10:30 PM (22:30)</span>
    <span id="alarm1030Countdown" style="font-weight:700; color:#111827; font-size:12px;">बाकी समय: --:--:--</span>
    <input id="alarmTimeInput" type="time" value="22:30" style="background:#fff; color:#111827; border:1px solid #cbd5e1; padding:2px 6px; border-radius:4px; font-weight:700; font-size:12px;" onchange="update1030AlarmConfig()">
    <button class="btn btn-dark" style="padding:3px 8px; font-size:11.5px;" onclick="toggle1030AlarmEnabled()">🔔 ON/OFF</button>
    <button class="btn btn-crimson" style="padding:3px 9px; font-size:11.5px; font-weight:800;" onclick="trigger1030NightDeskNow()">⚡ अभी 10:30 PM नाइट-डेस्क (Fresh News + 7 Editions) चलाएं</button>
  </div>
  <div style="color:var(--muted);" id="bannerTime"></div>
</div>

<!-- ======================================================================= -->
<!-- TAB 1: DUMMY + LIVE STORY/PHOTO EDITOR + CUTOUT WRAP + COMMERCIAL AD REFLOW -->
<!-- ======================================================================= -->
<div id="tab_studio">
  <div class="workspace">
    <div class="sidebar">
      <h3>8-पेज इंडेक्स (1-1 खोलें या Draw करें)</h3>
      <div id="sidebarList"></div>
    </div>
    <div class="main-area">
      <div class="page-header-card">
        <div class="page-header-info">
          <h2 id="curPageTitle">पेज 01 — फ्रंट पेज</h2>
          <p id="curPageSummary"></p>
          <div class="spec-badges" id="curPageBadges"></div>
        </div>
        <div style="display:flex; gap:7px; flex-wrap:wrap;">
          <button class="btn btn-emerald" onclick="openCurrentSavedFile(true)">📂 सिर्फ यही 1 पेज खोलें</button>
          <button class="btn btn-blue" onclick="openCurrentSavedFile(false)">➕ नए टैब में जोड़ें</button>
          <button class="btn btn-crimson" onclick="drawCurrentPage(false)">🎨 यह पेज अभी Page Designer में Draw करें</button>
          <button class="btn btn-gold" onclick="autoFillCurrentPageFromIans()">📡 ताज़ा IANS खबरों से यह पेज भरें व Draw करें</button>
          <a class="btn btn-dark" id="linkDownloadPdf" href="#" target="_blank">📄 CMYK PDF</a>
        </div>
      </div>

      <div class="dual-stage">
        <!-- LEFT: INTERACTIVE 8-COLUMN DUMMY -->
        <div class="stage-card">
          <div class="stage-card-head">
            <h3>📐 8-Column Structural Dummy (किसी भी ब्लॉक पर क्लिक करके नीचे तुरंत एडिट करें)</h3>
            <span style="font-size:11.5px; color:#4b5563;">Click Block ➔ Edit Story Below</span>
          </div>
          <div class="col-ruler">
            <span>Col 1</span><span>Col 2</span><span>Col 3</span><span>Col 4</span>
            <span>Col 5</span><span>Col 6</span><span>Col 7</span><span>Col 8</span>
          </div>
          <div class="dummy-sheet-outer">
            <div class="dummy-print-area" id="dummyCanvas"></div>
          </div>
          <div id="dummyInspector" style="margin-top:10px; padding:9px 11px; background:#f8fafc; border:1px solid #cbd5e1; border-radius:6px; font-size:12.5px; color:#111827;">
            👆 ऊपर डमी के किसी भी स्टोरी ब्लॉक पर क्लिक करें — नीचे उसका Live Story Editor खुल जाएगा!
          </div>
        </div>

        <!-- RIGHT: LIVE RENDERED BROADSHEET -->
        <div class="stage-card">
          <div class="stage-card-head">
            <h3>📰 Page Designer द्वारा तैयार वास्तविक पेज (Live Rendered Page)</h3>
            <a id="linkFullPng" href="#" target="_blank" style="color:#111827; font-size:12px; text-decoration:underline; font-weight:700;">🔍 300 DPI फुल साइज खोलें ↗</a>
          </div>
          <div class="rendered-preview-wrap">
            <img id="curPageImg" src="" alt="Rendered Page Preview" onclick="window.open(this.src, '_blank')">
          </div>
        </div>
      </div>

      <!-- BOTTOM OF TAB 1: LIVE STORY EDITOR + PHOTO/CUTOUT WRAP + COMMERCIAL AD REFLOW -->
      <div class="editor-grid">
        <!-- PANEL A: LIVE STORY & IANS SWAP EDITOR -->
        <div class="stage-card">
          <div class="stage-card-head">
            <h3>📝 1. Live Browser Story Editor (हेडलाइन, सबहेड, बाइलाइन, ब्लर्ब व खबर बदलें)</h3>
            <button class="btn btn-dark" style="padding:4px 9px; font-size:11px;" onclick="resetPageOverrides()">♻️ डिफ़ॉल्ट रीसेट करें</button>
          </div>
          <div class="slot-pills" id="storySlotPills"></div>

          <div class="form-row">
            <label>📡 IANS हिंदी एजेंसी पूल से सीधे इस स्लॉट में खबर डालें (1-Click Agency Swap):</label>
            <div style="display:flex; gap:8px;">
              <select id="iansQuickSelect"></select>
              <button class="btn btn-gold" onclick="applySelectedIansToSlot()">🔄 यह खबर भरें</button>
            </div>
          </div>
          <div class="form-row">
            <label>मुख्य हेडलाइन (DB Rasrand Bold • Minimum 30 pt • 100% Black):</label>
            <input type="text" id="edHeadline" placeholder="हेडलाइन यहाँ लिखें...">
          </div>
          <div class="form-row">
            <label>सबहेड / किकर (DB Hindi Bold • 100% Black):</label>
            <input type="text" id="edSubhead" placeholder="सबहेड / डेक यहाँ लिखें...">
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px;">
            <div class="form-row">
              <label>शहर (City — Black):</label>
              <input type="text" id="edCity" placeholder="इंदौर / नई दिल्ली">
            </div>
            <div class="form-row">
              <label>एजेंसी / ब्यूरो (Gray):</label>
              <input type="text" id="edAgency" placeholder="एजेंसी / ब्यूरो">
            </div>
            <div class="form-row">
              <label>1-शब्द रेड सब्जेक्ट ब्लर्ब:</label>
              <input type="text" id="edBlurb" placeholder="जैसे: सौगात / सामरिक">
            </div>
          </div>
          <div class="form-row">
            <label>मुख्य समाचार बॉडी टेक्स्ट (DB Hindi 11pt/11.25pt — अपने-आप Binary-Search से 100% फिट होगा):</label>
            <textarea id="edBody" placeholder="पूरी खबर यहाँ लिखें..."></textarea>
          </div>
          <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <button class="btn btn-crimson" onclick="saveSlotAndRedraw(true)">💾 सेव करें और अभी Page Designer में Live Redraw करें</button>
            <button class="btn btn-emerald" onclick="saveSlotAndRedraw(false)">💾 केवल सेव करें</button>
          </div>
        </div>

        <!-- PANEL B: PHOTO + CUTOUT CONTOUR WRAP + COMMERCIAL AD REFLOW -->
        <div style="display:flex; flex-direction:column; gap:16px;">
          <!-- PHOTO & CUTOUT CONTOUR WRAP CARD -->
          <div class="stage-card">
            <div class="stage-card-head">
              <h3>✂️ 2. Photo & Cutout Silhouette Contour Text-Wrap (फोटो व कटआउट रैप)</h3>
            </div>
            <div class="slot-pills" id="photoSlotPills"></div>
            <div class="form-row">
              <label>टेक्स्ट रैप मोड (Text-Wrap Mode in Page Designer):</label>
              <select id="edPhotoWrap">
                <option value="boundingBox">🔲 Rectangular Bounding Box Wrap (सामान्य आयताकार फोटो बॉक्स)</option>
                <option value="contour">✂️ Cutout Silhouette Contour Text-Wrap (चेहरे/शरीर के कटआउट के चारों तरफ टेक्स्ट मोड़ें)</option>
              </select>
            </div>
            <div class="form-row">
              <label>फोटो कैप्शन (DB Hindi 7 • 10.0 pt / 10.2 pt):</label>
              <input type="text" id="edPhotoCaption" placeholder="फोटो कैप्शन...">
            </div>
            <div class="form-row">
              <label>नया फोटो या Transparent PNG अपलोड करें (300 DPI CMYK / RGBA Cutout):</label>
              <input type="file" id="edPhotoFile" accept="image/*">
            </div>
            <button class="btn btn-purple" onclick="savePhotoSlotAndRedraw()">✂️ फोटो / Cutout Contour Wrap सेव करें व Page Designer में Draw करें</button>
          </div>

          <!-- DYNAMIC COMMERCIAL AD REFLOW CARD -->
          <div class="stage-card">
            <div class="stage-card-head">
              <h3>📢 3. Dynamic Commercial Display Ad & Grid Reflow (विज्ञापन रि-फ्लो इंजन)</h3>
            </div>
            <div class="form-row">
              <label>इस पेज पर विज्ञापन का आकार चुनें (बाकी खबरें अपने-आप सिकुड़कर रि-फ्लो हो जाएंगी):</label>
              <select id="edAdPreset">
                <option value="none">कोई विज्ञापन नहीं (100% संपादकीय खबरें)</option>
                <option value="quarter_br">क्वार्टर पेज विज्ञापन (Quarter Page: दाएं नीचे 4 Col × 15 cm)</option>
                <option value="bottom_strip">बॉटम स्ट्रिप विज्ञापन (Full Bottom Strip: 8 Col × 10.5 cm)</option>
                <option value="half_page">हाफ पेज विज्ञापन (Half Page Lower: 8 Col × 22.0 cm)</option>
                <option value="skybus_right">वर्टिकल स्काईबस विज्ञापन (Right Skybus: दाएं 2 Col × 22.0 cm)</option>
              </select>
            </div>
            <div class="form-row">
              <label>विज्ञापनदाता / ब्रांड शीर्षक (Advertiser Header):</label>
              <input type="text" id="edAdAdvertiser" value="आदित्य भारत विशेष उत्सव ऑफर">
            </div>
            <div class="form-row">
              <label>विज्ञापन मुख्य संदेश (Ad Main Headline):</label>
              <input type="text" id="edAdHeadline" value="त्योहारी सीजन में स्वदेशी उत्पादों पर विशेष छूट और आकर्षक उपहार योजना">
            </div>
            <div class="form-row">
              <label>विज्ञापन इमेज अपलोड करें (वैकल्पिक — Ready Ad Artwork JPG/PNG):</label>
              <input type="file" id="edAdFile" accept="image/*">
            </div>
            <button class="btn btn-crimson" onclick="saveAdAndRedraw()">📢 विज्ञापन लगाएं + खबरें रि-फ्लो करके Page Designer में Draw करें</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ======================================================================= -->
<!-- TAB 2: LIVE IANS HINDI AGENCY + 4-CITY LOCAL POOL                       -->
<!-- ======================================================================= -->
<div id="tab_ians" style="display:none; padding:20px;">
  <div class="stage-card" style="margin-bottom:16px;">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
      <div>
        <h2 style="margin:0;">📡 Live IANS हिंदी एजेंसी + 4-सिटी लोकल न्यूज़ पूल (`local_hindi_daily_vault`)</h2>
        <p style="margin:4px 0 0 0; color:var(--muted); font-size:13px;">यहाँ से किसी भी ताज़ा एजेंसी खबर को किसी भी पेज के किसी भी स्लॉट में 1-क्लिक में डालें या पूरा पेज ऑटो-फिल करें।</p>
      </div>
      <div style="display:flex; gap:8px; flex-wrap:wrap;">
        <select id="iansCatFilter" onchange="renderIansPool()" style="background:#ffffff; color:#111827; border:1px solid #cbd5e1; padding:8px 12px; border-radius:6px;">
          <option value="ALL">सभी कैटेगरी (ALL)</option>
          <option value="CHHATTISGARH">🌾 छत्तीसगढ़ विशेष 18-11-2026 (20 खबरें)</option>
          <option value="FRONT">फ्रंट पेज (FRONT)</option>
          <option value="NATIONAL">राष्ट्रीय (NATIONAL)</option>
          <option value="STATE">प्रादेशिक (STATE)</option>
          <option value="BUSINESS">कारोबार (BUSINESS)</option>
          <option value="SPORTS">खेल (SPORTS)</option>
          <option value="INTERNATIONAL">देश-विदेश (INTERNATIONAL)</option>
        </select>
        <button class="btn btn-gold" onclick="autoFillCurrentPageFromIans()">⚡ वर्तमान पेज को IANS खबरों से ऑटो-फिल व Draw करें</button>
      </div>
    </div>
  </div>
  <div class="wall-grid" id="iansGrid"></div>
</div>

<!-- ======================================================================= -->
<!-- TAB 3: VISUAL DRAG & DROP CUSTOM DUMMY LAYOUT BUILDER (NO-CODE)         -->
<!-- ======================================================================= -->
<div id="tab_custom" style="display:none; padding:20px;">
  <div class="page-header-card">
    <div>
      <h2 style="margin:0;">🧩 Visual Drag-and-Drop Custom Layout Dummy Builder (बिना कोडिंग नया पेज डिज़ाइन बनाएं)</h2>
      <p style="margin:4px 0 0 0; color:#4b5563; font-size:13px;">बाईं तरफ 8-कॉलम ग्रिड में अपने ब्लॉक जोड़ें, उनका कॉलम (`Col 1..8`), चौड़ाई (`Span 1..8`), Y-स्थिति (`cm`) व ऊंचाई (`cm`) सेट करें या माउस से ड्रैग करें, और सीधे <b>Page Designer</b> में Draw करें!</p>
    </div>
    <div style="display:flex; gap:8px; flex-wrap:wrap;">
      <button class="btn btn-emerald" onclick="addCustomBlock('flyer')">➕ 8-Col फ्लायर जोड़ें</button>
      <button class="btn btn-blue" onclick="addCustomBlock('lead')">➕ मेन लीड पैकेज जोड़ें</button>
      <button class="btn btn-purple" onclick="addCustomBlock('cutout_story')">➕ ✂️ Cutout Contour स्टोरी जोड़ें</button>
      <button class="btn btn-dark" onclick="addCustomBlock('story')">➕ सामान्य खबर जोड़ें</button>
      <button class="btn btn-gold" onclick="addCustomBlock('anchor')">➕ बॉटम एंकर जोड़ें</button>
      <button class="btn btn-dark" onclick="addCustomBlock('commercial_ad')">➕ 📢 विज्ञापन ब्लॉक जोड़ें</button>
      <button class="btn btn-crimson" onclick="buildCustomLayoutInPd()">🎨 यह कस्टम लेआउट अभी Page Designer में Draw करें</button>
    </div>
  </div>

  <div class="dual-stage" style="grid-template-columns: 1fr 1fr 1fr;">
    <!-- COL 1: ORIGINAL REFERENCE NEWSPAPER PAGE -->
    <div class="stage-card">
      <div class="stage-card-head">
        <h3>📸 1. सामने रखा ओरिजिनल रेफरेंस पेज (Original Reference Layout)</h3>
        <span style="font-size:11.5px; color:#4b5563;">Reference Scan</span>
      </div>
      <div class="rendered-preview-wrap">
        <img id="custRefImg" src="/vault/Original_Reference_Layout_02.png" alt="Original Reference Layout" onclick="window.open(this.src, '_blank')">
      </div>
    </div>

    <!-- COL 2: INTERACTIVE DRAGGABLE 8-COLUMN CUSTOM DUMMY -->
    <div class="stage-card">
      <div class="stage-card-head">
        <h3>📐 2. कस्टम 8-कॉलम डमी कैनवास (Drag & Drop Blocks)</h3>
        <button class="btn btn-dark" style="padding:4px 9px; font-size:11px;" onclick="loadStarterCustomLayout()">🔄 ओरिजिनल रेफरेंस डमी लोड करें</button>
      </div>
      <div class="col-ruler">
        <span>Col 1</span><span>Col 2</span><span>Col 3</span><span>Col 4</span>
        <span>Col 5</span><span>Col 6</span><span>Col 7</span><span>Col 8</span>
      </div>
      <div class="dummy-sheet-outer">
        <div class="dummy-print-area" id="customDummyCanvas"></div>
      </div>
    </div>

    <!-- COL 3: RENDERED CUSTOM PAGE PREVIEW IN PAGE DESIGNER -->
    <div class="stage-card">
      <div class="stage-card-head">
        <h3>📰 3. Page Designer में बना नया पेज (`Aditya_Bharat_Custom_Page_34x53.png`)</h3>
        <a id="custPdfLink" href="/vault/Aditya_Bharat_Custom_Page_CMYK_34x53.pdf" target="_blank" style="color:#111827; font-size:12px; font-weight:700;">📄 CMYK PDF ↗</a>
      </div>
      <div class="rendered-preview-wrap">
        <img id="custRenderedImg" src="/vault/Aditya_Bharat_Custom_Page_34x53.png" alt="Custom Page Preview" onclick="window.open(this.src, '_blank')">
      </div>
    </div>
  </div>

  <!-- BOTTOM BLOCK INSPECTOR FORM -->
  <div class="stage-card" style="margin-top:16px;">
    <div class="stage-card-head">
      <h3>⚙️ चुने गए कस्टम ब्लॉक की सेटिंग्स (Geometry & Content)</h3>
      <button class="btn btn-crimson" style="padding:4px 9px; font-size:11px;" onclick="deleteSelectedCustomBlock()">🗑️ यह ब्लॉक हटाएं</button>
    </div>
    <div style="display:grid; grid-template-columns: 1fr 1fr 1fr 1fr 1fr 1fr 1fr; gap:8px;">
      <div class="form-row">
        <label>पेज का नाम:</label>
        <input type="text" id="custPageTitle" value="खबरों का शहर">
      </div>
      <div class="form-row">
        <label>पेज नंबर:</label>
        <input type="text" id="custFolio" value="02">
      </div>
      <div class="form-row">
        <label>प्रकार (Type):</label>
        <select id="cbKind" onchange="updateSelectedCustomBlock()">
          <option value="flyer">Top Flyer (8-Col)</option>
          <option value="photo_feature_box">Photo Feature Box</option>
          <option value="tall_story_sidebar">Tall Story + Sidebar</option>
          <option value="lead">Main Lead</option>
          <option value="story_photo">Photo Story</option>
          <option value="cutout_story">✂️ Cutout Story</option>
          <option value="story">News Story</option>
          <option value="gray_box">40% Gray Box</option>
          <option value="anchor">Bottom Anchor</option>
          <option value="commercial_ad">📢 Commercial Ad</option>
        </select>
      </div>
      <div class="form-row">
        <label>Start Col (1-8):</label>
        <input type="number" id="cbCol" min="1" max="8" value="1" onchange="updateSelectedCustomBlock()">
      </div>
      <div class="form-row">
        <label>Span Cols (1-8):</label>
        <input type="number" id="cbSpan" min="1" max="8" value="4" onchange="updateSelectedCustomBlock()">
      </div>
      <div class="form-row">
        <label>Y-Top (cm):</label>
        <input type="number" id="cbY0" step="0.5" min="2.8" max="49" value="2.85" onchange="updateSelectedCustomBlock()">
      </div>
      <div class="form-row">
        <label>Height (cm):</label>
        <input type="number" id="cbH" step="0.5" min="4.0" max="48" value="12.0" onchange="updateSelectedCustomBlock()">
      </div>
    </div>
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
      <div class="form-row">
        <label>हेडलाइन (DB Rasrand Bold):</label>
        <input type="text" id="cbHead" oninput="updateSelectedCustomBlock()">
      </div>
      <div class="form-row">
        <label>सबहेड / किकर:</label>
        <input type="text" id="cbSub" oninput="updateSelectedCustomBlock()">
      </div>
    </div>
    <div class="form-row">
      <label>बॉडी टेक्स्ट (DB Hindi 11pt/11.25pt):</label>
      <textarea id="cbBody" oninput="updateSelectedCustomBlock()"></textarea>
    </div>
    <button class="btn btn-crimson" onclick="buildCustomLayoutInPd()">🎨 यह कस्टम लेआउट अभी Page Designer में Draw करें</button>
  </div>
</div>

<!-- TAB 4: ALL 8 PAGES WALL -->
<div id="tab_wall" style="display:none; padding:20px;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:10px;">
    <div>
      <h2 style="margin:0;">🗺️ आदित्य भारत — सभी 8 पेजों की Structural Dummy + Live Preview Wall</h2>
    </div>
    <div style="display:flex; gap:8px;">
      <button class="btn btn-dark" onclick="toggleWallMode('dummy')">📐 सभी की Structural Dummy दिखाएं</button>
      <button class="btn btn-blue" onclick="toggleWallMode('png')">📰 सभी के Rendered Pages दिखाएं</button>
    </div>
  </div>
  <div class="wall-grid" id="wallGrid"></div>
</div>

<!-- TAB 5: SYSTEM RULES -->
<div id="tab_system" style="display:none; padding:22px; max-width:1320px; margin:0 auto;">
  <div class="stage-card">
    <h2 style="margin-top:0;">📏 आदित्य भारत (Aditya Bharat) — सिखाया गया पूरा 8-पेज मास्टर सिस्टम + 5 नए सुपर-मॉड्यूल</h2>
    <table class="sys-table">
      <tr><th>मॉड्यूल</th><th>स्थिति (Status)</th><th>विवरण</th></tr>
      <tr><td><b>1. Live Browser Story & Photo Editor</b></td><td>✅ 100% सक्रिय</td><td>किसी भी पेज के किसी भी स्लॉट की हेडलाइन, सबहेड, शहर | एजेंसी, रेड ब्लर्ब, बॉडी और फोटो सीधे ब्राउज़र से बदलकर तुरंत Page Designer में Draw करें।</td></tr>
      <tr><td><b>2. Live IANS Hindi Wire Connector</b></td><td>✅ 100% सक्रिय</td><td><code>local_hindi_daily_vault</code> की सभी ताज़ा IANS और 4-सिटी लोकल खबरें सीधे किसी भी स्लॉट या पूरे पेज में 1-क्लिक में ऑटो-फिल होती हैं।</td></tr>
      <tr><td><b>3. Dynamic Commercial Ad Reflow</b></td><td>✅ 100% सक्रिय</td><td>Quarter-Page, Half-Page, Bottom Strip या Skybus विज्ञापन चुनते ही उस हिस्से की खबरें अपने-आप सिकुड़कर रि-फ्लो हो जाती हैं और विज्ञापन Draw हो जाता है।</td></tr>
      <tr><td><b>4. Cutout Contour Text-Wrap</b></td><td>✅ 100% सक्रिय</td><td>Page Designer के <code>WrapMode::Contour</code> और Silhouette PNG इंजन से फोटो के कटआउट आकार के चारों तरफ हिंदी टेक्स्ट मुड़ता है।</td></tr>
      <tr><td><b>5. Visual Drag-Drop Dummy Builder</b></td><td>✅ 100% सक्रिय</td><td>बिना कोडिंग के ब्राउज़र में 8-कॉलम ग्रिड पर नया लेआउट बनाकर सीधे Page Designer में Draw करें।</td></tr>
    </table>
  </div>
</div>

<!-- TAB 6: LOGS -->
<div id="tab_logs" style="display:none; padding:22px; max-width:1200px; margin:0 auto;">
  <div class="stage-card">
    <div class="stage-card-head">
      <h3>🖥️ Live Page Designer (Port 47123) Build & Execution Logs</h3>
      <button class="btn btn-dark" onclick="pollStatus()">🔄 रिफ्रेश लॉग</button>
    </div>
    <pre class="log-box" id="logBox">लॉग लोड हो रहा है...</pre>
  </div>
</div>

<script>
let CATALOG = [];
let CURRENT_INDEX = 0;
let WALL_MODE = 'dummy';
let PAGE_SLOTS_DATA = {stories: [], photos: [], ad_config: {preset: 'none'}};
let CUR_STORY_SLOT = 0;
let CUR_PHOTO_SLOT = 0;
let IANS_POOL = [];

// Custom Visual Dummy State
let CUSTOM_BLOCKS = [];
let SELECTED_CB_IDX = 0;

async function initApp() {
  const res = await fetch('/api/catalog');
  const data = await res.json();
  CATALOG = data.pages;
  const rIans = await fetch('/api/ians_pool');
  const dIans = await rIans.json();
  IANS_POOL = dIans.items || [];
  populateIansDropdown();
  renderIansPool();
  loadStarterCustomLayout();
  renderSidebar();
  await selectPage(0);
  renderWall();
  pollStatus();
  setInterval(pollStatus, 1800);
}

function switchTab(tabName) {
  ['studio', 'ians', 'custom', 'wall', 'system', 'logs'].forEach(t => {
    document.getElementById('tab_' + t).style.display = (t === tabName) ? 'block' : 'none';
    document.getElementById('tabBtn_' + t).classList.toggle('active', t === tabName);
  });
}

function renderSidebar() {
  const box = document.getElementById('sidebarList');
  box.innerHTML = CATALOG.map((p, idx) => `
    <div class="page-item ${idx === CURRENT_INDEX ? 'active' : ''}" onclick="selectPage(${idx})">
      <div class="page-item-top">
        <span>${p.title_hi}</span>
        <span class="folio-tag">P-${p.folio}</span>
      </div>
      <div class="page-item-sub">${p.layout_tag}</div>
      <div class="page-item-quick" onclick="event.stopPropagation();">
        <button class="mini-btn" style="background:#059669;" onclick="selectPage(${idx}); openSavedFile('${p.pd_file}', true)">📂 1-Page खोलें</button>
        <button class="mini-btn" style="background:#2563eb;" onclick="selectPage(${idx}); openSavedFile('${p.pd_file}', false)">➕ टैब जोड़ें</button>
        <button class="mini-btn" style="background:#c4121a;" onclick="selectPage(${idx}); drawSinglePage('${p.id}', false)">🎨 Draw</button>
      </div>
    </div>
  `).join('');
}

function buildDummyHtml(p, adPreset) {
  const colW = 3.625;
  const gutW = 0.40;
  let html = p.dummy_blocks.map((b) => {
    const xCm = (b.col - 1) * (colW + gutW);
    const wCm = b.span * colW + (b.span - 1) * gutW;
    const yCm = b.y0 - 1.0;
    const leftPct = (xCm / 32.0) * 100.0;
    const widthPct = (wCm / 32.0) * 100.0;
    const topPct = (yCm / 51.0) * 100.0;
    const heightPct = (b.h / 51.0) * 100.0;
    const safeTitle = b.title.replace(/"/g, '&quot;');
    const safeMeta = b.meta.replace(/"/g, '&quot;');
    const slotIdx = (b.slot_idx !== undefined) ? b.slot_idx : -1;
    return `
      <div class="dummy-block kind-${b.kind}"
           style="left:${leftPct.toFixed(2)}%; width:${widthPct.toFixed(2)}%; top:${topPct.toFixed(2)}%; height:${heightPct.toFixed(2)}%;"
           onclick="inspectDummyBlock('${safeTitle}', '${safeMeta}', ${b.col}, ${b.span}, ${b.y0}, ${b.h}, ${slotIdx})">
        <div class="db-title">${b.title}</div>
        <div class="db-meta">${b.meta}</div>
      </div>
    `;
  }).join('');

  const adMap = {
    quarter_br: {col: 5, span: 4, y0: 37.0, h: 15.0, title: "📢 COMMERCIAL AD (Quarter Page 4 Col × 15 cm)"},
    bottom_strip: {col: 1, span: 8, y0: 41.5, h: 10.5, title: "📢 COMMERCIAL AD (Bottom Strip 8 Col × 10.5 cm)"},
    half_page: {col: 1, span: 8, y0: 30.0, h: 22.0, title: "📢 COMMERCIAL AD (Half Page 8 Col × 22 cm)"},
    skybus_right: {col: 7, span: 2, y0: 30.0, h: 22.0, title: "📢 SKYBUS AD (2 Col × 22 cm)"}
  };
  if (adPreset && adMap[adPreset]) {
    const a = adMap[adPreset];
    const xCm = (a.col - 1) * (colW + gutW);
    const wCm = a.span * colW + (a.span - 1) * gutW;
    const yCm = a.y0 - 1.0;
    html += `
      <div class="dummy-block kind-commercial_ad"
           style="left:${((xCm/32)*100).toFixed(2)}%; width:${((wCm/32)*100).toFixed(2)}%; top:${((yCm/51)*100).toFixed(2)}%; height:${((a.h/51)*100).toFixed(2)}%;">
        <div class="db-title">${a.title}</div>
        <div class="db-meta">Dynamic Ad-Grid Reflow Active</div>
      </div>
    `;
  }
  return html;
}

function inspectDummyBlock(title, meta, col, span, y0, h, slotIdx) {
  const endCol = col + span - 1;
  document.getElementById('dummyInspector').innerHTML = `
    <div style="font-weight:800; color:#111827; margin-bottom:4px;">📌 ${title}</div>
    <div><b>कॉलम विस्तार:</b> Col ${col} से Col ${endCol} (${span} Columns) • <b>Y-स्थिति:</b> ${y0.toFixed(2)} cm से ${(y0 + h).toFixed(2)} cm (ऊंचाई: <b>${h.toFixed(2)} cm</b>)</div>
    <div style="color:#4b5563; margin-top:3px;"><b>नियम व विवरण:</b> ${meta}</div>
  `;
  if (slotIdx >= 0 && slotIdx < PAGE_SLOTS_DATA.stories.length) {
    selectStorySlot(slotIdx);
  }
}

async function selectPage(idx) {
  CURRENT_INDEX = idx;
  renderSidebar();
  const p = CATALOG[idx];
  document.getElementById('curPageTitle').textContent = p.title_hi;
  document.getElementById('curPageSummary').textContent = p.summary_hi;
  document.getElementById('curPageBadges').innerHTML = `
    <span class="spec-badge">📰 सेक्शन: <b>${p.section_hi}</b></span>
    <span class="spec-badge">🔢 कुल खबरें: <b>${p.stories_count}</b></span>
    <span class="spec-badge">🔠 हेडलाइन: <b>${p.min_head_pt} – ${p.max_head_pt} (DB Rasrand Bold)</b></span>
    <span class="spec-badge">🚫 खड़ी रूल: <b>0 (Zero Vertical Rules)</b></span>
  `;
  const ts = Date.now();
  const pngUrl = '/vault/' + encodeURIComponent(p.png_file) + '?t=' + ts;
  document.getElementById('curPageImg').src = pngUrl;
  document.getElementById('linkFullPng').href = pngUrl;
  document.getElementById('linkDownloadPdf').href = '/vault/' + encodeURIComponent(p.pdf_file) + '?t=' + ts;

  const rSlots = await fetch('/api/slots?page_id=' + encodeURIComponent(p.id));
  PAGE_SLOTS_DATA = await rSlots.json();
  const adPreset = (PAGE_SLOTS_DATA.ad_config && PAGE_SLOTS_DATA.ad_config.preset) || 'none';
  document.getElementById('edAdPreset').value = adPreset;
  if (PAGE_SLOTS_DATA.ad_config) {
    document.getElementById('edAdAdvertiser').value = PAGE_SLOTS_DATA.ad_config.advertiser || 'आदित्य भारत विशेष उत्सव ऑफर';
    document.getElementById('edAdHeadline').value = PAGE_SLOTS_DATA.ad_config.headline || '';
  }
  document.getElementById('dummyCanvas').innerHTML = buildDummyHtml(p, adPreset);
  renderStorySlotPills();
  renderPhotoSlotPills();
}

function renderStorySlotPills() {
  const box = document.getElementById('storySlotPills');
  const stories = PAGE_SLOTS_DATA.stories || [];
  if (!stories.length) {
    box.innerHTML = '<span style="color:var(--muted);">कोई स्टोरी स्लॉट नहीं मिला</span>';
    return;
  }
  if (CUR_STORY_SLOT >= stories.length) CUR_STORY_SLOT = 0;
  box.innerHTML = stories.map((s, i) => `
    <button class="slot-pill ${i === CUR_STORY_SLOT ? 'active' : ''}" onclick="selectStorySlot(${i})">
      खबर #${i + 1}: ${(s.headline || '').slice(0, 22)}...
    </button>
  `).join('');
  selectStorySlot(CUR_STORY_SLOT);
}

function selectStorySlot(idx) {
  CUR_STORY_SLOT = idx;
  const stories = PAGE_SLOTS_DATA.stories || [];
  document.querySelectorAll('#storySlotPills .slot-pill').forEach((el, i) => {
    el.classList.toggle('active', i === idx);
  });
  const s = stories[idx] || {};
  document.getElementById('edHeadline').value = s.headline || '';
  document.getElementById('edSubhead').value = s.subhead || '';
  document.getElementById('edCity').value = s.city || '';
  document.getElementById('edAgency').value = s.agency || '';
  document.getElementById('edBlurb').value = s.blurb || '';
  document.getElementById('edBody').value = s.body || '';
}

function renderPhotoSlotPills() {
  const box = document.getElementById('photoSlotPills');
  const photos = PAGE_SLOTS_DATA.photos || [];
  if (!photos.length) {
    box.innerHTML = '<span style="color:var(--muted);">इस पेज पर कोई फोटो स्लॉट नहीं है</span>';
    return;
  }
  if (CUR_PHOTO_SLOT >= photos.length) CUR_PHOTO_SLOT = 0;
  box.innerHTML = photos.map((ph, i) => `
    <button class="slot-pill ${i === CUR_PHOTO_SLOT ? 'active' : ''}" onclick="selectPhotoSlot(${i})">
      🖼️ फोटो #${i + 1} (${ph.wrap_mode === 'contour' ? '✂️ Cutout' : '🔲 Box'})
    </button>
  `).join('');
  selectPhotoSlot(CUR_PHOTO_SLOT);
}

function selectPhotoSlot(idx) {
  CUR_PHOTO_SLOT = idx;
  const photos = PAGE_SLOTS_DATA.photos || [];
  document.querySelectorAll('#photoSlotPills .slot-pill').forEach((el, i) => {
    el.classList.toggle('active', i === idx);
  });
  const ph = photos[idx] || {};
  document.getElementById('edPhotoWrap').value = ph.wrap_mode || 'boundingBox';
  document.getElementById('edPhotoCaption').value = ph.caption || '';
}

function populateIansDropdown() {
  const sel = document.getElementById('iansQuickSelect');
  sel.innerHTML = IANS_POOL.map((it, i) => `
    <option value="${i}">[${it.category} | ${it.city}] ${it.headline.slice(0, 68)}</option>
  `).join('');
}

function applySelectedIansToSlot() {
  const idx = parseInt(document.getElementById('iansQuickSelect').value || '0', 10);
  const it = IANS_POOL[idx];
  if (!it) return;
  document.getElementById('edHeadline').value = it.headline;
  document.getElementById('edSubhead').value = it.subhead || '';
  document.getElementById('edCity').value = it.city || 'नई दिल्ली';
  document.getElementById('edAgency').value = it.agency || 'आईएएनएस';
  document.getElementById('edBody').value = it.body || '';
}

async function saveSlotAndRedraw(redrawNow) {
  const p = CATALOG[CURRENT_INDEX];
  const payload = {
    page_id: p.id,
    slot_index: CUR_STORY_SLOT,
    story: {
      headline: document.getElementById('edHeadline').value,
      subhead: document.getElementById('edSubhead').value,
      city: document.getElementById('edCity').value,
      agency: document.getElementById('edAgency').value,
      blurb: document.getElementById('edBlurb').value,
      body: document.getElementById('edBody').value
    },
    redraw: !!redrawNow
  };
  await fetch('/api/save_slot', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });
  await selectPage(CURRENT_INDEX);
  pollStatus();
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(r.result.split(',')[1]);
    r.onerror = reject;
    r.readAsDataURL(file);
  });
}

async function savePhotoSlotAndRedraw() {
  const p = CATALOG[CURRENT_INDEX];
  const fileInput = document.getElementById('edPhotoFile');
  let b64 = '';
  let fname = '';
  if (fileInput.files && fileInput.files[0]) {
    fname = fileInput.files[0].name;
    b64 = await fileToBase64(fileInput.files[0]);
  }
  await fetch('/api/save_photo_slot', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      page_id: p.id,
      photo_index: CUR_PHOTO_SLOT,
      wrap_mode: document.getElementById('edPhotoWrap').value,
      caption: document.getElementById('edPhotoCaption').value,
      file_name: fname,
      file_b64: b64,
      redraw: true
    })
  });
  fileInput.value = '';
  await selectPage(CURRENT_INDEX);
  pollStatus();
}

async function saveAdAndRedraw() {
  const p = CATALOG[CURRENT_INDEX];
  const fileInput = document.getElementById('edAdFile');
  let b64 = '';
  let fname = '';
  if (fileInput.files && fileInput.files[0]) {
    fname = fileInput.files[0].name;
    b64 = await fileToBase64(fileInput.files[0]);
  }
  await fetch('/api/save_ad', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      page_id: p.id,
      preset: document.getElementById('edAdPreset').value,
      advertiser: document.getElementById('edAdAdvertiser').value,
      headline: document.getElementById('edAdHeadline').value,
      file_name: fname,
      file_b64: b64,
      redraw: true
    })
  });
  fileInput.value = '';
  await selectPage(CURRENT_INDEX);
  pollStatus();
}

async function resetPageOverrides() {
  const p = CATALOG[CURRENT_INDEX];
  await fetch('/api/reset_page', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({page_id: p.id, redraw: true})
  });
  await selectPage(CURRENT_INDEX);
  pollStatus();
}

async function autoFillCurrentPageFromIans() {
  const p = CATALOG[CURRENT_INDEX];
  await fetch('/api/ians_autofill', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({page_id: p.id, redraw: true})
  });
  await selectPage(CURRENT_INDEX);
  pollStatus();
}

function renderIansPool() {
  const cat = document.getElementById('iansCatFilter').value;
  const filtered = IANS_POOL.filter(x => cat === 'ALL' || x.category === cat);
  const grid = document.getElementById('iansGrid');
  grid.innerHTML = filtered.map((it, idx) => `
    <div class="wall-card">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span class="folio-tag">${it.category} • ${it.date}</span>
        <span style="font-size:11.5px; color:#4b5563;">${it.city} | ${it.agency}</span>
      </div>
      <strong style="font-size:15px; line-height:1.35; color:#111827;">${it.headline}</strong>
      <div style="font-size:12px; color:#4b5563; max-height:85px; overflow:hidden;">${it.body.slice(0, 220)}...</div>
      <div style="display:flex; gap:8px; margin-top:auto;">
        <button class="btn btn-crimson" style="flex:1; justify-content:center;" onclick="sendIansStoryToCurrentSlot('${it.wire_id}')">📲 वर्तमान स्लॉट (#${CUR_STORY_SLOT + 1}) में डालें व Draw करें</button>
      </div>
    </div>
  `).join('');
}

async function sendIansStoryToCurrentSlot(wireId) {
  const it = IANS_POOL.find(x => x.wire_id === wireId);
  if (!it) return;
  switchTab('studio');
  document.getElementById('edHeadline').value = it.headline;
  document.getElementById('edSubhead').value = it.subhead || '';
  document.getElementById('edCity').value = it.city || 'नई दिल्ली';
  document.getElementById('edAgency').value = it.agency || 'आईएएनएस';
  document.getElementById('edBody').value = it.body || '';
  await saveSlotAndRedraw(true);
}

// ============================================================================
// PART 5: VISUAL DRAG & DROP CUSTOM DUMMY LAYOUT BUILDER
// ============================================================================
function loadStarterCustomLayout() {
  CUSTOM_BLOCKS = [
    {col: 1, span: 8, y0: 2.85, h: 12.6, kind: 'flyer', headline: 'इंदौर के चौराहों पर स्मार्ट ट्रैफिक ग्रिड शुरू', subhead: 'रिंग रोड और बीआरटीएस पर एआई कैमरों से ट्रैफिक दबाव के अनुसार स्वतः बदलेगा सिग्नल समय', city: 'इंदौर', agency: 'सिटी रिपोर्टर', blurb: 'सुगम', photo: 'ab_p2_flyer_cmyk.jpg', photo_col: 4, photo_span: 3, underflow_lines: 4, body: ''},
    {col: 1, span: 5, y0: 15.85, h: 13.0, kind: 'photo_feature_box', top_rule: true, headline: 'इंदौर में ऑनलाइन ठगे गए डेढ़ लाख रुपये पुलिस ने वापस दिलाए', subhead: 'इंदौर क्राइम ब्रांच और साइबर सेल द्वारा त्वरित कार्रवाई कर पीड़ित व्यापारी को पूरी राशि वापस दिलाई गई। — फाइल फोटो', photo: 'ab_p2_lead_cmyk.jpg', body: ''},
    {col: 6, span: 3, y0: 15.85, h: 22.95, kind: 'tall_story_sidebar', top_rule: true, subhead: 'स्वच्छता अभियान और मेट्रो फीडर मार्गों को मिलेगी गति', headline: 'नए नगर आयुक्त ने संभाला पद', city: 'भोपाल', agency: 'विशेष संवाददाता', blurb: 'संवाद', body: ''},
    {col: 1, span: 2, y0: 29.25, h: 9.55, kind: 'story', top_rule: true, subhead: 'इंदौर अंचल में 3800 करोड़ का नया निवेश', headline: 'पीथमपुर में लगेंगी बारह नई फार्मा यूनिट्स', city: 'इंदौर', agency: 'औद्योगिक ब्यूरो', blurb: '', body: ''},
    {col: 3, span: 3, y0: 29.25, h: 9.55, kind: 'story_photo', top_rule: true, subhead: 'दमकल व पुलिस टीम ने रस्सी के सहारे किया रेस्क्यू', headline: 'बिलासपुर के अटल आवास में आग, 75 लोगों को बचाया', city: 'बिलासपुर', agency: 'प्रदेश ब्यूरो', blurb: '', photo: 'ab_p3_highway_cmyk.jpg', photo_col: 4, photo_span: 1, underflow_lines: 3, body: ''},
    {col: 1, span: 6, y0: 39.20, h: 12.80, kind: 'anchor', top_rule: true, headline: 'अहमदाबाद में प्राकृतिक खेती का विशेष प्रशिक्षण', subhead: 'गुजरात विद्यापीठ परिसर में आयोजित कार्यशाला में युवाओं और किसानों को जैविक कृषि तकनीक का प्रशिक्षण', city: 'अहमदाबाद', agency: 'विशेष संवाददाता', blurb: 'प्रशिक्षण', photo: 'ab_p2_anchor_cmyk.jpg', photo_col: 2, photo_span: 3, underflow_lines: 4, body: ''},
    {col: 7, span: 2, y0: 39.20, h: 12.80, kind: 'story', top_rule: true, headline: 'एमवाय अस्पताल में नई कैथ लैब शुरू', subhead: '', city: 'इंदौर', agency: 'स्वास्थ्य रिपोर्टर', blurb: '', body: ''}
  ];
  SELECTED_CB_IDX = 0;
  renderCustomDummyCanvas();
  loadCustomBlockIntoForm(0);
}

function renderCustomDummyCanvas() {
  const colW = 3.625;
  const gutW = 0.40;
  const mhHtml = `
    <div class="dummy-block kind-masthead_inside" style="left:0%; width:100%; top:0%; height:${(1.5/51)*100}%;">
      <div class="db-title">1.5 cm रनिंग मास्टहेड : [${document.getElementById('custPageTitle')?.value || 'विशेष पृष्ठ'}] | आदित्य भारत | पेज ${document.getElementById('custFolio')?.value || '09'}</div>
    </div>
  `;
  const blocksHtml = CUSTOM_BLOCKS.map((b, idx) => {
    const xCm = (b.col - 1) * (colW + gutW);
    const wCm = b.span * colW + (b.span - 1) * gutW;
    const yCm = b.y0 - 1.0;
    const leftPct = (xCm / 32.0) * 100.0;
    const widthPct = (wCm / 32.0) * 100.0;
    const topPct = (yCm / 51.0) * 100.0;
    const heightPct = (b.h / 51.0) * 100.0;
    const selBorder = (idx === SELECTED_CB_IDX) ? 'outline: 3px solid #f59e0b; z-index: 25;' : '';
    return `
      <div class="dummy-block kind-${b.kind}"
           draggable="true"
           ondragstart="onCustomDragStart(event, ${idx})"
           style="left:${leftPct.toFixed(2)}%; width:${widthPct.toFixed(2)}%; top:${topPct.toFixed(2)}%; height:${heightPct.toFixed(2)}%; ${selBorder}"
           onclick="loadCustomBlockIntoForm(${idx})">
        <div class="db-title">[#${idx + 1} ${b.kind.toUpperCase()}] ${b.headline}</div>
        <div class="db-meta">Cols ${b.col}..${b.col + b.span - 1} (${b.span} Col) | Y=${b.y0}cm | H=${b.h}cm</div>
      </div>
    `;
  }).join('');
  const canvas = document.getElementById('customDummyCanvas');
  canvas.innerHTML = mhHtml + blocksHtml;
  canvas.ondragover = (e) => e.preventDefault();
  canvas.ondrop = onCustomDrop;
}

let DRAG_CB_IDX = -1;
function onCustomDragStart(e, idx) {
  DRAG_CB_IDX = idx;
}
function onCustomDrop(e) {
  e.preventDefault();
  if (DRAG_CB_IDX < 0 || !CUSTOM_BLOCKS[DRAG_CB_IDX]) return;
  const rect = document.getElementById('customDummyCanvas').getBoundingClientRect();
  const relX = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
  const relY = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
  const b = CUSTOM_BLOCKS[DRAG_CB_IDX];
  const newCol = Math.max(1, Math.min(9 - b.span, Math.round(relX * 8) + 1));
  const newY0 = Math.max(2.85, Math.min(52.0 - b.h, Math.round((1.0 + relY * 51.0) * 2) / 2));
  b.col = newCol;
  b.y0 = newY0;
  SELECTED_CB_IDX = DRAG_CB_IDX;
  renderCustomDummyCanvas();
  loadCustomBlockIntoForm(SELECTED_CB_IDX);
}

function loadCustomBlockIntoForm(idx) {
  SELECTED_CB_IDX = idx;
  const b = CUSTOM_BLOCKS[idx];
  if (!b) return;
  document.getElementById('cbKind').value = b.kind;
  document.getElementById('cbCol').value = b.col;
  document.getElementById('cbSpan').value = b.span;
  document.getElementById('cbY0').value = b.y0;
  document.getElementById('cbH').value = b.h;
  document.getElementById('cbHead').value = b.headline || '';
  document.getElementById('cbSub').value = b.subhead || '';
  document.getElementById('cbBody').value = b.body || '';
  renderCustomDummyCanvas();
}

function updateSelectedCustomBlock() {
  const b = CUSTOM_BLOCKS[SELECTED_CB_IDX];
  if (!b) return;
  b.kind = document.getElementById('cbKind').value;
  b.col = Math.max(1, Math.min(8, parseInt(document.getElementById('cbCol').value || '1', 10)));
  b.span = Math.max(1, Math.min(9 - b.col, parseInt(document.getElementById('cbSpan').value || '3', 10)));
  b.y0 = Math.max(2.8, parseFloat(document.getElementById('cbY0').value || '2.85'));
  b.h = Math.max(4.0, parseFloat(document.getElementById('cbH').value || '10.0'));
  b.headline = document.getElementById('cbHead').value;
  b.subhead = document.getElementById('cbSub').value;
  b.body = document.getElementById('cbBody').value;
  renderCustomDummyCanvas();
}

function addCustomBlock(kind) {
  CUSTOM_BLOCKS.push({
    col: 1,
    span: kind === 'flyer' ? 8 : (kind === 'lead' || kind === 'anchor' ? 5 : 3),
    y0: 25.0,
    h: 10.0,
    kind: kind,
    headline: 'नया कस्टम समाचार शीर्षक (DB Rasrand Bold >= 30pt)',
    subhead: 'विशेष सबहेड पट्टी',
    city: 'इंदौर',
    agency: 'ब्यूरो',
    blurb: 'विशेष',
    body: ''
  });
  loadCustomBlockIntoForm(CUSTOM_BLOCKS.length - 1);
}

function deleteSelectedCustomBlock() {
  if (CUSTOM_BLOCKS.length <= 1) return;
  CUSTOM_BLOCKS.splice(SELECTED_CB_IDX, 1);
  SELECTED_CB_IDX = Math.max(0, SELECTED_CB_IDX - 1);
  loadCustomBlockIntoForm(SELECTED_CB_IDX);
}

async function buildCustomLayoutInPd() {
  const payload = {
    page_title: document.getElementById('custPageTitle').value || 'विशेष पृष्ठ',
    folio: document.getElementById('custFolio').value || '09',
    blocks: CUSTOM_BLOCKS
  };
  const res = await fetch('/api/build_custom_dummy', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (data.ok) {
    const ts = Date.now();
    document.getElementById('custRenderedImg').src = '/vault/' + data.png_file + '?t=' + ts;
    document.getElementById('custPdfLink').href = '/vault/' + data.pdf_file + '?t=' + ts;
  } else {
    alert('Error: ' + (data.error || 'Failed'));
  }
  pollStatus();
}

function renderWall() {
  const grid = document.getElementById('wallGrid');
  const ts = Date.now();
  grid.innerHTML = CATALOG.map((p, idx) => {
    const bodyContent = (WALL_MODE === 'dummy')
      ? `<div class="dummy-sheet-outer" style="max-width:100%;"><div class="dummy-print-area">${buildDummyHtml(p, 'none')}</div></div>`
      : `<div class="rendered-preview-wrap"><img src="/vault/${encodeURIComponent(p.png_file)}?t=${ts}" onclick="selectPage(${idx}); switchTab('studio');"></div>`;
    return `
      <div class="wall-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <strong style="font-size:15px;">${p.title_hi}</strong>
          <span class="folio-tag">P-${p.folio}</span>
        </div>
        <div style="font-size:12px; color:var(--muted);">${p.layout_tag}</div>
        ${bodyContent}
        <div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:4px;">
          <button class="btn btn-emerald" style="flex:1; justify-content:center;" onclick="openSavedFile('${p.pd_file}', true)">📂 1-Page खोलें</button>
          <button class="btn btn-blue" onclick="openSavedFile('${p.pd_file}', false)">➕ टैब जोड़ें</button>
          <button class="btn btn-crimson" onclick="drawSinglePage('${p.id}', false)">🎨 Draw</button>
        </div>
      </div>
    `;
  }).join('');
}

function toggleWallMode(mode) { WALL_MODE = mode; renderWall(); }
async function drawCurrentPage(keepTabs) { await drawSinglePage(CATALOG[CURRENT_INDEX].id, keepTabs); }

let ALARM_1030_ENABLED = true;

async function refresh1030AlarmBanner() {
  try {
    const res = await fetch('/api/alarm_1030_status');
    const data = await res.json();
    if (!data.ok || !data.alarm) return;
    const cfg = data.alarm.config || {};
    ALARM_1030_ENABLED = !!cfg.enabled;
    const badge = document.getElementById('alarm1030Badge');
    const cd = document.getElementById('alarm1030Countdown');
    const inp = document.getElementById('alarmTimeInput');
    if (inp && document.activeElement !== inp && cfg.alarm_time_24h) {
      inp.value = cfg.alarm_time_24h;
    }
    if (badge) {
      badge.textContent = (ALARM_1030_ENABLED ? 'ON • ' : 'OFF • ') + (cfg.display_time || '10:30 PM') + ' (' + (cfg.alarm_time_24h || '22:30') + ')';
      badge.style.background = ALARM_1030_ENABLED ? '#16a34a' : '#64748b';
    }
    if (cd) {
      cd.textContent = 'अगला अलार्म बाकी: ' + (data.alarm.countdown_hms || '--:--:--') + (cfg.last_built_edition_date ? (' | पिछला: ' + cfg.last_built_edition_date) : '');
    }
  } catch (e) {}
}

async function toggle1030AlarmEnabled() {
  ALARM_1030_ENABLED = !ALARM_1030_ENABLED;
  await fetch('/api/alarm_1030_config', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({enabled: ALARM_1030_ENABLED})
  });
  await refresh1030AlarmBanner();
}

async function update1030AlarmConfig() {
  const inp = document.getElementById('alarmTimeInput');
  const t24 = (inp && inp.value) ? inp.value : '22:30';
  await fetch('/api/alarm_1030_config', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({alarm_time_24h: t24, enabled: true})
  });
  await refresh1030AlarmBanner();
}

async function trigger1030NightDeskNow() {
  const dtEl = document.getElementById('cgDailyDateInput');
  const dmEl = document.getElementById('abPage1DummySelect');
  const dateStr = (dtEl && dtEl.value.trim()) ? dtEl.value.trim() : '';
  const dummyStr = (dmEl && dmEl.value) ? dmEl.value : 'AUTO';
  const res = await fetch('/api/trigger_1030pm_now', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({target_edition_date: dateStr, p1_dummy_id: dummyStr})
  });
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Error triggering 10:30 PM Night-Desk job');
  pollStatus();
}

setInterval(refresh1030AlarmBanner, 3000);
setTimeout(refresh1030AlarmBanner, 500);

async function sendAll7EditionsToMailAndWhatsapp() {
  const dtEl = document.getElementById('cgDailyDateInput');
  const dateStr = (dtEl && dtEl.value.trim()) ? dtEl.value.trim() : '19-11-2026';
  const res = await fetch('/api/deliver_all_7_editions', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({date_str: dateStr})
  });
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Error starting Email/WhatsApp delivery');
  pollStatus();
}

async function buildAll7Editions4States() {
  const dtEl = document.getElementById('cgDailyDateInput');
  const dmEl = document.getElementById('abPage1DummySelect');
  const dateStr = (dtEl && dtEl.value.trim()) ? dtEl.value.trim() : '19-11-2026';
  const dummyStr = (dmEl && dmEl.value) ? dmEl.value : 'DUMMY_1';
  const res = await fetch('/api/make_all_7_editions_4_states', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({date_str: dateStr, p1_dummy_id: dummyStr})
  });
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Error starting Make All 7 Editions build');
  selectPage(0);
  pollStatus();
}

async function buildFrontPage1() {
  const dtEl = document.getElementById('cgDailyDateInput');
  const edEl = document.getElementById('abEditionSelect');
  const dmEl = document.getElementById('abPage1DummySelect');
  const dateStr = (dtEl && dtEl.value.trim()) ? dtEl.value.trim() : '19-11-2026';
  const editionStr = (edEl && edEl.value) ? edEl.value : 'RAIPUR';
  const dummyStr = (dmEl && dmEl.value) ? dmEl.value : 'AUTO';
  const res = await fetch('/api/daily_p1_front', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({date_str: dateStr, edition: editionStr, dummy_id: dummyStr})
  });
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Error starting Page 01 Front Page build');
  selectPage(0);
  pollStatus();
}

async function buildChhattisgarhPages2And3(forceFreshLive) {
  const dtEl = document.getElementById('cgDailyDateInput');
  const dateStr = (dtEl && dtEl.value.trim()) ? dtEl.value.trim() : '18-11-2026';
  const res = await fetch('/api/daily_cg_10x2', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({date_str: dateStr, force_fresh_live: !!forceFreshLive, export_desktop_pdf: true})
  });
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Error starting Chhattisgarh Page 02 & 03 build');
  selectPage(2);
  pollStatus();
}

async function buildSampadakiyaPage4(forceNextSeries) {
  const dtEl = document.getElementById('cgDailyDateInput');
  const edEl = document.getElementById('abEditionSelect');
  const dateStr = (dtEl && dtEl.value.trim()) ? dtEl.value.trim() : '19-11-2026';
  const editionStr = (edEl && edEl.value) ? edEl.value : 'RAIPUR';
  const res = await fetch('/api/daily_p4_edit', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({date_str: dateStr, edition: editionStr, force_next_series: !!forceNextSeries})
  });
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Error starting Page 04 Sampadakiya build');
  selectPage(4);
  pollStatus();
}

async function buildPradeshikPage5() {
  const dtEl = document.getElementById('cgDailyDateInput');
  const edEl = document.getElementById('abEditionSelect');
  const dateStr = (dtEl && dtEl.value.trim()) ? dtEl.value.trim() : '19-11-2026';
  const editionStr = (edEl && edEl.value) ? edEl.value : 'RAIPUR';
  const res = await fetch('/api/daily_p5_pradeshik', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({date_str: dateStr, edition: editionStr})
  });
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Error starting Page 05 Pradeshik build');
  selectPage(5);
  pollStatus();
}

async function buildKarobarPage6(forceNextSeries) {
  const dtEl = document.getElementById('cgDailyDateInput');
  const edEl = document.getElementById('abEditionSelect');
  const dateStr = (dtEl && dtEl.value.trim()) ? dtEl.value.trim() : '19-11-2026';
  const editionStr = (edEl && edEl.value) ? edEl.value : 'RAIPUR';
  const res = await fetch('/api/daily_p6_business', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({date_str: dateStr, edition: editionStr, force_next_series: !!forceNextSeries})
  });
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Error starting Page 06 Karobar build');
  selectPage(6);
  pollStatus();
}

async function buildKhelFilmPage7() {
  const dtEl = document.getElementById('cgDailyDateInput');
  const edEl = document.getElementById('abEditionSelect');
  const dateStr = (dtEl && dtEl.value.trim()) ? dtEl.value.trim() : '19-11-2026';
  const editionStr = (edEl && edEl.value) ? edEl.value : 'RAIPUR';
  const res = await fetch('/api/daily_p7_sports_film', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({date_str: dateStr, edition: editionStr})
  });
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Error starting Page 07 Sports + Film build');
  selectPage(7);
  pollStatus();
}

async function buildDeshVideshPage8(forceFreshLive) {
  const dtEl = document.getElementById('cgDailyDateInput');
  const edEl = document.getElementById('abEditionSelect');
  const dateStr = (dtEl && dtEl.value.trim()) ? dtEl.value.trim() : '18-11-2026';
  const editionStr = (edEl && edEl.value) ? edEl.value : 'RAIPUR';
  const res = await fetch('/api/daily_p8_70_30', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({date_str: dateStr, edition: editionStr, force_fresh_live: !!forceFreshLive, export_desktop_pdf: true})
  });
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Error starting Page 08 Desh-Videsh build');
  selectPage(8);
  pollStatus();
}

async function drawSinglePage(pageId, keepTabs) {
  const res = await fetch('/api/draw', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({pages: [pageId], keep_tabs: !!keepTabs, combined_book: false})
  });
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Error starting build');
  pollStatus();
}

async function buildAllPagesTabs() {
  const allIds = ['page_01', 'page_02', 'page_03', 'page_04', 'page_05', 'page_06', 'page_07', 'page_08'];
  await fetch('/api/draw', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({pages: allIds, keep_tabs: false, combined_book: false})
  });
  pollStatus();
}

async function buildFull8PageDailyEdition(assembleOnly) {
  const dtEl = document.getElementById('cgDailyDateInput');
  const edEl = document.getElementById('abEditionSelect');
  const dmEl = document.getElementById('abPage1DummySelect');
  const dateStr = (dtEl && dtEl.value.trim()) ? dtEl.value.trim() : '19-11-2026';
  const editionStr = (edEl && edEl.value) ? edEl.value : 'RAIPUR';
  const dummyStr = (dmEl && dmEl.value) ? dmEl.value : 'AUTO';
  const res = await fetch('/api/daily_full_8pages_vector_pdf', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      date_str: dateStr,
      edition: editionStr,
      p1_dummy_id: dummyStr,
      assemble_only: !!assembleOnly
    })
  });
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Error starting Full 8-Page Vector PDF build');
  pollStatus();
}

async function drawAllCombinedBook() {
  await buildFull8PageDailyEdition(false);
}

async function openCurrentSavedFile(closeOthers) {
  await openSavedFile(CATALOG[CURRENT_INDEX].pd_file, closeOthers);
}

async function openSavedFile(pdFile, closeOthers) {
  await fetch('/api/open_pd', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({pd_file: pdFile, close_others: !!closeOthers})
  });
  pollStatus();
}

async function openAllPages(mode) {
  await fetch('/api/open_all_pd', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({mode: mode})
  });
  pollStatus();
}

let wasRunning = false;
async function pollStatus() {
  try {
    const res = await fetch('/api/status');
    const st = await res.json();
    const dot = document.getElementById('pdDot');
    const txt = document.getElementById('pdStatusText');
    if (st.pd.alive) {
      dot.className = 'dot';
      txt.textContent = `Page Designer Connected (Port ${st.pd.port})`;
    } else {
      dot.className = 'dot off';
      txt.textContent = `Page Designer Standby (Auto-Launch Ready)`;
    }
    const bannerTask = document.getElementById('bannerTask');
    if (st.build.running) {
      bannerTask.textContent = '⏳ ' + st.build.current_task;
      bannerTask.style.color = '#c4121a';
    } else {
      bannerTask.textContent = '✅ तैयार — Live Editor, IANS Wire, Cutout Wrap, Ad Reflow और Custom Builder सक्रिय हैं';
      bannerTask.style.color = '#111827';
      if (wasRunning) {
        selectPage(CURRENT_INDEX);
        renderWall();
      }
    }
    wasRunning = st.build.running;
    document.getElementById('bannerTime').textContent = 'अंतिम अपडेट: ' + st.build.last_updated;
    document.getElementById('logBox').textContent = st.build.last_log || '';
  } catch (e) {}
}

window.addEventListener('DOMContentLoaded', initApp);
</script>
</body>
</html>
"""


class AdityaBharatStudioHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _send_json(self, data: dict, status: int = 200):
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            raw = HTML_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return

        if path == "/api/catalog":
            self._send_json({"ok": True, "pages": PAGE_Catalog})
            return

        if path == "/api/slots":
            page_id = (qs.get("page_id") or ["page_01"])[0]
            self._send_json(ext.extract_default_slots_from_script(page_id))
            return

        if path == "/api/ians_pool":
            self._send_json({"ok": True, "items": ext.scan_ians_agency_pool(100)})
            return

        if path == "/api/status":
            self._send_json({
                "ok": True,
                "pd": check_page_designer_alive(),
                "build": BUILD_STATUS,
            })
            return

        if path == "/api/alarm_1030_status":
            import ab_daily_8page_full_edition_orchestrator as full_orch
            self._send_json({
                "ok": True,
                "alarm": full_orch.get_next_1030pm_alarm_status(),
            })
            return

        if path.startswith("/vault/"):
            rel_name = urllib.parse.unquote(path[len("/vault/"):])
            safe_path = (VAULT_DIR / rel_name).resolve()
            if not str(safe_path).startswith(str(VAULT_DIR.resolve())) or not safe_path.is_file():
                self.send_error(404, "File not found")
                return
            ext_s = safe_path.suffix.lower()
            ctype = "application/octet-stream"
            if ext_s == ".png":
                ctype = "image/png"
            elif ext_s == ".pdf":
                ctype = "application/pdf"
            elif ext_s == ".json":
                ctype = "application/json; charset=utf-8"
            data = safe_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(data)
            return

        self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}

        if path == "/api/save_slot":
            page_id = payload.get("page_id", "page_01")
            slot_idx = str(payload.get("slot_index", 0))
            story_data = payload.get("story") or {}
            ov = ext.load_overrides()
            ov.setdefault("pages", {}).setdefault(page_id, {}).setdefault("stories", {})[slot_idx] = story_data
            ext.save_overrides(ov)
            if payload.get("redraw"):
                run_builder_script_async([page_id])
            self._send_json({"ok": True})
            return

        if path == "/api/save_photo_slot":
            page_id = payload.get("page_id", "page_01")
            p_idx = str(payload.get("photo_index", 0))
            wrap_mode = payload.get("wrap_mode", "boundingBox")
            caption = payload.get("caption", "")
            fname = payload.get("file_name", "")
            fb64 = payload.get("file_b64", "")
            ov = ext.load_overrides()
            p_entry = ov.setdefault("pages", {}).setdefault(page_id, {}).setdefault("photos", {}).setdefault(p_idx, {})
            p_entry["wrap_mode"] = wrap_mode
            if caption:
                p_entry["caption"] = caption
            if fname and fb64:
                safe_fn = f"user_upload_{page_id}_p{p_idx}_{Path(fname).name}"
                (ext.PHOTOS_DIR / safe_fn).write_bytes(base64.b64decode(fb64))
                p_entry["src_photo"] = safe_fn
            ext.save_overrides(ov)
            if payload.get("redraw"):
                run_builder_script_async([page_id])
            self._send_json({"ok": True})
            return

        if path == "/api/save_ad":
            page_id = payload.get("page_id", "page_01")
            ov = ext.load_overrides()
            ad_entry = ov.setdefault("ads", {}).setdefault(page_id, {})
            ad_entry["preset"] = payload.get("preset", "none")
            ad_entry["advertiser"] = payload.get("advertiser", "")
            ad_entry["headline"] = payload.get("headline", "")
            fname = payload.get("file_name", "")
            fb64 = payload.get("file_b64", "")
            if fname and fb64:
                safe_fn = f"ad_{page_id}_{Path(fname).name}"
                (ext.CUSTOM_ADS_DIR / safe_fn).write_bytes(base64.b64decode(fb64))
                ad_entry["image_file"] = safe_fn
            ext.save_overrides(ov)
            if payload.get("redraw"):
                run_builder_script_async([page_id])
            self._send_json({"ok": True})
            return

        if path == "/api/reset_page":
            page_id = payload.get("page_id", "page_01")
            ov = ext.load_overrides()
            ov.get("pages", {}).pop(page_id, None)
            ov.get("ads", {}).pop(page_id, None)
            ext.save_overrides(ov)
            if payload.get("redraw"):
                run_builder_script_async([page_id])
            self._send_json({"ok": True})
            return

        if path == "/api/ians_autofill":
            page_id = payload.get("page_id", "page_01")
            pool = ext.scan_ians_agency_pool(100)
            cat_map = {
                "page_01": "FRONT",
                "page_01_opt2": "FRONT",
                "page_02": "STATE",
                "page_03": "STATE",
                "page_04": "NATIONAL",
                "page_05": "NATIONAL",
                "page_06": "BUSINESS",
                "page_07": "SPORTS",
                "page_08": "INTERNATIONAL",
            }
            target_cat = cat_map.get(page_id, "FRONT")
            cat_items = [x for x in pool if x["category"] == target_cat] + [x for x in pool if x["category"] != target_cat]
            slots_info = ext.extract_default_slots_from_script(page_id)
            ov = ext.load_overrides()
            page_st_ov = ov.setdefault("pages", {}).setdefault(page_id, {}).setdefault("stories", {})
            for idx_s, _s in enumerate(slots_info.get("stories", [])):
                if idx_s < len(cat_items):
                    it = cat_items[idx_s]
                    page_st_ov[str(idx_s)] = {
                        "headline": it["headline"],
                        "subhead": it["subhead"],
                        "city": it["city"],
                        "agency": it["agency"],
                        "body": it["body"],
                    }
            ext.save_overrides(ov)
            if payload.get("redraw"):
                run_builder_script_async([page_id])
            self._send_json({"ok": True, "filled": len(page_st_ov)})
            return

        if path == "/api/build_custom_dummy":
            try:
                ensure_page_designer_running()
                res = ext.build_custom_dummy_page_in_pd(payload)
                bring_page_designer_window_to_front()
                BUILD_STATUS["last_log"] = f"[CUSTOM VISUAL DUMMY BUILT IN {res.get('elapsed_sec')}s] -> {res.get('pd_file')}"
                BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                self._send_json(res)
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, status=500)
            return

        if path == "/api/open_pd":
            pd_file = payload.get("pd_file", "")
            close_others = bool(payload.get("close_others", True))
            try:
                res = open_saved_file_in_page_designer(pd_file, close_others=close_others)
                BUILD_STATUS["last_log"] = f"[OPENED] {pd_file} -> Page Designer में खुल गया है!"
                BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                self._send_json(res)
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, status=500)
            return

        if path == "/api/open_all_pd":
            mode = payload.get("mode", "book")
            try:
                res = open_all_8_pages_in_page_designer(mode=mode)
                BUILD_STATUS["last_log"] = f"[OPENED ALL 8 PAGES ({mode.upper()})] सभी 8 पेज Page Designer में खुल गए हैं!"
                BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                self._send_json(res)
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, status=500)
            return

        if path == "/api/daily_full_8pages_vector_pdf":
            if BUILD_STATUS["running"]:
                self._send_json({"ok": False, "error": "अभी Page Designer में पेज Draw हो रहा है, कृपया कुछ सेकंड प्रतीक्षा करें।"})
                return
            date_str = (payload.get("date_str") or "19-11-2026").strip()
            edition_str = (payload.get("edition") or "RAIPUR").strip().upper()
            dummy_str = (payload.get("p1_dummy_id") or "AUTO").strip().upper()
            assemble_only = bool(payload.get("assemble_only", False))

            def _full8_worker():
                with BUILD_LOCK:
                    BUILD_STATUS["running"] = True
                    BUILD_STATUS["current_task"] = f"संपूर्ण 8-पेज अख़बार ({edition_str} | {date_str} | {dummy_str}) + 1–8 Single Pure Vector PDF तैयार हो रहा है..."
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    try:
                        import ab_daily_8page_full_edition_orchestrator as full_orch

                        def _prog(m):
                            BUILD_STATUS["current_task"] = m
                            BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

                        res_f8 = full_orch.build_daily_full_8page_newspaper_and_single_vector_pdf(
                            date_str=date_str,
                            edition_code=edition_str,
                            p1_dummy_id=dummy_str,
                            build_individual_pages_first=not assemble_only,
                            progress_cb=_prog,
                        )
                        BUILD_STATUS["last_log"] = (
                            f"[FULL 8-PAGE EDITION + SINGLE 1-8 PURE VECTOR PDF BUILT ({edition_str} | {date_str})]\n"
                            f"PDF Pages: {res_f8.get('pdf_pages_count')} | Embedded Vector Fonts: {res_f8.get('embedded_vector_fonts_count')} (10,000% Zoom Safe!)\n"
                            f"Combined Desktop Vector PDF: {res_f8.get('desktop_combined_pdf')}\n"
                            f"Edition Desktop Vector PDF: {res_f8.get('edition_desktop_combined_pdf')}"
                        )
                    except Exception as e:
                        BUILD_STATUS["last_log"] = f"ERROR in Full 8-Page Vector PDF Orchestrator: {e}"
                    finally:
                        BUILD_STATUS["running"] = False
                        BUILD_STATUS["current_task"] = ""
                        BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

            threading.Thread(target=_full8_worker, daemon=True).start()
            self._send_json({"ok": True, "date_str": date_str, "edition": edition_str, "p1_dummy_id": dummy_str})
            return

        if path == "/api/alarm_1030_config":
            import ab_daily_8page_full_edition_orchestrator as full_orch
            updated = full_orch.save_daily_1030pm_alarm_config(payload)
            self._send_json({"ok": True, "config": updated, "alarm": full_orch.get_next_1030pm_alarm_status()})
            return

        if path == "/api/trigger_1030pm_now":
            if BUILD_STATUS["running"]:
                self._send_json({"ok": False, "error": "अभी Page Designer में पेज Draw हो रहा है, कृपया कुछ सेकंड प्रतीक्षा करें।"})
                return
            target_dt = (payload.get("target_edition_date") or "").strip() or None
            dummy_str = (payload.get("p1_dummy_id") or "AUTO").strip().upper()

            def _night1030_worker():
                with BUILD_LOCK:
                    BUILD_STATUS["running"] = True
                    BUILD_STATUS["current_task"] = "⏰ [10:30 PM NIGHT-DESK AUTO ALARM] ताज़ा खबरें कलेक्ट करके सभी 7 संस्करण (4 राज्य) + 1–8 Single Vector PDFs तैयार हो रहे हैं..."
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    try:
                        import ab_daily_8page_full_edition_orchestrator as full_orch

                        def _prog(m):
                            BUILD_STATUS["current_task"] = m
                            BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

                        res_1030 = full_orch.run_1030pm_night_desk_auto_edition_job(
                            target_edition_date=target_dt,
                            p1_dummy_id=dummy_str,
                            progress_cb=_prog,
                        )
                        BUILD_STATUS["last_log"] = (
                            f"[10:30 PM NIGHT-DESK AUTO EDITION COMPLETED ({res_1030.get('date_str')})]\n"
                            f"Editions Built: {res_1030.get('editions_count')} across {res_1030.get('states_count')} States\n"
                            f"Archive Dir: {res_1030.get('archive_dir')}"
                        )
                    except Exception as e:
                        BUILD_STATUS["last_log"] = f"ERROR in 10:30 PM Night-Desk Job: {e}"
                    finally:
                        BUILD_STATUS["running"] = False
                        BUILD_STATUS["current_task"] = ""
                        BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

            threading.Thread(target=_night1030_worker, daemon=True).start()
            self._send_json({"ok": True, "target_edition_date": target_dt, "p1_dummy_id": dummy_str})
            return

        if path == "/api/deliver_all_7_editions":
            date_str = (payload.get("date_str") or "19-11-2026").strip()

            def _deliv_worker():
                with BUILD_LOCK:
                    BUILD_STATUS["running"] = True
                    BUILD_STATUS["current_task"] = f"सभी 7 संस्करणों ({date_str}) की 1–8 पेज Vector PDF Email + WhatsApp पर भेजी जा रही हैं और GitHub Cloud Heartbeat अपडेट हो रहा है..."
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    try:
                        import ab_cloud_whatsapp_email_delivery_engine as deliv_eng
                        res_d = deliv_eng.deliver_all_7_editions_everywhere(date_str=date_str, source="LOCAL_PC")
                        BUILD_STATUS["last_log"] = (
                            f"[DELIVERY & HYBRID HEARTBEAT UPDATED ({date_str})]\n"
                            f"Editions Found: {res_d.get('editions_found')}\n"
                            f"Email Result: {res_d.get('email_result')}\n"
                            f"WhatsApp/Telegram Result: {res_d.get('whatsapp_telegram_result')}"
                        )
                    except Exception as e:
                        BUILD_STATUS["last_log"] = f"ERROR in Delivery: {e}"
                    finally:
                        BUILD_STATUS["running"] = False
                        BUILD_STATUS["current_task"] = ""
                        BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

            threading.Thread(target=_deliv_worker, daemon=True).start()
            self._send_json({"ok": True, "date_str": date_str})
            return

        if path == "/api/make_all_7_editions_4_states":
            if BUILD_STATUS["running"]:
                self._send_json({"ok": False, "error": "अभी Page Designer में पेज Draw हो रहा है, कृपया कुछ सेकंड प्रतीक्षा करें।"})
                return
            date_str = (payload.get("date_str") or "19-11-2026").strip()
            dummy_str = (payload.get("p1_dummy_id") or "DUMMY_1").strip().upper()

            def _all7_worker():
                with BUILD_LOCK:
                    BUILD_STATUS["running"] = True
                    BUILD_STATUS["current_task"] = (
                        f"सभी 7 संस्करण (CG: रायपुर/बिलासपुर/राजनांदगांव | MP: इंदौर/भोपाल | DL: नई दिल्ली | RJ: जयपुर) "
                        f"4-State Front Page News Alter + Masthead + Print Line + 7 Single 1–8 Vector PDFs बन रहे हैं..."
                    )
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    try:
                        import ab_daily_8page_full_edition_orchestrator as full_orch

                        def _prog(m):
                            BUILD_STATUS["current_task"] = m
                            BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

                        res_all7 = full_orch.build_all_7_editions_4_states_with_single_vector_pdfs(
                            date_str=date_str,
                            p1_dummy_id=dummy_str,
                            progress_cb=_prog,
                        )
                        ed_lines = "\n".join([
                            f"  • {e['edition_code']} ({e['city_hi']} | {e['state_hi']}): {e['desktop_vector_pdf']}"
                            for e in res_all7.get("editions", [])
                        ])
                        BUILD_STATUS["last_log"] = (
                            f"[ALL 7 EDITIONS (4 STATES) + 7 SINGLE 1-8 VECTOR PDFS BUILT ({date_str})]\n"
                            f"{ed_lines}\n"
                            f"Archive Folder: {res_all7.get('archive_dir')}"
                        )
                    except Exception as e:
                        BUILD_STATUS["last_log"] = f"ERROR in Make All 7 Editions: {e}"
                    finally:
                        BUILD_STATUS["running"] = False
                        BUILD_STATUS["current_task"] = ""
                        BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

            threading.Thread(target=_all7_worker, daemon=True).start()
            self._send_json({"ok": True, "date_str": date_str, "p1_dummy_id": dummy_str})
            return

        if path == "/api/daily_p1_front":
            if BUILD_STATUS["running"]:
                self._send_json({"ok": False, "error": "अभी Page Designer में पेज Draw हो रहा है, कृपया कुछ सेकंड प्रतीक्षा करें।"})
                return
            date_str = (payload.get("date_str") or "19-11-2026").strip()
            edition_str = (payload.get("edition") or "RAIPUR").strip().upper()
            dummy_str = (payload.get("dummy_id") or "AUTO").strip().upper()

            def _p1_worker():
                with BUILD_LOCK:
                    BUILD_STATUS["running"] = True
                    BUILD_STATUS["current_task"] = f"पेज 01 फ्रंट पेज ({edition_str} | {date_str} | {dummy_str} | 11 खबरें • 3 CM/State + 8 National/Intl/Biz/Sports • 0% Repeat) तैयार हो रहा है..."
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    try:
                        os.environ["AB_EDITION"] = edition_str
                        os.environ["AB_EDITION_DATE"] = date_str
                        import ab_front_page1_4dummies_engine as p1_eng
                        res_p1 = p1_eng.build_aditya_bharat_page1_with_dummy(
                            date_str=date_str,
                            edition_code=edition_str,
                            dummy_id=dummy_str,
                            export_desktop_pdf=True,
                        )
                        BUILD_STATUS["last_log"] = (
                            f"[PAGE 01 FRONT PAGE BUILT ({edition_str} | {date_str} | {res_p1.get('dummy_id')})]\n"
                            f"Stories: {res_p1.get('stories_count')} (3 {res_p1.get('state_group')} CM/State + 8 National/Intl/Biz/Sports)\n"
                            f"Zero Cross-Page Duplicates: {res_p1.get('zero_cross_page_duplicates')}\n"
                            f"Headline Pts: {res_p1.get('headline_pts')}\n"
                            f"Desktop PDF: {res_p1.get('desktop_pdf')}"
                        )
                    except Exception as e:
                        BUILD_STATUS["last_log"] = f"ERROR in Page 01 Front Page: {e}"
                    finally:
                        BUILD_STATUS["running"] = False
                        BUILD_STATUS["current_task"] = ""
                        BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

            threading.Thread(target=_p1_worker, daemon=True).start()
            self._send_json({"ok": True, "date_str": date_str, "edition": edition_str, "dummy_id": dummy_str})
            return

        if path == "/api/daily_p4_edit":
            if BUILD_STATUS["running"]:
                self._send_json({"ok": False, "error": "अभी Page Designer में पेज Draw हो रहा है, कृपया कुछ सेकंड प्रतीक्षा करें।"})
                return
            date_str = (payload.get("date_str") or "19-11-2026").strip()
            edition_str = (payload.get("edition") or "RAIPUR").strip().upper()
            force_next = bool(payload.get("force_next_series", False))

            def _p4_worker():
                with BUILD_LOCK:
                    BUILD_STATUS["running"] = True
                    BUILD_STATUS["current_task"] = f"पेज 04 संपादकीय ({edition_str} | {date_str} | आदित्य भारत सेंटर लोगो + दैनिक संपादकीय व आलेख) तैयार हो रहा है..."
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    try:
                        os.environ["AB_EDITION"] = edition_str
                        os.environ["AB_EDITION_DATE"] = date_str
                        import ab_sampadakiya_page4_engine as p4_eng
                        res_p4 = p4_eng.build_daily_sampadakiya_page4(
                            date_str=date_str,
                            edition_code=edition_str,
                            force_next_series=force_next,
                        )
                        BUILD_STATUS["last_log"] = (
                            f"[PAGE 04 SAMPADAKIYA BUILT ({edition_str} | {date_str} | {res_p4.get('package_id')})]\n"
                            f"Editorial 1: {res_p4.get('edit1_head')}\n"
                            f"Lead Opinion: {res_p4.get('lead_headline')}\n"
                            f"Desktop PDF: {res_p4.get('desktop_pdf')}"
                        )
                    except Exception as e:
                        BUILD_STATUS["last_log"] = f"ERROR in Page 04 Sampadakiya: {e}"
                    finally:
                        BUILD_STATUS["running"] = False
                        BUILD_STATUS["current_task"] = ""
                        BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

            threading.Thread(target=_p4_worker, daemon=True).start()
            self._send_json({"ok": True, "date_str": date_str, "edition": edition_str, "force_next_series": force_next})
            return

        if path == "/api/daily_p5_pradeshik":
            if BUILD_STATUS["running"]:
                self._send_json({"ok": False, "error": "अभी Page Designer में पेज Draw हो रहा है, कृपया कुछ सेकंड प्रतीक्षा करें।"})
                return
            date_str = (payload.get("date_str") or "19-11-2026").strip()
            edition_str = (payload.get("edition") or "RAIPUR").strip().upper()

            def _p5_worker():
                with BUILD_LOCK:
                    BUILD_STATUS["running"] = True
                    BUILD_STATUS["current_task"] = f"पेज 05 प्रादेशिक ({edition_str} | {date_str} | MP + CG + Rajasthan + Delhi • 12 नॉन-रिपीटिंग खबरें + सेंटर लोगो) तैयार हो रहा है..."
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    try:
                        os.environ["AB_EDITION"] = edition_str
                        os.environ["AB_EDITION_DATE"] = date_str
                        import ab_pradeshik_page5_12news_engine as p5_eng
                        res_p5 = p5_eng.build_aditya_bharat_page5_pradeshik_12news(
                            date_str=date_str,
                            edition_code=edition_str,
                            export_desktop_pdf=True,
                        )
                        BUILD_STATUS["last_log"] = (
                            f"[PAGE 05 PRADESHIK 12-STORIES BUILT ({edition_str} | {date_str})]\n"
                            f"States: {res_p5.get('states_covered')}\n"
                            f"Zero Cross-Page Duplicates: {res_p5.get('zero_cross_page_duplicates')}\n"
                            f"Headline Pts: {res_p5.get('headline_pts')}\n"
                            f"Desktop PDF: {res_p5.get('desktop_pdf')}"
                        )
                    except Exception as e:
                        BUILD_STATUS["last_log"] = f"ERROR in Page 05 Pradeshik: {e}"
                    finally:
                        BUILD_STATUS["running"] = False
                        BUILD_STATUS["current_task"] = ""
                        BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

            threading.Thread(target=_p5_worker, daemon=True).start()
            self._send_json({"ok": True, "date_str": date_str, "edition": edition_str})
            return

        if path == "/api/daily_p6_business":
            if BUILD_STATUS["running"]:
                self._send_json({"ok": False, "error": "अभी Page Designer में पेज Draw हो रहा है, कृपया कुछ सेकंड प्रतीक्षा करें।"})
                return
            date_str = (payload.get("date_str") or "19-11-2026").strip()
            edition_str = (payload.get("edition") or "RAIPUR").strip().upper()
            force_next = bool(payload.get("force_next_series", False))

            def _p6_worker():
                with BUILD_LOCK:
                    BUILD_STATUS["running"] = True
                    BUILD_STATUS["current_task"] = f"पेज 06 कारोबार ({edition_str} | {date_str} | आदित्य भारत सेंटर लोगो + 9 बिजनेस खबरें + बाजार मीटर) तैयार हो रहा है..."
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    try:
                        os.environ["AB_EDITION"] = edition_str
                        os.environ["AB_EDITION_DATE"] = date_str
                        import ab_karobar_page6_engine as p6_eng
                        res_p6 = p6_eng.build_daily_karobar_page6(
                            date_str=date_str,
                            edition_code=edition_str,
                            force_next_series=force_next,
                        )
                        BUILD_STATUS["last_log"] = (
                            f"[PAGE 06 KAROBAR BUILT ({edition_str} | {date_str} | {res_p6.get('package_id')})]\n"
                            f"Flyer: {res_p6.get('flyer_headline')}\n"
                            f"Lead: {res_p6.get('lead_headline')}\n"
                            f"Desktop PDF: {res_p6.get('desktop_pdf')}"
                        )
                    except Exception as e:
                        BUILD_STATUS["last_log"] = f"ERROR in Page 06 Karobar: {e}"
                    finally:
                        BUILD_STATUS["running"] = False
                        BUILD_STATUS["current_task"] = ""
                        BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

            threading.Thread(target=_p6_worker, daemon=True).start()
            self._send_json({"ok": True, "date_str": date_str, "edition": edition_str, "force_next_series": force_next})
            return

        if path == "/api/daily_p7_sports_film":
            if BUILD_STATUS["running"]:
                self._send_json({"ok": False, "error": "अभी Page Designer में पेज Draw हो रहा है, कृपया कुछ सेकंड प्रतीक्षा करें।"})
                return
            date_str = (payload.get("date_str") or "19-11-2026").strip()
            edition_str = (payload.get("edition") or "RAIPUR").strip().upper()

            def _p7_worker():
                with BUILD_LOCK:
                    BUILD_STATUS["running"] = True
                    BUILD_STATUS["current_task"] = f"पेज 07 खेल संसार + सिने संसार ({edition_str} | {date_str} | 8 खेल + 3 फिल्म खबरें + 5 सिल्हूट कटआउट + सेंटर लोगो) तैयार हो रहा है..."
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    try:
                        os.environ["AB_EDITION"] = edition_str
                        os.environ["AB_EDITION_DATE"] = date_str
                        import ab_khel_film_page7_engine as p7_eng
                        res_p7 = p7_eng.build_aditya_bharat_page7_khel_film_11news(
                            date_str=date_str,
                            edition_code=edition_str,
                            export_desktop_pdf=True,
                        )
                        BUILD_STATUS["last_log"] = (
                            f"[PAGE 07 KHEL + FILM CUTOUTS BUILT ({edition_str} | {date_str})]\n"
                            f"Sports: {res_p7.get('sports_stories_count')} | Film: {res_p7.get('film_stories_count')} | Cutouts: {res_p7.get('cutouts_count')}\n"
                            f"Headline Pts: {res_p7.get('headline_pts')}\n"
                            f"Desktop PDF: {res_p7.get('desktop_pdf')}"
                        )
                    except Exception as e:
                        BUILD_STATUS["last_log"] = f"ERROR in Page 07 Sports+Film: {e}"
                    finally:
                        BUILD_STATUS["running"] = False
                        BUILD_STATUS["current_task"] = ""
                        BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

            threading.Thread(target=_p7_worker, daemon=True).start()
            self._send_json({"ok": True, "date_str": date_str, "edition": edition_str})
            return

        if path == "/api/daily_p8_70_30":
            if BUILD_STATUS["running"]:
                self._send_json({"ok": False, "error": "अभी Page Designer में पेज Draw हो रहा है, कृपया कुछ सेकंड प्रतीक्षा करें।"})
                return
            date_str = (payload.get("date_str") or "18-11-2026").strip()
            edition_str = (payload.get("edition") or "RAIPUR").strip().upper()
            force_fresh = bool(payload.get("force_fresh_live", False))
            export_pdf = bool(payload.get("export_desktop_pdf", True))

            def _p8_worker():
                with BUILD_LOCK:
                    BUILD_STATUS["running"] = True
                    BUILD_STATUS["current_task"] = f"पेज 08 देश-विदेश ({edition_str} | {date_str} | 70% राष्ट्रीय + 30% अंतरराष्ट्रीय + Print Line) तैयार हो रहा है..."
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    try:
                        os.environ["AB_EDITION"] = edition_str
                        os.environ["AB_EDITION_DATE"] = date_str
                        import ab_desh_videsh_page8_engine as p8_eng
                        res_p8 = p8_eng.build_desh_videsh_page8_70_30(
                            date_str=date_str,
                            edition=edition_str,
                            force_fresh_live=force_fresh,
                            export_desktop_pdf=export_pdf,
                        )
                        BUILD_STATUS["last_log"] = (
                            f"[PAGE 08 DESH-VIDESH 70/30 BUILT ({edition_str} | {date_str})]\n"
                            f"Page 08 Pts: {res_p8['headline_pts']}\n"
                            f"Desktop PDF: {res_p8.get('desktop_pdf')}"
                        )
                    except Exception as e:
                        BUILD_STATUS["last_log"] = f"ERROR in Page 08 Desh-Videsh: {e}"
                    finally:
                        BUILD_STATUS["running"] = False
                        BUILD_STATUS["current_task"] = ""
                        BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

            threading.Thread(target=_p8_worker, daemon=True).start()
            self._send_json({"ok": True, "date_str": date_str, "edition": edition_str, "force_fresh_live": force_fresh})
            return

        if path == "/api/daily_cg_10x2":
            if BUILD_STATUS["running"]:
                self._send_json({"ok": False, "error": "अभी Page Designer में पेज Draw हो रहा है, कृपया कुछ सेकंड प्रतीक्षा करें।"})
                return
            date_str = (payload.get("date_str") or "18-11-2026").strip()
            force_fresh = bool(payload.get("force_fresh_live", False))
            export_pdf = bool(payload.get("export_desktop_pdf", True))

            def _cg_worker():
                with BUILD_LOCK:
                    BUILD_STATUS["running"] = True
                    BUILD_STATUS["current_task"] = f"छत्तीसगढ़ 10+10 खबरें ({date_str} | Fresh={force_fresh}) + असली फोटो + Page 02 & 03 + Desktop PDF तैयार हो रहे हैं..."
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    try:
                        import ab_chhattisgarh_10x2_engine as cg_eng
                        res_cg = cg_eng.build_both_chhattisgarh_pages_2_and_3(
                            date_str=date_str,
                            force_fresh_live=force_fresh,
                            export_desktop_pdf=export_pdf,
                        )
                        BUILD_STATUS["last_log"] = (
                            f"[DAILY CHHATTISGARH 10+10 BUILT ({date_str})]\n"
                            f"Page 02 Pts: {res_cg['page_02']['headline_pts']}\n"
                            f"Page 03 Pts: {res_cg['page_03']['headline_pts']}\n"
                            f"Desktop PDFs: {res_cg.get('desktop_pdfs')}"
                        )
                    except Exception as e:
                        BUILD_STATUS["last_log"] = f"ERROR in Daily CG 10+10: {e}"
                    finally:
                        BUILD_STATUS["running"] = False
                        BUILD_STATUS["current_task"] = ""
                        BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

            threading.Thread(target=_cg_worker, daemon=True).start()
            self._send_json({"ok": True, "date_str": date_str, "force_fresh_live": force_fresh})
            return

        if path == "/api/draw":
            if BUILD_STATUS["running"]:
                self._send_json({"ok": False, "error": "अभी Page Designer में पेज Draw हो रहा है, कृपया कुछ सेकंड प्रतीक्षा करें।"})
                return
            pages = payload.get("pages") or ["page_01"]
            keep_tabs = bool(payload.get("keep_tabs", False))
            combined_book = bool(payload.get("combined_book", False))
            run_builder_script_async(pages, keep_tabs=keep_tabs, combined_book=combined_book)
            self._send_json({"ok": True, "started": pages, "combined_book": combined_book})
            return

        self.send_error(404, "Not found")


def start_daily_1030pm_alarm_daemon():
    """
    24x7 Background Daemon Thread inside Port 2424 App:
    Checks local clock every 10 seconds. When local time reaches `alarm_time_24h` (default `22:30` / `10:30 PM`),
    automatically harvests the day's updated news and builds the complete 8-page newspaper across all 7 editions
    (4 states: CG, MP, DL, RJ) with Single 1-to-8 Pure Vector PDFs!
    """
    import datetime
    import ab_daily_8page_full_edition_orchestrator as full_orch
    full_orch.save_daily_1030pm_alarm_config({})

    def _alarm_loop():
        while True:
            try:
                cfg = full_orch.load_daily_1030pm_alarm_config()
                if cfg.get("enabled", True) and not BUILD_STATUS["running"]:
                    now = datetime.datetime.now()
                    cur_hm = now.strftime("%H:%M")
                    today_iso = now.strftime("%Y-%m-%d")
                    target_hm = (cfg.get("alarm_time_24h") or "22:30").strip()
                    if cur_hm == target_hm and cfg.get("last_triggered_date") != today_iso:
                        with BUILD_LOCK:
                            BUILD_STATUS["running"] = True
                            BUILD_STATUS["current_task"] = f"⏰ [AUTO 10:30 PM ALARM FIRED ({cur_hm})] ताज़ा खबरें खींचकर सभी 7 संस्करण (Pages 1–8) बन रहे हैं..."
                            BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                            try:
                                def _prog(m):
                                    BUILD_STATUS["current_task"] = m
                                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")

                                res_auto = full_orch.run_1030pm_night_desk_auto_edition_job(
                                    target_edition_date=None,
                                    p1_dummy_id=cfg.get("default_p1_dummy", "AUTO"),
                                    progress_cb=_prog,
                                )
                                BUILD_STATUS["last_log"] = (
                                    f"[AUTO 10:30 PM ALARM EDITION COMPLETED ({res_auto.get('date_str')})]\n"
                                    f"Built {res_auto.get('editions_count')} Editions (4 States) in {res_auto.get('elapsed_sec')}s\n"
                                    f"Archive: {res_auto.get('archive_dir')}"
                                )
                            except Exception as e:
                                BUILD_STATUS["last_log"] = f"ERROR in Auto 10:30 PM Alarm: {e}"
                            finally:
                                BUILD_STATUS["running"] = False
                                BUILD_STATUS["current_task"] = ""
                                BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
            except Exception:
                pass
            time.sleep(10.0)

    t = threading.Thread(target=_alarm_loop, daemon=True)
    t.start()


def main():
    start_daily_1030pm_alarm_daemon()
    server = ThreadingHTTPServer(("0.0.0.0", STUDIO_PORT), AdityaBharatStudioHandler)
    print(f"======================================================================")
    print(f" ADITYA BHARAT 5-IN-1 SUPER STUDIO ON  : http://127.0.0.1:{STUDIO_PORT}")
    print(f" Alternate Link                        : http://localhost:{STUDIO_PORT}")
    print(f" Daily Auto-Edition Alarm              : ACTIVE AT 10:30 PM (22:30 IST) DAILY")
    print(f" Vault Directory                       : {VAULT_DIR}")
    print(f"======================================================================", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
