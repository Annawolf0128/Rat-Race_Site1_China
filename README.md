# Reversed Beauty Contest：中国站实验员说明

面向已熟悉 oTree 的实验员。本项目使用中文界面，每场 **15 人、20 轮**，一个 Session 只运行一个 treatment。

## 从下载 ZIP 到打开 admin

**首次使用要完成：下载解压 → 检查 Python → 创建虚拟环境 → 安装依赖 → 启动 → 打开后台。**
不能跳过环境创建和依赖安装。选择下面与你电脑对应的一套步骤，每次只运行一条命令，成功后再继续。
代码框中的内容才是命令，不要复制终端提示符（例如 `%`、`$`、`PS C:\...>`）。

本项目固定使用 oTree 5.11.5，本地验证的 Python 为 3.9。以下首次安装过程需要网络。

### 1. 下载和解压（两种系统相同）

1. 打开 [中国站 GitHub 仓库](https://github.com/Annawolf0128/Rat-Race_Site1_China)，选择 **main** 分支。
2. 点击绿色 **Code → Download ZIP**，下载 `Rat-Race_Site1_China-main.zip`。
3. **Mac**：双击 ZIP 解压。**Windows**：右键 ZIP → **全部解压**；不要直接在 ZIP 内运行。
4. 将解压后的 `Rat-Race_Site1_China-main` 文件夹放到桌面。
5. 打开文件夹，确认这一层直接包含 `settings.py`、`requirements.txt`、`README.md` 和 `scripts` 文件夹。
   如果还套着一层同名文件夹，要使用里面这一层作为项目目录。

### 2A. Mac：准备环境并启动

**① 打开终端。** 按 Command + 空格，搜索“终端”或 Terminal，打开它。

**② 进入解压后的项目目录。** 如果文件夹按上一步放在桌面且名称未改，运行：

```bash
cd "$HOME/Desktop/Rat-Race_Site1_China-main"
```

如果保存位置或文件夹名不同：在终端输入 `cd `（末尾有空格），把 Finder 中的项目文件夹拖入终端，再按回车。
`cd` 的作用是进入指定文件夹。

确认目录内容：

```bash
ls
```

`ls` 只列出当前文件夹内容，不修改文件。应能看到 `settings.py`、`requirements.txt`、`rbc`、`scripts`。
如果没有，先回到正确目录再继续。

**③ 检查 Python。** 运行：

```bash
python3 --version
```

如果显示 **Python 3.9.x**（例如 `Python 3.9.6`），直接继续第④步。

如果找不到命令，或者显示其他版本：先试 `python3.9 --version`。若它显示 3.9.x，第④步改用 `python3.9`。
如果没有 Python 3.9，从 [Python 3.9.13 官方版本页](https://www.python.org/downloads/release/python-3913/) 的 Files
下载 **macOS 64-bit universal2 installer**，打开安装包并完成安装。重新打开终端、重新进入项目目录，
运行 `python3.9 --version` 确认成功，然后第④步使用 `python3.9`。

**④ 创建项目虚拟环境。** 第③步 `python3` 为 3.9.x 时运行：

```bash
python3 -m venv .venv
```

如果第③步使用的是 `python3.9`，则改为运行下面这一条；两条创建命令选一条即可：

```bash
python3.9 -m venv .venv
```

命令没有输出、重新出现终端提示符通常表示已完成。它会在项目中创建 `.venv` 文件夹。

**⑤ 安装依赖。** 运行并等待结束：

```bash
.venv/bin/python -m pip install -r requirements.txt
```

第一次通常会看到 `Successfully installed ...`，重复安装可能显示 `Requirement already satisfied`。
如果出现 `ERROR`，先处理错误，不继续启动。

**⑥ 启动实验服务。** 运行：

```bash
.venv/bin/python scripts/start_study.py --port 8000
```

正常启动会显示 `Running prodserver` 以及服务启动日志。此时终端保持运行、不返回输入提示符是正常的。
**保持这个终端窗口打开**，继续第 3 节打开网页。

### 2B. Windows：准备环境并启动

以下针对 Windows 10/11 的 Intel/AMD 64 位电脑。Windows ARM 需要单独确认运行环境。

**① 打开 PowerShell。** 在开始菜单搜索 PowerShell 并打开。不要在 Python 的 `>>>` 窗口输入下列命令。

**② 进入解压后的项目目录。** 如果文件夹在普通桌面目录，运行：

```powershell
cd "$HOME\Desktop\Rat-Race_Site1_China-main"
```

如果桌面由 OneDrive 管理或保存位置不同：在文件资源管理器打开项目文件夹，按 **Ctrl+L** 复制完整路径；
在 PowerShell 输入 `cd "复制的实际路径"`，再回车。引号内替换为实际路径，不是照抄中文。

确认目录内容：

```powershell
dir
```

应能看到 `settings.py`、`requirements.txt`、`rbc` 和 `scripts`。如果没有，先进入正确目录。

**③ 检查 Python。** 运行：

```powershell
py -3.9 --version
```

显示 **Python 3.9.x** 后继续。如果提示找不到 `py` 或没有 Python 3.9，从
[Python 3.9.13 官方版本页](https://www.python.org/downloads/release/python-3913/) 的 Files 下载 **Windows installer (64-bit)**。
安装时勾选 **Add Python 3.9 to PATH**，保留 pip 和 Python Launcher，完成安装。
随后新开 PowerShell、重新进入项目目录，再运行上面的版本检查。

**④ 创建项目虚拟环境。** 运行：

```powershell
py -3.9 -m venv .venv
```

**⑤ 安装依赖。** 等第④步成功，再运行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

看到安装成功或 `Requirement already satisfied` 后继续；出现 `ERROR` 时先处理错误。

**⑥ 启动实验服务。** 运行：

```powershell
.\.venv\Scripts\python.exe scripts\start_study.py --port 8000
```

正常启动会显示 `Running prodserver` 以及服务启动日志。**保持窗口打开**，继续下面第 3 节。
以上命令直接调用虚拟环境里的 Python，不需要运行激活脚本，也不需要修改 PowerShell 执行策略。

### 3. 在实验员电脑打开 admin

在浏览器地址栏输入：

**http://localhost:8000/sessions**

看到 **Sessions** 页面，以及 **Rooms、Data** 等菜单，即已成功进入 admin。**无需设置或输入密码、密钥。**

如果页面打不开，先看启动服务的终端是否报错。不要关闭终端后再尝试打开网页。

### 4. 以后再次启动和停止

首次安装成功后，下次只需打开终端、进入**同一个项目目录**，再运行对应系统的启动命令：

Mac：

```bash
.venv/bin/python scripts/start_study.py --port 8000
```

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe scripts\start_study.py --port 8000
```

然后打开 **http://localhost:8000/sessions**。不需要每次重建 `.venv` 或重新安装依赖。
实验结束并完成数据保存后，在服务终端按 **Ctrl+C** 停止服务。关闭浏览器不等于停止服务器。

### 5. 常见启动错误

| 报错或现象 | 处理 |
|---|---|
| `command not found: python` | 不使用单独的 `python` 命令。按上面步骤先创建 `.venv`，再使用完整的虚拟环境 Python 路径 |
| `python3` / `py` 找不到，或没有 3.9 | 按对应系统第③步安装 Python，并新开终端检查 |
| 找不到 `requirements.txt` / `scripts/start_study.py` | 当前目录不对，重新进入直接包含这些文件的项目目录 |
| 找不到 `.venv/bin/python` 或 `.venv\Scripts\python.exe` | 第④步环境创建没有完成，或当前目录不对；不要复制其他电脑的 `.venv` |
| 安装依赖出现网络、证书或下载错误 | 安装尚未成功，保留完整错误并处理网络/环境问题后重试，不继续启动 |
| `Address already in use` / 端口被占用 | 已有服务使用 8000；确认后停止旧服务，或把启动命令改为 `--port 8023`，同时浏览器改开 `http://localhost:8023/sessions` |

Python 3.9 已结束官方支持，此处版本用于复现现有实验环境；Windows 步骤仍需在现场机器验证。
程序使用默认 SQLite，数据保存在项目目录的 `db.sqlite3`，无需另外安装数据库。
启动方式不设后台登录保护，只用于受控实验室网络。

**被试电脑不能使用 `localhost`**：它们应使用实验员电脑的局域网 IP 和各自座位链接，见“开场与页面流程”。
实验参数在 `params.py`，场次配置在 `settings.py`；进行中的场次不要修改参数。

## Treatment 与规则

| Treatment / Session config | 分组 | 罚金 L | 每轮预测中位数 | 计划场数 |
|---|---|---|---|---|
| T1 `rbc_site1_small_low` | 3 × 5 人 | 20 | 无 | 1 |
| T2 `rbc_site1_small_high` | 3 × 5 人 | 40 | 无 | 1 |
| T3 `rbc_site1_large_low` | 1 × 15 人 | 20 | 无 | 3 |
| T4 `rbc_site1_large_high` | 1 × 15 人 | 40 | 无 | 3 |
| T5 `rbc_site1_small_low_belief` | 3 × 5 人 | 20 | 有 | 1 |
| T6 `rbc_site1_large_low_belief` | 1 × 15 人 | 20 | 有 | 1 |

共 10 场、150 人。每场人数必须为 15，轮数保持默认 20。

- 第 1 轮前按到达分组等待页的顺序组成小组，**组员固定至第 20 轮**。座位标签不预先决定分组。
- 每轮选择整数 `x ∈ [0,100]`，成本 `x²/200`。以包含自己的全组选择计算中位数。
- 本轮收益 `100 − x²/200 − 罚金`；**严格低于中位数罚 L，等于或高于不罚**。
- T5、T6 每轮先填写中位数预测（0–100 整数），没有额外预测奖金。

## 开场与页面流程

1. 使用 Room **`china_lab`**。15 台电脑分别使用座位标签 **01–15**，入口：
   `http://<服务器IP>:8000/room/china_lab?participant_label=01`（各电脑替换为自己的座位号）。
2. Room 中确认 15 个不同座位到齐，选择对应 treatment，创建 **15 人** Session，记录场次号。
3. 在该场 **Monitor** 确认所有人到 **Welcome**，点击 **「开始实验（仅欢迎页）」** 统一放行。

后续流程：实验说明 → 理解题（5 题全对）→ 20 轮〔预测（仅 T5/T6）→ 选择 → 同组等待 → 结果〕→ 问卷 → 付款。
当前六种配置不显示程序内 Consent 页，知情同意按实验室既定流程处理。

- 选择页必须先点击或拖动滑块才显示提交按钮，点击初始 50 也算选择。
- 同组全部提交后自动结算、显示结果；小组处理的三个组独立推进，admin 不需要逐轮放行。
- 禁止使用强制推进代替被试回答；问卷完成后个人即可进入 Payment，无需等待其他人问卷。
- 掉线后用原座位入口重进，保留原 Session；没有自动补位或缺失答案代填。永久退出的处理由研究负责人决定。
- 换场前完成付款和导出，再在 Room 点击 **Close this room**，让电脑重新打开座位入口候场，创建下一场。关闭 Room 不删除旧 Session。

## 报酬设定

**总报酬 = ¥15 出场费 + 抽中轮收益 × ¥0.50/点。** 建场时全场统一随机抽取一个支付轮，结束时显示；20 轮不累加支付。
参与者完成问卷后，后台 **Payments** 显示最终金额：**Payoff (bonus)** 为折算后的奖金，**Total** 为含出场费的人民币总额。
数据使用 oTree 标准 **Data** 导出（CSV，可用 Excel 打开）；每轮收益字段为 `round_payoff`，标准 `payoff` 用于抽中轮付款记账。

**已知运行问题：**等待场景曾出现 `database is locked` / HTTP 500 / 超时，尚未定位修复。
正式实验前需在实际服务器和 15 台电脑完成全流程、同时提交及断线恢复演练；异常时保留日志和数据，不强制推进。
