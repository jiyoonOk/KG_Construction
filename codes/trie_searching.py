import os
import json
import pandas as pd

# TODO: 질문들 엑셀 파일에서 들고와서 검색하기.
# TODO: 고도화1: 문제, 프로젝트, 서비스 등 보편적인 단어라서 많이 겹치는 키워드 처리 어떻게?
# TODO: 고도화2: 질문들 문장 단위로 나누어서 검색할 수 있게 하기
# TODO: 트라이 구조를 활용하여 검색 기능 구현한 것 설명할 수 있게 학습하기.

"""트라이 구조의 장점 : 빠른 검색 속도, 메모리 효율적 사용(중복 단어 처리, 접두사 공유), 문자열 검색에 특화, 자동 완성 및 사전 기능"""

class TrieNode:
    """트라이 노드 초기화"""
    def __init__(self):                 # self: 현재 인스턴스
        self.children = {}              # 자식 노드
        self.is_end_of_word = False     # 단어의 끝인지 여부
        self.subjects = []              # 해당 단어와 연관된 과목들의 리스트. 예를 들어, 단어 "암호"가 "컴퓨터 과학"과 "정보 보안" 두 과목과 연관되어 있다면, "암호" 노드의 subjects 리스트에 ["컴퓨터 과학", "정보 보안"]이 저장

class Trie:
    """트라이 구조 초기화"""
    def __init__(self):                 
        self.root = TrieNode()          # 루트 노드 생성
    
    """트라이에 단어를 삽입하고, 단어와 연관된 과목을 저장."""
    def insert(self, word, subject):                    # word: 삽입할 단어, subject: 단어와 연관된 과목
        node = self.root                                # 루트 노드부터 시작
        for char in word:                               # 단어의 각 문자에 대해
            if char not in node.children:               # 자식 노드에 문자가 없으면
                node.children[char] = TrieNode()        # 새로운 노드 생성
            node = node.children[char]                  # 다음 노드로 이동
        node.is_end_of_word = True                      # 단어의 끝을 표시
        node.subjects.append(subject)                   # 단어와 연관된 과목 추가
    
    """트라이에서 단어를 검색하고, 단어의 끝 여부와 연관된 과목 리스트를 반환."""
    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:               
                return False, []                        
            node = node.children[char]                  
        return node.is_end_of_word, node.subjects       

"""여러 JSON 파일을 로드하고 트라이 구조를 생성"""
def load_json_and_create_trie(json_file_paths):
    trie = Trie()                                                   # 트라이 생성
    for json_file_path in json_file_paths:                          # JSON 파일 경로(list)에 대해 반복
        with open(json_file_path, 'r', encoding='utf-8') as f:      # JSON 파일 열기
            index_dict = json.load(f)                               # JSON 파일 로드
        for term, subject in index_dict.items():                    # 인덱스 딕셔너리의 각 항목에 대해 반복
            trie.insert(term, subject)                              # 트라이에 단어 삽입
    return trie

"""트라이에서 키워드를 검색하여 결과를 반환"""
def search_questions_in_trie(trie, questions):
    results = []
    for question in questions:
        result = {"question": question, "subjects": {}}
        words = question.split()                                        
        for word in words:
            found, subjects = trie.search(word)                         
            if found:                                                   
                for subject in subjects:                                
                    if subject not in result["subjects"]:               
                        result["subjects"][subject] = []                
                    result["subjects"][subject].append(word)            
        results.append(result)
    return results                                                      # list: 각 질문에 대해 발견된 키워드와 연관된 과목 리스트를 포함한 결과

# 엑셀 파일 경로
xlsx_path = '/Users/jiyoon/Downloads/기술면접 지식그래프/질문모음.xlsx'

# 엑셀 파일에서 질문 리스트 로드
questions_df = pd.read_excel(xlsx_path)
questions = questions_df['질문'].dropna().astype(str).tolist()                      # 질문 열에서 NaN 제거하고 리스트로 변환

# 상위 디렉토리 설정
json_directory = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/index'

# JSON 파일 경로 리스트 생성
json_file_paths = [os.path.join(json_directory, filename) for filename in os.listdir(json_directory) if filename.endswith('.json')]

# 트라이 생성
trie = load_json_and_create_trie(json_file_paths)

# 질문 검색
search_results = search_questions_in_trie(trie, questions)

# 결과 출력
for result in search_results:
    print(result)
