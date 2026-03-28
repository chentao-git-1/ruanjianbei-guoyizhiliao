# ruanjianbei-guoyizhiliao

本仓库由 3 个子项目组成，分别是前端、Java 后端、LLM/RAG 服务。下面给出基于仓库现状的启动方法与详细技术栈说明。

---

## 1. 仓库结构

- `smart-education-front`：前端（Vue3）
- `smart-educetion-master`：后端（Spring Boot 多模块）
- `smart-edu-llm`：知识库与大模型服务（FastAPI + LangChain + Qdrant）

---

## 2. 详细技术栈

### 2.1 前端：`smart-education-front`

**语言与框架**
- JavaScript
- Vue `^3.2.13`
- Vue Router `^4.0.3`

**构建与工程化**
- Vue CLI Service `~5.0.0`
- Babel（`@babel/core ^7.12.16`）
- ESLint（`eslint ^7.32.0` + `eslint-plugin-vue ^8.0.3`）
- 包管理：npm / pnpm（存在 `pnpm-lock.yaml`）

**UI 与功能库**
- Element Plus `^2.9.11` + `@element-plus/icons-vue ^2.3.1`
- Vant `^4.9.19`
- Axios `^1.10.0`
- ECharts `^5.6.0`
- marked `^16.0.0`
- DOMPurify `^3.2.6`
- BigNumber.js `^9.3.0`

**关键配置依据**
- `smart-education-front/package.json`
- `smart-education-front/vue.config.js`（开发端口 `8080`）

---

### 2.2 后端：`smart-educetion-master`

**语言与框架**
- Java `17`
- Spring Boot `3.4.5`
- Spring Security `3.4.5`
- MyBatis Spring Boot Starter `3.0.4`
- MyBatis-Plus Spring Boot3 Starter `3.5.12`

**数据与中间件**
- PostgreSQL 驱动 `42.7.0`
- Druid `1.2.24`
- JWT（`io.jsonwebtoken:jjwt 0.12.6`）

**接口与辅助**
- SpringDoc OpenAPI `2.7.0`
- Jakarta Validation API `3.0.2`
- problem-spring-web-starter `0.29.1`
- Lombok `1.18.30`

**工程结构（Maven 多模块）**
- `auth`
- `common`
- `student`
- `teacher`

**端口（dev 配置）**
- `teacher`: `8081`（`teacher/src/main/resources/application-dev.yml`）
- `student`: `8082`（`student/src/main/resources/application-dev.yml`）
- `auth`: `8082`（`auth/src/main/resources/application-dev.yml`，通常作为依赖模块）

**关键配置依据**
- `smart-educetion-master/pom.xml`
- `smart-educetion-master/*/pom.xml`
- `smart-educetion-master/*/src/main/resources/application-dev.yml`
- `smart-educetion-master/common/src/main/resources/application.yml`

---

### 2.3 LLM 服务：`smart-edu-llm`

**语言与框架**
- Python
- FastAPI `0.116.0`
- Uvicorn

**LLM / RAG 栈**
- LangChain `0.3.26`
- langchain-community `0.3.27`
- langchain-core `0.3.68`
- langchain-qdrant `0.2.0`
- qdrant-client `1.14.3`
- langchain-deepseek `0.1.3`
- sentence-transformers `5.0.0`
- langchain-text-splitters `0.3.8`

**文档处理**
- unstructured
- pypdf
- python-docx
- python-multipart

**关键配置依据**
- `smart-edu-llm/requirements.txt`
- `smart-edu-llm/config.json`
- `smart-edu-llm/app/main.py`
- `smart-edu-llm/app/common.py`

---

## 3. 如何启动（本地开发推荐顺序）

> 推荐顺序：基础设施（PostgreSQL、Qdrant）→ 后端（teacher/student）→ LLM 服务 → 前端。

### 3.1 基础设施

#### PostgreSQL（后端依赖）
确保可访问 PostgreSQL，并创建对应数据库（如 `smart_edu`）。

后端默认配置位置：
- `smart-educetion-master/student/src/main/resources/application-dev.yml`
- `smart-educetion-master/teacher/src/main/resources/application-dev.yml`

请按本地环境修改 `druid.url`、`druid.username`、`druid.password`。

#### Qdrant（LLM 依赖）
```bash
docker pull qdrant/qdrant
docker volume create qdrant_data
docker run -p 6333:6333 -p 6334:6334 -v qdrant_data:/qdrant/storage qdrant/qdrant
```

并将 `smart-edu-llm/config.json` 中 `url` 配置为本地可访问地址（如 `http://localhost:6333`）。

---

### 3.2 启动后端（`smart-educetion-master`）

```bash
cd smart-educetion-master
chmod +x mvnw
./mvnw clean package -DskipTests
```

#### 启动 teacher 服务（8081）
```bash
java -jar teacher/target/teacher-0.0.1-SNAPSHOT.jar
```

#### 启动 student 服务（8082）
```bash
java -jar student/target/student-0.0.1-SNAPSHOT.jar
```

> 说明：`student` / `teacher` 模块已依赖 `auth` 与 `common`，通常本地联调时分别启动这两个业务服务即可。

---

### 3.3 启动 LLM 服务（`smart-edu-llm`）

```bash
cd smart-edu-llm
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后可访问：
- `http://localhost:8000/docs`

---

### 3.4 启动前端（`smart-education-front`）

```bash
cd smart-education-front
npm install
npm run serve
```

启动后访问：
- `http://localhost:8080`

---

## 4. 本地联调注意事项

1. 前端接口地址当前在 `smart-education-front/src/api/api.js` 中默认指向远端 IP，进行本地联调时请改为本地后端地址。
2. 后端 `application-dev.yml` 中数据库连接默认指向远端地址，需改为本地数据库。
3. LLM 的 `config.json` 中 Qdrant 地址默认是容器网络地址，需改为本机可访问地址。

---

## 5. 默认服务端口速查

- 前端：`8080`
- 后端 teacher：`8081`
- 后端 student：`8082`
- LLM FastAPI：`8000`
- Qdrant：`6333` / `6334`
- PostgreSQL：`5432`（常见默认端口）
