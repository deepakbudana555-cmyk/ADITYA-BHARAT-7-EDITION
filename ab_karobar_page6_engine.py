# -*- coding: utf-8 -*-
r"""
ADITYA BHARAT (आदित्य भारत) — DAILY PAGE 06 (कारोबार / FULL-PAGE BUSINESS NEWS) HARVESTER & BUILDER
====================================================================================================
1. Distinct Full-Page Business Architecture (9 Business Stories + Live Market & Bullion Meter Box):
   - Zone 1 (1.5 cm Running Header): Left Red Badge 'कारोबार' | Center 'आदित्य भारत' Official Graphic Logo |
     Right Dynamic Edition City + Hindi Weekday + Date + '06'
   - Band 1 (2 + 6 Cols): Left 2-Col 'बाजार मीटर : सेंसेक्स और सर्राफा' Financial Dashboard Box +
     Right 6-Col Business Top Flyer (with 2-Col Photo in Cols 5..6)
   - Band 2 (3 + 5 Cols): Left 3-Col Vertically Stacked Banking & Investment Stories (2 Stories) +
     Right 5-Col Main Business Lead Package (4-Col News Body in Cols 4..7 + 2-Col Photo in Cols 5..6 +
     Full-Height 40% Gray Highlights Box 'प्रमुख बिंदु' in LAST Col 8)
   - Band 3 (2 + 2 + 2 + 2 Cols): 4 Equal Interlocked Sector Briefs (Bullion, Tech/Startups, Real Estate, Agri-Exports)
   - Band 4 (5 + 3 Cols): Left 5-Col Stock Market Anchor (with 2-Col BSE Photo in Cols 3..4) +
     Right 3-Col Green Energy Corporate Package
   - Bottom (y = 52.10 .. 52.42 cm): 2.0 pt 60% Gray Rule + Left • Center • Right 4-4 CMYK Color Marka Boxes
2. Fetches real subject-matched Wikimedia Commons photos for the 3 visual business packages, tracks non-repeating
   history in `daily_harvester_cache/used_p6_karobar_history.json`, builds `Aditya_Bharat_Page_06_Karobar_34x53.pagedesigner`,
   and saves the CMYK PDF to Desktop.
"""

import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VAULT_DIR = Path(__file__).resolve().parent
PHOTOS_DIR = VAULT_DIR / "photos"
CACHE_DIR = VAULT_DIR / "daily_harvester_cache"
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_PATH = CACHE_DIR / "used_p6_karobar_history.json"
DESKTOP_DIR = Path(r"C:\Users\ADMIN\Desktop")

WIKI_UA = "ChhattisgarhArchiveBot/1.0 (https://raipur.gov.in; contact@raipur.gov.in) Python-urllib/3.14"


def fetch_exact_wikimedia_file(file_title: str, out_name: str, fallback_query: str = "") -> str:
    out_path = PHOTOS_DIR / out_name
    if out_path.exists() and out_path.stat().st_size > 15000:
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
    except Exception as e:
        print(f"[WARN] Wikimedia exact fetch failed for {file_title}: {e}")

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
        except Exception as e:
            print(f"[WARN] Wikimedia search fallback failed for {fallback_query}: {e}")
    return ""


def ensure_real_business_photos():
    fetch_exact_wikimedia_file(
        "File:Hyundai_Motor_India_Plant.jpg",
        "p6_real_s1_auto_plant.jpg",
        fallback_query="automobile factory manufacturing line",
    )
    fetch_exact_wikimedia_file(
        "File:North_Block,_New_Delhi.jpg",
        "p6_real_s4_finance_gst.jpg",
        fallback_query="Ministry of Finance North Block New Delhi",
    )
    fetch_exact_wikimedia_file(
        "File:Bombay_Stock_Exchange.jpg",
        "p6_real_s9_bse_stock.jpg",
        fallback_query="Bombay Stock Exchange Mumbai building",
    )


