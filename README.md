# Academic Reference Inserter

> **Insert, format, and cross-reference academic citations in Word documents.**  
> Supports Chinese (GB/T 7714-2015) and international (IEEE, APA 7th, Chicago, MLA, Harvard) standards.

[![Version](https://img.shields.io/badge/Release-v1.0.1-brightgreen)](#changelog)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 📖 **最新版本**: v1.0.1 — 更新于 2026-05-28

---

## Changelog

### v1.0.1 (2026-05-28)

#### ✨ 功能增强

**引用状态检查**——新增 `check-refs` 命令，自动检查论文中所有参考文献的引用状态。智能检测参考文献章节边界（含标题缺失时的降级方案 `find_reference_boundary_robust()`），逐条显示引用出现位置及上下文（`find_citation_occurrences()`），支持 `--report` 参数导出检查报告和 JSON 格式输出。

**自动搜索参考文献**——新增 `auto-find` 命令，通过 CrossRef API 自动搜索并插入参考文献。自动提取论文标题/关键词，交互式选择搜索结果（支持编号范围、`all`、`none`），自动去重（按 DOI 和标题匹配），插入后自动重排编号。

**工具函数增强**——新增 `find_reference_boundary_robust()`（鲁棒的引用边界检测）、`find_citation_occurrences()`（引用出现位置定位）、`extract_citation_content()`（引用编号解析）。引用边界检测鲁棒性提升。

#### 🐛 漏洞修复

**超链接样式**——由蓝色+下划线改为黑色上标（继承文档字体颜色，无下划线）。将 `superscript` 和 `color` 参数添加到 `make_hyperlink_element()`。

**重复超链接**——`replace_citation_with_hyperlink` 现在只处理 `<w:p>` 的直接子节点 `<w:r>`，跳过现有 `<w:hyperlink>` 元素内的 run。防止嵌套超链接导致视觉重复 `[1][1]`。

**级联重排错误**——`cmd_reorder` 使用单次顺序替换，导致级联导致 25 个引用编号中的 12 个损坏。采用两相替换修复（临时标记 → 最终编号）。`[25]→[7]→[8]→...→[25]`

**参考文献部分超链接**——`cmd_hyperlink` 现在正确跳过参考文献部分，防止参考文献条目出现虚假超链接。

**邻近引用删除**——新增 `dedup_adjacent_citations()` 在创建超链接前折叠正文 `[1][1][1]` → `[1]`。

### v1.0.0 (2026-05-29)

**初始发布功能:**

- 多格式引文支持（GB/T 7714、IEEE、APA、Chicago、MLA、Harvard）
- DOI 自动获取（通过 CrossRef API）
- BibTeX 导入/导出
- 完整流水线：分析 → 格式化 → 重排 → 超链接 → 验证
- 交互式控制台 CLI 模式
- Word 文档交叉引用超链接
- 验证检查（孤立引用、顺序、时效性、重复）
- 修改前自动备份

---

> 详细文档见 [.trae/skills/academic-ref-inserter/README.md](.trae/skills/academic-ref-inserter/README.md)
