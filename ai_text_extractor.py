#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 파일에서 텍스트를 추출하는 독립 모듈

사용법:
    from ai_text_extractor import extract_text_from_ai
    
    # 자동 방법 (권장)
    text = extract_text_from_ai("design.ai")
    
    # 직접 PDF 읽기
    text = extract_text_from_ai("design.ai", method="direct")
    
    # 변환 후 추출
    text = extract_text_from_ai("design.ai", method="convert")
"""

import os
import sys
import tempfile
from pathlib import Path

# Windows에서 UTF-8 출력 설정
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# PyPDF2 임포트 (선택적)
try:
    import PyPDF2
    from PyPDF2.errors import PdfReadError
    PDF_AVAILABLE = True
    PDF2_ERROR = None
except ImportError as e:
    PyPDF2 = None
    PdfReadError = Exception
    PDF_AVAILABLE = False
    PDF2_ERROR = str(e)


def extract_text_from_ai_as_pdf(file_path):
    """
    .ai 파일을 PDF로 가정하고 텍스트를 추출합니다.
    PyMuPDF를 우선 사용하고, 실패시 PyPDF2를 사용합니다.
    
    Args:
        file_path: .ai 파일 경로
        
    Returns:
        str: 추출된 텍스트 또는 오류 메시지
    """
    # 먼저 PyMuPDF 시도 (더 안정적)
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text.strip()
    except Exception:
        pass  # PyMuPDF 실패시 PyPDF2 시도
    
    # PyPDF2 사용 (폴백)
    if not PDF_AVAILABLE:
        error_msg = "오류: PDF 처리를 위한 패키지가 설치되지 않았습니다."
        if PDF2_ERROR:
            error_msg += f" (PyPDF2: {PDF2_ERROR})"
        error_msg += " pip install PyPDF2 또는 pip install PyMuPDF를 실행해주세요."
        return error_msg
    
    try:
        # 'rb' (read binary) 모드로 파일 열기
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            
            # 모든 페이지를 반복하며 텍스트 추출
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
            
    except PdfReadError:
        return "오류: 파일이 유효한 PDF 구조를 포함하고 있지 않거나, 손상되었을 수 있습니다."
    except FileNotFoundError:
        return "오류: 파일을 찾을 수 없습니다."
    except Exception as e:
        return f"오류 발생: {e}"


def extract_text_with_layout(file_path):
    """
    PyMuPDF를 사용하여 레이아웃을 고려한 텍스트 추출
    
    Args:
        file_path: .ai 파일 경로
        
    Returns:
        str: 추출된 텍스트 또는 오류 메시지
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return "오류: PyMuPDF가 설치되지 않았습니다. pip install PyMuPDF를 실행해주세요."
    
    try:
        doc = fitz.open(file_path)
        all_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_blocks = []
            
            # 텍스트 블록을 좌표 순서로 정렬
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if span["text"].strip():  # 빈 텍스트 제외
                                text_blocks.append({
                                    'text': span['text'],
                                    'bbox': span['bbox'],  # [x0, y0, x1, y1]
                                    'page': page_num
                                })
            
            # y좌표 기준으로 정렬 (위에서 아래로), 같은 y좌표면 x좌표 기준
            # PyMuPDF 좌표계: y가 작을수록 위쪽, 클수록 아래쪽
            text_blocks.sort(key=lambda x: (x['bbox'][1], x['bbox'][0]))
            
            # 정렬된 텍스트 결합
            page_text = []
            current_y = None
            line_text = []
            
            for block in text_blocks:
                y = block['bbox'][1]
                
                # 같은 줄인지 확인 (y좌표 차이가 5픽셀 이내)
                if current_y is None or abs(y - current_y) <= 5:
                    line_text.append(block['text'])
                    current_y = y
                else:
                    # 새로운 줄 시작
                    if line_text:
                        page_text.append(' '.join(line_text))
                    line_text = [block['text']]
                    current_y = y
            
            # 마지막 줄 추가
            if line_text:
                page_text.append(' '.join(line_text))
            
            all_text.extend(page_text)
        
        doc.close()
        return '\n'.join(all_text)
        
    except Exception as e:
        return f"레이아웃 기반 추출 오류: {e}"


