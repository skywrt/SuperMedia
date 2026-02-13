# SuperMedia - 色花堂资源搜索下载工具

[![Build and Push Docker Image](https://github.com/skywrt/supermedia/actions/workflows/docker-build.yml/badge.svg)](https://github.com/skywrt/supermedia/actions/workflows/docker-build.yml)

支持 amd64/arm64 多架构平台的 Docker 容器，用于搜索色花堂资源并推送到下载器。

## 功能特点

- 🔐 安全的登录认证
- 🔍 番号搜索功能
- 📱 响应式Web界面
- 🚀 多架构支持 (amd64/arm64)
- ⚡ 异步下载器支持
- 🎯 支持多个下载器后端

## 快速开始

### 使用预构建镜像

```bash
# 登录GitHub Container Registry
echo $PAT | docker login ghcr.io -u skywrt --password-stdin

# 拉取并运行
docker run -d \
  --name suppermedia \
  -p 5678:5678 \
  -v ./config.json:/app/config.json \
  -e WEB_USERNAME=admin \
  -e WEB_PASSWORD=yourpassword \
  ghcr.io/skywrt/supermedia:latest
