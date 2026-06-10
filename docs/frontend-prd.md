# Campus BUDDY 前端 PRD

> **版本**: v1.0 | **日期**: 2026-06-09 | **技术栈**: Vue 3 + Vite + Element Plus
> 后端 API 已完成，本文档所有功能与后端接口一一对齐。

---

## 一、产品概述

Campus BUDDY 是面向在校大学生的**校园搭子社交平台**。用户发布**邀约（Invitation）**来找搭子（学习/运动/约饭/出行），系统智能匹配推荐，匹配成功后实时聊天。

> **核心概念**：**邀约（Invitation）**是可被响应的公开招募帖，**搭子（Buddy）**是匹配成功后的关系。一个邀约 → 多人响应 → 匹配成功 → 成为搭子 → 聊天。

**用户端**: Mobile-First H5（优先手机端，兼容桌面）| **设计原则**: 触控友好，拇指热区适配

**核心闭环**: 发现邀约 → 发起匹配 → 对方回应 → 实时聊天 → 线下见面

---

## 二、用户画像

| 画像 | 场景 | 核心诉求 |
|------|------|----------|
| **期末复习党**（大二/大三） | 找图书馆/自习室学习搭子 | 同校同专业，互相监督 |
| **运动爱好者**（全年级） | 约羽毛球/篮球球友 | 匹配兴趣相同、时间契合的人 |
| **新生社交**（大一） | 认识新朋友、找饭搭子 | 拓展社交圈，降低社交门槛 |
| **校园探索者** | 周末出游/探店/爬山组队 | 找到同行伙伴，分摊费用 |

---

## 三、功能全景

```
Campus BUDDY 前端
├── 认证模块        注册 / 登录 / Token自动刷新 / 退出
├── 邀约模块        邀约广场 / 详情 / 发布 / 编辑 / 关闭 / 筛选搜索
├── 匹配模块        智能推荐 / 发起匹配 / 接受拒绝 / 匹配列表
├── 聊天模块        会话列表 / 实时聊天 / WebSocket / 消息已读
├── 通知模块        通知列表 / 未读角标 / 单条/批量/全部已读
├── 个人中心        资料展示 / 编辑 / 他人资料 / 统计
└── 通用模块        Loading / Toast / 空状态 / 网络异常 / 响应式
```

**优先级**: P0（核心闭环）> P1（体验增强）> P2（效率提升）> P3（锦上添花）

---

## 四、页面清单与路由

| 页面 | 路由 | 认证 | Tab | 说明 |
|------|------|:---:|:---:|------|
| 登录 | `/login` | 否 | - | 邮箱/用户名+密码 |
| 注册 | `/register` | 否 | - | 分步：账号→学校信息 |
| 邀约广场 | `/posts` | 是 | 1 | 首页，邀约卡片列表+筛选+搜索 |
| 邀约详情 | `/posts/:id` | 是 | - | 完整信息+发布者+匹配入口 |
| 发布邀约 | `/posts/new` | 是 | - | 表单页 |
| 编辑邀约 | `/posts/:id/edit` | 是 | - | 仅作者 |
| 智能推荐 | `/recommendations` | 是 | 2 | 匹配分数+推荐理由 |
| 我的匹配 | `/matches` | 是 | - | 状态筛选（待确认/已匹配/已拒绝） |
| 会话列表 | `/chats` | 是 | 3 | 最后消息预览+未读角标 |
| 聊天窗口 | `/chats/:id` | 是 | - | WebSocket实时+HTTP历史 |
| 通知列表 | `/notifications` | 是 | 4 | 未读蓝点+按类型区分 |
| 个人中心 | `/profile` | 是 | 5 | 资料+统计+退出 |
| 编辑资料 | `/profile/edit` | 是 | - | 部分更新表单 |
| 他人资料 | `/users/:id` | 是 | - | 公开资料+匹配按钮 |

**底部 Tab 栏**: 发现(1) / 推荐(2) / 消息(3) / 通知(4) / 我的(5)（Tab 3 和 4 带未读数字角标）

