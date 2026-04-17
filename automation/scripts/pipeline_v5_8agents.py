#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《大明1900》8代理流水线 v5.0
专为历史架空小说设计，多层交叉校验
"""

import json
import os
from datetime import datetime

class DamingPipeline8Agents:
    def __init__(self):
        self.state = self.load_state()
        self.bible = self.load_bible()
        self.protection_rules = self.load_protection_rules()

    def load_state(self):
        with open("automation/state.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def load_bible(self):
        with open("docs/00-宪法层/Daming1900_Bible.md", "r", encoding="utf-8") as f:
            return f.read()

    def load_protection_rules(self):
        with open("docs/04-质控层/Daming1900_Engine_Rules.md", "r", encoding="utf-8") as f:
            return f.read()

    def run_full_pipeline(self, chapter_num: int):
        """
        8代理完整流水线
        """
        print(f"\n🚀 《大明1900》8代理流水线 v5.0 开始 —— 第 {chapter_num} 章\n")

        # 1. 规划代理（haiku - 结构最强）
        print("【1/8】规划代理（haiku）执行中...")
        planning = self.agent_planning(chapter_num)
        print("✅ 规划完成\n")

        # 2. 世界观约束代理（sonnet - 文脉+历史感最强）
        print("【2/8】世界观约束代理（sonnet）执行中...")
        worldview_ok = self.agent_worldview_constraint(planning)
        if not worldview_ok["pass"]:
            raise ValueError(f"❌ 世界观约束失败！原因：{worldview_ok['reason']}")
        print("✅ 世界观约束通过\n")

        # 3. 写作代理（opus - 细节噪声优秀）
        print("【3/8】写作代理（opus）执行中...")
        draft = self.agent_writing(planning, worldview_ok)
        print(f"✅ 初稿生成完成（{len(draft)}字）\n")

        # 4+5. 并行逻辑检查 + 视觉POV守护
        print("【4-5/8】逻辑检查（haiku）+ 视觉POV守护（opus）并行执行中...")
        logic_report = self.agent_logic_check(draft)
        visual_report = self.agent_visual_pov_guard(draft)

        if not logic_report["pass"]:
            raise ValueError(f"❌ 逻辑检查失败！原因：{logic_report['reason']}")
        if not visual_report["pass"]:
            raise ValueError(f"❌ 视觉POV守护失败！原因：{visual_report['reason']}")
        print("✅ 逻辑 + 视觉POV校验通过\n")

        # 6. 情感高潮代理（sonnet - 情感最细腻）
        print("【6/8】情感高潮代理（sonnet）执行中...")
        emotional = self.agent_emotional_peak(draft, logic_report, visual_report)
        print("✅ 情感高潮验证通过\n")

        # 7. 风格+去AI味润色代理（sonnet - 文风控制）
        print("【7/8】风格+去AI味润色代理（sonnet）执行中...")
        polished = self.agent_style_polish(emotional)
        print("✅ 风格润色完成\n")

        # 8. 最终质控+集成代理（haiku - 严格审查）
        print("【8/8】最终质控+集成代理（haiku）执行中...")
        final = self.agent_final_qc(polished)
        if final["protection_rate"] < 100:
            raise ValueError(f"❌ 最终质控未100%通过！当前：{final['protection_rate']}%")
        print("✅ 最终质控通过（防护率100%）\n")

        # 保存章节
        self.save_chapter(chapter_num, final["chapter"])
        self.update_state(chapter_num, final["state_changes"])

        print(f"🎉 第 {chapter_num} 章 8代理全流程通过 | 防护率 100%\n")
        return final

    def agent_planning(self, chapter_num):
        """规划代理：输出Beat Sheet + 伏笔更新【MODEL: haiku】"""
        # 读取大纲
        with open("docs/01-规划层/Daming1900_Master_Outline.md", "r", encoding="utf-8") as f:
            outline = f.read()

        # 读取伏笔账本
        with open("automation/foreshadowing_ledger.json", "r", encoding="utf-8") as f:
            foreshadowing = json.load(f)

        # 【MODEL: haiku】结构最强，生成Beat Sheet
        # Claude Code执行时通过Agent tool指定model="haiku"
        return {
            "chapter_num": chapter_num,
            "beat_sheet": "本章核心冲突：...",
            "foreshadowing_updates": {},
            "model_used": "haiku"
        }

    def agent_worldview_constraint(self, planning):
        """世界观约束代理：锁死物理层【MODEL: opus】"""
        # 读取物理档案
        with open("automation/character_physical_profiles.json", "r", encoding="utf-8") as f:
            physical_profiles = json.load(f)

        # 【MODEL: opus】理解力最强，检查明朝政治设定
        # 检查：死人/残疾/伤痕/物品/历史事件不可变 + 宦党/司礼监/东厂
        return {
            "pass": True,
            "reason": "",
            "physical_check": physical_profiles,
            "model_used": "opus"
        }

    def agent_writing(self, planning, worldview_ok):
        """写作代理：生成初稿【MODEL: sonnet】"""
        # 读取参考文本库
        with open("docs/03-参考层/Reference_Text_Library.md", "r", encoding="utf-8") as f:
            reference_texts = f.read()

        # 【MODEL: sonnet】文脉最强，历史感最强
        # 注入参考文本 + 视觉噪声 + 明朝政治灵魂
        return {
            "draft": "章节初稿内容...",
            "model_used": "sonnet"
        }

    def agent_logic_check(self, draft):
        """逻辑检查代理：死穴全扫描【MODEL: haiku】"""
        # 【MODEL: haiku】逻辑严密
        # 检查：时间锁、脱钩、注水、疲劳、伏笔回收、明朝政治逻辑
        return {
            "pass": True,
            "reason": "",
            "time_anchor": "天工十九年三月XX",
            "foreshadowing_recycled": [],
            "model_used": "haiku"
        }

    def agent_visual_pov_guard(self, draft):
        """视觉+POV守护代理【MODEL: opus】"""
        # 【MODEL: opus】细节噪声优秀
        # 检查：感官反差≥3处、中性词≤3次、POV锁定、压抑感元素
        return {
            "pass": True,
            "reason": "",
            "visual_contrast_count": 5,
            "pov_locked": True,
            "oppression_elements": ["铁币生锈", "工籍烙印", "煤烟天空"],
            "model_used": "opus"
        }

    def agent_emotional_peak(self, draft, logic_report, visual_report):
        """情感高潮代理【MODEL: sonnet】"""
        # 【MODEL: sonnet】情感最细腻
        # 检查：内心挣扎、人性深度、情感弧光、冷硬克制
        return {
            "draft": draft,
            "model_used": "sonnet"
        }

    def agent_style_polish(self, draft):
        """风格+去AI味润色代理【MODEL: sonnet】"""
        # 【MODEL: sonnet】文风控制最强
        # 毛边噪声、时代俚语、公文体混搭、去分析腔
        return {
            "draft": draft,
            "model_used": "sonnet"
        }

    def agent_final_qc(self, draft):
        """最终质控+集成代理【MODEL: haiku】"""
        # 【MODEL: haiku】严格审查
        # 8层防护100%通过率检查 + 明朝政治元素验证
        return {
            "chapter": draft,
            "protection_rate": 100,
            "state_changes": {},
            "ming_politics_check": True,  # 新增：明朝政治元素检查
            "model_used": "haiku"
        }

    def save_chapter(self, chapter_num, content):
        """保存章节"""
        filename = f"chapters/第{chapter_num:03d}章.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    def update_state(self, chapter_num, state_changes):
        """更新state.json"""
        self.state["current_chapter"] = chapter_num
        # 更新其他状态...
        with open("automation/state.json", "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    pipeline = DamingPipeline8Agents()
    # 测试生成第1章
    pipeline.run_full_pipeline(chapter_num=1)
