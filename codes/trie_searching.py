import os
import json
import pandas as pd

# 질문들 엑셀 파일에서 들고와서 검색하기. O
# TODO: 고도화1: 문제, 프로젝트, 서비스 등 보편적인 단어라서 많이 겹치는 키워드 처리 어떻게?
# TODO: 고도화2: 질문들 문장 단위로 나누어서 검색할 수 있게 하기
# 트라이 구조를 활용하여 검색 기능 구현한 것 설명할 수 있게 학습하기. O

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
        subject = subject.replace('_', ' ')             # 과목 이름에 있는 '_'를 공백으로 대체

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
    
    """트라이를 재귀적으로 사전으로 변환"""
    def to_dict(self):
        def node_to_dict(node):
            node_dict = {
                "is_end_of_word": node.is_end_of_word,
                "subjects": node.subjects,
                "children": {char: node_to_dict(child) for char, child in node.children.items()}
            }
            return node_dict
        return node_to_dict(self.root)

"""여러 JSON 파일을 로드하고 트라이 구조를 생성"""
def load_json_and_create_trie(json_file_paths):
    trie = Trie()                                                   # 트라이 생성
    for json_file_path in json_file_paths:                          # JSON 파일 경로(list)에 대해 반복
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:      # JSON 파일 열기
                index_dict = json.load(f)                               # JSON 파일 로드
            for term, subject in index_dict.items():                    # 인덱스 딕셔너리의 각 항목에 대해 반복
                trie.insert(term, subject)                              # 트라이에 단어 삽입
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {json_file_path}: {e}")
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
                    if word not in result["subjects"][subject]:
                        result["subjects"][subject].append(word)            
        results.append(result)
    return results                                                      # list: 각 질문에 대해 발견된 키워드와 연관된 과목 리스트를 포함한 결과

def save_results_to_csv(results, output_path):
    """검색 결과를 CSV 파일로 저장"""
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_path, index=False, encoding='utf-8-sig')

def main():
    # 엑셀 파일 경로
    xlsx_path = '/Users/jiyoon/Downloads/기술면접 지식그래프/질문모음.xlsx'
    
    # 엑셀 파일에서 질문 리스트 로드
    try:
        questions_df = pd.read_excel(xlsx_path)
        questions = questions_df['질문'].dropna().astype(str).tolist()
    except FileNotFoundError:
        print(f"Excel file not found: {xlsx_path}")
        return
    
    # 상위 디렉토리 설정
    json_directory = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/index'
    
    # JSON 파일 경로 리스트 생성
    json_file_paths = [os.path.join(json_directory, filename) for filename in os.listdir(json_directory) if filename.endswith('.json')]
    
    # 트라이 생성
    trie = load_json_and_create_trie(json_file_paths)
    
    # 임의로 추가할 단어와 과목 리스트
    words_subjects_list = [
        ("네트워크", "네트워크"),
        ("데이터 통신", "데이터 통신"),
        ("데이터베이스", "데이터베이스"),
        ("리눅스", "리눅스"),
        ("머신러닝", "머신러닝"),
        ("빅데이터", "빅데이터"),
        ("소프트웨어 공학", "소프트웨어 공학"),
        ("알고리즘", "알고리즘"),
        ("자료구조", "자료구조"),
        ("컴퓨터 구조", "컴퓨터 구조"),
        ("컴퓨터 그래픽", "컴퓨터 그래픽"),
        ("컴퓨터 보안", "컴퓨터 보안"),
        ("C#", "C#"),
        ("C++", "C++언어"),
        ("C", "C언어"),
        ("JAVA", "JAVA"),
        ("OpenCV", "OpenCV"),
        ("Python", "Python"),
        ("web programming", "web programming")
    ]
    
    # 트라이에 임의의 단어와 과목 추가
    for word, subject in words_subjects_list:
        trie.insert(word, subject)
    
    # 질문 검색
    search_results = search_questions_in_trie(trie, questions)

    # 결과 엑셀 파일로 저장
    output_path = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/results/기술면접_검색결과.csv'
    save_results_to_csv(search_results, output_path)
    print(f"Results saved to {output_path}")
    
    # 결과 출력
    for result in search_results:
        print(result)
    
    # 트라이 구조를 JSON으로 저장
    trie_structure_path = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/results/trie_structure.json'
    try:
        with open(trie_structure_path, 'w', encoding='utf-8') as f:
            json.dump(trie.to_dict(), f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error saving trie structure to {trie_structure_path}: {e}")

if __name__ == "__main__":
    main()