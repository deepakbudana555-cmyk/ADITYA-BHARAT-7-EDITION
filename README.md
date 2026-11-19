# 📰 दैनिक आदित्य भारत — 7-Edition (4-State) Autonomous Newspaper Studio (`ADITYA-BHARAT-7-EDITION`)

**Hybrid Local PC (`Port 2424`) + GitHub Actions Free Windows Cloud Failover + Auto-WhatsApp & Auto-Email Delivery**

---

## 🌐 4 राज्य • 7 संस्करण (Automatic Front Page State News Alter + Masthead + Page 8 Print Line)

| क्र. | संस्करण (`Edition`) | राज्य (`State`) | पेज 01 फ्रंट पेज विशेष पैकेज (`State Alter / Ulter`) | पेज 08 प्रिंट लाइन (`RNI / PRGI`) |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **रायपुर (`RAIPUR`)** | छत्तीसगढ़ (`CG`) | मुख्यमंत्री विष्णुदेव साय व छत्तीसगढ़ की 3 प्रमुख खबरें + फोटो | `RNI NO. CHHHIN/2018/76773` |
| **2** | **बिलासपुर (`BILASPUR`)** | छत्तीसगढ़ (`CG`) | मुख्यमंत्री विष्णुदेव साय व छत्तीसगढ़ की 3 प्रमुख खबरें + फोटो | `PRGI No. CTHIN/25/A1423` |
| **3** | **राजनांदगांव (`RAJNANDGAON`)** | छत्तीसगढ़ (`CG`) | मुख्यमंत्री विष्णुदेव साय व छत्तीसगढ़ की 3 प्रमुख खबरें + फोटो | `PRGI No. CTHIN/25/A4799` |
| **4** | **इंदौर (`INDORE`)** | मध्य प्रदेश (`MP`) | मुख्यमंत्री डॉ. मोहन यादव व मध्य प्रदेश की 3 प्रमुख खबरें + फोटो | `RNI NO. MPHIN/2014/56594` |
| **5** | **भोपाल (`BHOPAL`)** | मध्य प्रदेश (`MP`) | मुख्यमंत्री डॉ. मोहन यादव व मध्य प्रदेश की 3 प्रमुख खबरें + फोटो | `RNI NO. MPHIN/2015/63660` |
| **6** | **नई दिल्ली (`NEW_DELHI`)** | दिल्ली (`DL`) | दिल्ली मुख्यमंत्री / कैबिनेट व दिल्ली-एनसीआर की 3 प्रमुख खबरें + फोटो | `PRGI No. DLHIN/25/A3662` |
| **7** | **जयपुर (`JAIPUR`)** | राजस्थान (`RJ`) | मुख्यमंत्री भजनलाल शर्मा व राजस्थान की 3 प्रमुख खबरें + फोटो | `PRGI No. RJHIN/26/A6072` |

---

## 🔄 Hybrid Local + GitHub Cloud Failover कैसे काम करता है?

1. **Mode 1 — जब आपका लोकल PC चालू है (`Local PC Mode`):**
   - `http://127.0.0.1:2424` (`aditya_bharat_studio_app_2424.py`) पर **🌐 MAKE ALL 7 EDITIONS** दबाते ही सातों संस्करणों की **1 से 8 पेज की सिंगल 100% Pure Vector PDF** (`10,000% Zoom Safe`) बनती है।
   - बनते ही `ab_cloud_whatsapp_email_delivery_engine.py` उन्हें सीधे आपके **Gmail (Email)** और **WhatsApp / Telegram** पर भेज देता है, और `published_all_editions/LAST_COMPLETED_HEARTBEAT.json` को GitHub पर अपडेट कर देता है।
2. **Mode 2 — जब आपका लोकल PC बंद है (`GitHub Actions Free Windows Cloud Mode`):**
   - रात 11:45 बजे (या जब भी आप मोबाइल से GitHub के **Actions ➔ Run workflow** बटन पर क्लिक करेंगे), GitHub का फ्री `windows-latest` क्लाउड सर्वर चालू होता है।
   - अगर उस दिन लोकल PC से अख़बार नहीं बना है, तो क्लाउड सर्वर खुद सातों संस्करणों की **1–8 पेज Vector PDF** बनाता है, उन्हें आपके **Email + WhatsApp/Telegram** पर भेजता है, और इस रिपॉजिटरी के **Releases** सेक्शन में अपलोड कर देता है!

---

## 🔐 GitHub Secrets (Email और WhatsApp ऑटो-डिलीवरी के लिए):
रिपॉजिटरी के **Settings ➔ Secrets and variables ➔ Actions** में ये Secrets डालें:
- `AB_SMTP_EMAIL`: आपका Gmail पता
- `AB_SMTP_APP_PASSWORD`: आपका 16-अक्षरों का Gmail App Password
- `AB_RECIPIENT_EMAILS`: जिन ईमेल पतों पर सातों संस्करण भेजने हैं (कॉमा से अलग करके)
- `AB_WA_PHONE_NUMBER_ID` & `AB_WA_ACCESS_TOKEN` & `AB_WA_RECIPIENTS`: Meta WhatsApp Cloud API के लिए
- `AB_TG_BOT_TOKEN` & `AB_TG_CHAT_ID`: Telegram पर तुरंत सातों PDF पाने के लिए
