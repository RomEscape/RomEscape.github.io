#!/usr/bin/env python3
"""연구 홈페이지 생성기: content/ 의 Markdown 과 site.yml 을 읽어 _site/ 에 정적 HTML 을 만든다.

  python build.py build                                   # _site/ 만들기
  python build.py import-journal 개발일지.md --project QFFT [--since 2026-11-01] [--match 키워드]
  python build.py selftest                                # 스스로 점검
"""
import argparse
import datetime as dt
import hashlib
import html
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

import markdown
import yaml

ROOT = Path(__file__).resolve().parent
STATUSES = ['계획', '진행 중', '완료', '실패', '보류']
NAV = [('home', 'index.html', '홈'), ('research', 'research/index.html', '연구'), ('experiments', 'experiments/index.html', '실험 기록'),
       ('talks', 'talks/index.html', '발표자료'), ('about', 'about.html', '소개')]
FRONT = re.compile(r'^---[ \t]*\n(.*?)\n---[ \t]*(?:\n|$)', re.S)


def esc(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def md(text):
    return markdown.markdown(text or '', extensions=['tables', 'fenced_code', 'sane_lists'])


def as_date(v, fallback):
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', str(v or fallback or ''))
    return dt.date(*map(int, m.groups())) if m else dt.date(1970, 1, 1)


def read_doc(p):
    text = p.read_text(encoding='utf-8')
    m = FRONT.match(text)
    meta = (yaml.safe_load(m.group(1)) or {}) if m else {}
    body = text[m.end():] if m else text
    meta['date'] = as_date(meta.get('date'), p.stem)
    meta['slug'] = p.stem
    meta['body'] = body if str(body).strip() else str(meta.get('body') or '')
    return meta


def load(root, kind):
    docs = [read_doc(p) for p in sorted((root / 'content' / kind).glob('*.md'))]
    return sorted([d for d in docs if d.get('published', True) is not False], key=lambda d: (d['date'], d['slug']), reverse=True)


def pill(status):
    i = STATUSES.index(status) if status in STATUSES else -1
    return f'<span class="pill s{i}">{esc(status)}</span>' if status else ''


def page(site, title, body, depth, active):
    r = '../' * depth
    links = []
    for key, href, label in NAV:
        cur = ' aria-current="page"' if key == active else ''
        links.append(f'<a href="{r}{href}"{cur}>{label}</a>')
    name = esc(site.get('name') or '연구 기록')
    full = name if active == 'home' else f'{esc(title)} · {name}'
    body = body.replace('="/uploads/', f'="{r}uploads/')  # 관리 화면이 넣는 /uploads/ 절대 경로를 저장소 이름 경로에서도 동작하게
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full}</title>
<meta name="description" content="{esc(site.get('tagline'))}">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="{r}static/style.css">
</head>
<body>
<header class="top"><div class="inner"><a class="brand" href="{r}index.html">{name}</a><nav>{''.join(links)}</nav></div></header>
<main class="inner">
{body}
</main>
<footer class="inner"><span>{name}</span><span>마지막 갱신 {dt.date.today().isoformat()}</span></footer>
</body>
</html>
'''


def exp_row(d, r):
    proj = f'<span class="proj">{esc(d.get("project"))}</span>' if d.get('project') else ''
    summ = f'<p>{esc(d.get("summary"))}</p>' if d.get('summary') else ''
    return (f'<li class="row" data-status="{esc(d.get("status"))}" data-project="{esc(d.get("project"))}">'
            f'<time>{d["date"].isoformat()}</time>{pill(d.get("status"))}'
            f'<a class="title" href="{r}experiments/{quote(d["slug"])}.html">{esc(d.get("title") or d["slug"])}</a>{proj}{summ}</li>')


def talk_row(d, r):
    ev = f'<span class="proj">{esc(d.get("event"))}</span>' if d.get('event') else ''
    summ = f'<p>{esc(d.get("summary"))}</p>' if d.get('summary') else ''
    return (f'<li class="row"><time>{d["date"].isoformat()}</time>'
            f'<a class="title" href="{r}talks/{quote(d["slug"])}.html">{esc(d.get("title") or d["slug"])}</a>{ev}{summ}</li>')


def research_card(d, exps, r):
    n = sum(1 for e in exps if d.get('project') and e.get('project') == d.get('project'))
    meta = ' · '.join(x for x in [pill(d.get('status')), f'실험 기록 {n}개' if n else ''] if x)
    summ = f'<p>{esc(d.get("summary"))}</p>' if d.get('summary') else ''
    return (f'<article class="card"><h3><a href="{r}research/{quote(d["slug"])}.html">{esc(d.get("title") or d["slug"])}</a></h3>'
            f'{summ}<p class="meta">{meta}</p></article>')


def talk_files(d, root):
    """발표 파일의 (원본 경로, PDF 경로)를 사이트 기준 상대 경로로 돌려준다. PDF가 없으면 None."""
    f = str(d.get('file') or '').lstrip('/')
    if not f:
        return None, None
    if f.lower().endswith('.pdf'):
        return f, f
    pdf = root / '_converted' / (Path(f).stem + '.pdf')  # ponytail: 하위 폴더에 같은 이름 파일이 있으면 겹침. 생기면 경로를 이름에 넣을 것
    return f, (f'uploads/pdf/{Path(f).stem}.pdf' if pdf.exists() else None)


def build(root=ROOT, out=None):
    out = Path(out or root / '_site')
    site = yaml.safe_load((root / 'site.yml').read_text(encoding='utf-8')) or {}
    exps, talks = load(root, 'experiments'), load(root, 'talks')
    research = sorted(load(root, 'research'), key=lambda d: (d.get('order') or 99, d['slug']))
    if out.exists():
        shutil.rmtree(out)
    (out / 'experiments').mkdir(parents=True)
    (out / 'talks').mkdir()
    (out / 'research').mkdir()
    shutil.copytree(root / 'static', out / 'static')
    if (root / 'uploads').exists():
        shutil.copytree(root / 'uploads', out / 'uploads', ignore=shutil.ignore_patterns('.gitkeep'))
    for pdf in (root / '_converted').glob('*.pdf'):
        (out / 'uploads' / 'pdf').mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, out / 'uploads' / 'pdf' / pdf.name)

    def write(rel, html_text):
        (out / rel).write_text(html_text, encoding='utf-8')

    # 홈
    empty_e = '<p class="empty">아직 공개한 실험 기록이 없습니다.</p>'
    empty_t = '<p class="empty">아직 올린 발표자료가 없습니다. 관리 화면의 "발표자료"에서 PPT를 올리면 여기에 나타납니다.</p>'
    links = ''.join(f'<li><a href="{esc(l.get("url"))}">{esc(l.get("label"))}</a></li>' for l in site.get('links') or [] if l.get('url'))
    home = f'''<section class="hero"><h1>{esc(site.get('name') or '연구 기록')}</h1>
