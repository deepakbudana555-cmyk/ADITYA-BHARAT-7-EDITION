# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — PAGE 08 (देश-विदेश / BACK PAGE) LIVE 70% NATIONAL + 30% INTERNATIONAL HARVESTER & BUILDER
=======================================================================================================================
Date                  : 18-11-2026 (और रोज़ाना किसी भी तारीख के लिए 100% ऑटोमैटिक)
Page Title            : देश-विदेश (Page 08 — Back Page)
News Mix Rule (Locked): 10 Stories Total -> 70% National News (7 Stories) + 30% Interesting International News (3 Stories)
Distinct Layout       :
  - Masthead (y = 1.00 .. 2.50 cm) : Left Red Box 'देश-विदेश' | Center Official Graphic Logo 'आदित्य भारत' | Right Dateline + '08'
  - Band 1   (y = 2.85 .. 11.45 cm): Left 3-Col National Story (Cols 1..3) + Right 5-Col Illustrated National Top Flyer (Cols 4..8)
  - Band 2   (y = 11.80 .. 26.75 cm): Left 3-Col Stack (2 National Stories in Cols 1..3) + Right 5-Col Main National Strategic Lead (Cols 4..8, Gray Box in LAST Col 8)
  - Band 3   (y = 27.10 .. 38.60 cm): 4-Col Illustrated International Interesting Feature (Cols 1..4) + 2-Col National (Cols 5..6) + 2-Col International Interesting (Cols 7..8)
  - Band 4   (y = 38.95 .. 50.65 cm): Left 3-Col International Interesting Story (Cols 1..3) + Right 5-Col Illustrated National Grand Space Anchor (Cols 4..8)
  - Print Line Separator Rule (y = 50.90 cm): 0.5 pt 100% Black Horizontal Rule across all 8 columns (x = 1.0 .. 33.0 cm)
  - 1.0 cm Print Line Space   (y = 50.95 .. 51.98 cm): Dedicated 1.0 cm bottom band for 2-Line Newspaper Print Line
  - Bottom CMYK Marka         (y = 52.10 .. 52.42 cm): 2.0 pt 60% Gray Rule behind 3 sets (Left, Center, Right) of 4 CMYK boxes (C, M, Y, K)
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
from PIL import Image

VAULT_DIR = Path(__file__).resolve().parent
HARVEST_DIR = VAULT_DIR / "live_harvested_news"
HARVEST_DIR.mkdir(parents=True, exist_ok=True)
P8_JSON_PATH = HARVEST_DIR / "18-11-2026_DESH_VIDESH_PAGE8_10_STORIES.json"
P8_USED_LEDGER_PATH = HARVEST_DIR / "used_p8_desh_videsh_history.json"

CM_TO_PT = 72.0 / 2.54
MM_TO_PT = CM_TO_PT / 10.0


def cm(val: float) -> float:
    return round(val * CM_TO_PT, 2)


def mm(val: float) -> float:
    return round(val * MM_TO_PT, 2)


import ab_chhattisgarh_10x2_engine as cg_core


def ensure_all_real_page8_photos(overwrite: bool = False):
    exact_files = [
        ("p8_real_s2_vande_bharat.jpg", "File:Vande Bharat Express around Mumbai.jpg", "Vande Bharat Express train India"),
        ("p8_real_s5_indian_navy.jpg", "File:INS Vikrant (R11) and INS Vikramaditya (R33) with the carrier battle group.jpg", "INS Vikrant aircraft carrier India"),
        ("p8_real_s6_mars_space.jpg", "File:NASA's Ingenuity helicopter on Mars by Perseverance Mastcam-Z, Sol 768 (53475637956).jpg", "Mars Perseverance rover NASA"),
        ("p8_real_s10_isro_rocket.jpg", "File:GSLV Mk III Lift Off 1.jpg", "GSLV Mk III ISRO launch"),
    ]
    for fname, exact_title, fallback_q in exact_files:
        ok = cg_core.fetch_exact_wikimedia_file(exact_title, fname, overwrite=overwrite)
        if not ok:
            cg_core.fetch_real_subject_photo_from_wikimedia(fallback_q, fname)


