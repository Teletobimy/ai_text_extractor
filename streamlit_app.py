import streamlit as st
import os
import tempfile
from pathlib import Path
import sys

# Windows에서 UTF-8 출력 설정
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from ai_text_extractor import extract_text_from_ai, extract_text_with_layout

def main():
    st.set_page_config(
        page_title="AI 파일 텍스트 추출기",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 AI 파일 텍스트 추출기")
    st.markdown("Adobe Illustrator (.ai) 파일에서 텍스트를 추출하는 도구입니다.")
    
    # 사이드바
    st.sidebar.header("설정")
    
    # 추출 방법 선택
    method = st.sidebar.selectbox(
        "추출 방법",
        ["auto", "layout", "direct", "convert"],
        index=0,
        help="auto: 레이아웃 기반 우선, layout: 레이아웃 기반만, direct: PDF 직접 읽기, convert: 변환 후 추출"
    )
    
    # 파일 업로드
    uploaded_file = st.file_uploader(
        "AI 파일을 업로드하세요",
        type=['ai'],
        help="Adobe Illustrator 파일 (.ai)을 업로드하세요"
    )
    
    if uploaded_file is not None:
        # 파일 정보 표시
        st.success(f"파일 업로드 완료: {uploaded_file.name}")
        st.info(f"파일 크기: {uploaded_file.size:,} bytes")
        
        # 추출 버튼
        if st.button("텍스트 추출 시작", type="primary"):
            with st.spinner("텍스트 추출 중..."):
                try:
                    # 임시 파일로 저장
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".ai") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # 텍스트 추출
                    if method == "layout":
                        text = extract_text_with_layout(tmp_path)
                    else:
                        text = extract_text_from_ai(tmp_path, method=method)
                    
                    # 임시 파일 삭제
                    os.unlink(tmp_path)
                    
                    if text.startswith("오류"):
                        st.error(f"추출 실패: {text}")
                    else:
                        st.success("텍스트 추출 성공!")
                        
                        # 통계 정보
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("총 문자 수", f"{len(text):,}자")
                        with col2:
                            lines = text.split('\n')
                            st.metric("총 줄 수", f"{len(lines)}줄")
                        with col3:
                            avg_chars = len(text)//len(lines) if lines else 0
                            st.metric("평균 줄당 문자", f"{avg_chars}자")
                        
                        # 추출된 텍스트 표시
                        st.subheader("추출된 텍스트")
                        
                        # 텍스트 영역
                        st.text_area(
                            "추출된 텍스트",
                            text,
                            height=400,
                            help="추출된 텍스트를 복사하여 사용하세요"
                        )
                        
                        # 다운로드 버튼
                        st.download_button(
                            label="텍스트 파일 다운로드",
                            data=text,
                            file_name=f"{Path(uploaded_file.name).stem}_extracted_text.txt",
                            mime="text/plain"
                        )
                        
                except Exception as e:
                    st.error(f"오류 발생: {str(e)}")
    
    # 사용법 안내
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 사용법")
    st.sidebar.markdown("""
    1. AI 파일을 업로드하세요
    2. 추출 방법을 선택하세요
    3. '텍스트 추출 시작' 버튼을 클릭하세요
    4. 추출된 텍스트를 확인하고 다운로드하세요
    """)
    
    st.sidebar.markdown("### 추출 방법 설명")
    st.sidebar.markdown("""
    - **auto**: 레이아웃 기반 추출을 우선 시도하고, 실패시 다른 방법 사용
    - **layout**: PyMuPDF를 사용한 레이아웃 기반 추출 (권장)
    - **direct**: PyPDF2를 사용한 직접 PDF 읽기
    - **convert**: AI→PDF 변환 후 텍스트 추출
    """)
    
    # 푸터
    st.markdown("---")
    st.markdown("**AI 파일 텍스트 추출기** - Adobe Illustrator 파일에서 텍스트를 추출하는 도구")

if __name__ == "__main__":
    main()
