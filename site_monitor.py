import requests
import hashlib
import time
from datetime import datetime

def get_site_hash(url):
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": "Site-Monitor-Bot/1.0"})
        if res.status_code == 200:
            return hashlib.sha256(res.text.encode('utf-8')).hexdigest(), res.status_code
        return None, res.status_code
    except Exception:
        return None, "Connection Failed"

def send_telegram_alert(bot_token, chat_id, message):
    if not bot_token or not chat_id:
        return
    api_url = f"https://telegram.org{bot_token}/sendMessage"
    try:
        requests.post(api_url, data={"chat_id": chat_id, "text": message}, timeout=5)
    except Exception:
        pass

def start_monitoring(url, interval=15, bot_token="", chat_id=""):
    if not url.startswith("http"):
        url = "https://" + url
    print(f"\n[*] بدء مراقبة الموقع: {url} (الفحص كل {interval} ثانية)")
    
    baseline_hash, status = get_site_hash(url)
    if not baseline_hash:
        print(f"[!] تعذر الوصول للموقع في البداية. الحالة: {status}")
        return

    print(f"[+] تم تسجيل البصمة الأمنية الأصلية (SHA-256): {baseline_hash[:16]}...")
    print("[*] اضغط Ctrl + C لإيقاف المراقبة في أي وقت.\n")

    try:
        while True:
            time.sleep(interval)
            current_hash, status = get_site_hash(url)
            now = datetime.now().strftime("%H:%M:%S")

            if not current_hash:
                alert = f"🚨 تنبيه طارئ ({now}): الموقع {url} توقف عن العمل! الحالة: {status}"
                print(alert)
                send_telegram_alert(bot_token, chat_id, alert)
            elif current_hash != baseline_hash:
                alert = f"⚠️ تحذير أمني ({now}): تم اكتشاف تغيير مفاجئ في محتوى موقع {url} (احتمال اختراق أو تشويه)!"
                print(alert)
                send_telegram_alert(bot_token, chat_id, alert)
                baseline_hash = current_hash
            else:
                print(f"[{now}] ✅ الموقع سليم ويعمل بشكل طبيعي (200 OK)")
    except KeyboardInterrupt:
        print("\n[*] تم إيقاف المراقبة بواسطة المستخدم.")

if __name__ == "__main__":
    print("=== أداة مراقبة سلامة المواقع والتنبيه الفوري ===")
    target = input("أدخل رابط الموقع للمراقبة (مثال: example.com): ").strip()
    token = input("أدخل Telegram Bot Token (أو اضغط Enter للتخطي): ").strip()
    cid = input("أدخل Telegram Chat ID (أو اضغط Enter للتخطي): ").strip()
    if target:
        start_monitoring(target, interval=10, bot_token=token, chat_id=cid)