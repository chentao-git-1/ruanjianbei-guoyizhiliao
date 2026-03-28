## SmartEdu 知识库/AI服务

该项目使用`langchain`框架整合了`Qdrant`向量数据库用作知识库与RAG、`DeepSeek`作为LLM，实现了基于知识库的大模型调用。

项目使用FastAPI部署为REST API应用，提供上传/查看/删除知识库文档、以及大模型问答（含非streaming、streaming）接口。


# 离线安装
确保主机网络正常（如果有问题，可以换个网络环境或者用代理），执行以下命令：
cd ~/projects/smart_education_llm
mkdir -p deps  # 创建存放依赖的目录
pip download -r requirements.txt -d deps -i https://mirrors.aliyun.com/pypi/simple/

### 安装和部署
- 在docker中运行Qdrant
```shell
docker pull qdrant/qdrant
```

```shell
docker volume create qdrant_data
```

```shell
docker run -p 6333:6333 -p 6334:6334 -v "qdrant/data:qdrant/storage:z" qdrant/qdrant
```

- 安装依赖
```shell
pip install -r requirements.txt
```

- 运行应用
```shell
uvicorn app.main:app
```

### 代码开发
#### 文件结构说明：
- `main.py`：程序入口，使用FastAPI构建应用
- `common.py`：存放全局常量和Qdrant数据库实例
- `docs_manager.py`：定义知识库文档管理的方法
- `FileLoader.py`：定义文档加载器
- `rag_chain.py`：定义核心RAG chain


#### 配置文件说明：
- 通过`config.json`配置文件，可配置：
  - Qdrant数据库URL和目标collection名称；
  - 知识库文件的实际存放路径；
  - 大模型服务的URL和API Key

#### 注意事项：
1. 目前支持的文档类型为：`.txt | .md | .docx | .doc | .pdf | .pptx | .ppt`。要添加新的文件格式支持，需要在`FileLoader.py`中添加新的loader。
2. 考虑到音视频文件的转写对计算资源有一定需求，预计难以在服务器本地完成，因此暂未支持音视频文件作为知识库文档内容。
3. 如果要将**知识库文件存储路径**（默认是data/doc/）与前端上传文件功能同步，可考虑使用`docker volume`将这个目录映射到宿主机路径。