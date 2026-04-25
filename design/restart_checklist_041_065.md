# 第41-65章重启执行清单

> 适用范围：`第41章 - 第65章`
>
> 用途：在重启 `41-65` 写作时，强制把“真实 BCE 写作、字数 gate、章型校验、审校落盘、日志、Telegram、GitHub”逐项打勾，不再依赖口头承诺。

---

## 一、重启总原则

1. `41-65` 必须视为重启重写，不得沿用旧失败产物。
2. 不允许人工代写正文冒充 BCE 写作结果。
3. 任何一章未通过硬 gate，不得进入日志、Telegram、GitHub。
4. 每完成 `5` 章才允许做一次 GitHub 推送。
5. 若 BCE 写作失败，本章停止，不得“先放行再说”。

---

## 二、批次划分

重启时固定按以下 5 章批次推进：

- `041-045`
- `046-050`
- `051-055`
- `056-060`
- `061-065`

每一批都必须先生成共享写作包，再逐章完成完整流水线。

---

## 三、批次启动前检查

### A. 文档真源检查

每一批开始前，必须确认已阅读：

- [ ] `BIBLE.md`
- [ ] `STYLE.md`
- [ ] `OUTLINE.md`
- [ ] `design/chapter_types.json`
- [ ] `design/chapter_policy.md`
- [ ] `PIPELINE.md`

### B. 章节类型检查

本批 5 章必须逐章核对：

- [ ] 本批每章都存在于 `design/chapter_types.json`
- [ ] `chapter_type` 与 `OUTLINE.md` 的实际剧情功能一致
- [ ] `key` 章没有被错误降为 `normal`

### C. 环境检查

- [ ] `./scripts/run_pipeline_preflight.sh` 通过
- [ ] `send_telegram.sh` 可执行
- [ ] BCE 当前 provider 真实为 `BCE`
- [ ] `validate_chapter_gate.py` 可执行

### D. 批次共享包检查

每批开始时必须生成：

- [ ] `context/generated/batch_XXX_YYY/write_pack.md`

并确认其中包含：

- [ ] 本批 5 章总目标
- [ ] 最近状态摘要
- [ ] 本批关键人物音色
- [ ] 禁用规则
- [ ] 本批章型分布说明

---

## 四、单章开写前检查

以某一章 `chapter_0XX` 为例，开写前必须确认：

- [ ] `context/generated/chapter_0XX/chapter_type.md` 已生成
- [ ] `context/generated/chapter_0XX/write_pack.md` 已生成
- [ ] 本章 `chapter_type` 已知
- [ ] 若本章是 `key`，默认模型必须是 `glm-5`
- [ ] 若本章是 `normal`，默认模型必须是 `deepseek-v3.2`

不得出现：

- [ ] 不知道章型就先写
- [ ] 口头临时改章型
- [ ] 为赶进度把 `key` 章按普通章处理

---

## 五、Step 2 写作硬检查

本章 BCE 写作完成后，必须同时存在：

- [ ] `draft/chapter_0XX_draft.md`
- [ ] `context/generated/chapter_0XX/bce_write_meta.json`

并逐项确认：

- [ ] `provider_name = BCE`
- [ ] `model` 存在且符合章型分流
- [ ] 若本章为 `normal`，正文主体汉字数在 `3500-4500`
- [ ] 若本章为 `key`，正文主体汉字数在 `5000-6000`
- [ ] 开头 200 字内进入具体场景
- [ ] 结尾存在明确钩子

### 写作硬失败条件

只要出现以下任一条，本章立刻停止：

- [ ] 没有 `bce_write_meta.json`
- [ ] `provider_name` 不是 `BCE`
- [ ] `normal` 章汉字数 `< 3500`
- [ ] `normal` 章汉字数 `> 4500`
- [ ] `key` 章汉字数 `< 5000`
- [ ] `key` 章汉字数 `> 6000`
- [ ] 明显不是按本章章型对应模型写出

若失败：

