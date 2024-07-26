# 使用官方 Python 基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到工作目录
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 10055

# 运行应用程序
CMD ["python", "pieces.py"]