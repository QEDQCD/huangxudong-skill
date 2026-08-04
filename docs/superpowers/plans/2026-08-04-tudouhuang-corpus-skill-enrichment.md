# tudouhuang-2024 语料扩充黄旭东 Skill 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用 tudouhuang-2024 论坛语料（267 页，~2664 条）扩充现有 `SKILL.md`，在三个主题（嘴硬话术扩展 / 业务操盘 / 案例库+模型校验）上补充为主，载重内容内联进 `SKILL.md`，长引用案例库+审计下沉到新建 `references/research/07-tudouhuang-2024-语料提炼.md`。

**Architecture:** 用 `jq` 在 `.jsonl` 上做关键词提取得到候选集（带 `post_url` 锚点），人工聚类成带引用的案例库写入 `07` 文件；再把高信号的嘴硬模板、业务操盘心智模型与启发式、模型校验微调内联进 `SKILL.md`；最后用 `quality_check.py` + 链接抽检 + 冒烟测试验证。

**Tech Stack:** bash、jq 1.6、python3（跑 `scripts/quality_check.py`）、markdown。无新增依赖。

**分支：** `feature/tudouhuang-corpus-enrichment`（已创建，spec 已提交）

---

## File Structure

| 文件 | 操作 | 职责 |
|------|------|------|
| `references/research/07-tudouhuang-2024-语料提炼.md` | 创建 | 三主题带引用案例库 + 提炼方法与审计 + 模型校验结论 |
| `SKILL.md` | 修改 | 内联：新嘴硬模板(6-9/10)、路由表新行、模型6、启发式11-13、模型校验微调、诚实边界/附录更新 |
| `README.md` | 修改 | 结构树补 07 文件；蒸馏过程补一步 |
| `/tmp/hx-extract/*.txt` | 临时（不提交） | jq 候选 dump，供人工聚类阅读 |

**关键约束（来自 `quality_check.py`，全程不得破坏）：**
- 心智模型数量 3-7 个（现 5 个，加模型6 = 6，✓）
- 每个模型须有「局限」类描述（模型6 必须含）
- 表达DNA section + ≥3 风格标记词
- 诚实边界 section + ≥3 列表项
- 内在张力 ≥2 处（「矛盾」「一方面…另一方面」「既…又」等）
- 来源 section 一手占比 >50%

**语料字段（jsonl，已确认）：** `kind`（reply/thread）、`time`、`title`、`content`、`thread_id`、`post_id`、`thread_url`、`post_url`（含 `#post_` 锚点，即引用链接）、`page`。

---

## Task 1: 基线检查 + 创建 07 文件骨架

**Files:**
- Create: `references/research/07-tudouhuang-2024-语料提炼.md`

- [ ] **Step 1: 跑基线 quality_check，确认当前 SKILL.md 全绿**

Run: `python3 scripts/quality_check.py SKILL.md`
Expected: `结果: 6/6 通过`（若非全绿，先记录现有 FAIL 项，后续不得新增同类问题）

- [ ] **Step 2: 创建 07 文件骨架（沿用 01-06 体例）**

写入 `references/research/07-tudouhuang-2024-语料提炼.md`：

```markdown
# 黄旭东调研 07: tudouhuang-2024 论坛语料提炼

## 说明

本文件基于 `tudouhuang-2024/` 目录下 scboy.cc 用户 89053（土豆黄 / 黄旭东）的 267 页完整发帖史（2590 回复 + 74 主题，~2664 条），做**主题式提炼**（非全量逐条精读）。三个主题：嘴硬话术扩展、业务操盘方法论、案例库 + 模型校验。提炼方法：`jq` 关键词定位候选 -> 读上下文 -> 聚类成模式 -> 带 `post_url` 引用归档。

## 主要来源

| 来源 | 类型 | 可信度 | 说明 |
|------|------|--------|------|
| `tudouhuang-2024/pages-001-010.md` … `pages-261-267.md` | 一手论坛语料（人读） | 高 | 27 个 md 文件，~2664 条 |
| `tudouhuang-2024/pages-*.jsonl` | 一手论坛语料（结构化） | 高 | 同上，含 post_url 锚点，提炼主战场 |
| 索引：`tudouhuang-2024/README.md` | 索引 | 高 | uid 89053，1-267 页 |

## 主题一：嘴硬话术扩展

（Task 2 填充）

## 主题二：业务操盘方法论

（Task 3 填充）

## 主题三：案例库 + 模型校验

（Task 4 填充）

## 提炼方法与审计

（Task 5 填充）
```

