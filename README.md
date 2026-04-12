# 黄旭东 Skill

## 我是谁

这是一个把黄旭东（黄哥 / 毒奶色 / Xiaose）蒸馏成可运行 skill 的人物视角包。

它不是简单模仿口头禅，也不是只做“毒奶梗合集”。它更接近一个能运行的直播间人格系统：

- 会先嘴硬拿场
- 会分锅、甩锅、摊锅
- 会把内容问题翻译成“观众到底看不看”
- 会把社区问题翻译成“边界怎么压住”
- 会在翻车后决定是嘴硬、认账、还是复盘

## 这个 Skill 有什么不一样？

这个 skill 和一般人物 skill 最大的区别，不是“像不像黄旭东说话”，而是：

1. **把“嘴硬”提到了主逻辑，不是附录**
   黄旭东不是先分析后表达的人，他很多时候是先顶一句、先口嗨、先给自己留台阶，然后才决定要不要认真解释。

2. **同时保留两条线**
   一条是 `嘴硬部分` 的场景化话术。
   一条是操盘、节目、社区、规则、分锅这些深层框架。

3. **能处理“前后不完全一致”**
   普通 skill 会试图把人物整理得很统一。
   这个 skill 刻意保留黄旭东式矛盾：
   - 嘴上说打比赛不是为了赢
   - 结果输了又疯狂复盘
   - 先嘴硬
   - 出了机制问题又会认真认账

4. **优先回答“局面”**
   它不是纯知识顾问，更像直播间里那个要拍板的人。

## 蒸馏了什么进去？

### 1. 场景话术

- 吹毛
- 吃苦
- 我们没打好
- 打比赛又不是为了赢
- 你别管，就问你赢没赢

### 2. 框架层

- 嘴硬拿场
- 核心阵地优先
- 内容先要能看
- 锅要分层
- 先试再说

### 3. 表达层

- 直播间第一句话式起手
- 兄弟语气
- 结果论
- 损味、自黑、甩锅
- 先定气质，后补分析

### 4. 证据层

- scboy.cc 论坛近年高密度语料
- 社区与赛事相关发帖
- 对外报道与时间线材料

## 安装

### Claude Code

把目录放到 Claude Code 的 skills 目录，例如：

```bash
mkdir -p ~/.claude/skills/huangxudong-skill
cp -a /path/to/huangxudong-skill/. ~/.claude/skills/huangxudong-skill/
```

然后在新会话里直接说：

- `用黄旭东的视角`
- `切到毒奶色模式`
- `huangxudong-skill`

### Cursor

如果你用的是支持本地 prompt / persona / skill 注入的 Cursor 工作流，把整个目录作为角色包保存，然后在自定义指令或 prompt library 里引用 `SKILL.md` 内容。

一个常见做法是：

1. 建一个 `prompts/huangxudong-skill.md`
2. 把 `SKILL.md` 的内容贴进去或软链接进去
3. 在 Cursor 对话中手动触发这个 persona

### OpenClaw

如果 OpenClaw 使用本地角色/技能目录，把整个文件夹复制到它的 skills 或 personas 目录，再在配置里引用 `SKILL.md`。不同版本目录结构可能不同，但原则一样：

1. 保留完整目录
2. 保留 `references/` 与 `scripts/`
3. 让运行时读取 `SKILL.md`

### Codex

复制到：

```bash
mkdir -p ~/.codex/skills/huangxudong-skill
cp -a /path/to/huangxudong-skill/. ~/.codex/skills/huangxudong-skill/
```

新开会话后通常就能作为本地 skill 被发现。

## Skill 结构

```text
huangxudong-skill/
├── SKILL.md
├── README.md
├── scripts/
│   ├── download_subtitles.sh
│   ├── merge_research.py
│   ├── quality_check.py
│   └── srt_to_transcript.py
└── references/
    └── research/
        ├── 01-writings.md
        ├── 02-conversations.md
        ├── 03-expression-dna.md
        ├── 04-external-views.md
        ├── 05-decisions.md
        └── 06-timeline.md
```

## 蒸馏过程

这个 skill 不是一句 prompt 写出来的，而是按下面流程做的：

1. 先搭目录和 research 结构
2. 抽取论坛原帖中的高密度语料
3. 按 6 个维度写研究文件
4. 从研究里提炼人物框架
5. 再把 “嘴硬话术”提升为最高优先级路由
6. 最后回填到：
   - 角色扮演规则
   - 回答工作流
   - 身份卡
   - 核心心智模型
   - 决策启发式
   - 表达 DNA

也就是说，这个 skill 的主轴现在不是“黄旭东会怎么分析”，而是“黄旭东会先怎么嘴硬，再怎么分析”。

## 局限性

1. 黄旭东缺少稳定可检索的书籍或长篇系统访谈，所以理论层很多来自论坛语料和事件发言。
2. 这个 skill 擅长的是：
   - 直播社区
   - 节目内容
   - 赛事运营
   - 争议处理
   - 嘴硬与分锅
   它不适合拿来回答纯学术或完全无关领域的深技术问题。
3. 人物的公开表达和真实私下想法未必完全一致。
4. “嘴硬部分”强化后，输出会更像黄旭东，但也会更不稳定、更有攻击性。这是刻意保留的人格特征。

## 持续更新

建议持续更新这几个部分：

1. **嘴硬模板**
   如果你后面又整理出新的黄旭东口头场景，优先补进 `嘴硬部分`。

2. **近年动态**
   更新 `时间线` 和 `最新动态`，保证人物不会停留在旧状态。

3. **社区与赛事案例**
   黄旭东最有价值的地方，在于节目、社区、赛事、争议怎么处理。新案例越多，skill 越准。

4. **质量检查**
   每次大改后跑一次：

```bash
python3 scripts/quality_check.py SKILL.md
```

如果你还想继续强化这个 skill，最值得加的不是更多梗，而是更多“嘴硬之后怎么收场”的真实案例。
