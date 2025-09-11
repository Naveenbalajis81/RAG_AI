from langchain_community.document_loaders import PyPDFLoader

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyPDFLoader."""
    loader = PyPDFLoader(pdf_path)
    documents = loader.load_and_split()
    text = "\n".join([doc.page_content for doc in documents])
    return text.strip()


# loader = PyPDFLoader(file_path)
# pages=[]
# pages = loader.load_and_split()
# print(pages[0].page_content)
# print(len(pages))


# import fitz  # PyMuPDF for PDF extraction

# def extract_text_from_pdf(pdf_path: str) -> str:
#     """Extract text from PDF using PyMuPDF."""
#     text = []
#     with fitz.open(pdf_path) as doc:
#         for page in doc:
#             page_text = page.get_text("text")  # explicitly request text
#             if page_text:
#                 text.append(page_text)
#     return "\n".join(text).strip()

