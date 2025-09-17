from gnani_sdk.router import GnaniRouter
from gnani_sdk.logging import setup_logger
from db_utils.mongo_utils import MongoDB
from db_utils.redis_utils import RedisDB
# new
from typing import Dict, Text, Any, List, Optional
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, APIRouter, Request, HTTPException, BackgroundTasks
from datetime import datetime, timezone, date, timedelta
# from num2words import num2words
from indic_numtowords import num2words
import os
import requests
import re
import time
from threading import Thread
import pytz
import json
IST = pytz.timezone('Asia/Kolkata')
date_format = "%d/%m/%Y"
def get_iso_date(date):
    return f"ISODate({date.isoformat()})"
mongo_db = MongoDB()
redis_utils = RedisDB()
# old
logger = setup_logger("project")
router = GnaniRouter().router
# def due_date_in_words(date_str, lang="english"):
#     formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"]
    
#     lang_mapping = {
#         "english": "en",
#         "hindi": "hi"
#     }
#     language = lang_mapping.get(lang.lower(), "en")
#     hindi_months = {
#         1: "जनवरी", 2: "फ़रवरी", 3: "मार्च", 4: "अप्रैल",
#         5: "मई", 6: "जून", 7: "जुलाई", 8: "अगस्त",
#         9: "सितंबर", 10: "अक्टूबर", 11: "नवंबर", 12: "दिसंबर"
#     }
#     for fmt in formats:
#         try:
#             date_obj = datetime.strptime(date_str, fmt)
#             day_words = nw.num2words(date_obj.day, lang=language)
#             year_words = nw.num2words(date_obj.year, lang=language)
#             month = (date_obj.strftime('%B') if language == "en"
#                      else hindi_months[date_obj.month])
#             return f"{day_words} {month.lower()} {year_words}"
#         except ValueError:
#             continue
#     return "due date"
    
    
MONTH_NAMES = {
    "english": [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ],
    "hindi": [
        "जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून",
        "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"
    ]
}
    
    
def get_ordinal(day):
    """Return the ordinal suffix for a given day."""
    if 10 <= day % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix}"
    
def due_date_format(date_str, language):
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"]
    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            
            if language=="english":
                day_with_ordinal = get_ordinal(date_obj.day)
                formatted_date = f"{day_with_ordinal} {date_obj.strftime('%B %Y')}"
                return formatted_date
            else:
                month_name = MONTH_NAMES[language][date_obj.month - 1]
                formatted_date = f"{date_obj.day} {month_name} {date_obj.year}"
                return formatted_date
        except ValueError:
            continue
    return "due date"