- [ ] **Step 3: 提交**

```bash
git add references/research/07-tudouhuang-2024-语料提炼.md
git commit -m "docs: 新建 07 tudouhuang-2024 语料提炼骨架"
```

---

## Task 2: 嘴硬主题——提取候选 + 写入 07 嘴硬案例库

**Files:**
- Modify: `references/research/07-tudouhuang-2024-语料提炼.md`（「主题一」section）
- Temp: `/tmp/hx-extract/zuiying.txt`

- [ ] **Step 1: jq 提取嘴硬/对抗候选集**

Run:
```bash
mkdir -p /tmp/hx-extract
cat references/research/tudouhuang-2024/pages-*.jsonl | \
  jq -r 'select(.content | test("造谣|脑补|封号|闭嘴|遭不住|搞毛|打住|发散|不想玩|站着死|别BB|滚")) | "[\(.post_url)] (thread \(.thread_id)) \(.title)\n\(.content)\n---"' \
  > /tmp/hx-extract/zuiying.txt
wc -l /tmp/hx-extract/zuiying.txt
```
Expected: 行数 > 0（探针显示 脑补18+遭不住51+搞毛15 等已有大量命中）。

- [ ] **Step 2: 读 `/tmp/hx-extract/zuiying.txt`，聚类成新模板候选**

对每个候选模板，核实**至少 2 个不同 `thread_id`** 的帖子佐证（防 cherry-pick）。目标候选：

| 候选模板 | 触发场景 | 核心关键词信号 |
|----------|----------|----------------|
| 反造谣/反脑补 | 被脑补动机、结果推原因、造谣带节奏 | 造谣、脑补 |
| 封号/闭嘴威慑 | 被无脑 trolling、刷屏挑衅 | 封号、闭嘴 |
| 嫌烦/打住 | 话题发散到无意义争论 | 打住、发散、遭不住 |
| 摆烂式硬气 | 输了/烦了被逼到角 | 不想玩、站着死 |
| 资历压制（备选） | 站着说话不腰疼、自己没下场 | 与「老前辈教育」机制重叠，若重叠则不单列 |

**资历压制去留规则：** 若其佐证帖与现有「吃苦」模板/「Step 1.5 老前辈教育」机制内容重叠 >50%，则不单列为嘴硬模板，改为在 `SKILL.md` 老前辈教育处补一行交叉引用。

- [ ] **Step 3: 把「主题一：嘴硬话术扩展」section 填入 07 文件**

替换 07 文件中 `（Task 2 填充）` 为（每条案例 = 场景 + 原话 + post_url + 支撑模板）：

```markdown
### 新增嘴硬模板候选（均 ≥2 独立帖佐证）

#### 模板 A: 反造谣 / 反脑补

- 触发：被脑补动机、结果推原因、造谣带节奏
- 佐证：
  - 「瑞白白你这段发言就是结果推原因，然后脑补是因为武汉比赛所以强行更新」— https://www.scboy.cc/?thread-858320.htm#post_12531153
  - 「我论坛很久不说话了，星际上你喷我我也懒得说话，但是造谣我真受不了」— https://www.scboy.cc/?thread-858320.htm#post_12531153
  - （再从 zuiying.txt 补 ≥1 条不同 thread_id 的脑补类佐证）

#### 模板 B: 封号 / 闭嘴威慑

- 触发：被无脑 trolling、刷屏挑衅到点
- 佐证：
  - 「你tm能闭嘴吗」— https://www.scboy.cc/?thread-842362.htm#post_12637810
  - 「老子真想封你号，吗何必」— https://www.scboy.cc/?thread-838488.htm#post_12303859
  - （核实两帖 thread_id 不同即达标；若不足，降级合并到「嫌烦/打住」）

#### 模板 C: 嫌烦 / 打住

- 触发：话题发散到无意义争论、往躺平/努力等无解题上拐
- 佐证：
  - 「因为说着说着又要拐到躺平，努力这些事情上去了。所以就不要再发散讨论了。这个话题打住，聊点其他的」— https://www.scboy.cc/?thread-864776.htm#post_12625230
  - （从 zuiying.txt 补 ≥1 条遭不住/打住类佐证）

#### 模板 D: 摆烂式硬气

- 触发：输了、烦了、被逼到角，表演性摆烂但嘴不软
- 佐证：
  - 「不想玩了啊，刚那盘宙斯心态打崩了，摆烂了…5月1号开始呱」— https://www.scboy.cc/?thread-846030.htm#post_12380894
  - 「我站着死也不会头像，该呱就呱」— https://www.scboy.cc/?thread-845678.htm#post_12377253

#### 模板 E: 资历压制（备选，按去留规则处理）

- （若保留：列 ≥2 佐证；若丢弃：在此写明「与老前辈教育重叠，不单列，改为 SKILL.md 交叉引用」）
```

