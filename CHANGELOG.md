# 更新日志 / Changelog

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

- 添加 `.gitignore` 配置文件（排除 `__pycache__/`、`*.tmp*`、`py_deps/`、`paper_rewriting_output/` 等）
- 添加 `check_format.py` 格式检查脚本
- 清理临时诊断脚本（`check_*.py`、`restore_*.py`、`verify_*.py` 等测试文件）

### 📦 文件统计

| 类别 | 数量 |
|------|------|
| 新增文件 | 205 |
| 新增代码行 | 30,204 |
| 推送大小 | 5.52 MiB |
| OMML 公式 | 3 |
| 图片文件 | 11 |