audio_files = {
    "January": "जनवरी",
    "February": "फरवरी",
    "March": "मार्च",
    "April": "अप्रैल",
    "May": "मई",
    "June": "जून",
    "July": "जुलाई",
    "August": "अगस्त",
    "September": "सितंबर",
    "October": "अक्टूबर",
    "November": "नवंबर",
    "December": "दिसंबर",
    "dollars":"डॉलर",
    "paise":"पैसे",
    "rupee":"रुपया",
    "rupees":"रुपये",
    "percent":"प्रतिशत",
    "2023": "दो हज़ार तेईस",
    "2024": "दो हज़ार चौबीस",
    "2025": "दो हज़ार पच्चीस",
    "2026": "दो हज़ार छब्बीस",
    "2027": "दो हज़ार सत्ताईस",
    "2028": "दो हज़ार अट्ठाईस",
    "2029": "दो हज़ार उनतीस",
    "2030": "दो हज़ार तीस",
    "2031": "दो हज़ार इकतीस",
    "2032": "दो हज़ार बत्तीस",
    "2033": "दो हज़ार तैंतीस",
    "2034": "दो हज़ार चौंतीस",
    "1": "एक",
    "2": "दो",
    "3": "तीन",
    "4": "चार",
    "5": "पाँच",
    "6": "छह",
    "7": "सात",
    "8": "आठ",
    "9": "नौ",
    "10": "दस",
    "11": "ग्यारह",
    "12": "बारह",
    "13": "तेरह",
    "14": "चौदह",
    "15": "पंद्रह",
    "16": "सोलह",
    "17": "सत्रह",
    "18": "अठारह",
    "19": "उन्नीस",
    "20": "बीस",
    "21": "इक्कीस",
    "22": "बाईस",
    "23": "तेइस",
    "24": "चौबीस",
    "25": "पच्चीस",
    "26": "छब्बीस",
    "27": "सत्ताईस",
    "28": "अट्ठाईस",
    "29": "उनतीस",
    "30": "तीस",
    "31": "इकतीस",
    "32": "बत्तीस",
    "33": "तैंतीस",
    "34": "चौंतीस",
    "35": "पैंतीस",
    "36": "छत्तीस",
    "37": "सैंतीस",
    "38": "अड़तीस",
    "39": "उनतालीस",
    "40": "चालीस",
    "41": "इकतालीस",
    "42": "बयालीस",
    "43": "तैंतालीस",
    "44": "चवालीस",
    "45": "पैंतालीस",
    "46": "छियालीस",
    "47": "सैंतालीस",
    "48": "अड़तालीस",
    "49": "उनचास",
    "50": "पचास",
    "51": "इक्यावन",
    "52": "बावन",
    "53": "तिरेपन",
    "54": "चौवन",
    "55": "पचपन",
    "56": "छप्पन",
    "57": "सत्तावन",
    "58": "अठावन",
    "59": "उनसाठ",
    "60": "साठ",
    "61": "इकसठ",
    "62": "बासठ",
    "63": "तिरेसठ",
    "64": "चौंसठ",
    "65": "पैंसठ",
    "66": "छियासठ",
    "67": "सड़सठ",
    "68": "अड़सठ",
    "69": "उनहत्तर",
    "70": "सत्तर",
    "71": "इकहत्तर",
    "72": "बहत्तर",
    "73": "तिहत्तर",
    "74": "चौहत्तर",
    "75": "पचहत्तर",
    "76": "छिहत्तर",
    "77": "सत्तहत्तर",
    "78": "अठहत्तर",
    "79": "उनासी",
    "80": "अस्सी",
    "81": "इक्यासी",
    "82": "बयासी",
    "83": "तिरासी",
    "84": "चौरासी",
    "85": "पचासी",
    "86": "छियासी",
    "87": "सत्तासी",
    "88": "अठासी",
    "89": "नवासी",
    "90": "नब्बे",
    "91": "इक्यानवे",
    "92": "बानवे",
    "93": "तिरेनवे",
    "94": "चौरानवे",
    "95": "पचानवे",
    "96": "छियानवे",
    "97": "सत्तानवे",
    "98": "अट्ठानवे",
    "99": "निन्यानवे",
    "100": "सौ",
    "200": "दो सौ",
    "300": "तीन सौ",
    "400": "चार सौ",
    "500": "पाँच सौ",
    "600": "छह सौ",
    "700": "सात सौ",
    "800": "आठ सौ",
    "900": "नौ सौ",
    "1000": "एक हजार",
    "2000": "दो हजार",
    "3000": "तीन हजार",
    "4000": "चार हजार",
    "5000": "पाँच हजार",
    "6000": "छह हजार",
    "7000": "सात हजार",
    "8000": "आठ हजार",
    "9000": "नौ हजार",
    "10000": "दस हजार",
    "11000": "ग्यारह हजार",
    "12000": "बारह हजार",
    "13000": "तेरह हजार",
    "14000": "चौदह हजार",
    "15000": "पंद्रह हजार",
    "16000": "सोलह हजार",
    "17000": "सत्रह हजार",
    "18000": "अठारह हजार",
    "19000": "उन्नीस हजार",
    "20000": "बीस हजार",
    "21000": "इक्कीस हजार",
    "22000": "बाईस हजार",
    "23000": "तेइस हजार",
    "24000": "चौबीस हजार",
    "25000": "पच्चीस हजार",
    "26000": "छब्बीस हजार",
    "27000": "सत्ताईस हजार",
    "28000": "अट्ठाईस हजार",
    "29000": "उनतीस हजार",
    "30000": "तीस हजार",
    "31000": "इकतीस हजार",
    "32000": "बत्तीस हजार",
    "33000": "तैंतीस हजार",
    "34000": "चौंतीस हजार",
    "35000": "पैंतीस हजार",
    "36000": "छत्तीस हजार",
    "37000": "सैंतीस हजार",
    "38000": "अड़तीस हजार",
    "39000": "उनतालीस हजार",
    "40000": "चालीस हजार",
    "41000": "इकतालीस हजार",
    "42000": "बयालीस हजार",
    "43000": "तैंतालीस हजार",
    "44000": "चवालीस हजार",
    "45000": "पैंतालीस हजार",
    "46000": "छियालीस हजार",
    "47000": "सैंतालीस हजार",
    "48000": "अड़तालीस हजार",
    "49000": "उनचास हजार",
    "50000": "पचास हजार",
    "51000": "इक्यावन हजार",
    "52000": "बावन हजार",
    "53000": "तिरेपन हजार",
    "54000": "चौवन हजार",
    "55000": "पचपन हजार",
    "56000": "छप्पन हजार",
    "57000": "सत्तावन हजार",
    "58000": "अठावन हजार",
    "59000": "उनसाठ हजार",
    "60000": "साठ हजार",
    "61000": "इकसठ हजार",
    "62000": "बासठ हजार",
    "63000": "तिरेसठ हजार",
    "64000": "चौंसठ हजार",
    "65000": "पैंसठ हजार",
    "66000": "छियासठ हजार",
    "67000": "सड़सठ हजार",
    "68000": "अड़सठ हजार",
    "69000": "उनहत्तर हजार",
    "70000": "सत्तर हजार",
    "71000": "इकहत्तर हजार",
    "72000": "बहत्तर हजार",
    "73000": "तिहत्तर हजार",
    "74000": "चौहत्तर हजार",
    "75000": "पचहत्तर हजार",
    "76000": "छिहत्तर हजार",
    "77000": "सत्तहत्तर हजार",
    "78000": "अठहत्तर हजार",
    "79000": "उनासी हजार",
    "80000": "अस्सी हजार",
    "81000": "इक्यासी हजार",
    "82000": "बयासी हजार",
    "83000": "तिरासी हजार",
    "84000": "चौरासी हजार",
    "85000": "पचासी हजार",
    "86000": "छियासी हजार",
    "87000": "सत्तासी हजार",
    "88000": "अठासी हजार",
    "89000": "नवासी हजार",
    "90000": "नब्बे हजार",
    "91000": "इक्यानवे हजार",
    "92000": "बानवे हजार",
    "93000": "तिरेनवे हजार",
    "94000": "चौरानवे हजार",
    "95000": "पचानवे हजार",
    "96000": "छियानवे हजार",
    "97000": "सत्तानवे हजार",
    "98000": "अट्ठानवे हजार",
    "99000": "निन्यानवे हजार",
    "100000": "एक लाख",
    "200000": "दो लाख",
    "300000": "तीन लाख",
    "400000": "चार लाख",
    "500000": "पाँच लाख",
    "600000": "छह लाख",
    "700000": "सात लाख",
    "800000": "आठ लाख",
    "900000": "नौ लाख",
    "1000000": "दस लाख",
    "1100000": "ग्यारह लाख",
    "1200000": "बारह लाख",
    "1300000": "तेरह लाख",
    "1400000": "चौदह लाख",
    "1500000": "पंद्रह लाख",
    "1600000": "सोलह लाख",
    "1700000": "सत्रह लाख",
    "1800000": "अठारह लाख",
    "1900000": "उन्नीस लाख",
    "2000000": "बीस लाख",
    "2100000": "इक्कीस लाख",
    "2200000": "बाईस लाख",
    "2300000": "तेइस लाख",
    "2400000": "चौबीस लाख",
    "2500000": "पच्चीस लाख",
    "2600000": "छब्बीस लाख",
    "2700000": "सत्ताईस लाख",
    "2800000": "अट्ठाईस लाख",
    "2900000": "उनतीस लाख",
    "3000000": "तीस लाख",
    "3100000": "इकतीस लाख",
    "3200000": "बत्तीस लाख",
    "3300000": "तैंतीस लाख",
    "3400000": "चौंतीस लाख",
    "3500000": "पैंतीस लाख",
    "3600000": "छत्तीस लाख",
    "3700000": "सैंतीस लाख",
    "3800000": "अड़तीस लाख",
    "3900000": "उनतालीस लाख",
    "4000000": "चालीस लाख",
    "4100000": "इकतालीस लाख",
    "4200000": "बयालीस लाख",
    "4300000": "तैंतालीस लाख",
    "4400000": "चवालीस लाख",
    "4500000": "पैंतालीस लाख",
    "4600000": "छियालीस लाख",
    "4700000": "सैंतालीस लाख",
    "4800000": "अड़तालीस लाख",
    "4900000": "उनचास लाख",
    "5000000": "पचास लाख",
    "5100000": "इक्यावन लाख",
    "5200000": "बावन लाख",
    "5300000": "तिरेपन लाख",
    "5400000": "चौवन लाख",
    "5500000": "पचपन लाख",
    "5600000": "छप्पन लाख",
    "5700000": "सत्तावन लाख",
    "5800000": "अठावन लाख",
    "5900000": "उनसाठ लाख",
    "6000000": "साठ लाख",
    "6100000": "इकसठ लाख",
    "6200000": "बासठ लाख",
    "6300000": "तिरेसठ लाख",
    "6400000": "चौंसठ लाख",
    "6500000": "पैंसठ लाख",
    "6600000": "छियासठ लाख",
    "6700000": "सड़सठ लाख",
    "6800000": "अड़सठ लाख",
    "6900000": "उनहत्तर लाख",
    "7000000": "सत्तर लाख",
    "7100000": "इकहत्तर लाख",
    "7200000": "बहत्तर लाख",
    "7300000": "तिहत्तर लाख",
    "7400000": "चौहत्तर लाख",
    "7500000": "पचहत्तर लाख",
    "7600000": "छिहत्तर लाख",
    "7700000": "सत्तहत्तर लाख",
    "7800000": "अठहत्तर लाख",
    "7900000": "उनासी लाख",
    "8000000": "अस्सी लाख",
    "8100000": "इक्यासी लाख",
    "8200000": "बयासी लाख",
    "8300000": "तिरासी लाख",
    "8400000": "चौरासी लाख",
    "8500000": "पचासी लाख",
    "8600000": "छियासी लाख",
    "8700000": "सत्तासी लाख",
    "8800000": "अठासी लाख",
    "8900000": "नवासी लाख",
    "9000000": "नब्बे लाख",
    "9100000": "इक्यानवे लाख",
    "9200000": "बानवे लाख",
    "9300000": "तिरेनवे लाख",
    "9400000": "चौरानवे लाख",
    "9500000": "पचानवे लाख",
    "9600000": "छियानवे लाख",
    "9700000": "सत्तानवे लाख",
    "9800000": "अट्ठानवे लाख",
    "9900000": "निन्यानवे लाख",
    "10000000": "एक करोड़",
    "20000000": "दो करोड़",
    "30000000": "तीन करोड़",
    "40000000": "चार करोड़",
    "50000000": "पाँच करोड़",
    "60000000": "छह करोड़",
    "70000000": "सात करोड़",
    "80000000": "आठ करोड़",
    "90000000": "नौ करोड़",
    "100000000": "दस करोड़",
    "110000000": "ग्यारह करोड़",
    "120000000": "बारह करोड़",
    "130000000": "तेरह करोड़",
    "140000000": "चौदह करोड़",
    "150000000": "पंद्रह करोड़",
    "160000000": "सोलह करोड़",
    "170000000": "सत्रह करोड़",
    "180000000": "अठारह करोड़",
    "190000000": "उन्नीस करोड़",
    "200000000": "बीस करोड़",
    "210000000": "इक्कीस करोड़",
    "220000000": "बाईस करोड़",
    "230000000": "तेइस करोड़",
    "240000000": "चौबीस करोड़",
    "250000000": "पच्चीस करोड़",
    "260000000": "छब्बीस करोड़",
    "270000000": "सत्ताईस करोड़",
    "280000000": "अट्ठाईस करोड़",
    "290000000": "उनतीस करोड़",
    "300000000": "तीस करोड़",
    "310000000": "इकतीस करोड़",
    "320000000": "बत्तीस करोड़",
    "330000000": "तैंतीस करोड़",
    "340000000": "चौंतीस करोड़",
    "350000000": "पैंतीस करोड़",
    "360000000": "छत्तीस करोड़",
    "370000000": "सैंतीस करोड़",
    "380000000": "अड़तीस करोड़",
    "390000000": "उनतालीस करोड़",
    "400000000": "चालीस करोड़",
    "410000000": "इकतालीस करोड़",
    "420000000": "बयालीस करोड़",
    "430000000": "तैंतालीस करोड़",
    "440000000": "चवालीस करोड़",
    "450000000": "पैंतालीस करोड़",
    "460000000": "छियालीस करोड़",
    "470000000": "सैंतालीस करोड़",
    "480000000": "अड़तालीस करोड़",
    "490000000": "उनचास करोड़",
    "500000000": "पचास करोड़",
    "510000000": "इक्यावन करोड़",
    "520000000": "बावन करोड़",
    "530000000": "तिरेपन करोड़",
    "540000000": "चौवन करोड़",
    "550000000": "पचपन करोड़",
    "560000000": "छप्पन करोड़",
    "570000000": "सत्तावन करोड़",
    "580000000": "अठावन करोड़",
    "590000000": "उनसठ करोड़",
    "600000000": "साठ करोड़",
    "610000000": "इकसठ करोड़",
    "620000000": "बासठ करोड़",
    "630000000": "तिरेसठ करोड़",
    "640000000": "चौंसठ करोड़",
    "650000000": "पैंसठ करोड़",
    "660000000": "छियासठ करोड़",
    "670000000": "सड़सठ करोड़",
    "680000000": "अड़सठ करोड़",
    "690000000": "उनहत्तर करोड़",
    "700000000": "सत्तर करोड़",
    "710000000": "इकहत्तर करोड़",
    "720000000": "बहत्तर करोड़",
    "730000000": "तिहत्तर करोड़",
    "740000000": "चौहत्तर करोड़",
    "750000000": "पचहत्तर करोड़",
    "760000000": "छिहत्तर करोड़",
    "770000000": "सत्तहत्तर करोड़",
    "780000000": "अठहत्तर करोड़",
    "790000000": "उनासी करोड़",
    "800000000": "अस्सी करोड़",
    "810000000": "इक्यासी करोड़",
    "820000000": "बयासी करोड़",
    "830000000": "तिरासी करोड़",
    "840000000": "चौरासी करोड़",
    "850000000": "पचासी करोड़",
    "860000000": "छियासी करोड़",
    "870000000": "सत्तासी करोड़",
    "880000000": "अठासी करोड़",
    "890000000": "नवासी करोड़",
    "900000000": "नब्बे करोड़",
    "910000000": "इक्यानवे करोड़",
    "920000000": "बानवे करोड़",
    "930000000": "तिरेनवे करोड़",
    "940000000": "चौरानवे करोड़",
    "950000000": "पचानवे करोड़",
    "960000000": "छियानवे करोड़",
    "970000000": "सत्तानवे करोड़",
    "980000000": "अट्ठानवे करोड़",
    "990000000": "निन्यानवे करोड़"
}
from dateutil import parser
def due_amount_audio(amount):
    try:
        amount = "".join(amount.split())
        print(f"amount we are getting as in due_amount_audio {amount}")
        
        length = len(amount)
        audio_sequence = []
        
        if length > 7:
            crores = amount[:-7]
            if crores != "0":
                audio_sequence.append(audio_files.get(f"{crores}0000000", crores))
            amount = amount[-7:]
        if length > 5:
            lakhs = amount[:-5]
            if lakhs != "0":
                audio_sequence.append(audio_files.get(f"{lakhs}00000", lakhs))
            amount = amount[-5:]
        
        if length > 3:
            thousands = amount[:-3]
            if thousands != "0":
                audio_sequence.append(audio_files.get(f"{thousands}000", thousands))
            amount = amount[-3:]
        
        if length > 2:
            hundreds = amount[:-2]
            if hundreds != "0" and int(hundreds) != 0:
                audio_sequence.append(audio_files.get(f"{hundreds}00", hundreds))
            amount = amount[-2:]
        
        if int(amount) > 0:
            amount = str(int(amount))
            audio_sequence.append(audio_files.get(amount, amount))
        
        audio_sequence = [seq for seq in audio_sequence if not seq.endswith("00")]
        
        audio_sequence_str = " ".join(audio_sequence)
        print(f"audio_sequence we are getting as in due_amount_audio {audio_sequence_str}")
        return audio_sequence_str
    except Exception as e:
        print(f"Error in due_amount_audio: {e}")
        return None