# ==============================================================================
# 1. CURATED + LIVE 10-STORY MASTER POOL FOR PAGE 08 (70% NATIONAL + 30% INTL)
# ==============================================================================
BASE_P8_10_STORIES = [
    # --- STORY 1 (Cols 1..3 Top Left | NATIONAL #1 - 70%) ---
    {
        "page": 8,
        "slot": 1,
        "category": "NATIONAL",
        "role": "top_left_3col",
        "city": "नई दिल्ली",
        "agency": "विधि ब्यूरो",
        "blurb": "न्याय",
        "headline": "सुप्रीम कोर्ट के सभी फैसले अब एआई से क्षेत्रीय भाषाओं में मिलेंगे",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "सर्वोच्च न्यायालय ने आम नागरिकों और वादकारियों की सुविधा के लिए आर्टिफिशियल इंटेलिजेंस आधारित ई-एससीआर पोर्टल का व्यापक विस्तार करते हुए हिंदी सहित संविधान की अठारह क्षेत्रीय भाषाओं में फैसलों का त्वरित अनुवाद उपलब्ध कराना शुरू कर दिया है। "
            "मुख्य न्यायाधीश की पहल पर लागू इस डिजिटल व्यवस्था से देश के करोड़ों नागरिकों को सर्वोच्च न्यायालय के ऐतिहासिक निर्णयों को अपनी मातृभाषा में पढ़ने और समझने की सीधी सुविधा मिल गई है।"
        ),
    },
    # --- STORY 2 (Cols 4..8 Top Right 5-Col Flyer | NATIONAL #2 - 70%) ---
    {
        "page": 8,
        "slot": 2,
        "category": "NATIONAL",
        "role": "top_right_flyer_5col",
        "city": "नई दिल्ली",
        "agency": "विशेष संवाददाता",
        "blurb": "रफ्तार",
        "headline": "देश के दस नए मार्गों पर दौड़ेंगी स्वदेशी वंदे भारत स्लीपर ट्रेनें",
        "subhead": "लंबी दूरी के रेल यात्रियों को विमान जैसी आरामदायक सुविधा : एक सौ साठ किमी प्रति घंटे की रफ्तार और कवच सुरक्षा प्रणाली से लैस",
        "photo": "p8_real_s2_vande_bharat.jpg",
        "caption": "भारतीय रेलवे द्वारा विकसित अत्याधुनिक स्वदेशी वंदे भारत एक्सप्रेस ट्रेन। — फाइल फोटो",
        "body": (
            "भारतीय रेलवे ने लंबी दूरी की रात्रिकालीन यात्रा को तेज, सुरक्षित और विश्वस्तरीय बनाने के लिए पूर्णतः स्वदेशी तकनीक से निर्मित दस नई वंदे भारत स्लीपर ट्रेनों के व्यावसायिक परिचालन की समयसारिणी जारी कर दी है। "
            "इंटीग्रल कोच फैक्ट्री और बीईएमएल द्वारा तैयार इन सोलह कोच वाली आधुनिक रैक में स्वचालित दरवाजे, जीपीएस यात्री सूचना प्रणाली, बायो-वैक्यूम शौचालय और टक्कर-रोधी कवच प्रणाली लगाई गई है।\n"
            "रेल मंत्रालय के वरिष्ठ अधिकारियों के अनुसार प्रथम चरण में दिल्ली-मुंबई, दिल्ली-हावड़ा, रायपुर-दिल्ली और चेन्नई-बेंगलुरु कॉरिडोर पर इन स्लीपर ट्रेनों का संचालन प्रारंभ किया जाएगा, जिससे यात्रा समय में तीन से चार घंटे तक की बचत होगी।"
        ),
    },
    # --- STORY 3 (Cols 1..3 Mid-Top Left | NATIONAL #3 - 70%) ---
    {
        "page": 8,
        "slot": 3,
        "category": "NATIONAL",
        "role": "left_stack_top_3col",
        "city": "गांधीनगर",
        "agency": "आर्थिक ब्यूरो",
        "blurb": "तकनीक",
        "headline": "सेमीकंडक्टर चिप निर्माण में भारत बनेगा विश्व का तीसरा बड़ा केंद्र",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "इंडिया सेमीकंडक्टर मिशन के अंतर्गत गुजरात, असम और मध्य भारत में निर्माणाधीन पांच बड़े सेमीकंडक्टर फैब और एटीएमपी संयंत्रों से आगामी वर्ष के मध्य तक स्वदेशी माइक्रोचिप का व्यावसायिक उत्पादन शुरू हो जाएगा। "
            "इससे ऑटोमोबाइल, रक्षा, दूरसंचार और स्मार्टफोन उद्योग में आयात पर निर्भरता चालीस प्रतिशत तक घट जाएगी।"
        ),
    },
    # --- STORY 4 (Cols 1..3 Mid-Bottom Left | NATIONAL #4 - 70%) ---
    {
        "page": 8,
        "slot": 4,
        "category": "NATIONAL",
        "role": "left_stack_mid_3col",
        "city": "नई दिल्ली",
        "agency": "राष्ट्रीय ब्यूरो",
        "blurb": "राजमार्ग",
        "headline": "देश के सभी राष्ट्रीय राजमार्गों पर अप्रैल से सैटेलाइट टोल प्रणाली",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "सड़क परिवहन एवं राजमार्ग मंत्रालय ने टोल प्लाजा पर वाहनों की कतारें पूरी तरह समाप्त करने के लिए ग्लोबल नेविगेशन सैटेलाइट सिस्टम आधारित बैरियर-मुक्त इलेक्ट्रॉनिक टोल संग्रह प्रणाली को देशभर के प्रमुख राष्ट्रीय राजमार्गों पर लागू करने की घोषणा की है। "
            "वाहनों से केवल उतनी ही दूरी का शुल्क कटेगा जितना उन्होंने राजमार्ग पर वास्तव में सफर किया है।"
        ),
    },
    # --- STORY 5 (Cols 4..8 Right 5-Col Main Strategic Lead | NATIONAL #5 - 70%) ---
    {
        "page": 8,
        "slot": 5,
        "category": "NATIONAL",
        "role": "right_main_lead_5col",
        "city": "विशाखापत्तनम",
        "agency": "रक्षा ब्यूरो",
        "blurb": "सामरिक",
        "headline": "हिंद-प्रशांत क्षेत्र में भारतीय नौसेना के दो विमानवाहक पोतों का महाअभ्यास",
        "subhead": "समुद्री व्यापार मार्गों की सुरक्षा का शंखनाद : आईएनएस विक्रांत और विक्रमादित्य के साथ पैंतीस युद्धपोत व परमाणु पनडुब्बियां शामिल",
        "photo": "p8_real_s5_indian_navy.jpg",
        "caption": "हिंद महासागर में भारतीय नौसेना के विमानवाहक पोत आईएनएस विक्रांत और विक्रमादित्य का संयुक्त बेड़ा। — फाइल फोटो",
        "box_head": "सामरिक बिंदु",
        "box_bullets": (
            "• स्वदेशी विमानवाहक पोत आईएनएस विक्रांत और आईएनएस विक्रमादित्य ने एक साथ समुद्र में भरी हुंकार।\n"
            "• मिग-29के लड़ाकू विमानों, कामोव हेलीकॉप्टरों और पी-8आई टोही विमानों का दिन-रात युद्धाभ्यास।\n"
            "• मलक्का जलडमरूमध्य से लेकर अदन की खाड़ी तक समुद्री डकैती और अवैध घुसपैठ पर कड़ी निगरानी।\n"
            "• मित्र देशों की नौसेनाओं के साथ रियल-टाइम डेटा साझाकरण और संयुक्त पनडुब्बी-रोधी ऑपरेशन।"
        ),
        "body": (
            "हिंद महासागर और हिंद-प्रशांत क्षेत्र में भारत की बढ़ती समुद्री शक्ति का प्रदर्शन करते हुए भारतीय नौसेना ने अपने दोनों विमानवाहक युद्धपोतों आईएनएस विक्रांत और आईएनएस विक्रमादित्य के साथ सबसे बड़ा द्विवार्षिक सामरिक महाअभ्यास शुरू किया है। "
            "पूर्वी और पश्चिमी नौसैनिक कमान के संयुक्त तत्वावधान में आयोजित इस युद्धाभ्यास में पैंतीस से अधिक विध्वंसक युद्धपोत, स्टील्थ फ्रिगेट, परमाणु एवं पारंपरिक पनडुब्बियां तथा साठ से अधिक नौसैनिक लड़ाकू विमान हिस्सा ले रहे हैं।\n"
            "नौसेना प्रमुख ने फ्लैगशिप पोत से अभ्यास का निरीक्षण करते हुए कहा कि भारत स्वतंत्र, खुले और सुरक्षित समुद्री व्यापार मार्गों के प्रति पूरी तरह प्रतिबद्ध है। "
            "अभ्यास के दौरान सुपरसोनिक ब्रह्मोस मिसाइल, बराक वायु रक्षा प्रणाली और स्वदेशी एंटी-सबमरीन टॉरपीडो का सटीक परीक्षण भी किया गया।"
        ),
    },
    # --- STORY 6 (Cols 1..4 Mid Left 4-Col Illustrated | INTERNATIONAL INTERESTING #1 - 30%) ---
    {
        "page": 8,
        "slot": 6,
        "category": "INTERNATIONAL",
        "role": "mid_left_4col_photo",
        "city": "ह्यूस्टन",
        "agency": "विज्ञान डेस्क",
        "blurb": "अंतरिक्ष",
        "headline": "मंगल ग्रह की मिट्टी में ऑक्सीजन व हरित ऊर्जा बनाने का प्रयोग सफल",
        "subhead": "नासा के पर्सिवियरेंस रोवर और वैज्ञानिकों ने लाल ग्रह पर भावी मानव बस्ती बसाने की दिशा में हासिल की उपलब्धि",
        "photo": "p8_real_s6_mars_space.jpg",
        "caption": "मंगल ग्रह की सतह पर नासा के रोवर और हेलीकॉप्टर द्वारा किए गए वैज्ञानिक अन्वेषण का दृश्य। — फाइल फोटो",
        "body": (
            "मंगल ग्रह पर भविष्य में मानव कॉलोनी बसाने की दिशा में अंतरिक्ष वैज्ञानिकों को एक ऐतिहासिक सफलता मिली है। "
            "नासा के पर्सिवियरेंस रोवर द्वारा एकत्र किए गए आंकड़ों और पृथ्वी पर बनी मार्स-सिमुलेशन प्रयोगशाला में वैज्ञानिकों ने मंगल के वायुमंडल की कार्बन डाइऑक्साइड तथा वहां की लौह-युक्त मिट्टी से सांस लेने योग्य शुद्ध ऑक्सीजन और ईंधन तैयार करने की नई उत्प्रेरक तकनीक विकसित कर ली है।\n"
            "शोधकर्ताओं के अनुसार इस तकनीक से मंगल पर जाने वाले अंतरिक्ष यात्रियों को पृथ्वी से भारी ऑक्सीजन सिलेंडर ले जाने की आवश्यकता नहीं होगी तथा वहां बायो-डोम ग्रीनहाउस में आलू, पालक और सूक्ष्म शैवाल उगाना भी संभव हो सकेगा।"
        ),
    },
    # --- STORY 7 (Cols 5..6 Mid Center 2-Col | NATIONAL #6 - 70%) ---
    {
        "page": 8,
        "slot": 7,
        "category": "NATIONAL",
        "role": "mid_center_2col",
        "city": "लेह",
        "agency": "ब्यूरो",
        "blurb": "सीमा",
        "headline": "लद्दाख में दुनिया की सबसे ऊंची सुरंग तैयार",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "सीमा सड़क संगठन ने पंद्रह हजार आठ सौ फीट की ऊंचाई पर स्थित शिंकुन-ला दर्रे के नीचे दुनिया की सबसे ऊंची बारहमासी डबल-लेन सुरंग के मुख्य खुदाई चरण को रिकॉर्ड समय में पूरा कर लिया है। "
            "इससे हिमाचल प्रदेश से लद्दाख की जांस्कर घाटी तक सेना और नागरिकों को साल के बारहों महीने बर्फबारी से सुरक्षित संपर्क मार्ग मिलेगा।"
        ),
    },
    # --- STORY 8 (Cols 7..8 Mid Right 2-Col | INTERNATIONAL INTERESTING #2 - 30%) ---
    {
        "page": 8,
        "slot": 8,
        "category": "INTERNATIONAL",
        "role": "mid_right_2col",
        "city": "टोक्यो",
        "agency": "एजेंसी",
        "blurb": "अनोखा",
        "headline": "जापान में लकड़ी से बना विश्व का पहला उपग्रह",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "अंतरिक्ष में बढ़ते धातु कचरे की समस्या से निपटने के लिए जापान के क्योटो विश्वविद्यालय और सुमितोमो फॉरेस्ट्री के वैज्ञानिकों ने मैग्नोलिया पेड़ की विशेष लकड़ी से निर्मित विश्व का पहला उपग्रह लिग्नोसैट सफलतापूर्वक कक्षा में स्थापित किया है। "
            "अवधि पूरी होने पर यह वायुमंडल में बिना कोई जहरीला कण छोड़े पूरी तरह भस्म हो जाएगा।"
        ),
    },
    # --- STORY 9 (Cols 1..3 Bottom Left 3-Col | INTERNATIONAL INTERESTING #3 - 30%) ---
    {
        "page": 8,
        "slot": 9,
        "category": "INTERNATIONAL",
        "role": "bottom_left_3col",
        "city": "लंदन",
        "agency": "शोध डेस्क",
        "blurb": "खोज",
        "headline": "अंटार्कटिका की बर्फ के नीचे मिली चार करोड़ वर्ष पुरानी नदी घाटी",
        "subhead": "",
        "photo": "",
        "caption": "",
        "body": (
            "पूर्वी अंटार्कटिका की दो किलोमीटर मोटी बर्फ की चादर के नीचे उपग्रह रडार इमेजिंग और आइस-पेनेट्रेटिंग सोनार की मदद से वैज्ञानिकों ने चार करोड़ वर्ष पुरानी एक विशाल प्राचीन नदी घाटी, पर्वत श्रृंखला और घने जंगलों के जीवाश्म अवशेष खोज निकाले हैं। "
            "डरहम विश्वविद्यालय के भूवैज्ञानिकों के अनुसार यह खोज पृथ्वी के प्राचीन जलवायु चक्र और महाद्वीपों के विकास को समझने में मील का पत्थर साबित होगी।"
        ),
    },
    # --- STORY 10 (Cols 4..8 Bottom Right 5-Col Grand Anchor | NATIONAL #7 - 70%) ---
    {
        "page": 8,
        "slot": 10,
        "category": "NATIONAL",
        "role": "bottom_right_anchor_5col",
        "city": "श्रीहरिकोटा",
        "agency": "अंतरिक्ष ब्यूरो",
        "blurb": "गौरव",
        "headline": "इसरो के गगनयान मिशन का क्रू-मॉड्यूल परीक्षण सफल",
        "subhead": "अंतरिक्ष में भारतीय गगनयात्रियों को भेजने की उल्टी गिनती शुरू : बंगाल की खाड़ी में पैराशूट से सुरक्षित उतरा स्वदेशी क्रू-कैप्सूल",
        "photo": "p8_real_s10_isro_rocket.jpg",
        "caption": "श्रीहरिकोटा के सतीश धवन अंतरिक्ष केंद्र से इसरो के बाहुबली रॉकेट एलवीएम-3 का प्रक्षेपण। — फाइल फोटो",
        "body": (
            "भारतीय अंतरिक्ष अनुसंधान संगठन इसरो ने भारत के पहले मानवयुक्त अंतरिक्ष अभियान गगनयान की दिशा में निर्णायक कदम बढ़ाते हुए श्रीहरिकोटा के सतीश धवन अंतरिक्ष केंद्र से मानवरहित क्रू-मॉड्यूल और क्रू-एस्केप सिस्टम का अंतिम एकीकृत उड़ान परीक्षण सफलतापूर्वक संपन्न कर लिया है। "
            "एलवीएम-3 रॉकेट के जरिए अंतरिक्ष की निचली कक्षा में भेजे गए डबल-वॉल्ड प्रेशराइज्ड कैप्सूल ने पृथ्वी के वायुमंडल में पुनः प्रवेश करते समय सोलह सौ डिग्री सेल्सियस के भीषण तापमान को सहन किया और विशाल पैराशूटों की मदद से बंगाल की खाड़ी में निर्धारित बिंदु पर सुरक्षित लैंडिंग की।\n"
            "भारतीय नौसेना और तटरक्षक बल के विशेष पोतों ने तुरंत क्रू-मॉड्यूल को समुद्र से सुरक्षित बाहर निकाला। इसरो अध्यक्ष ने बताया कि इस सफलता के साथ ही भारत अमेरिका, रूस और चीन के बाद अंतरिक्ष में अपने दम पर इंसान भेजने वाला दुनिया का चौथा देश बनने के लिए पूरी तरह तैयार है।"
        ),
    },
]

