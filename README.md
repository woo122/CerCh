# CerCh (서치)

기업 채용공고 기반 기술 · 자격증 트렌드 분석 사이트

---

## 환경별 사용법

### 처음 받을 때 (기숙사/강의실)
git clone https://github.com/woo122/CerCh.git

### 작업 후 저장할 때
```bash
git add .         # 올릴 파일 선택
git commit -m "작업내용"   # 세이브포인트 생성
git push          # GitHub에 업로드
```

### 다른 환경에서 최신 코드 받을 때
git pull

---

## 백엔드 서버 실행 (회원가입/로그인 등 기능 사용 시 필요)

### 처음 한 번만 - 패키지 설치
```bash
cd CerCh/backend
pip install -r requirements.txt
```

### 매번 작업 시 - 서버 실행
```bash
cd CerCh/backend
uvicorn main:app --reload
```

- 터미널에 `http://127.0.0.1:8000` 이 뜨면 정상 실행
- 이 터미널은 작업 중 계속 켜둬야 함
- API 테스트: `http://localhost:8000/docs`
- 서버 종료: `Ctrl + C`