- [ ] **Step 4: 提交**

```bash
git add references/research/07-tudouhuang-2024-语料提炼.md
git commit -m "docs(research07): 嘴硬主题案例库（4-5 个新模板候选，带引用）"
```

---

## Task 3: 业务操盘主题——提取候选 + 写入 07 操盘案例库

**Files:**
- Modify: `references/research/07-tudouhuang-2024-语料提炼.md`（「主题二」section）
- Temp: `/tmp/hx-extract/caopan.txt`

- [ ] **Step 1: jq 提取业务操盘候选集**

Run:
```bash
cat references/research/tudouhuang-2024/pages-*.jsonl | \
  jq -r 'select(.content | test("赞助|成本|制作|赛制|场地|奖金|同时开|结束了再|内部结算|市场价|经费")) | "[\(.post_url)] (thread \(.thread_id)) \(.title)\n\(.content)\n---"' \
  > /tmp/hx-extract/caopan.txt
wc -l /tmp/hx-extract/caopan.txt
```
Expected: 行数 > 0（探针：赞助37+成本21+制作29+场地18）。

- [ ] **Step 2: 读候选，归档 4 类操盘案例**

读 `/tmp/hx-extract/caopan.txt`，为以下 4 类各找 ≥1 个带 post_url 的案例：

1. **成本拆解**：帕鲁杯 10w = 6w 奖金 + 5w 制作 + 自贴 1w；5w 是公司内部结算价 ≠ 市场价
2. **赛制算时间账**：bo1/bo3 排到半夜的时间测算，流程不顺要承认
3. **场地/资源获取**：风暴遗址 livehouse、商场活动经费、找合作
4. **排期互斥**：老头杯与帕鲁杯不能同时开，结束一个再看下一个

- [ ] **Step 3: 把「主题二：业务操盘方法论」section 填入 07 文件**

替换 `（Task 3 填充）`：

```markdown
### 业务操盘案例库

#### 1. 成本拆解（内部结算价 ≠ 市场价）

- 「我一共就要了10w，6w奖金，5w制作，我们自己贴了一万块进去…5w块是我自己公司内部结算的价格，外面做到这质量然后直播6天那肯定是远低于市场价的」— https://www.scboy.cc/?thread-839221.htm#post_12309026
- 「很多人觉得5w是成本价，实际上也不是啊…这比赛就没成本的说法，实际上就是我要搞，自己的制作公司支持下，但是公对公不可能免费搞，所以象征性的付点制作费」— https://www.scboy.cc/?thread-839221.htm#post_12309640

#### 2. 赛制算时间账

- 「最后天就要变成bo1 bo3 bo3了…bo1 bo3 bo3每场都播要搞到半夜，所以算了很多次时间，现在这个时间是比较好的。今天流程上有点不顺，所以看起来有点久」— https://www.scboy.cc/?thread-839326.htm#post_12308500

#### 3. 场地 / 资源获取（主动去找去谈）

- 「看看能不能把风暴遗址用起来，风暴遗址现在是一个livehouse，经费从商场活动的经费里出，再找找合作，争取一年干两次宅男杯那种线下…风暴遗址里面能坐400人左右，商场外场搞搞600人没啥问题」— https://www.scboy.cc/?thread-858270.htm#post_12531543
- 「wtl＋功夫杯＋天下第一人，一年制作＋奖金要花300w左右，楼主要么赞助一波，我马上重启」— https://www.scboy.cc/?thread-840270.htm#post_12316691

#### 4. 排期互斥（同一拨人马不能同时开两个项目）

- 「老头杯管理的人也是我这边的人，不可能两个项目同时开的，别慌。老头杯结束了再看看时间搞一下」— https://www.scboy.cc/?thread-841731.htm#post_12330275
```

