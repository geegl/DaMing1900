# 大明1900

《大明1900》是一个长篇架空历史小说项目，定位为番茄小说平台连载作品，风格为历史架空 + 技术流 + 谍战 + 宫廷斗争。

当前仓库不仅保存正文，也保存整套写作控制资料，包括：

- 世界观与人物圣经
- 章节风格约束
- 番茄平台节奏标准
- 长线剧情大纲
- 章节写作流水线 SOP

## 目录结构

```text
.
├── BIBLE.md
├── STYLE.md
├── FANQIE_STANDARDS.md
├── OUTLINE.md
├── PIPELINE.md
├── send_telegram.sh
└── chapters/
    ├── chapter_001.md
    └── chapter_002.md
```

## 核心文件说明

- `BIBLE.md`
  世界观、技术路线、政治结构、人物音色、禁区约束

- `STYLE.md`
  单章写法、对话规范、节奏要求、禁用词表

- `FANQIE_STANDARDS.md`
  面向番茄平台的钩子、爽点、节奏与读者留存标准

- `OUTLINE.md`
  全书三幕结构、前期章节细纲、长线伏笔与章节日志

- `PIPELINE.md`
  当前正式写作 SOP，包含规划、写作、校对、Codex 二次校对、日志回填、Telegram 通知与终检流程

- `chapters/`
  已完成章节正文

## 当前状态

- 已完成第 1 章与第 2 章正文
- 已接入 Telegram 通知脚本
- 已整理章节生产 SOP
- 已安装用于终检的外部技能环境

## 维护原则

- 以 `BIBLE.md` 和 `OUTLINE.md` 为最高约束
- 所有新章节必须经过 `PIPELINE.md` 流程
- 不将任何敏感 token、密钥或本地环境配置写入仓库