**路由守卫**: 未登录 → `/login`；已登录访问登录/注册页 → `/posts`

> **命名约定**：前端路由 `/posts` 对应后端 API `/api/v1/posts`（历史原因保留），但产品层面统一称为**邀约（Invitation）**。前端代码中 `post` 相关变量/组件名可保持不变，仅用户可见文案使用"邀约"。

---

## 五、页面详细需求

### 5.1 登录 `/login`

- 登录方式：邮箱或用户名 + 密码
- 密码输入框可切换显示/隐藏
- 登录成功：存储 token → 跳转 `/posts`（邀约广场）；失败：表单上方错误提示
- 按钮防重复提交（loading 态），支持回车提交
- 已登录用户访问本页自动跳转首页

### 5.2 注册 `/register`

- **单页分步**（非多页跳转）：① 账号信息 → ② 学校信息，Step 组件串联
- 账号信息：用户名（3-50字符）、邮箱、手机号（选填）、密码（6-128）、确认密码
- 学校信息：大学（必填，建议联想输入）、学院、专业、年级（下拉选择）、昵称、性别
- 校验：失焦触发字段校验；邮箱格式；确认密码一致性；必填未完成时按钮置灰
- 注册成功自动登录并跳转首页

### 5.3 邀约广场 `/posts`（首页）

**布局**: 顶部搜索栏 → 类别标签栏 → 邀约卡片列表 → 右下角 FAB 发布按钮 → 底部 Tab

**邀约卡片展示**: 类别图标+标签、标题、描述（2行截断）、📍地点 🕐时间、👤发布者昵称·院系·年级、#标签列表、发布时间（相对时间）

**功能**:
- 类别筛选标签栏：全部/学习/运动/约饭/出行/其他，切换时重置列表
- 关键词搜索（标题+描述），防抖 500ms，与类别筛选叠加
- 每页 20 条，滚动到底自动加载更多（无限滚动）
- 下拉刷新
- 点击卡片 → 邀约详情；点击标签 → 按该标签筛选
- 空状态："还没有邀约，快来发布第一个吧！" + 发布按钮引导
- 已过期邀约不出现在列表中（后端已过滤）

### 5.4 邀约详情 `/posts/:id`

- 展示：类别、标题、完整描述、📍地点、🕐时间、👥人数（current/target）、#标签、发布时间
- **发布者信息卡片**：头像、昵称、院系、年级、bio、兴趣标签 → 可点击跳转他人资料
- **主操作按钮**「我想和TA成为搭子」→ 二次确认弹窗 → 发起匹配 → Toast "请求已发送"
- 已匹配/已发送请求 → 按钮灰显不可点击
- 自己的邀约 → 显示「编辑邀约」「关闭邀约」操作（关闭需二次确认）
- 已关闭邀约 → 显示状态标签，隐藏操作按钮

### 5.5 发布邀约 `/posts/new`

- **类别**：大卡片/按钮组单选（学习/运动/约饭/出行/其他），必选
- **标题**：必填，最长 200 字符，实时字数显示
- **描述**：选填，最长 5000 字符，textarea 自动增高
- **目标人数**：数字步进器，默认 1，范围 1-100
- **标签**：输入框回车添加，显示为可删除 chip，上限 10 个
- **地点/时间**：选填，各最长 200 字符
- **截止日期**：日期选择器，选填
- 发布成功 → 跳转邀约详情；失败 → 字段下方错误提示
- AI 审核拦截 → 弹窗告知违规原因，引导修改
- 草稿自动保存 localStorage（P2）

### 5.6 智能推荐 `/recommendations`

> **V1 推荐算法说明**：推荐结果由后端规则引擎计算（非 LLM），核心维度：
> - **标签重合度**：双方 interest tags 交集数量，重合越多分数越高
> - **学校权重**：同校优先 > 同城 > 其他学校
> - **时间权重**：最近活跃度（发布邀约/登录时间）加分
>
> 推荐理由由后端模板根据匹配维度自动生成（如"你们有 3 个共同兴趣标签，同校同专业"），非 LLM 实时生成。后续版本可升级为 LLM 推荐。

