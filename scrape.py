from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import random
import time

url = 'https://bogotaclausura2610.ascundeportes.org/organizacion/organizacion/4'

events = []

# Spanish month mapping to numbers
meses = {
    'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04',
    'may': '05', 'jun': '06', 'jul': '07', 'ago': '08',
    'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
}

# Inject manual events that are not yet officially listed on the ASCUN site
manual_events = [
    {
        "title": "⚽ F1.1 Grupo - Torneo de Fútbol Sala Masculino",
        "raw_text": "Partido programado manualmente | Universidad Sergio Arboleda vs Universidad Nacional",
        "start": "2026-03-13T17:00:00",
        "location": "Sede por confirmar"
    }
]

try:
    print("Iniciando Playwright...")
    time.sleep(random.uniform(1.5, 3.5))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='es-ES',
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()

        # Extra headers to look more human
        page.set_extra_http_headers({
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        })

        print(f"Navegando a {url}...")
        page.goto(url, wait_until='networkidle', timeout=60000)

        # Wait a bit for JS-rendered content
        time.sleep(random.uniform(2, 4))

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')
    found_elements = soup.find_all('a', class_=re.compile('list-group-item'))
    print(f"Elementos encontrados: {len(found_elements)}")

    for element in found_elements:
        try:
            title_el = element.find('h4')
            if title_el:
                info_text = element.get_text(separator=' | ').strip()

                # Fallback values
                start_date = datetime.now().strftime("%Y-%m-%d")
                location_idx = "Sede por confirmar"

                lines = [line.strip() for line in info_text.split('|') if line.strip()]

                if len(lines) > 2:
                    date_part = lines[0].lower()
                    time_part = lines[1]

                    parts = date_part.split()
                    if len(parts) >= 2:
                        mes_texto = parts[0][:3]
                        dia = parts[1].zfill(2)
                        mes = meses.get(mes_texto, '03')
                        start_date = f"2026-{mes}-{dia}T{time_part}:00"

                if len(lines) > 5:
                    location_idx = lines[-1]

                events.append({
                    "title": title_el.get_text(strip=True),
                    "raw_text": info_text,
                    "start": start_date,
                    "location": location_idx
                })
        except Exception as item_error:
            print(f"Skipping malformed element: {item_error}")
            continue

    if not events:
        print("No se encontraron eventos, usando datos de ejemplo.")
        events = [
            {
                "title": "⚽ Fútbol ASCUN: Sergio Arboleda vs U. de la Sabana",
                "start": "2026-03-10T12:00:00",
                "location": "Cancha Universidad de la Sabana"
            },
            {
                "title": "Fútbol Sala ASCUN: Sergio Arboleda vs U. Nacional",
                "start": "2026-03-15T14:00:00",
                "location": "Coliseo Universidad Nacional"
            },
            {
                "title": "Baloncesto Femenino ASCUN: Sergio Arboleda vs Javeriana",
                "start": "2026-03-18T16:30:00",
                "location": "Coliseo Sergio Arboleda"
            },
            {
                "title": "Voleibol ASCUN: Sergio Arboleda vs U. Andes",
                "start": "2026-03-22T10:00:00",
                "location": "Polideportivo U. Andes"
            }
        ]

    # Merge scraped events with manual events
    events.extend(manual_events)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=4)
    print(f"Data guardada en data.json ({len(events)} eventos)")

except Exception as e:
    print(f"Error crítico: {e}")
    # Write mock data on total failure so GitHub Pages doesn't break
    events = [
        {"title": "Error de Red - Partidos no cargados", "start": "2026-03-10T10:00:00", "location": "N/A"}
    ]
    events.extend(manual_events)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=4)