#-------------------------------------------------------------------------------------------------#
def date_audio(date_str):
    try:
        parsed_date = parser.parse(date_str)
        day = str(parsed_date.day)
        month = parsed_date.strftime("%B")  # Full month name
        year = str(parsed_date.year)
        day_audio = audio_files.get(day, day)
        month_audio = audio_files.get(month, month)
        year_audio = audio_files.get(year, year)
        audio_sequence = f"{day_audio} {month_audio} {year_audio}"
        print(f"Date: {date_str}")
        print(f"Audio sequence: {audio_sequence}")
        return audio_sequence
    except Exception as e:
        print(f"Error in date_audio: {e}")
        return None
#-------------------------------------------------------------------------------------------------#
def audio_policy(policy_number):
    try:
        policy_number = "".join(policy_number.split())
        print(f"policy_number we are getting as in audio_policy {policy_number}")
        audio_sequence = " ".join(audio_files.get(digit, digit) for digit in policy_number)
        print(f"audio_sequence we are getting as in audio_policy {audio_sequence}")
        return audio_sequence
    except Exception as e:
        print(f"Error in audio_policy: {e}")
        return None
#-------------------------------------------------------------------------------------------------#
def interest_audio(policy_number):
    try:
        policy_number = "".join(policy_number.split())
        print(f"policy_number we are getting as in interest_audio: {policy_number}")
        
        audio_sequence = []
        
        components = policy_number.split(".")
        
        if components[0] in audio_files:
            audio_sequence.append(audio_files[components[0]])
        else:
            for digit in components[0]:
                audio_sequence.append(audio_files.get(digit, digit))
        
        if len(components) > 1:
            audio_sequence.append(audio_files["."])
            
            for digit in components[1]:
                audio_sequence.append(audio_files.get(digit, digit))
        
        audio_sequence_str = " ".join(audio_sequence)
        print(f"audio_sequence we are getting as in interest_audio: {audio_sequence_str}")
        return audio_sequence_str
    except Exception as e:
        print(f"Error in interest_audio: {e}")
        return None
