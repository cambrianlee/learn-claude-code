# Git 工作流指南

本文档说明如何使用当前仓库的 Git 配置，同时从开源仓库学习并维护自己的修改。

---

## 📊 当前配置状态

### **远程仓库**
```bash
origin  → https://github.com/shareAI-lab/learn-claude-code.git  (原始开源仓库)
myfork  → git@github.com:cambrianlee/learn-claude-code.git      (你的 fork)
```

### **本地分支跟踪**
```bash
main 分支 → 跟踪 myfork/main
```

### **可视化结构**
```
你的本地仓库
    │
    ├── origin (远程) ──→ shareAI-lab/learn-claude-code (开源原始仓库)
    │                    ↑
    │                    │ 只读，可以拉取最新代码
    │
    └── myfork (远程) ──→ cambrianlee/learn-claude-code (你的 fork)
                         ↑
                         │ 可读写，推送你的修改
```

---

## 🎯 常用操作

### **1. 推送你的修改**
```bash
# 添加修改的文件
git add .

# 提交
git commit -m "描述你的修改"

# 推送到你的 fork
git push myfork main
```

### **2. 拉取原始开源仓库的最新代码**
```bash
# 从原始开源仓库拉取更新
git pull origin main
```

### **3. 同步上游更新到你的 fork**
```bash
# 1. 先从原始仓库拉取最新代码
git fetch origin

# 2. 合并到本地
git merge origin/main

# 3. 推送到你的 fork
git push myfork main
```

---

## 🔄 典型工作流程

### **场景 1：只从开源仓库学习**
```bash
# 定期同步上游更新
git pull origin main
```

### **场景 2：学习 + 修改自己的代码**
```bash
# 1. 获取上游最新代码
git fetch origin

# 2. 查看有什么不同
git log origin/main --oneline -10

# 3. 如果想合并上游代码
git merge origin/main

# 4. 推送你的修改到 fork
git push myfork main
```

### **场景 3：在不同机器间同步（家 ↔ 公司）**

**在家（修改代码后）：**
```bash
git add .
git commit -m "添加新功能"
git push myfork main
```

**在公司（获取最新代码）：**
```bash
# 方法 1：如果已经有这个仓库
git pull myfork main

# 方法 2：如果是第一次
git clone git@github.com:cambrianlee/learn-claude-code.git
cd learn-claude-code
```

---

## 🔧 实用命令

### **查看远程仓库配置**
```bash
git remote -v
```

### **查看分支跟踪关系**
```bash
git branch -vv
```

### **查看当前状态**
```bash
git status
```

### **查看提交历史**
```bash
# 简洁显示
git log --oneline -10

# 图形化显示
git log --graph --oneline --all
```

### **比较不同**
```bash
# 查看本地和 origin 的差异
git diff origin/main

# 查看本地和 myfork 的差异
git diff myfork/main
```

---

## ⚠️ 注意事项

### **1. 不要推送到 origin**
```bash
# ❌ 错误：会失败（没有权限）
git push origin main

# ✅ 正确：推送到自己的 fork
git push myfork main
```

### **2. 合并冲突时**
```bash
# 如果 git pull origin main 时出现冲突
git status  # 查看冲突文件

# 手动解决冲突后
git add <解决冲突的文件>
git commit -m "合并上游更新并解决冲突"
git push myfork main
```

### **3. 保持 fork 同步的最佳实践**
```bash
# 定期执行（每周或每月）
git fetch origin
git merge origin/main
git push myfork main
```

---

## 📝 命令速查表

| 操作 | 命令 | 目标 |
|------|------|------|
| **拉取开源仓库更新** | `git pull origin main` | shareAI-lab 的仓库 |
| **推送你的修改** | `git push myfork main` | cambrianlee 的仓库 |
| **查看远程仓库** | `git remote -v` | 查看配置 |
| **查看状态** | `git status` | 查看当前状态 |
| **查看日志** | `git log --oneline -10` | 查看最近提交 |
| **同步两者** | 先 `pull origin`，再 `push myfork` | 保持同步 |

---

## 🎓 核心概念

### **origin vs myfork**

- **origin**: 原始开源仓库（只读）
  - 用于获取最新的开源代码
  - 你没有写入权限

- **myfork**: 你自己的 fork（读写）
  - 用于保存你的修改
  - 你有完全的控制权

### **为什么需要两个远程仓库？**

1. **origin**: 保持与开源项目同步，获取最新更新
2. **myfork**: 保存你的学习笔记、示例代码等

这样你既能学习开源项目的最新进展，又能维护自己的修改。

---

## 🚀 快速开始

### **第一次在新机器上**
```bash
# 1. 克隆你的 fork
git clone git@github.com:cambrianlee/learn-claude-code.git
cd learn-claude-code

# 2. 确保远程配置正确
git remote -v

# 3. 配置 .env
cp .env.example .env
# 编辑 .env 文件，添加你的 API Key

# 4. 开始工作！
```

### **每次开始工作前**
```bash
# 1. 拉取最新代码（如果有多台机器）
git pull myfork main

# 2. （可选）同步上游开源仓库更新
git fetch origin
git merge origin/main
```

### **每次结束工作后**
```bash
# 1. 提交修改
git add .
git commit -m "描述你的修改"

# 2. 推送到 fork
git push myfork main
```

---

## 💡 最佳实践

1. **定期同步上游**: 每周或每月从 origin 拉取更新
2. **清晰的提交信息**: 使用有意义的中英文描述
3. **及时推送**: 完成功能后立即推送，避免丢失代码
4. **分支管理**: 如果要实验性修改，可以创建新分支
   ```bash
   git checkout -b feature-branch
   # 修改代码
   git push myfork feature-branch
   ```

---

## 📚 延伸阅读

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub Fork 工作流](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks)
- [Pro Git 中文版](https://git-scm.com/book/zh/v2)

---

**创建时间**: 2026-03-01
**最后更新**: 2026-03-01
