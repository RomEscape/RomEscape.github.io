# 연구 홈페이지

실험 기록과 발표자료(PPT)를 모아 두는 개인 홈페이지입니다. GitHub Pages에서 돌아가고, 주소는 **https://romescape.github.io** 입니다(GitHub 계정 RomEscape). PPT를 올리면 GitHub Actions가 PDF로 바꿔 브라우저에서 바로 보이게 합니다.

## 처음 한 번 설정

1. https://github.com/new 에서 저장소 이름을 **`RomEscape.github.io`**, 공개 범위를 **Public**으로 만듭니다(README 추가 등은 고르지 않음).
2. 이 폴더의 파일을 저장소에 올립니다.
   - git이 있으면: `git init && git add . && git commit -m "첫 올림" && git branch -M main && git remote add origin https://github.com/RomEscape/RomEscape.github.io.git && git push -u origin main`
   - 웹으로 올리면: 저장소의 **Add file → Upload files**에 폴더 안 내용을 끌어 놓습니다. 점(.)으로 시작하는 `.github`, `.pages.yml`이 빠지면 **Add file → Create new file**로 같은 경로·같은 내용으로 만듭니다.
3. 저장소 **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로 바꿉니다.
4. **Actions** 탭에서 "사이트 배포"가 초록색으로 끝나면 https://romescape.github.io 가 열립니다(2~4분).

## 고치고 올리기(관리 화면)

1. https://app.pagescms.org 에서 GitHub로 로그인하고 이 저장소를 고릅니다.
2. 왼쪽 메뉴
   - **실험 기록**: 새로 만들기 → 제목·날짜·프로젝트·상태(계획, 진행 중, 완료, 실패, 보류)·요약·내용 → 저장
   - **발표자료**: 새로 만들기 → "발표 파일"에 PPT·PPTX·PDF 올리기 → 저장. 몇 분 뒤 PDF로 바뀌어 보입니다.
   - **사이트 설정**: 이름, 소개글, 링크
3. 저장할 때마다 사이트가 자동으로 다시 만들어집니다.

## 개발일지 불러오기

연구 서버에서(이 폴더와 일지가 함께 있는 곳):

```bash
pip install -r requirements.txt
python build.py import-journal /경로/개발일지.md --project QFFT --since 2026-11-01
```

- 일지의 `## 2026-11-08 — 제목` 항목이 하나씩 `drafts/`에 초안으로 생깁니다. `drafts/`는 저장소에 올라가지 않습니다.
- 상태는 제목으로 짐작한 값이라 확인이 필요합니다.
- IP 주소, ssh, `/home/` 경로, 키·비밀번호로 보이는 글이 있으면 `check:` 줄에 개수를 적어 둡니다.
- 공개해도 되는 것만 `content/experiments/`로 옮기고 `published: true`로 바꿔 올립니다.

## 꼭 알아 둘 점

- **공개 저장소입니다.** 저장소에 올린 파일은 `published: false`여도 GitHub에서 누구나 읽을 수 있습니다. 아직 발표 전인 연구 내용, 서버 주소, 키는 올리지 마세요. 초안까지 숨기려면 GitHub Pro(유료)로 저장소를 비공개로 바꿔야 Pages를 계속 쓸 수 있습니다.
- **파일 크기.** 웹·관리 화면으로는 파일 하나에 25MB, git으로는 100MB까지 올라갑니다. 큰 PPT는 이미지를 압축하거나 PDF로 바꿔 올리세요.
- **사이트 전체 1GB 권장 한도**가 있습니다.

## 내 컴퓨터에서 미리 보기

```bash
pip install -r requirements.txt
python build.py selftest     # 생성기 점검
python build.py build        # _site/ 생성
python -m http.server -d _site 8000   # http://localhost:8000
```

PPT의 PDF 변환은 GitHub에서만 됩니다. 내 컴퓨터에서 보려면 LibreOffice로 `_converted/`에 PDF를 만들어 두면 됩니다.

## 파일 구성

| 경로 | 내용 |
|---|---|
| `site.yml` | 사이트 이름, 소개글, 링크 |
| `content/experiments/` | 실험 기록(Markdown) |
| `content/talks/` | 발표자료 설명(Markdown) |
| `uploads/` | 올린 PPT·PDF·그림 |
| `static/style.css` | 모양 |
| `build.py` | 사이트 생성기, 일지 불러오기, 자체 점검 |
| `.pages.yml` | 관리 화면 설정 |
| `.github/workflows/deploy.yml` | PDF 변환과 배포 |