#-------------------------------------------------------------------------------#
def days_check(give_date):
    try:
        if not give_date or give_date in ["0", "null", "None"]:
            raise ValueError("Invalid date")
        
        current_date = datetime.now().date()
        given_date_dt = datetime.strptime(give_date, "%d/%m/%Y").date()
        return (given_date_dt - current_date).days
    except Exception as e:
        print(f"[days_check error]: {e}")
        return 0
    
def format(lastdigits):
    ls = []
    for i in str(lastdigits):
        ls.append("{} ".format(i))

    str1 = ""
    for i in ls:
        str1 = str1+i
    return str1
    
def calculate_due_date_difference(due_date_str, today_date_str):
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        today_date = datetime.strptime(today_date_str, "%Y-%m-%d")
        
        difference = (today_date - due_date).days
        return difference
    except:
        return 0
    
def calculate_given_difference(mention_date, todays_date):
    try:
        mention_date = datetime.strptime(mention_date, "%Y-%m-%d")
        today_date = datetime.strptime(todays_date, "%Y-%m-%d")
        
        difference = (mention_date - today_date).days
        return difference
    except:
        return 0
@router.get("/status")
def status():
    logger.info("Project status route called")
    return {"ok": True}
@router.get("/test")
def test():
    logger.info("Project test route called")
    return {"ok": True}
@router.get("/mongo_test")
def mongo_test():
    logger.info("Project mongo_test route called", extra={"sender_id": "1234567890"})
    mongo_utils = mongo_db
    mongo_count = mongo_utils.mongo_file_count("input", {})
    logger.info(f"mongo_count: {mongo_count}")
    return {"mongo_count": mongo_count}
@router.get("/redis_test")
def redis_test():
    logger.info("Project redis_test route called", extra={"sender_id": "1234567890"})
    
    
    # Test string operations
    test_key = "test_key"
    test_value = "test_value"
    redis_utils.redis_set_value(test_key, test_value)
    retrieved_value = redis_utils.redis_get_value(test_key)
    
    # Test dictionary operations
    test_dict_key = "test_dict_key"
    test_dict = {"name": "test", "value": 123}
    redis_utils.redis_set_dict_value(test_dict_key, test_dict)
    retrieved_dict = redis_utils.redis_get_dict_value(test_dict_key)
    
    # Clean up test keys
    redis_utils.redis_delete_value(test_key)
    redis_utils.redis_delete_value(test_dict_key)
    
    logger.info(f"Redis test completed. Retrieved value: {retrieved_value}, Retrieved dict: {retrieved_dict}")
    return {
        "string_test": {
            "set_value": test_value,
            "retrieved_value": retrieved_value
        },
        "dict_test": {
            "set_dict": test_dict,
            "retrieved_dict": retrieved_dict
        }
    }
def format_amount_english(amount):
    """Convert amount to English words without using audio_files dictionary"""
    try:
        # Extract number from any format
        import re
        
        # If it's a string, try to extract digits
        if isinstance(amount, str):
            # First try to find digits
            numbers = re.findall(r'\d+', str(amount))
            if numbers:
                amount = int(numbers[0])
            elif amount.isdigit():
                amount = int(amount)
            else:
                return str(amount)
        
        # Convert to English words using num2words (NOT audio_files)
        from num2words import num2words
        english_words = num2words(int(amount))
        return english_words
        
    except Exception as e:
        print(f"Error converting amount to English: {e}")
        return str(amount)

@router.get("/initial_message")
def initial_message(request: Request):
    request_data = dict(request.query_params)
    logger.info(f"Bot Parameters received = {request_data}")
    start_time = datetime.now()
    status_code = 200
    sender_id = request_data.get("sender_id","Not_received")
    next_asr_lang = ""
    logger.info(f"initial_message started at {start_time} ----------- {sender_id}")
    try:
        phone_number = request_data.get("mobile")
        
        flow_id = request_data.get("flow_id")
        obj_id = request_data.get("_id","")
        vb_enrollment_status = request_data.get("vb_enrollment_status", "not_enrolled")
        c_date_time = datetime.now(IST)
        last_triggered_date = getISOFormat(c_date_time)
        
        # initialize variables
        phone_number = int(phone_number.replace("+",""))
        
        condition  =  {"_id":obj_id} if obj_id not  in [None," ",""] else {"phone_number":phone_number}  
        logger.info(f"initial_message condition_is {condition} ----------- {sender_id}")
        insert_fields = {"sender_id": sender_id,
                        "customerCRTId":sender_id,
                        "action": "initial_action",
                        "active_call": 1,
                        "call_status": "",
                        "conversation_log": [],
                        "fallback_conv": [],
                        "fallback_count": 0,
                        "fallback_failure": "no",
                        "setupTime": 0,
                        "sts": "",
                        "ask_renew_count":0,
                        "stage":"initial_message",
                        
                        }
        update_fields = {
                    "sender_id" : sender_id,
                    "customerCRTId" : sender_id,
                    "call_initiated" : True,
                    "said_details" : False,
                    "stage" : "initial_message"
                    
        }
        # fetch data from db
        input_collection = mongo_db.mongo_get_collection_data( "input", condition, {"_id": 0})
        request_data = {**request_data, **insert_fields}
        
        count = mongo_db.mongo_file_count("input", condition)
        # check if data to be updated or inserted
        if count!="":
            if count>0:
                input_collection = {**input_collection,**update_fields}
                is_updated =  mongo_db.mongo_update("input", update_fields, condition)
                if is_updated:
                    status = "data updated successfully"
                else:
                    status = "data not inserted"
            else:
                # no none data to pass on forward
                status = "Going to insert data block"
                updated_bot_details ={}
                for i in request_data:
                    if request_data[i] not in [None,""," "]:
                        updated_bot_details[i] =  request_data[i]
                updated_bot_details["insert_date_code"] = True      ### to track in case any data being inserted
                input_collection = {**updated_bot_details}
        else:
                status = "data updation failed"
        logger.info(f"[{sender_id}]: Details condition in initial message endpoint: {status}")

        full_name = str(input_collection.get("full_name", ""))
        agent_name = str(input_collection.get("agent_name", "riya"))  # Changed from alishba
        lender_name = str(input_collection.get("lender_name", "phonepe"))
        product_description = str(input_collection.get("product_description", "business loan"))
        loan_id = str(input_collection.get("loan_id", "1234"))
        
        # Financial data (exact DB field names)
        due_amount = str(input_collection.get("due_amount", "0"))
        due_date = str(input_collection.get("due_date", ""))
        
        # Language
        language = str(input_collection.get("language", "english")).lower()
        
        # Calculate derivatives
        last_4_digits = loan_id[-4:] if len(loan_id) >= 4 else loan_id
        c_date_time = datetime.now(IST)
        todays_date = c_date_time.strftime("%Y-%m-%d")
        
        # Calculate due days from due_date and today
        due_days = str(calculate_due_date_difference(due_date, todays_date))
        
        # Convert amounts and dates for both languages
        due_amount_eng = format_amount_english(due_amount) if due_amount else ""
        due_amount_hin = due_amount_audio(due_amount) if due_amount else ""
        due_date_eng = due_date_format(due_date, "english") if due_date else ""
        due_date_hin = due_date_format(due_date, "hindi") if due_date else ""
        
        initial_msg = f"hello, I am {{{{agent_name}}}} calling from phone pay. Am I speaking with {{{{full_name}}}}?"

        # ONLY use variables that exist in your MongoDB
        user_context = {
            # Direct DB fields
            "full_name": full_name,
            "agent_name": agent_name,
            "lender_name": lender_name,
            "product_description": product_description,
            "loan_id": loan_id,
            "due_amount": due_amount,
            "due_date": due_date,
            "language": language,
            "phone_number": phone_number,
            
            # Calculated fields
            "last_4_digits": last_4_digits,
            "due_amount_eng": due_amount_eng,
            "due_amount_hin": due_amount_hin,
            "due_date_eng": due_date_eng,
            "due_date_hin": due_date_hin,
            "due_days": due_days,
            "todays_date": todays_date,
            
            # Existing tracking fields from DB
            "sequence_number": input_collection.get("sequence_number", 0),
            "answered_seq": input_collection.get("answered_seq", 0),
            "call_sequence_mapping": input_collection.get("call_sequence_mapping", {}),
            "input_date": input_collection.get("input_date", ""),
            "flow_id": flow_id,
            "stage": "initial_message"
        }

        # ADD THIS MISSING PART:
        response_json_inya = {
            "initial_message": initial_msg,
            "user_context": user_context
        }
        end_time = datetime.now()
        
    except Exception as e:
        logger.exception("Exception in initial message fetch and update: " + str(e))
        response_json_inya = {}  
        initial_msg = "We are sorry for inconvenience we are having issue we will try again"
        status_code = 400
        end_time = datetime.now()
        
    logger.info(f"initial_action duration: {end_time - start_time} ------------ {sender_id}")
    logger.info(f"response content: {response_json_inya} | status: {status_code} | sender: {sender_id}")
    
    response_data = {
        "status_code": status_code,
        "message": None,
        "data": response_json_inya,
    }
    
    response = JSONResponse(content=response_data, status_code=status_code)
    logger.info(f"response content: {response.body.decode()} | status: {response.status_code} | sender: {sender_id}")
    return response

