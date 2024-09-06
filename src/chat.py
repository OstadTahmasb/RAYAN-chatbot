import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_unstructured import UnstructuredLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class Tagger:

    def __init__(self):
        self.__init_tagging_chain()
        self.__init_translation_chain()
        self.__init_retriever()
        self.__init_retriever_chain()

    def __init_tagging_chain(self):
        tagging_prompt = ChatPromptTemplate.from_template(
            """Extract the customer's problem from the passage below.
        
        The problem can be tagged with one of the following options:
        
        <<<
        login: customer has problem logging in to classroom or is uninformed about the login credentials
        telegram: customer can't access the telegram channel or can't watch the recorded videos
        quera: customer can't access the quera(کوئرا، کوورا، کورا) website or doesn't know about the website at all
        >>>
        
        Only extract the properties mentioned in the 'Classification' function.
        
        Passage:
        {input}
        """
        )
        tagging_llm = ChatOpenAI(temperature=0, model="gpt-4o-mini").with_structured_output(Classification)
        self.tagging_chain = tagging_prompt | tagging_llm

    def __init_translation_chain(self):
        translation_prompt = ChatPromptTemplate.from_template(
            """Translate the text in the passage below to American English in a polite tone.
        Also, Extract the language it was written in.
        
        Passage:
        {input}
        """
        )
        translation_llm = ChatOpenAI(temperature=0, model="gpt-4o-mini").with_structured_output(Translation)
        self.translation_chain = translation_prompt | translation_llm

    def __init_retriever(self):
        loader = UnstructuredLoader("../data/data.txt")
        loaded_doc = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n"],
            chunk_size=10,
            chunk_overlap=0,
            length_function=len,
        )
        documents = splitter.split_documents(loaded_doc)
        vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings())
        self.retriever = vectorstore.as_retriever(K=5)

    def __init_retriever_chain(self):
        retriever_prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="message"),
                ("user",
                 """You are given the message above. Your task is to generate a search query to retrieve the relevant information asked in the message from a vectorstore. Do not use specific keywords. Only respond with the query, and nothing more."""),
            ]
        )

    def tag(self, inp) -> str:
        # translation = self.translation_chain.invoke({"input": inp})
        # result = self.tagging_chain.invoke({"input": translation.translation})
        result = self.tagging_chain.invoke({"input": inp})
        return result.problem

    def info(self, inp):



class Classification(BaseModel):
    problem: str = Field(..., enum=["login", "telegram", "quera"],
                         description="Describes the field in which there is a problem")


class Translation(BaseModel):
    translation: str = Field(description="The translated text to polite American English")
    language: str = Field(description="The language the original text was written in")