<p class="tagline">{esc(site.get('tagline'))}</p><div class="prose">{md(site.get('intro'))}</div>{f'<ul class="links">{links}</ul>' if links else ''}</section>
{f'<section><div class="sec-head"><h2>연구</h2><a href="research/index.html">전체 보기</a></div><div class="cards">' + ''.join(research_card(d, exps, '') for d in research) + '</div></section>' if research else ''}
<div class="cols">
<section><div class="sec-head"><h2>최근 실험 기록</h2><a href="experiments/index.html">전체 보기</a></div>
{'<ul class="list">' + ''.join(exp_row(d, '') for d in exps[:6]) + '</ul>' if exps else empty_e}</section>
<section><div class="sec-head"><h2>최근 발표자료</h2><a href="talks/index.html">전체 보기</a></div>
{'<ul class="list">' + ''.join(talk_row(d, '') for d in talks[:6]) + '</ul>' if talks else empty_t}</section>
</div>'''
    write('index.html', page(site, '홈', home, 0, 'home'))

    # 연구 주제: 개요 글 + 같은 프로젝트 이름의 실험 기록 자동 목록
    body = '<h1>연구</h1>' + ('<div class="cards">' + ''.join(research_card(d, exps, '../') for d in research) + '</div>'
                              if research else '<p class="empty">아직 공개한 연구 주제가 없습니다.</p>')
    write('research/index.html', page(site, '연구', body, 1, 'research'))
    for d in research:
        rel = [e for e in exps if d.get('project') and e.get('project') == d.get('project')]
        rel_html = ('<section class="related"><div class="sec-head"><h2>관련 실험 기록</h2></div><ul class="list">'
                    + ''.join(exp_row(e, '../') for e in rel) + '</ul></section>') if rel else ''
        meta = ' · '.join(x for x in [pill(d.get('status')), esc(d.get('project')) if d.get('project') else ''] if x)
        body = f'''<p class="back"><a href="index.html">← 연구</a></p><h1>{esc(d.get('title') or d['slug'])}</h1>