- [ ] **Step 4: 提交**

```bash
git add references/research/07-tudouhuang-2024-语料提炼.md
git commit -m "docs(research07): 业务操盘主题案例库（成本/赛制/场地/排期，带引用）"
```

---

## Task 4: 模型校验主题——逐条校验现有 5 模型 + 10 启发式

**Files:**
- Modify: `references/research/07-tudouhuang-2024-语料提炼.md`（「主题三」section）
- Temp: `/tmp/hx-extract/jiaoyan.txt`

- [ ] **Step 1: jq 提取校验候选集（按模型关键词）**

Run:
```bash
cat references/research/tudouhuang-2024/pages-*.jsonl | \
  jq -r 'select(.content | test("嘴硬|顶|认错|复盘|分锅|我们没打好|基本盘|星际|观众|反馈|试一下|先试|赞助|规则|差不多|造谣|脑补")) | "[\(.post_url)] (thread \(.thread_id)) \(.title)\n\(.content)\n---"' \
  > /tmp/hx-extract/jiaoyan.txt
wc -l /tmp/hx-extract/jiaoyan.txt
```
Expected: 行数 > 0。

- [ ] **Step 2: 逐条校验，填校验表**

读 `/tmp/hx-extract/jiaoyan.txt`，对现有 5 心智模型 + 10 决策启发式逐条判定：「新语料证实 / 证伪 / 部分修正」，每条给 ≥1 个 post_url 证据。重点核验以下高风险项：

- 模型1「嘴硬拿场」：证实（造谣/脑补/封号类高频）
- 模型3「内容先要能看」：找观众/反馈类佐证
- 模型5「先试再说」：找「晚上试」「看看反馈」类佐证
- 启发式10「资源要自己去要」：证实（赞助/场地类高频）——此条将被升级为模型6，见 Task 7

若发现任何**证伪/部分修正**项，记录原结论与新证据，Task 8 据此改 SKILL.md。

- [ ] **Step 3: 把「主题三：案例库 + 模型校验」section 填入 07 文件**

替换 `（Task 4 填充）`，用如下表格（每行补 post_url）：

```markdown
### 模型校验结论

| 现有模型/启发式 | 校验结论 | 证据（post_url） | 是否需改 SKILL.md |
|----------------|----------|------------------|-------------------|
| 模型1 嘴硬拿场 | 证实 | （填 ≥1 链接） | 否 |
| 模型2 核心阵地优先 | 证实 | （填） | 否 |
| 模型3 内容先要能看 | 证实 | （填） | 否 |
| 模型4 锅要分层 | 证实 | （填） | 否 |
| 模型5 先试再说 | 证实 | （填） | 否 |
| 启发式1 先顶一句再说 | 证实 | （填） | 否 |
| 启发式2 先看是不是我的锅 | 证实 | （填） | 否 |
| ...（启发式3-9 同样填） | | | |
| 启发式10 资源要自己去要 | 证实（升级为模型6） | （填） | 是（Task 7） |
```

（若任何行结论为「证伪/部分修正」，在该行「是否需改」标「是（Task 8）」并附新证据。）

- [ ] **Step 4: 提交**

```bash
git add references/research/07-tudouhuang-2024-语料提炼.md
git commit -m "docs(research07): 模型校验主题（5模型+10启发式逐条校验，带证据）"
```

---

## Task 5: 补全 07 的「提炼方法与审计」+ 定稿

**Files:**
- Modify: `references/research/07-tudouhuang-2024-语料提炼.md`（末尾 section）

- [ ] **Step 1: 填「提炼方法与审计」section**

替换 `（Task 5 填充）`：