#-------------------------------------------------------------------------------------------------#
def getISOFormat(current_date):
    '''
    Argument: current_date :date type
    returns: ISO String format of date
    '''
    converted_date = str(current_date)
    converted_date = "ISODate"+"("+current_date.isoformat()+")"
    return converted_date


def sms(phone_number,bot_data):
    try:
        current_year = datetime.now().year
        current_month = datetime.now().month
        allocate_date = f"{current_year}-{current_month:02d}-01"
        
        allocation_month = str(bot_data.get("allocation_month", allocate_date))
        event_code = str(bot_data.get("STAGE_CODE", ""))
        loan_id = str(bot_data.get("loan_id", ""))
        sender_id = str(bot_data.get("sender_id", ""))
        
        communication_level = str(bot_data.get("communication_level","customer"))
        send_to = str(bot_data.get("send_to","applicant"))
        company_id = str(bot_data.get("company_id","a3e09e17-4a67-4fdf-8225-7b2cd6299e02"))
        
        if loan_id[0] in ["`", "'"]:
            loan_id = loan_id[1:]
          
        url = f"https://apiprod.credgenics.com/helicarrier/trigger/event?company_id={company_id}"
  
        payload = json.dumps({
          "allocation_month": allocation_month,
          "loan_id": loan_id,
          "company_id": company_id,
          "communication_level": communication_level,
          "source": "V1G",
          "event_name": event_code,
          "inbound_bot_id": "vb_l&t_bucketX_VG1",
          "send_to": send_to,
          "send_to_closed_acc": False
          })
      
        headers = {
            'authenticationtoken': 'ab361169-4fbf-4ca8-951e-3a7a03cbc68f',
            'content-type': 'application/json'
          }
        
        logger.info(f"payload is --------->{payload} | sender:{sender_id}")
        response = requests.request("POST", url, headers=headers, data=payload)
        logger.info(f"sms response is --------->{payload} | sender:{sender_id}")
        logger.info(f"{response.status_code} | sender:{sender_id}")
        
        if response.status_code in [200, "200"]:
            sms_sent = "yes"
        else:
            sms_sent = "no"
            
        sms_data ={
          "phone_number": phone_number, #bot_data.get("phone_number"),
          "customerCRTId": bot_data.get("sender_id"),
          "tempDate": str(datetime.now().strftime("%d/%m/%Y")),
          "response_text": response.text,
          "response_code": response.status_code,
          "sms_sent": sms_sent,
          "event_name": event_code
        }
        rs = mongo_db.mongo_insert( col_type = "sms", record = sms_data)
        return response.text
    except Exception as e:
        return f"Failure ---- {e}"



def delete_unwanted_fields(bot_data):
    removed = []
    unwanted_keys = [
        "bot_config",
        "transcript",
        "user_mongo_data",
        "prompt",
        "messages",
        "language_specific_prompt",
        "callStatus"
    ]
    
    for key in unwanted_keys:
        if key in bot_data:
            del bot_data[key]
            removed.append(key)
    
    if removed:
        print(f"Removed fields from bot_data: {', '.join(removed)}")
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return
def convert_to_string(data):
    call_keys = [
        "callStartTime", 
        "callConnectedTime", 
        "callEndTime"    
        ]
    for k in call_keys:
        v = data.get(k)
        if not v or v in ["None", " ", ""]:
            data[k] = ""
            continue
        try:
            # Try parsing known format: "2024/06/04 14:30:00 +0530"
            if isinstance(v, str) and "/" in v:
                dt = datetime.strptime(v.strip(), "%Y/%m/%d %H:%M:%S %z")
            elif isinstance(v, datetime):
                dt = v
            else:
                # Example fallback: "2024-06-04 14:30:00"
                dt = datetime.strptime(v.strip(), "%Y-%m-%d %H:%M:%S")
            dt = dt - timedelta(hours=5, minutes=30)
            data[k] = "ISODate(" + dt.isoformat() + ")"
        except Exception as e:
            print(f"Error parsing {k}: {v} -> {e}")
            data[k] = ""
            continue
    return data
def get_requried_fields_to_update(bot_data):
    print(f"we have data before get_requried_fields_to_update :: {bot_data}")
    fields_to_update = {}
    inya_call_status_dict = bot_data.get("call_infra", {}).get("call_status", {})
    sender_id = inya_call_status_dict.get("customerCRTId", "")
    call_status = inya_call_status_dict.get("callStatus", "")
    sequence_number = bot_data.get('sequence_number', 0)
    answered_seq = bot_data.get('answered_seq', 0)
    no_answer_seq = bot_data.get('no_answer_seq', 0)
    last_triggered_date = bot_data.get("user_context",{}).get("last_triggered_date","")
    # c_date_time = datetime.now(IST)
    # last_triggered_date = getISOFormat(c_date_time)
    # inserted_on = getISOFormat(inserted_on)
    # parsed_date = datetime.fromisoformat(inserted_on)
    # inserted_on =  f"ISODate({parsed_date.isoformat()})"
    
    if call_status in ['NO ANSWER', 'BUSY', 'FAILED']:
        answered = False
    else:
        answered = True
    fields_to_update["sequence_number"] = sequence_number
    fields_to_update['last_triggered_date'] = last_triggered_date
    fields_to_update['call_initiated'] = bot_data.get("call_initiated", True)
    fields_to_update['call_comp_flag'] = bot_data.get('call_comp_flag', 'no')
    fields_to_update['setupTime'] = bot_data.get('setup_time', 0)
    call_duration = timedelta(seconds=bot_data.get('setup_time', 0))
    fields_to_update['call_duration'] = str(call_duration)
    fields_to_update['call_status'] = call_status
    fields_to_update['sts'] = call_status
    fields_to_update['customerCRTId'] = bot_data.get('conversation_id')
    fields_to_update['sender_id'] = bot_data.get('conversation_id')
    fields_to_update['call_uid'] = bot_data.get('conversation_id')
    fields_to_update['conversation_log'] = bot_data.get('conversation_log')
    fields_to_update['call_sequence_mapping'] = bot_data.get('call_sequence_mapping', None)
    fields_to_update['flow_id'] = bot_data.get("flow_id", "")
    fields_to_update['language'] = bot_data.get("language", "")
    
    if answered:
        fields_to_update["answered_seq"] = answered_seq + 1
        fields_to_update['STAGE_CODE'] = bot_data.get('STAGE_CODE', 'DSCN')
    else:
        fields_to_update['STAGE_CODE'] = "RNR"
        fields_to_update["no_answer_seq"] = no_answer_seq + 1
        
    print(f"we have data after get_requried_fields_to_update :: {fields_to_update}")
    return fields_to_update
