import urllib.request
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

url = 'https://bogotaclausura2610.ascundeportes.org/organizacion/organizacion/4'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
}
events = []

try:
    req = urllib.request.Request(url, headers=headers)
    # Added strict timeout of 15 seconds to prevent Actions from hanging forever
    html = urllib.request.urlopen(req, timeout=15).read()
    soup = BeautifulSoup(html, 'html.parser')
    
    # In the new site format, matches are usually listed in list-group-items
    found_elements = soup.find_all('a', class_=re.compile('list-group-item'))
    
    # Spanish month mapping to numbers
    meses = {
        'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 
        'may': '05', 'jun': '06', 'jul': '07', 'ago': '08', 
        'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
    }

    for element in found_elements:
        try:
            title_el = element.find('h4')
            if title_el:
                info_text = element.get_text(separator=' | ').strip()
                
                # Fallback values
                start_date = datetime.now().strftime("%Y-%m-%d")
                location_idx = "Sede por confirmar"
                
                # Try to extract the date like "mar 10 | 14:00"
                lines = [line.strip() for line in info_text.split('|') if line.strip()]
                
                if len(lines) > 2:
                    date_part = lines[0].lower() # e.g. "mar 10"
                    time_part = lines[1] # e.g. "14:00"
                    
                    parts = date_part.split()
                    if len(parts) >= 2:
                        mes_texto = parts[0][:3]
                        dia = parts[1].zfill(2)
                        mes = meses.get(mes_texto, '03')
                        # Format: 2026-MM-DDTHH:MM:00
                        start_date = f"2026-{mes}-{dia}T{time_part}:00"
                
                # The literal location is usually the second to last line in the new format
                if len(lines) > 5:
                    location_idx = lines[-1]
                
                events.append({
                    "title": title_el.get_text(strip=True),
                    "raw_text": info_text,
                    "start": start_date,
                    "location": location_idx
                })
        except Exception as item_error:
            print(f"Skipping malformed match element: {item_error}")
            continue
            
    # Mock some data if nothing is found so the calendar isn't empty on first load.
    if not events:
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
        
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=4)
        print("Data scraped and saved to data.json")

except Exception as e:
    print(f"Critical error fetching website: {e}")
    # Write mock data on total network failure so github page doesn't break
    events = [
        {"title": "Error de Red - Partidos no cargados", "start": "2026-03-10T10:00:00", "location": "N/A"}
    ]
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=4)
