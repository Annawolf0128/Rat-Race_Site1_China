# Rat Race（反向选美）实验 — 中国站

本仓库是"Rat Race / Reversed Beauty Contest"实验的中国站独立部署包，基于 oTree 5，
界面全中文，报酬按人民币结算。本文档面向实验室的实验员：说明实验内容、如何配置服务器、
以及每一场实验的标准操作流程。

---

## 一、先看这里：实验员电脑安装与启动（Windows / Mac）

**当前按实验安排恢复 oTree 默认 SQLite。实验员电脑安装 Python 和项目依赖即可，不需要安装 PostgreSQL、配置数据库账号或启动数据库服务。15 台被试电脑只需要浏览器。**

数据自动保存到项目目录的 `db.sqlite3`。启动脚本忽略外部 `DATABASE_URL`，使用这个默认数据库，同时保留后台登录保护。
以前 PostgreSQL 中的场次不会自动搬入 SQLite；切换后看不到旧场次不代表旧数据被删除。

安装前拿到修复后的完整项目，不只复制某个 `.py` 文件，不复制其他电脑的 `.venv`。
从 GitHub 使用 Code → Download ZIP 下载后，先完整解压，将含 `settings.py` 的项目文件夹命名为 `otree_china`。
Windows 放到 `C:\otree_china`，Mac 放到个人主目录 `~/otree_china`，即可直接使用下文示例命令；不要在压缩包内部运行。
正式运行和演练分别用两个项目目录，各自创建虚拟环境和数据库，
例如 `otree_china` 与 `otree_china_test`；正式目录从不含测试 `db.sqlite3` 的代码包开始，不用 resetdb 清理已有数据。

### 1. Windows 首次安装

以下以 Windows 10/11 Intel/AMD 64 位电脑、项目位于 `C:\otree_china` 为例。Windows ARM 需另行确认兼容性。

