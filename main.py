import os

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Yangi tokenni (BotFather /revoke dan keyin) shu yerga qo'ying
# yoki BOT_TOKEN nomli environment variable orqali bering.
TOKEN = os.getenv("BOT_TOKEN", "8927119060:AAHg5JFVE67Vlaab0cW1xHQTd_fkhJmFKzs")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "6179245247")

vrachlar_bazasi = [
    {"id": 1, "ism": "Dr. Umarov Alisher", "mutaxassislik": "Kardiolog", "narxi": "150 000 so'm", "bosh_vaqtlar": ["09:00", "10:00", "11:00"]},
    {"id": 2, "ism": "Dr. Karimova Madina", "mutaxassislik": "Stomatolog", "narxi": "200 000 so'm", "bosh_vaqtlar": ["14:00", "15:30", "16:45"]},
    {"id": 3, "ism": "Dr. Aliyev Hasan", "mutaxassislik": "Pediatr", "narxi": "120 000 so'm", "bosh_vaqtlar": ["10:30", "11:30"]},
]

navbatlar_bazasi = []


class NavbatYaratish(BaseModel):
    vrach_id: int
    bemor_ismi: str
    tanlangan_vaqt: str


def telegram_xabar_yuborish(matn: str):
    # To'g'ri URL: https://api.telegram.org/bot<TOKEN>/sendMessage
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": matn,
        "parse_mode": "Markdown",
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print("Telegram javobi:", response.text)
    except Exception as e:
        print(f"Telegramga yuborishda xatolik: {e}")


@app.get("/", response_class=HTMLResponse)
def asosiy_sahifa():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h2 style='color:red; text-align:center;'>'index.html' fayli topilmadi!</h2>"


@app.get("/vrachlar")
def vrachlarni_korish():
    return vrachlar_bazasi


@app.get("/navbatlar")
def navbatlarni_korish():
    return navbatlar_bazasi


@app.post("/ochrat-olish")
def ochrat_olish(data: NavbatYaratish):
    vrach = next((v for v in vrachlar_bazasi if v["id"] == data.vrach_id), None)
    if not vrach:
        raise HTTPException(status_code=404, detail="Bunday shifokor topilmadi!")
    if data.tanlangan_vaqt not in vrach["bosh_vaqtlar"]:
        raise HTTPException(status_code=400, detail="Bu vaqt band yoki mavjud emas!")

    vrach["bosh_vaqtlar"].remove(data.tanlangan_vaqt)

    yangi_navbat = {
        "navbat_id": len(navbatlar_bazasi) + 1,
        "vrach_ismi": vrach["ism"],
        "mutaxassislik": vrach["mutaxassislik"],
        "bemor_ismi": data.bemor_ismi,
        "vaqt": data.tanlangan_vaqt,
        "xizmat_haqqi": vrach["narxi"],
    }
    navbatlar_bazasi.append(yangi_navbat)

    xabar_matni = (
        "🔔 *Yangi onlayn navbat olindi!*\n\n"
        f"🆔 *Kvitansiya:* #{yangi_navbat['navbat_id']}\n"
        f"👤 *Bemor:* {yangi_navbat['bemor_ismi']}\n"
        f"👨‍⚕️ *Shifokor:* {yangi_navbat['vrach_ismi']}\n"
        f"📅 *Vaqt:* {yangi_navbat['vaqt']}\n"
        f"💰 *Narxi:* {yangi_navbat['xizmat_haqqi']}\n"
    )
    telegram_xabar_yuborish(xabar_matni)

    return {"xabar": "Navbat muvaffaqiyatli band qilindi!", "batafsil_malumot": yangi_navbat}