#!/usr/bin/env python3
"""
合并6个Agent的调研结果，生成Phase 1.5调研Review检查点的摘要表格。
扫描 references/research/ 目录下的01-06 md文件，统计每个维度的来源数量、
一手/二手占比、关键发现。

用法:
    python3 merge_research.py <skill目录路径>

示例:
    python3 merge_research.py .claude/skills/elon-musk-skill

输出: 打印markdown格式的摘要表格到stdout
"""

import sys
import re
from pathlib import Path

AGENTS = {
    '01-writings': '著作',
    '02-conversations': '对话',
    '03-expression-dna': '表达',
    '04-external-views': '他者',
    '05-decisions': '决策',
    '06-timeline': '时间线',
}


def count_sources(content):
    """统计来源数量和一手/二手占比"""
    # 计算URL数量作为来源数
    urls = re.findall(r'https?://[^\s\)]+', content)

    # 检测一手/二手标记
    primary_markers = len(re.findall(r'一手|primary|本人|原文|原始|直接引用', content, re.IGNORECASE))
    secondary_markers = len(re.findall(r'二手|secondary|转述|总结|评论|分析', content, re.IGNORECASE))

    return {
        'url_count': len(urls),
        'unique_urls': len(set(urls)),
        'primary_markers': primary_markers,
        'secondary_markers': secondary_markers,
    }


def extract_key_findings(content, max_items=3):
    """提取关键发现（取前几个二级标题或加粗项）"""
    # 尝试提取##标题
    headings = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
    if headings:
        return headings[:max_items]

    # fallback: 提取加粗项
    bolds = re.findall(r'\*\*(.+?)\*\*', content)
    if bolds:
        return bolds[:max_items]

    # fallback: 取前3个非空行
    lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
    return [l[:50] + '...' if len(l) > 50 else l for l in lines[:max_items]]


def find_contradictions(files):
    """简单检测跨文件矛盾（同一关键词出现不同判断）"""
    contradictions = []
    # 检测「但是」「然而」「相反」「矛盾」等矛盾标记
    for name, content in files.items():
        matches = re.findall(r'(?:矛盾|相反|但实际上|然而.*?不同|争议).{0,100}', content)
        for m in matches:
            contradictions.append("{}: {}".format(AGENTS.get(name, name), m[:80]))
    return contradictions[:5]  # 最多5条


def main():
    if len(sys.argv) < 2:
        print("用法: python3 merge_research.py <skill目录路径>")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    research_dir = skill_dir / 'references' / 'research'

    if not research_dir.exists():
        print("❌ 目录不存在: {}".format(research_dir))
        sys.exit(1)

    files = {}
    rows = []
    total_sources = 0
    total_primary = 0
    total_secondary = 0
    missing = []

    for key, label in AGENTS.items():
        md_file = research_dir / "{}.md".format(key)
        if not md_file.exists():
            missing.append(label)
            rows.append("│ {label:<12} │ {missing:<8} │ {empty:<24} │".format(
                label=label, missing='❌ 缺失', empty='—'))
            continue

        content = md_file.read_text(encoding='utf-8')
        files[key] = content
        stats = count_sources(content)
        findings = extract_key_findings(content)

        total_sources += stats['unique_urls']
        total_primary += stats['primary_markers']
        total_secondary += stats['secondary_markers']

        findings_str = ', '.join(findings) if findings else '—'
        if len(findings_str) > 40:
            findings_str = findings_str[:37] + '...'

        rows.append("│ {label:<12} │ {count:<8} │ {findings:<24} │".format(
            label=label, count=stats['unique_urls'], findings=findings_str))

    # 矛盾检测
    contradictions = find_contradictions(files)

    # 输出
    print("┌──────────────┬──────────┬──────────────────────────┐")
    print("│ Agent        │ 来源数量  │ 关键发现                  │")
    print("├──────────────┼──────────┼──────────────────────────┤")
    for row in rows:
        print(row)
    print("├──────────────┼──────────┼──────────────────────────┤")

    primary_ratio = "{}/{}".format(total_primary, total_primary + total_secondary) if (total_primary + total_secondary) > 0 else "未标记"
    print("│ 总来源数      │ {total:<8} │ 一手占比: {ratio:<15} │".format(
        total=total_sources, ratio=primary_ratio))

    if contradictions:
        print("│ 矛盾点        │ {count}处      │ {text:<24} │".format(
            count=len(contradictions), text=contradictions[0][:24]))
    else:
        print("│ 矛盾点        │ 0处      │ {empty:<24} │".format(empty='—'))

    if missing:
        print("│ 信息不足维度   │ {count}个      │ {text:<24} │".format(
            count=len(missing), text=', '.join(missing)))
    else:
        print("│ 信息不足维度   │ 无       │ {empty:<24} │".format(empty='—'))

    print("└──────────────┴──────────┴──────────────────────────┘")

    # 总结
    if total_sources < 10:
        print("\n⚠️ 总来源数 <10，建议降低期望或补充调研")
    if missing:
        print("\n⚠️ 缺失维度: {}，建议补充或在诚实边界中标注".format(', '.join(missing)))


if __name__ == '__main__':
    main()
