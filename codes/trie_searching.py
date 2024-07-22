import os
import json

# TODO: 질문들 엑셀 파일에서 들고와서 검색하기.
# TODO: 고도화1: 문제, 프로젝트, 대해, 관리 등 의미 없는 키워드 처리
# TODO: 고도화2: 질문들 문장 단위로 나누어서 검색할 수 있게 하기
# TODO: 트라이 구조를 활용하여 검색 기능 구현한 것 설명할 수 있게 학습하기.

class TrieNode:
    def __init__(self):
        """트라이 노드를 초기화합니다."""
        self.children = {}  # 자식 노드
        self.is_end_of_word = False  # 단어의 끝인지 여부
        self.subjects = []  # 해당 단어와 연관된 과목들

class Trie:
    def __init__(self):
        """트라이 구조를 초기화합니다."""
        self.root = TrieNode()
    
    def insert(self, word, subject):
        """단어와 과목을 트라이에 삽입합니다.
        
        Args:
            word (str): 삽입할 단어
            subject (str): 단어와 연관된 과목
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.subjects.append(subject)
    
    def search(self, word):
        """트라이에서 단어를 검색합니다.
        
        Args:
            word (str): 검색할 단어

        Returns:
            tuple: (단어의 끝 여부, 단어와 연관된 과목 리스트)
        """
        node = self.root
        for char in word:
            if char not in node.children:
                return False, []
            node = node.children[char]
        return node.is_end_of_word, node.subjects

def load_json_and_create_trie(json_file_paths):
    """여러 JSON 파일을 로드하고 트라이 구조를 생성합니다.
    
    Args:
        json_file_paths (list): JSON 파일 경로 리스트

    Returns:
        Trie: 생성된 트라이 구조
    """
    trie = Trie()
    for json_file_path in json_file_paths:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            index_dict = json.load(f)
        for term, subject in index_dict.items():
            trie.insert(term, subject)
    return trie

def search_questions_in_trie(trie, questions):
    """질문 리스트에서 키워드를 검색하여 결과를 반환합니다.
    
    Args:
        trie (Trie): 트라이 구조
        questions (list): 질문 리스트

    Returns:
        list: 각 질문에 대해 발견된 키워드와 연관된 과목 리스트를 포함한 결과 리스트
    """
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
    return results

# 상위 디렉토리 설정
json_directory = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/index'

# JSON 파일 경로 리스트 생성
json_file_paths = [os.path.join(json_directory, filename) for filename in os.listdir(json_directory) if filename.endswith('.json')]

# 트라이 생성
trie = load_json_and_create_trie(json_file_paths)

# 예제 질문 리스트
questions = [
    "SKT가 왜 지원자를 뽑아야 하는가?",
    "서비스 기업들이 많은데 왜 SKT를 오고 싶은가?",
    "다른 기업은 어느곳에 지원했나?",
    "그룹끼리 협동하여 도전하는 모습을 보여줘야하는 과제들이 굉장히 많이 출제됨",
    "기술적으로 깊이있는 질문을 했는데 특정 서비스의 로우레벨을 물어봤음 서비스 아이디에이션 PT는 어떻게할것인지? 그룹으로 하는 토의질문",
    "기술적인 트랜드를 어떻게 학습하는지, 대용량 트래픽 처리 경험, 알림 및 모니터링 관리",
    "어려운 문제 해결에 대해 접근하는 방법과해결하는 과정 및 코드리뷰",
    "딱히 기술적인 질문 중에 기억나는 건 없고 대부분 간단한 기술 질문 이었기 때문에 어렵지 않앗습니다",
    "MVC MVP MVVM과 같은 아키텍트 패턴 질문, 비동기 처리에 관한 질문, 프로젝트 경험 질문을 합니 다.",
    "리눅스 버전별 차이점, 프로젝트 진행 경험, 현재 skt 시스템에서 개선해야될점 어떻게하면 관리가 용 이할지 서술 발표시기 16일 후 불합격 보통 도움이 돼요 0",
    "SPA앱에서 메모리를 관리하는 방법? 디버깅하는 방법? 프로젝트하면서 어려웠던 경험?",
    "Use case를 바탕으로 최근 보안공격의 형태와 침해사고 유형별 시스템별을 설명하라. 4g/5g등 이동통신망의 구조와 5G보안공격, MEC에 대한 보안아키텍처 설계 방향성 설명",
    "1. 네트워크 망분리 찬성/반대 2. 어떤 소프트웨어 개발론을 도입해야 하는가? 3. WAS 관련 문제 4. 네트워크 쪽 문제 5. 인생그래프(가장 어려웠던 일, 영향을 끼친 일)"
]

# 질문 검색
search_results = search_questions_in_trie(trie, questions)

# 결과 출력
for result in search_results:
    print(result)
