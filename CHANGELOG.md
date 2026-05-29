# 更新日志 / Changelog

## [1.0.1] - 2026-05-28

### 🐛 漏洞修复

**超链接样式**——由蓝色+下划线改为黑色上标（继承文档字体颜色，无下划线）。将 `superscript` 和 `color` 参数添加到 `make_hyperlink_element()`。

**重复超链接**——`replace_citation_with_hyperlink` 现在只处理 `<w:p>` 的直接子节点 `<w:r>`，跳过现有 `<w:hyperlink>` 元素内的 run。防止嵌套超链接导致视觉重复 `[1][1]`。

**级联重排错误**——`cmd_reorder` 使用单次顺序替换，导致级联导致 25 个引用编号中的 12 个损坏。采用两相替换修复（临时标记 → 最终编号）。`[25]→[7]→[8]→...→[25]`

**参考文献部分超链接**——`cmd_hyperlink` 现在正确跳过参考文献部分，防止参考文献条目出现虚假超链接。

**邻近引用删除**——新增 `dedup_adjacent_citations()` 在创建超链接前折叠正文 `[1][1][1]` → `[1]`。

## [1.0.0] - 2026-05-29

### 🐛 论文修复 (Document Recovery)

#### 公式恢复
- 从备份文档中恢复了 3 个核心 OMML 公式（可编辑格式）
  - **公式 1**：`g_t = σ(w_t)` — 时间门控函数
  - **公式 2**：`g_v = σ(MLP([h_t; h_d; x_t]))` — 变量门控函数
  - **公式 3**：`y_fused = g_v ⊙ y_D + (1-g_v) ⊙ y_T` — 融合输出
- 恢复的公式可在 Word 中直接双击编辑

#### 图片恢复
- 恢复了 11 张论文插图（共 24 个媒体文件），包括：
  - HybridModel 整体架构图
  - 多城市预测对比图（北京/上海/广州）
  - MAE/MSE 柱状对比图
  - 门控收敛分析图
  - 消融实验对比图
  - 误差分布图、推理延迟图等

#### 题注修复
- 修复了图题注：`"图如下："` → `"图1 HybridModel整体架构"`
- 确保图/表编号格式符合学术规范

#### 兼容性修复
- 修复了 `[Content_Types].xml` 中图片 MIME 类型缺失导致的 python-docx `KeyError`
- 添加了 `image/png` 和 `image/x-wmf` 的 Override 条目

#### 保护机制
- 在 `fix_docx.py` 中添加 `_should_skip_paragraph()` 函数
- 自动检测并跳过包含 OMML 公式、绘图元素、Equation 样式的段落
- 防止正则处理时误清除公式/图片内容

### 🚀 技能增强 (Skill Enhancement)

#### academic-ref-inserter 新增功能

**`check-refs` 命令** — 引用状态检查
- 智能检测参考文献章节边界（含标题缺失时的降级方案）
- 逐条显示引用出现位置及上下文
- 支持 `--report` 参数导出检查报告
- 支持 JSON 格式输出

**`auto-find` 命令** — 自动搜索参考文献
- 自动提取论文标题/关键词
- 通过 CrossRef API 搜索相关文献
- 交互式选择搜索结果（支持编号范围、`all`、`none`）
- 自动去重（按 DOI 和标题匹配）
- 插入后自动重排编号

**工具函数增强**
- `find_reference_boundary_robust()` — 鲁棒的引用边界检测
- `find_citation_occurrences()` — 引用出现位置定位
- `extract_citation_content()` — 引用编号解析

### 🔧 其他变更

- 添加 `check_format.py` 格式检查脚本
- 清理临时诊断脚本（`check_*.py`、`restore_*.py`、`verify_*.py` 等测试文件）

### 📂 版本控制

- 初始化 Git 仓库，配置远程 `origin` → `https://github.com/fuwenhao12/academic-ref-inserter.git`
- 创建 `.gitignore` 配置文件（排除 `__pycache__/`、`*.tmp*`、`py_deps/`、`paper_rewriting_output/` 等）
- 使用 GitHub Personal Access Token 完成身份认证
- 首次提交并推送：205 个文件，5.52 MiB 至 `master` 分支
- 补充提交：添加 `CHANGELOG.md` 更新日志文件

### 📦 文件统计

| 类别 | 数量 |
|------|------|
| 新增文件 | 205 |
| 新增代码行 | 30,204 |
| 推送大小 | 5.52 MiB |
| OMML 公式 | 3 |
| 图片文件 | 11 |
