# 校园找搭子系统 — 后端 PRD

> **版本**: v1.0  
> **日期**: 2026-06-09  
> **技术栈**: FastAPI + Pydantic-AI + SQLite + SQLAlchemy 2.0 + Pydantic v2 + JWT  
> **架构模式**: 企业级分层架构（API → Service → Model → Schema → Database）

---

## 一、项目概述

### 1.1 项目背景

校园找搭子系统是一个面向在校大学生的社交匹配平台。用户可以在平台上发布"找搭子"帖子（学习搭子、运动搭子、约饭搭子、出行搭子等），系统利用 AI 进行智能匹配推荐，帮助用户快速找到志趣相投的伙伴。

### 1.2 核心目标

1. 提供完整的用户注册、登录、个人资料管理能力
2. 支持多类型的搭子帖子发布、浏览、筛选、关闭
3. 基于 Pydantic-AI 实现智能匹配推荐，根据用户画像和需求计算匹配度并生成推荐理由
4. 基于 Pydantic-AI 实现内容安全审核，对用户发布的内容进行合规检查
5. 提供搭子之间的聊天能力（匹配成功后）
6. 支持 App + Web 双端统一认证

### 1.3 业务范围

| 模块 | 说明 |
|------|------|
| 用户系统 | 注册、登录、JWT认证、个人资料管理、学校认证 |
| 帖子系统 | 发布搭子帖、浏览、筛选（按类别/标签/时间）、关闭帖子 |
| 智能匹配 | AI 分析用户画像和需求，推荐最合适的搭子并生成推荐理由 |
| 内容审核 | AI 自动审核帖子和聊天内容，过滤违规信息 |
| 聊天系统 | 匹配成功后的一对一聊天 |
| 通知系统 | 匹配通知、消息通知、系统通知 |

---

## 二、技术架构

### 2.1 技术选型

| 层级 | 技术 | 版本 | 选型理由 |
|------|------|------|----------|
| Web框架 | FastAPI | latest | 高性能异步框架，原生 OpenAPI/Swagger 支持，类型安全 |
| ORM | SQLAlchemy | 2.0+ | 成熟稳定，2.0 原生支持异步，与 FastAPI 配合良好 |
| 数据库 | SQLite | — | 轻量零配置，适合校园场景的并发量；后续可无缝迁移到 PostgreSQL |
| 数据校验 | Pydantic | v2 | Rust 内核，性能优异，与 FastAPI 深度集成 |
| AI Agent | Pydantic-AI | latest | 结构化输出 + Agent 工作流，与 Pydantic v2 同生态 |
| 认证 | JWT (python-jose) | — | 无状态认证，适合 App + Web 双端场景 |
| 密码哈希 | passlib + bcrypt | — | 业界标准的密码哈希方案 |
| 配置管理 | python-dotenv | — | .env 文件管理环境变量，12-Factor App 推荐做法 |
| 数据存储 | JSON | — | 灵活的标签、用户画像等半结构化数据存储（SQLite JSON 字段） |
| 异步 | AnyIO / asyncio | — | FastAPI 原生异步，全链路 async |

### 2.2 架构分层图

```
┌─────────────────────────────────────┐
│            API 层 (Router)           │  ← HTTP 请求入口，参数校验，Swagger 文档
├─────────────────────────────────────┤
│          Schema 层 (Pydantic)        │  ← 请求/响应模型，数据校验与序列化
├─────────────────────────────────────┤
│          Service 层 (Business)       │  ← 核心业务逻辑，编排调用
├─────────────────────────────────────┤
│     AI 模块 (Pydantic-AI Agent)      │  ← AI 匹配推荐 & 内容安全审核
├─────────────────────────────────────┤
│          Model 层 (SQLAlchemy)       │  ← ORM 模型，数据库映射
├─────────────────────────────────────┤
│        Database 层 (Session)         │  ← 连接管理，事务控制，会话工厂
└─────────────────────────────────────┘
```

### 2.3 数据流设计

```
用户请求 → API Router → Schema 校验 → Service 业务处理
                                         ├── Model/Database（数据持久化）
                                         └── AI Agent（智能匹配/内容审核）
                                         → Schema 序列化 → JSON 响应
```

---

## 三、项目目录结构

