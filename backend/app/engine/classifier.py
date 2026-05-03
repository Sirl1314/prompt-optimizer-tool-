from ..schemas.pipeline import AnalysisReport, DomainResult, ParsedInput


_DOMAIN_KEYWORDS = {
    "code_dev": {
        "strong": ["code", "function", "implement", "bug", "debug", "API", "interface",
                   "frontend", "backend", "Python", "JavaScript", "React", "component",
                   "class", "import", "export", "database", "SQL", "deploy",
                   "代码", "函数", "实现", "接口", "前端", "后端", "数据库", "部署"],
        "medium": ["develop", "programming", "framework", "library", "module", "package",
                   "开发", "编程", "框架", "库", "模块"],
    },
    "copywriting": {
        "strong": ["copy", "poem", "article", "writing", "rewrite", "polish", "title",
                   "advertise", "brand", "story", "poetry", "essay", "report", "summary",
                   "文案", "诗词", "文章", "写作", "改写", "润色", "标题", "品牌", "故事", "诗歌", "散文", "报告", "总结"],
        "medium": ["write", "describe", "content", "text", "写", "描述", "内容", "文本"],
    },
    "data_analysis": {
        "strong": ["data", "analysis", "statistics", "chart", "visualization", "pandas",
                   "matplotlib", "CSV", "JSON", "trend", "correlation", "regression",
                   "clean", "missing value",
                   "数据", "分析", "统计", "图表", "可视化", "趋势", "相关性", "回归", "清洗", "缺失值"],
        "medium": ["numbers", "table", "report", "metric", "数字", "表格", "报表", "指标"],
    },
    "marketing": {
        "strong": ["marketing", "promotion", "advertising", "KOL", "KOC", "traffic",
                   "conversion", "follower", "WeChat", "Little Red Book", "TikTok",
                   "short video", "live stream",
                   "营销", "推广", "广告", "流量", "转化", "粉丝", "公众号", "小红书", "抖音", "短视频", "直播"],
        "medium": ["brand", "product", "user", "market", "sales", "品牌", "产品", "用户", "市场", "销售"],
    },
    "healthcare": {
        "strong": ["disease", "symptom", "diagnosis", "treatment", "medication", "surgery",
                   "patient", "doctor", "clinical", "pharmacology", "side effect",
                   "examination", "health",
                   "疾病", "症状", "诊断", "治疗", "用药", "手术", "患者", "医生", "临床", "药理", "副作用", "检查", "健康"],
        "medium": ["hospital", "body", "pain", "medicine", "医院", "身体", "疼痛", "药", "医"],
    },
    "legal": {
        "strong": ["law", "contract", "regulation", "litigation", "arbitration",
                   "infringement", "copyright", "patent", "clause", "judgment",
                   "court", "lawyer", "compliance", "GDPR", "PIPL",
                   "法律", "合同", "法规", "诉讼", "仲裁", "侵权", "版权", "专利", "条款", "判决", "法院", "律师", "合规"],
        "medium": ["agreement", "breach", "compensation", "mandatory", "协议", "违约", "赔偿", "强制"],
    },
    "education": {
        "strong": ["teaching", "course", "student", "exam", "quiz", "homework",
                   "lesson plan", "knowledge point", "explain", "learning",
                   "grade", "elementary", "middle school", "high school", "university",
                   "教学", "课程", "学生", "考试", "测验", "作业", "教案", "知识点", "讲解", "学习",
                   "年级", "小学", "初中", "高中", "大学", "培训"],
        "medium": ["education", "teacher", "classroom", "textbook", "教育", "教师", "课堂", "教材"],
    },
    "ai_visual": {
        "strong": ["drawing", "painting", "generate image", "AI art", "Midjourney",
                   "Stable Diffusion", "DALL-E", "video generation", "Sora", "Kling",
                   "prompt", "image", "style", "composition", "resolution", "negative prompt",
                   "绘画", "画图", "生成图", "AI绘画", "视频生成", "可灵",
                   "画面", "风格", "构图", "分辨率", "负向词"],
        "medium": ["picture", "image", "generate", "visual", "design", "illustration",
                   "图片", "图像", "生成", "视觉", "设计图", "插画"],
    },
}


def classify_domain(parsed: ParsedInput, _analysis: AnalysisReport | None = None) -> DomainResult:
    text = parsed.raw_text.lower()

    scores: dict[str, float] = {}
    for domain, keywords in _DOMAIN_KEYWORDS.items():
        score = 0.0
        for kw in keywords["strong"]:
            if kw.lower() in text:
                score += 2.0
        for kw in keywords["medium"]:
            if kw.lower() in text:
                score += 0.5
        scores[domain] = score

    if parsed.has_code_blocks:
        scores["code_dev"] += 3.0

    if not any(v > 0 for v in scores.values()):
        return DomainResult(domain="copywriting", confidence=0.3, alternative_domains=[])

    best = max(scores, key=scores.get)
    max_score = scores[best]
    confidence = min(max_score / max(max_score, 5.0), 1.0)

    alternatives = sorted(
        [d for d, s in scores.items() if d != best and s > 0],
        key=lambda d: scores[d], reverse=True
    )[:2]

    return DomainResult(
        domain=best,
        confidence=round(confidence, 2),
        alternative_domains=alternatives,
    )
