import fitz
import os
import csv
from tqdm import tqdm
import re

def extract_relevant_sections(filename): ## pdf 1개는 여러 페이지로 구성됨
    sections = []
    current_section = []
    capture = False

    content_list = []
    pages = fitz.open(filename)
    for page in pages:
        text = page.get_text()
        doc2list = text.split("\n")
        content_list.extend(doc2list)

        
    for line in content_list:
        line = line.strip()  # Remove leading/trailing whitespace
        # print(line)
        if line.startswith("개발"):
            capture = True
            if current_section:  # Save previous section
                sections.append(current_section)
                current_section = []
        # print(sections)
        if capture:
            current_section.append(line)
        # print(sections)
        if "도움이 돼요" in line:
            capture = False
            if current_section:
                sections.append(current_section)
                current_section = []
        # print(sections)
    
    return sections


def parse_section_to_dict(section, com_name):
    section_dict = {}
    i = 0
    while i < len(section):
        line = section[i]
        if "개발" in line:
            parts = line.split("\xa0/\xa0")
            section_dict["직무"] = parts[1][1:4].strip() if len(parts) > 1 else ""
        elif "면접난이도" in line:
            section_dict["면접난이도"] = section[i + 1].strip() if i + 1 < len(section) else ""
        elif "면접일자" in line:
            section_dict["면접일자"] = section[i + 1].strip() if i + 1 < len(section) else ""
        elif "면접경로" in line:
            section_dict["면접경로"] = section[i + 1].strip() if i + 1 < len(section) else ""
        elif "면접질문" in line:
            questions = []
            i += 1
            while i < len(section) and not section[i].startswith("면접답변") and not section[i].startswith("면접결과"):
                questions.append(section[i].strip())
                i += 1
            section_dict["면접질문"] = questions
            i -= 1  # Adjust index after loop
        elif "면접답변" in line:
            answers = []
            i += 1
            while i < len(section) and not section[i].startswith("발표시기"):
                answers.append(section[i].strip())
                i += 1
            section_dict["면접답변 혹은 면접느낌"] = " ".join(answers)
            i -= 1  # Adjust index after loop
        elif "합격" in line or "불합격" in line:
            section_dict["면접결과"] = "합격" if "합격" in line else "불합격"
            
        section_dict["회사명"] =  com_name
            
        i += 1
    
    return section_dict


def save_dicts_to_csv(dicts, output_filename):
    # 미리 정의된 필드 목록
    predefined_fields = ['회사명', '직무', '면접난이도', '면접일자', '면접경로', '면접질문', '면접답변 혹은 면접느낌', '면접결과']
    
    # 파일이 존재하는지와 파일이 비어있는지 확인 ㅎㅔ더 중복으로 쓰이는것 방지
    file_exists = os.path.exists(output_filename)
    should_write_header = not file_exists or os.stat(output_filename).st_size == 0
    
    with open(output_filename, 'a', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=predefined_fields)
        
        # 파일이 새로 생성되거나 비어있으면 헤더를 쓴다
        if should_write_header:
            dict_writer.writeheader()
        
        for d in dicts:
            # 필드에 값이 없는 경우 비워두기 위해 미리 필드를 설정
            filtered_dict = {field: d.get(field, '') for field in predefined_fields}
            dict_writer.writerow(filtered_dict)



def list_directories_excluding_parent(directory, exclude):
    # Get parent directory
    parent_directory = os.path.dirname(directory)
    # Get all items in the parent directory
    items = os.listdir(parent_directory)
    # Filter out items that are not directories or are the excluded directory
    directories = [item for item in items if os.path.isdir(os.path.join(parent_directory, item)) and item != exclude]
    
    return directories

# 현재 디렉토리와 제외할 디렉토리를 지정
current_directory = os.getcwd()
exclude_directory = 'codes'
# Get parent directory
parent_directory = os.path.dirname(current_directory) ##/Users/hyejinpark/Desktop/interview_it
# Get all items in the parent directory
items = os.listdir(parent_directory)
# Filter out items that are not directories or are the excluded directory
directories = [item for item in items if os.path.isdir(os.path.join(parent_directory, item)) and item != exclude_directory]



for dir in tqdm(directories):
    com_name = dir
    dirpath = "../"+dir
    all_files = os.listdir(dirpath)
    # "page_"로 시작하고 ".pdf"로 끝나는 파일 필터링
    pdf_files = [file for file in all_files if file.startswith("page_") and file.endswith(".pdf")]
    # 파일을 숫자 기준으로 정렬
    sorted_files = sorted(pdf_files, key=lambda x: int(re.search(r'\d+', x).group()))

    ##pdf_file 처리
    for files in sorted_files:
        filename = dirpath+"/"+files
        sections = extract_relevant_sections(filename)
        section_dicts = [parse_section_to_dict(section, com_name) for section in sections]

        save_dicts_to_csv(section_dicts, "./interview_QA")