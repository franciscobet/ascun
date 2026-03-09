import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request('https://bogotaclausura2610.ascundeportes.org/', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
scripts = re.findall(r'src="([^"]+\.js[^"]*)"', html)
print("Scripts found:", scripts)

for s in scripts:
    clean_s = s.split('?')[0] # remove query params
    if not clean_s.startswith('http'):
        url = f'https://bogotaclausura2610.ascundeportes.org/{clean_s}'
        try:
            print(f"Fetching {url}")
            js_code = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), context=ctx).read().decode('utf-8')
            api_urls = re.findall(r'https?://[^\s"\'\`]+api[^\s"\'\`]+', js_code)
            if api_urls:
                print(f"APIs in {clean_s}:", set(api_urls))
        except Exception as e:
            print(f"Error fetching {url}: {e}")
