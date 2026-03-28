from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_deepseek import ChatDeepSeek

from app.common import LLM_API_BASE, LLM_API_KEY
from app.docs_manager import vector_store

retriever = vector_store.as_retriever(search_kwargs={"k": 3})
base_deepseek = ChatDeepSeek(
    model='DeepSeek-V3',
    api_base=LLM_API_BASE,
    api_key=LLM_API_KEY,
)

streaming_deepseek = ChatDeepSeek(
    model='DeepSeek-V3',
    api_base=LLM_API_BASE,
    api_key=LLM_API_KEY,
    streaming=True,
)

# === 使用history awareness ===
# 1. 检索
contextualize_system_prompt = ("你将接收一段对话记录和一个用户的最新提问，"
                               "这个提问可能和对话记录中的内容有关联。"
                               "你需要将这个用户最新提问重新构造，使其包含对话记录中的相关内容。"
                               "你**不需要**回答用户最后的问题！"
                               "只需要输出经过重新构造的用户最新问题，确保它附带对话记录中的有关内容。"
                               "如果你认为对话记录中没有与用户最新提问有关的内容，则原样返回用户的最新提问。"
                               )
contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}")
])
history_aware_retriever = create_history_aware_retriever(
    llm=base_deepseek,
    retriever=retriever,
    prompt=contextualize_prompt,
)

# 2. 回答问题
qa_system_prompt = """你可以利用下面的Context来辅助你回答问题。如果你认为Context和用户提出的问题没有关联，就忽略Context。

Context:
{context}
"""

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", qa_system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}")
])

question_answer_chain = create_stuff_documents_chain(
    llm=base_deepseek,
    prompt=qa_prompt,
)

question_answer_chain_streaming = create_stuff_documents_chain(
    llm=streaming_deepseek,
    prompt=qa_prompt,
)

# 组装：非streaming和streaming
historical_rag_chain = create_retrieval_chain(
    history_aware_retriever, question_answer_chain
)

historical_rag_chain_streaming = create_retrieval_chain(
    history_aware_retriever, question_answer_chain_streaming
)

# === 不使用history awareness ===
rag_chain = create_retrieval_chain(
    retriever=retriever,
    combine_docs_chain=question_answer_chain
)

rag_chain_streaming = create_retrieval_chain(
    retriever=retriever,
    combine_docs_chain=question_answer_chain_streaming
)
