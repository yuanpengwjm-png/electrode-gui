# 仓库、VS Code 与 Git

实际修改位于 `electrode-gui` Git 仓库。上一版主启动脚本在父目录，会漏出仓库；本次已将完整启动脚本、安装脚本、依赖声明及 VS Code 配置放回仓库。父目录脚本仅转发到仓库内入口。

## 换电脑 / clone 后

1. 打开仓库文件夹，安装带 tkinter 的 Python 3.10+，建议 3.12。
2. 双击 `Setup_Environment.cmd`：创建 `.venv`，联网安装 `requirements_live.txt`。不会把 Python 环境提交到 Git。
3. VS Code 执行 **Python: Select Interpreter**，选择此仓库 `.venv/Scripts/python.exe`。已有工作区可能记住旧选择，`defaultInterpreterPath` 不一定覆盖它。
4. F5 选择 **Electrode QA - Real-time / Post**；或双击仓库内 `Start_Electrode_QA.cmd`。直接实时模式使用 `Start_Live.cmd`。

单纯打开文件夹不等于已经安装依赖；环境只需首次建立。启动代码也会检查缺失的 pylsl 并尝试切换到项目环境，但调试时仍应直接选择正确解释器，避免子进程导致断点不命中。

## 审核后提交本轮 Real-time / Post 源码

本次没有替用户执行 commit 或 push。推荐先在 VS Code Source Control 查看差异，或在仓库终端运行：

```powershell
git status --short
git diff
git add .gitignore .vscode/launch.json .vscode/settings.json
git add Start_Electrode_QA.cmd Start_Live.cmd Setup_Environment.cmd requirements.txt requirements_live.txt
git add runtime_bootstrap.py main.py live_main.py gui.py
git add services/live_analysis.py services/live_discovery.py views/live_window.py views/workspace.py views/heatmap_view.py
git add tests/test_live_workflow.py tests/test_runtime_bootstrap.py tests/live_auto_smoke.py tests/audit_live_deployment.py
git add README.md README_LIVE_CN.md REALTIME_POST_GUIDE.md GIT_SETUP_CN.md DEPLOYMENT_REVIEW_CN.md
git diff --cached --stat
git diff --cached
git commit -m "Add peer live and post workflows with ECG monitoring"
git push
```

以上列出的是本轮核心源码；CT noise 已移到同级 `../noise-analysis` 文件夹，不在此 Git 仓库内，应在该目录另行管理版本，不能把未跟踪文件误认为已经上传。已有暂存内容也要一起检查。

## 打包产物

当前 Git 已跟踪 `dist/` 1426 项、`build-live/` 11 项和旧 ZIP 1 项，共 1438 项。新增 `.gitignore` 只阻止未来未跟踪产物，不能停止跟踪这些旧文件。

建议以后将 EXE/ZIP 放在 GitHub Releases。是否停止跟踪现有产物，等待你审核；本次没有执行 `git rm --cached`，没有删除文件、重写历史或替换旧 EXE。源码变化不会自动更新旧 EXE。

依赖中的 pylsl 固定到 1.18.5；numpy/scipy/matplotlib 目前仍为版本下限，完整版本锁定也列入部署审核。未在一台无依赖的新电脑上执行联网安装验证。
