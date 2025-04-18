# 我的技术博客

一个基于 Jekyll 的个人技术博客系统，具有现代化的设计和交互体验。

## 项目概述

这是一个使用 Jekyll 构建的静态博客网站，专注于技术内容分享。项目特点包括：
- 清晰的布局设计
- 响应式界面
- 可调整的侧边栏
- 实时搜索功能
- 分类和标签系统

## 技术栈

- **静态站点生成器**: Jekyll 4.x
- **前端技术**:
  - HTML5
  - CSS3 (SCSS)
  - Vanilla JavaScript
- **包管理**: Ruby Bundler
- **部署**: GitHub Pages (可选)

## 项目结构

```
myBlog/
├── _config.yml          # Jekyll 配置文件
├── _layouts/           # 布局模板
│   ├── default.html    # 默认布局模板
│   └── post.html      # 文章页面模板
├── _posts/            # 博客文章目录
├── assets/            # 静态资源
│   ├── css/          # 样式文件
│   └── js/           # JavaScript 文件
├── _site/            # 生成的静态文件（不提交到版本控制）
└── README.md         # 项目说明文档
```

## 核心功能

### 1. 布局系统
- 可调整宽度的左侧导航栏
- 自适应的内容区域
- 响应式设计，支持移动设备

### 2. 导航功能
- 文章搜索（实时过滤）
- 最近更新列表
- 分类目录
- 标签云

### 3. 文章系统
- Markdown 写作支持
- 文章分类和标签
- 代码高亮
- 响应式图片

### 4. 交互设计
- 平滑的动画效果
- 直观的导航体验
- 可拖拽调整布局

## 文件说明

### 核心文件

1. **_layouts/default.html**
   - 网站的主要布局模板
   - 包含页面结构和样式定义
   - 实现了侧边栏和主内容区的布局
   - 包含交互功能的 JavaScript 代码

2. **_config.yml**
   - Jekyll 的配置文件
   - 定义网站的基本信息
   - 设置构建参数

3. **_posts/**
   - 存放所有博客文章
   - 使用 Markdown 格式
   - 文件名格式：YYYY-MM-DD-title.md

## 使用说明

### 环境要求
- Ruby 2.7+
- RubyGems
- Bundler

### 安装步骤

1. 克隆项目：
```bash
git clone [repository-url]
cd myBlog
```

2. 安装依赖：
```bash
bundle install
```

3. 运行开发服务器：
```bash
bundle exec jekyll serve
```

4. 访问本地站点：
```
http://localhost:4000
```

### 写作指南

1. 在 `_posts` 目录下创建新的 Markdown 文件
2. 文件名格式：`YYYY-MM-DD-title.md`
3. 添加文章头信息：
```yaml
---
layout: post
title: "文章标题"
date: YYYY-MM-DD HH:MM:SS +0800
categories: [分类1, 分类2]
tags: [标签1, 标签2]
---
```

## 自定义配置

### 修改样式
- 编辑 `_layouts/default.html` 中的内联样式
- 可以根据需要将样式抽取到单独的 CSS 文件

### 添加新功能
- 在 `_layouts/default.html` 中的 JavaScript 部分添加新的交互功能
- 可以根据需要添加新的布局模板

## 维护说明

- 定期更新 Jekyll 和其他依赖
- 备份博客文章
- 检查并优化网站性能

## 后续优化计划

1. 添加评论系统
2. 实现文章目录导航
3. 优化移动端体验
4. 添加深色模式
5. 优化搜索功能
6. 添加文章阅读时间估算
7. 集成统计分析

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个项目。在提交之前，请确保：
1. 代码符合现有的风格
2. 添加了必要的文档说明
3. 测试了变更的功能

## 许可证

MIT License

## Git 使用指南

### 基础概念

1. **工作区（Working Directory）**
   - 当前目录下的所有文件
   - 直接编辑的地方

2. **暂存区（Staging Area）**
   - 临时存储修改的地方
   - 使用 `git add` 命令将修改添加到暂存区

3. **本地仓库（Local Repository）**
   - 使用 `git commit` 提交的历史记录
   - 包含所有版本信息

4. **远程仓库（Remote Repository）**
   - GitHub 上的仓库
   - 用于多人协作和备份

### 日常博客更新流程

1. **写作前更新本地代码**
```bash
git pull origin main  # 从远程获取最新代码
```

2. **创建新文章**
- 在 `_posts` 目录下创建文章
- 文件名格式：`YYYY-MM-DD-title.md`

3. **提交更改**
```bash
git add .  # 添加所有更改到暂存区
git commit -m "post: 添加新文章《文章标题》"  # 提交更改
git push origin main  # 推送到 GitHub
```

### 常用 Git 命令

```bash
# 查看仓库状态
git status

# 查看修改内容
git diff

# 查看提交历史
git log

# 撤销工作区修改
git checkout -- <file>

# 撤销暂存区修改
git reset HEAD <file>

# 创建新分支
git checkout -b <branch-name>

# 切换分支
git checkout <branch-name>
```

### 关于合并冲突

合并冲突（Merge Conflict）发生在以下情况：
1. 同一个文件的同一部分被不同人（或分支）修改
2. Git 无法自动决定使用哪个版本

解决冲突的步骤：
1. 打开冲突文件，会看到类似下面的标记：
```
<<<<<<< HEAD
当前分支的内容
=======
其他分支的内容
>>>>>>> branch-name
```

2. 手动编辑文件，选择要保留的内容
3. 删除冲突标记
4. 使用 `git add` 标记冲突已解决
5. 使用 `git commit` 完成合并

### 提交规范

为保持提交历史清晰，建议使用以下格式：

- `post: ` 添加或修改文章
- `feat: ` 添加新功能
- `fix: ` 修复问题
- `docs: ` 更新文档
- `style: ` 修改样式
- `refactor: ` 代码重构
- `chore: ` 其他修改

示例：`git commit -m "post: 添加新文章《Git 入门指南》"`