**推荐卡片**: 匹配分数（大字+环形进度条，90+=绿/70-89=蓝/50-69=橙/<50=灰）、头像、昵称、学校、专业、年级、兴趣标签、推荐理由（引用样式，15-40字中文）

- 按分数降序排列，默认展示 10 人
- 「想搭」按钮 → 发起匹配 → 卡片变为"请求已发送"遮罩态
- 「查看资料」→ 他人资料页
- 空状态："完善你的兴趣标签和个人简介，AI 可以给你更精准的推荐哦～" + 引导完善资料

### 5.7 我的匹配 `/matches`

- 列表按更新时间倒序，分页加载
- 顶部状态筛选：全部/待确认/已匹配/已拒绝
- 每项展示：对方头像、昵称、学校、匹配分数、状态标签（待确认=橙/已匹配=绿/已拒绝=灰）、时间
- **别人发来的待确认** → 显示「接受」「拒绝」按钮（均需二次确认）
- **我发起的待确认** → 显示"等待对方回应"文案
- **已匹配** → 点击可跳转聊天窗口
- 接受匹配成功 → 自动跳转聊天页
- 空状态："还没有匹配记录，去发现页找搭子吧！" + 跳转引导

### 5.8 聊天模块

#### 会话列表 `/chats`

- 按最后消息时间倒序，分页加载
- 每项：对方头像、昵称、最后消息预览（1行截断）、时间（相对时间）、未读红色数字角标
- 点击进入聊天窗口
- 空状态："还没有聊天，去发现页找个搭子吧！"

#### 聊天窗口 `/chats/:id`

**布局**: 顶部（返回+对方昵称+在线状态）→ 消息列表（上拉加载历史）→ 底部输入栏

**消息气泡**: 自己的右对齐蓝色，对方的左对齐灰色；显示发送时间（同分钟内不重复）；日期变化时显示日期分隔线

**功能**:
- 进入时 HTTP 拉取最近 50 条历史消息（按时间正序），自动滚到底部
- 建立 WebSocket：`ws://host/api/v1/ws/chat/{chat_id}?token=xxx`
- 回车发送，Shift+回车换行；空消息不可发送
- 发送时 AI 审核，拦截则弹窗提示；发送失败气泡显示红色感叹号+点击重发
- 新消息到达时若用户已在底部附近则自动滚动
- 对方在线状态（基于 WebSocket 上下线事件）

**WebSocket 管理**:
- 心跳：客户端每 30s 发 `{"type":"ping"}`，60s 未收到 pong 视为断线
- 断线重连：指数退避（1→2→4→8s，上限 30s），重连后 HTTP 拉增量消息（since_id）
- 离开聊天窗口关闭连接；Token 过期静默刷新后重连
- 收到消息但窗口未激活 → 会话列表显示未读角标

### 5.9 通知 `/notifications`

- 按时间倒序，分页加载；顶部筛选：全部/未读
- 每项：类型图标（🤝匹配/💬消息/📢系统）、标题、内容、时间
- 未读项：左侧蓝色圆点 + 背景色略深；点击进入对应页面 + 自动标记已读
- 顶部「全部已读」按钮；左滑标记已读（移动端 P2）
- 三种通知类型：

| 类型 | 触发场景 | 标题示例 |
|------|----------|----------|
| match | 有人发起匹配 | "新的搭子请求" |
| match | 对方接受/拒绝 | "匹配成功！" / "搭子请求被拒绝" |
| message | 收到聊天消息 | "新消息"（含发送者和内容预览） |
| system | 系统公告 | 系统通知（预留） |

### 5.10 个人中心 `/profile`

- **顶部**: 大头像+昵称+学校·专业·年级+bio +「编辑资料」按钮
- **统计卡片**: 我的邀约数 / 匹配数 / 搭子数（已匹配）
- **功能列表**: 我的邀约 / 我的匹配 / 账号设置(预留) / 帮助与反馈(预留) / 退出登录
- 退出登录：二次确认 → 清除 token → 跳转登录页