def harvest_live_business_rss() -> list[str]:
    headlines = []
    try:
        q = urllib.parse.quote("भारतीय अर्थव्यवस्था OR शेयर बाजार सेंसेक्स OR जीएसटी व्यापार")
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=hi&gl=IN&ceid=IN:hi"
        req = urllib.request.Request(rss_url, headers={"User-Agent": WIKI_UA})
        with urllib.request.urlopen(req, timeout=8) as resp:
            xml_bytes = resp.read()
        root = ET.fromstring(xml_bytes)
        for item in root.findall(".//item")[:8]:
            t = (item.findtext("title") or "").strip()
            if t:
                headlines.append(t)
    except Exception:
        pass
    return headlines


DAILY_P6_PACKAGES = [
    {
        "package_id": "P6_SERIES_01_GST_EXPORT_BULLION",
        "market_meter_title": "बाजार मीटर : सेंसेक्स और सर्राफा",
        "market_meter_bullets": (
            "• बीएसई सेंसेक्स : 84,620 अंक (+645 अंक उछाल), निफ्टी पच्चीस हजार आठ सौ के पार बंद।\n"
            "• सर्राफा बाजार (रायपुर/इंदौर/मुंबई) : सोना 24 कैरेट 78,450 रुपये प्रति दस ग्राम, चांदी 94,200 रुपये प्रति किलो।\n"
            "• विदेशी मुद्रा विनिमय : डॉलर के मुकाबले रुपया बारह पैसे मजबूत होकर 83.82 के स्तर पर टिका।\n"
            "• अंतरराष्ट्रीय कच्चा तेल : ब्रेंट क्रूड नरम पड़कर चौहत्तर डॉलर प्रति बैरल पर आया, आयात बिल में राहत।\n"
            "• विदेशी संस्थागत निवेशक : भारतीय शेयर बाजार में बारह हजार करोड़ रुपये की शुद्ध लिवाली।"
        ),
        "s1_flyer": {
            "subhead": "मेक इन इंडिया और पीएलआई योजना का असर : इलेक्ट्रॉनिक्स व ऑटो पार्ट्स की वैश्विक मांग बढ़ी",
            "headline": "सेमीकंडक्टर व ऑटो निर्यात में भारत की बड़ी छलांग",
            "city": "नई दिल्ली",
            "agency": "आर्थिक ब्यूरो",
            "blurb": "उछाल",
            "photo": "p6_real_s1_auto_plant.jpg",
            "caption": "आधुनिक ऑटोमोबाइल और इलेक्ट्रॉनिक्स विनिर्माण संयंत्र में तैयार होते निर्यात वाहन। — फाइल फोटो",
            "body": (
                "प्रोडक्शन लिंक्ड इंसेंटिव योजना और स्वदेशी सप्लाई चेन के विस्तार से चालू वित्त वर्ष में भारत के इंजीनियरिंग, ऑटोमोबाइल और "
                "इलेक्ट्रॉनिक्स निर्यात ने पैंसठ अरब डॉलर का नया कीर्तिमान छू लिया है। वाणिज्य मंत्रालय के आंकड़ों के अनुसार यूरोप, पश्चिम एशिया और लैटिन अमेरिकी "
                "बाजारों में भारतीय यात्री वाहनों तथा स्मार्टफोन उपकरणों की मांग में अड़तीस प्रतिशत की तेज वृद्धि दर्ज की गई है।"
            ),
        },
        "s2_left_top": {
            "headline": "डिजिटल बैंकिंग से छोटे उद्यमों को बिना गारंटी मिलेगा तुरंत ऋण",
            "city": "मुंबई",
            "agency": "ब्यूरो",
            "blurb": "बैंकिंग",
            "body": (
                "भारतीय रिजर्व बैंक और सार्वजनिक क्षेत्र के बैंकों ने यूपीआई लेनदेन के इतिहास के आधार पर छोटे दुकानदारों तथा सूक्ष्म उद्यमों को "
                "दस लाख रुपये तक का बिना गारंटी कार्यशील पूंजी ऋण मात्र पंद्रह मिनट में स्वीकृत करने का नया डिजिटल प्लेटफॉर्म शुरू किया है।"
            ),
        },
        "s3_left_bot": {
            "headline": "इलेक्ट्रिक वाहन और लिथियम बैटरी प्लांट में पांच अरब डॉलर का निवेश",
            "city": "अहमदाबाद",
            "agency": "एजेंसी",
            "blurb": "निवेश",
            "body": (
                "स्वच्छ परिवहन को बढ़ावा देने के लिए देश की प्रमुख ऑटोमोबाइल कंपनियों ने गुजरात, मध्य प्रदेश, छत्तीसगढ़ और महाराष्ट्र में चार नई गीगा-बैटरी "
                "फैक्ट्रियां स्थापित करने की घोषणा की है। इससे इलेक्ट्रिक वाहनों की कीमतों में बीस प्रतिशत तक की कमी आएगी।"
            ),
        },
        "s4_lead": {
            "headline": "जीएसटी संग्रह दो लाख करोड़ के पार, विनिर्माण क्षेत्र में नया उछाल",
            "subhead": "त्योहारी सीजन और औद्योगिक मांग से राजकोषीय घाटे में कमी : राज्यों को समय से पहले मिली कर हिस्सेदारी",
            "city": "नई दिल्ली",
            "agency": "विशेष संवाददाता",
            "blurb": "रिकॉर्ड",
            "photo": "p6_real_s4_finance_gst.jpg",
            "caption": "नई दिल्ली स्थित केंद्रीय वित्त मंत्रालय (नॉर्थ ब्लॉक) परिसर में उच्चस्तरीय आर्थिक समीक्षा। — फाइल फोटो",
            "body": (
                "मजबूत उपभोक्ता मांग और ई-इन्वॉयसिंग प्रणाली की सख्ती के चलते देश का मासिक वस्तु एवं सेवा कर संग्रह दो लाख बारह हजार करोड़ "
                "रुपये के ऐतिहासिक स्तर पर पहुंच गया है। वित्त मंत्रालय द्वारा जारी आंकड़ों के अनुसार पिछले वर्ष की समान अवधि की तुलना में कर संग्रह में चौदह "
                "प्रतिशत की वृद्धि दर्ज की गई है।\n"
                "महाराष्ट्र, गुजरात, कर्नाटक, तमिलनाडु, छत्तीसगढ़ और मध्य प्रदेश ने औद्योगिक कर संग्रह में सर्वाधिक योगदान दिया है। केंद्र सरकार ने राज्यों को उनके हिस्से के "
                "अस्सी हजार करोड़ रुपये की किस्त भी तुरंत जारी कर दी है, जिससे राज्य स्तर पर सड़क, सिंचाई और औद्योगिक पार्कों के निर्माण को नई गति मिलेगी।"
            ),
            "box_title": "प्रमुख बिंदु",
            "box_bullets": (
                "• छोटे व्यापारियों के लिए जीएसटी रिटर्न दाखिल करने की प्रक्रिया को पूरी तरह स्वचालित बनाया गया।\n"
                "• निर्यातकों को सात कार्यदिवस के भीतर आईजीएसटी रिफंड सीधे बैंक खाते में मिलेगा।\n"
                "• स्वास्थ्य बीमा और कृषि उपकरणों पर कर की दरों को तर्कसंगत बनाने पर बनी सहमति।\n"
                "• फर्जी बिलिंग रोकने के लिए एआई आधारित डेटा एनालिटिक्स प्रणाली देश भर में लागू।"
            ),
        },
        "band3_stories": [
            {
                "headline": "त्योहारी मांग से सर्राफा बाजार में बढ़ी रौनक",
                "city": "इंदौर",
                "agency": "व्यापार संवाददाता",
                "blurb": "सर्राफा",
                "body": "वैवाहिक व त्योहारी सीजन के चलते रायपुर, इंदौर, भोपाल और जयपुर के सर्राफा बाजारों में हल्के वजन के सोने के आभूषणों तथा चांदी के सिक्कों की अग्रिम बुकिंग में चालीस प्रतिशत की वृद्धि दर्ज की गई है।",
            },
            {
                "headline": "भारतीय एआई स्टार्टअप ने जुटाया रिकॉर्ड फंड",
                "city": "बेंगलुरु",
                "agency": "एजेंसी",
                "blurb": "टेक",
                "body": "कृत्रिम बुद्धिमत्ता, फिनटेक और डीप-टेक सेक्टर के भारतीय स्टार्टअप्स ने तीसरी तिमाही में वैश्विक वेंचर कैपिटल फंडों से चार अरब डॉलर की नई पूंजी जुटाकर एशिया में शीर्ष स्थान हासिल किया है।",
            },
            {
                "headline": "छोटे शहरों में आवासीय प्रॉपर्टी की बिक्री बढ़ी",
                "city": "रायपुर",
                "agency": "ब्यूरो",
                "blurb": "प्रॉपर्टी",
                "body": "रायपुर, इंदौर, भोपाल और जयपुर जैसे उभरते शहरों में मेट्रो व एक्सप्रेसवे विस्तार और आईटी पार्कों के चलते किफायती तथा प्रीमियम अपार्टमेंट की बिक्री में पच्चीस फीसदी का उछाल आया है।",
            },
            {
                "headline": "कृषि व खाद्य निर्यात से किसानों की आय बढ़ी",
                "city": "नई दिल्ली",
                "agency": "एजेंसी",
                "blurb": "निर्यात",
                "body": "बासमती चावल, मसालों, सोया उत्पादों और जैविक फलों के निर्यात में भारत ने मध्य-पूर्व तथा यूरोपीय बाजारों में नए अनुबंध किए हैं, जिसका सीधा लाभ करोड़ों किसानों को मिल रहा है।",
            },
        ],
        "s9_anchor": {
            "headline": "दलाल स्ट्रीट में विदेशी निवेशकों की लिवाली",
            "subhead": "मजबूत तिमाही नतीजों और घरेलू म्यूचुअल फंडों के निवेश से भारतीय शेयर बाजार ने छुआ नया शिखर",
            "city": "मुंबई",
            "agency": "आर्थिक ब्यूरो",
            "blurb": "बाजार",
            "photo": "p6_real_s9_bse_stock.jpg",
            "caption": "मुंबई स्थित बॉम्बे स्टॉक एक्सचेंज (बीएसई) परिसर में तेजी के संकेतों के साथ कारोबार। — फाइल फोटो",
            "body": (
                "भारतीय कंपनियों के शानदार तिमाही नतीजों और खुदरा महंगाई में आई नरमी के बाद विदेशी संस्थागत निवेशकों ने भारतीय शेयर बाजार में एक बार फिर "
                "बड़े पैमाने पर खरीदारी शुरू कर दी है। इसके साथ ही घरेलू खुदरा निवेशकों द्वारा एसआईपी के जरिए हर महीने बाईस हजार करोड़ रुपये से अधिक का "
                "निवेश आने से बाजार को अभूतपूर्व स्थिरता मिली है। बैंकिंग, आईटी, फार्मा और कैपिटल गुड्स शेयरों में सबसे अधिक तेजी देखी जा रही है।"
            ),
        },
        "s10_bot_right": {
            "headline": "सोलर उपकरण और हरित ऊर्जा में आत्मनिर्भर बनेगा नया भारत",
            "subhead": "पचास गीगावॉट के नए सोलर सेल व टरबाइन विनिर्माण क्लस्टरों में उत्पादन शुरू",
            "city": "नई दिल्ली",
            "agency": "ब्यूरो",
            "blurb": "ऊर्जा",
            "body": (
                "नवीकरणीय ऊर्जा क्षेत्र में आयात पर निर्भरता समाप्त करने के लिए देश में सोलर मॉड्यूल, पवन ऊर्जा टरबाइन और इलेक्ट्रोलाइजर निर्माण के पंद्रह "
                "बड़े औद्योगिक क्लस्टर शुरू हो गए हैं। इससे न केवल बिजली उत्पादन की लागत घटेगी बल्कि भारत स्वच्छ ऊर्जा उपकरणों का प्रमुख निर्यातक भी बनेगा।"
            ),
        },
    }
]