```
campus-buddy/
│
├── app/                            # 应用主目录
│   ├── __init__.py
│   │
│   ├── main.py                     # FastAPI 应用入口：创建app实例，注册中间件，挂载路由，配置Swagger
│   │
│   ├── api/                        # ===== API 层 =====
│   │   ├── __init__.py
│   │   ├── deps.py                 # 依赖注入：get_current_user、get_db、权限校验等可复用依赖
│   │   └── v1/                     # API v1 版本（URL前缀 /api/v1）
│   │       ├── __init__.py
│   │       ├── router.py           # v1 路由汇总：将所有子路由汇聚到一个路由器上
│   │       ├── auth.py             # 认证接口：注册 /register、登录 /login、刷新令牌 /refresh
│   │       ├── users.py            # 用户接口：获取/更新个人资料、上传头像
│   │       ├── posts.py            # 帖子接口：CRUD 搭子帖、列表筛选、搜索
│   │       ├── matches.py          # 匹配接口：获取推荐列表、发起匹配请求、查看匹配结果
│   │       ├── chats.py            # 聊天接口：获取会话列表、发送消息、获取历史消息
│   │       └── notifications.py    # 通知接口：获取通知列表、标记已读、批量操作
│   │
│   ├── services/                   # ===== Service 层 =====
│   │   ├── __init__.py
│   │   ├── auth_service.py         # 认证逻辑：注册参数校验、密码哈希、JWT 签发与验证、令牌刷新
│   │   ├── user_service.py         # 用户逻辑：个人资料 CRUD、头像处理、学校认证
│   │   ├── post_service.py         # 帖子逻辑：帖子 CRUD、状态管理、过期自动关闭
│   │   ├── match_service.py        # 匹配逻辑：调用 AI 匹配引擎、生成推荐列表、匹配状态管理
│   │   ├── chat_service.py         # 聊天逻辑：消息发送存储、历史查询、会话管理
│   │   ├── notification_service.py # 通知逻辑：通知创建、列表查询、标记已读、批量操作
│   │   └── moderation_service.py   # 审核逻辑：调用 AI 审核引擎，对帖子和消息进行内容审查
│   │
│   ├── models/                     # ===== Model 层 (SQLAlchemy ORM) =====
│   │   ├── __init__.py
│   │   ├── base.py                 # 基类模型：定义 id、created_at、updated_at 等公共字段和通用方法
│   │   ├── user.py                 # 用户表：账号信息、学校信息、个人画像标签
│   │   ├── post.py                 # 帖子表：搭子帖内容、分类、标签、状态、过期时间
│   │   ├── match.py                # 匹配表：匹配双方、匹配分数、AI 推荐理由、状态
│   │   ├── chat.py                 # 聊天会话表：绑定的匹配、参与用户
│   │   ├── message.py              # 消息表：消息内容、类型、发送者、已读状态
│   │   └── notification.py         # 通知表：通知类型、内容、已读状态
│   │
│   ├── schemas/                    # ===== Schema 层 (Pydantic v2) =====
│   │   ├── __init__.py
│   │   ├── common.py               # 通用模型：分页请求/响应、统一 API 响应格式、错误模型
│   │   ├── auth.py                 # 认证模型：注册请求、登录请求、令牌响应
│   │   ├── user.py                 # 用户模型：用户资料创建/更新/响应
│   │   ├── post.py                 # 帖子模型：帖子创建/更新/列表筛选/响应
│   │   ├── match.py                # 匹配模型：匹配请求/推荐响应/AI推荐理由
│   │   ├── chat.py                 # 聊天模型：会话列表响应、发送消息请求、消息响应
│   │   └── notification.py         # 通知模型：通知响应、批量操作请求
│   │
│   ├── db/                         # ===== Database 层 =====
│   │   ├── __init__.py
│   │   ├── session.py              # 数据库会话工厂：创建异步 engine、sessionmaker、get_db 生成器
│   │   └── init_db.py              # 初始化脚本：首次运行时自动建表、可选种子数据
│   │
│   ├── core/                       # ===== 核心基础设施 =====
│   │   ├── __init__.py
│   │   ├── config.py               # 配置管理：使用 pydantic-settings 读取 .env，定义所有配置项
│   │   ├── security.py             # 安全模块：JWT 编码/解码、密码哈希/校验、令牌过期管理
│   │   └── exceptions.py           # 异常处理：自定义 HTTP 异常类、全局异常处理器
│   │
│   └── ai/                         # ===== AI 模块 (Pydantic-AI) =====
│       ├── __init__.py
│       ├── agent.py                # Agent 配置：LLM 模型初始化、Agent 实例创建、工具注册
│       ├── matching.py             # 匹配引擎：用户画像分析 prompt、匹配打分逻辑、推荐理由生成
│       └── moderation.py           # 审核引擎：内容安全审核 prompt、违规分类、审核结果结构化输出
│
├── alembic/                        # 数据库迁移（SQLAlchemy 官方迁移工具）
│   ├── env.py                      # Alembic 环境配置：连接数据库、加载模型元数据
│   ├── script.py.mako              # 迁移脚本模板
│   └── versions/                   # 迁移版本文件目录
│       └── .gitkeep
│
├── tests/                          # 测试目录
│   ├── __init__.py
│   ├── conftest.py                 # pytest 配置：数据库 fixture、测试客户端、模拟用户
│   ├── test_auth.py                # 认证模块测试
│   ├── test_users.py               # 用户模块测试
│   ├── test_posts.py               # 帖子模块测试
│   ├── test_matches.py             # 匹配模块测试
│   └── test_chats.py               # 聊天模块测试
│
├── .env.example                    # 环境变量模板（不含敏感信息，可提交到版本控制）
├── .env                            # 实际环境变量（不提交到版本控制）
├── .gitignore                      # Git 忽略规则
├── alembic.ini                     # Alembic 配置文件
├── requirements.txt                # Python 依赖清单
└── README.md                       # 项目说明文档
```

### 目录职责速查表

| 目录 | 职责 | 依赖方向 |
|------|------|----------|
| `app/api/` | HTTP 路由定义，参数解析，调用 Service | → Service, Schema |
| `app/services/` | 业务逻辑实现，编排 Model 和 AI 模块 | → Model, AI |
| `app/models/` | 数据库表结构定义（ORM 映射） | → Database（基类） |
| `app/schemas/` | API 请求/响应数据结构定义 | 无依赖（纯数据） |
| `app/db/` | 数据库连接、会话、事务管理 | 无依赖 |
| `app/core/` | 配置、安全、异常（横切关注点） | 无依赖 |
| `app/ai/` | Pydantic-AI Agent 配置和 Prompt 管理 | → Schema（结构化输出） |
| `alembic/` | 数据库版本迁移 | → Model（元数据） |
| `tests/` | 单元测试和集成测试 | → 所有模块 |

---

## 四、核心模块设计思路

### 4.1 用户与认证模块

**设计思路**：

1. **注册**：用户通过手机号或邮箱注册，密码使用 bcrypt 哈希后存储。注册时需绑定学校信息（大学、学院、专业、年级），作为匹配的重要画像维度。
2. **登录**：验证凭据后签发两个令牌——`access_token`（短期，15分钟）和 `refresh_token`（长期，7天）。access_token 过期后用 refresh_token 无感刷新。
3. **个人资料**：用户可设置昵称、头像、性别、个人简介、兴趣标签（JSON 存储），这些是 AI 匹配的核心输入。
4. **JWT 依赖注入**：在 `deps.py` 中实现 `get_current_user` 依赖，自动从请求头解析 token 并注入当前用户对象，Service 层无需手动处理认证。

**关键方法**：
- `POST /api/v1/auth/register` — 注册
- `POST /api/v1/auth/login` — 登录
- `POST /api/v1/auth/refresh` — 刷新令牌
- `GET /api/v1/users/me` — 获取当前用户资料
- `PUT /api/v1/users/me` — 更新当前用户资料

### 4.2 搭子帖子模块

**设计思路**：

1. **分类体系**：帖子按大类（学习、运动、约饭、出行、其他）+ 自定义标签（JSON数组）组织，支持灵活扩展。
2. **生命周期**：帖子有状态机（active → closed/cancelled），到达 `expires_at` 后由后台定时任务自动标记为 closed。
3. **列表筛选**：支持按类别、标签、学校、发布时间、人数等多维度组合筛选和排序，使用 SQLAlchemy 动态查询构建。
4. **人数管理**：帖子设置目标人数 `target_count` 和当前人数 `current_count`，达到目标后自动关闭。

**关键方法**：
- `POST /api/v1/posts` — 发布搭子帖
- `GET /api/v1/posts` — 帖子列表（分页 + 筛选）
- `GET /api/v1/posts/{id}` — 帖子详情
- `PUT /api/v1/posts/{id}` — 更新帖子
- `DELETE /api/v1/posts/{id}` — 关闭帖子

### 4.3 AI 智能匹配模块（Pydantic-AI 核心场景）

**设计思路**：

1. **用户画像构建**：AI Agent 综合分析用户的学校信息、兴趣标签、历史发帖记录、匹配偏好，生成结构化的用户画像。
2. **匹配打分**：当用户浏览帖子或主动寻求推荐时，AI Agent 对候选搭子进行多维度打分（兴趣重合度、学校匹配度、活跃度、历史评价等），输出匹配分数（0-100）和自然语言推荐理由。
3. **结构化输出**：利用 Pydantic-AI 的 `result_type` 机制，要求 Agent 输出严格符合 Pydantic Schema 结构的匹配结果，保证下游可直接使用。
4. **推荐列表生成**：按匹配分数降序排列，推荐 TOP-N 给用户。

