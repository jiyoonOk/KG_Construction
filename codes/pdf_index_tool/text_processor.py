import re
from ignore_terms import IGNORE_TERMS

# 상수 정의
REMOVE_PATTERN = r'\s*\d+(,\s*\d+)*$'               # 줄의 마지막 숫자 제거
SPLIT_PATTERN = r'\(|\)'                            # 괄호 안과 밖의 내용 분리          
SUB_SPLIT_PATTERN = r'[,;:]\s*|\s*과\s*|\s*와\s*'   
MIN_TERM_LENGTH = 1
ANGLE_BRACKET_PATTERN = r'<.>'                      # 꺾쇠 괄호와 그 안의 한 문자 제거

def extract_index_terms(content_list, directory_name):
    """텍스트에서 인덱스 용어 추출"""
    terms_dict = {}
    for line in content_list:
        line = clean_line(line)                             # 라인 클린업
        if line:
            terms = split_line_into_terms(line)             
            for term in terms:
                if term not in IGNORE_TERMS:
                    terms_dict[term] = directory_name       # 용어와 디렉토리 이름 매핑
    return terms_dict

def clean_line(line):
    """라인을 클린업하여 불필요한 부분 제거"""
    line = line.strip()                                         # 앞뒤 공백 제거
    line = re.sub(REMOVE_PATTERN, '', line)
    line = re.sub(ANGLE_BRACKET_PATTERN, '', line)
    return line if len(line) > MIN_TERM_LENGTH else None

def split_line_into_terms(line):
    """라인을 용어로 분리"""
    parts = re.split(SPLIT_PATTERN, line)                       # 괄호 안과 밖의 내용 분리
    terms = []
    for part in parts:
        part = part.strip()                                     # 문자열 앞뒤 공백 제거
        if len(part) > MIN_TERM_LENGTH:
            sub_parts = re.split(SUB_SPLIT_PATTERN, part)       
            terms.extend([sub.strip() for sub in sub_parts if len(sub.strip()) > MIN_TERM_LENGTH and not sub.isdigit()])
    return terms
