# CSS加载问题排查

## 问题现象
界面显示不正常，可能是CSS文件没有正确加载。

## 排查步骤

### 1. 检查浏览器控制台
1. 打开浏览器开发者工具（F12）
2. 查看Console标签页，看是否有404错误
3. 查看Network标签页，检查CSS文件是否成功加载

### 2. 直接访问CSS文件
在浏览器中访问以下URL，看是否能正常加载CSS：
- http://127.0.0.1:8888/static/themes/simple/sxng-ltr.min.css

如果显示404错误，说明静态文件路径有问题。

### 3. 清除浏览器缓存
1. 按 `Ctrl + Shift + Delete` 打开清除浏览数据
2. 选择"缓存的图片和文件"
3. 点击"清除数据"
4. 刷新页面（按 `Ctrl + F5` 强制刷新）

### 4. 检查静态文件
确认以下文件存在：
- `searx/static/themes/simple/sxng-ltr.min.css`
- `searx/static/themes/simple/sxng-core.min.js`

### 5. 如果CSS文件不存在或需要重新构建
如果CSS文件不存在，需要构建前端资源：

```powershell
# 进入前端目录
cd client\simple

# 安装依赖
npm install

# 构建前端资源
npm run build
```

构建完成后，CSS和JS文件会生成到 `searx/static/themes/simple/` 目录。

