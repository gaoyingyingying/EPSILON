# Git 管理命令顺序指南（epsilon-reproduction）

本指南按“先后顺序”给出常用命令，可直接在项目根目录执行：

```bash
cd ~/epsilon-reproduction
```

## 1. 首次接管项目（本地已有文件，准备纳入 Git）

```bash
# 初始化（若已初始化可跳过）
git init

# 查看当前状态
git status
git branch -vv
git remote -v
```

## 2. 首次提交（本项目要包含 results）

```bash
# 添加需要跟踪的内容（包含 results）
git add src/ results/ .gitignore

# 首次提交
git commit -m "chore: initial import with experiment results"
```

## 3. 绑定远程并首次推送

```bash
# 仅第一次需要（URL 换成你的仓库地址）
git remote add origin <REMOTE_URL>

# 统一主分支名称
git branch -M main

# 推送并建立跟踪关系
git push -u origin main
```

## 4. 日常开发标准流程（推荐每次都按此顺序）

```bash
# 1) 回到主分支并更新
git checkout main
git pull --rebase

# 2) 新建功能分支
git checkout -b feat/<short-topic>

# 3) 开发后查看改动
git status
git diff

# 4) 分块暂存并提交（避免一次性大提交）
git add -p
git commit -m "feat: <what changed>"

# 5) 推送功能分支
git push -u origin feat/<short-topic>
```

## 5. 合并前同步主分支（减少冲突）

```bash
git fetch origin
git rebase origin/main
```

若出现冲突：

```bash
# 编辑冲突文件后
git add <resolved-files>
git rebase --continue
```

## 6. 常用“安全恢复”命令（不删历史）

```bash
# 临时收起当前改动（含未跟踪文件）
git stash -u

# 恢复最近一次 stash
git stash pop

# 丢弃某个文件的未提交改动
git restore <file>

# 查看近期提交图
git log --oneline --graph --decorate -20
```

## 7. 子模块误操作修复（src/EPSILON 点不开时）

当你看到 `mode 160000`，说明目录被当成子模块记录了。按下面修复为普通目录：

```bash
# 从索引里移除子模块记录（不删工作区文件）
git rm --cached src/EPSILON

# 如果存在嵌套 git 元数据，再执行这一句
rm -rf src/EPSILON/.git

# 重新按普通目录纳入版本管理
git add src/EPSILON
git commit -m "fix: track EPSILON as regular directory instead of submodule"
git push origin main
```

## 8. 提交前检查清单（建议每次 20 秒过一遍）

```bash
git status
git diff --stat
git log --oneline -5
```

确认点：
- 当前分支是否正确（`main` / `feat/*`）。
- 是否误提交临时文件、大日志或构建产物。
- 提交信息是否能表达“做了什么 + 为什么”。