**Pydantic-AI 工作流**：
```
用户请求推荐 → 查询用户画像 & 候选搭子列表
             → Agent.run(prompt, result_type=MatchResult)
             → 结构化匹配结果（分数+理由）
             → 排序返回 TOP-N
```

**关键方法**：
- `GET /api/v1/matches/recommendations` — 获取 AI 推荐列表
- `POST /api/v1/matches/request/{user_id}` — 向某用户发起匹配请求
- `GET /api/v1/matches` — 我的匹配列表

### 4.4 AI 内容审核模块（Pydantic-AI 核心场景）

**设计思路**：

1. **自动审核触发**：用户发布帖子或发送消息时，异步调用 AI 审核 Agent。
2. **多维度检查**：检查内容包括但不限于——违规广告、色情低俗、暴力威胁、隐私泄露、骚扰信息。
3. **结构化审核结果**：Agent 返回 `ModerationResult`（违规类型、是否违规、置信度、处理建议）。
4. **分级处理**：根据置信度决定——直接放行（<30%）、人工复审标记（30%-70%）、自动屏蔽（>70%）。

**Pydantic-AI 工作流**：
```
内容提交 → Agent.run(content + moderation_prompt, result_type=ModerationResult)
         → 获取审核结果
         → 分级处理（放行/标记/屏蔽）
```

**关键方法**：
- 在 `post_service.py` 和 `chat_service.py` 中调用 `moderation_service.py` 的审核方法
- 审核方法是内部调用，不暴露独立的 API 端点

### 4.5 聊天模块

**设计思路**：

1. **会话绑定**：每个聊天会话 `Chat` 绑定一个匹配记录 `Match`，确保只有匹配成功的双方才能聊天。
2. **消息类型**：支持文本消息和图片消息（图片存储路径/URL）。
3. **已读状态**：消息记录已读/未读状态，用于红点提醒。
4. **历史查询**：按时间序拉取消息，支持分页加载（避免一次加载过多）。

**关键方法**：
- `GET /api/v1/chats` — 我的会话列表
- `POST /api/v1/chats/{chat_id}/messages` — 发送消息
- `GET /api/v1/chats/{chat_id}/messages` — 获取历史消息（分页）

### 4.6 通知模块

**设计思路**：

1. **通知类型**：匹配成功通知、收到新消息通知、系统通知。
2. **创建时机**：由 Service 层的各个方法在业务操作完成后自动触发通知创建。
3. **已读管理**：支持单条标记已读和全部标记已读。

**关键方法**：
- `GET /api/v1/notifications` — 获取通知列表
- `PUT /api/v1/notifications/{id}/read` — 标记单条已读
- `PUT /api/v1/notifications/read-all` — 全部标记已读

---

## 五、数据库设计思路

### 5.1 核心实体关系

```
User (1) ──────< Post (N)         一个用户发布多个帖子
User (1) ──────< Match (N)        一个用户可以参与多个匹配（作为发起方或接收方）
Match (1) ──────< Chat (1)        一个匹配对应一个聊天会话
Chat (1) ──────< Message (N)      一个会话包含多条消息
User (1) ──────< Notification (N) 一个用户有多条通知
```

### 5.2 各表核心字段设计思路

| 表 | 核心字段 | 说明 |
|----|----------|------|
| **user** | username, email, phone, hashed_password, university, college, major, grade, nickname, avatar, gender, bio, tags(JSON), is_active, is_verified, created_at | tags 使用 JSON 类型存储兴趣标签列表 |
| **post** | user_id(FK), title, description, category, tags(JSON), target_count, current_count, location, time_range, status, expires_at, created_at | category 使用枚举；tags 灵活扩展 |
| **match** | user_id(FK), target_user_id(FK), post_id(FK), match_score, ai_reason, status, created_at | ai_reason 存储 AI 生成的推荐理由文本 |
| **chat** | match_id(FK), user1_id(FK), user2_id(FK), created_at | 唯一约束 match_id |
| **message** | chat_id(FK), sender_id(FK), content, content_type, is_read, created_at | content_type 枚举：text / image |
| **notification** | user_id(FK), type, title, content, is_read, created_at | type 枚举：match / message / system |

### 5.3 JSON 字段使用策略

- **user.tags**：`["Python", "机器学习", "羽毛球"]` — 兴趣标签列表
- **post.tags**：`["期末复习", "图书馆", "大二"]` — 帖子自定义标签
- 优势：灵活的标签体系无需额外建关联表，SQLite 原生支持 JSON 查询函数

---

## 六、API 设计规范

### 6.1 统一响应格式

所有 API 响应使用统一的结构：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

分页响应的 data 中包含：

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

### 6.2 HTTP 状态码约定

| 状态码 | 语义 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如重复注册） |
| 422 | 请求格式正确但语义有误 |
| 500 | 服务器内部错误 |

### 6.3 路由命名规范

- 使用 RESTful 风格：资源名复数形式
- 版本前缀：`/api/v1/`
- 认证接口除外（`/api/v1/auth/`），其余接口均需携带 JWT token
- Swagger 文档自动生成，每个端点通过 docstring 和 `summary` / `description` 参数添加说明

---

## 七、配置与环境变量

### 7.1 .env 配置项设计

所有环境变量通过 `pydantic-settings` 的 `BaseSettings` 读取，在 `app/core/config.py` 中集中管理。

```env
# ===== 应用配置 =====
APP_NAME=CampusBuddy
APP_VERSION=1.0.0
DEBUG=false
SECRET_KEY=your-secret-key-here

# ===== 数据库配置 =====
DATABASE_URL=sqlite+aiosqlite:///./campus_buddy.db

# ===== JWT 配置 =====
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# ===== LLM 配置（Pydantic-AI） =====
PDAI_BASE_URL=https://api.openai.com/v1
PDAI_API_KEY=sk-your-api-key
PDAI_MODEL=gpt-4o-mini

# ===== 服务配置 =====
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# ===== CORS 配置 =====
CORS_ORIGINS=["*"]
```

### 7.2 环境变量命名说明

- 使用 `PDAI_BASE_URL` 和 `PDAI_API_KEY` 替代 `OPENAI_BASE_URL` 和 `OPENAI_API_KEY`，避免与系统级或其它库的 OpenAI 环境变量冲突
- `PDAI_` 前缀代表 Pydantic-AI，语义清晰，表明这些配置是给 pydantic-ai 库使用的

---

## 八、开发实施步骤

> **关于时间估算的说明**：以下每个阶段给出两个时间——「理想编码时间」（一切顺利、一次性写对的纯编码时间）和「现实预估」（包含调试、返工、Prompt 调优、边界处理）。括号内的天数默认为理想时间。

---

### 阶段一：项目骨架搭建（理想 1 天 / 现实 0.5~1 天）

