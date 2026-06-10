# 🚀 CampusBuddy 免费部署指南

## 整体架构

```
用户浏览器
    ├── GitHub Pages          →  前端 Vue 页面
    │   https://<用户名>.github.io/campus-buddy/
    │
    └── Render (免费)          →  后端 FastAPI
        https://campus-buddy-api.onrender.com
```

## ⚠️ 免费方案限制

- Render 免费版 **15 分钟无人访问会休眠**，首次唤醒需等待 30~60 秒
- Render 免费版磁盘是临时的，SQLite 数据**重启后可能被清空**
- 每月 750 小时免费额度（刚好够一个实例）
- GitHub Pages 每月 100GB 流量（足够展示使用）

---

## 第一步：创建 GitHub 仓库

1. 打开 https://github.com/new
2. 仓库名填 `campus-buddy`（或你喜欢的名字）
3. 不要勾选 "Add a README file"（本地已有代码）
4. 创建后在本地执行：

```bash
git remote add origin https://github.com/<你的用户名>/campus-buddy.git
git branch -M main
git push -u origin main
```

推送后 GitHub Actions 会自动构建前端并部署到 GitHub Pages。

---

## 第二步：部署后端到 Render

### 2.1 创建 Render 账号

打开 https://render.com → 用 GitHub 账号注册登录

### 2.2 一键部署（推荐）

1. Render 面板 → **New** → **Blueprint**
2. 选择你的 `campus-buddy` 仓库
3. Render 会读取 `render.yaml` 自动配置
4. 点击 **Apply**，等待构建完成（约 3-5 分钟）

### 2.3 手动部署（备选）

如果 Blueprint 不行，手动创建：

1. Render 面板 → **New** → **Web Service**
2. 选择你的仓库
3. 配置如下：

| 配置项 | 值 |
|--------|-----|
| Name | `campus-buddy-api` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Plan | Free |

4. 添加环境变量：

| Key | Value |
|-----|-------|
| `SECRET_KEY` | 随便输一串乱码（如 `a8f3d2k9...`） |
| `JWT_SECRET_KEY` | 另一串乱码 |
| `PDAI_BASE_URL` | `https://api.deepseek.com` |
| `PDAI_API_KEY` | `sk-你的deepseek-api-key` |
| `PDAI_MODEL` | `deepseek-chat` |
| `CORS_ORIGINS` | `["*"]` |

5. 点击 **Create Web Service**

### 2.4 获取后端地址

部署成功后，Render 会给你一个 URL，类似：
```
https://campus-buddy-api.onrender.com
```

记下这个地址，下一步要用。

---

## 第三步：配置前端指向后端

1. 打开你的 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions**
2. 切换到 **Variables** 标签
3. 点击 **New repository variable**，添加：

| Name | Value |
|------|-------|
| `VITE_API_BASE_URL` | `https://campus-buddy-api.onrender.com/api/v1` |

4. 如果你的仓库名不是 `campus-buddy`，再添加一个：

| Name | Value |
|------|-------|
| `VITE_BASE` | `/你的仓库名/` |

5. 回到 **Actions** 标签 → 点击 **Deploy Frontend to GitHub Pages** → **Run workflow** 手动触发一次

---

## 第四步：开启 GitHub Pages

1. 仓库 → **Settings** → **Pages**
2. **Source** 选择 **GitHub Actions**
3. 等待部署完成，访问 `https://<用户名>.github.io/campus-buddy/`

---

## 第五步：验证部署

1. 访问前端地址 → 应该能看到注册/登录页面
2. 注册一个账号 → 如果能注册成功，说明前后端联通了
3. 访问后端 Swagger 文档：`https://campus-buddy-api.onrender.com/docs`

---

## 常见问题

### Q: 访问时页面白屏？
A: 按 F12 打开控制台，看报错。通常是 `VITE_BASE` 路径不对，检查变量是否设成 `/你的仓库名/`。

### Q: 注册报错 "Network error"？
A: 检查 `VITE_API_BASE_URL` 变量是否正确，注意结尾要有 `/api/v1`。

### Q: Render 后端太慢？
A: 免费版冷启动需要 30-60 秒。可以用 [UptimeRobot](https://uptimerobot.com) 设置每 5 分钟 ping 一次你的后端，防止休眠。

### Q: DeepSeek API 费用？
A: DeepSeek API 非常便宜，deepseek-chat 模型约 ¥1/百万 token，日常使用几乎不花钱。

### Q: 如何更新部署？
A: 推送到 GitHub → Actions 自动部署前端；Render 自动检测推送并重新部署后端。