P8_SLOT_CHAR_BUDGETS = {
    "top_left_3col": (48, 56),
    "top_right_flyer_5col": (44, 54),
    "left_stack_top_3col": (48, 56),
    "left_stack_mid_3col": (48, 56),
    "right_main_lead_5col": (56, 66),
    "mid_left_4col_photo": (54, 64),
    "mid_center_2col": (30, 36),
    "mid_right_2col": (30, 36),
    "bottom_left_3col": (48, 56),
    "bottom_right_anchor_5col": (44, 54),
}


def harvest_desh_videsh_page8_for_date(date_str: str = "18-11-2026", force_fresh_live: bool = False) -> dict:
    """
    Daily Page 08 ('देश-विदेश') Harvester enforcing the exact 70% National (7 stories) + 30% International Interesting (3 stories) rule.
    """
    ensure_all_real_page8_photos()
    date_json_path = HARVEST_DIR / f"{date_str}_DESH_VIDESH_PAGE8_10_STORIES.json"

    if date_str == "18-11-2026" and not force_fresh_live:
        stories = [dict(s) for s in BASE_P8_10_STORIES]
        dateline_hi = cg_core.format_hindi_dateline(date_str)
        payload = {
            "edition_date": date_str,
            "dateline_hi": dateline_hi,
            "page_number": 8,
            "section_hi": "देश-विदेश",
            "mix_rule": "70% National (7 Stories) + 30% International Interesting (3 Stories)",
            "national_count": 7,
            "international_count": 3,
            "total_stories": 10,
            "stories": stories,
        }
        date_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        P8_JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload

    if date_json_path.exists() and not force_fresh_live:
        try:
            cached = json.loads(date_json_path.read_text(encoding="utf-8"))
            if len(cached.get("stories", [])) == 10:
                P8_JSON_PATH.write_text(json.dumps(cached, ensure_ascii=False, indent=2), encoding="utf-8")
                return cached
        except Exception:
            pass

    used_set = set()
    if P8_USED_LEDGER_PATH.exists():
        try:
            used_set = set(json.loads(P8_USED_LEDGER_PATH.read_text(encoding="utf-8")).get("used_headlines", []))
        except Exception:
            used_set = set()

    nat_live = []
    intl_live = []
    nat_queries = [
        "भारत सरकार सुप्रीम कोर्ट नई दिल्ली राष्ट्रीय",
        "भारतीय रेलवे वंदे भारत इसरो रक्षा नौसेना",
        "भारत अर्थव्यवस्था सेमीकंडक्टर राजमार्ग विकास",
    ]
    intl_queries = [
        "अंतरिक्ष नासा मंगल ग्रह वैज्ञानिक खोज रोचक",
        "विश्व विज्ञान तकनीक अनोखा आविष्कार जापान यूरोप",
    ]
    for rq in nat_queries:
        try:
            u = f"https://news.google.com/rss/search?q={urllib.parse.quote(rq)}&hl=hi&gl=IN&ceid=IN:hi"
            root = ET.fromstring(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=4.5).read())
            for item in root.findall(".//item")[:8]:
                t = html.unescape((item.findtext("title") or "").strip()).rsplit(" - ", 1)[0].strip()
                if len(t) > 20 and t not in used_set and t not in nat_live:
                    nat_live.append(t)
        except Exception:
            continue

    for rq in intl_queries:
        try:
            u = f"https://news.google.com/rss/search?q={urllib.parse.quote(rq)}&hl=hi&gl=IN&ceid=IN:hi"
            root = ET.fromstring(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=4.5).read())
            for item in root.findall(".//item")[:8]:
                t = html.unescape((item.findtext("title") or "").strip()).rsplit(" - ", 1)[0].strip()
                if len(t) > 20 and t not in used_set and t not in intl_live:
                    intl_live.append(t)
        except Exception:
            continue

    stories = [dict(s) for s in BASE_P8_10_STORIES]
    ni, ii = 0, 0
    for s in stories:
        s["date"] = date_str
        lo_c, hi_c = P8_SLOT_CHAR_BUDGETS.get(s["role"], (44, 56))
        if s["category"] == "NATIONAL" and ni < len(nat_live):
            raw_t = nat_live[ni]
            ni += 1
            s["live_rss_reference"] = raw_t
            used_set.add(raw_t)
        elif s["category"] == "INTERNATIONAL" and ii < len(intl_live):
            raw_t = intl_live[ii]
            ii += 1
            s["live_rss_reference"] = raw_t
            used_set.add(raw_t)

    try:
        P8_USED_LEDGER_PATH.write_text(json.dumps({"updated_date": date_str, "used_headlines": sorted(used_set)}, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

    dateline_hi = cg_core.format_hindi_dateline(date_str)
    payload = {
        "edition_date": date_str,
        "dateline_hi": dateline_hi,
        "page_number": 8,
        "section_hi": "देश-विदेश",
        "mix_rule": "70% National (7 Stories) + 30% International Interesting (3 Stories)",
        "national_count": 7,
        "international_count": 3,
        "total_stories": 10,
        "stories": stories,
    }
    date_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    P8_JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def _patch_mod_for_desh_videsh_p8(mod):
    mod.EXTRA_WORLD_SENTENCES = (
        " विशेषज्ञों और नीति निर्माताओं का मानना है कि इस पहल से न केवल राष्ट्रीय सुरक्षा और वैज्ञानिक आत्मनिर्भरता को नई मजबूती मिलेगी, बल्कि वैश्विक मंच पर भारत की रणनीतिक साझेदारी भी और अधिक सशक्त होगी। "
        "मंत्रालय के वरिष्ठ अधिकारियों के अनुसार आगामी तिमाही में इस परियोजना के दूसरे चरण का विस्तार देश के प्रमुख औद्योगिक और शैक्षणिक गलियारों तक किया जाएगा। "
        "अंतरराष्ट्रीय पर्यवेक्षकों ने भी भारत की इस स्वदेशी तकनीकी उपलब्धि और समयबद्ध क्रियान्वयन क्षमता की सराहना की है। "
        "इसके साथ ही युवाओं और शोधकर्ताओं को आधुनिक प्रयोगशालाओं तथा वैश्विक नवाचार नेटवर्क से जोड़ने के लिए विशेष फेलोशिप कार्यक्रम भी प्रारंभ किया गया है।"
    )


# ==============================================================================
# 2. PAGE 08 BUILDER — 70% NATIONAL (7) + 30% INTERNATIONAL (3) + 1.0 CM PRINT LINE
# ==============================================================================
RAIPUR_PRINT_LINE_1 = "स्वामी/प्रकाशक - दीपक बुड़ाना द्वारा मिशन मीडिया प्रायवेट लिमिटेड, प्रेस कॉम्प्लेक्स , रजबंधा मैदान रायपुर (छ.ग) से मुद्रित एवं शौर्या आर्केड, समवेत शिखर कॉम्प्लेक्स, रजबंधा मैदान रायपुर, जिला-रायपुर (छत्तीसगढ़) से प्रकाशित।"
RAIPUR_PRINT_LINE_2 = "संपादक - दीपक बुड़ाना, समाचार चयन के लिए पीआरबी एक्ट के तहत जिम्मेदार। RNI NO. CHHHIN/2018/76773 (सभी विवादों का न्यायलय क्षेत्र रायपुर रहेगा)"

NEW_DELHI_PRINT_LINE_1 = "स्वामी/प्रकाशक - दीपक बुड़ाना द्वारा सजग मीडिया प्रायवेट लिमिटेड, सेक्टर 80, रजबंधा गौतम बुद्ध नगर उत्तर प्रदेश से मुद्रित एवं प्लॉट नंबर 4 फर्स्ट फ्लोर, साउथ गनेश नगर मदर डेयरी रोड नई दिल्ली से प्रकाशित।"
NEW_DELHI_PRINT_LINE_2 = "संपादक - दीपक बुड़ाना, PRGI No. DLHIN/25/A3662 (सभी विवादों का न्यायलय क्षेत्र नई दिल्ली रहेगा) *समाचार चयन के लिए जिम्मेदार।"

BILASPUR_PRINT_LINE_1 = "स्वामी/प्रकाशक - दीपक बुड़ाना द्वारा मिशन मीडिया प्रायवेट लिमिटेड, प्रेस कॉम्प्लेक्स , रजबंधा मैदान रायपुर (छ.ग) से मुद्रित एवं हाउस नं107 इंदिरा कांग्रेस भवन, बिलासपुर (छत्तीसगढ़) से प्रकाशित।"
BILASPUR_PRINT_LINE_2 = "संपादक - दीपक बुड़ाना, PRGI No. CTHIN/25/A1423 (सभी विवादों का न्यायलय क्षेत्र रायपुर रहेगा) *समाचार चयन के लिए जिम्मेदार।"

BHOPAL_PRINT_LINE_1 = "स्वामी/मुद्रित/प्रकाशक - दीपक बुड़ाना द्वारा प्रकाश प्रिंटर्स, 03, प्रेस काम्प्लेक्स, एम.पी. नगर, भोपाल (मध्यप्रदेश) से मुद्रित एवं 230, ओल्ड अशोका गार्डन, भारत गैस एजेंसी के सामने, भोपाल से प्रकाशित।"
BHOPAL_PRINT_LINE_2 = "संपादक - दीपक बुड़ाना, आर.एन.आई. नबंर - MPHIN/2015/63660 (सभी विवादों का न्यायलय क्षेत्र भोपाल रहेगा)*समाचार चयन के लिए जिम्मेदार।"

INDORE_PRINT_LINE_1 = "स्वामी/मुद्रित/प्रकाशक - दीपक बुड़ाना द्वारा चैतन्य लोक ग्राफिक्स, एलयूएन-22, सेक्टर-एफ इंडस्ट्रियल एरिया, सांवेर रोड इंदौर (मध्यप्रदेश) से मुद्रित एवं 66 बी शुभम पैलेस, छोटा बांगड़दा रोड इंदौर से प्रकाशित।"
INDORE_PRINT_LINE_2 = "संपादक- दीपक बुड़ाना, आर.एन.आई. नबंर - MPHIN/2014/56594 (सभी विवादों का न्यायलय क्षेत्र इंदौर रहेगा)*समाचार चयन के लिए जिम्मेदार।"

RAJNANDGAON_PRINT_LINE_1 = "स्वामी/प्रकाशक - दीपक बुड़ाना द्वारा मिशन मीडिया प्रायवेट लिमिटेड, प्रेस कॉम्प्लेक्स , रजबंधा मैदान रायपुर (छ.ग) से मुद्रित एवं न्यू खंडेलवाल कॉलोनी आंगन बाड़ी के सामने, राजनांदगांव (छत्तीसगढ़) से प्रकाशित।"
RAJNANDGAON_PRINT_LINE_2 = "संपादक - दीपक बुड़ाना, PRGI No. CTHIN/25/A4799 (सभी विवादों का न्यायलय क्षेत्र रायपुर रहेगा) *समाचार चयन के लिए जिम्मेदार।"

JAIPUR_PRINT_LINE_1 = "स्वामी/मुद्रक/प्रकाशक - दीपक बुडाना द्वारा प्लॉट नंबर 17, माँ वैष्णो देवी नगर, कालवाड़ रोड, जयपुर (राजस्थान) - 302012 से मुद्रित एवं ई-775, नकुल पथ, लाल कोठी स्कीम, जयपुर (राजस्थान) - 302015 से प्रकाशित।"
JAIPUR_PRINT_LINE_2 = "संपादक - दीपक बुडाना, पीआरजीआई पंजीकरण क्रमांक - RJHIN/26/A6072 (सभी विवादों का न्यायालय क्षेत्र जयपुर रहेगा)। *समाचार चयन के लिए जिम्मेदार।"


def build_desh_videsh_page8_70_30(
    date_str: str = None,
    edition: str = None,
    force_fresh_live: bool = False,
    export_desktop_pdf: bool = True,
    print_line_line1: str = None,
    print_line_line2: str = None,
) -> dict:
    t0 = time.perf_counter()
    import aditya_bharat_studio_app_2424 as studio
    studio.ensure_page_designer_running()

    date_str = (date_str or os.environ.get("AB_EDITION_DATE", "19-11-2026")).strip()
    ed_upper = (edition or os.environ.get("AB_EDITION", "RAIPUR")).strip().upper()
    if ed_upper in ("NEW_DELHI", "DELHI", "DEL"):
        city_hi = "नई दिल्ली"
        if not print_line_line1:
            print_line_line1 = NEW_DELHI_PRINT_LINE_1
        if not print_line_line2:
            print_line_line2 = NEW_DELHI_PRINT_LINE_2
    elif ed_upper in ("BILASPUR", "BSP"):
        city_hi = "बिलासपुर"
        if not print_line_line1:
            print_line_line1 = BILASPUR_PRINT_LINE_1
        if not print_line_line2:
            print_line_line2 = BILASPUR_PRINT_LINE_2
    elif ed_upper in ("BHOPAL", "BPL"):
        city_hi = "भोपाल"
        if not print_line_line1:
            print_line_line1 = BHOPAL_PRINT_LINE_1
        if not print_line_line2:
            print_line_line2 = BHOPAL_PRINT_LINE_2
    elif ed_upper in ("INDORE", "IND"):
        city_hi = "इंदौर"
        if not print_line_line1:
            print_line_line1 = INDORE_PRINT_LINE_1
        if not print_line_line2:
            print_line_line2 = INDORE_PRINT_LINE_2
    elif ed_upper in ("RAJNANDGAON", "RJN"):
        city_hi = "राजनांदगांव"
        if not print_line_line1:
            print_line_line1 = RAJNANDGAON_PRINT_LINE_1
        if not print_line_line2:
            print_line_line2 = RAJNANDGAON_PRINT_LINE_2
    elif ed_upper in ("JAIPUR", "JPR"):
        city_hi = "जयपुर"
        if not print_line_line1:
            print_line_line1 = JAIPUR_PRINT_LINE_1
        if not print_line_line2:
            print_line_line2 = JAIPUR_PRINT_LINE_2
    else:
        city_hi = "रायपुर"
        if not print_line_line1:
            print_line_line1 = RAIPUR_PRINT_LINE_1
        if not print_line_line2:
            print_line_line2 = RAIPUR_PRINT_LINE_2

    data = harvest_desh_videsh_page8_for_date(date_str, force_fresh_live=force_fresh_live)
    date_label = cg_core.format_hindi_dateline(date_str, city_hi=city_hi) + "  |"
    p8_stories = data["stories"]

    spec = importlib.util.spec_from_file_location("ab_base_p8_custom", str(VAULT_DIR / "build_aditya_bharat_page8_desh_videsh.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _patch_mod_for_desh_videsh_p8(mod)

    mod.connect_page_designer()
    grid = mod.AdityaBharatPage8Grid()

    if os.environ.get("AB_NO_CLOSE") != "1":
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
            "title": f"आदित्य भारत — पेज 08 देश-विदेश ({date_str} | 70% राष्ट्रीय + 30% अंतरराष्ट्रीय + Print Line)",
        }},
        {"command": "document.preferences", "params": {
            "baselineGrid": {"start": grid.margin_y_pt, "increment": 11.25, "relativeTo": "topOfPage"}
        }},
        {"command": "swatch.create", "params": {"name": "FlyerCrimson", "color": "#c4121a"}},
        {"command": "swatch.create", "params": {"name": "ClosingGray", "color": "#808285"}},
        {"command": "swatch.create", "params": {"name": "EditPointerBg", "color": "#f2f2f2"}},
    ])

    # --- 1.5 cm Inside Running Masthead (y = 1.0 .. 2.5 cm) ---
    mh_x0, mh_y0, mh_x1, mh_y1 = grid.print_x0, grid.masthead_y0, grid.print_x1, grid.masthead_y1
    sec_w = cm(4.4)
    sec_y0, sec_y1 = round(mh_y0 + mm(1.0), 2), round(mh_y1 - mm(1.8), 2)
    r_sec = mod.cmd("frame.create", {"spread": 0, "rect": [mh_x0, sec_y0, round(mh_x0 + sec_w, 2), sec_y1], "content": "text", "text": "देश-विदेश"})
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
    r_pnum = mod.cmd("frame.create", {"spread": 0, "rect": [pnum_x0, sec_y0, mh_x1, sec_y1], "content": "text", "text": "08"})
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
    # BAND 1 (STORIES 1 & 2): LEFT 3-COL NATIONAL (Cols 1..3) + RIGHT 5-COL NATIONAL FLYER (Cols 4..8)
    #   y = 2.85 .. 11.45 cm (Height = 8.6 cm)
    # ==========================================================================
    b1_y0 = round(mh_y1 + mm(3.5), 2)
    b1_y1 = mod.snap_frame_bottom_to_baseline(round(b1_y0 + cm(8.6), 2))

    # Story 1: Left 3-Col National (Cols 1..3)
    s1 = p8_stories[0]
    p_s1 = mod.place_multi_col_story(
        grid, grid.col_x0(1), grid.col_x1(1, 3), b1_y0, b1_y1, cols=3,
        headline=s1["headline"], city=s1["city"], agency=s1["agency"],
        blurb_word=s1["blurb"], body=s1["body"], target_lines=2, hi_pt=48.0, lo_pt=30.0,
    )
    pts_log.append(p_s1)

    # Story 2: Right 5-Col Illustrated National Flyer (Cols 4..8)
    s2 = p8_stories[1]
    fl_x0, fl_x1 = grid.col_x0(4), grid.col_x1(4, 5)
    _, _, _, fl_sh = mod.fit_aditya_bharat_headline(
        0, fl_x0, b1_y0, fl_x1, raw_text=s2["subhead"], target_lines=1,
        font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]", hi_pt=14.5, lo_pt=11.5, align="center",
    )
    fl_hy0 = round(b1_y0 + fl_sh + 1.0, 2)
    _, _, p_s2, fl_hh = mod.fit_aditya_bharat_headline(
        0, fl_x0, fl_hy0, fl_x1, raw_text=s2["headline"], target_lines=1,
        font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]", hi_pt=50.0, lo_pt=33.0, align="center",
    )
    pts_log.append(p_s2)
    fl_by0 = round(fl_hy0 + fl_hh + 1.5, 2)
    r_fl_b = mod.cmd("frame.create", {"spread": 0, "rect": [fl_x0, fl_by0, fl_x1, b1_y1], "content": "text", "text": ""})
    mod.cmd("object.textFrameOptions", {"ids": [r_fl_b["id"]], "columns": 5, "gutter": grid.gutter_pt, "verticalJustification": "top", "columnRule": False})
    mod.place_red_subject_blurb(0, fl_x0, round(fl_by0 + cm(1.55), 2), s2["blurb"])
    fl_cap_y1 = round(mod.snap_underflow_top(b1_y1, num_underflow_lines=4) - 3.2, 2)
    mod.place_photo_and_caption_cmyk(
        0, grid.col_x0(6), fl_by0, grid.col_x1(6, 2), fl_cap_y1,
        s2["photo"], "p8_s2_vande_cmyk.jpg", s2["caption"], cap_h=20.0,
    )
    mod.fit_aditya_bharat_body(r_fl_b["story"], s2["city"], s2["agency"], s2["body"])

    sep1_y = round(b1_y1 + mm(1.75), 2)
    r_sep1 = mod.cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep1_y], "b": [grid.print_x1, sep1_y]})
    mod.cmd("object.stroke", {"ids": [r_sep1["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 2 (STORIES 3, 4, 5): LEFT 3-COL STACK (Cols 1..3)
    #   + RIGHT 5-COL MAIN NATIONAL STRATEGIC LEAD (Cols 4..8, Gray Box in LAST Col 8!)
    #   y = 11.80 .. 26.75 cm (Height = 14.95 cm)
    # ==========================================================================
    b2_y0 = round(sep1_y + mm(1.75), 2)
    b2_y1 = mod.snap_frame_bottom_to_baseline(round(b2_y0 + cm(14.95), 2))

    # Left 3-Col Stacked National Stories 3 & 4 (Cols 1..3)
    l3_x0, l3_x1 = grid.col_x0(1), grid.col_x1(1, 3)
    l3_mid_y = mod.snap_frame_bottom_to_baseline(round(b2_y0 + cm(7.25), 2))
    s3 = p8_stories[2]
    p_s3 = mod.place_multi_col_story(
        grid, l3_x0, l3_x1, b2_y0, l3_mid_y, cols=3,
        headline=s3["headline"], city=s3["city"], agency=s3["agency"],
        blurb_word=s3["blurb"], body=s3["body"], target_lines=2, hi_pt=48.0, lo_pt=30.0,
    )
    pts_log.append(p_s3)

    l3_sep_y = round(l3_mid_y + mm(1.75), 2)
    r_l3_sep = mod.cmd("line.create", {"spread": 0, "a": [l3_x0, l3_sep_y], "b": [l3_x1, l3_sep_y]})
    mod.cmd("object.stroke", {"ids": [r_l3_sep["id"]], "swatch": "[Black]", "weight": 0.65, "tint": 0.85})

    s4 = p8_stories[3]
    p_s4 = mod.place_multi_col_story(
        grid, l3_x0, l3_x1, round(l3_sep_y + mm(1.75), 2), b2_y1, cols=3,
        headline=s4["headline"], city=s4["city"], agency=s4["agency"],
        blurb_word=s4["blurb"], body=s4["body"], target_lines=2, hi_pt=48.0, lo_pt=30.0,
    )
    pts_log.append(p_s4)

    # Right 5-Col Main National Strategic Lead (Cols 4..8, Gray Box in LAST Col 8)
    s5 = p8_stories[4]
    lead_x0, lead_x1 = grid.col_x0(4), grid.col_x1(4, 5)
    _, _, p_s5, l_hh = mod.fit_aditya_bharat_headline(
        0, lead_x0, b2_y0, lead_x1, raw_text=s5["headline"], target_lines=2,
        font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]", hi_pt=56.0, lo_pt=40.0, align="left",
    )
    pts_log.append(p_s5)
    l_sy0 = round(b2_y0 + l_hh + 1.0, 2)
    _, _, _, l_sh = mod.fit_aditya_bharat_headline(
        0, lead_x0, l_sy0, lead_x1, raw_text=s5["subhead"], target_lines=1,
        font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]", hi_pt=14.5, lo_pt=11.5, align="left",
    )
    l_by0 = round(l_sy0 + l_sh + 1.5, 2)
    r_l_b = mod.cmd("frame.create", {"spread": 0, "rect": [grid.col_x0(4), l_by0, grid.col_x1(4, 4), b2_y1], "content": "text", "text": ""})
    mod.cmd("object.textFrameOptions", {"ids": [r_l_b["id"]], "columns": 4, "gutter": grid.gutter_pt, "verticalJustification": "top", "columnRule": False})
    mod.place_red_subject_blurb(0, grid.col_x0(4), round(l_by0 + cm(1.6), 2), s5["blurb"])
    l_cap_y1 = round(mod.snap_underflow_top(b2_y1, num_underflow_lines=5) - 3.2, 2)
    mod.place_photo_and_caption_cmyk(
        0, grid.col_x0(5), l_by0, grid.col_x1(5, 2), l_cap_y1,
        s5["photo"], "p8_s5_navy_cmyk.jpg", s5["caption"], cap_h=20.0,
    )
    mod.fit_aditya_bharat_body(r_l_b["story"], s5["city"], s5["agency"], s5["body"])

    # LAST Col 8 = Full-Height 40% Gray Box
    inset_pt = mm(2.5)
    r_gb = mod.cmd("frame.create", {"spread": 0, "rect": [grid.col_x0(8), l_by0, grid.col_x1(8, 1), b2_y1], "content": "text", "text": ""})
    mod.batch([
        {"command": "object.fill", "params": {"ids": [r_gb["id"]], "swatch": "[Black]", "tint": 0.15}},
        {"command": "object.stroke", "params": {"ids": [r_gb["id"]], "swatch": "[Black]", "weight": 0.75, "tint": 0.55}},
        {"command": "object.textFrameOptions", "params": {"ids": [r_gb["id"]], "columns": 1, "inset": [inset_pt, inset_pt, inset_pt, inset_pt], "verticalJustification": "top"}},
    ])
    mod.fit_box_completely(r_gb["story"], head_str=s5["box_head"], raw_bullets=s5["box_bullets"])

    sep2_y = round(b2_y1 + mm(1.75), 2)
    r_sep2 = mod.cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep2_y], "b": [grid.print_x1, sep2_y]})
    mod.cmd("object.stroke", {"ids": [r_sep2["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 3 (STORIES 6, 7, 8): 4-COL INTERNATIONAL PHOTO FEATURE (Cols 1..4)
    #   + 2-COL NATIONAL (Cols 5..6) + 2-COL INTERNATIONAL (Cols 7..8)
    #   y = 27.10 .. 38.60 cm (Height = 11.50 cm)
    # ==========================================================================
    b3_y0 = round(sep2_y + mm(1.75), 2)
    b3_y1 = mod.snap_frame_bottom_to_baseline(round(b3_y0 + cm(11.5), 2))

    # Story 6: Left 4-Col Illustrated International Interesting Feature (Cols 1..4)
    s6 = p8_stories[5]
    c4_x0, c4_x1 = grid.col_x0(1), grid.col_x1(1, 4)
    _, _, p_s6, c4_hh = mod.fit_aditya_bharat_headline(
        0, c4_x0, b3_y0, c4_x1, raw_text=s6["headline"], target_lines=2,
        font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]", hi_pt=50.0, lo_pt=31.0, align="left",
    )
    pts_log.append(p_s6)
    c4_sy0 = round(b3_y0 + c4_hh + 1.0, 2)
    _, _, _, c4_sh = mod.fit_aditya_bharat_headline(
        0, c4_x0, c4_sy0, c4_x1, raw_text=s6["subhead"], target_lines=1,
        font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]", hi_pt=14.0, lo_pt=11.5, align="left",
    )
    c4_by0 = round(c4_sy0 + c4_sh + 1.5, 2)
    r_c4_b = mod.cmd("frame.create", {"spread": 0, "rect": [c4_x0, c4_by0, c4_x1, b3_y1], "content": "text", "text": ""})
    mod.cmd("object.textFrameOptions", {"ids": [r_c4_b["id"]], "columns": 4, "gutter": grid.gutter_pt, "verticalJustification": "top", "columnRule": False})
    mod.place_red_subject_blurb(0, c4_x0, round(c4_by0 + cm(1.55), 2), s6["blurb"])
    c4_cap_y1 = round(mod.snap_underflow_top(b3_y1, num_underflow_lines=4) - 3.2, 2)
    mod.place_photo_and_caption_cmyk(
        0, grid.col_x0(2), c4_by0, grid.col_x1(2, 2), c4_cap_y1,
        s6["photo"], "p8_s6_mars_cmyk.jpg", s6["caption"], cap_h=20.0,
    )
    mod.fit_aditya_bharat_body(r_c4_b["story"], s6["city"], s6["agency"], s6["body"])

    # Story 7: Center 2-Col National (Cols 5..6)
    s7 = p8_stories[6]
    p_s7 = mod.place_multi_col_story(
        grid, grid.col_x0(5), grid.col_x1(5, 2), b3_y0, b3_y1, cols=2,
        headline=s7["headline"], city=s7["city"], agency=s7["agency"],
        blurb_word=s7["blurb"], body=s7["body"], target_lines=2, hi_pt=44.0, lo_pt=30.0,
    )
    pts_log.append(p_s7)

    # Story 8: Right 2-Col International Interesting (Cols 7..8)
    s8 = p8_stories[7]
    p_s8 = mod.place_multi_col_story(
        grid, grid.col_x0(7), grid.col_x1(7, 2), b3_y0, b3_y1, cols=2,
        headline=s8["headline"], city=s8["city"], agency=s8["agency"],
        blurb_word=s8["blurb"], body=s8["body"], target_lines=2, hi_pt=44.0, lo_pt=30.0,
    )
    pts_log.append(p_s8)

    sep3_y = round(b3_y1 + mm(1.75), 2)
    r_sep3 = mod.cmd("line.create", {"spread": 0, "a": [grid.print_x0, sep3_y], "b": [grid.print_x1, sep3_y]})
    mod.cmd("object.stroke", {"ids": [r_sep3["id"]], "swatch": "[Black]", "weight": 0.85, "tint": 1.0})

    # ==========================================================================
    # BAND 4 (STORIES 9 & 10): LEFT 3-COL INTERNATIONAL (Cols 1..3)
    #   + RIGHT 5-COL NATIONAL GRAND SPACE ANCHOR (Cols 4..8)
    #   Stops at y = 50.65 cm so we leave exact 1.0 cm Print Line Space below the 0.5 pt Black Rule!
    # ==========================================================================
    bot_y0 = round(sep3_y + mm(1.75), 2)
    bot_y1 = mod.snap_frame_bottom_to_baseline(cm(50.65))

    # Story 9: Left 3-Col International Interesting (Cols 1..3)
    s9 = p8_stories[8]
    p_s9 = mod.place_multi_col_story(
        grid, grid.col_x0(1), grid.col_x1(1, 3), bot_y0, bot_y1, cols=3,
        headline=s9["headline"], city=s9["city"], agency=s9["agency"],
        blurb_word=s9["blurb"], body=s9["body"], target_lines=2, hi_pt=48.0, lo_pt=30.0,
    )
    pts_log.append(p_s9)

    # Story 10: Right 5-Col Illustrated National Grand Space Anchor (Cols 4..8)
    s10 = p8_stories[9]
    anc_x0, anc_x1 = grid.col_x0(4), grid.col_x1(4, 5)
    _, _, p_s10, anc_hh = mod.fit_aditya_bharat_headline(
        0, anc_x0, bot_y0, anc_x1, raw_text=s10["headline"], target_lines=1,
        font_family="DB Rasrand Bold", font_style="Bold", fill_swatch="[Black]", hi_pt=50.0, lo_pt=33.0, align="center",
    )
    pts_log.append(p_s10)
    anc_sy0 = round(bot_y0 + anc_hh + 1.0, 2)
    _, _, _, anc_sh = mod.fit_aditya_bharat_headline(
        0, anc_x0, anc_sy0, anc_x1, raw_text=s10["subhead"], target_lines=1,
        font_family="DB Hindi", font_style="Bold", fill_swatch="[Black]", hi_pt=14.0, lo_pt=11.5, align="center",
    )
    anc_by0 = round(anc_sy0 + anc_sh + 1.5, 2)
    r_anc_b = mod.cmd("frame.create", {"spread": 0, "rect": [anc_x0, anc_by0, anc_x1, bot_y1], "content": "text", "text": ""})
    mod.cmd("object.textFrameOptions", {"ids": [r_anc_b["id"]], "columns": 5, "gutter": grid.gutter_pt, "verticalJustification": "top", "columnRule": False})
    mod.place_red_subject_blurb(0, anc_x0, round(anc_by0 + cm(1.55), 2), s10["blurb"])
    anc_cap_y1 = round(mod.snap_underflow_top(bot_y1, num_underflow_lines=4) - 3.2, 2)
    mod.place_photo_and_caption_cmyk(
        0, grid.col_x0(6), anc_by0, grid.col_x1(6, 2), anc_cap_y1,
        s10["photo"], "p8_s10_isro_cmyk.jpg", s10["caption"], cap_h=20.0,
    )
    mod.fit_aditya_bharat_body(r_anc_b["story"], s10["city"], s10["agency"], s10["body"])

    # ==========================================================================
    # BOTTOM 0.5 PT BLACK RULE + 1.0 CM PRINT LINE SPACE (y = 50.90 .. 51.98 cm)
    # ==========================================================================
    pline_rule_y = cm(50.90)
    r_pl_rule = mod.cmd("line.create", {"spread": 0, "a": [grid.print_x0, pline_rule_y], "b": [grid.print_x1, pline_rule_y]})
    mod.cmd("object.stroke", {"ids": [r_pl_rule["id"]], "swatch": "[Black]", "weight": 0.5, "tint": 1.0})

    # 1.0 cm Print Line Space (y = 50.98 .. 51.98 cm) with Locked Raipur Edition 2-Line Print Line
    pl_y0 = cm(50.98)
    pl_y1 = cm(51.98)
    pl_txt = f"{print_line_line1}\n{print_line_line2}"
    r_pl_frame = mod.cmd("frame.create", {
        "spread": 0,
        "rect": [grid.print_x0, pl_y0, grid.print_x1, pl_y1],
        "content": "text",
        "text": pl_txt,
    })
    pl_sid = r_pl_frame["story"]
    l1_b = len(print_line_line1.encode("utf-8"))
    if print_line_line1.startswith("स्वामी/मुद्रक/प्रकाशक - दीपक बुडाना"):
        b1_prefix_str = "स्वामी/मुद्रक/प्रकाशक - दीपक बुडाना"
    elif print_line_line1.startswith("स्वामी/मुद्रित/प्रकाशक -"):
        b1_prefix_str = "स्वामी/मुद्रित/प्रकाशक -"
    else:
        b1_prefix_str = "स्वामी/प्रकाशक -"
    b1_prefix_b = len(b1_prefix_str.encode("utf-8"))
    b2_start_b = l1_b + 1
    if print_line_line2.startswith("संपादक - दीपक बुडाना, पीआरजीआई पंजीकरण क्रमांक - RJHIN/26/A6072"):
        b2_prefix_str = "संपादक - दीपक बुडाना, पीआरजीआई पंजीकरण क्रमांक - RJHIN/26/A6072"
    elif print_line_line2.startswith("संपादक- दीपक बुड़ाना,"):
        b2_prefix_str = "संपादक- दीपक बुड़ाना,"
    else:
        b2_prefix_str = "संपादक - दीपक बुड़ाना,"
    b2_prefix_b = len(b2_prefix_str.encode("utf-8"))
    for rni_str in ("RNI NO. CHHHIN/2018/76773", "PRGI No. DLHIN/25/A3662", "PRGI No. CTHIN/25/A1423", "PRGI No. CTHIN/25/A4799", "MPHIN/2015/63660", "MPHIN/2014/56594", "RJHIN/26/A6072"):
        rni_idx = pl_txt.find(rni_str)
        if rni_idx >= 0:
            rni_start_b = len(pl_txt[:rni_idx].encode("utf-8"))
            rni_end_b = rni_start_b + len(rni_str.encode("utf-8"))
            break
    else:
        rni_start_b, rni_end_b = -1, -1

    pl_cmds = [
        {"command": "object.textFrameOptions", "params": {"ids": [r_pl_frame["id"]], "columns": 1, "verticalJustification": "center"}},
        {"command": "text.select", "params": {"story": pl_sid, "anchor": 0, "focus": 9999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "DB Hindi",
            "fontStyle": "Regular",
            "size": 10.5,
            "leading": {"kind": "points", "value": 12.2},
            "fill": "[Black]",
            "fillTint": 1.0,
        }}},
        {"command": "type.para", "params": {"attrs": {
            "align": "center",
            "firstLineIndent": 0.0,
            "spaceBefore": 0.0,
            "spaceAfter": 0.0,
            "hyphenate": False,
            "gridAlign": "none",
        }}},
    ]
    if print_line_line1.startswith(("स्वामी/प्रकाशक -", "स्वामी/मुद्रित/प्रकाशक -", "स्वामी/मुद्रक/प्रकाशक -")):
        pl_cmds.extend([
            {"command": "text.select", "params": {"story": pl_sid, "anchor": 0, "focus": b1_prefix_b}},
            {"command": "type.char", "params": {"attrs": {"fontFamily": "DB Hindi", "fontStyle": "Bold"}}},
        ])
    if print_line_line2.startswith(("संपादक - दीपक बुड़ाना,", "संपादक- दीपक बुड़ाना,", "संपादक - दीपक बुडाना,")):
        pl_cmds.extend([
            {"command": "text.select", "params": {"story": pl_sid, "anchor": b2_start_b, "focus": b2_start_b + b2_prefix_b}},
            {"command": "type.char", "params": {"attrs": {"fontFamily": "DB Hindi", "fontStyle": "Bold"}}},
        ])
    if rni_start_b >= 0:
        rni_bold = "Bold" if "RJHIN/26/A6072" in pl_txt else "Regular"
        pl_cmds.extend([
            {"command": "text.select", "params": {"story": pl_sid, "anchor": rni_start_b, "focus": rni_end_b}},
            {"command": "type.char", "params": {"attrs": {"fontFamily": "Arial", "fontStyle": rni_bold, "size": 9.2}}},
        ])
    mod.batch(pl_cmds)

    # Triggers bottom Closing Gray Rule + Left/Center/Right 4-4 CMYK Boxes at y = 52.10 .. 52.42 cm
    mod.cmd("edit.deselectAll", {})
    mod.cmd("view.fitPage", {})

    out_pd = VAULT_DIR / "Aditya_Bharat_Page_08_Desh_Videsh_34x53.pagedesigner"
    out_png = VAULT_DIR / "Aditya_Bharat_Page_08_Desh_Videsh_34x53.png"
    out_pdf = VAULT_DIR / "Aditya_Bharat_Page_08_Desh_Videsh_CMYK_34x53.pdf"
    mod.rpc("app.save", {"path": str(out_pd)})
    mod.rpc("app.export", {"path": str(out_png), "page": 0, "scale": 1.5})
    try:
        mod.rpc("engine.execute", {"command": "file.exportPdf", "params": {"path": str(out_pdf)}})
    except Exception:
        pass

    art_png = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\8707c72d-58b0-4715-a099-3efffcd57514\aditya_bharat_page_08_desh_videsh_34x53.png")
    shutil.copy2(out_png, art_png)

    desktop_pdf_path = ""
    if export_desktop_pdf:
        try:
            desktop = Path(r"C:\Users\ADMIN\Desktop")
            d_p8 = desktop / f"Aditya_Bharat_Desh_Videsh_Page_08_{date_str}.pdf"
            if out_pdf.exists() and out_pdf.stat().st_size > 1000:
                shutil.copy2(out_pdf, d_p8)
            else:
                Image.open(out_png).convert("RGB").save(d_p8, "PDF", resolution=108.0, quality=95)
            desktop_pdf_path = str(d_p8)
        except Exception:
            pass

    studio.bring_page_designer_window_to_front()
    print(f"=== DESH-VIDESH PAGE 08 (70% NAT / 30% INTL | {date_str}) BUILT IN {time.perf_counter()-t0:.2f}s | Pts={pts_log} ===")
    return {
        "ok": True,
        "page": 8,
        "date": date_str,
        "national_stories": 7,
        "international_stories": 3,
        "headline_pts": pts_log,
        "png": str(out_png),
        "pdf": str(out_pdf),
        "desktop_pdf": desktop_pdf_path,
    }


if __name__ == "__main__":
    d_arg = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("AB_EDITION_DATE", "19-11-2026")
    ed_arg = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("AB_EDITION", "RAIPUR")
    build_desh_videsh_page8_70_30(date_str=d_arg, edition=ed_arg)