1. 创建项目目录结构（按第三章的目录树）
2. 编写 `requirements.txt`（fastapi, uvicorn, sqlalchemy\[asyncio\], aiosqlite, pydantic, pydantic-ai, pydantic-settings, python-jose, passlib, bcrypt, python-dotenv, alembic, pytest, httpx）
3. 创建 `.env.example` 和 `.gitignore`
4. 实现 `app/core/config.py`：使用 pydantic-settings 读取 .env
5. 实现 `app/db/session.py`：创建异步 engine 和 sessionmaker
6. 实现 `app/models/base.py`：ORM 基类
7. 实现 `app/main.py`：创建 FastAPI 实例，配置 CORS，注册 v1 路由，配置 Swagger
8. 验证骨架可以启动并访问 Swagger 文档页面

> **波动因素**：依赖版本冲突（常见于 aiosqlite + sqlalchemy 版本组合）、pydantic-settings 与 pydantic-ai 的版本兼容。这个阶段最可控。

### 阶段二：认证与用户模块（理想 2 天 / 现实 2~3 天）

1. 实现 `user` 和 `notification` 的 ORM Model
2. 实现 `auth` 和 `user` 的 Pydantic Schema
3. 实现 `app/core/security.py`：JWT 签发/验证，密码哈希/校验
4. 实现 `app/core/exceptions.py`：自定义异常类
5. 实现 `app/api/deps.py`：`get_current_user`、`get_db` 依赖
6. 实现 `auth_service.py`：注册、登录、令牌刷新
7. 实现 `user_service.py`：个人资料 CRUD
8. 实现 `api/v1/auth.py` 和 `api/v1/users.py` 路由
9. 编写认证和用户模块的单元测试
10. 验证注册→登录→获取资料→更新资料的完整流程

> **波动因素**：JWT refresh token 的轮转策略、令牌过期边界测试、密码哈希配置。这部分是 FastAPI 最成熟的领域，波动不大。

### 阶段三：帖子模块（理想 1.5 天 / 现实 1.5~2.5 天）

1. 实现 `post` 的 ORM Model（含 JSON 标签字段）
2. 实现 `post` 的 Pydantic Schema（创建/更新/列表筛选/响应）
3. 实现 `post_service.py`：CRUD + 分页筛选 + 过期状态管理
4. 实现 `api/v1/posts.py` 路由
5. 编写帖子模块的单元测试
6. 手动测试发布帖子 → 筛选列表 → 查看详情 → 关闭帖子的流程

> **波动因素**：JSON 字段在 SQLite 中的查询写法（与 PostgreSQL 不同）、分页 + 多条件组合筛选的 Query 构建复杂度、过期时间边界的时区处理。

### 阶段四：AI 模块集成（理想 2 天 / 现实 3~6 天 ⚠️ 波动最大）

1. 实现 `app/ai/agent.py`：
   - 配置 Pydantic-AI Agent，绑定 LLM 模型（通过 `PDAI_*` 环境变量）
   - 定义 `deps` 函数和工具（如有需要）
2. 实现 `app/ai/matching.py`：
   - 设计匹配推荐的 system prompt
   - 定义 `MatchResult` 结构化输出 Schema（分数、推荐理由）
   - 封装 `recommend()` 方法
3. 实现 `app/ai/moderation.py`：
   - 设计内容审核的 system prompt
   - 定义 `ModerationResult` 结构化输出 Schema（违规类型、是否违规、置信度、建议）
   - 封装 `moderate()` 方法
4. 实现 `match_service.py`：调用 AI 匹配引擎，管理匹配记录
5. 实现 `moderation_service.py`：调用 AI 审核引擎，实现分级处理策略
6. 实现 `api/v1/matches.py` 路由
7. 在 `post_service.py` 中集成审核调用
8. 编写 AI 模块的单元测试（mock Agent 响应）
9. 用真实 LLM 端到端验证匹配推荐和内容审核效果

> **⚠️ 波动因素（本阶段是最大风险点）**：
> - **pydantic-ai 是新库**：文档和社区踩坑帖都相对少，遇到问题排查成本高
> - **Prompt 调优是迭代过程不是一次性任务**：匹配推荐的 prompt 至少 3~5 轮调优才能让推荐理由"像人话"；审核 prompt 需要在漏审和误杀之间反复找平衡点
> - **LLM 的非确定性**：同样的 prompt 不同时候返回质量不同，结构化输出偶发解析失败需要 fallback
> - **审核响应时间**：AI 审核是同步阻塞消息发送的，需要控制超时（建议 3s），超时后是放行还是拒绝的策略需要权衡
> - **费用预估**：调优过程本身消耗 tokens，需要控制

### 阶段五：聊天与通知模块（理想 1.5 天 / 现实 2~4 天）

1. 实现 `chat` 和 `message` 的 ORM Model
2. 实现 `chat` 和 `notification` 的 Pydantic Schema
3. 实现 `chat_service.py`：会话管理、消息发送与查询
4. 实现 `notification_service.py`：通知创建、列表、已读管理
5. 在 `match_service.py` 中集成匹配成功自动发通知
6. 在 `chat_service.py` 中集成新消息通知
7. 实现 `api/v1/chats.py` 和 `api/v1/notifications.py` 路由
8. 编写聊天和通知模块的单元测试

> **波动因素**：
> - **WebSocket 连接管理器的边界处理**：心跳超时判定、脏连接清理、多端广播时一个连接断开不影响其他——这些在代码量上不大但在调试上费时
> - **SQLite 并发下的 WebSocket**：多个 WebSocket 同时触发数据库写入，SQLite 的串行写锁可能导致消息发送延迟。需要验证并发场景
> - **离线消息的增量拉取**：`since` 参数的语义（包含还是不包含边界消息）、断线期间消息去重
> - **端到端测试复杂**：WebSocket 测试不能用 httpx，需要用 `websockets` 库或 FastAPI 的 `TestClient`，测试代码比 HTTP 接口测试多一倍

### 阶段六：数据库迁移与收尾（理想 0.5 天 / 现实 0.5~1 天）

1. 配置 Alembic（alembic.ini + env.py）
2. 生成初始迁移脚本
3. 实现 `app/db/init_db.py`：开发环境自动建表 + 可选种子数据
4. 配置全局异常处理器
5. 补充 Swagger 文档的标签分组和描述
6. 最终集成测试：全链路验证

> **波动因素**：Alembic 对 SQLite 的 ALTER TABLE 支持有限（SQLite 不支持 MODIFY COLUMN 等操作），部分迁移可能需要手动写 `batch_alter_table` 逻辑。

---

### 时间汇总

| 阶段 | 理想编码 | 现实预估 | 风险等级 |
|------|:---:|:---:|:---:|
| 一、骨架搭建 | 1 天 | 0.5~1 天 | 🟢 低 |
| 二、认证与用户 | 2 天 | 2~3 天 | 🟢 低 |
| 三、帖子模块 | 1.5 天 | 1.5~2.5 天 | 🟡 中 |
| **四、AI 模块集成** | **2 天** | **3~6 天** | **🔴 高** |
| 五、聊天与通知 | 1.5 天 | 2~4 天 | 🟡 中 |
| 六、收尾 | 0.5 天 | 0.5~1 天 | 🟢 低 |
| **合计** | **8.5 天** | **10~17.5 天** | — |