<p class="meta">{meta}</p>{f'<p class="lead">{esc(d.get("summary"))}</p>' if d.get('summary') else ''}<div class="prose">{md(d['body'])}</div>{rel_html}'''
        write(f'research/{d["slug"]}.html', page(site, d.get('title') or d['slug'], body, 1, 'research'))

    # 실험 기록 목록(월별 묶음 + 상태·프로젝트 거르기)
    projects = sorted({d.get('project') for d in exps if d.get('project')})
    groups, cur = [], None
    for d in exps:
        ym = d['date'].strftime('%Y년 %m월')
        if ym != cur:
            groups.append((ym, []))
            cur = ym
        groups[-1][1].append(exp_row(d, '../'))
    chips = ''.join(f'<button type="button" data-status="{esc(s)}">{esc(s)}</button>' for s in STATUSES)
    opts = ''.join(f'<option value="{esc(p)}">{esc(p)}</option>' for p in projects)
    body = f'''<h1>실험 기록</h1>
<div class="filters" role="group" aria-label="거르기"><button type="button" data-status="" aria-pressed="true">전체</button>{chips}
<label>프로젝트 <select id="proj"><option value="">전체</option>{opts}</select></label><span id="count" class="small"></span></div>
{''.join(f'<section class="month"><h2>{ym}</h2><ul class="list">{"".join(rows)}</ul></section>' for ym, rows in groups) or empty_e}
<script>
(function(){{var st='',pj=document.getElementById('proj');
function apply(){{var n=0;document.querySelectorAll('.month').forEach(function(m){{var v=0;
m.querySelectorAll('.row').forEach(function(r){{var ok=(!st||r.dataset.status===st)&&(!pj.value||r.dataset.project===pj.value);r.hidden=!ok;if(ok)v++;}});
m.hidden=!v;n+=v;}});document.getElementById('count').textContent=n+'개';}}
document.querySelectorAll('.filters button').forEach(function(b){{b.addEventListener('click',function(){{st=b.dataset.status;
document.querySelectorAll('.filters button').forEach(function(x){{x.setAttribute('aria-pressed',x===b);}});apply();}});}});
pj.addEventListener('change',apply);apply();}})();
</script>'''
    write('experiments/index.html', page(site, '실험 기록', body, 1, 'experiments'))
    for d in exps:
        meta = ' · '.join(x for x in [d['date'].isoformat(), esc(d.get('project')) if d.get('project') else '', pill(d.get('status'))] if x)
        src = f'<p class="small">원본: {esc(d.get("source"))}</p>' if d.get('source') else ''
        body = f'''<p class="back"><a href="index.html">← 실험 기록</a></p><h1>{esc(d.get('title') or d['slug'])}</h1>
<p class="meta">{meta}</p>{f'<p class="lead">{esc(d.get("summary"))}</p>' if d.get('summary') else ''}<div class="prose">{md(d['body'])}</div>{src}'''
        write(f'experiments/{d["slug"]}.html', page(site, d.get('title') or d['slug'], body, 1, 'experiments'))

    # 발표자료
    body = '<h1>발표자료</h1>' + ('<ul class="list">' + ''.join(talk_row(d, '../') for d in talks) + '</ul>' if talks else empty_t)
    write('talks/index.html', page(site, '발표자료', body, 1, 'talks'))
    for d in talks:
        orig, pdf = talk_files(d, root)
        orig, pdf = (quote(x, safe='/') if x else x for x in (orig, pdf))
        if pdf:
            viewer = (f'<div class="viewer"><object data="../{esc(pdf)}" type="application/pdf" aria-label="발표 슬라이드">'
                      f'<p>이 브라우저에서는 PDF를 바로 보여 줄 수 없습니다. <a href="../{esc(pdf)}">PDF 열기</a></p></object></div>')
            acts = f'<a class="btn" href="../{esc(pdf)}" target="_blank" rel="noopener">새 창에서 보기</a>'
        else:
            viewer = '<p class="empty">PDF 변환본이 아직 없습니다. 방금 올렸다면 몇 분 뒤 새로 고쳐 보세요.</p>' if orig else ''
            acts = ''
        if orig:
            acts += f'<a class="btn" href="../{esc(orig)}" download>원본 내려받기</a>'
        meta = ' · '.join(x for x in [d['date'].isoformat(), esc(d.get('event'))] if x)
        body = f'''<p class="back"><a href="index.html">← 발표자료</a></p><h1>{esc(d.get('title') or d['slug'])}</h1>