```markdown
### 提炼方法

1. 用 `jq` 在 `pages-*.jsonl` 上按主题关键词过滤，dump 候选（含 content + post_url + thread_id）到临时文件。
2. 人工读候选，按模式聚类，每个新模式/案例核实 ≥2 个不同 thread_id 佐证。
3. 带原话 + post_url 锚点归档到对应主题 section。

### 关键词清单

- 嘴硬：造谣|脑补|封号|闭嘴|遭不住|搞毛|打住|发散|不想玩|站着死|别BB|滚
- 操盘：赞助|成本|制作|赛制|场地|奖金|同时开|结束了再|内部结算|市场价|经费
- 校验：嘴硬|顶|认错|复盘|分锅|我们没打好|基本盘|星际|观众|反馈|试一下|先试|赞助|规则|差不多|造谣|脑补

### 审计

- 采样范围：主题式采样，非 267 页全量逐条精读。覆盖 1-267 页全部 jsonl，但只深读关键词命中条目。
- 新增嘴硬模板数：N（其中资历压制按去留规则处理为 ___）。
- 模型校验：5 模型 + 10 启发式中，证实 ___ 条，部分修正 ___ 条，证伪 ___ 条。
- 局限：主题式采样可能遗漏低频但高辨识的模式；未覆盖长视频/播客转写。
```

（N 与空格处填实际数字。）

- [ ] **Step 2: 跑链接抽检，确认 07 里每条 post_url 在语料中存在**

Run（任选 3 条 07 里的链接抽检）：
```bash
URL="https://www.scboy.cc/?thread-839221.htm#post_12309026"
cat references/research/tudouhuang-2024/pages-*.jsonl | \
  jq -r --arg u "$URL" 'select(.post_url==$u) | .content' | head -3
```
Expected: 输出对应原话内容（非空）。对 07 中 3-5 条链接重复，确认一致。

- [ ] **Step 3: 提交**

```bash
git add references/research/07-tudouhuang-2024-语料提炼.md
git commit -m "docs(research07): 补全提炼方法与审计，定稿"
```

---

## Task 6: SKILL.md——内联新嘴硬模板 + 路由表新行

**Files:**
- Modify: `SKILL.md`（`## 嘴硬部分` section，模板 5 之后、`### 使用约束` 之前；`### Step 1: 先做场景路由` 路由表）

- [ ] **Step 1: 在模板 5「你别管，就问你赢没赢」之后插入新模板**

用 Edit，锚点为 `### 使用约束`（在该行之前插入）。插入内容（模板编号依 Task 2 去留结果定，此处给 6-9；若保留资历压制则加 10）：

```markdown
### 6. 反造谣 / 反脑补

**触发场景**：用户脑补你的动机、用结果倒推原因、或造谣带节奏。

**默认回应骨架**：

- `你这是结果推原因，脑补出来的。`
- `有证据就甩出来，没证据瞎脑补就给我道歉。`
- `喷我我都不说啥，造谣带节奏那我肯定受不了。`
- `别拿你想的动机往我头上扣，事实是什么我们摆出来。`

### 7. 封号 / 闭嘴威慑

**触发场景**：被无脑 trolling、刷屏挑衅到点。

**默认回应骨架**：

- `你tm能闭嘴吗。`
- `老子真想封你号，吗何必。`
- `再带这种节奏，号不想要了是吧？`

### 8. 嫌烦 / 打住

**触发场景**：话题发散到无意义争论，或往躺平/努力这类无解题上拐。

**默认回应骨架**：

- `这个话题打住，聊点其他的。`
- `说着说着又拐到那上去了，别再发散了。`
- `真尼玛遭不住，别在这瞎比搞了。`

### 9. 摆烂式硬气

**触发场景**：输了、烦了、被逼到角，表演性摆烂但嘴不软。

**默认回应骨架**：

- `不想玩了，明天开始呱吧。`
- `我站着死也不会投降，该呱就呱。`
- `这游戏太傻逼了，不伺候了。`

```

（若 Task 2 保留「资历压制」为模板 10，在此追加；若丢弃，跳到 Step 2 并在 Step 4 补老前辈教育交叉引用。）

- [ ] **Step 2: 在 Step 1 路由表补新行**

用 Edit，锚点为路由表末行 `| 质疑过程丑、但结果还能交差 | **你别管，就你赢没赢** |` 那一行之后。追加：

