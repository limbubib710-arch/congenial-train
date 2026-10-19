#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║   OSINT-MASTER v1.0 — All-in-One Tool    ║
║   For Authorized Research / Termux       ║
╚══════════════════════════════════════════╝
"""

import os, sys, re, json, time, socket, subprocess
import requests
from colorama import Fore, Style, init
from prettytable import PrettyTable

init(autoreset=True)

# ═══════════════════════ COLORS ═══════════════════════
R = Fore.RED; G = Fore.GREEN; Y = Fore.YELLOW
C = Fore.CYAN; M = Fore.MAGENTA; W = Fore.WHITE; B = Fore.BLUE
BR = Style.BRIGHT; FR = Style.RESET_ALL

def slow_print(text, delay=0.005):
    for ch in text:
        sys.stdout.write(ch); sys.stdout.flush(); time.sleep(delay)
    print()

def banner():
    os.system("clear")
    print(f"""{BR}{M}
   ██████╗ ███████╗██╗███╗   ██╗████████╗
  ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝
  ██║   ██║███████╗██║██╔██╗ ██║   ██║
  ██║   ██║╚════██║██║██║╚██╗██║   ██║
  ╚██████╔╝███████║██║██║ ╚████║   ██║
   ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝{FR}
{BR}{C}  ════════ ALL-IN-ONE OSINT TOOL v1.0 ════════{FR}
{Y}   [ Advanced Open-Source Intelligence Suite ]{FR}
""")

def line():
    print(f"{C}{'─'*50}{FR}")

def info(msg):  print(f"{G}[+]{W} {msg}{FR}")
def warn(msg):  print(f"{Y}[!]{W} {msg}{FR}")
def err(msg):   print(f"{R}[x]{W} {msg}{FR}")
def ask(msg):   return input(f"{C}[?]{W} {msg}{FR}")

# ═══════════════════════ MODULES ═══════════════════════

def ip_lookup():
    ip = ask("Enter IP address (blank = your IP): ").strip()
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        d = requests.get(url, timeout=10).json()
        if d.get("status") != "success":
            return err("Lookup failed: " + str(d.get("message")))
        t = PrettyTable()
        t.field_names = [f"{C}Field{FR}", f"{C}Value{FR}"]
        for k, v in d.items():
            t.add_row([k, v])
        print(t)
    except Exception as e:
        err(f"Error: {e}")

def ip_port_scan():
    ip = ask("Target IP/Host: ").strip()
    ports_in = ask("Ports (e.g. 21,22,80,443 or 1-1000): ").strip()
    ports = set()
    for p in ports_in.split(","):
        if "-" in p:
            a, b = p.split("-"); ports.update(range(int(a), int(b)+1))
        elif p.isdigit(): ports.add(int(p))
    info(f"Scanning {ip} ({len(ports)} ports)...")
    open_ports = []
    for port in sorted(ports):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.8)
        if s.connect_ex((ip, port)) == 0:
            try:
                s.send(b"HEAD / HTTP/1.1\r\n\r\n")
                banner_ = s.recv(256).decode(errors="ignore").split("\n")[0]
            except Exception:
                banner_ = "?"
            print(f"  {G}[OPEN]{W} {port:<6} {banner_}")
            open_ports.append(port)
        s.close()
    info(f"Done. Open: {open_ports if open_ports else 'none'}")

def username_hunt():
    user = ask("Username to search: ").strip()
    sites = {
        "GitHub":      f"https://github.com/{user}",
        "Twitter/X":   f"https://x.com/{user}",
        "Instagram":   f"https://instagram.com/{user}",
        "Reddit":      f"https://reddit.com/user/{user}",
        "TikTok":      f"https://tiktok.com/@{user}",
        "Facebook":    f"https://facebook.com/{user}",
        "YouTube":     f"https://youtube.com/@{user}",
        "Pinterest":   f"https://pinterest.com/{user}",
        "Twitch":      f"https://twitch.tv/{user}",
        "Steam":       f"https://steamcommunity.com/id/{user}",
        "GitLab":      f"https://gitlab.com/{user}",
        "Medium":      f"https://medium.com/@{user}",
        "Spotify":     f"https://open.spotify.com/user/{user}",
        "SoundCloud":  f"https://soundcloud.com/{user}",
        "Telegram":    f"https://t.me/{user}",
    }
    hdr = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    t = PrettyTable(); t.field_names = [f"{C}Platform{FR}", f"{C}Status{FR}", f"{C}URL{FR}"]
    for name, url in sites.items():
        try:
            r = requests.get(url, headers=hdr, timeout=8, allow_redirects=False)
            found = r.status_code in (200, 405)  # IG blocks bots with 405 sometimes
            status = f"{G}FOUND{FR}" if found else f"{R}NOT FOUND{FR}"
        except Exception:
            status = f"{Y}ERROR{FR}"
        t.add_row([name, status, url])
    print(t)

def email_breach():
    email = ask("Email to check (HIBP): ").strip()
    try:
        r = requests.get(f"https://api.hibp-api.com"? if False else f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=true",
                         timeout=10)
        if r.status_code == 200:
            warn("BREACHED! Found in these breaches:")
            for b in r.json():
                print(f"  {R}•{W} {b['Name']}")
        elif r.status_code == 404:
            info("No breaches found for this email (or rate-limited).")
        else:
            err(f"HTTP {r.status_code} — HIBP API now requires a key; trying alternates...")
            r2 = requests.get(f"https://api.mailmetrix.net/check/{email}", timeout=10)
            print(r2.text[:500])
    except Exception as e:
        err(f"Error: {e}")
    info("Tip: also try https://www.dehashed.com & intelx.io manually.")

def phone_lookup():
    num = ask("Phone number with country code (e.g. +97798XXXXXXXX): ").strip()
    try:
        r = requests.get(f"http://ip-api.com/json/?q={num}")  # not valid — use numverify
    except Exception:
        pass
    # Use numverify-style via public endpoint fallback
    try:
        r = requests.get(f"https://api.phonevalidators.com/v1/{num}", timeout=8)
        print(r.text)
    except Exception:
        pass
    # Offline country/cARRIER heuristic via phonenumbers lib if installed
    try:
        import phonenumbers
        from phonenumbers import geocoder, carrier, timezone
        p = phonenumbers.parse(num)
        print(f"  {G}Valid:{W} {phonenumbers.is_valid_number(p)}")
        print(f"  {G}Country:{W} {geocoder.description_for_number(p, 'en')}")
        print(f"  {G}Carrier:{W} {carrier.name_for_number(p, 'en')}")
        print(f"  {G}Timezone:{W} {timezone.time_zones_for_number(p)}")
    except ImportError:
        err("Install extra: pip install phonenumbers")

def domain_recon():
    dom = ask("Domain (e.g. example.com): ").strip()
    line()
    try:
        info("DNS records (via dig/system):")
        for rtype in ("A", "MX", "NS", "TXT"):
            try:
                out = subprocess.run(["getent", "hosts" if rtype=="A" else "hosts", dom],
                                     capture_output=True, text=True, timeout=5)
            except Exception:
                pass
        # DNS via socket (Termux-friendly, no dnspython needed)
        try:
            ips = socket.gethostbyname_ex(dom)
            print(f"  {G}A records:{W} {ips[2]}")
        except Exception as e:
            err(f"DNS fail: {e}")
        # crt.sh subdomain discovery
        info("Subdomains via crt.sh:")
        try:
            r = requests.get(f"https://crt.sh/?q=%25.{dom}&output=json", timeout=20)
            subs = sorted({s["name_value"].lstrip("*.") for s in r.json()})
            for s in subs[:40]:
                print(f"  {C}->{W} {s}")
            print(f"  {Y}... total {len(subs)}{FR}")
        except Exception as e:
            err(f"crt.sh fail: {e}")
        # WHOIS via curl (whois pkg in Termux: pkg install whois)
        out = subprocess.run(["whois", dom], capture_output=True, text=True)
        if out.returncode == 0:
            keep = [l for l in out.stdout.splitlines() if re.match(r"(Domain Name|Registrar|Creation|Expiry|Name Server|Registrant)", l)]
            if keep:
                info("WHOIS (key lines):")
                for l in keep: print(f"  {W}{l}")
    except Exception as e:
        err(f"Error: {e}")

def exif_extractor():
    path = ask("Path to image: ").strip()
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS
        img = Image.open(path)
        exif = img._getexif() or {}
        gps = {}
        for tag_id, val in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for k, v in val.items():
                    gps[GPSTAGS.get(k, k)] = v
            else:
                print(f"  {G}{tag}:{W} {val}")
        if gps:
            warn("GPS data found! Decoding:")
            lat = gps.get("GPSLatitude"); lon = gps.get("GPSLongitude")
            if lat and lon:
                la = float(lat[0]) + float(lat[1])/60 + float(lat[2])/3600
                lo = float(lon[0]) + float(lon[1])/60 + float(lon[2])/3600
                if gps.get("GPSLatitudeRef") == "S": la = -la
                if gps.get("GPSLongitudeRef") == "W": lo = -lo
                print(f"  {M}Maps: https://maps.google.com/?q={la},{lo}{FR}")
        else:
            info("No EXIF/GPS data.")
    except ImportError:
        err("Install: pip install Pillow")

def github_recon():
    user = ask("GitHub username: ").strip()
    try:
        r = requests.get(f"https://api.github.com/users/{user}", timeout=10).json()
        t = PrettyTable(); t.field_names = [f"{C}Field{FR}", f"{C}Value{FR}"]
        for k in ("login","name","company","blog","location","email","bio",
                  "public_repos","followers","following","created_at"):
            t.add_row([k, r.get(k)])
        print(t)
        info("Repositories:")
        repos = requests.get(f"https://api.github.com/users/{user}/repos?per_page=100", timeout=10).json()
        for repo in repos:
            print(f"  {C}-{W} {repo['name']} ({Y}{repo['language']}{W}) stars:{repo['stargazers_count']}")
    except Exception as e:
        err(f"Error: {e}")

def google_dork():
    q = ask("Dork query (e.g. site:example.com inurl:admin): ").strip()
    webbrowser_dorks = [
        f"https://www.google.com/search?q={q}",
        f"https://www.bing.com/search?q={q}",
        f"https://search.marcia.com/?q={q}",
        f"https://www.shodan.io/search?query={q}",
        f"https://censys.io/search?q={q}",
    ]
    info("Opening dork engines (termux-open-url):")
    for url in webbrowser_dorks[:2]:
        print(f"  {C}{url}{FR}")
    subprocess.run(["termux-open-url", webbrowser_dorks[0]], capture_output=True)

def paste_search():
    q = ask("Search pastes for keyword: ").strip()
    try:
        info("Searching psbdmp.ws (paste dumps)...")
        r = requests.get(f"https://psbdmp.ws/api/search/{q}", timeout=15).json()
        ids = r.get("data", [])[:10] if isinstance(r, dict) else r[:10]
        for i in ids:
            pid = i["id"] if isinstance(i, dict) else i
            print(f"  {C}https://pastebin.com/raw/{pid}{FR}")
    except Exception as e:
        err(f"Error: {e}")

def metadata_scraper():
    url = ask("Website URL: ").strip()
    hdr = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=hdr, timeout=12)
        html = r.text
        emails = set(re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", html))
        socials = re.findall(r"https?://(?:www\.)?(twitter|x|instagram|facebook|linkedin|github|t)\.com/[\w\./-]+", html)
        phones = re.findall(r"\+?\d[\d\s\-\(\)]{8,}\d", html)
        warn("Emails found:")
        for e in emails: print(f"  {G}•{W} {e}")
        warn("Social links:")
        for s in set(socials): print(f"  {G}•{W} {s}")
        warn("Possible phone numbers:")
        for p in set(phones)[:10] if isinstance(phones, list) else []:
            print(f"  {G}•{W} {p}")
    except Exception as e:
        err(f"Error: {e}")

def termux_intel():
    warn("Local device info (self-recon):")
    cmds = {
        "IP (wifi)": "ifconfig 2>/dev/null || ip addr show",
        "Public IP": "curl -s ifconfig.me",
        "Battery": "termux-battery-status 2>/dev/null",
    }
    for name, cmd in cmds.items():
        out = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"  {G}{name}:{W} {out.stdout.strip()[:200]}")

# ═══════════════════════ MENU ═══════════════════════
MENU = f"""
{BR}{C}  ┌──────────────────────────────────────────┐{FR}
{BR}{C}  │{W}  [1]  IP Address Lookup                  {C}│
{BR}{C}  │{W}  [2]  Port Scanner + Banner Grab         {C}│
{BR}{C}  │{W}  [3]  Username Hunt (15 platforms)       {C}│
{BR}{C}  │{W}  [4]  Email Breach Check (HIBP)          {C}│
{BR}{C}  │{W}  [5]  Phone Number Lookup                {C}│
{BR}{C}  │{W}  [6]  Domain Recon (DNS+Subs+WHOIS)      {C}│
{BR}{C}  │{W}  [7]  EXIF / GPS Image Extractor         {C}│
{BR}{C}  │{W}  [8]  GitHub OSINT Recon                 {C}│
{BR}{C}  │{W}  [9]  Google Dork Launcher               {C}│
{BR}{C}  │{W}  [10] Paste Site Search                 {C}│
{BR}{C}  │{W}  [11] Website Metadata Scraper          {C}│
{BR}{C}  │{W}  [12] Device Self-Intel (Termux)        {C}│
{BR}{C}  │{W}  [0]  Exit                              {C}│
{BR}{C}  └──────────────────────────────────────────┘{FR}
"""

MODULES = {
    "1": ip_lookup, "2": ip_port_scan, "3": username_hunt,
    "4": email_breach, "5": phone_lookup, "6": domain_recon,
    "7": exif_extractor, "8": github_recon, "9": google_dork,
    "10": paste_search, "11": metadata_scraper, "12": termux_intel,
}

def main():
    banner()
    slow_print(f"{G}[*] Initializing OSINT-MASTER...{FR}")
    time.sleep(0.5)
    while True:
        print(MENU)
        choice = ask("Select module: ").strip()
        if choice == "0":
            print(f"{M}[*] Stay ethical. Goodbye!{FR}")
            sys.exit(0)
        if choice in MODULES:
            line()
            MODULES[choice]()
            line()
        else:
            err("Invalid option.")
        input(f"{Y}[enter to continue]{FR}")
        banner()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}[x] Interrupted. Bye.{FR}")