### 扭曲因素总结

影响现实时间的主要不是代码量，而是以下四个因素：

1. **pydantic-ai 是新库（最大变量）**：不像 FastAPI/SQLAlchemy 有 10 年社区积累，遇到问题 ChatGPT 都不一定有准确答案，排查靠读源码
2. **Prompt 工程不是代码工程**：写匹配推荐 prompt 和写 CRUD 是两种完全不同的工作模式——代码有对错，prompt 只有"够不够好"，调优是开放的
3. **WebSocket 的复杂度在边界不在主流程**：发送消息的 happy path 半小时就能跑通，但心跳超时、重连去重、多端同步这些边界各要半天
4. **测试成本等于编码成本**：一个有质量的测试套件，代码量通常是被测代码的 0.8~1.5 倍

---

## 九、代码规范要求

### 9.1 PEP8 规范

- 使用 `black` 或 `ruff` 做代码格式化
- 行宽限制 100 字符（FastAPI 推荐，PEP8 是 79 但现代项目多用 100）
- 变量命名：`snake_case`（函数、变量）、`PascalCase`（类、模型）、`UPPER_CASE`（常量）
- 所有公开函数和类必须有 docstring
- import 顺序：标准库 → 第三方库 → 本地模块，每组之间空一行

### 9.2 类型注解

- **所有接口函数**必须声明参数类型和返回值类型
- Service 层方法必须有完整的类型注解
- 使用 `Optional[T]`、`Union[T, None]`、`list[T]` 等泛型
- 异步函数返回 `Coroutine` 或直接标注返回类型

### 9.3 Swagger 文档

- 每个路由通过 `tags` 参数分组
- 通过 `summary` 和 `description` 添加接口说明
- Schema 类通过 `Field(description=..., example=...)` 为字段添加示例和描述
- 响应模型通过 `response_model` 参数声明

---

## 十、待确认事项分析

> 以下对四个开放问题进行逐项分析，每个问题给出方案对比、推荐结论及理由。

---

### 10.1 学校认证方式

#### 问题本质

如何验证用户的在校学生身份——这是校园产品的信任基石。虚假身份会直接导致匹配体验崩坏。

#### 方案对比

| 维度 | 方案A：手动填写 | 方案B：.edu 邮箱验证 | 方案C：对接教务系统 |
|------|:---:|:---:|:---:|
| **安全性** | ⭐ 极低，可随意伪造 | ⭐⭐⭐ 中等，邮箱可注册但门槛较高 | ⭐⭐⭐⭐⭐ 极高，学号+密码对接教务 |
| **开发成本** | ⭐⭐⭐⭐⭐ 几乎为零 | ⭐⭐⭐ 需集成邮件服务 | ⭐ 极高，每个学校接口不同 |
| **用户体验** | ⭐⭐⭐⭐⭐ 无摩擦 | ⭐⭐⭐⭐ 需登录邮箱点击链接 | ⭐⭐ 需记住教务密码，部分学校无接口 |
| **覆盖面** | 100% | ~95%（部分学校不提供 .edu 邮箱） | ~30%（仅少数学校开放 API） |
| **运营风险** | 高（水军/广告可随意注册） | 中（可人为批量注册） | 低 |

#### 推荐：分阶段演进

```
Phase 1（MVP）: 方案 A + B 混合
  ├── 注册时必须填写学校、学院、专业、年级（必填项）
  ├── .edu 邮箱验证为可选项
  └── 已验证用户获得「已认证」徽章，排序靠前

Phase 2（成熟期）: 引入方案 C
  ├── 对接 2-3 所主要合作院校的教务系统
  └── 其余学校沿用 Phase 1 方案
```

#### 理由

1. **校园产品冷启动阶段**，低摩擦注册比严格认证更重要——先有人气再治理质量
2. **.edu 邮箱在国内普及率参差不齐**：很多 985/211 不提供，二三本更少。强行作为唯一验证方式会大量拦截真实用户
3. **手动填写并非毫无价值**：学校+专业+年级的组合本身就是匹配算法的重要画像维度，即使未认证也能让 AI 匹配正常工作
4. **「认证徽章 + 排序加权」的激励模式**比强制验证更符合产品增长逻辑——让已验证用户获得更多曝光，驱动用户自愿认证
5. 教务系统对接的碎片化问题在国内极其严重——每所学校接口不一，适合作为长期优化项而非 MVP 依赖

---

### 10.2 图片存储方案

#### 问题本质

用户头像和聊天图片的持久化存储方案选择。

#### 方案对比

| 维度 | 方案A：本地文件系统 | 方案B：云存储 OSS | 方案C：Base64 + 数据库 |
|------|:---:|:---:|:---:|
| **实现复杂度** | ⭐⭐⭐⭐⭐ 简单，FastAPI StaticFiles 即可 | ⭐⭐⭐ 需集成 SDK，配置 Bucket | ⭐⭐⭐⭐ 简单，SQLite BLOB |
| **运维成本** | ⭐⭐⭐ 需自行备份 | ⭐⭐⭐⭐⭐ 云服务商兜底 | ⭐⭐⭐⭐ 随数据库备份 |
| **扩展性** | ⭐⭐ 单机限制，多实例需共享存储 | ⭐⭐⭐⭐⭐ 弹性扩展 | ⭐ 数据库会迅速膨胀 |
| **成本** | 免费（服务器磁盘） | 极小（校园产品图片量不大） | SQLite 性能下降 |
| **访问速度** | 快（本地 I/O） | 较快（CDN 加速） | 慢（数据库往返） |

#### 推荐：方案 A 起步 + 预留云存储接口

```
实施策略：
  ├── MVP: 本地存储到 /static/uploads/{avatars,chat_images}/
  │    └── FastAPI StaticFiles 挂载直接访问
  ├── 数据库字段存储 URL 字符串（非文件路径），天然解耦
  │    └── 本地："/static/uploads/avatars/xxx.jpg"
  │    └── 云端："https://oss.example.com/avatars/xxx.jpg"
  └── 在 config.py 中定义 STORAGE_BACKEND 配置项
       └── 切换时仅需修改 .env 和替换 upload 函数
```

#### 理由

1. **SQLite 项目的自然选择**：单文件部署，本地存储与 SQLite 的轻量哲学一致。不需要 MySQL/PostgreSQL 的运维复杂度却引入 OSS，属于架构上的风格不一致
2. **校园产品的图片量级可控**：头像 + 聊天图片（非朋友圈式 UGC 瀑布流），一个 5000 用户的产品一年图片量也就几百 MB，远不到需要 OSS 的量级
3. **URL 字段解耦是核心**：无论存哪里，Model 层只关心 URL 字符串，上传逻辑封装在 Service 层的一个函数里——这是低成本、高灵活性的关键设计
4. **真有需求时迁移成本极低**：只需修改 `upload_image()` 函数内部实现 + 批量迁移已有文件到 OSS（一次脚本），其余代码零改动

