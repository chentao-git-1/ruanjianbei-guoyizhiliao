import json
import os.path

from langchain_text_splitters import CharacterTextSplitter
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.FileLoader import LoaderFactory
from app.common import vector_store, DOC_DIR

os.makedirs(DOC_DIR, exist_ok=True)

splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)


def ingest(path: str) -> int:
    """
    将一个文档内容加入知识库
    :param path: 文档路径
    :return: 知识库新增chunks数量
    """
    loader = LoaderFactory.get_loader(path)
    docs = loader.load()
    splits = splitter.split_documents(docs)
    vector_store.add_documents(splits)
    return len(splits)


def delete(path: str):
    """
    从知识库中删除指定文档的内容
    :param path: 文档路径
    :return: 删除是否成功
    """
    # fname = os.path.basename(path)
    if not os.path.exists(path):
        return {'message': '不存在指定的文件'}
    os.remove(path)
    return vector_store.client.delete(
        collection_name=vector_store.collection_name,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="metadata.source",
                    match=MatchValue(value=path),
                )
            ]
        )
    )