- [ ] 不做一致性校对
- [ ] 不做 Codex 二审
- [ ] 不做终检
- [ ] 不回填日志
- [ ] 不发 Telegram
- [ ] 不进 GitHub

---

## 六、Step 3 一致性校对检查

必须落盘：

- [ ] `reviews/consistency/review_bce_consistency_0XX.md`

必须检查：

- [ ] 世界观一致性
- [ ] 人物音色一致性
- [ ] 禁词 / AI 痕迹扫描
- [ ] 钩子评分
- [ ] 最终建议为 `PASS`

若结果不是 `PASS`：

- [ ] 本章返回写作，不得继续放行

---

## 七、Step 4 Codex 二审检查

必须落盘：

- [ ] `reviews/codex/review_codex_0XX.md`

必须检查：

- [ ] 节奏是否单调
- [ ] 段落是否说明腔过重
- [ ] 人物音色是否漂移
- [ ] 场景是否空泛
- [ ] 综合评分 `>= 3/5`

若不满足：

- [ ] 本章返回写作，不得继续放行

---

## 八、Step 5 日志回填检查

必须完成：

- [ ] 终稿保存到 `chapters/chapter_0XX.md`
- [ ] `OUTLINE.md` 日志区新增或覆盖本章唯一条目

日志必须包含：

- [ ] 标题
- [ ] 摘要
- [ ] 谢长庚状态
- [ ] 新增伏笔
- [ ] 评分
- [ ] 模型消耗

若日志缺失：

- [ ] 本章不得进入 Telegram 与 GitHub 放行

---

## 九、Step 6 终检检查

必须落盘：

- [ ] `reviews/final/review_bce_final_0XX.md`

必须检查：

- [ ] 连载感评分 `>= 3/5`
- [ ] 最终结论为 `PASS`
- [ ] 普通章默认终检模型为 `ernie-4.5-turbo-20260402`
- [ ] 关键章默认终检模型为 `glm-5`

若终检不通过：

- [ ] 本章不得进入 Telegram 与 GitHub 放行

---

## 十、Telegram 放行检查

本章只有在以下全部满足时才允许发通知：

- [ ] 写作 gate 通过
- [ ] 一致性校对 `PASS`
- [ ] Codex 二审通过
- [ ] 终检 `PASS`
- [ ] `OUTLINE.md` 日志已更新

发送后必须确认：

- [ ] Telegram 脚本返回成功

若 Telegram 失败：

- [ ] 记为异常
- [ ] 本批推送前必须补发成功

---

## 十一、GitHub 放行检查

每一批 `5` 章结束后，才允许推送。

本批推送前必须全部满足：

- [ ] 本批 5 章正文齐全
- [ ] 本批 5 章草稿齐全
- [ ] 本批 5 章三轮审校文件齐全
- [ ] 本批 5 章日志已回填
- [ ] 本批 Telegram 已全部成功

若有任一章仍未满足：

- [ ] 不得推 GitHub

---

## 十二、批次结束后抽查

每批结束后至少抽查两章：

### 抽查项

- [ ] `chapter_type` 是否正确进入上下文包
- [ ] 写作模型是否与章型一致
- [ ] `normal` 章字数是否在 `3500-4500`
- [ ] `key` 章字数是否在 `5000-6000`
- [ ] 关键人物音色是否稳定
- [ ] 本章是否真配得上当前 `chapter_type`

建议抽查方式：

- 每批抽 `1` 章 `normal`
- 每批抽 `1` 章 `key`

---

## 十三、41-65 重启时的强制提醒

以下行为一律禁止：

- [ ] 为了不断更，先人工补正文再补流程
- [ ] BCE 没写出来，却继续走审校
- [ ] 字数不达标仍然放行
- [ ] Telegram / GitHub 先发先推，后面再补质量
- [ ] 口头说“这章算关键章”，却不改 `chapter_types.json`

重启 `41-65` 的目标不是“尽快补回来”，而是：

- **把第 40 章以前的质量线重新建立起来**
- **把后续 100-400 章能长期稳定执行的流程真正跑通**