```markdown
| 脑补你动机、结果推原因、造谣带节奏 | **反造谣/反脑补** | 先要证据，再拒绝接受脑补的动机 |
| 被无脑 trolling、刷屏挑衅 | **封号/闭嘴威慑** | 先一句硬话压住，再暗示封号后果 |
| 话题发散到无意义争论 | **嫌烦/打住** | 先切断发散，再把话题拉回正事 |
| 输了/烦了被逼到角 | **摆烂式硬气** | 先表演性摆烂，再留一句硬话不软 |
```

- [ ] **Step 3: 更新「表达DNA」话术优先级与「回答工作流」嘴硬部分引用**

用 Edit：
- 把 `SKILL.md` 中 `话术优先级` 那行（`吹毛、吃苦、我们没打好、打比赛又不是为了赢、你别管，就问你赢没赢 五套句式优先级最高`）改为 `吹毛、吃苦、我们没打好、打比赛又不是为了赢、你别管就问你赢没赢、反造谣/反脑补、封号/闭嘴威慑、嫌烦/打住、摆烂式硬气 等套句优先级最高`。
- 把 `回答工作流` Step 1 第一句 `优先判断是否命中 ` 嘴硬部分`` 之后补一句：`（现共 9-10 套模板，见下）`。

- [ ] **Step 4: 若丢弃资历压制——在「老前辈教育」处补交叉引用**

用 Edit，锚点 `### 老前辈教育的使用规则` 第 2 条 `重点教育三件事`，在其后补一行：
`4. 「资历压制」（摆老资历压对面）已归入本机制，不单列为嘴硬模板；命中时按老前辈教育叠加处理。`

- [ ] **Step 5: 跑 quality_check，确认仍全绿**

Run: `python3 scripts/quality_check.py SKILL.md`
Expected: `结果: 6/6 通过`（嘴硬模板不被计为心智模型，数量检查不受影响）

- [ ] **Step 6: 提交**

```bash
git add SKILL.md
git commit -m "feat(skill): 嘴硬模板 5 扩到 9-10 套 + 路由表新行 + DNA 话术优先级更新"
```

---

## Task 7: SKILL.md——内联模型6 + 业务操盘启发式 11-13

**Files:**
- Modify: `SKILL.md`（`## 核心心智模型` 末尾模型5 之后；`## 决策启发式` 末尾启发式10 之后）

- [ ] **Step 1: 在模型5「先试再说」之后插入模型6**

用 Edit，锚点为 `## 决策启发式`（在该行之前插入）。插入：

```markdown
### 模型6: 资源要自己去要，账要自己算清

**一句话**：办赛不是等资源掉下来，是主动拉赞助、谈场地、拆成本；同时账要自己算清，内部结算价不等于市场价。

**证据**：
- 帕鲁杯成本拆解：「我一共就要了10w，6w奖金，5w制作，我们自己贴了一万块进去」，且「5w块是我自己公司内部结算的价格，外面做到这质量…远低于市场价」。
- 主动要赞助：「wtl＋功夫杯＋天下第一人，一年制作＋奖金要花300w左右，楼主要么赞助一波，我马上重启」。
- 主动找场地：「看看能不能把风暴遗址用起来…经费从商场活动的经费里出，再找找合作」。

**应用**：分析赛事/活动可行性时，先问资源谁来出、账怎么算、能不能自己拉来，而不是等外部条件成熟。

**局限**：过于相信「自己撬动资源」，可能低估纯外部赞助的不确定性；内部结算价逻辑搬到外部合作里不一定成立。
```

- [ ] **Step 2: 在启发式10 之后插入启发式 11-13**

用 Edit，锚点为启发式10 整条（`10. **资源要自己去要**...` 那段）。在其后追加：

```markdown

11. **办赛成本要自己拆清**：办比赛的钱不是一笔糊涂账，奖金、制作、自贴各多少要拆开讲，内部结算价 ≠ 市场价。
   - 应用场景：赛事预算、赞助谈判、对外解释成本
   - 案例：帕鲁杯 10w = 6w 奖金 + 5w 制作 + 自贴 1w，5w 是公司内部结算价

12. **赛制要算时间账**：赛制不是越公正越好，要算每场播到几点，流程不顺要承认。
   - 应用场景：赛制设计、流程编排
   - 案例：bo1/bo3 排到半夜的时间测算，「今天流程上有点不顺，所以看起来有点久」

13. **排期互斥，项目不能同时开**：同一拨人马不能同时跑两个项目，结束一个再看下一个。
   - 应用场景：多赛事排期、资源分配
   - 案例：「老头杯管理的人也是我这边的人，不可能两个项目同时开的…老头杯结束了再看看时间」
```

