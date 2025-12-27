# Docker部署指南

## 📋 目录
- [架构说明](#架构说明)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [常用命令](#常用命令)
- [故障排查](#故障排查)

---

## 🏗️ 架构说明

### 整体架构
```
┌─────────────────────────────────────────────────────────┐
│                  外部访问（端口7860）                      │
│                    http://0.0.0.0:7860                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│            Nginx反向代理容器（端口7860）                   │
│  - 前端静态文件服务（React构建产物）                        │
│  - API请求代理 → FastAPI后端                              │
│  - 静态资源服务（音频、视频文件）                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│          FastAPI后端容器（内部端口8001）                   │
│  - AI模型调用（ModelScope、阿里云）                        │
│  - TTS语音合成                                           │
│  - 视频生成业务逻辑                                       │
└─────────────────────────────────────────────────────────┘
```

### 端口说明
| 端口 | 服务 | 说明 |
|------|------|------|
| **7860** | Nginx（前端） | 对外暴露的唯一端口，访问应用 |
| 8001 | FastAPI（后端） | 内部端口，仅容器间通信 |

### 多阶段构建
1. **frontend-builder**：构建React前端（生成静态文件）
2. **backend**：运行FastAPI后端服务
3. **final**：最终的Nginx镜像（集成前端静态文件 + 反向代理）

---

## 🚀 快速开始

### 1. 准备环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入API密钥
# 必填：
# - MODELSCOPE_API_KEY
# - ALIYUN_ACCESS_KEY_ID
# - ALIYUN_ACCESS_KEY_SECRET
# - DASHSCOPE_API_KEY
```

### 2. 使用Docker Compose部署（推荐）

#### 启动服务
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看服务状态
docker-compose ps
```

#### 访问应用
```bash
# 浏览器访问
http://localhost:7860
```

#### 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 3. 使用单独Docker命令部署

#### 构建镜像
```bash
# 构建前端镜像
docker build --target frontend-builder -t travel-assistant-frontend:build .

# 构建后端镜像
docker build --target backend -t travel-assistant-backend:latest .

# 构建最终镜像
docker build -t travel-assistant:latest .
```

#### 运行容器
```bash
# 创建网络
docker network create travel-assistant-network

# 运行后端容器
docker run -d \
  --name travel-assistant-backend \
  --network travel-assistant-network \
  --env-file .env \
  -v $(pwd)/static:/app/static \
  -p 8001:8001 \
  travel-assistant-backend:latest

# 运行前端容器
docker run -d \
  --name travel-assistant-frontend \
  --network travel-assistant-network \
  -p 7860:7860 \
  -v $(pwd)/static:/app/static:ro \
  --link travel-assistant-backend:backend \
  travel-assistant:latest
```

---

## ⚙️ 配置说明

### 环境变量
| 变量名 | 说明 | 是否必填 |
|--------|------|---------|
| `MODELSCOPE_API_KEY` | ModelScope API密钥 | ✅ 是 |
| `ALIYUN_ACCESS_KEY_ID` | 阿里云AccessKey ID | ✅ 是 |
| `ALIYUN_ACCESS_KEY_SECRET` | 阿里云AccessKey Secret | ✅ 是 |
| `ALIYUN_TTS_DEFAULT_VOICE` | 默认TTS语音 | ❌ 否（默认：xiaoyun） |
| `DASHSCOPE_API_KEY` | 阿里云DashScope API密钥 | ✅ 是 |
| `OPENAI_API_KEY` | OpenAI API密钥 | ❌ 否（可选） |
| `BACKEND_PORT` | 后端端口 | ❌ 否（默认：8001） |

### Nginx配置（nginx.conf）
主要配置项：
- **前端端口**：`listen 7860`
- **API代理**：`location /api/` → `http://backend:8001/api/`
- **静态资源**：`location /static/` → `/app/static/`
- **最大上传大小**：`client_max_body_size 100M`
- **超时设置**：300秒（支持长时间API调用）

### 数据持久化
```yaml
# static目录挂载（音频、视频文件）
volumes:
  - ./static:/app/static
```

---

## 🔧 常用命令

### Docker Compose命令
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f [service_name]

# 查看服务状态
docker-compose ps

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh

# 重新构建镜像
docker-compose build

# 重新构建并启动
docker-compose up -d --build

# 删除所有容器和卷
docker-compose down -v
```

### Docker命令
```bash
# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 查看容器日志
docker logs -f [container_id]

# 进入容器
docker exec -it [container_id] /bin/bash

# 复制文件到容器
docker cp [local_file] [container_id]:[path]

# 复制文件从容器
docker cp [container_id]:[path] [local_file]

# 删除容器
docker rm [container_id]

# 删除镜像
docker rmi [image_id]

# 清理未使用的资源
docker system prune -a
```

---

## 🐛 故障排查

### 问题1：容器无法启动
```bash
# 查看容器日志
docker-compose logs backend
docker-compose logs frontend

# 检查环境变量是否正确配置
cat .env

# 检查端口是否被占用
netstat -tunlp | grep 7860
netstat -tunlp | grep 8001
```

### 问题2：API调用失败
```bash
# 检查后端服务状态
docker-compose ps backend

# 查看后端日志
docker-compose logs -f backend

# 检查网络连通性
docker-compose exec frontend ping backend
```

### 问题3：静态文件无法访问
```bash
# 检查static目录权限
ls -la static/

# 检查static目录挂载
docker-compose exec frontend ls -la /app/static/

# 修复权限
chmod -R 755 static/
```

### 问题4：内存不足
```bash
# 查看容器资源使用情况
docker stats

# 限制容器内存使用
# 在docker-compose.yml中添加：
# deploy:
#   resources:
#     limits:
#       memory: 2G
```

### 问题5：前端构建失败
```bash
# 重新构建前端
docker-compose build frontend

# 清理缓存后重新构建
docker-compose build --no-cache frontend
```

### 问题6：Nginx配置错误
```bash
# 测试Nginx配置
docker-compose exec frontend nginx -t

# 重新加载Nginx配置
docker-compose exec frontend nginx -s reload
```

---

## 📊 监控与维护

### 健康检查
```bash
# 检查前端健康状态
curl http://localhost:7860/health

# 检查后端健康状态
curl http://localhost:7860/api/docs
```

### 日志查看
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看最近100行日志
docker-compose logs --tail=100
```

### 资源监控
```bash
# 查看容器资源使用情况
docker stats

# 查看磁盘使用情况
docker system df

# 清理未使用的镜像和容器
docker system prune -a
```

---

## 🔒 安全建议

1. **不要提交.env文件到Git**
   - `.env`已加入`.gitignore`
   - 使用`.env.example`作为模板

2. **使用HTTPS**
   - 生产环境建议配置SSL证书
   - 使用Let's Encrypt免费证书

3. **限制访问**
   - 使用防火墙限制端口访问
   - 配置Nginx IP白名单

4. **定期更新**
   - 定期更新基础镜像（nginx、python、node）
   - 更新依赖包

---

## 📝 部署清单

- [ ] 配置环境变量（.env文件）
- [ ] 创建static目录（`mkdir -p static`）
- [ ] 检查端口7860、8001是否被占用
- [ ] 构建Docker镜像
- [ ] 启动服务（docker-compose up -d）
- [ ] 访问应用（http://localhost:7860）
- [ ] 测试功能（目的地推荐、行程规划等）
- [ ] 查看日志确认无错误

---

## 📞 技术支持

如遇到问题，请检查：
1. Docker版本是否 >= 20.10
2. Docker Compose版本是否 >= 2.0
3. 环境变量是否正确配置
4. 网络连接是否正常
5. API密钥是否有效

---

## 📚 参考资料
- [Docker官方文档](https://docs.docker.com/)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [Nginx配置指南](https://nginx.org/en/docs/)
- [FastAPI部署指南](https://fastapi.tiangolo.com/deployment/)
