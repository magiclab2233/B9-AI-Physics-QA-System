# 使用Python 3.10作为基础镜像
FROM registry.sensetime.com/sensestudy/vecsearch:1.0-baseimage

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY src/ ./src/
COPY data/ ./data/

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动服务
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"] 