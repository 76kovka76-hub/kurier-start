#!/usr/bin/env python3
from pathlib import Path
import re, sys
R=Path(__file__).resolve().parent; h=(R/'index.html').read_text(encoding='utf-8'); p=(R/'privacy.html').read_text(encoding='utf-8'); e=[]
def ck(x,m):
    if not x:e.append(m)
ck('<h1' in h,'Missing H1'); ck('name="keywords"' in h,'Missing keyword meta'); ck('не является официальным сайтом' in h.lower(),'Missing independent-site disclaimer')
ck('https://vkusvill.ru/job/courier/' in h,'Missing official courier link'); ck('https://wa.me/79201461682' in h and 'https://t.me/daaaggg1' in h,'Missing contact links')
ck('<form' not in h.lower(),'Form must stay disabled until legal docs are ready'); ck('id="phone"' not in h and 'id="name"' not in h,'Personal-data input found')
ck('не предусмотрены анкеты' in p,'No-data notice missing'); ck('[указать' not in p,'Template placeholder found')
ck('canonical' not in h,'Canonical must wait for verified domain'); ck((R/'styles.css').is_file(),'Missing CSS')
for a in re.finditer(r'<a\b([^>]*target="_blank"[^>]*)>',h,re.I): ck('noopener' in a.group(1),'Unsafe external target blank')
if e: print('FAIL\n'+'\n'.join(e)); sys.exit(1)
print('PASS: public no-form release checks')