---

### 10.3 消息实时性

#### 问题本质

匹配成功后双方聊天，消息送达是走 WebSocket 实时推送还是 HTTP 轮询。

#### 方案对比

| 维度 | 方案A：HTTP 轮询 | 方案B：WebSocket | 方案C：SSE + HTTP 互补 |
|------|:---:|:---:|:---:|
| **实时性** | ⭐⭐ 取决于轮询间隔（3-5s） | ⭐⭐⭐⭐⭐ 真正的实时 | ⭐⭐⭐⭐ 准实时 |
| **实现复杂度** | ⭐⭐⭐⭐⭐ 就是普通 GET 接口 | ⭐⭐ 需管理连接池、心跳、重连 | ⭐⭐⭐ 较简单 |
| **服务器资源** | ⭐⭐ 无效请求多，数据库压力大 | ⭐⭐⭐⭐ 长连接，省资源 | ⭐⭐⭐⭐ |
| **App 端支持** | ⭐⭐⭐⭐⭐ 通用 | ⭐⭐⭐⭐⭐ 通用 | ⭐⭐⭐⭐ Android 需处理 |
| **离线消息** | 天然支持 | 需额外设计 | 天然支持 |
| **SQLite 并发** | ⚠️ 高频轮询会导致锁竞争 | ✅ 事件驱动，压力更小 | ✅ |

#### 推荐：WebSocket，不做轮询过渡

```
架构设计：
  ├── WebSocket 端点: /api/v1/ws/{chat_id}?token=xxx
  │    ├── 连接时验证 JWT（在 URL 参数或首次消息中传递）
  │    ├── 消息格式: {"type": "message", "data": {...}}
  │    └── 心跳: 每 30s ping/pong
  ├── 连接管理器: app/core/ws_manager.py
  │    ├── 维护 {user_id: [websocket_connections]} 映射
  │    ├── 用户多端在线时广播到所有连接
  │    └── 断线自动清理
  └── 离线消息兜底:
       └── 对方不在线时，消息持久化到 message 表
       └── 下次打开会话时通过 GET /messages 拉取历史
```

#### 理由

1. **「先 HTTP 后改造」是伪节省**：HTTP 轮询和 WebSocket 的 Service 层、Model 层几乎相同，差异仅在传输层。但轮询方式下你需要额外处理——轮询间隔调优、未读计数、重复消息去重——这些都是 WebSocket 不需要考虑的，反而不划算
2. **聊天的核心体验就是实时**：一个找搭子产品，用户匹配成功后发消息给对方，如果对方要等 5 秒才看到——这个体验在 2026 年是无法接受的。聊天是匹配闭环的最后一公里，值得从一开始就做好
3. **FastAPI 原生支持 WebSocket**：不需要额外的库，不增加项目依赖，代码量也很小（连接管理器 ~50 行）
4. **SQLite 写锁问题是另一个推手**：HTTP 轮询意味着每 3-5 秒每个活跃用户都会发起一次 SELECT 查询，当并发用户数增长时会放大 SQLite 的读写锁竞争。WebSocket 事件驱动模型下，只有在真正有新消息时才触发数据库写入，无消息时仅维持 TCP 连接，零数据库开销
5. **对 App 端没有任何兼容问题**：无论是原生 App（OkHttp 支持 WebSocket）还是 WebView/React Native/Flutter，WebSocket 都是标配

---

### 10.4 帖子过期关闭机制

#### 问题本质

帖子到达 `expires_at` 时间后，如何将状态从 `active` 变为 `closed`。

#### 方案对比

| 维度 | 方案A：查询时过滤 | 方案B：APScheduler 定时 | 方案C：混合方案 |
|------|:---:|:---:|:---:|
| **数据一致性** | ⭐⭐ 实际 status 未改变 | ⭐⭐⭐⭐ 状态实时更新 | ⭐⭐⭐⭐⭐ |
| **查询性能** | ⭐⭐ 每条 SQL 都带时间条件 | ⭐⭐⭐⭐⭐ 直接查 status | ⭐⭐⭐⭐⭐ |
| **实现复杂度** | ⭐⭐⭐⭐⭐ 0 行额外代码 | ⭐⭐⭐ spawn 一个进程 | ⭐⭐⭐⭐ |
| **可靠性** | ⭐⭐⭐⭐⭐ 不依赖外部进程 | ⭐⭐⭐ 进程可能挂 | ⭐⭐⭐⭐⭐ |
| **通知/副作用** | ❌ 无法触发关闭通知 | ✅ 可以发通知 | ✅ |

#### 推荐：方案 C（混合方案）—— 查询过滤为主 + 轻量定时兜底

```
实施策略：
  ├── 主防线: 所有列表查询 WHERE status = 'active' AND expires_at > datetime('now')
  │    └── 确保过期帖子在任何情况下都不会出现在列表中
  │
  ├── 辅助: 帖子详情接口中按需判断
  │    └── 返回时附带 computed_status 字段：真正的 active vs 已过期但未刷新状态
  │
  └── 兜底: FastAPI lifespan 事件中启动一个轻量 asyncio 定时任务
       ├── 每 10 分钟扫描一次
       ├── UPDATE posts SET status='closed' WHERE status='active' AND expires_at < datetime('now')
       └── 批量更新 + 可选发送过期通知
```

#### 理由

1. **查询过滤是硬防线，必须做**：无论定时任务是否运行，列表绝不能出现过期帖子。`WHERE expires_at > now()` 是最可靠的保障，不依赖任何外部进程
2. **定时任务只是锦上添花**：它的作用是更新 status 字段让 DBA 看着干净 + 触发关闭通知，但不影响核心功能
3. **不要为了定时任务引入 APScheduler 依赖**：asyncio 自带的能力就够了——
   - 不需要额外的进程模型
   - 不需要 Redis/消息队列
   - 与 FastAPI 共享同一个 event loop
   - 10 分钟间隔对 SQLite 的负载完全可以忽略
4. **FastAPI lifespan 是官方推荐的后台任务模式**：在 app 启动时创建任务，关闭时优雅取消，比 APScheduler 更轻量且与框架生命周期一致
5. **如果帖子量真的涨到需要精确到秒级的关闭**（比如秒杀型找搭子），可以再加一个方案——在帖子详情接口首次发现过期时即时更新，类似懒删除模式

---

### 综合建议汇总

| 事项 | 推荐方案 | 一句话 |
|------|----------|--------|
| 学校认证 | Phase 1 手动填写 + 可选 .edu 验证 | 先降门槛做增长，认证作为增值激励 |
| 图片存储 | 本地文件系统 + URL 字段解耦 | 与 SQLite 轻量哲学一致，迁移成本极低 |
| 消息实时性 | 直接上 WebSocket | 聊天体验不能妥协，且不比轮询更贵 |
| 过期关闭 | 查询过滤 + asyncio 定时兜底 | 查询是硬防线，定时只是锦上添花 |

