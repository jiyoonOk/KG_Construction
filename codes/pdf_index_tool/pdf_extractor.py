import fitz

def extract_text_from_pdf(filename):
    """PDF 파일에서 텍스트를 추출합니다."""
    content_list = []
    try:
        with fitz.open(filename) as pdf_document:                   # pdf_document는 pdf 파일을 열어서 읽을 수 있는 객체
            for page in pdf_document:
                text = page.get_text()
                content_list.extend(text.split("\n"))
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
    return content_list
