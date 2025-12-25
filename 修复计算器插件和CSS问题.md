# 修复计算器插件和CSS加载问题

## 问题1: 计算器插件错误

**错误信息**: `SyntaxError: Syntax error in part "中山天气" (char 1)`

**原因**: 计算器插件在解析非数学表达式（如中文查询）时，`parse()` 方法会抛出异常，但异常处理不完整。

**修复**: 已修复 `client/simple/src/js/plugin/Calculator.ts`，将 `parse()` 调用也包含在 try-catch 中。

**需要操作**: 重新构建前端资源（见下方）

## 问题2: CSS文件未加载

从界面显示来看，CSS文件仍然没有正确加载。可能的原因：

1. 服务器未重启，修复未生效
2. 浏览器缓存问题
3. 静态文件路径配置问题

## 解决步骤

### 步骤1: 重新构建前端资源（修复计算器插件）

由于修改了TypeScript文件，需要重新构建：

```powershell
# 进入前端目录
cd D:\OPEN_WEBUI\Gitlab\searXNG_01\searxng\client\simple

# 安装依赖（如果还没有安装）
npm install

# 构建前端资源
npm run build
```

构建完成后，CSS和JS文件会更新到 `searx/static/themes/simple/` 目录。

### 步骤2: 重启服务器

1. 停止当前服务器（按 `Ctrl + C`）
2. 重新运行启动脚本

### 步骤3: 清除浏览器缓存

1. 按 `Ctrl + Shift + Delete`
2. 选择"缓存的图片和文件"
3. 点击"清除数据"
4. 强制刷新页面（`Ctrl + F5`）

### 步骤4: 验证修复

1. **检查CSS加载**: 
   - 打开开发者工具（F12）
   - 查看Network标签
   - 刷新页面
   - 确认 `sxng-ltr.min.css` 返回200状态码

2. **测试计算器插件**:
   - 搜索数学表达式（如 `2+2`）应该显示计算结果
   - 搜索中文查询（如 `中山天气`）不应该报错

3. **测试搜索功能**:
   - 输入关键词进行搜索
   - 确认能正常显示结果

## 如果CSS仍然无法加载

如果重新构建和重启后CSS仍然无法加载，请检查：

1. **直接访问CSS文件URL**:
   - 在浏览器中访问: http://127.0.0.1:8888/static/themes/simple/sxng-ltr.min.css
   - 如果返回404，说明路径配置有问题
   - 如果返回200，说明是浏览器缓存问题

2. **检查文件是否存在**:
   ```powershell
   Test-Path D:\OPEN_WEBUI\Gitlab\searXNG_01\searxng\searx\static\themes\simple\sxng-ltr.min.css
   ```

3. **查看服务器日志**:
   - 查看终端输出，看是否有关于静态文件的错误信息

