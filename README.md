# AI/PDF 파일 텍스트 추출기

Adobe Illustrator (.ai) 파일과 PDF 파일에서 텍스트를 추출하는 Python 도구입니다.

## 🌐 Streamlit Cloud에서 실행하기

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app/)

이 앱을 Streamlit Cloud에서 실행하려면:

1. 이 저장소를 GitHub에 푸시하세요
2. [Streamlit Cloud](https://share.streamlit.io/)에 접속하세요
3. GitHub 저장소를 연결하세요
4. 앱이 자동으로 배포됩니다!

### ⚠️ 파일 크기 제한
- **Streamlit Cloud**: 최대 200MB
- **더 큰 파일**: 로컬에서 실행하세요

## 기능

- **다중 파일 형식** 지원:
  - **AI 파일**: Adobe Illustrator 파일 (.ai)
  - **PDF 파일**: 일반 PDF 문서 (.pdf)
- **다중 추출 방법** 지원:
  - **레이아웃 기반** (PyMuPDF, 권장) - 좌표 기반으로 자연스러운 순서
  - **직접 PDF 읽기** (PyPDF2) - 기본 PDF 텍스트 추출
  - **변환 후 추출** - AI→PDF 변환 후 텍스트 추출 (AI 파일만)
- **자동 감지**: 파일 형식에 따른 최적 추출 방법 자동 선택
- **배치 처리**: 폴더 내 모든 파일 일괄 처리
- **웹 인터페이스**: Streamlit 기반 사용자 친화적 UI
- **다운로드 지원**: 추출된 텍스트를 .txt 파일로 다운로드

## 설치

### 로컬 실행

```bash
# 저장소 클론
git clone https://github.com/your-username/ai-text-extractor.git
cd ai-text-extractor

# 의존성 설치
pip install -r requirements_streamlit.txt

# Streamlit 앱 실행
streamlit run streamlit_app.py
```

### Streamlit Cloud 배포

1. 이 저장소를 GitHub에 푸시
2. [Streamlit Cloud](https://share.streamlit.io/) 접속
3. GitHub 저장소 연결
4. 자동 배포 완료!

## 사용법

### 🌐 웹 인터페이스 (권장)

Streamlit 웹 앱을 사용하면 브라우저에서 쉽게 텍스트를 추출할 수 있습니다:

1. **파일 업로드**: AI 또는 PDF 파일을 드래그 앤 드롭 또는 클릭하여 업로드
2. **추출 방법 선택**: auto, layout, direct, convert 중 선택
3. **텍스트 추출**: "텍스트 추출 시작" 버튼 클릭
4. **결과 확인**: 추출된 텍스트를 화면에서 확인
5. **다운로드**: 텍스트 파일로 다운로드

### 💻 명령행 버전

```bash
# 기본 텍스트 추출
python ai_text_extractor.py input.ai

# 레이아웃 기반 추출
python ai_text_extractor.py input.ai --method layout

# 출력 파일 지정
python ai_text_extractor.py input.ai --output extracted.txt

# 기존 ai_to_ppt.py 사용
python ai_to_ppt.py input.ai --extract-text
```

## 추출 방법

### Auto (기본)
- **레이아웃 기반 추출**을 우선 시도
- 실패시 **직접 PDF 읽기**로 대체
- 가장 안정적인 방법

### Layout (권장)
- **PyMuPDF**를 사용한 좌표 기반 추출
- 자연스러운 읽기 순서 보장
- 가장 정확한 텍스트 추출

### Direct
- **PyPDF2**를 사용한 기본 PDF 읽기
- 빠르지만 순서가 뒤죽박죽일 수 있음

### Convert
- AI→PDF 변환 후 텍스트 추출
- 외부 도구 필요 (Inkscape 등)

## 문제 해결

### PyMuPDF 설치 오류
```bash
# PyMuPDF 설치
pip install PyMuPDF

# 또는 conda 사용
conda install -c conda-forge pymupdf
```

### PyPDF2 설치 오류
```bash
# PyPDF2 설치
pip install PyPDF2

# 최신 버전 설치
pip install --upgrade PyPDF2
```

### 텍스트 추출 실패
- AI 파일이 실제로 PDF 구조를 포함하는지 확인
- 파일이 손상되지 않았는지 확인
- 다른 추출 방법 시도 (layout → direct → convert)

## 시스템 요구사항

- **Python**: 3.7 이상
- **메모리**: 최소 2GB RAM
- **브라우저**: 최신 웹 브라우저 (Streamlit 앱용)

## 라이선스

이 도구는 MIT 라이선스 하에 배포됩니다.

## 기여

버그 리포트나 기능 요청은 GitHub Issues를 통해 제출해주세요.

## 변경 이력

### v2.0.0
- Streamlit 웹 인터페이스 추가
- 레이아웃 기반 텍스트 추출 (PyMuPDF)
- 자연스러운 읽기 순서 보장
- 웹 기반 파일 업로드 및 다운로드

### v1.0.0
- 초기 버전
- 기본 PDF 텍스트 추출 (PyPDF2)
- 명령행 인터페이스