### 5.11 编辑资料 `/profile/edit`

- 可编辑：头像(URL)、昵称、性别、bio、标签、手机号、大学、学院、专业、年级
- 标签编辑交互与发布邀约一致
- 初始值自动填充当前资料；保存失败字段下方显示错误
- 保存成功 → 返回个人中心并刷新

### 5.12 他人资料 `/users/:id`

- 公开信息：头像、昵称、学校、专业、年级、bio、兴趣标签
- **不展示**：邮箱、手机号
- 「想和TA成为搭子」按钮；已有匹配记录则显示匹配状态

---

## 六、状态管理

### Pinia Store 设计

| Store | 核心 State | 核心 Actions |
|-------|-----------|-------------|
| **auth** | accessToken, refreshToken, currentUser, isAuthenticated | login, register, refreshToken, fetchUser, updateProfile, logout |
| **posts** | posts[], currentPost, pagination, filters, isLoading | fetchPosts, fetchPostById, createPost, updatePost, closePost, setFilters（代码层保留 post 命名，用户面为邀约） |
| **matches** | recommendations[], matches[], isLoading | fetchRecommendations, requestMatch, handleMatchAction, fetchMyMatches |
| **chats** | chatList[], currentChat, messages[], unreadTotal, wsConnected | fetchChatList, fetchMessages, sendMessage, connectWS, disconnectWS, markRead |
| **notifications** | notifications[], unreadCount, isLoading | fetchNotifications, markRead, markAllRead, markBatchRead |
| **ui** | globalLoading | — |

### API 层设计（Axios）

- **请求拦截器**: 自动注入 `Authorization: Bearer {access_token}`
- **响应拦截器**: 401→自动 refresh→重试；从 `APIResponse` 提取 `data`；网络错误统一 Toast
- **Token 存储**: access_token 存内存(Pinia)，refresh_token 存 localStorage

---

## 七、视觉设计风格

### 7.1 设计定位

扁平化、现代、简洁的校园风格。卡片化布局，微圆角轻阴影，年轻活力但不幼稚。

### 7.2 色彩体系

| Token | 色值 | 用途 |
|-------|------|------|
| **主色 Primary** | `#409EFF` | 主按钮、Tab 选中、链接、强调 |
| **辅色 Secondary** | `#67C23A` | 成功状态、在线、高匹配度 |
| **危险 Danger** | `#F56C6C` | 拒绝、删除、未读角标、违规 |
| **背景 Background** | `#F5F7FA` | 全局底层背景 |
| **文字 Text** | `#303133` | 正文主文字 |
| **类别色** | 学习 `#409EFF` / 运动 `#F56C6C` / 约饭 `#E6A23C` / 出行 `#67C23A` / 其他 `#909399` | 各类别独立标识色 |

- 按钮 hover：主色加深 10%
- 标签、进度条、消息气泡统一使用主色/辅色体系

### 7.3 字体层级

| 层级 | 字号 | 字重 | 字体 | 用途 |
|------|:---:|:---:|------|------|
| H1 | 24px | 700 | Inter | 详情页大标题 |
| H2 | 18px | 600 | Inter | 卡片标题、页面标题 |
| Body | 15px | 400 | Roboto | 正文、描述 |
| Caption | 13px | 400 | Roboto | 辅助信息、时间、地点 |

### 7.4 圆角与阴影

| 元素 | 圆角 | 阴影 |
|------|:---:|------|
| 卡片 | 12px | `0 4px 12px rgba(0,0,0,0.08)` |
| 卡片 hover | 12px | `0 8px 24px rgba(0,0,0,0.12)`（shadow-lg） |
| 按钮 | 8px | — |
| 聊天气泡 | 16px | — |
| 输入框 | 8px | — |
| 标签/徽章 | 4px | — |

### 7.5 响应式布局

| 断点 | 宽度 | 列数 | 布局特征 |
|------|------|:---:|------|
| **Mobile** | < 768px | 1 列 | 底部 Tab Bar，全屏页面 |
| **Tablet** | 768-1024px | 2 列 | 侧边导航（无 Tab Bar） |
| **Desktop** | > 1024px | 3 列 | 最大宽 1200px 居中 |