1. 从 [Python 3.9.13 官方版本页](https://www.python.org/downloads/release/python-3913/) 的 Files 下载 **Windows installer (64-bit)**。
   安装 pip、Python Launcher，勾选 Add Python to PATH。
2. 新开 PowerShell，执行下面命令；每条成功后再继续。无需修改 PowerShell 执行策略。

```powershell
cd C:\otree_china
py -3.9 --version
py -3.9 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

依赖固定为 oTree 5.11.5。保存最后一条生成的密钥，正常重启不更换。
用记事本在项目目录外创建 `C:\start-china.cmd`，保存类型为“所有文件”，确认不是 `.cmd.txt`。
填写自己的 admin 密码及刚生成的密钥；密码使用足够长的随机字母数字，避免命令行特殊字符。

```bat
@echo off
cd /d C:\otree_china || exit /b 1
set "DATABASE_URL="
set "OTREE_ADMIN_PASSWORD=REPLACE_ADMIN_PASSWORD"
set "OTREE_SECRET_KEY=REPLACE_GENERATED_SECRET"
.venv\Scripts\python.exe scripts\start_study.py --port 8000
pause
```

双击启动文件，保持窗口打开；出现报错时先处理，不同时开多个服务窗口。
启动文件含密码，不上传 GitHub 或发给被试。

### 2. Mac 首次安装

以项目位于 `~/otree_china` 为例。从 [Python 3.9.13 官方版本页](https://www.python.org/downloads/release/python-3913/)
下载 **macOS 64-bit universal2 installer**，安装后新开终端：

```bash
cd ~/otree_china
python3.9 --version
python3.9 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python -c 'import secrets; print(secrets.token_hex(32))'
```

保存生成的密钥。使用纯文本编辑器创建 `~/start-china.command`（文本编辑 App 要先选“制作纯文本”）：

```bash
#!/bin/zsh
cd "$HOME/otree_china" || exit 1
unset DATABASE_URL
export OTREE_ADMIN_PASSWORD='REPLACE_ADMIN_PASSWORD'
export OTREE_SECRET_KEY='REPLACE_GENERATED_SECRET'
.venv/bin/python scripts/start_study.py --port 8000
```

填写自己的密码和固定密钥后执行：

```bash
chmod 700 ~/start-china.command
~/start-china.command
```

以后可从终端运行或双击 `.command` 文件，保持窗口打开。文件含密码，不上传 GitHub。
无需安装 Homebrew 或 PostgreSQL。

**版本与验收范围：**现有程序使用 Python 3.9 / oTree 5.11.5；Python 3.9 已结束官方支持，旧安装器仅用于复现项目环境，
不是长期公网部署建议。升级运行环境需单独验收。Windows 安装步骤未在实际 Windows 电脑执行验证。

### 3. 连接 15 台被试电脑

1. 实验员电脑启动服务后打开 **http://127.0.0.1:8000/sessions**，用户名 `admin`，使用启动文件中设置的密码。
   初次启动会创建数据库表，不需要 `otree resetdb`。
2. 查实验员电脑的局域网 IPv4：Windows 用 `ipconfig` 看当前网卡；Mac 在系统设置的网络连接详情中查看。
3. 被试电脑使用实际 IP，例如 `http://192.168.1.20:8000/room/china_lab?participant_label=01`。
   示例 IP 必须替换，座位分别为 **01–15**。被试电脑不能用 `127.0.0.1` 连接实验员电脑。
4. 本机能开、其他电脑不能开时，让 IT 允许实验室网络访问 **TCP 8000**；不关闭整个防火墙，不需要开放数据库端口。
5. 先在独立演练目录完成完整流程、多人同时提交、迟交、断线恢复和导出检查，再启动正式目录的服务。
   两个目录不要同时占用同一端口，切换前停止前一个服务。

### 4. 每天启动、停止与备份

- [ ] 运行对应启动文件，保持电脑供电、不休眠；浏览器进入 admin，按第六节操作 Room 和 Session。
- [ ] 每场导出 CSV 和 Page times，核对付款。换场只操作 Room，不删除数据库、不改密钥、不重新安装。
- [ ] 当天全部完成、导出后，在服务窗口按 **Ctrl+C**，等启动脚本和后台 worker 完全退出。
- [ ] 停服后复制项目目录的 `db.sqlite3` 到带日期的备份目录，并备份到另一存储位置。
  如存在 `db.sqlite3-wal`、`db.sqlite3-shm` 或 `db.sqlite3-journal`，也保留这些同名前缀文件；异常关机后不要自行删它们。
- [ ] 不在服务仍运行时仅复制主数据库文件来当作完整备份。恢复演练使用另一份项目目录，不覆盖正式库。

**当前测试边界：**2026-09-10 复查六场 20 轮与 1,800 次选择通过，但欢迎页长停留测试再次锁库、HTTP 500 和超时。此前 SQLite 测试也出现过 `database is locked` / HTTP 500，恢复默认不等于修复了这些问题。
历史 25 场完整验收使用 PostgreSQL，不能直接当作当前 SQLite 的稳定性证明。现场必须复验；报错时保留场次、日志和数据库，
不要强行推进或 resetdb。付款精度、滑块和固定分组等代码修复继续保留。

---

## 二、实验简介

**游戏规则**（被试视角）：每组 5 人或 15 人，固定分组玩 **20 轮**。每轮每人从
0–100 中选一个整数 x：

- **成本** = x² ÷ 200（数字越大成本越高，选 100 花 50 点）
- 全组提交后计算**小组中位数**；数字**严格低于**中位数的人支付固定**罚金 L**
  （L = 20 或 40，随处理而定；罚金与低多少无关）
- 每轮收益 = 100 − 成本 − 罚金（若被罚）


**流程**：分组等待 → 欢迎页（实验员统一放行）→ 实验说明 → 理解测试（5 题，必须全对，
答错会提示第几题错，页内有"📖 查看实验规则"按钮）→ 20 轮决策（belief 处理组每轮先预测
中位数，必填 0–100 整数）→ 问卷（11 题全必填）→ 报酬页。

**报酬**：出场费 **¥15** + 全场统一随机抽取一轮的收益 × **¥0.5/点**。
单人范围 ¥20.5–65，每场 15 名正式参与者报酬上限合计 **¥975**，需能支付到分；候补等其他费用另计。

## 三、处理（Treatment）与场次计划

每场固定 **15 人**、只跑一个处理。共 6 个处理、10 场、150 人：

| # | 组构成 | 罚金 L | Belief 预测 | 场次数 |
|---|---|---|---|---|
| Treatment 1 | 3 组 × 5 人 | 20 | 无 | 1 |
| Treatment 2 | 3 组 × 5 人 | 40 | 无 | 1 |
| Treatment 3 | 1 组 × 15 人 | 20 | 无 | 3 |
| Treatment 4 | 1 组 × 15 人 | 40 | 无 | 3 |
| Treatment 5 | 3 组 × 5 人 | 20 | 有 | 1 |
| Treatment 6 | 1 组 × 15 人 | 20 | 有 | 1 |

人数硬校验：每场必须恰好 15 人，多一个少一个都无法建场。候补安排和未上场者补偿按研究负责人确认的方案执行，程序不会自动处理。

## 四、服务器配置与数据保存

按第一节配置 Python、项目依赖、`OTREE_ADMIN_PASSWORD` 和 `OTREE_SECRET_KEY`，运行 `scripts/start_study.py`。
默认 SQLite 数据库位于项目目录的 `db.sqlite3`；无需单独安装数据库。启动脚本清除继承的 `DATABASE_URL`，
启用正式模式及后台登录保护。已有外部数据库保持原样，不自动迁移。

有效选择提交成功后由服务器保存；同组全部提交后，计算并保存每人的成本、罚金和 `round_payoff`。
20 轮分别留记录；分析各轮收益使用 `rbc.<轮次>.player.round_payoff`，标准 `payoff` 用于最终抽中轮付款。
尚未完成组内结算时，收益字段的初始 0 不能当作已经实现的收益。
首次分组后成员固定到第 20 轮，等待页只同步原组；断线时保持原场次、原座位身份。
首次分组按到达分组等待页的顺序形成，之后不重新随机分组。01–15 是座位标签，不保证 01–05 必然同组。
不同轮次在数据库中使用不同的 group 行，因此数据库内部 `group_id` 改变不等于换组；核对时应比较同组参与者名单。

**导出字段速查（`<轮次>` 为 1–20）：**

| 要核对的数据 | CSV 列名 |
|---|---|
| 参与者身份 / 座位标签 | `participant.code` / `participant.label` |
| 本轮选择 | `rbc.<轮次>.player.x_choice` |
| 本轮成本 / 实付罚金 | `rbc.<轮次>.player.cost` / `rbc.<轮次>.player.penalty_paid` |
| 本轮个人收益（点） | **`rbc.<轮次>.player.round_payoff`** |
| 本轮所在组 / 组内编号 | `rbc.<轮次>.group.id_in_subsession` / `rbc.<轮次>.player.id_in_group` |
| 本轮组中位数 | `rbc.<轮次>.group.median_x` |
| 本轮预测（仅预测处理） | `rbc.<轮次>.player.belief_median` |
| 抽中的支付轮 / 最终支付点数 | `participant.paid_round` / `participant.payoff` |

`rbc.<轮次>.player.payoff` 是 oTree 标准付款记账字段，本程序只在最后一轮记入抽中轮金额，
其余轮为 0 是预期行为；**分析逐轮收益一定读取 `round_payoff`**。人民币总额以 Payments / 参与者报酬页为准。
未完成的场次会有尚未选择的空值和未结算的初始收益；核查完整性前先确认参与者实际完成到哪一轮。


未提交、未到达服务器或保存失败的请求不能视为已记录。数据库锁定等报错需要处理后确认进度，
实验员不需要逐轮手动保存，但仍须每场导出和停服备份。详见 [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)。

## 五、被试电脑设置（一次性）

本项目配置了常驻候场室（Room）：`china_lab`，座位号 01–15。
给 15 台被试电脑的浏览器各设一个**桌面书签/主页**：

```
http://<服务器IP>:8000/room/china_lab?participant_label=01   ← 1 号机
http://<服务器IP>:8000/room/china_lab?participant_label=02   ← 2 号机
...依次到 15
```

未关联场次时，被试点书签进入候场页；Room 已关联场次时，入口会进入该场次。
也可以打开 `/room/china_lab`，手动输入两位座位号 **01–15**（01–09 保留前面的零）。
`1`、`Seat01`、姓名等不在当前允许列表中。展开 Room 页的 **Participant-specific URLs → Show/hide** 可复制各座位链接。

**一台电脑固定一个座位号，一名被试只开一个实验标签页。** 相同座位号在同一场次中对应同一身份，
两台电脑使用相同座位号会操作同一份数据。只要 Room 仍关联原场次，重新点原书签就能回到原身份。
原先使用 `Seat01` 等标签的旧测试场次不会自动改名；改用数字标签后应新建测试场次。

注意：其他电脑的网址必须填写实验服务器的实际 IP 或域名。`127.0.0.1` 和 `localhost` 只指向正在使用的那台电脑，
不能作为全实验室统一入口；端口以现场启动配置为准（本文示例为 8000）。

## 六、每场实验的操作流程（实验员 checklist）

### A. 开场前准备

- [ ] 按第一节启动当前程序，保持服务器运行，关闭自动休眠。
- [ ] 在实验员电脑登录后台 `/sessions`，用户名 `admin`，密码使用现场配置值。被试电脑只打开座位入口。
- [ ] 对照第三节场次计划，确认本场 Treatment、罚金、是否预测；每场 **15 人、20 轮**，保持默认轮数。
- [ ] 准备付款方式，能支付精确到人民币分的金额（例如 ¥64.75）；不自行取整。
- [ ] 检查 15 台电脑分别使用 **01–15**，没有重复座位号，也没有开着上一场参与者页面。

### B. 在 Room 里创建本场 Session

**Room 是重复使用的入口，Session 是一次实验及其数据。** `china_lab` 同时只关联一场；
Sessions 列表里其他场次不会因为存在就自动接入该 Room。现场统一从 Room 创建本场，避免把参与者送入错误场次。

1. 后台点击 **Rooms → 中国实验室 China Lab (15 seats)**。
2. 若显示 **Go to active session**，说明仍关联着一场。先点进去确认场次号；若是正在进行的本场，直接继续使用。
   若是上一场，按下面 G 节完成收尾后再解除关联。
3. Room 没有关联场次时，让 15 台电脑打开各自的座位书签。
4. 检查 Room 显示 **15 participants present**、**0 participants not present**，展开名单核对 01–15。
5. 在 **Create a new session** 表单中选择正确 Treatment，确认人数 **15**，点击 **Create session**。
6. 记录本场日期、Treatment、Session code、实验员。后续监控、付款和导出都核对这个场次号。

创建后参与者进入分组等待页，再进入欢迎页。人数到齐不是自动开始的条件，仍需下面的统一放行。

### C. 统一开始

- [ ] 打开本场 **Monitor**；也可通过 Room 的 **Go to active session** 进入。
- [ ] 确认全部 15 人的当前页面都是 **Welcome**（欢迎页）。
- [ ] 宣读既定开场说明，确认所有人准备好。
- [ ] 点击 **「开始实验（仅欢迎页）」**，所有人进入实验说明页。

按钮在未全部到 Welcome 时不可用。若不能点击，先查看哪位参与者还未到欢迎页，处理其连接或入口问题。
被试无法自行跳过欢迎页，必须由实验员统一开始。

### D. 实验进行中

实验员主要观察 **Monitor** 中的页面和轮次，不需要每轮点击开始。

| 页面 / 情况 | 正常逻辑 | 实验员操作 |
|---|---|---|
| Instructions：实验说明 | 被试阅读后自行下一页 | 按统一口径解释规则 |
| Quiz：理解测试 | 5 题全对才能继续，错误会提示 | 请被试重读规则并自行回答 |
| Belief：预测 | 仅 Treatment 5、6 出现，每轮必填 | 不代填；预测没有额外奖金 |
| Choice：选择 | 点击或拖动滑块后出现「提交」；点击 50 也算选择 | 确认被试知道先选择再提交 |
| WaitForGroup：等待 | 同组所有人提交后自动显示结果 | 查同组是否仍有人在预测或选择页 |
| Results：结果 | 被试阅读后自行下一页 | 不需要 admin 放行 |
| Survey：问卷 | 第 20 轮结束后出现，11 题必填；选“其他”需说明 | 请被试按页面提示完成 |
| Payment：实验结束 | 自己完成问卷即显示个人报酬 | 保留页面用于核对付款 |

小组处理是 **3 个 5 人组各自推进**；大组处理是 **15 人一起等待**。
不同组、不同被试的进度不完全一致是正常现象。恰好等于中位数不罚，只有严格低于中位数才罚。

### E. 掉线、等待不动或异常

1. 先记下 **场次号、座位号、轮次和页面名称**。
2. 查看 Monitor：若同组还有人未提交，先确认对方是在正常作答还是断线。
3. 单台电脑断线或页面关闭：确认网络恢复，让其重新打开**原座位书签**；Room 必须仍关联原场次。
   若尚未提交，可能需要重新选择；已成功提交的答案按原场次记录继续。
4. 多台电脑同时打不开：检查服务器进程、网络和数据库错误日志。需要重启时使用原代码、原数据库和原配置，
   恢复服务后再打开原入口。不要在进行中的场次修改代码或参数。
5. 若确实需要重启且后台仍可访问，先导出 CSV 和 Page times；突然断电可能丢失未写入数据库的页面时间缓冲。
6. 有人永久退出：该组没有自动补位或代填机制，会继续等待。由研究负责人按研究方案决定中止与补偿，并记录原因。

**不要为了消除等待而替被试填 0、强制推进、切换 Room 场次、创建替代场次或执行 resetdb。**
若 Room 已误切换，先从 Sessions 找回原场次和对应参与者链接，由实验员核实身份后恢复。

### F. 付款与数据保存

- [ ] Monitor 中确认全部 15 人都到 **Payment**（参与者标题为“实验结束”），而非只看到部分人完成。
- [ ] 打开本场 **Payments**，按参与者 label（01–15）核对座位；不要把列表序号当成座位号。
- [ ] 按**包含出场费的总金额**付款，并与被试付款页“合计”核对。后台总金额已含 ¥15，不再另加一次。
- [ ] 支付轮次在参与者付款页显示；每场所有人使用同一随机轮。20 轮收益不累加支付。
- [ ] 例如抽中的轮次全组选 10：收益 99.500 点，折算 ¥49.75，加出场费后 **¥64.75**。
- [ ] 逐人记录实付金额及是否已支付，避免重复付款；若金额不一致，保留页面和数据并核查后再结算。
- [ ] 导出本场 CSV：在该场 **Data** 页使用场次导出链接，核对场次号。
- [ ] 在顶部 **Data** 导出页下载 **Page times**；该文件可能包含多场，按 session code 区分并保留原文件。
- [ ] 确认文件能打开，CSV 有 15 名参与者、20 轮选择、问卷、支付轮次和金额。
- [ ] 用日期、Treatment、场次号命名保存，例如 `2026-09-XX_T1_<session_code>.csv`，备份到指定位置。

CSV 是实验数据导出；完整数据库备份由服务器负责人按现场方案执行。

### G. 换下一场与当天收尾

1. 确认上一场已全部完成、付款核对和数据备份已完成，让上一批参与者离场。
2. 返回 **Rooms → China Lab**，点击 **Close this room**。
   此按钮解除 Room 与原 Session 的关联，**不会删除原 Session 或其数据**；原场仍可在 Sessions 中查看。
3. 让各电脑关闭上一场的参与者页面，重新打开原来的数字座位书签，进入候场。
   已打开的上一场付款页不会自动变成下一场。
4. 按 B、C 节创建下一场、核对 Treatment 和新场次号，并统一开始。座位书签不需要换。
5. 当天结束后，确认所有导出与数据库备份完成，再由服务器负责人停止服务。

## 七、常见问题

| 问题 | 处理 |
|---|---|
| 被试电脑打不开候场页 | 检查是否和服务器同一局域网、IP 是否写对；服务器防火墙放行 8000 端口 |
| Room 页人数一直不满 15 | 有电脑没点书签，或两台电脑用了同一座位号 |
| 建场报"requires exactly 15 participants" | Create session 时人数必须是 15 |
| 页面关闭或网络中断 | Room 仍关联原场次时重开原座位书签；不要中途改代码或换场 |
| 忘记后台密码 | 在实验结束或妥善暂停后，修改本机启动文件中的 `OTREE_ADMIN_PASSWORD` 再重启；不要重置数据库 |

---

*参数速查：E=100，k=200，L=20/40，T=20 轮，出场费 ¥15，1 点=¥0.5，
全场同轮支付。所有可调参数集中在 `params.py`，修改后需重启服务器。*
