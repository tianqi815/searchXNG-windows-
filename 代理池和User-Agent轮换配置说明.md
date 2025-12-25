# 代理池和 User-Agent 轮换配置说明

## 概述

本次更新实现了两个主要功能来增强 SearXNG 对抗 Google 等搜索引擎的反爬虫机制：

1. **代理池配置** - 支持轮换使用多个代理IP
2. **User-Agent 轮换** - 支持多种浏览器类型的随机轮换

## 1. User-Agent 轮换功能

### 1.1 更新内容

- **文件**: `searxng/searx/data/useragents.json`
- **新增浏览器类型**: Chrome, Edge, Safari（除了原有的 Firefox）
- **更新版本号**: 使用最新的浏览器版本号

### 1.2 工作原理

`gen_useragent()` 函数现在会：
1. 检查 `useragents.json` 中是否存在 `browsers` 键
2. 如果存在，随机选择一个浏览器类型（Firefox/Chrome/Edge/Safari）
3. 随机选择操作系统和版本号
4. 生成对应的 User-Agent 字符串

### 1.3 使用示例

每次调用 `gen_useragent()` 都会返回不同的 User-Agent，例如：

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.0 Safari/537.36
Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.0 Safari/537.36 Edg/130.0.6723.0
```

## 2. 代理池配置功能

### 2.1 配置位置

在 `searxng/config/settings.yml` 中配置代理池。

### 2.2 全局代理池配置

在 `outgoing` 部分配置全局代理池，所有引擎都会使用：

```yaml
outgoing:
  # 代理池配置 - 轮换使用多个代理IP以避免被限制
  proxies:
    http:
      - http://proxy1.example.com:8080
      - http://proxy2.example.com:8080
      - socks5://proxy3.example.com:1080
    https:
      - http://proxy1.example.com:8080
      - http://proxy2.example.com:8080
      - socks5://proxy3.example.com:1080
```

### 2.3 单个引擎专用代理池

为特定引擎（如 Google）配置专用代理池：

```yaml
engines:
  - name: google
    disabled: false
    proxies:
      http:
        - http://proxy1.example.com:8080
        - http://proxy2.example.com:8080
        - socks5://proxy3.example.com:1080
      https:
        - http://proxy1.example.com:8080
        - http://proxy2.example.com:8080
        - socks5://proxy3.example.com:1080
```

### 2.4 代理协议支持

SearXNG 支持以下代理协议：
- `http://` - HTTP 代理
- `https://` - HTTPS 代理
- `socks5://` - SOCKS5 代理
- `socks5h://` - SOCKS5 代理（DNS 解析在代理端）

### 2.5 轮换机制

当配置了多个代理时，SearXNG 会自动使用 **round-robin（轮询）** 方式：
- 每次请求使用不同的代理
- 自动在代理列表中轮换
- 如果某个代理失败，会自动尝试下一个

## 3. Google 引擎增强

### 3.1 增强的反爬虫检测

更新了 `detect_google_sorry()` 函数，现在可以检测：
- ✅ Google Sorry 页面重定向
- ✅ 异常流量提示（"unusual traffic"）
- ✅ reCAPTCHA 挑战
- ✅ 403 Forbidden 状态码
- ✅ 空结果页面（可能被阻止）

### 3.2 增强的 HTTP 头

在 `request()` 函数中添加了更真实的浏览器 HTTP 头：
- `Accept`: 完整的 MIME 类型列表
- `Accept-Encoding`: 支持 gzip, deflate, br, zstd
- `Sec-Fetch-*`: 更真实的浏览器安全头
- `Referer`: 设置 Google 首页作为来源

## 4. 使用建议

### 4.1 代理池配置建议

1. **使用高质量代理**: 选择稳定、低延迟的代理服务
2. **代理数量**: 建议配置 3-5 个代理，确保有足够的轮换
3. **代理类型**: 优先使用住宅代理（residential proxy）而非数据中心代理
4. **测试代理**: 配置前先测试代理的可用性和速度

### 4.2 User-Agent 使用

- User-Agent 会自动轮换，无需手动配置
- 每次请求都会使用不同的 User-Agent
- 支持 Firefox、Chrome、Edge、Safari 四种主流浏览器

### 4.3 监控和调试

- 查看日志文件了解代理使用情况
- 如果遇到 CAPTCHA，检查日志中的错误信息
- 使用 `debug: true` 模式获取更详细的日志

## 5. 故障排除

### 5.1 代理连接失败

如果代理连接失败：
1. 检查代理地址和端口是否正确
2. 确认代理服务是否正常运行
3. 检查防火墙设置
4. 尝试使用不同的代理协议（http/socks5）

### 5.2 仍然遇到 CAPTCHA

如果配置了代理池和 User-Agent 轮换后仍然遇到 CAPTCHA：
1. 增加代理数量
2. 降低请求频率（在代码中添加延迟）
3. 使用更高质量的代理（住宅代理）
4. 检查 IP 是否被 Google 封禁

### 5.3 查看日志

启用调试模式查看详细日志：

```yaml
general:
  debug: true
```

日志会显示：
- 使用的代理 IP
- User-Agent 信息
- 请求和响应详情
- 错误信息

## 6. 注意事项

⚠️ **重要提示**:
- 代理池配置需要有效的代理服务
- 免费代理通常不稳定，建议使用付费代理服务
- 遵守目标网站的使用条款和 robots.txt
- 不要过度频繁地请求，避免被封禁

## 7. 相关文件

- `searxng/searx/data/useragents.json` - User-Agent 配置
- `searxng/searx/utils.py` - `gen_useragent()` 函数
- `searxng/searx/engines/google.py` - Google 引擎实现
- `searxng/config/settings.yml` - 配置文件