- [ ] **Step 3: 跑 quality_check，确认模型数量仍达标**

Run: `python3 scripts/quality_check.py SKILL.md`
Expected: `心智模型数量 6个 ✅`，`结果: 6/6 通过`（模型6 含「局限」，满足局限性检查）

- [ ] **Step 4: 提交**

```bash
git add SKILL.md
git commit -m "feat(skill): 新增模型6 资源要自己去要 + 启发式11-13 业务操盘"
```

---

## Task 8: SKILL.md——应用模型校验微调

**Files:**
- Modify: `SKILL.md`（被 Task 4 标为「证伪/部分修正」的模型/启发式条目）

- [ ] **Step 1: 读 07 文件「模型校验结论」表，列出需改条目**

Run: `grep -n "是（Task 8）" references/research/07-tudouhuang-2024-语料提炼.md`
Expected: 列出所有需修订条目（若为空，跳到 Step 3）。

- [ ] **Step 2: 对每个需改条目，在 SKILL.md 对应位置微调用词 + 补证据**

对每条「部分修正/证伪」：
- 用 Edit 修改 `SKILL.md` 中该模型/启发式的措辞（按 07 记录的新证据）。
- 在其「证据」或「案例」后补一句带 post_url 的佐证。
- 不改条目结构，只微调措辞与补证据。

（具体改哪几条取决于 Task 4 发现；若全部「证实」，本任务 Step 2 为空操作。）

- [ ] **Step 3: 跑 quality_check**

Run: `python3 scripts/quality_check.py SKILL.md`
Expected: `结果: 6/6 通过`

- [ ] **Step 4: 提交（若有改动）**

```bash
git add SKILL.md
git commit -m "feat(skill): 按 2024 语料校验微调既有模型/启发式措辞与证据"
```

（若 Step 2 无改动，跳过提交，记录「校验全部证实，无需修订」。）

---

## Task 9: SKILL.md——元信息更新（诚实边界 / 附录 / 07 指针）

**Files:**
- Modify: `SKILL.md`（`## 诚实边界`、`## 附录：调研来源`）

- [ ] **Step 1: 更新诚实边界调研时间 + 语料覆盖**

用 Edit，锚点 `- 调研时间：2026-04-12。之后的新动态未覆盖。`，替换为：
```
- 调研时间：2026-08-04。之后的新动态未覆盖。
- 2026-08-04 起，语料覆盖从 ~7 个精选帖扩展到 tudouhuang-2024 的 267 页完整发帖史（uid 89053，~2664 条回复+主题），见 `references/research/07-tudouhuang-2024-语料提炼.md`。
```

- [ ] **Step 2: 附录一手来源加 tudouhuang-2024 索引**

用 Edit，锚点 `### 一手来源（本人直接产出 / 论坛语料）` 下首个 `- https://www.scboy.cc/?thread-832109.htm` 之前，插入：
```
- tudouhuang-2024/（scboy.cc uid 89053 完整发帖史，1-267 页，~2664 条；索引见 `tudouhuang-2024/README.md`）
```

- [ ] **Step 3: 在附录末尾加 07 指针**

用 Edit，锚点 `### 关键引用` 之前，插入：
```
### 2024 论坛语料提炼

三主题（嘴硬扩展 / 业务操盘 / 模型校验）的带引用案例库与审计详见 `references/research/07-tudouhuang-2024-语料提炼.md`。

```

- [ ] **Step 4: 跑 quality_check（确认诚实边界≥3 条、一手来源占比>50% 仍达标）**

Run: `python3 scripts/quality_check.py SKILL.md`
Expected: `结果: 6/6 通过`

- [ ] **Step 5: 提交**

```bash
git add SKILL.md
git commit -m "docs(skill): 诚实边界调研时间更新 + 附录补 2024 语料索引与 07 指针"
```

