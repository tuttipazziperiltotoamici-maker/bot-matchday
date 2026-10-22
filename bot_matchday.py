import os
import sys
import traceback
import collections
import types

# --- FIX COMPATIBILITÀ PYTHON 3.13 ---
imghdr_mock = types.ModuleType('imghdr')
imghdr_mock.what = lambda file, h=None: None
sys.modules['imghdr'] = imghdr_mock
# --- FIX COMPATIBILITÀ ---
if not hasattr(collections, 'Iterable'):
    import collections.abc
    collections.Iterable = collections.abc.Iterable

# --- SISTEMA DI SICUREZZA ---
def mostra_errore_e_ferma(exctype, value, tb):
    print("\n" + "="*50)
    print("⚠️ ERRORE RILEVATO:")
    traceback.print_exception(exctype, value, tb)
    print("="*50)
    print(f"\nPython Path: {sys.executable}") # Ti dice quale Python sta girando
    input("\nPremi INVIO per chiudere...")

sys.excepthook = mostra_errore_e_ferma

# --- VERIFICA LIBRERIE ---
try:
    import pandas as pd
    from PIL import Image, ImageDraw, ImageFont
    from telegram import Update
    from telegram.ext import Updater, CommandHandler, CallbackContext
except ImportError as e:
    print(f"\n❌ ERRORE: Libreria mancante -> {e}")
    print(f"Stai usando questo Python: {sys.executable}")
    print("\nPROVA A LANCIARE IL BOT COSI':")
    print(f"python \"{sys.argv[0]}\"")
    input("\nPremi INVIO per uscire...")
    sys.exit()

# --- CONFIGURAZIONE ---
TOKEN = "7428488218:AAFbB23pcyg4C2vW0eR_qm37a-AM4J_L_2c"  # <--- METTI IL TUO TOKEN
CSV_PATH = "https://docs.google.com/spreadsheets/d/1z0-LJFIhUeVx6bOxnAMsmMJi1VSTcWpgOshy0_Ohx80/export?format=csv&gid=2090560117"
LOGHI_DIR = "loghi"
FONT_PATH = "arialbd.ttf"
OUTPUT_DIR = "output_match"

# Crea cartelle
for folder in [OUTPUT_DIR, LOGHI_DIR]:
    if not os.path.exists(folder): os.makedirs(folder)

def crea_immagine_singola(row, index):
    W, H = 1220, 368
    img = Image.new("RGBA", (W, H), color="white")
    draw = ImageDraw.Draw(img)

    try:
        font_squadra = ImageFont.truetype(FONT_PATH, size=38)
        font_dati = ImageFont.truetype(FONT_PATH, size=35)
    except:
        font_squadra = font_dati = ImageFont.load_default()

    casa = str(row['squadra_casa']).strip().upper()
    trasf = str(row['squadra_trasferta']).strip().upper()
    data = str(row['data']).strip().upper()
    ora = str(row['ora']).strip()

    # Loghi
    def incolla_logo(nome, cx):
        for ext in [".png", ".PNG"]:
            p = os.path.join(LOGHI_DIR, f"{nome}{ext}")
            if os.path.exists(p):
                l = Image.open(p).convert("RGBA").resize((180, 180))
                img.paste(l, (cx - 90, 50), l)
                return True
        return False

    incolla_logo(casa, 250)
    incolla_logo(trasf, 970)

    # Testi
    draw.text((250, 240), casa, font=font_squadra, fill="black", anchor="mt")
    draw.text((970, 240), trasf, font=font_squadra, fill="black", anchor="mt")
    draw.text((610, 100), data, font=font_dati, fill="#333333", anchor="mm")

    # Rettangolo Ora
    draw.rounded_rectangle([530, 180, 690, 240], radius=12, fill="#007bff")
    draw.text((610, 210), ora, font=font_dati, fill="white", anchor="mm")

    path_salv = os.path.join(OUTPUT_DIR, f"match_{index}.png")
    img.save(path_salv)
    return path_salv

def genera(update: Update, context: CallbackContext):
    update.message.reply_text("⏳ Generazione immagini...")
    try:
        df = pd.read_csv(CSV_PATH)
        for index, row in df.iterrows():
            f_path = crea_immagine_singola(row, index)
            with open(f_path, "rb") as p:
                update.message.reply_photo(photo=p)
        update.message.reply_text("✅ Operazione completata!")
    except Exception as e:
        update.message.reply_text(f"❌ Errore: {e}")

def main():
    print("--- TOTOAMICI BOT ---")
    if TOKEN == "_" or TOKEN == "":
        print("❌ MANCA IL TOKEN!")
        input("Premi INVIO...")
        return

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("genera", genera))

    print("🚀 BOT ONLINE! Scrivi /genera su Telegram.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
