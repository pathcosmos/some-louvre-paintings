import json, glob, re, subprocess, os, sys
R = sys.argv[1]
ws = sorted([w for f in glob.glob(R + '/notes/*.json') for w in json.load(open(f))], key=lambda w: w['n'])
def num(s): return s.replace(',', '.')
for w in ws:
    url = w['louvre']['url']; ark = url.rsplit('/', 1)[-1]
    p = f"{R}/louvre/{ark}.json"
    if not os.path.exists(p):
        subprocess.run(['curl', '-sL', '-A', 'Mozilla/5.0', url + '.json', '-o', p])
    try: d = json.load(open(p))
    except Exception as e: print(w['n'], 'FETCH FAIL', url); continue
    inv = d['objectNumber'][0]['value']
    dims = {x['type']: x['value'] for x in d.get('dimension', [])}
    h, l = dims.get('Hauteur'), dims.get('Largeur')
    meta = dict(w['meta_ko'])
    issues = []
    if meta.get('소장번호', '').replace('-', ' ') != inv.split('/')[0].strip().replace('-', ' '): issues.append(f"inv meta={meta.get('소장번호')} louvre={inv}")
    if h and l:
        hc, lc = round(float(num(h)) * (100 if d['dimension'][0]['unit'] == 'm' else 1), 1), round(float(num(l)) * (100 if d['dimension'][0]['unit'] == 'm' else 1), 1)
        nums = [float(x) for x in re.findall(r'[\d.]+', meta.get('크기', ''))]
        if nums[:2] != [hc, lc]: issues.append(f"dim meta={meta.get('크기')} louvre={h}x{l}{d['dimension'][0]['unit']} {dims}")
    else: issues.append(f"dims louvre={dims}")
    dc = d.get('dateCreated') or [{}]
    print(f"{w['n']:02} {'OK ' if not issues else 'CHK'} date[louvre]={dc[0].get('text')!r} ({dc[0].get('startYear')}-{dc[0].get('endYear')}) | meta={meta.get('제작')!r} | room={d.get('room')!r}", *issues, sep='\n    ' if issues else ' ')
