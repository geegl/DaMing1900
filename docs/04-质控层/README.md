# 质控层文档索引

## 保留的核心文档

| 文档 | 说明 | 用途 |
|------|------|------|
| `Daming1900_Engine_Rules.md` | 引擎规则 | 写作引擎核心规则 |
| `Writing_Guide.md` | 写作指南 | 已移至`05-写作指南/` |

## 已归档的历史文档

以下文档已整合到`05-写作指南/Writing_Guide.md`：

- `front-10-chapters-critical-diagnosis.md` → 质检失效教训
- `front-50-chapters-reconstruction.md` → 篇幅塌陷教训
- `chapter-11-20-tech-design.md` → 技术代差设定
- `logic-patches-v2.md` → 逻辑漏洞预防
- `rust-remover-mechanism-design.md` → 感官设定

## 清理原则

1. **保留核心规则文档**
2. **整合教训类文档**到写作指南
3. **删除重复报告**和临时补丁

---

**建议操作**：

```bash
# 删除冗余文件
rm /Users/roven/Documents/Trae/DaMing/docs/04-质控层/front-*-inspection*.md
rm /Users/roven/Documents/Trae/DaMing/docs/04-质控层/chapter-*-design.md
rm /Users/roven/Documents/Trae/DaMing/docs/04-质控层/batch-*.md
rm /Users/roven/Documents/Trae/DaMing/docs/04-质控层/option-*.md
rm /Users/roven/Documents/Trae/DaMing/docs/04-质控层/*-fixes.md
```
