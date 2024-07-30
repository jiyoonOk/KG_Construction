import os
import json
import pandas as pd
import unicodedata

def load_search_results(csv_path):
    """CSV 파일에서 검색 결과를 로드"""
    return pd.read_csv(csv_path)

def load_subjects_from_json(json_path):
    """JSON 파일에서 과목 리스트를 로드"""
    with open(json_path, 'r', encoding='utf-8') as f:
        subjects_dict = json.load(f)
    # 과목 리스트는 value 값들을 모두 모아 하나의 리스트로 만듭니다.
    subjects = list(subjects_dict.values())
    return subjects

def normalize_subject(subject):
    """과목 이름을 정규화하여 파일 이름으로 사용할 수 있도록 변환"""
    return unicodedata.normalize('NFKC', subject).replace('/', '_').replace('\\', '_')

def split_subjects_to_csv(results_df, subjects, output_directory):
    """subject별로 질문을 나눠 각각의 CSV 파일로 저장"""
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # 각 subject별로 질문을 나눠서 저장
    for subject in subjects:
        subject_questions = []
        subject_extracted_terms = []
        for idx, row in results_df.iterrows():
            subjects_dict = eval(row['subjects'])
            if subject in subjects_dict:
                subject_questions.append(row['question'])
                extracted_terms = ', '.join(subjects_dict[subject])
                subject_extracted_terms.append(extracted_terms)
        
        # 데이터프레임으로 변환
        subject_df = pd.DataFrame({
            'question': subject_questions,
            'extracted_terms': subject_extracted_terms
        })
        
        # 파일 이름 생성
        sanitized_subject = normalize_subject(subject)  # 파일 이름으로 사용할 수 없는 문자 대체
        subject_csv_path = os.path.join(output_directory, f'{sanitized_subject}.csv')
        
        # CSV 파일로 저장
        subject_df.to_csv(subject_csv_path, index=False, encoding='utf-8-sig')
        print(f"Saved {subject_csv_path} -> {len(subject_questions)}개")

def main():
    csv_path = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/results/기술면접_검색결과_키워드있음.csv'
    json_path = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/index/과목.json'
    output_directory = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/results/subjects'

    # CSV 파일 로드
    results_df = load_search_results(csv_path)

    # JSON 파일에서 과목 리스트 로드
    subjects = load_subjects_from_json(json_path)

    # subject별로 질문을 나눠 각각의 CSV 파일로 저장
    split_subjects_to_csv(results_df, subjects, output_directory)

if __name__ == "__main__":
    main()
