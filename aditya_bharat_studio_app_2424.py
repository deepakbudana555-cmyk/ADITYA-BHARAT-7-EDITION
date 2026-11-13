# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — 8-PAGE MASTER SYSTEM, DUMMY BLUEPRINT & PAGE DESIGNER STUDIO
===========================================================================================
Dedicated Non-Clashing Port : http://127.0.0.1:2424  (http://localhost:2424)
Page Designer TCP RPC Port  : 47123 (auto-launches pagedesigner.exe & brings window to front)
Vault Directory             : E:\RND\ADB HINDI EDITION\ADITYA_BHARAT_DESIGN_VAULT
"""

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
STUDIO_PORT = 2424
PD_RPC_PORT = 47123

BUILD_LOCK = threading.Lock()
BUILD_STATUS = {
    "running": False,
    "current_task": "",
    "last_log": "आदित्य भारत 8-पेज स्टूडियो तैयार है (Port 2424)। आप 1-1 पेज या सभी 8 पेज एक साथ Page Designer में Open या Draw कर सकते हैं।",
    "last_updated": time.strftime("%H:%M:%S"),
}

PAGE_Catalog = [
    {
        "id": "page_01",
        "folio": "01",
        "title_hi": "पेज 01 — फ्रंट पेज (Master Option 1)",
        "section_hi": "मुख्य पृष्ठ",
        "script": "build_aditya_bharat_page1.py",
        "pd_file": "Aditya_Bharat_Page_01_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_01_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_01_CMYK_34x53.pdf",
        "stories_count": 7,
        "min_head_pt": "34.0 pt",
        "max_head_pt": "74.0 pt",
        "layout_tag": "6cm मास्टहेड + 8-Col फ्लायर + 5-Col लीड + 1+5+2 बॉटम एंकर",
        "summary_hi": "ऊपर 6.0 cm फ्रंट मास्टहेड ज़ोन, 12.5 cm का 8-कॉलम टॉप फ्लायर (Cols 4..5 में सेंटर फोटो), बीच में 5-कॉलम मेन लीड + दाएं 3-कॉलम में सेकंड लीड व 2 खबरें, और नीचे 1 + 5 + 2 कॉलम का बॉटम एंकर बैंड।",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 6.0, "kind": "masthead_front", "title": "ZONE 1: फ्रंट पेज मास्टहेड स्पेस (आदित्य भारत)", "meta": "Cols 1..8 | 32.0 × 6.0 cm | आरक्षित मुख्य लोगो स्पेस + डेटलाइन पट्टी"},
            {"col": 1, "span": 8, "y0": 7.0, "h": 12.5, "kind": "flyer", "title": "STORY 1: 8-कॉलम टॉप फ्लायर पैकेज (6-Col Text + 2-Col Center Photo)", "meta": "Cols 1..8 | 12.5 cm | ऊपर 18pt Subhead + 64pt DB Rasrand Bold Headline | Cols 4..5 में Photo + Caption"},
            {"col": 1, "span": 1, "y0": 19.8, "h": 21.85, "kind": "gray_box", "title": "40% Gray लीड बॉक्स", "meta": "Col 1 | 21.85 cm | 2.5mm चारों तरफ इनसेट | 18pt Box Head"},
            {"col": 2, "span": 4, "y0": 19.8, "h": 21.85, "kind": "lead", "title": "STORY 2: 5-कॉलम मेन लीड पैकेज (2-Line 74pt Headline + Subhead)", "meta": "Cols 1..5 (Body Cols 2..5) | 21.85 cm | Cols 3..4 में लीड फोटो + हाइलाइट बॉक्स + अंडरफ्लो"},
            {"col": 6, "span": 3, "y0": 19.8, "h": 11.2, "kind": "story_photo", "title": "STORY 3: दाएं 3-कॉलम सेकंड लीड (Photo + Body)", "meta": "Cols 6..8 | 11.2 cm | 42pt 2-Line Headline + Subhead + Photo"},
            {"col": 6, "span": 2, "y0": 31.3, "h": 10.35, "kind": "story", "title": "STORY 4: थर्ड न्यूज़ (2-Col)", "meta": "Cols 6..7 | 10.35 cm | 36pt 2-Line Headline + Red Blurb"},
            {"col": 8, "span": 1, "y0": 31.3, "h": 10.35, "kind": "story", "title": "STORY 5: सिंगल कॉलम", "meta": "Col 8 | 10.35 cm | 34pt Headline"},
            {"col": 1, "span": 1, "y0": 42.0, "h": 10.0, "kind": "story", "title": "STORY 6: बाएं 1-Col खबर", "meta": "Col 1 | 10.0 cm | 34pt Headline"},
            {"col": 2, "span": 5, "y0": 42.0, "h": 10.0, "kind": "anchor", "title": "STORY 7: बॉटम 5-कॉलम सेंटर एंकर (48pt Headline + Subhead + Photo)", "meta": "Cols 2..6 | 10.0 cm | Cols 3..4 में सेंटर फोटो + 5-कॉलम टेक्स्ट"},
            {"col": 7, "span": 2, "y0": 42.0, "h": 10.0, "kind": "story", "title": "STORY 8: दाएं 2-Col खबर", "meta": "Cols 7..8 | 10.0 cm | 36pt Headline"}
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
            {"col": 1, "span": 8, "y0": 7.0, "h": 12.5, "kind": "flyer", "title": "STORY 1: 8-कॉलम टॉप फ्लायर पैकेज", "meta": "Cols 1..8 | 12.5 cm | 18pt Subhead + 64pt Headline + Cols 4..5 Photo"},
            {"col": 1, "span": 1, "y0": 19.8, "h": 21.85, "kind": "gray_box", "title": "40% Gray लीड बॉक्स", "meta": "Col 1 | 21.85 cm | 2.5mm इनसेट"},
            {"col": 2, "span": 4, "y0": 19.8, "h": 21.85, "kind": "lead", "title": "STORY 2: 5-कॉलम मेन लीड (Option 2 Package)", "meta": "Cols 1..5 | 21.85 cm | 74pt Headline + Photo + Box"},
            {"col": 6, "span": 3, "y0": 19.8, "h": 11.2, "kind": "story_photo", "title": "STORY 3: दाएं 3-कॉलम सेकंड लीड", "meta": "Cols 6..8 | 11.2 cm | 42pt Headline + Photo"},
            {"col": 6, "span": 2, "y0": 31.3, "h": 10.35, "kind": "story", "title": "STORY 4: 2-Col खबर", "meta": "Cols 6..7 | 10.35 cm | 36pt Headline"},
            {"col": 8, "span": 1, "y0": 31.3, "h": 10.35, "kind": "story", "title": "STORY 5: 1-Col खबर", "meta": "Col 8 | 10.35 cm | 34pt Headline"},
            {"col": 1, "span": 1, "y0": 42.0, "h": 10.0, "kind": "story", "title": "STORY 6: 1-Col खबर", "meta": "Col 1 | 10.0 cm | 34pt Headline"},
            {"col": 2, "span": 5, "y0": 42.0, "h": 10.0, "kind": "anchor", "title": "STORY 7: बॉटम 5-कॉलम सेंटर एंकर", "meta": "Cols 2..6 | 10.0 cm | 48pt Headline + Photo"},
            {"col": 7, "span": 2, "y0": 42.0, "h": 10.0, "kind": "story", "title": "STORY 8: दाएं 2-Col खबर", "meta": "Cols 7..8 | 10.0 cm | 36pt Headline"}
        ]
    },
    {
        "id": "page_02",
        "folio": "02",
        "title_hi": "पेज 02 — महानगर (City Page 1)",
        "section_hi": "महानगर",
        "script": "build_aditya_bharat_page2.py",
        "pd_file": "Aditya_Bharat_Page_02_Mahanagar_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_02_Mahanagar_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_02_Mahanagar_CMYK_34x53.pdf",
        "stories_count": 8,
        "min_head_pt": "32.0 pt",
        "max_head_pt": "66.0 pt",
        "layout_tag": "8-Col सिटी फ्लायर + 5-Col लीड + 3-Col स्टोरी + 2+4+2 मिड + 2+6 सिटी एंकर",
        "summary_hi": "1.5 cm इनसाइड मास्टहेड ('महानगर' रेड बॉक्स + '02'), 8-कॉलम मेट्रो फ्लायर, बाएं 5-कॉलम स्मार्ट हेल्थ लीड + दाएं 3-कॉलम रिवरफ्रंट स्टोरी, बीच में 2+4+2 इंटरलॉक बैंड, और नीचे 2+6 कॉलम का सिटी एंकर।",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 1.5, "kind": "masthead_inside", "title": "1.5 cm रनिंग मास्टहेड : [महानगर] | आदित्य भारत | इंदौर, मंगलवार | 02", "meta": "Cols 1..8 | 1.5 cm | नीचे 2.0pt 60% Gray Rule"},
            {"col": 1, "span": 8, "y0": 2.85, "h": 10.2, "kind": "flyer", "title": "STORY 1: 8-कॉलम महानगर टॉप फ्लायर (इंदौर-भोपाल मेट्रो विस्तार)", "meta": "Cols 1..8 | 10.2 cm | 18pt Subhead + 66pt Headline + Cols 4..5 Photo + 'सौगात' Blurb"},
            {"col": 1, "span": 5, "y0": 13.4, "h": 16.5, "kind": "lead", "title": "STORY 2: 5-कॉलम सिटी मेन लीड (स्मार्ट हेल्थ मिशन व सुपर स्पेशियलिटी)", "meta": "Cols 1..5 | 16.5 cm | 56pt 2-Line Headline + Subhead + Cols 3..4 Photo & Highlight Box"},
            {"col": 6, "span": 3, "y0": 13.4, "h": 16.5, "kind": "story_photo", "title": "STORY 3: दाएं 3-कॉलम सचित्र पैकेज (कान्ह-सरस्वती रिवरफ्रंट)", "meta": "Cols 6..8 | 16.5 cm | 38pt Headline + Cols 7..8 Photo + Underflow"},
            {"col": 1, "span": 2, "y0": 30.25, "h": 10.6, "kind": "story", "title": "STORY 4: बाएं 2-Col ट्रैफिक/फ्लाईओवर खबर", "meta": "Cols 1..2 | 10.6 cm | 34pt Headline + 'यातायात' Blurb"},
            {"col": 3, "span": 4, "y0": 30.25, "h": 10.6, "kind": "story_photo", "title": "STORY 5: बीच में 4-कॉलम सचित्र पैकेज (आईटी पार्क व स्टार्टअप हब)", "meta": "Cols 3..6 | 10.6 cm | 39pt Headline + Cols 4..5 Photo"},
            {"col": 7, "span": 2, "y0": 30.25, "h": 10.6, "kind": "story", "title": "STORY 6: दाएं 2-Col स्वच्छता/सोलर खबर", "meta": "Cols 7..8 | 10.6 cm | 33pt Headline"},
            {"col": 1, "span": 2, "y0": 41.2, "h": 10.8, "kind": "story", "title": "STORY 7: बाएं 2-Col राजवाड़ा धरोहर स्टोरी", "meta": "Cols 1..2 | 10.8 cm | 34pt Headline + 'धरोहर' Blurb"},
            {"col": 3, "span": 6, "y0": 41.2, "h": 10.8, "kind": "anchor", "title": "STORY 8: दाएं 6-कॉलम महानगर बॉटम एंकर (मालवा लोक उत्सव व सांस्कृतिक संध्या)", "meta": "Cols 3..8 | 10.8 cm | 49pt Headline + Subhead + Cols 5..6 Photo"}
        ]
    },
    {
        "id": "page_03",
        "folio": "03",
        "title_hi": "पेज 03 — प्रादेशिक (Vertical-Start Layout)",
        "section_hi": "प्रादेशिक",
        "script": "build_aditya_bharat_page3.py",
        "pd_file": "Aditya_Bharat_Page_03_Pradeshik_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_03_Pradeshik_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_03_Pradeshik_CMYK_34x53.pdf",
        "stories_count": 11,
        "min_head_pt": "30.0 pt",
        "max_head_pt": "52.5 pt",
        "layout_tag": "No-Flyer Vertical Start: बाएं 5-Col लीड (आखिरी Col 5 में Gray Box) + दाएं 3-Col स्टैक",
        "summary_hi": "ऊपर फ्लायर के बिना सीधा बाएं 5-कॉलम वर्टिकल लीड (खबर Col 1 से शुरू, आखिरी Col 5 में फुल-हाइट 40% Gray बॉक्स), नीचे 3+2 खबरें, दाएं 3-कॉलम में 3 स्टैक्ड पैकेज + फैक्ट बॉक्स, मिड में 2+4+2 बैंड, और नीचे 6+2 बॉटम एंकर। सभी 11 हेडलाइन >= 30 pt!",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 1.5, "kind": "masthead_inside", "title": "1.5 cm रनिंग मास्टहेड : [प्रादेशिक] | आदित्य भारत | इंदौर, मंगलवार | 03", "meta": "Cols 1..8 | 1.5 cm | नीचे 2.0pt 60% Gray Rule"},
            {"col": 1, "span": 4, "y0": 2.85, "h": 19.6, "kind": "lead", "title": "STORY 1: बाएं 5-कॉलम वर्टिकल लीड (औद्योगिक कॉरिडोर — No Top Flyer!)", "meta": "Cols 1..4 Body + Compact Photo (Cols 1..2, 11-line underflow) | 52.5pt 2-Line Headline + Subhead"},
            {"col": 5, "span": 1, "y0": 5.5, "h": 16.95, "kind": "gray_box", "title": "40% Gray Box (Col 5)", "meta": "आखिरी Col 5 में फुल-हाइट 40% Gray Box (100% भरा हुआ)"},
            {"col": 1, "span": 3, "y0": 22.8, "h": 8.05, "kind": "story", "title": "STORY 2: नर्मदा-क्षिप्रा सिंचाई लिंक (3-Col)", "meta": "Cols 1..3 | 8.05 cm | 33.0pt Headline + 'सिंचाई' Blurb"},
            {"col": 4, "span": 2, "y0": 22.8, "h": 8.05, "kind": "story", "title": "STORY 3: मेडिकल कॉलेज सीटें (2-Col)", "meta": "Cols 4..5 | 8.05 cm | 30.0pt Headline + 'स्वास्थ्य' Blurb"},
            {"col": 6, "span": 3, "y0": 2.85, "h": 10.6, "kind": "story_photo", "title": "STORY 4: दाएं टॉप 3-Col सचित्र खबर (अटल एक्सप्रेस-वे)", "meta": "Cols 6..8 | 10.6 cm | 37.0pt Headline + Cols 7..8 Compact Photo"},
            {"col": 6, "span": 3, "y0": 13.8, "h": 8.3, "kind": "story", "title": "STORY 5: दाएं मिड 3-Col खबर (सेमीकंडक्टर व एआई लैब)", "meta": "Cols 6..8 | 8.3 cm | 36.5pt Headline + 'शिक्षा' Blurb"},
            {"col": 6, "span": 2, "y0": 22.45, "h": 8.4, "kind": "story", "title": "STORY 6: सोलर पंप सब्सिडी (2-Col)", "meta": "Cols 6..7 | 8.4 cm | 34.5pt Headline"},
            {"col": 8, "span": 1, "y0": 22.45, "h": 8.4, "kind": "gray_box", "title": "निवेश एक नजर (Box)", "meta": "Col 8 | 8.4 cm | 15% Gray Fact Box"},
            {"col": 1, "span": 2, "y0": 31.2, "h": 9.7, "kind": "story", "title": "STORY 7: ई-मंडी भुगतान (2-Col)", "meta": "Cols 1..2 | 9.7 cm | 30.0pt Headline"},
            {"col": 3, "span": 4, "y0": 31.2, "h": 9.7, "kind": "story_photo", "title": "STORY 8: बीच में 4-कॉलम सचित्र पैकेज (सीएम राइज व स्मार्ट स्कूल)", "meta": "Cols 3..6 | 9.7 cm | 37.5pt Headline + Subhead + Cols 4..5 Photo"},
            {"col": 7, "span": 2, "y0": 31.2, "h": 9.7, "kind": "story", "title": "STORY 9: महिला स्व-सहायता समूह (2-Col)", "meta": "Cols 7..8 | 9.7 cm | 33.0pt Headline"},
            {"col": 1, "span": 6, "y0": 41.25, "h": 10.75, "kind": "anchor", "title": "STORY 10: बाएं 6-कॉलम प्रादेशिक बॉटम एंकर (टाइगर रिजर्व व इको-हेरिटेज सर्किट)", "meta": "Cols 1..6 | 10.75 cm | 50.0pt 1-Line Headline + Subhead + Cols 3..4 Photo (9-line underflow)"},
            {"col": 7, "span": 2, "y0": 41.25, "h": 10.75, "kind": "story", "title": "STORY 11: दाएं 2-Col टेक्सटाइल पार्क खबर", "meta": "Cols 7..8 | 10.75 cm | 30.5pt Headline"}
        ]
    },
    {
        "id": "page_04",
        "folio": "04",
        "title_hi": "पेज 04 — संपादकीय (Editorial & Opinion Page)",
        "section_hi": "संपादकीय",
        "script": "build_aditya_bharat_page5_edit.py",
        "pd_file": "Aditya_Bharat_Page_04_Sampadakiya_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_04_Sampadakiya_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_04_Sampadakiya_CMYK_34x53.pdf",
        "stories_count": 8,
        "min_head_pt": "30.5 pt",
        "max_head_pt": "42.5 pt",
        "layout_tag": "बाएं 2-Col संपादकीय रेल + दाएं 6-Col मंथन आलेख + 4+2 विश्लेषण + 3+3 पत्र व इतिहास",
        "summary_hi": "पेज 04 पर गुजरात समाचार शैली का कसा हुआ संपादकीय लेआउट — बाएं 2 कॉलम (Cols 1..2) में मुख्य संपादकीय 1, संपादकीय 2 और 'ऊर्जा' प्रेरक स्तंभ; दाएं 6 कॉलम (Cols 3..8) में टॉप मंथन आलेख, 4+2 विशेष विश्लेषण व लोकतंत्र की नब्ज, और नीचे 3+3 में पाठकों के पत्र व इतिहास के पन्नों से।",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 1.5, "kind": "masthead_inside", "title": "1.5 cm रनिंग मास्टहेड : [संपादकीय] | आदित्य भारत | इंदौर, मंगलवार | 04", "meta": "Cols 1..8 | 1.5 cm | नीचे 2.0pt 60% Gray Rule"},
            {"col": 1, "span": 2, "y0": 2.85, "h": 21.0, "kind": "editorial", "title": "EDITORIAL 1: मुख्य संपादकीय (आत्मनिर्भर अर्थनीति और समावेशी विकास)", "meta": "Cols 1..2 | 21.0 cm | 33.0pt DB Rasrand Bold + Gray Callout Pointer Box + 'सं' Drop-Cap"},
            {"col": 1, "span": 2, "y0": 24.15, "h": 14.3, "kind": "editorial", "title": "EDITORIAL 2: दूसरा संपादकीय (जल संरक्षण को जन-आंदोलन बनाने का समय)", "meta": "Cols 1..2 | 14.3 cm | 32.5pt 2-Line Headline + 2-Col Editorial"},
            {"col": 1, "span": 2, "y0": 38.75, "h": 13.25, "kind": "editorial", "title": "COLUMN 3: 'ऊर्जा' प्रेरक स्तंभ (संकल्प और धैर्य से ही खुलते हैं मार्ग)", "meta": "Cols 1..2 | 13.25 cm | Red Ribbon 'ऊर्जा' + 31.0pt Headline + Author Line"},
            {"col": 3, "span": 6, "y0": 2.85, "h": 18.8, "kind": "lead", "title": "FEATURE 4: 6-कॉलम मुख्य वैचारिक आलेख — 'मंथन' (कृत्रिम बुद्धिमत्ता के युग में मानवीय मूल्यों का संतुलन)", "meta": "Cols 3..8 | 18.8 cm | 42.5pt 2-Line Headline + Subhead + Author Card + Cols 5..6 Illustration"},
            {"col": 3, "span": 4, "y0": 22.0, "h": 16.45, "kind": "story_photo", "title": "ANALYSIS 5: 4-कॉलम विशेष विश्लेषण (हरित ऊर्जा क्रांति से बदलेगी ग्रामीण अर्थव्यवस्था)", "meta": "Cols 3..6 | 16.45 cm | 39.0pt Headline + Author Card + Cols 5..6 Photo"},
            {"col": 7, "span": 2, "y0": 22.0, "h": 16.45, "kind": "story", "title": "COLUMN 6: 'लोकतंत्र की नब्ज' (न्यायिक सुधार और त्वरित न्याय)", "meta": "Cols 7..8 | 16.45 cm | 30.5pt Headline + 2-Col Opinion"},
            {"col": 3, "span": 3, "y0": 38.8, "h": 13.2, "kind": "anchor", "title": "LETTERS 7: 'पाठकों के पत्र' (संपादक के नाम 3 चयनित पत्र)", "meta": "Cols 3..5 | 13.2 cm | 35.0pt Headline + 3 Reader Letters"},
            {"col": 6, "span": 3, "y0": 38.8, "h": 13.2, "kind": "anchor", "title": "HISTORY 8: 'इतिहास के पन्नों से' (आज का इतिहास व फोटो)", "meta": "Cols 6..8 | 13.2 cm | 35.0pt Headline + Historical Photo + 3 Events"}
        ]
    },
    {
        "id": "page_05",
        "folio": "05",
        "title_hi": "पेज 05 — राष्ट्रीय (National News Page)",
        "section_hi": "राष्ट्रीय",
        "script": "build_aditya_bharat_page4.py",
        "pd_file": "Aditya_Bharat_Page_05_Rashtriya_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_05_Rashtriya_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_05_Rashtriya_CMYK_34x53.pdf",
        "stories_count": 8,
        "min_head_pt": "30.5 pt",
        "max_head_pt": "59.0 pt",
        "layout_tag": "8-Col फ्लायर + 6-Col लीड (आखिरी Col 6 में Gray Box) + दाएं 2-Col + 3+3+2 बैंड + 5+3 एंकर",
        "summary_hi": "पेज 05 ('राष्ट्रीय') पर 8-कॉलम टॉप फ्लायर, उसके नीचे 6-कॉलम का बड़ा लीड पैकेज (मुख्य खबर Col 1 से शुरू, आखिरी Col 6 में फुल-हाइट 40% Gray बॉक्स) + दाएं 2-कॉलम सुप्रीम कोर्ट खबर, बीच में 3+3+2 इंटरलॉक बैंड, और नीचे 5+3 कॉलम का बॉटम एंकर।",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 1.5, "kind": "masthead_inside", "title": "1.5 cm रनिंग मास्टहेड : [राष्ट्रीय] | आदित्य भारत | इंदौर, मंगलवार | 05", "meta": "Cols 1..8 | 1.5 cm | नीचे 2.0pt 60% Gray Rule"},
            {"col": 1, "span": 8, "y0": 2.85, "h": 11.0, "kind": "flyer", "title": "STORY 1: 8-कॉलम राष्ट्रीय टॉप फ्लायर (हाई-स्पीड रेल व बुलेट कॉरिडोर)", "meta": "Cols 1..8 | 11.0 cm | 18pt Subhead + 46.5pt Headline + Cols 4..5 Compact Photo (7-line underflow)"},
            {"col": 1, "span": 5, "y0": 14.2, "h": 17.2, "kind": "lead", "title": "STORY 2: 6-कॉलम राष्ट्रीय मेन लीड (रक्षा विनिर्माण व स्वदेशी युद्धपोत — News in Cols 1..5)", "meta": "Cols 1..5 Body + Cols 3..4 Photo & 15% Box | 59.0pt 2-Line Headline + Subhead"},
            {"col": 6, "span": 1, "y0": 17.1, "h": 14.3, "kind": "gray_box", "title": "40% Gray Box (Col 6)", "meta": "6-Col लीड के आखिरी Col 6 में फुल-हाइट 40% Gray Box ('प्रमुख बिंदु')"},
            {"col": 7, "span": 2, "y0": 14.2, "h": 17.2, "kind": "story", "title": "STORY 3: दाएं 2-Col सुप्रीम कोर्ट डिजिटल गोपनीयता खबर", "meta": "Cols 7..8 | 17.2 cm | 36.0pt Headline + 'न्याय' Blurb"},
            {"col": 1, "span": 3, "y0": 31.75, "h": 9.6, "kind": "story_photo", "title": "STORY 4: बाएं 3-Col इसरो गगनयान सचित्र खबर", "meta": "Cols 1..3 | 9.6 cm | 36.0pt Headline + Cols 2..3 Photo"},
            {"col": 4, "span": 3, "y0": 31.75, "h": 9.6, "kind": "story", "title": "STORY 5: बीच में 3-Col ग्रामीण टेली-मेडिसिन पैकेज", "meta": "Cols 4..6 | 9.6 cm | 37.0pt Headline + Subhead + 'स्वास्थ्य' Blurb"},
            {"col": 7, "span": 2, "y0": 31.75, "h": 9.6, "kind": "story", "title": "STORY 6: दाएं 2-Col ग्रीन हाइड्रोजन खबर", "meta": "Cols 7..8 | 9.6 cm | 30.5pt Headline"},
            {"col": 1, "span": 5, "y0": 41.7, "h": 10.3, "kind": "anchor", "title": "STORY 7: बाएं 5-कॉलम राष्ट्रीय बॉटम एंकर (राष्ट्रीय शिक्षा नीति व कौशल विश्वविद्यालय)", "meta": "Cols 1..5 | 10.3 cm | 44.5pt 1-Line Headline + Subhead + Cols 3..4 Photo (8-line underflow)"},
            {"col": 6, "span": 3, "y0": 41.7, "h": 10.3, "kind": "story", "title": "STORY 8: दाएं 3-Col विदेशी मुद्रा भंडार पैकेज", "meta": "Cols 6..8 | 10.3 cm | 37.0pt Headline + Subhead"}
        ]
    },
    {
        "id": "page_06",
        "folio": "06",
        "title_hi": "पेज 06 — कारोबार (Business & Economy Page)",
        "section_hi": "कारोबार",
        "script": "build_aditya_bharat_page6_business.py",
        "pd_file": "Aditya_Bharat_Page_06_Karobar_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_06_Karobar_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_06_Karobar_CMYK_34x53.pdf",
        "stories_count": 10,
        "min_head_pt": "30.5 pt",
        "max_head_pt": "58.0 pt",
        "layout_tag": "बाएं 2-Col मार्केट रेल + दाएं 6-Col फ्लायर व 6-Col लीड (Col 8 में Gray Box) + 5+3 एंकर",
        "summary_hi": "पेज 06 ('कारोबार') का अलग बिज़नेस आर्किटेक्चर — बाएं Cols 1..2 में वर्टिकल मार्केट रेल (बाजार मीटर बॉक्स + 2 कॉरपोरेट/सर्राफा खबरें), दाएं Cols 3..8 में 6-कॉलम फ्लायर, 6-कॉलम लीड (आखिरी Col 8 में Gray Box), 3+3 मिड बैंड और नीचे पूरे 8 कॉलम में 5+3 स्टार्टअप एंकर।",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 1.5, "kind": "masthead_inside", "title": "1.5 cm रनिंग मास्टहेड : [कारोबार] | आदित्य भारत | इंदौर, मंगलवार | 06", "meta": "Cols 1..8 | 1.5 cm | नीचे 2.0pt 60% Gray Rule"},
            {"col": 1, "span": 2, "y0": 2.85, "h": 11.2, "kind": "gray_box", "title": "बाजार मीटर : प्रमुख सूचकांक", "meta": "Cols 1..2 | 11.2 cm | सेंसेक्स, निफ्टी, सोना, चांदी, रुपया, कच्चा तेल, एफपीआई"},
            {"col": 1, "span": 2, "y0": 14.4, "h": 13.0, "kind": "story", "title": "STORY 1 (Rail): यूपीआई ने तोड़े सारे रिकॉर्ड (2-Col)", "meta": "Cols 1..2 | 13.0 cm | 34.5pt Headline + 'डिजिटल' Blurb"},
            {"col": 1, "span": 2, "y0": 27.75, "h": 13.1, "kind": "story", "title": "STORY 2 (Rail): सोना-चांदी में भारी खरीदारी (2-Col)", "meta": "Cols 1..2 | 13.1 cm | 33.5pt Headline + 'सर्राफा' Blurb"},
            {"col": 3, "span": 6, "y0": 2.85, "h": 10.2, "kind": "flyer", "title": "STORY 3: दाएं 6-कॉलम बिजनेस टॉप फ्लायर (सेंसेक्स-निफ्टी में ऐतिहासिक उछाल)", "meta": "Cols 3..8 | 10.2 cm | 18pt Subhead + 42.5pt Headline + Cols 5..6 Photo"},
            {"col": 3, "span": 5, "y0": 13.4, "h": 16.5, "kind": "lead", "title": "STORY 4: दाएं 6-कॉलम बिजनेस मेन लीड (आरबीआई मौद्रिक नीति व विनिर्माण — Cols 3..7 Body)", "meta": "Cols 3..7 Body + Cols 4..5 Photo | 58.0pt 2-Line Headline + Subhead"},
            {"col": 8, "span": 1, "y0": 16.3, "h": 13.6, "kind": "gray_box", "title": "40% Gray Box (Col 8)", "meta": "लीड के आखिरी Col 8 में फुल-हाइट 40% Gray Box ('नीतिगत फैसले')"},
            {"col": 3, "span": 3, "y0": 30.25, "h": 10.6, "kind": "story_photo", "title": "STORY 5: 3-Col सेमीकंडक्टर व इलेक्ट्रॉनिक्स क्लस्टर सचित्र खबर", "meta": "Cols 3..5 | 10.6 cm | 36.0pt Headline + Cols 4..5 Photo"},
            {"col": 6, "span": 3, "y0": 30.25, "h": 10.6, "kind": "story", "title": "STORY 6: 3-Col एमएसएमई सस्ता ऋण व हरित ऊर्जा पैकेज", "meta": "Cols 6..8 | 10.6 cm | 36.0pt Headline + Subhead"},
            {"col": 1, "span": 5, "y0": 41.2, "h": 10.8, "kind": "anchor", "title": "STORY 7: बाएं 5-कॉलम कारोबार बॉटम एंकर (टियर-2 शहरों के स्टार्टअप्स में रिकॉर्ड निवेश)", "meta": "Cols 1..5 | 10.8 cm | 42.5pt 1-Line Headline + Subhead + Cols 3..4 Photo"},
            {"col": 6, "span": 3, "y0": 41.2, "h": 10.8, "kind": "story", "title": "STORY 8: दाएं 3-Col इलेक्ट्रिक वाहन बिक्री पैकेज", "meta": "Cols 6..8 | 10.8 cm | 35.5pt Headline + Subhead"}
        ]
    },
    {
        "id": "page_07",
        "folio": "07",
        "title_hi": "पेज 07 — खेल संसार (Sports — 12 Stories)",
        "section_hi": "खेल संसार",
        "script": "build_aditya_bharat_page7_sports.py",
        "pd_file": "Aditya_Bharat_Page_07_Khel_Sansar_34x53.pagedesigner",
        "png_file": "Aditya_Bharat_Page_07_Khel_Sansar_34x53.png",
        "pdf_file": "Aditya_Bharat_Page_07_Khel_Sansar_CMYK_34x53.pdf",
        "stories_count": 12,
        "min_head_pt": "30.0 pt",
        "max_head_pt": "55.5 pt",
        "layout_tag": "No-Flyer Asymmetric Sports: बाएं 3-Col स्टैक + दाएं 5-Col लीड (3-Col Action Photo) + 12 खबरें",
        "summary_hi": "पेज 07 ('खेल संसार') पर बिना टॉप फ्लायर के डायनामिक स्पोर्ट्स लेआउट — बाएं Cols 1..3 में 2 स्टैक्ड खबरें, दाएं Cols 4..8 में 5-कॉलम मेन स्पोर्ट्स लीड (बीच में 3-कॉलम का प्रॉपर बड़ा एक्शन फोटो + आखिरी Col 8 में मैच स्कोरकार्ड बॉक्स), मिड में 4+4, लोअर में 2+3+3, और नीचे 5+3 एंकर। कुल 12 खेल खबरें (सभी >= 30 pt)!",
        "dummy_blocks": [
            {"col": 1, "span": 8, "y0": 1.0, "h": 1.5, "kind": "masthead_inside", "title": "1.5 cm रनिंग मास्टहेड : [खेल संसार] | आदित्य भारत | इंदौर, मंगलवार | 07", "meta": "Cols 1..8 | 1.5 cm | नीचे 2.0pt 60% Gray Rule"},
            {"col": 1, "span": 3, "y0": 2.85, "h": 12.2, "kind": "story_photo", "title": "STORY 1: बाएं टॉप 3-Col चैंपियंस ट्रॉफी सचित्र पैकेज", "meta": "Cols 1..3 | 12.2 cm | 36.5pt Headline + Cols 2..3 Photo"},
            {"col": 1, "span": 3, "y0": 15.4, "h": 11.75, "kind": "story", "title": "STORY 2: बाएं मिड 3-Col महिला हॉकी एशिया कप खबर", "meta": "Cols 1..3 | 11.75 cm | 36.0pt Headline + 'हॉकी' Blurb"},
            {"col": 4, "span": 4, "y0": 2.85, "h": 16.8, "kind": "lead", "title": "STORY 3: दाएं 5-कॉलम मेन स्पोर्ट्स लीड (रोहित-विराट शतकीय साझेदारी + 3-Col Action Photo)", "meta": "Cols 4..7 Body + Cols 5..7 में 3-Col बड़ा एक्शन फोटो (5.5 cm) | 55.5pt 2-Line Headline"},
            {"col": 8, "span": 1, "y0": 5.6, "h": 14.05, "kind": "gray_box", "title": "स्कोरकार्ड (Col 8)", "meta": "लीड के आखिरी Col 8 में 40% Gray Box ('मैच स्कोरकार्ड')"},
            {"col": 4, "span": 3, "y0": 20.0, "h": 7.15, "kind": "story", "title": "STORY 4: एशियाई एथलेटिक्स स्वर्ण (3-Col)", "meta": "Cols 4..6 | 7.15 cm | 35.0pt Headline"},
            {"col": 7, "span": 2, "y0": 20.0, "h": 7.15, "kind": "story", "title": "STORY 5: प्रज्ञानानंद शतरंज खिताब (2-Col)", "meta": "Cols 7..8 | 7.15 cm | 34.0pt Headline"},
            {"col": 1, "span": 4, "y0": 27.5, "h": 8.6, "kind": "story_photo", "title": "STORY 6: बाएं 4-Col निशानेबाजी विश्व कप सचित्र खबर", "meta": "Cols 1..4 | 8.6 cm | 36.0pt Headline + Cols 2..3 Photo"},
            {"col": 5, "span": 4, "y0": 27.5, "h": 8.6, "kind": "story", "title": "STORY 7: दाएं 4-Col बैडमिंटन सुपर सीरीज खबर", "meta": "Cols 5..8 | 8.6 cm | 35.5pt Headline + 'बैडमिंटन' Blurb"},
            {"col": 1, "span": 2, "y0": 36.45, "h": 6.95, "kind": "story", "title": "STORY 8: कुश्ती ट्रायल (2-Col)", "meta": "Cols 1..2 | 6.95 cm | 34.0pt Headline"},
            {"col": 3, "span": 3, "y0": 36.45, "h": 6.95, "kind": "story", "title": "STORY 9: प्रो कबड्डी लीग (3-Col)", "meta": "Cols 3..5 | 6.95 cm | 34.5pt Headline"},
            {"col": 6, "span": 3, "y0": 36.45, "h": 6.95, "kind": "story", "title": "STORY 10: डेविस कप टेनिस (3-Col)", "meta": "Cols 6..8 | 6.95 cm | 35.5pt Headline"},
            {"col": 1, "span": 5, "y0": 43.75, "h": 8.25, "kind": "anchor", "title": "STORY 11: बाएं 5-कॉलम स्पोर्ट्स एंकर (ग्रासरूट फुटबॉल अकादमी व खेल नर्सरी)", "meta": "Cols 1..5 | 8.25 cm | 42.5pt 1-Line Headline + Subhead + Cols 3..4 Photo"},
            {"col": 6, "span": 3, "y0": 43.75, "h": 8.25, "kind": "story", "title": "STORY 12: दाएं 3-Col तीरंदाजी विश्व कप खबर", "meta": "Cols 6..8 | 8.25 cm | 30.0pt Headline"}
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
            {"col": 1, "span": 8, "y0": 2.85, "h": 8.6, "kind": "flyer", "title": "STORY 1: 8-कॉलम वर्ल्ड डिप्लोमेसी टॉप फ्लायर (सुरक्षा परिषद में भारत की स्थायी दावेदारी)", "meta": "Cols 1..8 | 8.6 cm | 16.5pt Subhead + 53.5pt Headline + Cols 4..5 UN Photo"},
            {"col": 1, "span": 4, "y0": 11.8, "h": 15.0, "kind": "lead", "title": "STORY 4: बाएं 5-कॉलम सामरिक लीड (हिंद-प्रशांत नौसैनिक महाअभ्यास — Cols 1..4 Body)", "meta": "Cols 1..4 Body + Cols 2..3 Navy Photo (7-line underflow) | 58.0pt 2-Line Headline + Subhead"},
            {"col": 5, "span": 1, "y0": 14.5, "h": 12.3, "kind": "gray_box", "title": "सामरिक बिंदु (Col 5)", "meta": "लीड के आखिरी Col 5 में फुल-हाइट 40% Gray Box (100% भरा हुआ)"},
            {"col": 6, "span": 3, "y0": 11.8, "h": 24.0, "kind": "story_photo", "title": "STORY 5: दाएं 3-कॉलम लंबा विशेष फीचर (अंटार्कटिका मैत्री-टू शोध केंद्र + यूरोपीय व्यापार)", "meta": "Cols 6..8 | 24.0 cm | 36.0pt Headline + Cols 7..8 Antarctica Photo + 2 Stacked Stories"},
            {"col": 1, "span": 4, "y0": 27.15, "h": 8.7, "kind": "story", "title": "STORY 6: बाएं 4-Col पूर्वोत्तर 4 नए एयरपोर्ट व राजमार्ग", "meta": "Cols 1..4 | 8.7 cm | 35.0pt Headline"},
            {"col": 5, "span": 1, "y0": 27.15, "h": 8.7, "kind": "story", "title": "STORY 7: ब्रिक्स मुद्रा व्यापार", "meta": "Col 5 | 8.7 cm | 34.0pt Headline"},
            {"col": 1, "span": 4, "y0": 36.2, "h": 7.1, "kind": "story", "title": "STORY 8 & 9: भारत-जापान चिप समझौता व हरित ऊर्जा मॉडल (4-Col)", "meta": "Cols 1..4 | 7.1 cm | 33.0pt Headline"},
            {"col": 5, "span": 4, "y0": 36.2, "h": 7.1, "kind": "story", "title": "STORY 10: प्रवासी भारतीयों के लिए 20 देशों में ई-सेवा केंद्र (4-Col)", "meta": "Cols 5..8 | 7.1 cm | 36.0pt Headline"},
            {"col": 1, "span": 3, "y0": 43.65, "h": 8.35, "kind": "story", "title": "STORY 11: बाएं 3-Col विदेशी विवि में योग व दर्शन पीठ", "meta": "Cols 1..3 | 8.35 cm | 33.0pt Headline"},
            {"col": 4, "span": 5, "y0": 43.65, "h": 8.35, "kind": "anchor", "title": "STORY 12: दाएं 5-कॉलम ग्रैंड स्पेस एंकर (अंतरिक्ष स्टेशन अभियान के लिए नासा और इसरो साथ)", "meta": "Cols 4..8 | 8.35 cm | 42.0pt 1-Line Headline + Subhead + Cols 6..7 ISRO Photo"}
        ]
    }
]


def bring_page_designer_window_to_front():
    """Brings the native Windows Page Designer window to the foreground so the user sees it immediately."""
    try:
        user32 = ctypes.windll.user32
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        found_hwnds = []

        def _enum_cb(hwnd, _lparam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value
                    if "Page Designer" in title or "आदित्य भारत" in title or "Aditya_Bharat" in title:
                        found_hwnds.append(hwnd)
            return True

        user32.EnumWindows(WNDENUMPROC(_enum_cb), 0)
        for hwnd in found_hwnds:
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.SetForegroundWindow(hwnd)
    except Exception:
        pass


def check_page_designer_alive() -> dict:
    for port in (PD_RPC_PORT, 49200):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.6) as _s:
                return {"alive": True, "port": port}
        except Exception:
            pass
    return {"alive": False, "port": PD_RPC_PORT}


def ensure_page_designer_running() -> int:
    st = check_page_designer_alive()
    if st["alive"]:
        return st["port"]
    pd_exe = Path(r"E:\RND\Gujarat_Samachar\Page_Designer_Software\pagedesigner.exe")
    if not pd_exe.exists():
        pd_exe = Path(r"E:\RND\open page layout software\pagedesigner.exe")
    subprocess.Popen([str(pd_exe), "--control", str(PD_RPC_PORT)], cwd=str(pd_exe.parent))
    for _ in range(35):
        time.sleep(0.35)
        st2 = check_page_designer_alive()
        if st2["alive"]:
            return st2["port"]
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
    """
    mode == 'book': Opens the combined 8-page document (Aditya_Bharat_Full_8Pages_34x53.pagedesigner) with Pages 1..8!
    mode == 'tabs': Opens all 8 individual .pagedesigner files as 8 separate tabs simultaneously!
    """
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

    # Mode 'tabs' (or fallback if combined book isn't built yet): open all 8 files as 8 tabs
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
                r_o = _rpc_call(s, f_in, "app.open", {"path": str(p)})
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

                # If building all 8 tabs together, close old tabs once at start, then keep all 8 new tabs open!
                if len(page_ids) > 1 or keep_tabs:
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
                    script_path = VAULT_DIR / item["script"]
                    BUILD_STATUS["current_task"] = f"Page Designer में {item['title_hi']} Draw हो रहा है ({idx_p + 1}/{len(page_ids)})..."
                    BUILD_STATUS["last_updated"] = time.strftime("%H:%M:%S")
                    env = os.environ.copy()
                    if len(page_ids) > 1 or keep_tabs:
                        env["AB_NO_CLOSE"] = "1"
                    t0 = time.perf_counter()
                    proc = subprocess.run(
                        [sys.executable, str(script_path)],
                        cwd=str(VAULT_DIR),
                        env=env,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                    )
                    dt = time.perf_counter() - t0
                    out_txt = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
                    logs.append(f"[{item['title_hi']} — {dt:.1f}s | exit={proc.returncode}]\n{out_txt.strip()}")
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
<title>आदित्य भारत (Aditya Bharat) — 8-Page Master System, Dummy & Page Designer Studio (Port 2424)</title>
<style>
  :root {
    --bg: #0f141c;
    --panel: #171f2c;
    --panel2: #1e293b;
    --border: #2e3c52;
    --crimson: #c4121a;
    --crimson-light: #ff4d55;
    --gold: #f59e0b;
    --emerald: #10b981;
    --blue: #3b82f6;
    --purple: #7c3aed;
    --text: #f1f5f9;
    --muted: #94a3b8;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: 'Segoe UI', 'Nirmala UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
  }
  header {
    background: linear-gradient(90deg, #111827 0%, #1e1b2e 50%, #111827 100%);
    border-bottom: 2px solid var(--crimson);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    position: sticky;
    top: 0;
    z-index: 100;
    flex-wrap: wrap;
    box-shadow: 0 6px 20px rgba(0,0,0,0.45);
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .brand-badge {
    background: var(--crimson);
    color: #fff;
    font-weight: 800;
    font-size: 20px;
    padding: 8px 14px;
    border-radius: 6px;
    letter-spacing: 0.5px;
    box-shadow: 0 2px 10px rgba(196,18,26,0.5);
  }
  .brand-title h1 {
    margin: 0;
    font-size: 19px;
    font-weight: 800;
  }
  .brand-title p {
    margin: 2px 0 0 0;
    font-size: 12px;
    color: var(--muted);
  }
  .header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  .pd-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    background: #1e293b;
    border: 1px solid var(--border);
  }
  .dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: var(--emerald);
    box-shadow: 0 0 8px var(--emerald);
  }
  .dot.off {
    background: var(--gold);
    box-shadow: 0 0 8px var(--gold);
  }
  .btn {
    border: none;
    border-radius: 7px;
    padding: 8px 13px;
    font-size: 12.5px;
    font-weight: 700;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
    text-decoration: none;
    color: #fff;
  }
  .btn:hover { transform: translateY(-1px); filter: brightness(1.08); }
  .btn:disabled { opacity: 0.55; cursor: not-allowed; transform: none; }
  .btn-crimson { background: var(--crimson); }
  .btn-emerald { background: #059669; }
  .btn-blue { background: #2563eb; }
  .btn-purple { background: var(--purple); }
  .btn-dark { background: #334155; border: 1px solid #475569; }
  .btn-gold { background: #d97706; }

  .top-tabs {
    display: flex;
    gap: 8px;
    padding: 10px 20px;
    background: #131b26;
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
  }
  .tab-btn {
    background: #1e293b;
    color: #cbd5e1;
    border: 1px solid var(--border);
    padding: 9px 16px;
    border-radius: 7px;
    font-size: 13.5px;
    font-weight: 700;
    cursor: pointer;
  }
  .tab-btn.active {
    background: var(--crimson);
    color: #fff;
    border-color: var(--crimson-light);
  }

  .status-banner {
    background: #162235;
    border-bottom: 1px solid var(--border);
    padding: 8px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 13px;
  }
  .status-banner .task {
    color: #38bdf8;
    font-weight: 700;
  }

  .workspace {
    display: grid;
    grid-template-columns: 295px 1fr;
    min-height: calc(100vh - 140px);
  }
  .sidebar {
    background: var(--panel);
    border-right: 1px solid var(--border);
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .sidebar h3 {
    margin: 2px 0 4px 0;
    font-size: 12.5px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--muted);
  }
  .page-item {
    background: var(--panel2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 9px 11px;
    cursor: pointer;
    transition: all 0.15s ease;
  }
  .page-item:hover { border-color: #64748b; }
  .page-item.active {
    border-color: var(--crimson-light);
    background: linear-gradient(135deg, rgba(196,18,26,0.22), rgba(30,41,59,0.95));
    box-shadow: inset 3px 0 0 var(--crimson);
  }
  .page-item-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 800;
    font-size: 13.5px;
  }
  .folio-tag {
    background: var(--crimson);
    color: #fff;
    font-size: 11px;
    padding: 2px 7px;
    border-radius: 4px;
  }
  .page-item-sub {
    font-size: 11px;
    color: var(--muted);
    margin-top: 4px;
    line-height: 1.3;
  }
  .page-item-quick {
    display: flex;
    gap: 6px;
    margin-top: 7px;
  }
  .mini-btn {
    flex: 1;
    border: none;
    border-radius: 5px;
    padding: 5px 6px;
    font-size: 11px;
    font-weight: 700;
    color: #fff;
    cursor: pointer;
    text-align: center;
  }

  .main-area {
    padding: 16px 20px;
    overflow-y: auto;
  }
  .page-header-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
  }
  .page-header-info h2 {
    margin: 0 0 4px 0;
    font-size: 19px;
  }
  .page-header-info p {
    margin: 0;
    font-size: 13px;
    color: #cbd5e1;
    max-width: 780px;
  }
  .spec-badges {
    display: flex;
    gap: 8px;
    margin-top: 8px;
    flex-wrap: wrap;
  }
  .spec-badge {
    background: #0f172a;
    border: 1px solid #334155;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    color: #e2e8f0;
  }

  .dual-stage {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
    align-items: start;
  }
  @media (max-width: 1280px) {
    .dual-stage { grid-template-columns: 1fr; }
  }
  .stage-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
  }
  .stage-card-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
  }
  .stage-card-head h3 {
    margin: 0;
    font-size: 15px;
  }

  .dummy-sheet-outer {
    width: 100%;
    max-width: 580px;
    margin: 0 auto;
    aspect-ratio: 34 / 53;
    background: #fcfaf2;
    border: 2px solid #475569;
    border-radius: 4px;
    position: relative;
    box-shadow: 0 10px 28px rgba(0,0,0,0.5);
    padding: 2.94% 2.94%;
  }
  .dummy-print-area {
    width: 100%;
    height: 100%;
    position: relative;
    border: 1px dashed #94a3b8;
    background-image: repeating-linear-gradient(
      to right,
      rgba(148, 163, 184, 0.14) 0%,
      rgba(148, 163, 184, 0.14) 11.328%,
      transparent 11.328%,
      transparent 12.578%
    );
  }
  .col-ruler {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 4px;
    margin-bottom: 6px;
    max-width: 580px;
    margin-left: auto;
    margin-right: auto;
  }
  .col-ruler span {
    background: #1e293b;
    border: 1px solid #334155;
    color: #93c5fd;
    font-size: 11px;
    font-weight: 700;
    text-align: center;
    padding: 3px 0;
    border-radius: 4px;
  }
  .dummy-block {
    position: absolute;
    border-radius: 3px;
    padding: 4px 6px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.12s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 1px 3px rgba(0,0,0,0.18);
  }
  .dummy-block:hover {
    z-index: 20;
    outline: 2.5px solid #dc2626;
    transform: scale(1.008);
  }
  .dummy-block .db-title {
    font-size: 10.5px;
    font-weight: 800;
    line-height: 1.2;
    color: #0f172a;
  }
  .dummy-block .db-meta {
    font-size: 9px;
    font-weight: 600;
    line-height: 1.15;
    color: #334155;
    background: rgba(255,255,255,0.75);
    padding: 1px 4px;
    border-radius: 2px;
  }
  .kind-masthead_front { background: linear-gradient(135deg, #fee2e2, #fecaca); border: 2px solid #dc2626; }
  .kind-masthead_inside { background: #c4121a; border: 1.5px solid #7f1d1d; }
  .kind-masthead_inside .db-title, .kind-masthead_inside .db-meta { color: #ffffff; background: transparent; }
  .kind-flyer { background: linear-gradient(135deg, #fef3c7, #fde68a); border: 1.5px solid #d97706; }
  .kind-lead { background: linear-gradient(135deg, #dbeafe, #bfdbfe); border: 2px solid #1d4ed8; }
  .kind-gray_box { background: #cbd5e1; border: 2px solid #334155; }
  .kind-story_photo { background: linear-gradient(135deg, #d1fae5, #a7f3d0); border: 1.5px solid #059669; }
  .kind-story { background: #ffffff; border: 1.5px solid #64748b; }
  .kind-anchor { background: linear-gradient(135deg, #f3e8ff, #e9d5ff); border: 2px solid #7c3aed; }
  .kind-editorial { background: linear-gradient(135deg, #e0f2fe, #bae6fd); border: 1.5px solid #0284c7; }

  .rendered-preview-wrap { text-align: center; }
  .rendered-preview-wrap img {
    width: 100%;
    max-width: 580px;
    border-radius: 4px;
    border: 2px solid #475569;
    box-shadow: 0 10px 28px rgba(0,0,0,0.5);
    cursor: zoom-in;
  }
  .wall-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 18px;
  }
  .wall-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .sys-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
    font-size: 13.5px;
  }
  .sys-table th, .sys-table td {
    border: 1px solid var(--border);
    padding: 9px 12px;
    text-align: left;
  }
  .sys-table th { background: #1e293b; color: #f8fafc; }
  .sys-table tr:nth-child(even) { background: rgba(30,41,59,0.45); }
  pre.log-box {
    background: #090d14;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px;
    color: #a7f3d0;
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
      <h1>आदित्य भारत — 8-Page Master System, Dummy & Page Designer Studio</h1>
      <p>URL: <b>http://127.0.0.1:2424</b> • <b>1-1 पेज</b> या <b>सभी 8 पेज एक साथ (1 Book या 8 Tabs)</b> Page Designer में तुरंत Open / Draw करें</p>
    </div>
  </div>
  <div class="header-actions">
    <div class="pd-pill">
      <span class="dot" id="pdDot"></span>
      <span id="pdStatusText">Page Designer जाँच रहे हैं...</span>
    </div>
    <button class="btn btn-emerald" onclick="openAllPages('book')" title="एक ही डॉक्यूमेंट में पेज 1 से 8 तक पूरे 8 पेज एक साथ खोलें">📚 सभी 8 पेज (1 संयुक्त फाइल में) खोलें</button>
    <button class="btn btn-blue" onclick="openAllPages('tabs')" title="Page Designer में 8 अलग-अलग टैब्स में सभी 8 पेज एक साथ खोलें">🗂️ सभी 8 पेज (8 अलग Tabs में) खोलें</button>
    <button class="btn btn-purple" onclick="drawAllCombinedBook()" title="एक ही डॉक्यूमेंट के अंदर पेज 1 से 8 तक नए सिरे से Draw करें">🚀 पूरे 8 पेज (1 Book में) खुद Draw करें</button>
    <button class="btn btn-crimson" onclick="buildAllPagesTabs()" title="8 अलग-अलग टैब्स में सभी 8 पेज नए सिरे से Draw करें">🎨 पूरे 8 पेज (8 Tabs में) खुद Draw करें</button>
  </div>
</header>

<div class="top-tabs">
  <button class="tab-btn active" id="tabBtn_studio" onclick="switchTab('studio')">1. 📐 पेज-वार Interactive Dummy + 1-1 Page Designer Controls</button>
  <button class="tab-btn" id="tabBtn_wall" onclick="switchTab('wall')">2. 🗺️ एक साथ सभी 8 पेजों की Dummy & Preview Wall</button>
  <button class="tab-btn" id="tabBtn_system" onclick="switchTab('system')">3. 📏 सिखाया गया पूरा सिस्टम व स्टाइलशीट (Master Rules Vault)</button>
  <button class="tab-btn" id="tabBtn_logs" onclick="switchTab('logs')">4. 🖥️ Live Page Designer RPC & Build Logs</button>
</div>

<div class="status-banner">
  <div>
    <strong>Live इंजन स्टेटस:</strong>
    <span class="task" id="bannerTask">तैयार (Ready)</span>
  </div>
  <div style="color:var(--muted);" id="bannerTime"></div>
</div>

<!-- TAB 1: SINGLE PAGE INTERACTIVE DUMMY + RENDERED PREVIEW + PAGE DESIGNER CONTROLS -->
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
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
          <button class="btn btn-emerald" onclick="openCurrentSavedFile(true)" title="सिर्फ यही 1 पेज Page Designer में खोलें">📂 सिर्फ यही 1 पेज खोलें (1-Page Open)</button>
          <button class="btn btn-blue" onclick="openCurrentSavedFile(false)" title="पहले से खुले पेजों को बंद किए बिना इसे नए टैब में खोलें">➕ नए टैब में यह पेज जोड़ें (Add Tab)</button>
          <button class="btn btn-crimson" onclick="drawCurrentPage(false)" title="सिर्फ यही 1 पेज नए सिरे से Page Designer में Draw करें">🎨 सिर्फ यही 1 पेज खुद Draw करें</button>
          <button class="btn btn-purple" onclick="drawCurrentPage(true)" title="पहले से खुले टैब्स को बंद किए बिना यह पेज नए टैब में Draw करें">➕ नए टैब में Draw करें</button>
          <a class="btn btn-gold" id="linkDownloadPdf" href="#" target="_blank">📄 CMYK PDF</a>
          <a class="btn btn-dark" id="linkDownloadPd" href="#" download>💾 .pagedesigner</a>
        </div>
      </div>

      <div class="dual-stage">
        <div class="stage-card">
          <div class="stage-card-head">
            <h3>📐 8-Column Structural Dummy Blueprint (32 × 51 cm Print Area)</h3>
            <span style="font-size:12px; color:var(--muted);">किसी भी ब्लॉक पर क्लिक करें</span>
          </div>
          <div class="col-ruler">
            <span>Col 1</span><span>Col 2</span><span>Col 3</span><span>Col 4</span>
            <span>Col 5</span><span>Col 6</span><span>Col 7</span><span>Col 8</span>
          </div>
          <div class="dummy-sheet-outer">
            <div class="dummy-print-area" id="dummyCanvas"></div>
          </div>
          <div id="dummyInspector" style="margin-top:12px; padding:10px 12px; background:#0f172a; border:1px solid #334155; border-radius:8px; font-size:13px;">
            👆 ऊपर डमी के किसी भी ज़ोन/स्टोरी बॉक्स पर क्लिक करके उसका सटीक कॉलम गणित और फॉन्ट साइज देखें।
          </div>
        </div>

        <div class="stage-card">
          <div class="stage-card-head">
            <h3>📰 Page Designer द्वारा तैयार वास्तविक पेज (Live Rendered Page)</h3>
            <a id="linkFullPng" href="#" target="_blank" style="color:#38bdf8; font-size:12.5px; text-decoration:none; font-weight:700;">🔍 फुल साइज (300 DPI) खोलें ↗</a>
          </div>
          <div class="rendered-preview-wrap">
            <img id="curPageImg" src="" alt="Rendered Page Preview" onclick="window.open(this.src, '_blank')">
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- TAB 2: ALL 8 PAGES DUMMY & PREVIEW WALL -->
<div id="tab_wall" style="display:none; padding:20px;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:10px;">
    <div>
      <h2 style="margin:0;">🗺️ आदित्य भारत — सभी 8 पेजों की Structural Dummy + Live Preview Wall</h2>
      <p style="margin:4px 0 0 0; color:var(--muted); font-size:13.5px;">यहाँ से 1-1 पेज या एक साथ सभी 8 पेज Page Designer में खोलें या Draw करें।</p>
    </div>
    <div style="display:flex; gap:8px; flex-wrap:wrap;">
      <button class="btn btn-dark" onclick="toggleWallMode('dummy')">📐 सभी की Structural Dummy दिखाएं</button>
      <button class="btn btn-blue" onclick="toggleWallMode('png')">📰 सभी के Rendered Pages दिखाएं</button>
      <button class="btn btn-emerald" onclick="openAllPages('book')">📚 सभी 8 पेज (1 Book में) खोलें</button>
      <button class="btn btn-purple" onclick="openAllPages('tabs')">🗂️ सभी 8 पेज (8 Tabs में) खोलें</button>
    </div>
  </div>
  <div class="wall-grid" id="wallGrid"></div>
</div>

<!-- TAB 3: COMPLETE LEARNED SYSTEM & STYLESHEET VAULT -->
<div id="tab_system" style="display:none; padding:22px; max-width:1320px; margin:0 auto;">
  <div class="stage-card" style="margin-bottom:18px;">
    <h2 style="margin-top:0;">📏 आदित्य भारत (Aditya Bharat) — सिखाया गया पूरा 8-पेज मास्टर सिस्टम (Locked DNA)</h2>
    <p style="color:#cbd5e1; font-size:14px;">यह पूरा सिस्टम स्थायी रूप से <code>aditya_bharat_stylesheet_system.json</code> और <code>ADITYA_BHARAT_STYLESHEET_VAULT.md</code> में लॉक है और हर पेज बिल्डर इसी गणित से Page Designer में पेज Draw करता है:</p>

    <h3>1. पेज आकार, फिक्स प्रिंट एरिया और 8-कॉलम ग्रिड (Page & Grid Geometry)</h3>
    <table class="sys-table">
      <tr><th>पैरामीटर</th><th>लॉक्ड मान (Specification)</th><th>Points (@ 72 DPI)</th><th>अनिवार्य नियम</th></tr>
      <tr><td><b>प्रिंट एरिया (Fixed Print Area)</b></td><td><b>32.0 cm × 51.0 cm</b></td><td>907.09 pt × 1445.67 pt</td><td>100% FIXED (x = 1..33 cm, y = 1..52 cm)</td></tr>
      <tr><td><b>बाहरी मार्जिन (Outer Margins)</b></td><td><b>1.0 cm चारों तरफ</b> (Top, Bottom, Left, Right)</td><td>28.35 pt चारों तरफ</td><td>खुला और प्रीमियम ब्रॉडशीट बॉर्डर</td></tr>
      <tr><td><b>कुल बाहरी पेज साइज (Total Canvas)</b></td><td><b>34.0 cm × 53.0 cm</b></td><td>963.78 pt × 1502.36 pt</td><td>32 + 2 = 34 cm चौड़ाई, 51 + 2 = 53 cm ऊंचाई</td></tr>
      <tr><td><b>कॉलम व गटर (Columns & Gutter)</b></td><td><b>8 Columns</b> (प्रत्येक 3.625 cm) + <b>4.0 mm Gutter</b></td><td>Col = 102.76 pt, Gutter = 11.34 pt</td><td>Zero Vertical Column Rules (खड़ी रूल पूर्णतः बंद)</td></tr>
      <tr><td><b>बेसलाइन ग्रिड (Baseline Grid)</b></td><td><b>11.25 pt</b> (Start @ 1.0 cm)</td><td>11.25 pt</td><td>बॉडी टेक्स्ट <code>allLines</code> सख्ती से बेसलाइन पर लॉक</td></tr>
    </table>

    <h3 style="margin-top:20px;">2. कोर टाइपोग्राफी, फॉन्ट और रंग नियम (Typography & Color System)</h3>
    <table class="sys-table">
      <tr><th>एलिमेंट</th><th>फॉन्ट फैमिली</th><th>पॉइंट साइज व लीडिंग</th><th>रंग व विशेष नियम</th></tr>
      <tr><td><b>मुख्य स्टोरी हेडलाइन</b></td><td><code>DB Rasrand Bold</code> (DB RASRANG BOLD)</td><td><b>Minimum 30.0 pt</b> (30pt – 74pt), Leading = <code>pt + 1.0 pt</code></td><td><b>100% K Black</b> (लाल हेडलाइन कहीं भी नहीं लगेगी!)</td></tr>
      <tr><td><b>बॉडी टेक्स्ट (Body Copy)</b></td><td><code>DB Hindi</code> (Regular)</td><td><b>11.0 pt / 11.25 pt</b></td><td>100% K Black, Justified, Baseline Locked</td></tr>
      <tr><td><b>सबहेड / किकर (Subhead)</b></td><td><code>DB Hindi</code> (Bold)</td><td>फ्लायर में <b>18.0 pt</b>, लीड/एंकर में 13–16 pt</td><td>100% K Black (ऊपर या नीचे)</td></tr>
      <tr><td><b>3-टोन बाइलाइन (Byline)</b></td><td><code>DB Hindi</code> (Bold)</td><td>11.0 pt / 11.25 pt</td><td><code>[शहर (Black)] | (Red) [एजेंसी (Gray)]</code> + नीचे 0.85pt Gray Rule</td></tr>
      <tr><td><b>रेड सब्जेक्ट ब्लर्ब (1-Word Blurb)</b></td><td><code>DB Hindi 6</code> (Bold)</td><td><b>22.0 pt</b></td><td>Red Box (<code>#c4121a</code>) में White Text + नीचे 3.0pt Gray Rule</td></tr>
      <tr><td><b>लीड फुल-हाइट 40% Gray बॉक्स</b></td><td><code>DB Rasrand Bold</code> (Head) + <code>DB Hindi Bold</code></td><td>Head: 16–18 pt, Body: 10.5/11.3 pt</td><td><b>हमेशा लीड के आखिरी कॉलम (Last Col) में</b>, 2.5mm चारों तरफ इनसेट, 100% भरा हुआ</td></tr>
      <tr><td><b>फोटो कैप्शन (Photo Caption)</b></td><td><code>DB Hindi 7</code></td><td><b>10.0 pt / 10.2 pt</b></td><td>100% K Black, कॉम्पैक्ट फोटो के ठीक नीचे + साफ अंडरफ्लो</td></tr>
    </table>
  </div>
</div>

<!-- TAB 4: LIVE PAGE DESIGNER RPC & BUILD LOGS -->
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

async function initApp() {
  const res = await fetch('/api/catalog');
  const data = await res.json();
  CATALOG = data.pages;
  renderSidebar();
  selectPage(0);
  renderWall();
  pollStatus();
  setInterval(pollStatus, 1800);
}

function switchTab(tabName) {
  ['studio', 'wall', 'system', 'logs'].forEach(t => {
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

function buildDummyHtml(p) {
  const colW = 3.625;
  const gutW = 0.40;
  return p.dummy_blocks.map((b) => {
    const xCm = (b.col - 1) * (colW + gutW);
    const wCm = b.span * colW + (b.span - 1) * gutW;
    const yCm = b.y0 - 1.0;
    const leftPct = (xCm / 32.0) * 100.0;
    const widthPct = (wCm / 32.0) * 100.0;
    const topPct = (yCm / 51.0) * 100.0;
    const heightPct = (b.h / 51.0) * 100.0;
    const safeTitle = b.title.replace(/"/g, '&quot;');
    const safeMeta = b.meta.replace(/"/g, '&quot;');
    return `
      <div class="dummy-block kind-${b.kind}"
           style="left:${leftPct.toFixed(2)}%; width:${widthPct.toFixed(2)}%; top:${topPct.toFixed(2)}%; height:${heightPct.toFixed(2)}%;"
           onclick="inspectDummyBlock('${safeTitle}', '${safeMeta}', ${b.col}, ${b.span}, ${b.y0}, ${b.h})">
        <div class="db-title">${b.title}</div>
        <div class="db-meta">${b.meta}</div>
      </div>
    `;
  }).join('');
}

function inspectDummyBlock(title, meta, col, span, y0, h) {
  const endCol = col + span - 1;
  document.getElementById('dummyInspector').innerHTML = `
    <div style="font-weight:800; color:#38bdf8; margin-bottom:4px;">📌 ${title}</div>
    <div><b>कॉलम विस्तार:</b> Col ${col} से Col ${endCol} (${span} Columns) • <b>Y-स्थिति:</b> ${y0.toFixed(2)} cm से ${(y0 + h).toFixed(2)} cm (ऊंचाई: <b>${h.toFixed(2)} cm</b>)</div>
    <div style="color:#cbd5e1; margin-top:3px;"><b>नियम व विवरण:</b> ${meta}</div>
  `;
}

function selectPage(idx) {
  CURRENT_INDEX = idx;
  renderSidebar();
  const p = CATALOG[idx];
  document.getElementById('curPageTitle').textContent = p.title_hi;
  document.getElementById('curPageSummary').textContent = p.summary_hi;
  document.getElementById('curPageBadges').innerHTML = `
    <span class="spec-badge">📰 सेक्शन: <b>${p.section_hi}</b></span>
    <span class="spec-badge">🔢 कुल खबरें: <b>${p.stories_count}</b></span>
    <span class="spec-badge">🔠 हेडलाइन रेंज: <b>${p.min_head_pt} – ${p.max_head_pt} (DB Rasrand Bold)</b></span>
    <span class="spec-badge">🚫 खड़ी रूल: <b>0 (Zero Vertical Rules)</b></span>
    <span class="spec-badge">🐍 स्क्रिप्ट: <code>${p.script}</code></span>
  `;
  document.getElementById('dummyCanvas').innerHTML = buildDummyHtml(p);
  const ts = Date.now();
  const pngUrl = '/vault/' + encodeURIComponent(p.png_file) + '?t=' + ts;
  document.getElementById('curPageImg').src = pngUrl;
  document.getElementById('linkFullPng').href = pngUrl;
  document.getElementById('linkDownloadPdf').href = '/vault/' + encodeURIComponent(p.pdf_file) + '?t=' + ts;
  document.getElementById('linkDownloadPd').href = '/vault/' + encodeURIComponent(p.pd_file);
}

function renderWall() {
  const grid = document.getElementById('wallGrid');
  const ts = Date.now();
  grid.innerHTML = CATALOG.map((p, idx) => {
    const bodyContent = (WALL_MODE === 'dummy')
      ? `<div class="dummy-sheet-outer" style="max-width:100%;"><div class="dummy-print-area">${buildDummyHtml(p)}</div></div>`
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

function toggleWallMode(mode) {
  WALL_MODE = mode;
  renderWall();
}

async function drawCurrentPage(keepTabs) {
  const p = CATALOG[CURRENT_INDEX];
  await drawSinglePage(p.id, keepTabs);
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
  const res = await fetch('/api/draw', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({pages: allIds, keep_tabs: false, combined_book: false})
  });
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Error starting build');
  pollStatus();
}

async function drawAllCombinedBook() {
  const res = await fetch('/api/draw', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({pages: [], keep_tabs: false, combined_book: true})
  });
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Error starting combined build');
  pollStatus();
}

async function openCurrentSavedFile(closeOthers) {
  const p = CATALOG[CURRENT_INDEX];
  await openSavedFile(p.pd_file, closeOthers);
}

async function openSavedFile(pdFile, closeOthers) {
  const res = await fetch('/api/open_pd', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({pd_file: pdFile, close_others: !!closeOthers})
  });
  const data = await res.json();
  if (!data.ok) alert('त्रुटि: ' + (data.error || 'Failed'));
  pollStatus();
}

async function openAllPages(mode) {
  const res = await fetch('/api/open_all_pd', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({mode: mode})
  });
  const data = await res.json();
  if (!data.ok) alert('त्रुटि: ' + (data.error || 'Failed'));
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
      bannerTask.style.color = '#fbbf24';
    } else {
      bannerTask.textContent = '✅ तैयार — आप 1-1 पेज या सभी 8 पेज (1 Book या 8 Tabs) में तुरंत Open/Draw कर सकते हैं';
      bannerTask.style.color = '#34d399';
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

        if path == "/api/status":
            self._send_json({
                "ok": True,
                "pd": check_page_designer_alive(),
                "build": BUILD_STATUS,
            })
            return

        if path.startswith("/vault/"):
            rel_name = urllib.parse.unquote(path[len("/vault/"):])
            safe_path = (VAULT_DIR / rel_name).resolve()
            if not str(safe_path).startswith(str(VAULT_DIR.resolve())) or not safe_path.is_file():
                self.send_error(404, "File not found")
                return
            ext = safe_path.suffix.lower()
            ctype = "application/octet-stream"
            if ext == ".png":
                ctype = "image/png"
            elif ext == ".pdf":
                ctype = "application/pdf"
            elif ext == ".json":
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

        if path == "/api/open_pd":
            pd_file = payload.get("pd_file", "")
            close_others = bool(payload.get("close_others", True))
            try:
                res = open_saved_file_in_page_designer(pd_file, close_others=close_others)
                mode_str = "1-Page Exclusive Open" if close_others else "Added as New Tab"
                BUILD_STATUS["last_log"] = f"[{mode_str}] {pd_file} -> Page Designer में खुल गया है!"
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


def main():
    server = ThreadingHTTPServer(("0.0.0.0", STUDIO_PORT), AdityaBharatStudioHandler)
    print(f"======================================================================")
    print(f" ADITYA BHARAT 8-PAGE STUDIO RUNNING ON: http://127.0.0.1:{STUDIO_PORT}")
    print(f" Alternate Link                        : http://localhost:{STUDIO_PORT}")
    print(f" Vault Directory                       : {VAULT_DIR}")
    print(f"======================================================================", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
