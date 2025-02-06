from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime, timedelta
import random
import os
import qrcode

# Folder do zapisu faktur
OUTPUT_DIR = "faktury"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# register font coding utf-8
pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

LOGO_PATH = "logo.png"

# Dane sprzedawcy i nabywcy
SPRZEDAWCA = {
    "nazwa": "Firma XYZ Sp. z o.o.",
    "adres": "ul. Przykładowa 1, 00-001 Warszawa",
    "nip": "123-456-78-90",
    "konto": f"PL{random.randint(10**25, 10**26 - 1)}"
}

NABYWCA = {
    "nazwa": "Klient ABC S.A.",
    "adres": "ul. Kupiecka 5, 00-002 Kraków",
    "nip": "987-654-32-10"
}

# Lista produktów
PRODUKTY = [
    ("Usługa konsultingowa", 1000, 23),
    ("Licencja na oprogramowanie", 2500, 23),
    ("Szkolenie online", 500, 23),
    ("Serwis IT", 700, 8),
    ("Hosting strony", 300, 23),
    ("Projekt graficzny", 1200, 8),
    ("Druk materiałów reklamowych", 400, 23),
    ("Doradztwo podatkowe", 1500, 8),
    ("Sprzęt komputerowy", 3500, 23),
    ("Abonament miesięczny", 100, 5),
    ("Opłata za domenę", 150, 23)
]

def generuj_qr(numer_faktury, kwota, konto):
    """Generuje kod QR z danymi przelewu."""
    dane_przelewu = f"PL|{konto}|{kwota}|{numer_faktury}|Firma XYZ Sp. z o.o."
    qr = qrcode.make(dane_przelewu)
    qr_path = os.path.join(OUTPUT_DIR, f"qr_{numer_faktury}.png")
    qr.save(qr_path)
    return qr_path

def generuj_fakture():
    numer_faktury = f"FV-{random.randint(1000, 99999)}_{datetime.now().month}_{datetime.now().year}"
    data_wystawienia = datetime.now().strftime("%Y-%m-%d")
    termin_platnosci = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

    # Status faktury (losowy)
    status_faktury = random.choice(["Opłacona", "Do zapłaty"])

    plik_faktury = os.path.join(OUTPUT_DIR, f"{numer_faktury}.pdf")
    c = canvas.Canvas(plik_faktury, pagesize=A4)

    if os.path.exists(LOGO_PATH):
        c.drawImage(LOGO_PATH, 50, 730, width=50, height=100, mask='auto')

    # Nagłówek faktury
    c.setFont("Arial", 16)
    c.drawString(200, 800, "FAKTURA VAT")
    c.setFont("Arial", 12)
    c.drawString(200, 780, f"Numer: {numer_faktury}")
    c.drawString(200, 765, f"Data wystawienia: {data_wystawienia}")

    #
    c.setStrokeColor(colors.black)
    c.line(50, 715, 550, 715)

    # Sprzedawca
    c.setFont("Arial", 12)
    c.drawString(50, 720, "Sprzedawca:")
    c.drawString(50, 700, f"{SPRZEDAWCA['nazwa']}")
    c.drawString(50, 685, f"{SPRZEDAWCA['adres']}")
    c.drawString(50, 670, f"NIP: {SPRZEDAWCA['nip']}")
    c.drawString(50, 655, f"Konto: {SPRZEDAWCA['konto']}")

    # Nabywca
    c.drawString(300, 720, "Nabywca:")
    c.drawString(300, 700, f"{NABYWCA['nazwa']}")
    c.drawString(300, 685, f"{NABYWCA['adres']}")
    c.drawString(300, 670, f"NIP: {NABYWCA['nip']}")

    # 🔹 Linia pod danymi sprzedawcy i nabywcy
    c.line(50, 650, 550, 650)

    # Tabela pozycji
    c.setFont("Arial", 10)
    c.drawString(50, 635, "Lp.")
    c.drawString(80, 635, "Nazwa towaru/usługi")
    c.drawString(250, 635, "Ilość")
    c.drawString(300, 635, "Cena netto")
    c.drawString(380, 635, "VAT [%]")
    c.drawString(430, 635, "Cena brutto")

    y = 615
    suma_netto = suma_brutto = 0

    # Losowe produkty
    wybrane_produkty = random.sample(PRODUKTY, random.randint(1, 6))

    for i, (nazwa, cena_netto, vat) in enumerate(wybrane_produkty, 1):
        ilosc = random.randint(1, 5)
        cena_brutto = round(cena_netto * (1 + vat / 100), 2)
        suma_netto += cena_netto * ilosc
        suma_brutto += cena_brutto * ilosc

        c.drawString(50, y, str(i))
        c.drawString(80, y, nazwa)
        c.drawString(250, y, str(ilosc))
        c.drawString(300, y, f"{cena_netto:.2f} zł")
        c.drawString(380, y, str(vat))
        c.drawString(430, y, f"{cena_brutto:.2f} zł")
        y -= 20

    # Linia pod tabelą
    c.line(50, y, 550, y)

    suma_vat = round(suma_brutto - suma_netto, 2)
    c.setFont("Arial", 12)
    c.drawString(50, y-20, f"Suma netto: {suma_netto:.2f} zł")
    c.drawString(50, y-40, f"VAT: {suma_vat:.2f} zł")
    c.drawString(50, y-60, f"Suma brutto: {suma_brutto:.2f} zł")

    # Linia pod podsumowaniem
    c.line(50, y-70, 550, y-70)

    # Dodanie kodu QR (jeśli faktura nieopłacona)
    if status_faktury == "Do zapłaty":
        qr_path = generuj_qr(numer_faktury, suma_brutto, SPRZEDAWCA['konto'])
        c.drawImage(qr_path, 400, y-65, width=60, height=60, mask='auto')

    # Status płatności
    c.setFont("Arial", 12)
    c.setFillColor(colors.red if status_faktury == "Do zapłaty" else colors.green)
    c.drawString(50, y-90, f"Status: {status_faktury}")
    if status_faktury == 'Do zapłaty':
        c.drawString(50,y-110,f"Termin Płatności: {termin_platnosci}")

    c.save()
    print(f"Faktura wygenerowana: {plik_faktury}")

if __name__ == "__main__":

    generuj_fakture()
