# ============================================
# 多阶段构建：银发族智能旅行助手
# ============================================

# ============================================
# 阶段1：构建前端（React + Vite）
# ============================================
FROM node:18-alpine AS frontend-builder

# 设置工作目录
WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package.json frontend/package-lock.json ./

# 安装依赖
RUN npm ci --only=production

# 复制前端源代码
COPY frontend/ ./

# 构建前端（生产环境构建）
RUN npm run build

# ============================================
# 阶段2：后端（FastAPI + Python）
# ============================================
FROM python:3.10-slim AS backend

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 复制项目代码
COPY . .

# 创建静态文件目录
RUN mkdir -p static

# 设置FastAPI后端端口
ENV BACKEND_PORT=8001

# 暴露后端端口（内部端口，不直接暴露给外部）
EXPOSE 8001

# 启动FastAPI服务
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001"]

# ============================================
# 阶段3：最终镜像（Nginx反向代理）
# ============================================
FROM nginx:alpine AS final

# 安装curl（用于健康检查）
RUN apk add --no-cache curl

# 复制自定义Nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 从frontend-builder复制构建好的前端静态文件
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# 复制静态资源目录（生成的音频、视频等）
RUN mkdir -p /app/static
COPY static /app/static

# 设置权限
RUN chmod -R 755 /app/static

# 暴露前端端口（7860）
EXPOSE 7860

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]
