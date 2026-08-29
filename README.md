# Rat Race（反向选美）实验 — 中国站

本仓库是"Rat Race / Reversed Beauty Contest"实验的中国站独立部署包，基于 oTree 5，
界面全中文，报酬按人民币结算。本文档面向实验室的实验员：说明实验内容、如何配置服务器、
以及每一场实验的标准操作流程。

---

## 一、实验简介

**游戏规则**（被试视角）：每组 5 人或 15 人，固定分组玩 **20 轮**。每轮每人从
0–100 中选一个整数 x：

- **成本** = x² ÷ 200（数字越大成本越高，选 100 花 50 点）
- 全组提交后计算**小组中位数**；数字**严格低于**中位数的人支付固定**罚金 L**
  （L = 20 或 40，随处理而定；罚金与低多少无关）
- 每轮收益 = 100 − 成本 − 罚金（若被罚）

张力所在：全组都选低数字最省钱，但谁也不敢先降——这就是"rat race"。

**流程**：分组等待 → 欢迎页（实验员统一放行）→ 实验说明 → 理解测试（5 题，必须全对，
答错会提示第几题错，页内有"📖 查看实验规则"按钮）→ 20 轮决策（belief 处理组每轮先预测
中位数，必填 0–100 整数）→ 问卷（11 题全必填）→ 报酬页。

**报酬**：出场费 **¥15** + 全场统一随机抽取一轮的收益 × **¥0.5/点**。
单人范围 ¥20.5–65，每场（15 人）按上限备 **¥975** 现金即可。

## 二、处理（Treatment）与场次计划

每场固定 **15 人**、只跑一个处理。共 6 个处理、10 场、150 人：

| # | 组构成 | 罚金 L | Belief 预测 | 场次数 |
|---|---|---|---|---|
| Treatment 1 | 3 组 × 5 人 | 20 | 无 | 1 |
| Treatment 2 | 3 组 × 5 人 | 40 | 无 | 1 |
| Treatment 3 | 1 组 × 15 人 | 20 | 无 | 3 |
| Treatment 4 | 1 组 × 15 人 | 40 | 无 | 3 |
| Treatment 5 | 3 组 × 5 人 | 20 | 有 | 1 |
| Treatment 6 | 1 组 × 15 人 | 20 | 有 | 1 |

⚠ 人数硬校验：每场必须恰好 15 人，多一个少一个都无法建场。建议每场多约 2 名候补，
未上场者发出场费 ¥15 请回。

## 三、服务器配置（一次性，约 15 分钟）

需要一台实验期间保持开机的电脑（Windows/Mac 均可）作为服务器，和被试电脑连同一个局域网。
需要 **Python 3.9**。

### macOS / Linux

```bash
git clone https://github.com/Annawolf0128/Rat-Race_Site1_China.git
cd Rat-Race_Site1_China
python3.9 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows PowerShell

```powershell
git clone https://github.com/Annawolf0128/Rat-Race_Site1_China.git
Set-Location Rat-Race_Site1_China
py -3.9 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 正式启动（每次实验前）

```bash
# macOS / Linux
export OTREE_ADMIN_PASSWORD=你们的后台密码
export OTREE_PRODUCTION=1
otree prodserver 8000

# Windows PowerShell
$env:OTREE_ADMIN_PASSWORD="你们的后台密码"
$env:OTREE_PRODUCTION=1
otree prodserver 8000
```

- **必须用 `prodserver`**：数据写入 `db.sqlite3` 真实保存。`devserver` 只用于自测——
  它的数据在内存里，重启就没了，严禁用于正式实验
- 查服务器局域网 IP（如 `192.168.1.20`）：Mac `ipconfig getifaddr en0`；Windows `ipconfig`
- 后台入口：`http://<服务器IP>:8000/demo`，用户名 `admin`，密码即上面设置的

## 四、被试电脑设置（一次性）

本项目配置了常驻候场室（Room）：`china_lab`，座位号 Seat01–Seat15。
给 15 台被试电脑的浏览器各设一个**桌面书签/主页**：

```
http://<服务器IP>:8000/room/china_lab?participant_label=Seat01   ← 1 号机
http://<服务器IP>:8000/room/china_lab?participant_label=Seat02   ← 2 号机
...依次到 Seat15
```

被试点书签即进入候场页（"请等待实验开始"），**全程不需要输入任何网址**。
同一座位号刷新/重开浏览器会回到同一身份，不会占用两个名额——断线重连就是"再点一次书签"。

## 五、每场实验的操作流程（实验员 checklist）

1. **开场前**：确认 prodserver 在跑；被试落座、点开书签进入候场
2. 后台 → **Rooms** → china_lab，等待显示 **15/15 present**
3. 在该 Room 页选择本场的 **Treatment（1–6）** → **Create session**
   （人数会自动填 15）——所有候场浏览器自动进入实验，停在"欢迎"页
4. 打开该场次的 **Monitor** 页，确认 15 人都到齐欢迎页后，宣读开场说明，
   点 **"Advance slowest participant(s)"** 统一放行
5. 实验自动进行（约 30–45 分钟）。Monitor 页可实时看每人进度：
   - 有人卡在理解测试：系统会提示 ta 第几题错，页内可展开规则重读，一般无需干预
   - 有人掉线：让 ta 重新点击桌面书签即可回到原进度
6. 全部到达"实验结束"页后：后台 **Payments** 页有每人应付金额
   （出场费 + 抽中轮收益，页面同时显示抽中的是第几轮），按表付款
7. **数据导出**：后台 → Data → 下载 CSV（每场结束都导出备份一次）

**出问题需要重开一场**：直接在 Room 里重新 Create session，让被试"再点一次书签"
即可进入新场次；作废场次在数据导出时按 session code 剔除。

## 六、自测工具（正式实验前强烈建议跑一遍）

仓库自带**网格测试台**：一个页面平铺显示全部 15 名被试的实时画面，可自动推进整场。

1. 自测时用 `otree devserver 8000`（测试数据不入库）
2. 浏览器打开 `http://localhost:8000/static/grid.html`
3. 选一个 Treatment → "新建场次并平铺" → 点 **"▶ 自动推进"**，约 1–2 分钟自动跑完全场；
   也可取消某格"自动"勾选、亲自体验该被试的画面
4. 跑通即说明环境配置正确，换 prodserver 进入正式模式

## 七、常见问题

| 问题 | 处理 |
|---|---|
| 被试电脑打不开候场页 | 检查是否和服务器同一局域网、IP 是否写对；服务器防火墙放行 8000 端口 |
| Room 页人数一直不满 15 | 有电脑没点书签，或两台电脑用了同一座位号 |
| 建场报"requires exactly 15 participants" | Create session 时人数必须是 15 |
| 中途改了代码/重启服务器 | prodserver 数据在库里不丢；进行中的场次被试重新点书签即可继续 |
| 忘记后台密码 | 重启 prodserver 前重新 `export OTREE_ADMIN_PASSWORD=...` |

---

*参数速查：E=100，k=200，L=20/40，T=20 轮，出场费 ¥15，1 点=¥0.5，
全场同轮支付。所有可调参数集中在 `params.py`，修改后需重启服务器。*
