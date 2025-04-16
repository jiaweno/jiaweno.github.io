# 开发指南

本文档详细说明了如何进行博客系统的开发和定制。

## 开发环境设置

### 必要软件
1. Ruby
2. RubyGems
3. Bundler
4. Git
5. 文本编辑器（推荐 VS Code）

### 本地开发流程

1. **克隆项目后首次运行**：
```bash
bundle install
bundle exec jekyll serve
```

2. **日常开发流程**：
```bash
bundle exec jekyll serve --livereload
```

## 项目结构详解

### 目录结构
```
myBlog/
├── _config.yml          # 配置文件
├── _layouts/           # 布局模板
├── _posts/            # 文章
├── _site/            # 生成的静态文件
├── assets/           # 静态资源
├── docs/            # 文档
└── README.md        # 项目说明
```

### 关键文件说明

#### 1. _config.yml
```yaml
# 网站设置
title: 我的技术博客
description: 一个记录技术探索和学习心得的个人空间
baseurl: ""
url: ""

# 构建设置
markdown: kramdown
theme: minima
plugins:
  - jekyll-feed
```

#### 2. _layouts/default.html
- 定义了网站的基本HTML结构
- 包含了响应式设计
- 实现了可调整宽度的侧边栏
- 集成了搜索功能

## 开发指南

### 添加新功能

1. **添加新的布局模板**
```
_layouts/
└── new-layout.html
```

2. **创建新的包含文件**
```
_includes/
└── new-component.html
```

3. **添加新的样式**
```css
/* 在 default.html 中添加 */
<style>
  .new-component {
    /* 样式定义 */
  }
</style>
```

### 自定义主题

1. **修改颜色方案**
```css
:root {
  --primary-color: #1e88e5;
  --text-color: #333;
  --background-color: #f5f5f5;
}
```

2. **调整布局**
```css
.sidebar {
  width: 300px;  /* 默认宽度 */
  min-width: 200px;
  max-width: 600px;
}
```

### JavaScript 功能开发

1. **添加新的交互功能**
```javascript
document.addEventListener('DOMContentLoaded', function() {
  // 新功能代码
});
```

2. **优化现有功能**
```javascript
// 搜索功能优化示例
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
```

## 最佳实践

### 代码规范

1. **HTML**
- 使用语义化标签
- 保持结构清晰
- 添加适当的注释

2. **CSS**
- 使用 BEM 命名规范
- 避免过度嵌套
- 注意性能优化

3. **JavaScript**
- 使用现代 ES6+ 语法
- 避免全局变量
- 做好错误处理

### 性能优化

1. **图片优化**
- 使用适当的图片格式
- 实现懒加载
- 提供响应式图片

2. **代码优化**
- 压缩 CSS 和 JavaScript
- 减少 DOM 操作
- 使用事件委托

### 安全考虑

1. **XSS 防护**
- 过滤用户输入
- 使用 CSP
- 转义输出

2. **其他安全措施**
- 使用 HTTPS
- 更新依赖
- 定期安全审查

## 故障排除

### 常见问题

1. **Jekyll 构建错误**
```bash
bundle exec jekyll doctor
```

2. **样式问题**
- 检查 CSS 优先级
- 验证媒体查询
- 测试不同浏览器

3. **JavaScript 错误**
- 使用浏览器开发工具调试
- 检查控制台错误
- 添加日志输出

## 部署指南

### GitHub Pages

1. **配置**
```yaml
# _config.yml
baseurl: "/blog-name"
url: "https://username.github.io"
```

2. **部署**
```bash
git push origin main
```

### 自定义服务器

1. **构建**
```bash
JEKYLL_ENV=production bundle exec jekyll build
```

2. **部署**
- 将 `_site` 目录部署到服务器
- 配置 Web 服务器
- 设置 SSL 证书 