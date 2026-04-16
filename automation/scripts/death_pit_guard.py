#!/usr/bin/env python3
"""
《大明1900》防死穴系统 v3.0
防止六大死穴：人物同质化、多线脱钩、章节注水、文体漂移、后期疲劳、情感缺失
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set

PROJECT_ROOT = Path(__file__).parent.parent.parent
AUTOMATION_DIR = PROJECT_ROOT / "automation"
VOICE_PROFILES_FILE = AUTOMATION_DIR / "character_voice_profiles.json"
FORESHADOWING_FILE = AUTOMATION_DIR / "foreshadowing_ledger.json"
STATE_FILE = AUTOMATION_DIR / "state.json"

class DeathPitGuard:
    """防死穴系统 - 守护长篇小说的生命线"""

    def __init__(self):
        self.voice_profiles = self.load_json(VOICE_PROFILES_FILE)
        self.foreshadowing = self.load_json(FORESHADOWING_FILE)
        self.state = self.load_json(STATE_FILE)

        # 禁用词库（防止分析腔/文体漂移）
        self.banned_phrases = [
            "由此可见", "从叙事角度", "这体现了", "可以看作",
            "综上所述", "总而言之", "不难看出", "值得注意的是",
            "这表明了", "这反映了", "从某种意义上说", "可以说",
            "显然", "毫无疑问", "不可否认", "客观地说"
        ]

        # 高张力词汇（防止后期平淡化）
        self.high_tension_keywords = [
            "死", "杀", "血", "炸", "碎", "断", "燃", "爆"
        ]

    def load_json(self, file_path: Path) -> dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # ==================== 死穴1：人物同质化检测 ====================

    def check_character_homogenization(self, chapter_content: str, chapter_num: int) -> List[str]:
        """检查人物是否同质化"""
        errors = []

        # 提取所有对话
        dialogues = self._extract_dialogues(chapter_content)

        # 检查每个人物的对话是否符合其语言特征
        for char_name, char_profile in self.voice_profiles.items():
            if char_name == "说明" or char_name == "验证规则":
                continue

            if char_name in dialogues:
                char_dialogues = dialogues[char_name]

                # 检查句式长度
                avg_length = sum(len(d) for d in char_dialogues) / len(char_dialogues)
                expected_length = char_profile.get("语言特征", {}).get("平均句长", "10-15字")

                # 简化版本，实际需要更复杂的分析
                if avg_length > 30:
                    errors.append(
                        f"⚠️ 第{chapter_num}章：{char_name}平均句长{avg_length:.1f}字，"
                        f"预期{expected_length}，可能同质化"
                    )

                # 检查禁用台词
                for dialogue in char_dialogues:
                    if "禁用台词" in char_profile:
                        for banned in char_profile["禁用台词"]:
                            if banned in dialogue:
                                errors.append(
                                    f"❌ 第{chapter_num}章：{char_name}使用了禁用台词「{banned}」"
                                )

        return errors

    def _extract_dialogues(self, content: str) -> Dict[str, List[str]]:
        """提取对话（简化版本）"""
        dialogues = {}
        # 简化：假设对话格式为"XXX说：..."
        # 实际需要更复杂的NLP分析
        pattern = r'([^\s]+)说[：:](.+?)(?=[^\s]+说[：:]|$)'
        matches = re.findall(pattern, content)

        for char_name, dialogue in matches:
            if char_name not in dialogues:
                dialogues[char_name] = []
            dialogues[char_name].append(dialogue.strip())

        return dialogues

    # ==================== 死穴2：多线脱钩检测 ====================

    def check_plot_decoupling(self, chapter_num: int) -> List[str]:
        """检查多线是否脱钩"""
        errors = []

        # 检查伏笔进展
        foreshadowing_state = self.foreshadowing["主线追踪"]["三帝纪"]

        for arc_name, arc_data in foreshadowing_state.items():
            for foreshadow in arc_data.get("关键伏笔", []):
                foreshadow_id = foreshadow["ID"]
                plant_chapter = foreshadow["章节"]
                target_chapter = foreshadow["回收章节"]
                status = foreshadow["状态"]

                # 检查是否超期未回收
                if chapter_num > target_chapter and status == "待回收":
                    errors.append(
                        f"❌ 第{chapter_num}章：伏笔{foreshadow_id}应在第{target_chapter}章回收，"
                        f"现已超期{chapter_num - target_chapter}章"
                    )

                # 检查是否有进展（每10章应该有进展）
                if chapter_num - plant_chapter >= 10 and chapter_num % 10 == 0:
                    if status == "待回收":
                        errors.append(
                            f"⚠️ 第{chapter_num}章：伏笔{foreshadow_id}已埋下{chapter_num - plant_chapter}章，"
                            f"但无进展记录"
                        )

        return errors

    # ==================== 死穴3：章节注水检测 ====================

    def check_chapter_water(self, chapter_content: str, chapter_num: int) -> List[str]:
        """检查章节是否注水"""
        errors = []

        # 1. 检查核心冲突推进
        has_conflict = any(kw in chapter_content for kw in
            ["冲突", "对抗", "战斗", "决定", "发现", "揭露", "死亡"])

        if not has_conflict:
            errors.append(
                f"⚠️ 第{chapter_num}章：未检测到核心冲突推进，可能为过场填充"
            )

        # 2. 检查动作描写占比
        action_keywords = ["走", "跑", "拿", "打", "砸", "看", "听", "说"]
        action_count = sum(chapter_content.count(kw) for kw in action_keywords)
        total_words = len(chapter_content)

        if total_words > 1000 and action_count / total_words < 0.05:
            errors.append(
                f"⚠️ 第{chapter_num}章：动作描写占比{action_count/total_words*100:.1f}%，"
                f"可能过于静态（注水嫌疑）"
            )

        # 3. 检查对话占比（过多对话也是注水）
        dialogue_pattern = r'[""「」](.+?)[""「」"]'
        dialogues = re.findall(dialogue_pattern, chapter_content)
        dialogue_ratio = len(''.join(dialogues)) / total_words if total_words > 0 else 0

        if dialogue_ratio > 0.7:
            errors.append(
                f"⚠️ 第{chapter_num}章：对话占比{dialogue_ratio*100:.1f}%，"
                f"可能过于对话流（注水嫌疑）"
            )

        return errors

    # ==================== 死穴4：文体漂移检测 ====================

    def check_style_drift(self, chapter_content: str, chapter_num: int) -> List[str]:
        """检查是否有分析腔/文体漂移"""
        errors = []

        for phrase in self.banned_phrases:
            if phrase in chapter_content:
                # 找到具体位置
                pos = chapter_content.find(phrase)
                context = chapter_content[max(0, pos-20):pos+len(phrase)+20]

                errors.append(
                    f"❌ 第{chapter_num}章：检测到分析腔「{phrase}」\n"
                    f"   上下文：...{context}..."
                )

        return errors

    # ==================== 死穴5：后期疲劳检测 ====================

    def check_fatigue(self, chapter_content: str, chapter_num: int, prev_chapters: List[str]) -> List[str]:
        """检查后期是否平淡化"""
        errors = []

        if chapter_num < 50:
            return errors  # 只检测后期

        # 1. 检查高张力词汇密度
        tension_count = sum(chapter_content.count(kw) for kw in self.high_tension_keywords)
        word_count = len(chapter_content)
        tension_ratio = tension_count / word_count if word_count > 0 else 0

        # 对比前期的平均张力
        if prev_chapters:
            early_tension_ratios = []
            for early_chapter in prev_chapters[:10]:  # 前10章
                early_tension = sum(early_chapter.count(kw) for kw in self.high_tension_keywords)
                early_ratio = early_tension / len(early_chapter) if len(early_chapter) > 0 else 0
                early_tension_ratios.append(early_ratio)

            avg_early_tension = sum(early_tension_ratios) / len(early_tension_ratios)

            if tension_ratio < avg_early_tension * 0.5:
                errors.append(
                    f"⚠️ 第{chapter_num}章：张力密度{tension_ratio*100:.2f}%，"
                    f"前期平均{avg_early_tension*100:.2f}%，下降{(1-tension_ratio/avg_early_tension)*100:.1f}%，"
                    f"可能为后期疲劳"
                )

        # 2. 检查细节密度（形容词、副词数量）
        adj_count = len(re.findall(r'的|地|得', chapter_content))
        adj_ratio = adj_count / word_count if word_count > 0 else 0

        if adj_ratio < 0.02:
            errors.append(
                f"⚠️ 第{chapter_num}章：细节密度{adj_ratio*100:.2f}%，"
                f"可能过于简略（后期疲劳）"
            )

        return errors

    # ==================== 死穴6：情感缺失检测 ====================

    def check_emotional_void(self, chapter_content: str, chapter_num: int) -> List[str]:
        """检查是否缺乏情感共鸣"""
        errors = []

        # 1. 检查是否有"情感高潮"场景标记
        emotional_markers = [
            "泪", "哭", "笑", "颤抖", "拥抱", "跪下", "嘶吼", "沉默"
        ]

        has_emotional_scene = any(marker in chapter_content for marker in emotional_markers)

        # 2. 检查关键时刻是否有情感爆发
        if chapter_num in [3, 50, 95, 100, 150, 200]:  # 关键章节
            if not has_emotional_scene:
                errors.append(
                    f"⚠️ 第{chapter_num}章：关键章节但未检测到情感高潮场景"
                )

        # 3. 检查人物是否有内心挣扎
        struggle_markers = ["犹豫", "挣扎", "矛盾", "选择", "决定"]
        has_struggle = any(marker in chapter_content for marker in struggle_markers)

        # 每10章至少应该有一次内心挣扎
        if chapter_num % 10 == 0 and not has_struggle:
            errors.append(
                f"⚠️ 第{chapter_num}章：检测节点章节但无内心挣扎描写，可能缺乏人性深度"
            )

        return errors

    # ==================== 综合检测 ====================

    def full_check(self, chapter_content: str, chapter_num: int, prev_chapters: List[str] = None) -> Dict[str, List[str]]:
        """执行全部六大死穴检测"""
        results = {
            "人物同质化": self.check_character_homogenization(chapter_content, chapter_num),
            "多线脱钩": self.check_plot_decoupling(chapter_num),
            "章节注水": self.check_chapter_water(chapter_content, chapter_num),
            "文体漂移": self.check_style_drift(chapter_content, chapter_num),
            "后期疲劳": self.check_fatigue(chapter_content, chapter_num, prev_chapters or []),
            "情感缺失": self.check_emotional_void(chapter_content, chapter_num)
        }

        return results

    def generate_report(self, results: Dict[str, List[str]], chapter_num: int) -> str:
        """生成检测报告"""
        report = f"""
## 第{chapter_num}章防死穴检测报告

"""

        total_errors = 0
        for pit_name, errors in results.items():
            if errors:
                total_errors += len(errors)
                report += f"### {pit_name}\n"
                for error in errors:
                    report += f"{error}\n"
                report += "\n"

        if total_errors == 0:
            report += "✅ 未检测到死穴问题\n"
        else:
            report += f"❌ 共发现{total_errors}个问题\n"

        return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description='防死穴系统 v3.0')
    parser.add_argument('--check', type=str, help='检查指定章节文件')
    parser.add_argument('--chapter', type=int, help='章节编号')

    args = parser.parse_args()
    guard = DeathPitGuard()

    if args.check and args.chapter:
        with open(args.check, 'r', encoding='utf-8') as f:
            content = f.read()

        results = guard.full_check(content, args.chapter)
        print(guard.generate_report(results, args.chapter))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
