import os
import json
import pandas as pd

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.subjects = []

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, subject):
        subject = subject.replace('_', ' ')
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.subjects.append(subject)

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False, []
            node = node.children[char]
        return node.is_end_of_word, node.subjects

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def collect_all_words(self, node=None, prefix='', words=None):
        if words is None:
            words = []
        if node is None:
            node = self.root
        
        if node.is_end_of_word:
            words.append((prefix, node.subjects))
        
        for char, child_node in node.children.items():
            self.collect_all_words(child_node, prefix + char, words)
        
        return words

    def to_dict(self):
        def node_to_dict(node):
            node_dict = {
                "is_end_of_word": node.is_end_of_word,
                "subjects": node.subjects,
                "children": {char: node_to_dict(child) for char, child in node.children.items()}
            }
            return node_dict
        return node_to_dict(self.root)

def load_json_and_create_trie(json_file_paths):
    trie = Trie()
    for json_file_path in json_file_paths:
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                index_dict = json.load(f)
            for term, subject in index_dict.items():
                trie.insert(term, subject)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {json_file_path}: {e}")
    return trie

def search_questions_in_trie(trie, questions_df):
    results = []
    for idx, row in questions_df.iterrows():
        question = row['면접질문']
        result = {
            "회사명": row['회사명'],
            "면접질문": question,
            "면접답변 혹은 면접느낌": row['면접답변 혹은 면접느낌'],
            "subjects": {}
        }
        length = len(question)
        for i in range(length):
            node = trie.root
            last_found_word = None
            last_subjects = []
            current_depth = 0
            for j in range(i, length):
                if question[j] not in node.children:
                    break
                node = node.children[question[j]]
                if node.is_end_of_word and (j - i + 1) > current_depth:
                    last_found_word = question[i:j+1]
                    last_subjects = node.subjects
                    current_depth = j - i + 1
            if last_found_word:
                for subject in last_subjects:
                    if subject not in result["subjects"]:
                        result["subjects"][subject] = []
                    if last_found_word not in result["subjects"][subject]:
                        result["subjects"][subject].append(last_found_word)
        results.append(result)
    return results

def save_separated_results(results, keywords_output_path, no_keywords_output_path):
    keywords_results = [result for result in results if result["subjects"]]
    no_keywords_results = [result for result in results if not result["subjects"]]
    
    keywords_df = pd.DataFrame(keywords_results)
    no_keywords_df = pd.DataFrame(no_keywords_results)
    
    keywords_df.to_csv(keywords_output_path, index=False, encoding='utf-8-sig')
    no_keywords_df.to_csv(no_keywords_output_path, index=False, encoding='utf-8-sig')

def main():
    xlsx_path = '/Users/jiyoon/Downloads/기술면접 지식그래프/면접후기2.xlsx'
    
    try:
        questions_df = pd.read_excel(xlsx_path, usecols=["회사명", "면접질문", "면접답변 혹은 면접느낌"])
        questions_df = questions_df.dropna(subset=['면접질문'])
    except FileNotFoundError:
        print(f"Excel file not found: {xlsx_path}")
        return
    
    json_directory = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/index'
    json_file_paths = [os.path.join(json_directory, filename) for filename in os.listdir(json_directory) if filename.endswith('.json')]
    
    trie = load_json_and_create_trie(json_file_paths)
    
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
    
    for word, subject in words_subjects_list:
        trie.insert(word, subject)
    
    search_results = search_questions_in_trie(trie, questions_df)

    keywords_output_path = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/results/회사정보_기술면접_검색결과_키워드있음.csv'
    no_keywords_output_path = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/results/회사정보_기술면접_검색결과_키워드없음.csv'
    save_separated_results(search_results, keywords_output_path, no_keywords_output_path)
    print(f"Results with keywords saved to {keywords_output_path}")
    print(f"Results without keywords saved to {no_keywords_output_path}")
    
    for result in search_results:
        print(result)
    
    trie_structure_path = '/Users/jiyoon/Downloads/기술면접 지식그래프/KG_Construction/codes/results/trie_structure.json'
    try:
        with open(trie_structure_path, 'w', encoding='utf-8') as f:
            json.dump(trie.to_dict(), f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error saving trie structure to {trie_structure_path}: {e}")

if __name__ == "__main__":
    main()