---

## 十一、核心流程深度分析：匹配成功 → 创建聊天室 → WebSocket → 实时聊天

> 用户提出的核心链路：**匹配成功 → 创建聊天室 → 建立 WebSocket 连接 → 实时聊天**  
> 以下对该链路进行逐环节拆解，标识可行性与潜在风险，给出最终方案。

---

### 11.1 结论先行：可行，但箭头不是等号

这个链路**整体可行**，但四个环节之间的箭头**不是简单的 `→`（then），而是两种不同性质的箭头混在一起**。如果不区分清楚，代码实现会走偏。

```
匹配成功 ──[同步/事务]──→ 创建聊天室 ──[通知推送]──→ 用户感知
                                                      │
                                             用户点击进入聊天
                                                      │
                                             建立 WebSocket 连接
                                                      │
                                                 实时聊天
```

关键洞察：**前两步（匹配成功→创建聊天室）是服务端同步操作，中间有一个用户决策的异步断点，后两步（WebSocket→聊天）是客户端主动触发的**。

---

### 11.2 逐环节拆解

#### 环节 1：匹配成功

**触发方式有两种模式需要先明确：**

| 模式 | 流程 | 适用场景 |
|------|------|----------|
| **请求-同意模式** | 用户A发起匹配请求 → 用户B收到通知 → B点击同意 → 匹配成功 | 看到具体某个人/帖子，想搭 |
| **AI推荐-一键匹配** | 系统推荐列表 → 用户A点击"想搭" → 自动匹配成功（对方可事后拒绝） | AI推荐场景，降低摩擦 |

**推荐采用请求-同意模式**，理由：

1. 匹配是双向关系，单方面决定不符合社交产品直觉
2. AI 推荐 + 自动匹配虽然快，但会产生大量无效匹配——对方不感兴趣
3. 请求-同意模式下，匹配成功的双方都有明确的参与意愿，聊天质量更高

**匹配成功的服务端动作（同一事务内完成）**：
```
事务开始
  ├── 1. UPDATE match SET status = 'accepted', updated_at = NOW()
  ├── 2. INSERT INTO chat (match_id, user1_id, user2_id)
  ├── 3. INSERT INTO notification (user_id=userA, type='match_success', ...)
  └── 4. INSERT INTO notification (user_id=userB, type='match_success', ...)
事务提交
```

这四步必须在同一个数据库事务中完成——要么全部成功，要么全部回滚。不能出现匹配显示成功但聊天室没创建的情况。

#### 环节 2：创建聊天室

**创建时机**：在匹配成功的事务中**自动创建**，不需要用户额外操作。

**关键设计决策——一个 Match 对应一个 Chat**：

```
Match 表: (id=1, user_id=10, target_user_id=20, status='accepted', ...)
Chat 表:  (id=1, match_id=1, user1_id=10, user2_id=20, created_at=...)
```

`match_id` 在 Chat 表中设置 `UNIQUE` 约束，保证一个匹配只对应一个聊天室。这样：
- 用户在任何时候进入聊天，URL 始终是同一个 chat_id
- 不会因为重复进入而创建多个空会话
- 聊天记录天然聚合在一个会话下

**为什么不把创建聊天室作为独立步骤**：

如果把「创建聊天室」放在用户手动点击「开始聊天」时，会多出一个不必要的用户操作步骤和一次额外的 API 调用。匹配成功 = 双方已经同意搭伙，此时就应该有聊天能力。聊天室在服务端静默创建，客户端收到匹配成功通知后直接跳转即可。

#### 环节 3：建立 WebSocket 连接

**这是最容易产生误解的环节**。WebSocket 连接不是匹配成功时自动建立的，而是：

```
匹配成功通知 → 用户看到通知 → 点击进入聊天页面 → 客户端发起 WebSocket 连接
```

**连接建立的正确时机**：

```
客户端行为:
  1. 收到匹配成功通知（推送/轮询/列表刷新）
  2. 点击进入聊天页面
  3. GET /api/v1/chats/{chat_id}/messages  ← 先拉历史消息（HTTP）
  4. new WebSocket("ws://.../ws/chat/{chat_id}?token=xxx")  ← 再建立实时通道
  5. 收到消息时更新 UI
```

步骤 3 和 4 谁先谁后其实无所谓——可以并行：
- HTTP 拉历史消息
- WebSocket 开始监听新消息

**WebSocket 认证方案**：

```
方案 A（推荐）: URL 查询参数传递 token
  ws://host/api/v1/ws/chat/{chat_id}?token={jwt_access_token}

方案 B: 连接后首条消息认证
  连接 → 发送 {"type": "auth", "token": "xxx"}
       → 服务端验证 → 发送 {"type": "auth_ok"}
       → 开始收发消息

方案 A 更简洁，也是 FastAPI WebSocket 的常用模式——
可以在 accept 之前就完成认证并拒绝非法连接，避免资源浪费。
```

**连接管理器的核心职责**：

```
ConnectionManager:
  active_connections: dict[int, list[WebSocket]]
  # {user_id: [ws1, ws2, ...]}  支持同一用户多端连接

  connect(user_id, websocket):
    ├── 添加到 active_connections[user_id]
    ├── 广播上线状态（可选）
    └── 启动心跳检测

  disconnect(user_id, websocket):
    ├── 从列表中移除
    └── 清理空列表

  send_to_user(user_id, message):
    └── 向该用户的所有连接广播消息

  send_to_chat(chat_id, message, sender_id):
    ├── 查询 chat 的另一个用户（非 sender）
    └── 调用 send_to_user(target_user_id, message)
```

#### 环节 4：实时聊天

**消息发送的完整流程（一条消息的生命周期）**：

```
发送方客户端:
  1. 用户在输入框输入消息并发送
  2. WebSocket.send({"type": "message", "content": "你好！"})

服务端:
  3. 接收消息，提取 chat_id 和 content
  4. 验证：当前用户是否是 chat 的参与者？
     ├── 否 → 返回错误
     └── 是 → 继续
  5. 异步调用 AI 审核（moderation_service.moderate()）
     ├── 违规高置信度 → 拒绝发送，返回提示
     └── 通过/低置信度 → 继续
  6. 持久化：INSERT INTO message (chat_id, sender_id, content, ...)
  7. 查询目标用户：SELECT user1_id, user2_id FROM chat WHERE id=?
  8. 判断目标用户是否在线：
     ├── 在线 → connection_manager.send_to_user(target_user, message_json)
     └── 离线 → 消息已持久化，对方上线后通过 HTTP 拉取

接收方客户端:
  9. (在线) WebSocket.onMessage → 解析 JSON → 渲染到聊天气泡
     (离线) 下次打开聊天 → GET /messages → 渲染所有未读消息
     同时标记已读：PUT /messages/{last_read_id}/mark-read
```

**消息协议设计**：

