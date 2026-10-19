import json, glob, re, sys
R, OUT = sys.argv[1], sys.argv[2]
ws = sorted([w for f in glob.glob(R + '/notes/*.json') for w in json.load(open(f))], key=lambda w: w['n'])
ROOM_NAME = {"700": "Salle Mollien", "702": "Salle Daru", "708": "Salon Carré", "709": "Salle des Sept Mètres",
             "710": "Grande Galerie", "712": "Grande Galerie", "716": "Grande Galerie", "711": "Salle des États"}
out = {}
for w in ws:
    d = json.load(open(f"{R}/louvre/{w['louvre']['url'].rsplit('/', 1)[-1]}.json"))
    inv = d['objectNumber'][0]['value'].split('/')[0].strip()
    # 원제: 사이트 제목은 영어 통용 제목을 유지하고, 루브르 공식 제목은 여기서 병기
    meta = [["원제", d["title"].strip().rstrip(".")]]
    for k, v in w['meta_ko']:
        if k == '소장번호': v = inv
        if k == '전시실':
            m = re.search(r'Salle (\d+)', d.get('room') or '')
            if not m: continue
            v = f"드농관 {m[1]}호실" + (f" · {ROOM_NAME[m[1]]}" if m[1] in ROOM_NAME else "")
        meta.append([k, v])
    out[w['n']] = {
        "meta": meta,
        "body": w['body_ko'],
        "src": w['louvre']['url'],
        "refs": [s['url'] for s in w['sources'] if s['url'].startswith('http') and 'collections.louvre.fr' not in s['url']],
    }
with open(OUT, 'w') as f:
    f.write("// 작품 설명 데이터 (키: 작품 번호 n). 2026-10 조사.\n")
    f.write("// meta 값은 collections.louvre.fr 공식 기록(src) 기준(괄호 안 보충 설명은 다른 출처 포함), body 는 src·refs 를 근거로 새로 작성한 요약.\n// refs 에만 근거한 서술은 「알려져 있다/전한다」로 표현\n")
    f.write("// 전시실은 루브르 기록 기준이며 실제 배치는 바뀔 수 있음\n")
    j = lambda v: json.dumps(v, ensure_ascii=False)
    f.write("const DETAILS = {\n")
    for n, e in out.items():
        f.write(f"  {n}: {{\n    meta: {j(e['meta'])},\n    body: [\n")
        f.write("".join(f"      {j(p)},\n" for p in e['body']))
        f.write(f"    ],\n    src: {j(e['src'])},\n    refs: {j(e['refs'])},\n  }},\n")
    f.write("};\n")
print(len(out), 'works written')