def extract_text_from_ai_via_conversion(ai_path: Path, temp_dir: Path = None):
    """
    .ai 파일을 PDF로 변환한 후 텍스트를 추출합니다.
    이 방법은 .ai 파일이 실제로 PDF 구조를 포함하지 않은 경우에 사용됩니다.
    
    Args:
        ai_path: .ai 파일 경로
        temp_dir: 임시 디렉토리 (선택사항)
        
    Returns:
        str: 추출된 텍스트 또는 오류 메시지
    """
    if temp_dir is None:
        temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # AI를 PDF로 변환하는 함수 (외부 의존성 필요)
        # 실제 구현에서는 Inkscape나 Adobe Illustrator가 필요합니다
        pdf_path = temp_dir / (ai_path.stem + "_temp.pdf")
        
        # 여기서는 변환 기능이 없으므로 오류 메시지 반환
        return "오류: AI→PDF 변환 기능을 사용하려면 ai_to_ppt.py의 전체 기능이 필요합니다."
        
    except Exception as e:
        return f"변환 중 오류 발생: {e}"


def extract_text_from_ai(ai_path, method: str = "auto"):
    """
    .ai 파일에서 텍스트를 추출합니다.
    
    Args:
        ai_path: .ai 파일 경로 (str 또는 Path)
        method: 추출 방법 ("auto", "direct", "convert", "layout")
            - auto: 레이아웃 기반 추출 시도 후 실패시 기본 PDF 읽기
            - direct: .ai 파일을 직접 PDF로 읽기만 시도
            - convert: AI→PDF 변환 후 텍스트 추출
            - layout: PyMuPDF를 사용한 레이아웃 기반 추출
    
    Returns:
        str: 추출된 텍스트 또는 오류 메시지
    """
    ai_path = Path(ai_path)
    
    if not ai_path.exists():
        return "오류: 파일을 찾을 수 없습니다."
    
    if not ai_path.suffix.lower() == ".ai":
        return "오류: .ai 파일이 아닙니다."
    
    if method == "direct":
        return extract_text_from_ai_as_pdf(ai_path)
    elif method == "convert":
        return extract_text_from_ai_via_conversion(ai_path)
    elif method == "layout":
        return extract_text_with_layout(ai_path)
    else:  # auto
        # 먼저 레이아웃 기반 추출 시도
        print("[INFO] 레이아웃 기반 텍스트 추출을 시도합니다...")
        layout_result = extract_text_with_layout(ai_path)
        
        # 성공했고 텍스트가 있으면 반환
        if not layout_result.startswith("오류") and layout_result.strip():
            print("[SUCCESS] 레이아웃 기반 추출 성공!")
            return layout_result
        
        # 실패했으면 기본 PDF 읽기 시도
        print("[INFO] 레이아웃 기반 추출 실패, 기본 PDF 읽기를 시도합니다...")
        direct_result = extract_text_from_ai_as_pdf(ai_path)
        
        # 성공했고 텍스트가 있으면 반환
        if not direct_result.startswith("오류") and direct_result.strip():
            return direct_result
        
        # 실패했거나 텍스트가 없으면 변환 방법 시도
        print("[INFO] 기본 PDF 읽기 실패, 변환 방법을 시도합니다...")
        return extract_text_from_ai_via_conversion(ai_path)


def main():
    """명령줄 인터페이스"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI 파일에서 텍스트 추출")
    parser.add_argument("ai_file", help=".ai 파일 경로")
    parser.add_argument("--method", choices=["auto", "direct", "convert", "layout"], 
                       default="auto", help="추출 방법 (auto=레이아웃기반, direct=PDF직접읽기, convert=변환후추출, layout=레이아웃기반)")
    parser.add_argument("--output", "-o", help="출력 파일 경로 (선택사항)")
    
    args = parser.parse_args()
    
    # 텍스트 추출
    text = extract_text_from_ai(args.ai_file, method=args.method)
    
    if text.startswith("오류"):
        print(f"[ERROR] {text}")
        return 1
    
    # 결과 출력
    print("=" * 50)
    print("추출된 텍스트:")
    print("=" * 50)
    print(text)
    print("=" * 50)
    
    # 파일로 저장
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"\n텍스트가 저장되었습니다: {output_path}")
    else:
        # 기본 파일명으로 저장
        ai_path = Path(args.ai_file)
        output_path = ai_path.parent / (ai_path.stem + "_extracted_text.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"\n텍스트가 저장되었습니다: {output_path}")
    
    return 0


if __name__ == "__main__":
    exit(main())