#-----------------------------------------------------------------------------------------------------------------------------------#
def call_sequence_update(data):
    
    inya_call_status_dict = data.get("call_infra", {}).get("call_status", {})
    sender_id = inya_call_status_dict.get("customerCRTId", "")
    call_status = inya_call_status_dict.get("callStatus", "")
    
    STAGE_CODE = data.get('STAGE_CODE')
    sequence_number = int(data.get('sequence_number'))
    trigger_times = 2
    c_date_time = datetime.now(IST)
    todays_date = str(c_date_time.strftime("%Y-%m-%d"))
    logger.info(f"data we are getting inside call_sequence_update : {data}  ----- {sender_id}", data)
    try: 
        if "call_sequence_mapping" in data:
            if str(todays_date) in data["call_sequence_mapping"]:
                data["call_sequence_mapping"][str(todays_date)]["calls_triggered"] +=1
                if call_status == "ANSWERED":
                    data["call_sequence_mapping"][str(todays_date)]["answered"] +=1
                else:
                    data["call_sequence_mapping"][str(todays_date)]["not_answered"] +=1
            else:
                if call_status == "ANSWERED":
                    data["call_sequence_mapping"][str(todays_date)] = {
                        "calls_triggered":1,
                        "answered":1,
                        "not_answered":0, 
                        "max_trigger":trigger_times
                    }
                else:
                    data["call_sequence_mapping"][str(todays_date)] = {
                        "calls_triggered":1,
                        "answered":0,
                        "not_answered":1, 
                        "max_trigger":trigger_times
                    }
        else:
            if call_status == "ANSWERED":
                logger.info('Call has been initiated',data)
                data["call_sequence_mapping"] = {}
                data["call_sequence_mapping"][str(todays_date)] = {
                    "calls_triggered":1,
                    "answered":1,
                    "not_answered":0, 
                    "max_trigger":trigger_times
                }
            else:
                data["call_sequence_mapping"] = {}
                data["call_sequence_mapping"][str(todays_date)] = {
                    "calls_triggered":1,
                    "answered":0,
                    "not_answered":1, 
                    "max_trigger":trigger_times
                }
    except Exception as e:
        logger.error(f"Exception in call sequence : {e} ----- {sender_id}", data)
#-----------------------------------------------------------------------------------------------------------------------------------#
def call_logic(bot_data):
    """
    Determine the next follow-up call time based on retry logic for same-day delivery survey.
    - Calls are made for same-day delivery, no calls for today's data on the next day.
    - Max 3 attempts per day with approximately 1-hour gap.
    - Calls can be made any day of the week.
    - Delivery and survey calls occur until 9 PM.
    - Handles cases where user requests callback later.
    - Uses order_id to differentiate multiple orders for the same phone number.
    """
    try:
        max_trigger = 2
        c_date_time = datetime.now(IST)
        todays_date = str(c_date_time.strftime("%Y-%m-%d"))
        try:
            total_calls_triggered = bot_data["call_sequence_mapping"][str(todays_date)]["calls_triggered"]
        except Exception as e:
            print(f"error in seq numbers :: {e}")
        stage_code = bot_data.get("STAGE_CODE")
        #change here
        next_atmpt_codes = ["RNR"]
        trigger_call = True
        
        if total_calls_triggered < max_trigger:
            if stage_code in next_atmpt_codes:
                trigger_call = True
                next_date = datetime.now() + timedelta(minutes=60)
            else:
                trigger_call = False
                next_date = datetime.now() + timedelta(days=1)
                next_date = next_date.replace(hour=10, minute=00, second=0, microsecond=0)
        else:
            trigger_call = False
            next_date = datetime.now() + timedelta(days=1)
            next_date = next_date.replace(hour=8, minute=00, second=0, microsecond=0)
    except Exception as e:
        print(e)
    
    if next_date.hour >= 19:
        trigger_call = False
        next_date = next_date + timedelta(days=1)
        next_date = next_date.replace(hour=8, minute=00, second=0, microsecond=0)
    # ntd = getISOFormat(next_date)
    ntd = next_date - timedelta(hours=5,minutes=30)
    ntd = getISOFormat(ntd)
    return ntd, trigger_call

#-----------------------------------------------------------------------------------------------------------------------------------#
def extract_closure_reason(conversation_log):
    """Extract closure reason from conversation"""
    reasons = []
    
    for msg in conversation_log:
        if msg.get('role') == 'user':
            content = msg.get('content', '').lower()
            
            # Check for common reasons
            if any(word in content for word in ['store', 'shop', 'business', 'बंद', 'closed']):
                reasons.append("Business/Store closed")
            elif any(word in content for word in ['money', 'पैसा', 'cash', 'funds', 'नहीं है']):
                reasons.append("No money available")
            elif any(word in content for word in ['sick', 'ill', 'hospital', 'बीमार']):
                reasons.append("Medical emergency")
            elif any(word in content for word in ['job', 'work', 'employment', 'नौकरी']):
                reasons.append("Job loss/Work issues")
            elif any(word in content for word in ['family', 'परिवार', 'emergency']):
                reasons.append("Family emergency")
    
    return ", ".join(reasons) if reasons else "Not specified"

def extract_partial_amount(conversation_log):
    """Extract partial amount from conversation"""
    import re
    
    for msg in conversation_log:
        if msg.get('role') == 'user':
            content = msg.get('content', '')
            
            # Look for numbers that could be amounts
            numbers = re.findall(r'\b\d+\b', content)
            for num in numbers:
                if 100 <= int(num) <= 100000:  # Reasonable amount range
                    return int(num)
    
    return 0  # No partial amount mentioned