### 7.6 图标与动效

- **图标**: Element Plus Icons 线性风格，Tab 未选中灰 `#909399`、选中主色
- **按钮 hover**: 主色加深 10%
- **卡片 hover**: shadow-lg 浮起效果
- **页面切换**: fade / slide 过渡
- **弹窗**: fade-in / fade-out
- **消息列表**: 新消息自动滚动到底部

---

## 八、关键交互规范

### 8.1 加载与状态

| 场景 | 处理 |
|------|------|
| 首屏加载 | 全屏 Spinner |
| 列表追加 | 底部"加载中..."或骨架屏 |
| 表单提交 | 按钮 loading + "提交中..." |
| 下拉刷新 | 顶部下拉动画 |
| WebSocket 连接中 | 聊天顶部黄色"连接中..." |

### 8.2 空状态文案

| 场景 | 文案 | 引导操作 |
|------|------|----------|
| 邀约列表空 | "还没有邀约，快来发布第一个吧！" | 发布按钮 |
| 搜索无结果 | "没有找到相关邀约，试试其他关键词？" | 清除搜索 |
| 推荐列表空 | "完善你的兴趣标签和个人简介..." | 完善资料 |
| 匹配/会话/通知空 | "还没有XX，去发现页找搭子吧！" | 去发现 |

### 8.3 错误处理

| 错误 | 处理 |
|------|------|
| 网络断开 | 顶部横幅"网络连接已断开" |
| 401 | 自动刷新token，失败→登录页 |
| 403/404/409/422 | Toast 或表单字段错误提示 |
| 500 | "服务器繁忙，请稍后再试" |
| AI 审核拦截 | 弹窗显示违规原因，引导修改 |

### 8.4 二次确认场景

发起匹配、接受匹配、拒绝匹配、关闭邀约、退出登录——均需弹窗确认

---

## 九、组件架构

### 目录结构

```
src/
├── views/           ← 页面级组件（14个，对应路由）
├── components/
│   ├── common/      ← AppHeader, AppTabBar, LoadingSpinner, EmptyState, UserAvatar, InfiniteScroll
│   ├── post/        ← PostCard, PostForm, CategorySelector, PostStatusBadge（代码层保留 post 命名，用户面为邀约）
│   ├── user/        ← UserBriefCard, UserProfileForm, TagsEditor
│   ├── match/       ← RecommendationCard, MatchCard, MatchScoreBadge, MatchStatusBadge
│   ├── chat/        ← ChatListItem, MessageBubble, MessageInput, ChatHeader, DateDivider
│   └── notification/← NotificationItem, NotificationBadge
├── stores/          ← auth, posts, matches, chats, notifications, ui (Pinia)
├── composables/     ← useAuth, useWebSocket, useInfiniteScroll, usePagination, useDebounce
├── api/             ← client(Axios实例), auth, users, posts, matches, chats, messages, notifications
├── router/          ← index.ts (路由表+守卫)
├── utils/           ← format, storage, constants
└── assets/          ← styles (variables/global/mixins), images
```

### 组件原则

- 单一职责，每个组件 ≤300 行
- Props/Emits 使用 TypeScript 类型定义
- 所有 composable 和 store action 必须写 JSDoc

---

## 十、性能与非功能需求

| 指标 | 目标 |
|------|------|
| 首屏加载 (FCP) | < 1.5s（移动端 4G） |
| 可交互时间 (TTI) | < 3s |
| 消息发送延迟 | < 200ms（感知） |
| 打包体积 (gzip) | < 500KB |
| 列表滚动 | ≥ 55 FPS |

- **兼容性**: iOS Safari 15+, Android Chrome 10+, Chrome/Firefox/Edge 最新版, 微信内置浏览器
- **安全**: XSS 默认转义；access_token 仅存内存；路由守卫；敏感信息仅个人中心可见
- **图片懒加载**: 所有列表图片均懒加载

