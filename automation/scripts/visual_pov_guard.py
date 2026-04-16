#!/usr/bin/env python3
"""
《大明1900》视觉层面+视角层面防护系统
防止视觉降噪 + POV死锁
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent
AUTOMATION_DIR = PROJECT_ROOT / "automation"
VISUAL_NOISE_FILE = AUTOMATION_DIR / "visual_noise_library.json"
POV_LOCK_FILE = AUTOMATION_DIR / "pov_lock_system.json"

class VisualPOVGuard:
    """视觉层面+视角层面防护"""

    def __init__(self):
        self.visual_noise = self.load_json(VISUAL_NOISE_FILE)
        self.pov_lock = self.load_json(POV_LOCK_FILE)

        # 中性平滑词
        self.neutral_words = ["微微", "淡淡", "隐约", "似乎", "仿佛", "略显"]

    def load_json(self, file_path: Path) -> dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # ==================== 视觉降噪检测 ====================

    def check_visual_noise(self, chapter_content: str, chapter_num: int) -> List[str]:
        """检查是否有视觉降噪（AI把描写磨平）"""
        errors = []

        # 1. 检查中性平滑词
        for word in self.neutral_words:
            count = chapter_content.count(word)
            if count > 3:
                errors.append(
                    f"⚠️ 第{chapter_num}章：中性词「{word}」出现{count}次，超过上限3次"
                )

        # 2. 检查感官反差
        sensory_contrast_count = self._count_sensory_contrast(chapter_content)
        if sensory_contrast_count < 3:
            errors.append(
                f"⚠️ 第{chapter_num}章：感官反差仅{sensory_contrast_count}处，"
                f"需要至少3处（脏/乱/血腥 vs 精致/华丽/庄严）"
            )

        # 3. 检查时代噪声
        era_noise_count = self._count_era_noise(chapter_content)
        if era_noise_count < 5:
            errors.append(
                f"⚠️ 第{chapter_num}章：时代噪声仅{era_noise_count}处，"
                f"需要至少5处（方言、俚语、时代特有词汇）"
            )

        # 4. 检查视觉瑕疵（破格句）
        irregular_count = self._count_irregular_sentences(chapter_content)
        word_count = len(chapter_content)
        irregular_ratio = irregular_count / max(word_count / 20, 1)  # 粗略估计

        if irregular_ratio < 0.05:
            errors.append(
                f"⚠️ 第{chapter_num}章：破格句占比{irregular_ratio*100:.1f}%，"
                f"建议5-8%以增加毛边感"
            )

        return errors

    def _count_sensory_contrast(self, content: str) -> int:
        """计算感官反差数量"""
        # 简化版本：检查是否同时出现脏乱词汇和精致词汇
        dirty_words = ["脏", "乱", "血", "腥", "臭", "锈", "污", "煤", "油"]
        refined_words = ["精致", "华丽", "庄严", "丝绸", "檀香", "抛光"]

        dirty_count = sum(content.count(w) for w in dirty_words)
        refined_count = sum(content.count(w) for w in refined_words)

        # 如果同时出现两种词汇，算一次反差
        return min(dirty_count, refined_count)

    def _count_era_noise(self, content: str) -> int:
        """计算时代噪声数量"""
        # 晚清/晚明特有词汇
        era_words = [
            "兹有", "查办", "相应", "合行", "切切",  # 公文体
            "话说", "且说", "看官", "后话",  # 说书味
            "机器局", "制造局", "洋行", "买办", "海关银"  # 洋务新名词
        ]

        return sum(content.count(w) for w in era_words)

    def _count_irregular_sentences(self, content: str) -> int:
        """计算破格句数量"""
        # 简化版本：检查短句、重复、断句
        sentences = re.split(r'[。！？]', content)

        irregular_count = 0
        for i, s in enumerate(sentences):
            # 1. 极短句（<5字）
            if len(s.strip()) < 5 and len(s.strip()) > 0:
                irregular_count += 1
            # 2. 重复句（连续两句相同或相似）
            if i > 0 and s.strip() == sentences[i-1].strip():
                irregular_count += 1

        return irregular_count

    # ==================== POV死锁检测 ====================

    def check_pov_violation(self, chapter_content: str, chapter_num: int, declared_pov: str) -> List[str]:
        """检查是否违反POV锁定"""
        errors = []

        # 1. 检查是否声明视角
        if not declared_pov:
            errors.append(
                f"❌ 第{chapter_num}章：未声明视角角色，必须在章节开头声明"
            )
            return errors

        # 2. 检查是否允许该视角
        pov_table = self.pov_lock["POV分配表"]

        # 确定当前章节范围
        if chapter_num <= 30:
            allowed_povs = pov_table["第1-30章"]["主视角"]
        elif chapter_num <= 70:
            allowed_povs = pov_table["第31-70章"]["主视角"]
        elif chapter_num <= 155:
            allowed_povs = pov_table["第71-155章"]["主视角"]
        else:
            allowed_povs = pov_table["第156-220章"]["主视角"]

        if declared_pov not in allowed_povs:
            errors.append(
                f"❌ 第{chapter_num}章：视角角色「{declared_pov}」不在允许列表中\n"
                f"   允许视角：{', '.join(allowed_povs)}"
            )

        # 3. 检查上帝视角标记
        god_view_markers = self.pov_lock["违规检测"]["上帝视角标记"]
        for marker in god_view_markers:
            if marker in chapter_content:
                errors.append(
                    f"❌ 第{chapter_num}章：检测到上帝视角标记「{marker}」"
                )

        # 4. 检查视角跳跃标记
        jump_markers = self.pov_lock["违规检测"]["视角跳跃标记"]
        for marker in jump_markers:
            if marker in chapter_content:
                # 检查是否有明确分隔符
                if "***" not in chapter_content:
                    errors.append(
                        f"⚠️ 第{chapter_num}章：检测到视角跳跃标记「{marker}」，"
                        f"但无明确分隔符（***）"
                    )

        # 5. 检查心理描写越界
        # 简化版本：检查是否描写了非视角角色的内心
        # 实际需要更复杂的NLP分析

        return errors

    # ==================== 综合检测 ====================

    def full_check(self, chapter_content: str, chapter_num: int, declared_pov: str = None) -> Dict[str, List[str]]:
        """执行视觉+视角双重检测"""
        results = {
            "视觉降噪": self.check_visual_noise(chapter_content, chapter_num),
            "POV死锁": self.check_pov_violation(chapter_content, chapter_num, declared_pov)
        }

        return results

    def generate_report(self, results: Dict[str, List[str]], chapter_num: int) -> str:
        """生成检测报告"""
        report = f"""
## 第{chapter_num}章视觉+视角层面检测报告

"""

        total_errors = 0
        for check_name, errors in results.items():
            if errors:
                total_errors += len(errors)
                report += f"### {check_name}\n"
                for error in errors:
                    report += f"{error}\n"
                report += "\n"

        if total_errors == 0:
            report += "✅ 未检测到视觉降噪或POV违规问题\n"
        else:
            report += f"❌ 共发现{total_errors}个问题\n"

        return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description='视觉+视角层面防护系统')
    parser.add_argument('--check', type=str, help='检查指定章节文件')
    parser.add_argument('--chapter', type=int, help='章节编号')
    parser.add_argument('--pov', type=str, help='声明的视角角色')

    args = parser.parse_args()
    guard = VisualPOVGuard()

    if args.check and args.chapter:
        with open(args.check, 'r', encoding='utf-8') as f:
            content = f.read()

        results = guard.full_check(content, args.chapter, args.pov)
        print(guard.generate_report(results, args.chapter))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