def extract_payment_commitment_date(conversation_log):
    """Extract when user promises to pay"""
    for msg in conversation_log:
        if msg.get('role') == 'user':
            content = msg.get('content', '').lower()
            
            if any(word in content for word in ['दो दिन', 'two day', '2 day']):
                return (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            elif any(word in content for word in ['कल', 'tomorrow', 'kal']):
                return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            elif any(word in content for word in ['एक हफ्ता', 'week', 'सप्ताह']):
                return (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            elif any(word in content for word in ['महीना', 'month', 'maheena']):
                return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    return ""

#-----------------------------------------------------------------------------------------------------------------------------------#
def process_call_status_thread(bot_data):
    """
    process_call_status - to add post conversation logic - UPDATED to use only MongoDB fields
    """
    logger.info(f"process_call_status_thread is : {bot_data}", bot_data)
    _id = bot_data.get("_id")
    phone_number = int(bot_data.get("phone_number", 0))
    
    sender_id = bot_data.get("conversation_id")
    
    output_data = {**bot_data}
    
    callConnectedTime = bot_data["call_infra"]["call_status"]["callConnectedTime"]
    if callConnectedTime in ["None", None, " ", ""]:
        callConnectedTime = ""
        bot_data['callConnectedTime'] = callConnectedTime
    
    callConnectedTime_a = bot_data.get("callConnectedTime", "")
    if callConnectedTime_a in ["None", None, " ", ""]:
        callConnectedTime = ""
        bot_data['callConnectedTime'] = callConnectedTime
        
    logger.info(f"bot_data is : {bot_data}", bot_data)
    
    try:
        # Updating customer details with new data
        empty_data = bot_data.get("empty_data")
        empty_conv_data = bot_data.get("empty_data")
        
        if empty_data == True or empty_conv_data == True:
            if "_id" in bot_data:
                del bot_data['_id']
            res_reject = mongo_db.mongo_insert(col_type = "reject", record = bot_data)
        
        else: 
            infra = bot_data["call_infra"]["call_status"]
            logger.info(f"we have inya infra as: {infra} , sender_id={sender_id}", bot_data)
            
            setupTime = bot_data["call_infra"]["call_status"]["setupTime"]
            ringingTime = bot_data["call_infra"]["call_status"]["ringingTime"]
            setupTime = int(setupTime)
            ringingTime = int(ringingTime)
            
            logger.info(f"we have setup and ringing time as:: {setupTime}, {ringingTime} sender_id={sender_id} ", bot_data)
            
            try:
                fields_to_convert = bot_data.get("call_infra", {}).get("call_status", {})
                converted_fields = convert_to_string(fields_to_convert)
                callStartTime = converted_fields.get("callStartTime", "")
                callConnectedTime = converted_fields.get("callConnectedTime", "")
                callEndTime = converted_fields.get("callEndTime", "")
            except Exception as e:
                logger.error(f"Exception in date conversion :: {e} - {sender_id}")
            
            try:
                conversation_log = bot_data.get('conversation_log', [])
                stage_code = bot_data.get('STAGE_CODE', 'DSCN')
                
                # CLOSURE ANALYTICS - Extract key metrics (these fields exist in MongoDB)
                closure_reason = extract_closure_reason(conversation_log)
                closure_time = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
                partial_amount_agreed = extract_partial_amount(conversation_log)
                payment_commitment_date = extract_payment_commitment_date(conversation_log)
                
                # Add closure analytics to bot_data
                bot_data['closure_reason'] = closure_reason
                bot_data['closure_time'] = closure_time
                bot_data['partial_amount_agreed'] = partial_amount_agreed
                bot_data['payment_commitment_date'] = payment_commitment_date
                
                logger.info(f"Closure Analytics - Reason: {closure_reason}, Partial Amount: {partial_amount_agreed}, Commitment Date: {payment_commitment_date}, sender_id={sender_id}", bot_data)

                inya_call_status_dict = bot_data.get("call_infra", {}).get("call_status", {})
                sender_id = inya_call_status_dict.get("customerCRTId", "")
                call_status = inya_call_status_dict.get("callStatus", "")
                
                # Extract ONLY MongoDB fields from user_context
                user_context = bot_data.get("user_context", {})
                
                # Direct MongoDB fields that exist in your database
                full_name = user_context.get("full_name", "")
                agent_name = user_context.get("agent_name", "riya")  # Changed from alishba
                lender_name = user_context.get("lender_name", "phonepe")
                product_description = user_context.get("product_description", "merchant loan")
                loan_id = user_context.get("loan_id", "")
                due_amount = user_context.get("due_amount", "")
                due_date = user_context.get("due_date", "")  # This exists in MongoDB
                language = user_context.get("language", "english")
                phone_number = user_context.get("phone_number", phone_number)
                
                # MongoDB tracking fields
                sequence_number = user_context.get("sequence_number", 0)
                answered_seq = user_context.get("answered_seq", 0)
                call_sequence_mapping = user_context.get("call_sequence_mapping", {})
                input_date = user_context.get("input_date", "")
                flow_id = user_context.get("flow_id", "")
                stage = user_context.get("stage", "")
                
                # Calculate derived fields (not stored separately in MongoDB)
                last_4_digits = loan_id[-4:] if len(loan_id) >= 4 else loan_id
                c_date_time = datetime.now(IST)
                todays_date = c_date_time.strftime("%Y-%m-%d")
                due_days = str(calculate_due_date_difference(due_date, todays_date)) if due_date else "0"

            except Exception as e:
                logger.error(f"Exception in usercontext :: {e} - {sender_id}")
                # Set default values if extraction fails
                full_name = ""
                agent_name = "riya"
                lender_name = "phonepe"
                product_description = "merchant loan"
                loan_id = ""
                due_amount = ""
                due_date = ""
                language = "english"
                sequence_number = 0
                answered_seq = 0
                call_sequence_mapping = {}
                input_date = ""
                flow_id = ""
                stage = ""
                last_4_digits = ""
                due_days = "0"
                todays_date = datetime.now(IST).strftime("%Y-%m-%d")
                
            inya_stage_code = bot_data.get('STAGE_CODE','')
            logger.info(f"we have STAGE_CODE in else block from inya as :: {inya_stage_code} sender_id={sender_id} ", bot_data)
            
            # Call infrastructure data
            bot_data['callEndTime'] = callEndTime
            bot_data['callConnectedTime'] = callConnectedTime
            bot_data['callStartTime'] = callStartTime
            bot_data['sender_id'] = sender_id
            bot_data['call_status'] = call_status
            bot_data['setupTime'] = setupTime
            bot_data['ringingTime'] = ringingTime
            bot_data['setup_time'] = setupTime

            # Update bot_data with ONLY MongoDB fields
            bot_data['sequence_number'] = sequence_number + 1
            bot_data['answered_seq'] = answered_seq
            bot_data['call_sequence_mapping'] = call_sequence_mapping
            bot_data['input_date'] = input_date
            bot_data['full_name'] = full_name
            bot_data['language'] = language
            bot_data['agent_name'] = agent_name
            bot_data['lender_name'] = lender_name
            bot_data['due_amount'] = due_amount
            bot_data['due_date'] = due_date  # This exists in MongoDB
            bot_data['product_description'] = product_description
            bot_data['loan_id'] = loan_id
            bot_data['phone_number'] = phone_number
            bot_data['flow_id'] = flow_id
            bot_data['stage'] = stage
            
            # Calculated fields (not stored separately but used for processing)
            bot_data['last_4_digits'] = last_4_digits
            bot_data['due_days'] = due_days
            bot_data['todays_date'] = todays_date

            inya_call_status_dict = bot_data.get("call_infra", {}).get("call_status", {})
            inya_call_status = inya_call_status_dict.get("callStatus", "")                
            
            # Stage code logic
            if setupTime == 0:
                bot_data['STAGE_CODE'] = "RNR"
                bot_data['call_status'] = "NO ANSWER"
            elif inya_stage_code == "RNR":
                bot_data['STAGE_CODE'] = "RNR"
                bot_data['call_status'] = "NO ANSWER"
            elif inya_call_status == "ANSWERED" and inya_stage_code == "RNR":
                bot_data['STAGE_CODE'] = "DSCN"
                bot_data['call_status'] = "ANSWERED"
            
            # Handle tempDate field (exists in MongoDB)
            tempDate = bot_data.get('tempDate', datetime.now().strftime("%d/%m/%Y"))
            bot_data['tempDate'] = tempDate
            
            # Clean unwanted fields
            delete_unwanted_fields(bot_data)
            
            try:
                call_sequence_update(bot_data)
            except Exception as e:
                logger.error(f"Exception in call_sequence_update: {e}", bot_data)
            
            # Calculate next trigger logic
            next_trigger_date, trigger_call = call_logic(bot_data)
            logger.info(f"next_trigger_date and trigger_call = {next_trigger_date} :: {trigger_call} :: sender_id={sender_id} ", bot_data)
          
            bot_data["next_trigger_date"] = next_trigger_date
            bot_data["trigger_call"] = trigger_call
            
            # Get fields to update with only MongoDB fields
            updated_data = get_requried_fields_to_update(bot_data)
            updated_data["next_trigger_date"] = next_trigger_date
            updated_data["trigger_call"] = trigger_call
            
            # Add closure analytics to updated_data for database storage (these fields exist in MongoDB)
            updated_data['closure_reason'] = bot_data.get('closure_reason', '')
            updated_data['closure_time'] = bot_data.get('closure_time', '')
            updated_data['partial_amount_agreed'] = bot_data.get('partial_amount_agreed', 0)
            updated_data['payment_commitment_date'] = bot_data.get('payment_commitment_date', '')
            
            logger.info(f"updated_data is : {updated_data}", bot_data)
            bot_data.update(updated_data)
            logger.info(f"check logs | {bot_data} ---- ", bot_data)
            
            # Update MongoDB with only existing fields
            res_cust = mongo_db.mongo_update(col_type = "input", record=updated_data, upd_cond = {"sender_id":sender_id})
            logger.info(f"check logs | res_cust --- {res_cust} --{sender_id}--{phone_number}--- ", bot_data)
            
            # Clean up _id field
            if "_id" in bot_data:
                del bot_data['_id']
            
            # Handle call_date to tempDate conversion (both exist in MongoDB)
            if "call_date" in bot_data:
                bot_data['tempDate'] = bot_data['call_date']
            
            # Check report data
            res_data_rep = mongo_db.mongo_file_count(col_type = "report", q1 = {"sender_id":sender_id}) 
            logger.info(f"{sender_id} has updating details as {res_data_rep}", bot_data)

            # SMS logic for PTP stage codes
            stage_code = bot_data["STAGE_CODE"]
            env = "prod"
            if stage_code in ["PTP"] and env in ["prod"]:
                try:
                    t1 = ThreadWithReturnValue(target=sms, args=(phone_number, bot_data))
                    t1.start()
                    sms_response = t1.join()
                    bot_data['sms_response'] = sms_response
                except Exception as e:
                    sms_response = f"sms error --------------------> {e}"
                    logger.error(f"SMS error: {e}")
            
            # Handle error stage codes
            inya_error = bot_data['STAGE_CODE']
            if inya_error in ["ERROR"]:
                logger.info(f"inya_error sender id as {sender_id} --- {inya_error}", bot_data)
                
            # Insert to appropriate collection based on conditions
            if res_data_rep in ["", None, {}, False, 0] and inya_error not in ["ERROR"]:
                res_report = mongo_db.mongo_insert(col_type = "output", record = bot_data)
            else:
                res_report = mongo_db.mongo_insert(col_type = "reject", record = bot_data)
                logger.info(f"check logs | reject db ---- {res_report} ---- ", bot_data)
            
            logger.info(f"check logs | Call Status ---- DB updates {res_cust} | {res_report} ---- {sender_id}", bot_data)
            
    except Exception as e:
        logger.error(f"check logs | Call Status ---- Error in updating collections-----> {e}, {sender_id}", bot_data)
        
    return output_data

def get_requried_fields_to_update(bot_data):
    """Updated to include only MongoDB fields"""
    logger.info(f"get_requried_fields_to_update input: {bot_data}")
    
    fields_to_update = {}
    inya_call_status_dict = bot_data.get("call_infra", {}).get("call_status", {})
    sender_id = inya_call_status_dict.get("customerCRTId", "")
    call_status = inya_call_status_dict.get("callStatus", "")
    
    # Get existing MongoDB fields
    sequence_number = bot_data.get('sequence_number', 0)
    answered_seq = bot_data.get('answered_seq', 0)
    no_answer_seq = bot_data.get('no_answer_seq', 0)
    last_triggered_date = bot_data.get("user_context",{}).get("last_triggered_date","")
    
    if call_status in ['NO ANSWER', 'BUSY', 'FAILED']:
        answered = False
    else:
        answered = True
        
    # Only MongoDB fields
    fields_to_update["sequence_number"] = sequence_number
    fields_to_update['last_triggered_date'] = last_triggered_date
    fields_to_update['call_initiated'] = bot_data.get("call_initiated", True)
    fields_to_update['call_comp_flag'] = bot_data.get('call_comp_flag', 'no')
    fields_to_update['setupTime'] = bot_data.get('setup_time', 0)
    
    call_duration = timedelta(seconds=bot_data.get('setup_time', 0))
    fields_to_update['call_duration'] = str(call_duration)
    fields_to_update['call_status'] = call_status
    fields_to_update['sts'] = call_status
    fields_to_update['customerCRTId'] = bot_data.get('conversation_id')
    fields_to_update['sender_id'] = bot_data.get('conversation_id')
    fields_to_update['call_uid'] = bot_data.get('conversation_id')
    fields_to_update['conversation_log'] = bot_data.get('conversation_log')
    fields_to_update['call_sequence_mapping'] = bot_data.get('call_sequence_mapping', {})
    fields_to_update['flow_id'] = bot_data.get("flow_id", "")
    fields_to_update['language'] = bot_data.get("language", "")
    
    # MongoDB user data fields
    fields_to_update['full_name'] = bot_data.get('full_name', '')
    fields_to_update['agent_name'] = bot_data.get('agent_name', 'riya')
    fields_to_update['lender_name'] = bot_data.get('lender_name', 'phonepe')
    fields_to_update['product_description'] = bot_data.get('product_description', 'merchant loan')
    fields_to_update['loan_id'] = bot_data.get('loan_id', '')
    fields_to_update['due_amount'] = bot_data.get('due_amount', '')
    fields_to_update['due_date'] = bot_data.get('due_date', '')
    fields_to_update['phone_number'] = bot_data.get('phone_number', 0)
    fields_to_update['stage'] = bot_data.get('stage', '')
    
    if answered:
        fields_to_update["answered_seq"] = answered_seq + 1
        fields_to_update['STAGE_CODE'] = bot_data.get('STAGE_CODE', 'DSCN')
    else:
        fields_to_update['STAGE_CODE'] = "RNR"
        fields_to_update["no_answer_seq"] = no_answer_seq + 1
        
    logger.info(f"get_requried_fields_to_update output: {fields_to_update}")
    return fields_to_update

#-----------------------------------------------------------------------------------------------------------------------------------#
def process_call_status(bot_data):
    logger.info("=============Entered call status function============", bot_data)
    try:
        t1 = ThreadWithReturnValue(target=process_call_status_thread, args=(bot_data,))
        t1.start()
    except Exception as e:
        logger.info("Exception in creating call status thread" + str(e), bot_data)
        
    logger.info("=============Exiting call status function============", bot_data)
    output_data = {**bot_data}
    status_code = 200
    return status_code,output_data
@router.post("/call_status/")
async def call_data(request: Request):
    request_json_object = await request.json()
    logger.info(f"request_json_object: {request_json_object}")
    
    status_code,output_response = process_call_status(request_json_object)
    logger.info(f"response content for call_status: {output_response} | status_code: {status_code}")
    response = JSONResponse(content=output_response, status_code=status_code)
    logger.info(f"response call status content: {response.body.decode()} | status: {response.status_code} ")
    return response