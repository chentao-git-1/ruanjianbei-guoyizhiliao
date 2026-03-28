import os
import shutil
from typing import List

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.common import DOC_DIR
from app.docs_manager import ingest, delete
from app.rag_chain import rag_chain, rag_chain_streaming, base_deepseek, streaming_deepseek, historical_rag_chain, historical_rag_chain_streaming
from app.schema import ChatRequest, Message, FileRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/docs/upload")
async def upload(file: UploadFile = File(...)):
    path = os.path.normpath(os.path.join(DOC_DIR, file.filename))
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    count = ingest(path)
    return {"added_chunks": count}


@app.get("/docs/list")
def list_docs():
    files = os.listdir(DOC_DIR)
    return {"files": files}


@app.get("/docs/download")
def download_doc(req: FileRequest):
    path = os.path.normpath(os.path.join(DOC_DIR, req.filename))
    if not os.path.exists(path):
        return {"success": False, "message": "File not found"}
    return FileResponse(path=path, filename=req.filename)


@app.post("/docs/delete")
async def delete_file(req: FileRequest):
    path = os.path.normpath(os.path.join(DOC_DIR, req.filename))
    result = delete(path)
    return {"deleted": req.filename, "result": result}


def to_history(messages: List[Message]):
    """
    将规范的messages拆分为历史消息和当前问题
    :param messages: OpenAI规范messages
    :return: (history/历史消息, input/当前问题)
    """
    hist = []
    for m in messages[:-1]:
        hist.append((m.role, m.content))
    return hist, messages[-1].content


@app.post("/chat", response_model=dict)
async def chat(req: ChatRequest):
    hist, question = to_history(req.messages)
    if not hist:
        print("No history message detected.")
        out = rag_chain.invoke({"chat_history": [], "input": question})
    else:
        out = historical_rag_chain.invoke({"chat_history": hist, "input": question})

    return {"answer": out["answer"], "sources": [d.metadata["source"] for d in out["context"]]}


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    hist, question = to_history(req.messages)

    def streamer():
        for chunk in rag_chain_streaming.stream({"chat_history": [], "input": question}):
            if 'answer' in chunk:
                yield chunk['answer']

    def historical_streamer():
        for chunk in historical_rag_chain_streaming.stream({"chat_history": hist, "input": question}):
            if 'answer' in chunk:
                yield chunk['answer']

    if not hist:
        print("No history message detected.")
        return StreamingResponse(streamer(), media_type="text/event-stream")

    return StreamingResponse(historical_streamer(), media_type="text/event-stream")


@app.post("/chat/plain")
async def chat_plain(req: ChatRequest):
    out = base_deepseek.invoke([(m.role, m.content) for m in req.messages])
    return {"answer": out.content}


@app.post("/chat/stream/plain")
async def chat_stream_plain(req: ChatRequest):
    def streamer():
        for chunk in streaming_deepseek.stream([(m.role, m.content) for m in req.messages]):
            yield chunk.content

    return StreamingResponse(streamer(), media_type="text/event-stream")
