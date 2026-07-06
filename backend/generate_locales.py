# =====================================================================
# FILE: backend/generate_locales.py
# DESCRIPTION: Automates creating public/locales/ folders and files
#              for 49 major global languages with consistent keys.
# =====================================================================

import os
import json

LANGUAGES = [
    "en", "hi", "bn", "te", "ta", "kn", "ml", "pa", "gu", "mr", "ur", "ne", "si", "ar", "fr",
    "de", "es", "pt", "it", "nl", "ru", "zh-CN", "zh-TW", "ja", "ko", "th", "vi", "tr", "fa",
    "he", "id", "ms", "sw", "pl", "uk", "ro", "hu", "cs", "el", "fi", "no", "sv", "da", "is",
    "fil", "af", "zu", "or"
]

# Basic translations dictionary for key languages
TRANSLATIONS = {
    "en": {
        "common": {
            "save": "Save Configuration",
            "saving": "Saving...",
            "back": "Back",
            "continue": "Continue",
            "sign_out": "Sign Out",
            "dark_theme": "Dark Theme",
            "light_theme": "Light Theme",
            "theme": "Theme",
            "language": "Language",
            "units": "Units",
            "cancel": "Cancel",
            "success": "Success",
            "error": "Error",
            "back_to_chat": "Back to Chat",
            "brand": "AgriAgent AI Portal",
            "subtitle": "Setup Assistant"
        },
        "dashboard": {
            "title": "Portal Configuration",
            "subtitle": "Configure language, theme parameters, units, and preferences",
            "onboarding_title": "AgriAgent AI Portal Setup",
            "onboarding_subtitle": "Setup your personal login profile information & user interface preference.",
            "personal_settings": "Personal Settings",
            "farm_details": "Farm Details",
            "regional_settings": "Regional Settings",
            "full_name": "Full Name",
            "email": "Email (Read-Only)",
            "country": "Country",
            "state": "State",
            "district": "District",
            "farm_name": "Farm Name",
            "farm_location": "Farm Location",
            "primary_crop": "Primary Crop",
            "secondary_crop": "Secondary Crop",
            "farm_size": "Farm Size",
            "size_units": "Size Units",
            "soil_type": "Soil Type",
            "irrigation": "Irrigation",
            "season": "Season",
            "gps_geotagging": "Smart Farm Geotagging",
            "gps_description": "Allow AgriAgent AI to automatically detect your farm location for highly accurate weather forecasts, disease prediction, and personalized recommendations.",
            "fetch_location": "Fetch Location",
            "use_gps": "Use Current GPS Location",
            "gps_success": "Location detected successfully",
            "gps_denied": "Permission Denied (Manual Fallback Active)",
            "map_preview": "Farm Map Preview",
            "map_placeholder": "Map preview will display once location is geocoded or detected.",
            "save_and_continue": "Save & Continue",
            "ai_preview": "AI Workspace Preview",
            "ai_status": "AgriAgent AI Status",
            "quick_stats": "Quick Stats",
            "recent_chats": "Recent Chats",
            "images": "Images",
            "weather": "Weather",
            "diseases": "Diseases"
        },
        "chat": {
            "new_chat": "New Chat",
            "placeholder": "Ask AgriAgent AI about crops, weather, diseases...",
            "welcome_title": "Welcome to AgriAgent AI",
            "welcome_desc": "Your intelligent agricultural assistant. How can I help you today?",
            "thinking": "Thinking...",
            "checking_weather": "Checking weather...",
            "analyzing_image": "Analyzing image...",
            "consulting_disease": "Consulting disease expert...",
            "consulting_crop": "Consulting crop expert...",
            "resolving_location": "Resolving location...",
            "generating_rec": "Generating recommendation..."
        },
        "weather": {
            "weather_forecast": "Weather Forecast",
            "humidity": "Humidity",
            "wind_speed": "Wind Speed",
            "precipitation": "Precipitation",
            "temperature": "Temperature",
            "advisory": "Weather Advisory"
        },
        "settings": {
            "system_settings": "System Settings",
            "system_desc": "Review preferences, location metadata, and configure farm profiles.",
            "soil_crop_seasons": "Soil & Crop Seasons",
            "gps_diagnostics": "GPS Location Diagnostics",
            "no_coords": "No coordinates captured. Attach your location in chat to reverse geocode weather advisories.",
            "danger_zone": "Delete Account (Danger Zone)",
            "danger_desc": "Permanently deletes your account records, user settings, crop logs, and diagnostic images.",
            "delete_btn": "Delete Account",
            "change_password": "Change Account Password",
            "new_password": "New Password",
            "confirm_password": "Confirm New Password",
            "notification_toggles": "Notification Toggles",
            "weather_alerts": "Weather Alerts",
            "disease_alerts": "Disease Alerts",
            "irrigation_recs": "Irrigation Recommendations",
            "gov_schemes": "Government Schemes"
        }
    },
    "hi": {
        "common": {
            "save": "कॉन्फ़िगरेशन सहेजें",
            "saving": "सहेज रहा है...",
            "back": "पीछे",
            "continue": "जारी रखें",
            "sign_out": "साइन आउट",
            "dark_theme": "डार्क थीम",
            "light_theme": "लाइट थीम",
            "theme": "थीम",
            "language": "भाषा",
            "units": "इकाइयां",
            "cancel": "रद्द करें",
            "success": "सफलता",
            "error": "त्रुटि",
            "back_to_chat": "चैट पर वापस जाएं",
            "brand": "एग्रीकोर एआई पोर्टल",
            "subtitle": "सेटअप सहायक"
        },
        "dashboard": {
            "title": "पोर्टल कॉन्फ़िगरेशन",
            "subtitle": "भाषा, थीम पैरामीटर, इकाइयां और प्राथमिकताएं कॉन्फ़िगर करें",
            "onboarding_title": "एग्रीकोर एआई पोर्टल सेटअप",
            "onboarding_subtitle": "अपनी व्यक्तिगत लॉगिन प्रोफ़ाइल जानकारी और उपयोगकर्ता इंटरफ़ेस प्राथमिकता सेट करें।",
            "personal_settings": "व्यक्तिगत सेटिंग्स",
            "farm_details": "खेत का विवरण",
            "regional_settings": "क्षेत्रीय सेटिंग्स",
            "full_name": "पूरा नाम",
            "email": "ईमेल (केवल पढ़ने के लिए)",
            "country": "देश",
            "state": "राज्य",
            "district": "जिला",
            "farm_name": "खेत का नाम",
            "farm_location": "खेत का स्थान",
            "primary_crop": "प्राथमिक फसल",
            "secondary_crop": "सहायक फसल",
            "farm_size": "खेत का आकार",
            "size_units": "आकार की इकाइयाँ",
            "soil_type": "मिट्टी का प्रकार",
            "irrigation": "सिंचाई",
            "season": "मौसम",
            "gps_geotagging": "स्मार्ट फार्म जियोटैगिंग",
            "gps_description": "अत्यंत सटीक मौसम पूर्वानुमान, रोग की भविष्यवाणी और व्यक्तिगत सिफारिशों के लिए एग्रीकोर एआई को स्वचालित रूप से आपके खेत के स्थान का पता लगाने की अनुमति दें।",
            "fetch_location": "स्थान प्राप्त करें",
            "use_gps": "वर्तमान जीपीएस स्थान का उपयोग करें",
            "gps_success": "स्थान का सफलतापूर्वक पता लगा लिया गया",
            "gps_denied": "अनुमति अस्वीकृत (मैनुअल फॉलबैक सक्रिय)",
            "map_preview": "खेत का नक्शा पूर्वावलोकन",
            "map_placeholder": "स्थान भू-कोडित या पता चलने के बाद मानचित्र पूर्वावलोकन प्रदर्शित होगा।",
            "save_and_continue": "सहेजें और जारी रखें",
            "ai_preview": "एआई कार्यक्षेत्र पूर्वावलोकन",
            "ai_status": "एग्रीकोर एआई स्थिति",
            "quick_stats": "त्वरित आँकड़े",
            "recent_chats": "हालिया चैट",
            "images": "छवियां",
            "weather": "मौसम",
            "diseases": "रोग"
        },
        "chat": {
            "new_chat": "नई चैट",
            "placeholder": "फसलों, मौसम, बीमारियों के बारे में एग्रीएजेंट एआई से पूछें...",
            "welcome_title": "एग्रीकोर एआई में आपका स्वागत है",
            "welcome_desc": "आपका बुद्धिमान कृषि सहायक। आज मैं आपकी क्या मदद कर सकता हूँ?",
            "thinking": "सोच रहा हूँ...",
            "checking_weather": "मौसम की जाँच की जा रही है...",
            "analyzing_image": "छवि का विश्लेषण किया जा रही है...",
            "consulting_disease": "रोग विशेषज्ञ से परामर्श किया जा रहा है...",
            "consulting_crop": "फसल विशेषज्ञ से परामर्श किया जा रहा है...",
            "resolving_location": "स्थान का निर्धारण किया जा रहा है...",
            "generating_rec": "सिफारिश तैयार की जा रही है..."
        },
        "weather": {
            "weather_forecast": "मौसम पूर्वानुमान",
            "humidity": "आर्द्रता",
            "wind_speed": "हवा की गति",
            "precipitation": "वर्षा",
            "temperature": "तापमान",
            "advisory": "मौसम सलाहकार"
        },
        "settings": {
            "system_settings": "सिस्टम सेटिंग्स",
            "system_desc": "प्राथमिकताओं, स्थान मेटाडेटा की समीक्षा करें और खेत प्रोफाइल कॉन्फ़िगर करें।",
            "soil_crop_seasons": "मिट्टी और फसल के मौसम",
            "gps_diagnostics": "जीपीएस स्थान निदान",
            "no_coords": "कोई निर्देशांक कैप्चर नहीं किया गया। मौसम सलाहकारों को उलटने के लिए चैट में अपना स्थान संलग्न करें।",
            "danger_zone": "खाता हटाएं (खतरा क्षेत्र)",
            "danger_desc": "आपके खाते के रिकॉर्ड, उपयोगकर्ता सेटिंग्स, फसल लॉग और नैदानिक छवियों को स्थायी रूप से हटा देता है।",
            "delete_btn": "खाता हटाएं",
            "change_password": "खाता पासवर्ड बदलें",
            "new_password": "नया पासवर्ड",
            "confirm_password": "नए पासवर्ड की पुष्टि करें",
            "notification_toggles": "अधिसूचना टॉगल",
            "weather_alerts": "मौसम अलर्ट",
            "disease_alerts": "रोग अलर्ट",
            "irrigation_recs": "सिंचाई सिफारिशें",
            "gov_schemes": "सरकारी योजनाएं"
        }
    },
    "or": {
        "common": {
            "save": "ସଂରଚନା ସଂରକ୍ଷଣ କରନ୍ତୁ",
            "saving": "ସଂରକ୍ଷଣ ହେଉଛି...",
            "back": "ପଛକୁ",
            "continue": "ଜାରି ରଖନ୍ତୁ",
            "sign_out": "ସାଇନ୍ ଆଉଟ୍",
            "dark_theme": "ଡାର୍କ ଥିମ୍",
            "light_theme": "ଲାଇଟ୍ ଥିମ୍",
            "theme": "ଥିମ୍",
            "language": "ଭାଷା",
            "units": "ଏକକ",
            "cancel": "ବାତିଲ କରନ୍ତୁ",
            "success": "ସଫଳତା",
            "error": "ତ୍ରୁଟି",
            "back_to_chat": "ଚାଟ୍‌କୁ ଫେରନ୍ତୁ",
            "brand": "ଏଗ୍ରିକୋର୍ ଏଆଇ ପୋର୍ଟାଲ୍",
            "subtitle": "ସେଟଅପ୍ ସହାୟକ"
        },
        "dashboard": {
            "title": "ପୋର୍ଟାଲ୍ ସଂରଚନା",
            "subtitle": "ଭାଷା, ଥିମ୍ ପାରାମିଟର, ଏକକ ଏବଂ ପସନ୍ଦ ସେଟ୍ କରନ୍ତୁ",
            "onboarding_title": "ଏଗ୍ରିକୋର୍ ଏଆଇ ପୋର୍ଟାଲ୍ ସେଟଅପ୍",
            "onboarding_subtitle": "ଆପଣଙ୍କର ବ୍ୟକ୍ତିଗତ ପ୍ରୋଫାଇଲ୍ ଏବଂ ଇଣ୍ଟରଫେସ୍ ପସନ୍ଦ ସେଟ୍ କରନ୍ତୁ |",
            "personal_settings": "ବ୍ୟକ୍ତିଗତ ସେଟିଙ୍ଗସ୍",
            "farm_details": "ଫାର୍ମ ବିବରଣୀ",
            "regional_settings": "ଆଞ୍ଚଳିକ ସେଟିଙ୍ଗସ୍",
            "full_name": "ପୂରା ନାମ",
            "email": "ଇମେଲ୍ (କେବଳ ପଢିବା ପାଇଁ)",
            "country": "ଦେଶ",
            "state": "ରାଜ୍ୟ",
            "district": "ଜିଲ୍ଲା",
            "farm_name": "ଫାର୍ମ ନାମ",
            "farm_location": "ଫାର୍ମ ସ୍ଥାନ",
            "primary_crop": "ମୁଖ୍ୟ ଫସଲ",
            "secondary_crop": "ସହାୟକ ଫସଲ",
            "farm_size": "ଫାର୍ମ ଆକାର",
            "size_units": "ଆକାର ଏକକ",
            "soil_type": "ମାଟି ପ୍ରକାର",
            "irrigation": "ଜଳସେଚନ",
            "season": "ଋତୁ",
            "gps_geotagging": "ସ୍ମାର୍ଟ ଫାର୍ମ ଜିଓଟ୍ୟାଗିଂ",
            "gps_description": "ସଠିକ୍ ପାଣିପାଗ ପୂର୍ବାନୁମାନ, ରୋଗ ଚିହ୍ନଟ ଏବଂ ବ୍ୟକ୍ତିଗତ ପରାମର୍ଶ ପାଇଁ ଏଗ୍ରିକୋର୍ ଏଆଇ କୁ ଆପଣଙ୍କ ଫାର୍ମ ସ୍ଥାନ ଚିହ୍ନଟ କରିବାକୁ ଅନୁମତି ଦିଅନ୍ତୁ |",
            "fetch_location": "ସ୍ଥାନ ଚିହ୍ନଟ କରନ୍ତୁ",
            "use_gps": "ଜิପିଏସ୍ ସ୍ଥାନ ବ୍ୟବହାର କରନ୍ତୁ",
            "gps_success": "ସ୍ଥାନ ସଫଳତାର ସହ ଚିହ୍ନଟ ହେଲା",
            "gps_denied": "ଅନୁମତି ପ୍ରତ୍ୟାଖ୍ୟାନ ହେଲା",
            "map_preview": "ମାନଚିତ୍ର ପୂର୍ବାବଲୋକନ",
            "map_placeholder": "ସ୍ଥାନ ଚିହ୍ନଟ ହେବା ପରେ ମାନଚିତ୍ର ପ୍ରଦର୍ଶିତ ହେବ।",
            "save_and_continue": "ସଂରକ୍ଷଣ କରନ୍ତୁ ଏବଂ ଜାରି ରଖନ୍ତୁ",
            "ai_preview": "ଏଆଇ ପୂର୍ବାବଲୋକନ",
            "ai_status": "ଏଗ୍ରିକୋର୍ ଏଆଇ ସ୍ଥିତି",
            "quick_stats": "ପରିସଂଖ୍ୟାନ",
            "recent_chats": "ନିକଟ ଅତୀତର ଚାଟ୍",
            "images": "ଛବିଗୁଡ଼ିକ",
            "weather": "ପାଣିପାଗ",
            "diseases": "ରୋଗ"
        },
        "chat": {
            "new_chat": "ନୂତନ ଚାଟ୍",
            "placeholder": "ଫସଲ, ପାଣିପାଗ, ରୋଗ ବିଷୟରେ ଏଗ୍ରିଏଜେଣ୍ଟ୍ କୁ ପଚାରନ୍ତୁ...",
            "welcome_title": "ଏଗ୍ରିକୋର୍ ଏଆଇ କୁ ସ୍ଵାଗତ",
            "welcome_desc": "ଆପଣଙ୍କର ବୁଦ୍ଧିମାନ କୃଷି ସହାୟକ। ଆଜି ମୁଁ ଆପଣଙ୍କୁ କିପରି ସାହାଯ୍ୟ କରିପାରିବି?",
            "thinking": "ଚିନ୍ତା କରୁଛି...",
            "checking_weather": "ପାଣିପାଗ ଯାଞ୍ଚ କରୁଛି...",
            "analyzing_image": "ଫଟୋ ବିଶ୍ଳେଷଣ କରୁଛି...",
            "consulting_disease": "ରୋଗ ବିଶେଷଜ୍ଞଙ୍କ ସହ ପରାମର୍ଶ କରୁଛି...",
            "consulting_crop": "ଫସଲ ବିଶେଷଜ୍ଞଙ୍କ ସହ ପରାମର୍ଶ କରୁଛି...",
            "resolving_location": "ସ୍ଥାନ ନିର୍ଣ୍ଣୟ କରୁଛି...",
            "generating_rec": "ପରାମର୍ଶ ପ୍ରସ୍ତୁତ କରୁଛି..."
        },
        "weather": {
            "weather_forecast": "ପାଣିପାଗ ପୂର୍ବାନୁମାନ",
            "humidity": "ଆର୍ଦ୍ରତା",
            "wind_speed": "ପବନର ବେଗ",
            "precipitation": "ବୃଷ୍ଟିପାତ",
            "temperature": "ତାପମାତ୍ରା",
            "advisory": "ପାଣିପାଗ ପରାମର୍ଶ"
        },
        "settings": {
            "system_settings": "ସିଷ୍ଟମ୍ ସେଟିଙ୍ଗସ୍",
            "system_desc": "ପସନ୍ଦ, ସ୍ଥାନ ମେଟାଡାଟା ସମୀକ୍ଷା କରନ୍ତୁ ଏବଂ ଫାର୍ମ ପ୍ରୋଫାଇଲ୍ ସେଟ୍ କରନ୍ତୁ।",
            "soil_crop_seasons": "ମୃତ୍ତିକା ଏବଂ ଫସଲ ଋତୁ",
            "gps_diagnostics": "ଜିପିଏସ୍ ସ୍ଥାନ ନିଦାନ",
            "no_coords": "କୌଣସି ସ୍ଥାନ ମିଳିଲା ନାହିଁ।",
            "danger_zone": "ଖାତା ବିଲୋପ କରନ୍ତୁ (ବିପଦ କ୍ଷେତ୍ର)",
            "danger_desc": "ଆପଣଙ୍କର ଖାତା ବିବରଣୀ, ସେଟିଙ୍ଗ୍ ଏବଂ ଫଟୋଗୁଡ଼ିକୁ ସ୍ଥାୟୀ ଭାବରେ ବିଲୋପ କରନ୍ତୁ।",
            "delete_btn": "ଖାତା ବିଲୋପ କରନ୍ତୁ",
            "change_password": "ପାସୱାର୍ଡ ପରିବର୍ତ୍ତନ କରନ୍ତୁ",
            "new_password": "ନୂତନ ପାସୱାର୍ଡ",
            "confirm_password": "ନୂତନ ପାସୱାର୍ଡ ନିଶ୍ଚିତ କରନ୍ତୁ",
            "notification_toggles": "ବିଜ୍ଞପ୍ତି ଟଗଲ୍",
            "weather_alerts": "ପାଣିପାଗ ଚେତାବନୀ",
            "disease_alerts": "ରୋଗ ଚେତାବନୀ",
            "irrigation_recs": "ଜଳସେଚନ ପରାମର୍ଶ",
            "gov_schemes": "ସରକାରୀ ଯୋଜନା"
        }
    }
}

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "locales"))
    os.makedirs(base_dir, exist_ok=True)
    
    english_template = TRANSLATIONS["en"]
    
    for lang in LANGUAGES:
        lang_dir = os.path.join(base_dir, lang)
        os.makedirs(lang_dir, exist_ok=True)
        
        # Determine source translation structure
        source_trans = TRANSLATIONS.get(lang, None)
        
        for namespace in ["common", "dashboard", "chat", "weather", "settings"]:
            file_path = os.path.join(lang_dir, f"{namespace}.json")
            
            if source_trans and namespace in source_trans:
                data = source_trans[namespace]
            else:
                # Fallback to English templates but ensure keys match exactly
                data = english_template[namespace]
                
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
    print(f"Successfully generated localization directories and JSON files for {len(LANGUAGES)} languages.")

if __name__ == "__main__":
    main()