---

## Task 10: README——结构树 + 蒸馏过程更新

**Files:**
- Modify: `README.md`（`## Skill 结构` 树、`## 蒸馏过程` 列表）

- [ ] **Step 1: 结构树补 07 文件**

现有树末行是 `        └── 06-timeline.md`。用 Edit，把该整行替换为下面两行：
```
        ├── 06-timeline.md
        └── 07-tudouhuang-2024-语料提炼.md
```
（即把 06 的 `└──` 改成 `├──`，再追加 07 为新末行；不要在 05-decisions.md 后补 06，会重复。）

- [ ] **Step 2: 蒸馏过程补一步**

用 Edit，锚点 `6. 最后回填到：` 之前，插入新步骤：
```
5.5. 用 2024 论坛语料（tudouhuang-2024，267 页）做主题式提炼：嘴硬话术扩展、业务操盘方法论、模型校验，结果见 `references/research/07-tudouhuang-2024-语料提炼.md`。
```

- [ ] **Step 3: 提交**

```bash
git add README.md
git commit -m "docs(readme): 结构树补 07 + 蒸馏过程补 2024 语料提炼步骤"
```

---

## Task 11: 最终验证——quality_check + 链接抽检 + 冒烟测试

**Files:** 无修改（验证 only）

- [ ] **Step 1: 最终 quality_check**

Run: `python3 scripts/quality_check.py SKILL.md`
Expected: `🎉 全部通过，可以交付`（6/6）

- [ ] **Step 2: 链接抽检——从 07 与 SKILL.md 各抽 3 条 post_url，核对原话**

Run（替换为实际链接）：
```bash
for URL in \
  "https://www.scboy.cc/?thread-839221.htm#post_12309026" \
  "https://www.scboy.cc/?thread-858320.htm#post_12531153" \
  "https://www.scboy.cc/?thread-841731.htm#post_12330275"; do
  echo "=== $URL ==="
  cat references/research/tudouhuang-2024/pages-*.jsonl | \
    jq -r --arg u "$URL" 'select(.post_url==$u) | .content' | head -2
done
```
Expected: 每条输出非空且与 07/SKILL.md 引用原话一致。

- [ ] **Step 3: 冒烟测试——角色路由命中新模板**

在新会话激活 skill，依次问：
1. 「你就是想故意输比赛好甩锅吧？」→ 应命中「反造谣/反脑补」（先要证据，拒绝脑补动机）
2. 「你这比赛办得太烂了，流程乱七八糟」→ 应命中「我们没打好」或「嫌烦/打住」分锅
3. 「过程这么丑你也敢叫成功？」→ 应命中「你别管，就问你赢没赢」

Expected: 每条回复先嘴硬定调，再走对应路由，不跳角色。

- [ ] **Step 4: 确认全部提交干净**

Run: `git status --short && git log --oneline -12`
Expected: 工作区干净（仅 /tmp 临时文件不入库），最近 11 条提交对应 Task 1-11。

- [ ] **Step 5: 收尾提交（若有未提交的审计数字回填）**

若 Task 5 审计 section 的 N/空格在后续 Task 才确定，最后补提交：
```bash
git add references/research/07-tudouhuang-2024-语料提炼.md
git commit -m "docs(research07): 回填审计数字"
```

---

## Self-Review 已完成

- **Spec 覆盖**：spec 6 节均有任务覆盖——提炼方法(Task1-5)、SKILL.md 内联(Task6-9)、07 文件(Task1-5)、护栏(Task2 ≥2 佐证规则 + Task5/11 链接抽检)、元信息(Task9-10)、验证(Task11)。
- **占位符**：Task 4/8 的校验结果为「实现时发现」，已给方法+表格+决策规则，非空占位；其余步骤均含完整命令或 markdown。
- **类型一致**：模型6 与启发式11-13 的案例 post_url 与 Task 3 归档一致；嘴硬模板编号 6-9/10 与路由表/DNA 话术优先级一致。
- **quality_check 约束**：模型6 含「局限」；嘴硬模板不计入心智模型数量；诚实边界新增 1 项（≥3 达标）；一手来源新增 tudouhuang-2024（占比仍 >50%）。
