# SearXNG Windows 安装说明

## 安装完成

SearXNG已成功安装在Windows系统上，使用Python虚拟环境方式。

## 项目结构

```
searxng/
├── venv/              # Python虚拟环境
├── config/            # 配置文件目录
│   └── settings.yml   # SearXNG配置文件
├── searx/             # SearXNG源码
└── ...
```

## 运行SearXNG

### 启动开发服务器

1. 打开PowerShell或CMD
2. 进入项目目录：
   ```powershell
   cd D:\OPEN_WEBUI\Gitlab\searXNG_01\searxng
   ```

3. 激活虚拟环境：
   ```powershell
   # PowerShell
   .\venv\Scripts\Activate.ps1
   
   # CMD
   venv\Scripts\activate.bat
   ```

4. 设置环境变量并启动服务器：
   ```powershell
   # PowerShell
   $env:SEARXNG_SETTINGS_PATH="config\settings.yml"
   python searx\webapp.py
   
   # CMD
   set SEARXNG_SETTINGS_PATH=config\settings.yml
   python searx\webapp.py
   ```

5. 在浏览器中访问：http://127.0.0.1:8888

## 修改源码

源码位于 `searx/` 目录下，可以直接使用任何IDE（如VS Code、PyCharm）进行编辑。

修改后，重启服务器即可看到效果。

## 配置文件

配置文件位于 `config/settings.yml`，可以根据需要进行修改。

主要配置项：
- `general.debug`: 调试模式（开发时建议设为true）
- `server.secret_key`: 服务器密钥（已自动生成）
- `server.limiter`: 限流保护
- `server.image_proxy`: 图片代理

## Windows兼容性修复

已修复以下Windows兼容性问题：
- `searx/valkeydb.py`: 修复了`pwd`模块在Windows上不可用的问题

## 注意事项

1. 首次运行可能需要一些时间来初始化
2. 如果遇到端口占用，可以在配置文件中修改端口
3. 开发模式下，修改Python代码后需要重启服务器
4. 修改前端资源（CSS/JS）可能需要重新构建

## 停止服务器

在运行服务器的终端中按 `Ctrl+C` 停止服务器。

