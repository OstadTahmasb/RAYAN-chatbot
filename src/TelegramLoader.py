from langchain_community.document_loaders import TelegramChatFileLoader

loader = TelegramChatFileLoader("../data/RAYAN_AI_CHANNEL.json")
docs = loader.load()
print(docs)