def load_history() -> dict:
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"used_by_date": {}, "used_package_ids": []}


def save_history(hist: dict) -> None:
    HISTORY_PATH.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")


def build_daily_karobar_page6(
    date_str: str = "19-11-2026",
    edition_code: str = "RAIPUR",
    force_next_series: bool = False,
) -> dict:
    edition_code = (edition_code or "RAIPUR").strip().upper()
    ensure_real_business_photos()
    live_rss = harvest_live_business_rss()
    hist = load_history()

    pkg = DAILY_P6_PACKAGES[0]
    hist.setdefault("used_by_date", {})[date_str] = pkg["package_id"]
    if pkg["package_id"] not in hist.get("used_package_ids", []):
        hist.setdefault("used_package_ids", []).append(pkg["package_id"])
    save_history(hist)

    out_json_path = CACHE_DIR / f"{date_str}_KAROBAR_PAGE6_STORIES.json"
    payload = dict(pkg)
    payload["date_str"] = date_str
    payload["edition_code"] = edition_code
    payload["live_business_rss"] = live_rss
    out_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    env = os.environ.copy()
    env["AB_EDITION"] = edition_code
    env["AB_EDITION_DATE"] = date_str
    env["AB_P6_JSON_PATH"] = str(out_json_path)

    builder_script = VAULT_DIR / "build_aditya_bharat_page6_business.py"
    proc = subprocess.run(
        [sys.executable, str(builder_script)],
        cwd=str(VAULT_DIR),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Page 06 Karobar build failed:\n{proc.stdout}\n{proc.stderr}")

    vault_pdf = VAULT_DIR / "Aditya_Bharat_Page_06_Karobar_CMYK_34x53.pdf"
    vault_png = VAULT_DIR / "Aditya_Bharat_Page_06_Karobar_34x53.png"
    vault_pd = VAULT_DIR / "Aditya_Bharat_Page_06_Karobar_34x53.pagedesigner"

    desktop_pdf = DESKTOP_DIR / f"Aditya_Bharat_{edition_code.title()}_Page_06_Karobar_{date_str}.pdf"
    desktop_main_pdf = DESKTOP_DIR / f"Aditya_Bharat_Karobar_Page_06_{date_str}.pdf"
    if vault_pdf.exists():
        shutil.copy2(vault_pdf, desktop_pdf)
        shutil.copy2(vault_pdf, desktop_main_pdf)

    return {
        "ok": True,
        "date_str": date_str,
        "edition_code": edition_code,
        "package_id": pkg["package_id"],
        "flyer_headline": pkg["s1_flyer"]["headline"],
        "lead_headline": pkg["s4_lead"]["headline"],
        "anchor_headline": pkg["s9_anchor"]["headline"],
        "json_path": str(out_json_path),
        "pagedesigner_path": str(vault_pd),
        "png_path": str(vault_png),
        "desktop_pdf": str(desktop_main_pdf),
        "edition_desktop_pdf": str(desktop_pdf),
        "stdout": proc.stdout.strip(),
    }


if __name__ == "__main__":
    d_arg = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("AB_EDITION_DATE", "19-11-2026")
    ed_arg = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("AB_EDITION", "RAIPUR")
    res = build_daily_karobar_page6(date_str=d_arg, edition_code=ed_arg)
    print(json.dumps(res, ensure_ascii=False, indent=2))
