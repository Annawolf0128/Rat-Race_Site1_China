# 中国站验收测试

全部测试只允许使用专门的测试数据库。不要在已有正式数据库上运行，也不要 reset 正式数据。
固定依赖见 requirements.txt；本轮验收：Python 3.9 / oTree 5.11.5 / PostgreSQL 16。

设置 `QA_OUTPUT_DIR` 为结果目录；HTTP 测试设置 `QA_BASE_URL=http://localhost:8021`。

| 脚本 | 范围 |
|---|---|
| payment_boundaries.py | 404 个金额组合、奇数组中位数、重复结算/刷新、支付轮次、输入范围；用独立 ORM 测试数据库 |
| configuration_checks.py | 拒绝非法人数/轮数/组大小/支付参数；用独立 ORM 测试数据库 |
| concurrent_flows.py | 六种处理，每种 15 人、20 轮；管理员放行后同步提交 |
| acceptance_edges.py | 六种处理逐项检查分组等待、长等待、禁止自行开始、错误题回填、强制推进保护、迟交、旧页重放、问卷、付款 |
| mixed_load.py | 四场共 60 人同步选择，另有一场停留欢迎页；全部完成 20 轮 |
| room_recovery.py | Room 座位身份、无效座位、同身份重进，准备 14 人已提交的重启检查点 |
| verify_acceptance.py | PostgreSQL 保存数据、实际 CSV 导出、逐人页面顺序、无自动代填答案的交叉核对 |
| study_launch.py | 独立数据库/端口 8022，正式启动脚本、后台登录、匿名 API 阻止和停止流程 |
| backup_compare.py | 停服后，比较源库与备份恢复库的六张核心表 |

`configuration_checks.py` 和 `payment_boundaries.py` 使用与 HTTP 服务器不同的 `DATABASE_URL`。
HTTP 测试服务器也必须使用专用 PostgreSQL，并设置 `OTREE_PRODUCTION=1` 隐藏 Debug。
合成数据服务器可在仅绑定 127.0.0.1 的情况下不设置 AUTH_LEVEL，方便 REST 驱动；正式服务器必须使用 scripts/start_study.py。

部分恢复/部署脚本针对本轮本机测试集群 127.0.0.1:55432，数据库名 china_qa / china_qa_units / china_qa_auth / china_qa_restored。
换环境前应修改这些测试专用连接，不要把脚本指向正式数据库。
`verify_acceptance.py` 使用已记录的场次 JSON；浏览器场次信息存入 browser_runs.json。

重启恢复：保存 room_restart.json 后停止 oTree 和它的 timeoutworker，再按相同 DATABASE_URL 启动；
用原 Seat01–Seat15 书签检查身份、14 个等待状态及最后一个 Choice，再提交最后一人并完成剩余轮次。
重启前先调用 ExportPageTimes 导出缓冲中的页面记录。

浏览器检查包含完整六种处理，以及手工错误题、滑块初始 50、两类等待页、管理员放行、重启后自动跳转、付款与后台一致性。
本轮不再以偶数组或小数中位数作为正式实验验收项。
