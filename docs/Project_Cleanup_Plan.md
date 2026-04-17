# 项目清理方案

## 一、规划层补丁文件处理

### 删除文件
| 文件 | 原因 | 状态 |
|------|------|------|
| `political-forces-layout-21-50.md` | 内容已整合到Bible.md | 待删除 |
| `第1-10章重构BeatSheet.md` | 已整合到Master Outline v5.0 | 待删除 |

### 保留文件
| 文件 | 说明 |
|------|------|
| `Daming1900_Master_Outline.md` | 唯一大纲 v5.0 |
| `character-database.md` | 人物数据库 |
| `northern-threat-manchu-remnants.md` | 北方威胁设定 |
| `political-architecture-1900.md` | 政治架构设定 |

---

## 二、根目录冗余文件清理

### 删除文件
| 文件 | 原因 |
|------|------|
| `AUTOMATION_WORKFLOW.md` | 旧版工作流，已过时 |
| `CLOUD_COLLABORATION_GUIDE.md` | 不需要云协作指南 |
| `V5_UPGRADE_GUIDE.md` | 升级已完成，不再需要 |

### 保留文件
| 文件 | 说明 |
|------|------|
| `CLAUDE.md` | 项目CLAUDE配置 |
| `README.md` | 项目说明 |
| `.gitignore` | Git配置 |
| `setup_github.sh` | GitHub设置脚本（可选保留） |

---

## 三、progress目录归档

### 删除文件
| 文件 | 原因 |
|------|------|
| `BATCH_01_REPORT.md` ~ `BATCH_05_REPORT.md` | 旧批次报告，已清空重写 |
| `CURRENT.md` | 旧进度，已过时 |
| `HISTORY.md` | 旧历史，已过时 |
| `stats.json` | 旧统计数据 |

### 保留目录
- progress/ 目录保留，但清空内容（未来放新进度）

---

## 四、automation目录清理

### 删除目录
| 目录 | 内容 | 原因 |
|------|------|------|
| `automation/reports/` | 旧章节报告 | 旧批次已删除 |
| `automation/pipeline_reports/` | 旧流水线报告 | 旧批次已删除 |
| `automation/quality_reports/` | 旧质量报告 | 旧批次已删除 |
| `automation/validation_reports/` | 旧验证报告 | 旧批次已删除 |
| `automation/chapters/` | 空 | 空 |
| `automation/output/` | 空 | 空 |
| `automation/checkpoints/` | 空 | 空 |
| `automation/beat_sheets/` | beat_sheet文件 | 已整合到Master Outline |

### 保留目录
| 目录 | 内容 | 说明 |
|------|------|------|
| `automation/scripts/` | Python脚本 | 核心脚本保留 |
| `automation/`根目录 | JSON配置文件 | state.json, profiles等 |

---

## 五、.codepilot-uploads清理

### 删除文件
| 文件 | 原因 |
|------|------|
| `1776419392563-Daming1900_Master_Outline.md` | 旧版大纲 |
| `1776442284400-Reference_Text_Library.md` | 重复文件 |
| `1776442476136-Reference_Text_Library.md` | 重复文件 |
| `*.png` | 上传的图片（可选保留） |

---

## 六、最终项目结构

```
DaMing/
├── CLAUDE.md                 # 项目CLAUDE配置
├── README.md                 # 项目说明
├── .gitignore
│
├── docs/                     # 22个核心文档
│   ├── 00-宪法层/           # 4个文件
│   ├── 01-规划层/           # 4个文件（删除2个补丁）
│   ├── 02-执行层/           # 1个文件
│   ├── 03-参考层/           # 3个文件
│   ├── 04-质控层/           # 3个文件
│   ├── 05-写作指南/         # 1个文件
│   ├── 06-参考资料/         # 5个txt
│   └── README.md
│
├── automation/               # 自动化系统
│   ├── scripts/             # Python脚本
│   ├── *.json               # 配置文件（保留）
│   └── *.md                 # 说明文档（保留）
│
├── chapters/                 # 章节目录（空，待写入）
│
├── progress/                 # 进度目录（清空旧内容）
│
└── memory/                   # 记忆系统
```

---

## 执行步骤

1. 删除规划层补丁文件
2. 删除根目录冗余文档
3. 清空progress目录
4. 删除automation子目录中的旧报告
5. 清理.codepilot-uploads重复文件
6. 更新README

---

**准备执行清理？**
