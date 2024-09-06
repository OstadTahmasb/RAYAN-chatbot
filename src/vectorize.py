from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_unstructured import UnstructuredLoader

import dotenv
import pickle

if __name__ == "__main__":
    dotenv.load_dotenv()
    loader = UnstructuredLoader("../data/data.txt")
    splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n'],
        chunk_size=20,
        chunk_overlap=0,
        length_function=len,
    )
    loaded_doc = loader.load()
    documents = splitter.split_documents(loaded_doc)
    for doc in documents:
        print(doc.page_content.strip())
        print('-' * 80)
    vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings())
    with open("../data/vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)
