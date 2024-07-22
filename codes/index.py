import fitz  # PyMuPDF 모듈, PDF 파일 작업을 위한 라이브러리
import re
import os

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

def extract_index_terms(content_list):
    """텍스트에서 인덱스 용어를 추출합니다."""
    terms = []
    for line in content_list:
        line = line.strip()  # 앞뒤 공백 제거
        
        # 줄의 마지막 숫자 제거
        line = re.sub(REMOVE_PATTERN, '', line)

        # 꺾쇠 괄호와 그 안의 내용 제거
        line = re.sub(ANGLE_BRACKET_PATTERN, '', line)
        
        # 괄호 안과 밖의 내용 분리
        parts = re.split(SPLIT_PATTERN, line)  # parts: "근거리 통신망(LAN; Local Area Network)" -> ['근거리 통신망', 'LAN; Local Area Network', '']
        
        for part in parts:
            part = part.strip()  # 문자열 앞뒤 공백 제거
            if len(part) <= MIN_TERM_LENGTH:
                continue
            
            # 쉼표, 세미콜론, 콜론, '과', '와'로 분리
            sub_parts = re.split(SUB_SPLIT_PATTERN, part)  # 예: ['LAN', 'Local Area Network']
            terms.extend([t.strip() for t in sub_parts if t.strip() and len(t.strip()) > MIN_TERM_LENGTH])
    
    # 중복 제거 및 빈 문자열 제거
    terms = list(dict.fromkeys(terms))  # 중복 제거
    
    return terms

def remove_unwanted_terms(terms):
    """숫자로만 이루어진 용어와 무시할 용어를 제거합니다."""
    return [term for term in terms if not term.isdigit() and term not in IGNORE_TERMS]

def extract_index_from_pdf(filename):
    """PDF 파일에서 인덱스를 추출합니다."""
    content_list = extract_text_from_pdf(filename)
    terms = extract_index_terms(content_list)
    terms = remove_unwanted_terms(terms)
    return terms

def convert_index_to_text(terms):
    """추출된 인덱스 텍스트로 변환합니다."""
    # 중복 제거하지 않고 순서를 유지
    text = ', '.join(terms)
    return text

def save_to_python_file(directory_name, index_text):
    """인덱스 텍스트를 디렉토리명으로 된 파이썬 파일로 저장합니다."""
    save_directory = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/index'
    os.makedirs(save_directory, exist_ok=True)
    filename = os.path.join(save_directory, f'{directory_name}.py')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {directory_name} 인덱스 용어\n")
        f.write(f"index_terms = '''{index_text}'''\n")

# 상위 디렉토리 설정
parent_directory = '/Users/jiyoon/Downloads/기술면접 지식그래프/IT도서 찾아보기'

# 상위 디렉토리 내의 모든 디렉토리 순회
for directory_name in os.listdir(parent_directory):
    directory_path = os.path.join(parent_directory, directory_name)
    if os.path.isdir(directory_path):  # 디렉토리인지 확인
        all_terms = []
        # 디렉토리 내의 모든 PDF 파일 순회
        for filename in os.listdir(directory_path):
            if filename.endswith('.pdf'):
                filepath = os.path.join(directory_path, filename)
                # PDF에서 인덱스 추출
                index_terms = extract_index_from_pdf(filepath)
                all_terms.extend(index_terms)
        
        # 인덱스 텍스트로 변환
        index_text = convert_index_to_text(all_terms)

        # 파이썬 파일로 저장
        save_to_python_file(directory_name, index_text)