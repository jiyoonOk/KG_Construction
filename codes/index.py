import fitz  # PyMuPDF 모듈, PDF 파일 작업을 위한 라이브러리
import re
import os
import json

# 상수 정의
REMOVE_PATTERN = r'\s*\d+(,\s*\d+)*$'               # 줄의 마지막 숫자 제거
SPLIT_PATTERN = r'\(|\)'                            # 괄호 안과 밖의 내용 분리          
SUB_SPLIT_PATTERN = r'[,;:]\s*|\s*과\s*|\s*와\s*'   
IGNORE_TERMS = ["찾아보기", "기호", "색인", "| 찾아보기 |", "<기호>"]           # 무시할 용어
MIN_TERM_LENGTH = 1
ANGLE_BRACKET_PATTERN = r'<.>'  # 꺾쇠 괄호와 그 안의 한 문자 제거

def extract_text_from_pdf(filename):
    """PDF 파일에서 텍스트를 추출합니다."""
    content_list = []
    pages = fitz.open(filename)  # PDF 파일 열기
    for page in pages:
        text = page.get_text()  # 페이지의 텍스트 추출
        doc2list = text.split("\n")  # 텍스트를 줄 단위로 분할
        content_list.extend(doc2list)  # 줄 단위 텍스트를 content_list에 추가
    return content_list

def extract_index_terms(content_list, directory_name):
    """텍스트에서 인덱스 용어를 추출합니다."""
    terms_dict = {}
    for line in content_list:
        line = line.strip()  # 앞뒤 공백 제거
        
        # 줄의 마지막 숫자 제거
        line = re.sub(REMOVE_PATTERN, '', line)

        # 꺾쇠 괄호와 그 안의 내용 제거
        line = re.sub(ANGLE_BRACKET_PATTERN, '', line)
        
        # 괄호 안과 밖의 내용 분리
        parts = re.split(SPLIT_PATTERN, line)
        
        for part in parts:
            part = part.strip()  # 문자열 앞뒤 공백 제거
            if len(part) <= MIN_TERM_LENGTH:
                continue
            
            # 쉼표, 세미콜론, 콜론, '과', '와'로 분리
            sub_parts = re.split(SUB_SPLIT_PATTERN, part)
            for sub_part in sub_parts:
                sub_part = sub_part.strip()
                if sub_part and len(sub_part) > MIN_TERM_LENGTH:
                    terms_dict[sub_part] = directory_name
    
    return terms_dict

def remove_unwanted_terms(terms_dict):
    """숫자로만 이루어진 용어와 무시할 용어를 제거합니다."""
    return {term: subject for term, subject in terms_dict.items() if not term.isdigit() and term not in IGNORE_TERMS}

def extract_index_from_pdf(filename, directory_name):
    """PDF 파일에서 인덱스를 추출합니다."""
    content_list = extract_text_from_pdf(filename)
    terms_dict = extract_index_terms(content_list, directory_name)
    terms_dict = remove_unwanted_terms(terms_dict)
    return terms_dict

def save_to_json_file(directory_name, index_dict):
    """인덱스 딕셔너리를 JSON 파일로 저장합니다."""
    save_directory = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/index'
    os.makedirs(save_directory, exist_ok=True)
    filename = os.path.join(save_directory, f'{directory_name}.json')
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(index_dict, f, ensure_ascii=False, indent=4)

# 상위 디렉토리 설정
parent_directory = '/Users/jiyoon/Downloads/기술면접 지식그래프/IT도서 찾아보기'

# 상위 디렉토리 내의 모든 디렉토리 순회
for directory_name in os.listdir(parent_directory):
    directory_path = os.path.join(parent_directory, directory_name)
    if os.path.isdir(directory_path):  # 디렉토리인지 확인
        all_terms_dict = {}
        # 디렉토리 내의 모든 PDF 파일 순회
        for filename in os.listdir(directory_path):
            if filename.endswith('.pdf'):
                filepath = os.path.join(directory_path, filename)
                # PDF에서 인덱스 추출
                index_terms_dict = extract_index_from_pdf(filepath, directory_name)
                all_terms_dict.update(index_terms_dict)
        
        # JSON 파일로 저장
        save_to_json_file(directory_name, all_terms_dict)
