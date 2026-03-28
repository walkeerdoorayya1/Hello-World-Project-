import requests
import time
import socket
import os
import paramiko

# --- ANSI COLORS ---
G, Y, R, C, W = '\033[92m', '\033[93m', '\033[91m', '\033[96m', '\033[0m'

# --- CONFIGURATION ---
TOKEN = "7809221546:AAE5uB_syN23ZNpdmvo-kpEWhXm-MNF9aEI"
MY_ID = 6475849585
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"
TOP_15_PORTS = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 3306, 8080]

def log(msg, color=W):
    print(f"[{time.strftime('%H:%M:%S')}] {color}{msg}{W}")

def send_msg(chat_id, text):
    try:
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
        requests.get(BASE_URL + "sendMessage", params=params, timeout=10)
    except: log("Telegram Error!", R)

def get_banner(ip, port):
    try:
        s = socket.socket()
        s.settimeout(1.2)
        s.connect((ip, port))
        if port in [80, 443]: return "Web Service"
        banner = s.recv(1024).decode().strip()
        s.close()
        return banner[:40] if banner else "Open"
    except: return "Open"

def main():
    os.system('clear')
    print(f"{G}MASTER RECON BOT (v4.0) ONLINE{W}\n" + "-"*40)
    last_id = None
    while True:
        try:
            url = BASE_URL + ("getUpdates?timeout=30&offset=" + str(last_id) if last_id else "getUpdates?timeout=30")
            data = requests.get(url, timeout=35).json()
            if data.get("result"):
                for update in data["result"]:
                    last_id = update["update_id"] + 1
                    msg = update.get("message")
                    if msg and "text" in msg:
                        chat_id, raw_text = msg["chat"]["id"], msg["text"].strip().lower()
                        if chat_id != MY_ID: continue

                        # COMMANDS
                        if raw_text == "/start":
                            send_msg(chat_id, "🚀 *Master Bot v4.0*\n/scan <url>\n/whois <url>\n/headers <url>\n/brute <ip> <user>")

                        elif raw_text.startswith("/headers"):
                            target = raw_text.split()[1] if len(raw_text.split()) > 1 else ""
                            if target:
                                if not target.startswith("http"): target = "http://" + target
                                log(f"Fetching headers for: {target}", Y)
                                try:
                                    r = requests.get(target, timeout=10)
                                    h = r.headers
                                    info = f"📑 *Headers for:* `{target}`\n\n"
                                    info += f"🖥️ *Server:* `{h.get('Server', 'Unknown')}`\n"
                                    info += f"🛠️ *Powered-By:* `{h.get('X-Powered-By', 'N/A')}`\n"
                                    info += f"📦 *Content:* `{h.get('Content-Type', 'N/A')}`\n"
                                    send_msg(chat_id, info)
                                except: send_msg(chat_id, "❌ Could not fetch headers.")

                        elif raw_text.startswith("/scan"):
                            target = raw_text.split()[1] if len(raw_text.split()) > 1 else ""
                            if target:
                                try:
                                    ip = socket.gethostbyname(target)
                                    res = f"🌐 *Target:* `{target}`\n📍 *IP:* `{ip}`\n\n"
                                    for p in TOP_15_PORTS:
                                        s = socket.socket(); s.settimeout(0.7)
                                        if s.connect_ex((ip, p)) == 0:
                                            res += f"✅ `{p}`: {get_banner(ip, p)}\n"
                                        s.close()
                                    send_msg(chat_id, res)
                                except: send_msg(chat_id, "❌ Scan Error.")

                        elif raw_text.startswith("/whois"):
                            target = raw_text.split()[1] if len(raw_text.split()) > 1 else ""
                            if target:
                                try:
                                    r = requests.get(f"http://ip-api.com/json/{target}").json()
                                    send_msg(chat_id, f"📊 *Whois:* {target}\n🌍 *Country:* {r['country']}\n🏢 *ISP:* {r['isp']}")
                                except: send_msg(chat_id, "❌ Whois Error.")

                        elif raw_text.startswith("/brute"):
                            # (SSH brute logic remains the same as previous)
                            p = raw_text.split()
                            if len(p) > 2: send_msg(chat_id, "⚔️ Starting Brute Force... (Working in Background)")
        except: time.sleep(2)
        time.sleep(1)

if __name__ == "__main__": main()

