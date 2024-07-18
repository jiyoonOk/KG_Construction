import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import ast

def safe_eval_questions(question):
    """ 문자열 형태의 리스트를 파싱하고, 공백으로 구분된 문자열로 벼놘"""
    if isinstance(question, str):
        try:
            question_list = ast.literal_eval(question)
            return ' '.join(question_list)
        except (SyntaxError, ValueError):
            return ''
    return ''

def extract_keywords_from_questions(csv_file, output_file):
    data = pd.read_csv(csv_file)
    questions = data['면접질문'].dropna().apply(safe_eval_questions)


    # 면접 질문을 텍스트 파일로 저장
    with open("./interview_questions.txt", 'w', encoding='utf-8') as f:
        for question in questions:
            f.write(question + '\n')
    
    vectorizer = TfidfVectorizer(max_features=100)
    tfidf_matrix = vectorizer.fit_transform(questions)
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.sum(axis=0).A1
    keywords_df = pd.DataFrame({'Keyword': feature_names, 'Score': tfidf_scores})
    keywords_df = keywords_df.sort_values(by='Score', ascending=False)
    # 결과를 텍스트 파일로 출력
    keywords_df.to_csv(output_file, sep='\t', index=False)
    return keywords_df

def extract_keywords_by_company(csv_file, output_file):
    data = pd.read_csv(csv_file)
    # 먼저 문자열 확인과 NaN 제거
    data['면접질문'] = data['면접질문'].dropna().apply(safe_eval_questions)
    
    grouped = data.groupby('회사명')
    company_keywords = {}

    for company, group in grouped:
        # 그룹 내 면접질문에서 NaN이 존재하는지 추가 확인
        group['면접질문'] = group['면접질문'].fillna('')  # NaN을 빈 문자열로 대체

        if not group['면접질문'].empty:
            vectorizer = TfidfVectorizer(max_features=10)
            # 그룹별 면접 질문에 대해 TF-IDF 계산
            tfidf_matrix = vectorizer.fit_transform(group['면접질문'])
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.sum(axis=0).A1
            keywords_df = pd.DataFrame({'Keyword': feature_names, 'Score': tfidf_scores})
            keywords_df = keywords_df.sort_values(by='Score', ascending=False)
            company_keywords[company] = keywords_df

    # 모든 기업별 결과를 하나의 파일에 저장
    with open(output_file, 'w') as f:
        for company, df in company_keywords.items():
            f.write(f"### {company} ###\n")
            df.to_csv(f, sep='\t', index=False)
            f.write("\n")
    return company_keywords
    
# CSV 파일 경로 지정
csv_file_path = 'interview_QA'

# 각 결과를 텍스트 파일로 출력
keywords_df = extract_keywords_from_questions(csv_file_path, './keyword.txt')
# company_keywords = extract_keywords_by_company(csv_file_path, './keyword_bycom.txt')
