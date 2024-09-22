from langchain_community.document_loaders import TelegramChatFileLoader
from langchain_core.documents import Document

loader = TelegramChatFileLoader("../data/RAYAN_AI_CHANNEL.json")
docs = loader.load()
print(docs)