<p class="meta">{meta}</p>{f'<p class="lead">{esc(d.get("summary"))}</p>' if d.get('summary') else ''}{viewer}
{f'<div class="actions">{acts}</div>' if acts else ''}<div class="prose">{md(d['body'])}</div>'''
        write(f'talks/{d["slug"]}.html', page(site, d.get('title') or d['slug'], body, 1, 'talks'))

    # 소개
    body = f'<h1>소개</h1><div class="prose">{md(site.get("about") or site.get("intro"))}</div>' + (f'<ul class="links">{links}</ul>' if links else '')
    write('about.html', page(site, '소개', body, 0, 'about'))
    return out, len(exps), len(talks)


# ── 개발일지 불러오기 ──────────────────────────────────────────────
HEAD = re.compile(r'^## (\d{4}-\d{2}-\d{2})(?:T\S*)?\s*(?:[—–-]\s*)?(.*)$')
CHECKS = [('IP 주소', r'\b\d{1,3}(?:\.\d{1,3}){3}\b'), ('ssh', r'(?i)\bssh\b'), ('/home/ 경로', r'/home/'),
          ('키·비밀번호', r'(?i)api[_ -]?key|access[_ ]?token|password|secret|비밀번호|apikeys')]


def parse_journal(text):
    heads = list(re.finditer(r'^## [^\n]*$', text, re.M))
    out = []
    for i, h in enumerate(heads):
        m = HEAD.match(h.group(0))
        if not m:
            continue
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        title = re.sub(r'(\s*\[[^\]]*\])+\s*$', '', m.group(2)).strip() or m.group(1)
        out.append(dict(date=m.group(1), title=title, raw_title=m.group(2).strip(), body=text[h.end():end].strip('\n')))
    return out


def guess_status(t):
    for status, pat in [('실패', r'실패|FAIL|기각|못 미침'), ('보류', r'보류|HOLD'), ('완료', r'결과|완료'),
                        ('계획', r'사전등록|계획|설계|준비'), ('진행 중', r'실행|진행|재개|시작')]:
        if re.search(pat, t):
            return status
    return '완료'


def summarize(body):
    for para in re.split(r'\n\s*\n', body):
        p = para.strip()
        if not p or p.startswith(('|', '```', '#')):
            continue
        p = re.sub(r'\*\*|`|^[-*]\s+', '', p, flags=re.M).replace('\n', ' ')
        return p[:140] + ('…' if len(p) > 140 else '')
    return ''


def import_journal(path, project, since=None, match=None, dest=None):
    dest = Path(dest or ROOT / 'drafts')  # 저장소에 안 올라가는 폴더. 확인한 것만 content/experiments/ 로 옮긴다
    dest.mkdir(parents=True, exist_ok=True)
    made = skipped = 0
    for e in parse_journal(Path(path).read_text(encoding='utf-8')):
        if (since and e['date'] < since) or (match and match not in e['raw_title']):
            continue
        f = dest / f"{e['date']}-{hashlib.sha1((e['date'] + e['raw_title']).encode()).hexdigest()[:8]}.md"
        if f.exists():
            skipped += 1
            continue
        found = [f'{name} {len(re.findall(p, e["body"]))}' for name, p in CHECKS if re.search(p, e['body'])]
        meta = dict(title=e['title'], date=e['date'], project=project, status=guess_status(e['raw_title']),
                    summary=summarize(e['body']), published=False, source=Path(path).name)
        if found:
            meta['check'] = '공개 전 확인: ' + ', '.join(found)
        f.write_text('---\n' + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + '---\n\n' + e['body'] + '\n', encoding='utf-8')
        made += 1
    return made, skipped


def selftest():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        (t / 'static').mkdir()
        (t / 'static' / 'style.css').write_text('body{}')
        (t / 'site.yml').write_text('name: 시험\nintro: "**소개**"\nlinks:\n  - label: GitHub\n    url: https://github.com/\n', encoding='utf-8')
        for kind in ('experiments', 'talks', 'research'):
            (t / 'content' / kind).mkdir(parents=True)
        (t / 'content/research/topic.md').write_text('---\ntitle: 연구 주제\nproject: QFFT\nstatus: 진행 중\nsummary: 요약\n---\n\n본문\n', encoding='utf-8')
        (t / 'content/experiments/2026-11-08-a.md').write_text('---\ntitle: 공개 기록\ndate: 2026-11-08\nstatus: 완료\nproject: QFFT\n---\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n![그림](/uploads/x.png)\n', encoding='utf-8')
        (t / 'content/experiments/2026-11-07-b.md').write_text('---\ntitle: 숨긴 기록\ndate: 2026-11-07\npublished: false\n---\n본문\n', encoding='utf-8')
        (t / 'content/talks/2026-11-03-c.md').write_text('---\ntitle: 회의 발표\ndate: 2026-11-03\nfile: /uploads/meeting.pptx\n---\n', encoding='utf-8')
        (t / 'uploads').mkdir()
        (t / 'uploads/meeting.pptx').write_bytes(b'x')
        (t / '_converted').mkdir()
        (t / '_converted/meeting.pdf').write_bytes(b'%PDF')
        out, ne, nt = build(t, t / '_site')
        assert (ne, nt) == (1, 1)
        assert not (out / 'experiments/2026-11-07-b.html').exists()
        e = (out / 'experiments/2026-11-08-a.html').read_text(encoding='utf-8')
        assert '<table>' in e and 'src="../uploads/x.png"' in e and 'class="pill s2"' in e
        k = (out / 'talks/2026-11-03-c.html').read_text(encoding='utf-8')
        assert 'data="../uploads/pdf/meeting.pdf"' in k and 'href="../uploads/meeting.pptx" download' in k
        assert (out / 'uploads/pdf/meeting.pdf').exists() and '<strong>소개</strong>' in (out / 'index.html').read_text(encoding='utf-8')
        rp = (out / 'research/topic.html').read_text(encoding='utf-8')
        assert 'href="../experiments/2026-11-08-a.html"' in rp and '숨긴 기록' not in rp and '실험 기록 1개' in (out / 'research/index.html').read_text(encoding='utf-8')
        assert 'href="research/index.html"' in (out / 'index.html').read_text(encoding='utf-8')
        j = t / 'j.md'
        j.write_text('# 일지\n\n## 2026-11-08 — B01 사전등록 [Claude 세션]\n\n**배경.** 서버 10.0.0.1 에 ssh 로 접속.\n\n'
                     '## 2026-11-08 — B01 결과: 사전 기준 통과\n\n결과 문단.\n\n## 정정 이력\n\n| 표 |\n', encoding='utf-8')
        assert import_journal(j, 'QFFT', dest=t / 'imp') == (2, 0) and import_journal(j, 'QFFT', dest=t / 'imp') == (0, 2)
        docs = sorted((t / 'imp').glob('*.md'), key=lambda p: p.read_text(encoding='utf-8'))
        metas = [read_doc(p) for p in docs]
        by = {m['title']: m for m in metas}
        assert by['B01 사전등록']['status'] == '계획' and by['B01 결과: 사전 기준 통과']['status'] == '완료'
        assert all(m['published'] is False for m in metas) and 'IP 주소 1' in by['B01 사전등록']['check']
        assert '정정 이력' not in by['B01 결과: 사전 기준 통과']['body']
    print('selftest 통과')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='연구 홈페이지 생성기')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('build', help='_site/ 만들기')
    sub.add_parser('selftest', help='스스로 점검')
    ij = sub.add_parser('import-journal', help='개발일지의 날짜별 항목을 비공개 초안으로 불러오기')
    ij.add_argument('journal')
    ij.add_argument('--project', required=True, help='프로젝트 이름(예: QFFT)')
    ij.add_argument('--since', help='이 날짜(YYYY-MM-DD) 이후 항목만')
    ij.add_argument('--match', help='제목에 이 글자가 들어간 항목만')
    a = ap.parse_args()
    if a.cmd == 'build':
        out, ne, nt = build()
        print(f'{out} 생성: 실험 기록 {ne}개, 발표자료 {nt}개')
    elif a.cmd == 'selftest':
        selftest()
    else:
        made, skipped = import_journal(a.journal, a.project, a.since, a.match)
        print(f'새 초안 {made}개, 이미 있어 건너뜀 {skipped}개 → drafts/ (저장소에 안 올라감). 내용을 확인하고 공개할 것만 content/experiments/ 로 옮긴 뒤 published: true 로 바꾸세요.')
    sys.exit(0)
