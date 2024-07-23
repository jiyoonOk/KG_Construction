import os
from pdf_extractor import extract_text_from_pdf
from text_processor import extract_index_terms
from file_handler import save_to_json_file

def process_directory(parent_directory):
    """상위 디렉토리 내의 모든 디렉토리와 PDF 파일 처리"""
    for directory_name in os.listdir(parent_directory):
        directory_path = os.path.join(parent_directory, directory_name)
        if os.path.isdir(directory_path):
            all_terms_dict = {}
            for filename in os.listdir(directory_path):
                if filename.endswith('.pdf'):
                    filepath = os.path.join(directory_path, filename)
                    content_list = extract_text_from_pdf(filepath)
                    index_terms_dict = extract_index_terms(content_list, directory_name)
                    all_terms_dict.update(index_terms_dict)
            save_to_json_file(directory_name, all_terms_dict)

if __name__ == "__main__":
    parent_directory = '/Users/jiyoon/Downloads/기술면접 지식그래프/IT도서 찾아보기'
    process_directory(parent_directory)
