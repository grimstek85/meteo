import tkinter as tk
from tkinter import messagebox
import urllib.request, json, threading, datetime

BG = "#15171a"
CARD = "#202328"
TEXT = "#f5f7fa"
MUTED = "#aeb6c2"
ACCENT = "#6db3ff"

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "WindowsWeatherWidget/1.0"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read().decode("utf-8"))

def weather_label(code):
    codes = {
        0: ("Ciel dégagé", "☀️"),
        1: ("Principalement dégagé", "🌤️"),
        2: ("Partiellement nuageux", "⛅"),
        3: ("Couvert", "☁️"),
        45: ("Brouillard", "🌫️"), 48: ("Brouillard givrant", "🌫️"),
        51: ("Bruine légère", "🌦️"), 53: ("Bruine", "🌦️"), 55: ("Forte bruine", "🌧️"),
        61: ("Pluie légère", "🌦️"), 63: ("Pluie", "🌧️"), 65: ("Forte pluie", "🌧️"),
        71: ("Neige légère", "🌨️"), 73: ("Neige", "❄️"), 75: ("Forte neige", "❄️"),
        80: ("Averses légères", "🌦️"), 81: ("Averses", "🌧️"), 82: ("Fortes averses", "⛈️"),
        95: ("Orage", "⛈️"), 96: ("Orage avec grêle", "⛈️"), 99: ("Orage avec grêle", "⛈️")
    }
    return codes.get(code, ("Conditions météo", "🌡️"))

def locate_and_weather():
    try:
        loc = get_json("https://ipapi.co/json/")
        lat, lon = loc["latitude"], loc["longitude"]
        city = loc.get("city") or loc.get("region") or "Localisation"
        country = loc.get("country_name", "")
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
            "precipitation,weather_code,wind_speed_10m"
            "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
            "&timezone=auto&forecast_days=5"
        )
        return city, country, get_json(url)
    except Exception as e:
        raise RuntimeError("Impossible de récupérer la météo. Vérifie ta connexion Internet.") from e

class WeatherWidget(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Météo locale")
        self.geometry("360x500")
        self.minsize(320, 440)
        self.configure(bg=BG)
        self.attributes("-topmost", True)
        self.resizable(False, False)

        self.header = tk.Frame(self, bg=BG)
        self.header.pack(fill="x", padx=18, pady=(15, 5))
        self.title_lbl = tk.Label(self.header, text="MÉTÉO LOCALE", font=("Segoe UI", 11, "bold"),
                                  bg=BG, fg=MUTED)
        self.title_lbl.pack(side="left")
        self.refresh_btn = tk.Button(self.header, text="↻", command=self.refresh,
                                     font=("Segoe UI", 16), bg=BG, fg=TEXT,
                                     activebackground=BG, activeforeground=ACCENT,
                                     bd=0, relief="flat", cursor="hand2")
        self.refresh_btn.pack(side="right")

        self.city_lbl = tk.Label(self, text="Recherche de votre position…", font=("Segoe UI", 17, "bold"),
                                 bg=BG, fg=TEXT)
        self.city_lbl.pack(pady=(10, 0))

        self.temp_lbl = tk.Label(self, text="--°", font=("Segoe UI", 52, "bold"),
                                 bg=BG, fg=TEXT)
        self.temp_lbl.pack()

        self.condition_lbl = tk.Label(self, text="Chargement…", font=("Segoe UI", 13),
                                      bg=BG, fg=MUTED)
        self.condition_lbl.pack(pady=(0, 12))

        self.info = tk.Frame(self, bg=CARD)
        self.info.pack(fill="x", padx=18, pady=4)
        self.info_labels = []
        for title in ["Ressenti", "Humidité", "Vent", "Pluie"]:
            f = tk.Frame(self.info, bg=CARD)
            f.pack(fill="x", padx=14, pady=7)
            a = tk.Label(f, text=title, font=("Segoe UI", 10), bg=CARD, fg=MUTED)
            a.pack(side="left")
            b = tk.Label(f, text="--", font=("Segoe UI", 10, "bold"), bg=CARD, fg=TEXT)
            b.pack(side="right")
            self.info_labels.append(b)

        tk.Label(self, text="PRÉVISIONS", font=("Segoe UI", 10, "bold"),
                 bg=BG, fg=MUTED).pack(anchor="w", padx=18, pady=(15, 6))

        self.forecast = tk.Frame(self, bg=BG)
        self.forecast.pack(fill="x", padx=18)

        self.status = tk.Label(self, text="Mise à jour automatique toutes les 15 min",
                               font=("Segoe UI", 8), bg=BG, fg=MUTED)
        self.status.pack(pady=(10, 8))

        self.refresh()
        self.after(900000, self.refresh)

    def refresh(self):
        self.refresh_btn.config(state="disabled")
        self.status.config(text="Mise à jour…")
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            city, country, data = locate_and_weather()
            self.after(0, lambda: self.update_ui(city, country, data))
        except Exception as e:
            self.after(0, lambda: self.show_error(str(e)))

    def update_ui(self, city, country, data):
        c = data["current"]
        label, icon = weather_label(c["weather_code"])
        self.city_lbl.config(text=f"📍 {city}" + (f", {country}" if country else ""))
        self.temp_lbl.config(text=f"{round(c['temperature_2m'])}°")
        self.condition_lbl.config(text=f"{icon}  {label}")
        vals = [
            f"{round(c['apparent_temperature'])}°C",
            f"{c['relative_humidity_2m']} %",
            f"{round(c['wind_speed_10m'])} km/h",
            f"{c['precipitation']} mm"
        ]
        for lbl, val in zip(self.info_labels, vals):
            lbl.config(text=val)

        for w in self.forecast.winfo_children():
            w.destroy()

        days = data["daily"]
        names = ["Aujourd’hui", "Demain"]
        for i in range(2, 5):
            try:
                d = datetime.date.fromisoformat(days["time"][i])
                names.append(["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"][d.weekday()])
            except:
                names.append("Jour")

        for i in range(5):
            card = tk.Frame(self.forecast, bg=CARD)
            card.pack(fill="x", pady=3)
            tk.Label(card, text=names[i], width=11, anchor="w", bg=CARD, fg=TEXT,
                     font=("Segoe UI", 9, "bold")).pack(side="left", padx=8, pady=6)
            lab, ic = weather_label(days["weather_code"][i])
            tk.Label(card, text=ic, bg=CARD, fg=TEXT, font=("Segoe UI", 12)).pack(side="left")
            tk.Label(card, text=f"{round(days['temperature_2m_max'][i])}° / {round(days['temperature_2m_min'][i])}°",
                     bg=CARD, fg=TEXT, font=("Segoe UI", 9)).pack(side="right", padx=8)
        self.refresh_btn.config(state="normal")
        now = datetime.datetime.now().strftime("%H:%M")
        self.status.config(text=f"Dernière mise à jour : {now} • actualisation 15 min")

    def show_error(self, msg):
        self.refresh_btn.config(state="normal")
        self.status.config(text="Erreur de connexion")
        messagebox.showerror("Météo locale", msg)

if __name__ == "__main__":
    WeatherWidget().mainloop()
