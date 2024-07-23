import os
import json

def save_to_json_file(directory_name, index_dict):
    """인덱스 딕셔너리를 JSON 파일로 저장"""
    save_directory = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/index'
    os.makedirs(save_directory, exist_ok=True)
    filename = os.path.join(save_directory, f'{directory_name}.json')
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(index_dict, f, ensure_ascii=False, indent=4)
        print(f"File '{filename}' has been saved (or overwritten) successfully.")
    except Exception as e:
        print(f"Error saving file {filename}: {e}")