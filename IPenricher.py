import requests
import os
import threading
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv

load_dotenv()
#Getting keys from other file
VT_KEY = os.getenv("VT_API_KEY")
ABUSE_KEY = os.getenv("ABUSEIPDB_API_KEY")


def check_virustotal(ip): #VT lookup
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": VT_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": f"VT returned status {response.status_code}"}
    data = response.json()
    stats = data["data"]["attributes"]["last_analysis_stats"]
    return {
        "malicious":  stats.get("malicious",  0),
        "suspicious": stats.get("suspicious", 0),
        "harmless":   stats.get("harmless",   0),
        "undetected": stats.get("undetected", 0),
    }

def check_abuseipdb(ip):
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": ABUSE_KEY, "Accept": "application/json"}
    params = {"ipAddress": ip, "maxAgeInDays": 90}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return {"error": f"AbuseIPDB returned status {response.status_code}"}
    data = response.json()["data"]
    return {
        "abuse_score":   data.get("abuseConfidenceScore", 0),
        "total_reports": data.get("totalReports",         0),
        "country":       data.get("countryCode",    "Unknown"),
        "isp":           data.get("isp",            "Unknown"),
        "is_tor":        data.get("isTor",              False),
    }

def get_risk_verdict(vt_result, abuse_result):
    score = 0
    if vt_result.get("malicious", 0) >= 5:
        score += 50
    elif vt_result.get("malicious", 0) >= 1:
        score += 25
    if abuse_result.get("abuse_score", 0) >= 75:
        score += 40
    elif abuse_result.get("abuse_score", 0) >= 25:
        score += 20
    if abuse_result.get("is_tor"):
        score += 10
    if score >= 70:
        return "HIGH RISK"
    elif score >= 30:
        return "MEDIUM RISK"
    return "LOW RISK"

def enrich_ip_data(ip):
    vt    = check_virustotal(ip)
    abuse = check_abuseipdb(ip)
    return vt, abuse, get_risk_verdict(vt, abuse)

#Color Palette for the GUI
BG      = "#f4f6f9"   #Light grey canvas
SURFACE = "#ffffff"   #White card surface
BORDER  = "#d1d9e6"   #Soft dividers
TEXT    = "#1a1d26"   #Near-black text
MUTED   = "#6b7a99"   #Secondary labels
ACCENT  = "#2563eb"   #Blue highlight
GREEN   = "#16a34a"
YELLOW  = "#d97706"
RED     = "#dc2626"

VERDICT_PALETTE = {
    "HIGH RISK":   (RED,    "#fde8e8", "▲ HIGH RISK"),
    "MEDIUM RISK": (YELLOW, "#fef3cd", "◆ MEDIUM RISK"),
    "LOW RISK":    (GREEN,  "#dcfce7", "● LOW RISK"),
}


class IPEnricherApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("IP Enrichment Tool")
        self.root.geometry("680x560")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._build_ui()


    def _build_ui(self): #Creating Layout
        header = tk.Frame(self.root, bg=BG, pady=24)
        header.pack(fill="x", padx=28)

        tk.Label(
            header, text="I P   E N R I C H M E N T", bg=BG, fg=ACCENT,
            font=("Courier New", 18, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header, text="VirusTotal  ·  AbuseIPDB",
            bg=BG, fg=MUTED, font=("Courier New", 9),
        ).pack(anchor="w")

        tk.Frame(self.root, bg=ACCENT, height=1).pack(fill="x", padx=28) #Styling line

        input_outer = tk.Frame(self.root, bg=BG, pady=20) #Styling for input
        input_outer.pack(fill="x", padx=28)

        tk.Label(
            input_outer, text="TARGET IP", bg=BG, fg=MUTED,
            font=("Courier New", 8, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        row = tk.Frame(input_outer, bg=BG)
        row.pack(fill="x")

        self.ip_var = tk.StringVar()
        self.entry = tk.Entry(
            row, textvariable=self.ip_var,
            font=("Courier New", 13), bg=SURFACE, fg=ACCENT,
            insertbackground=ACCENT, relief="flat",
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=BORDER,
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 10))
        self.entry.bind("<Return>", lambda _: self._start_lookup())

        self.run_btn = tk.Button(
            row, text="ANALYZE", command=self._start_lookup,
            font=("Courier New", 10, "bold"), bg=ACCENT, fg="#ffffff",
            relief="flat", padx=18, pady=9, cursor="hand2",
            activebackground="#1d4ed8", activeforeground="#ffffff",
        )
        self.run_btn.pack(side="right")

        self.status_var = tk.StringVar(value="Enter an IP address above and press ANALYZE") #Status Bar
        tk.Label(
            self.root, textvariable=self.status_var,
            bg=BG, fg=MUTED, font=("Courier New", 8),
        ).pack(anchor="w", padx=28)

        self.results_area = tk.Frame(self.root, bg=BG) #For Results
        self.results_area.pack(fill="both", expand=True, padx=28, pady=16)

        self._show_placeholder()


    def _clear_results(self):
        for w in self.results_area.winfo_children():
            w.destroy()

    def _show_placeholder(self):
        self._clear_results()
        tk.Label(
            self.results_area, text="[ awaiting target ]",
            bg=BG, fg=BORDER, font=("Courier New", 11),
        ).pack(expand=True)

    def _show_loading(self, ip):
        self._clear_results()
        tk.Label(
            self.results_area,
            text=f"querying threat intel for {ip} ...",
            bg=BG, fg=MUTED, font=("Courier New", 10),
        ).pack(expand=True)

    def _show_error(self, msg):
        self._clear_results()
        tk.Label(
            self.results_area, text=f"ERROR: {msg}",
            bg=BG, fg=RED, font=("Courier New", 10), wraplength=600,
        ).pack(expand=True)
        self._reset_btn()
        self.status_var.set("An error occurred.")

    def _reset_btn(self):
        self.run_btn.config(state="normal", text="ANALYZE")


    def _start_lookup(self): #Logic for looking up IP
        ip = self.ip_var.get().strip()
        if not ip:
            messagebox.showwarning("Missing Input", "Please enter an IP address.")
            return
        self.run_btn.config(state="disabled", text="WORKING…")
        self.status_var.set(f"Querying APIs for {ip} …")
        self._show_loading(ip)
        threading.Thread(target=self._lookup_thread, args=(ip,), daemon=True).start()

    def _lookup_thread(self, ip):
        try:
            vt, abuse, verdict = enrich_ip_data(ip)
            self.root.after(0, self._show_results, ip, vt, abuse, verdict)
        except Exception as exc:
            self.root.after(0, self._show_error, str(exc))


    def _show_results(self, ip, vt, abuse, verdict): #Preparing to output results
        self._clear_results()

        fg_v, bg_v, label_v = VERDICT_PALETTE.get(
            verdict, (ACCENT, SURFACE, verdict)
        )

        banner = tk.Frame(self.results_area, bg=bg_v, pady=10) #Showing results
        banner.pack(fill="x", pady=(0, 12))

        tk.Label(
            banner, text=label_v,
            bg=bg_v, fg=fg_v, font=("Courier New", 14, "bold"),
        ).pack(side="left", padx=16)
        tk.Label(
            banner, text=ip,
            bg=bg_v, fg=fg_v, font=("Courier New", 14),
        ).pack(side="right", padx=16)

        cols = tk.Frame(self.results_area, bg=BG) #Collums for results
        cols.pack(fill="both", expand=True)

        self._vt_card(cols, vt)
        self._abuse_card(cols, abuse)

        self.status_var.set(f"Analysis complete  —  {ip}")
        self._reset_btn()

    def _vt_card(self, parent, vt):
        card = tk.Frame(parent, bg=SURFACE, padx=16, pady=14,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self._card_title(card, "VIRUSTOTAL", "#7c6fff")

        mal = vt.get("malicious", 0)
        rows = [
            ("MALICIOUS",  str(mal),                  RED if int(mal or 0) > 0 else GREEN),
            ("SUSPICIOUS", str(vt.get("suspicious", "N/A")), YELLOW),
            ("CLEAN",      str(vt.get("harmless",   "N/A")), TEXT),
            ("UNDETECTED", str(vt.get("undetected", "N/A")), MUTED),
        ]
        for label, value, color in rows:
            self._data_row(card, label, value, color)

    def _abuse_card(self, parent, abuse):
        card = tk.Frame(parent, bg=SURFACE, padx=16, pady=14,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(side="right", fill="both", expand=True, padx=(6, 0))

        self._card_title(card, "ABUSEIPDB", ACCENT)

        score = abuse.get("abuse_score", 0)
        score_color = RED if score >= 75 else YELLOW if score >= 25 else GREEN
        tor_val   = "YES" if abuse.get("is_tor") else "NO"
        tor_color = RED if abuse.get("is_tor") else GREEN

        rows = [
            ("ABUSE SCORE",  f"{score}/100",                       score_color),
            ("REPORTS",      str(abuse.get("total_reports", "N/A")), TEXT),
            ("COUNTRY",      abuse.get("country", "N/A"),            TEXT),
            ("ISP",          abuse.get("isp",     "N/A"),            MUTED),
            ("TOR NODE",     tor_val,                                tor_color),
        ]
        for label, value, color in rows:
            self._data_row(card, label, value, color)


    @staticmethod
    def _card_title(parent, text, color):
        tk.Label(
            parent, text=text,
            bg=SURFACE, fg=color, font=("Courier New", 10, "bold"),
        ).pack(anchor="w", pady=(0, 8))
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=(0, 8))

    @staticmethod
    def _data_row(parent, label, value, value_color):
        row = tk.Frame(parent, bg=SURFACE)
        row.pack(fill="x", pady=3)
        tk.Label(
            row, text=label, bg=SURFACE, fg=MUTED,
            font=("Courier New", 8), width=13, anchor="w",
        ).pack(side="left")
        tk.Label(
            row, text=value, bg=SURFACE, fg=value_color,
            font=("Courier New", 9, "bold"), anchor="e",
        ).pack(side="right")


def cli_enrich(ip): #Checking IP
    print(f"\n{'='*50}")
    print(f"  IP Enrichment Report: {ip}")
    print(f"{'='*50}")
    print("\n[*] Querying VirusTotal...")
    vt    = check_virustotal(ip)
    print("[*] Querying AbuseIPDB...")
    abuse = check_abuseipdb(ip)
    verdict = get_risk_verdict(vt, abuse)
    print(f"\n  VERDICT: {verdict}")
    print(f"\n  VirusTotal:")
    print(f"    Malicious detections : {vt.get('malicious', 'N/A')}")
    print(f"    Suspicious           : {vt.get('suspicious', 'N/A')}")
    print(f"    Clean                : {vt.get('harmless', 'N/A')}")
    print(f"\n  AbuseIPDB:")
    print(f"    Abuse score          : {abuse.get('abuse_score', 'N/A')}/100")
    print(f"    Total reports        : {abuse.get('total_reports', 'N/A')}")
    print(f"    Country              : {abuse.get('country', 'N/A')}")
    print(f"    ISP                  : {abuse.get('isp', 'N/A')}")
    print(f"    Tor exit node        : {abuse.get('is_tor', 'N/A')}")
    print(f"\n{'='*50}\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cli_enrich(sys.argv[1]) 
    else:
        root = tk.Tk()
        IPEnricherApp(root)
        root.mainloop() #Used to Open GUI
