# Online Tools Platform 在线工具站

一个轻量级的在线工具平台，提供 PDF、图片、文本和开发者工具，支持 SEO 优化和广告变现。

## 功能特性

### PDF 工具
- PDF 压缩
- PDF 转 Word
- PDF 合并
- PDF 拆分
- 图片转 PDF

### 图片工具
- 图片压缩
- 格式转换 (WebP/PNG/JPEG/BMP)
- 图片裁剪
- 九宫格切图（可拖拽分割线）
- 按大小切分压缩
- ICO 图标生成

### 文本工具
- JSON 格式化
- Base64 编解码
- 正则表达式测试
- Markdown 转 HTML

### 开发者工具
- JWT 解码
- Cron 表达式生成器
- UUID 生成器

## 技术栈

- **后端**: Python 3.11 + FastAPI
- **前端**: 原生 HTML/CSS/JavaScript
- **测试**: Pytest + Hypothesis (属性测试)

## 快速开始

### 环境要求

- Python 3.11+
- pip 或 conda

### 安装依赖

```bash
# 使用 pip
pip install -r requirements.txt

# 或使用 conda
conda create -n tools python=3.11
conda activate tools
pip install -r requirements.txt
```

### 本地运行

```bash
# 开发模式
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

访问 http://localhost:8000 即可使用。

### 运行测试

```bash
pytest tests/ -v
```

## 生产部署

### 1. 服务器准备 (Ubuntu/Debian)

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 和依赖
sudo apt install python3.11 python3.11-venv python3-pip nginx -y

# 创建项目目录
sudo mkdir -p /var/www/tools
sudo chown $USER:$USER /var/www/tools
```

### 2. 部署代码

```bash
# 克隆代码
cd /var/www/tools
git clone <your-repo-url> .

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn
```

### 3. 创建 Systemd 服务

```bash
sudo nano /etc/systemd/system/tools.service
```

写入以下内容：

```ini
[Unit]
Description=Online Tools Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/tools
Environment="PATH=/var/www/tools/venv/bin"
ExecStart=/var/www/tools/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable tools
sudo systemctl start tools
sudo systemctl status tools
```

### 4. Nginx 配置

```bash
sudo nano /etc/nginx/sites-available/tools
```

写入以下配置：

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL 证书 (使用 Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    
    # 文件上传大小限制
    client_max_body_size 50M;
    
    # 静态文件缓存
    location /static/ {
        alias /var/www/tools/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 1000;
    
    # API 代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/tools /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. SSL 证书 (Let's Encrypt)

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

### 6. 防火墙配置

```bash
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## 1G 小机优化配置

对于 1GB 内存的小型服务器，使用以下优化配置：

### Gunicorn 配置 (减少 worker)

```bash
# 修改 systemd 服务，使用 2 个 worker
ExecStart=/var/www/tools/venv/bin/gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 --max-requests 1000 --max-requests-jitter 50
```

### Nginx 优化

```nginx
# 在 nginx.conf 的 http 块中添加
worker_processes 1;
worker_connections 512;

# 启用 sendfile
sendfile on;
tcp_nopush on;
tcp_nodelay on;

# 减少 buffer
client_body_buffer_size 10K;
client_header_buffer_size 1k;
large_client_header_buffers 2 1k;
```

### 添加 Swap (如果没有)

```bash
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 目录结构

```
.
├── api/                    # API 路由
│   ├── dev.py             # 开发者工具 API
│   ├── image.py           # 图片处理 API
│   ├── pdf.py             # PDF 处理 API
│   └── text.py            # 文本处理 API
├── core/                   # 核心模块
│   ├── file_handler.py    # 文件处理
│   ├── middleware.py      # 中间件
│   └── task_queue.py      # 任务队列
├── models/                 # 数据模型
│   └── schemas.py
├── services/              # 业务逻辑
│   ├── dev_service.py
│   ├── image_service.py
│   ├── pdf_service.py
│   └── text_service.py
├── static/                # 静态文件
│   ├── css/
│   ├── js/
│   ├── tools/             # 工具页面
│   └── index.html
├── tests/                 # 测试
│   └── property/          # 属性测试
├── temp_files/            # 临时文件目录
├── main.py                # 应用入口
├── requirements.txt       # Python 依赖
└── README.md
```

## 广告集成

在 `static/js/ads.js` 中配置广告代码：

```javascript
// Google AdSense 示例
window.adConfig = {
    enabled: true,
    adClient: 'ca-pub-xxxxxxxxxxxxxxxx',
    slots: {
        header: 'xxxxxxxxxx',
        sidebar: 'xxxxxxxxxx',
        footer: 'xxxxxxxxxx'
    }
};
```

## SEO 优化

- 每个工具页面都有独立的 title 和 meta description
- 自动生成 sitemap.xml
- 语义化 HTML 结构
- 移动端响应式设计

## License

MIT