```json
// 客户端 → 服务端（发送消息）
{
  "type": "message",
  "content": "明天下午3点图书馆见？",
  "content_type": "text"
}

// 服务端 → 客户端（推送消息）
{
  "type": "message",
  "message_id": 12345,
  "chat_id": 1,
  "sender_id": 10,
  "sender_nickname": "小明",
  "sender_avatar": "/static/uploads/avatars/10.jpg",
  "content": "明天下午3点图书馆见？",
  "content_type": "text",
  "created_at": "2026-06-09T15:30:00Z"
}

// 服务端 → 客户端（系统消息）
{
  "type": "system",
  "action": "user_online",       // 对方上线
  "user_id": 20,
  "chat_id": 1
}

// 心跳（双向）
// 客户端 → 服务端: {"type": "ping"}
// 服务端 → 客户端: {"type": "pong"}
```

---

### 11.3 边界场景分析

| 场景 | 问题 | 处理方案 |
|------|------|----------|
| **匹配成功但对方不在线** | 聊天室创建了，对方看不到 | 聊天室已建、消息持久化；对方上线后通过通知进入聊天 + HTTP 拉取历史消息 |
| **用户在聊天中 Token 过期** | WebSocket 连接断开 | 客户端监听 token 过期 → 自动 refresh token → 重新连接 WebSocket（静默完成，不打断用户） |
| **用户关闭聊天页面但未断开 WebSocket** | 消息仍在推送但 UI 不渲染 | 客户端 `beforeunload` / App `onPause` 时主动 close WebSocket；下次进入重新连接拉消息 |
| **同一用户多端同时在线** | 手机和电脑同时收到消息 | 正常行为——ConnectionManager 向所有连接广播，两端都收到 |
| **匹配被拒绝** | 没有匹配成功，不会有聊天室 | 拒绝时只更新 match.status='rejected'，不创建 chat。流程在此终止 |
| **用户被对方拉黑/举报** | 已有聊天室怎么处理 | 聊天室保留（证据留存），但禁止发送新消息。返回错误码告知用户 |
| **消息审核被拦截** | 消息已输入但发不出去 | 服务端返回 `{"type": "error", "reason": "内容不合规", "detail": "..."}`。消息不落库 |
| **WebSocket 连接断开重连** | 断线期间的消息丢失 | 重连后不依赖 WebSocket 补推——客户端主动 GET /messages?since={last_msg_id} 拉取增量 |

---

### 11.4 修正后的完整链路图

```
                        ┌─── 服务端同步事务 ───┐
                        │                       │
  用户A 发起匹配请求 ──→ 用户B 收到通知并同意    │
                        │   ├── match.status = 'accepted'
                        │   ├── chat 自动创建     │
                        │   └── 双方收到通知       │
                        │                       │
                        └───────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
              用户A 看到通知              用户B 看到通知
                    │                         │
              点击进入聊天                点击进入聊天
                    │                         │
        ┌─────── HTTP ───────┐    ┌─────── HTTP ───────┐
        │ GET /messages      │    │ GET /messages      │  ← 拉历史消息
        │ WebSocket connect  │    │ WebSocket connect  │  ← 建实时通道
        └────────────────────┘    └────────────────────┘
                    │                         │
                    └──────────┬──────────────┘
                               ▼
                        ┌─ 实时聊天 ─┐
                        │ 消息发送    │
                        │ AI 审核    │
                        │ 持久化     │
                        │ WebSocket  │
                        │   推送     │
                        └───────────┘
```

---

### 11.5 可行性总结

| 环节 | 可行？ | 一句话 |
|------|:---:|--------|
| 匹配成功 → 创建聊天室 | ✅ **可行且应该原子化** | 在同一事务中完成，不需要拆分 |
| 创建聊天室 → WebSocket 连接 | ⚠️ **有用户决策断点** | 中间需要用户看到通知并点击进入——不能自动建立连接 |
| WebSocket 连接 → 实时聊天 | ✅ **可行** | FastAPI 原生 WebSocket + 连接管理器，技术成熟 |
| 整体链路 | ✅ **可行** | 理解两个断点（用户决策 + 主动连接）后，实现路径清晰 |

**核心要记住的三件事**：

1. **前两步是原子的**：匹配成功和创建聊天室在同一个数据库事务中完成，不存在中间状态
2. **第三步不是一个自动步骤**：WebSocket 连接是用户主动进入聊天页面时由客户端发起的，不要试图在匹配成功时自动建立
3. **离线是常态不是异常**：校园场景下，一方在线一方离线是常见的——消息持久化 + HTTP 历史拉取 + WebSocket 在线推送，三条腿都要有

---

## 十二、附录

### A. 依赖清单（requirements.txt 内容规划）

| 包名 | 用途 |
|------|------|
| `fastapi` | Web 框架 |
| `uvicorn[standard]` | ASGI 服务器 |
| `sqlalchemy[asyncio]` | 异步 ORM |
| `aiosqlite` | SQLite 异步驱动 |
| `pydantic` | 数据校验（v2） |
| `pydantic-ai` | AI Agent 框架 |
| `pydantic-settings` | 配置管理 |
| `python-jose[cryptography]` | JWT 处理 |
| `passlib[bcrypt]` | 密码哈希 |
| `python-dotenv` | .env 读取 |
| `alembic` | 数据库迁移 |
| `python-multipart` | 文件上传支持 |
| `pytest` | 测试框架 |
| `pytest-asyncio` | 异步测试支持 |
| `httpx` | 测试用 HTTP 客户端 |

### B. API 端点速查表

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 | 否 |
| POST | `/api/v1/auth/login` | 用户登录 | 否 |
| POST | `/api/v1/auth/refresh` | 刷新令牌 | 否 |
| GET | `/api/v1/users/me` | 获取当前用户资料 | 是 |
| PUT | `/api/v1/users/me` | 更新当前用户资料 | 是 |
| POST | `/api/v1/posts` | 发布搭子帖 | 是 |
| GET | `/api/v1/posts` | 帖子列表（筛选+分页） | 是 |
| GET | `/api/v1/posts/{id}` | 帖子详情 | 是 |
| PUT | `/api/v1/posts/{id}` | 更新帖子 | 是 |
| DELETE | `/api/v1/posts/{id}` | 关闭帖子 | 是 |
| GET | `/api/v1/matches/recommendations` | AI 推荐列表 | 是 |
| POST | `/api/v1/matches/request/{user_id}` | 发起匹配 | 是 |
| GET | `/api/v1/matches` | 我的匹配列表 | 是 |
| GET | `/api/v1/chats` | 我的会话列表 | 是 |
| POST | `/api/v1/chats/{chat_id}/messages` | 发送消息 | 是 |
| GET | `/api/v1/chats/{chat_id}/messages` | 历史消息 | 是 |
| GET | `/api/v1/notifications` | 通知列表 | 是 |
| PUT | `/api/v1/notifications/{id}/read` | 标记已读 | 是 |
| PUT | `/api/v1/notifications/read-all` | 全部已读 | 是 |