---

## 十一、开发阶段

| 阶段 | 内容 | 时间 |
|:---:|------|:---:|
| **一** | 项目骨架 + Vite/Vue3/Element Plus + 路由 + Axios + Pinia auth + 登录注册 | 2-3天 |
| **二** | 邀约广场/详情/发布 + 智能推荐 + 匹配 + 通知 + 个人中心/编辑 + 他人资料 + Tab栏 | 4-5天 |
| **三** | 会话列表 + 聊天窗口 + WebSocket管理 + 消息收发 + 历史分页 + 已读 + 断线重连 | 3-4天 |
| **四** | 错误处理完善 + 空状态 + 骨架屏 + 动效 + 响应式适配 + PWA + 全流程联调 | 2-3天 |
| **合计** | | **11-15天** |

### 阶段一验收
- [ ] 注册→登录→Token刷新→获取用户信息 全流程可走通
- [ ] 路由守卫正确拦截未登录/已登录状态

### 阶段二验收
- [ ] 邀约浏览/筛选/搜索/发布/详情/匹配全流程可走通
- [ ] 智能推荐正常展示，接受/拒绝匹配正常
- [ ] 通知列表+已读操作正常
- [ ] Tab栏导航+未读角标准确

### 阶段三验收
- [ ] WebSocket实时收发正常，双方实时看到消息
- [ ] 断线自动重连+增量消息拉取
- [ ] 历史消息分页加载，离开页面关闭WebSocket

### 阶段四验收
- [ ] 三端（手机/平板/桌面）布局正常
- [ ] 异常场景有合理兜底
- [ ] 完整用户流程可走通：注册 → 发布邀约 → 匹配 → 聊天

---

## 附录

### A. 后端 API 速查（前端视角）

| 方法 | 路径 | 说明 | Token |
|------|------|------|:---:|
| POST | `/api/v1/auth/register` | 注册 | 否 |
| POST | `/api/v1/auth/login` | 登录 | 否 |
| POST | `/api/v1/auth/refresh` | 刷新token | 否 |
| GET/PUT | `/api/v1/users/me` | 获取/更新当前用户 | 是 |
| POST/GET | `/api/v1/posts` | 发布邀约/邀约列表(筛选+分页) | 是 |
| GET/PUT/DELETE | `/api/v1/posts/:id` | 邀约详情/编辑/关闭 | 是 |
| GET | `/api/v1/matches/recommendations` | 智能推荐（V1规则引擎） | 是 |
| POST | `/api/v1/matches/request/:userId` | 发起匹配 | 是 |
| POST | `/api/v1/matches/:id/action` | 接受/拒绝 | 是 |
| GET | `/api/v1/matches` | 匹配列表(分页) | 是 |
| GET | `/api/v1/chats` | 会话列表 | 是 |
| GET/POST | `/api/v1/chats/:id/messages` | 历史消息/发送(HTTP) | 是 |
| POST | `/api/v1/chats/:id/messages/read` | 标记已读 | 是 |
| WS | `/api/v1/ws/chat/:id?token=xxx` | 实时聊天 | query |
| GET | `/api/v1/notifications` | 通知列表 | 是 |
| PUT | `/api/v1/notifications/:id/read` | 标记已读 | 是 |
| PUT | `/api/v1/notifications/read-all` | 全部已读 | 是 |
| PUT | `/api/v1/notifications/batch-read` | 批量已读 | 是 |

### B. 统一响应格式

```json
{ "code": 200, "message": "success", "data": {...} }
// 分页: { "items": [...], "total": 100, "page": 1, "page_size": 20 }
```

### C. Element Plus 关键组件

ElButton, ElInput, ElTag, ElBadge, ElAvatar, ElCard, ElSkeleton, ElEmpty, ElMessage, ElMessageBox, ElDialog, ElTabs, ElSteps, ElForm, ElPagination, ElDrawer, ElImage, ElBacktop, ElTooltip, ElPopconfirm

---

> **文档结束** | 基于后端实际代码分析撰写，所有功能与已实现 API 严格对齐。
