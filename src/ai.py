import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_unstructured import UnstructuredLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories.file import FileChatMessageHistory

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class AI:

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.__init_tagging_chain()
        self.__init_translation_chain()
        self.__init_retrievers()
        self.__init_info_chains()

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
{input}"""
        )
        tagging_llm = ChatOpenAI(temperature=0, model="gpt-4o-mini").with_structured_output(Classification)
        self.tagging_chain = tagging_prompt | tagging_llm

    def __init_translation_chain(self):
        translation_prompt = ChatPromptTemplate.from_template(
            """Translate the text in the passage below to American English in a polite tone.
Also, Extract the language it was written in.
        
Passage:
{input}"""
        )
        translation_llm = ChatOpenAI(temperature=0, model="gpt-4o-mini").with_structured_output(Translation)
        self.translation_chain = translation_prompt | translation_llm

    def __init_retrievers(self):
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n"],
            chunk_size=10,
            chunk_overlap=0,
            length_function=len,
        )

        contest_loader = UnstructuredLoader("../data/contest_data.txt")
        contest_documents = splitter.split_documents(contest_loader.load())
        contest_vectorstore = FAISS.from_documents(contest_documents, OpenAIEmbeddings())
        self.contest_retriever = contest_vectorstore.as_retriever(K=5)

        courses_loader = UnstructuredLoader("../data/courses_data.txt")
        courses_document = splitter.split_documents(courses_loader.load())
        courses_vectorstore = FAISS.from_documents(courses_document, OpenAIEmbeddings())
        self.courses_retriever = courses_vectorstore.as_retriever(k=5)

    def __init_info_chains(self):
        query_generating_prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="messages"),
                ("user",
                 "You are given the messages above. Your task is to generate a search query to retrieve the relevant information asked in the messages from a vectorstore. Do not use specific keywords. Only respond with the query, and nothing more."),
            ]
        )

        contest_answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system",
                 """You are a helpful support bot. You are asked questions about the RAYAN AI International contest.
RAYAN AI International contest is a professional contest held by Sharif University. Contestants from all over the world compete to win cash prizes in a coding contest about Trustworthiness in Machine Learning.
Your task is to answer the question only based on the context below and other information already provided to you in the chat.
keep a polite tone and answer positively about the contest.
If you don't know the answer to a question just say something like 'I don't know' or something similar. Do not make up answers or data from your own or other sources.

>>>context
{context}
<<<
"""),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        contest_answer_chain = create_stuff_documents_chain(self.llm, contest_answer_prompt)
        self.contest_info_chain = (RunnablePassthrough
                                   .assign(context=(
                                            query_generating_prompt
                                            | self.llm
                                            | StrOutputParser()
                                            | self.contest_retriever))
                                   .assign(response=contest_answer_chain))

        courses_answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system",
                 """You are a helpful support bot. You are asked questions about the educational courses held to prepare participants for the RAYAN AI International contest.
RAYAN AI International contest is a professional contest held by Sharif University. Contestants from all over the world compete to win cash prizes in a coding contest about Trustworthiness in Machine Learning.
Two educational courses are held by Sharif University professors who teach the subjects needed for the contest.
Your task is to answer the question only based on the context below and other information already provided to you in the chat.
keep a polite tone and answer positively about the contest.
If you don't know the answer to a question just say something like 'I don't know' or something similar. Do not make up answers or data from your own or other sources.

>>>context
{context}
<<<
"""),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        courses_answer_chain = create_stuff_documents_chain(self.llm, courses_answer_prompt)
        self.courses_info_chain = (RunnablePassthrough
                                   .assign(context=
                                           query_generating_prompt
                                           | self.llm
                                           | StrOutputParser()
                                           | self.courses_retriever)
                                   .assign(response=courses_answer_chain))

    def tag(self, inp) -> str:
        # translation = self.translation_chain.invoke({"input": inp})
        # result = self.tagging_chain.invoke({"input": translation.translation})
        result = self.tagging_chain.invoke({"input": inp})
        return result.problem

    def get_contest_info(self, inp, id):
        path = "../history/" + str(id)
        if not os.path.exists(path):
            os.mkdir(path)
        history = FileChatMessageHistory(path + "/his")
        history.add_user_message(inp)
        messages = history.messages
        response = self.contest_info_chain.invoke({"messages": messages})
        return response

    def get_courses_info(self, inp):
        history = FileChatMessageHistory("his")
        history.add_user_message(inp)
        messages = history.messages
        response = self.courses_info_chain.invoke({"messages": messages})
        return response


class Classification(BaseModel):
    problem: str = Field(..., enum=["login", "telegram", "quera"],
                         description="Describes the field in which there is a problem")


class Translation(BaseModel):
    translation: str = Field(description="The translated text to polite American English")
    language: str = Field(description="The language the original text was written in")
