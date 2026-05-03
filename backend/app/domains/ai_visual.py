from .base import DomainStrategyBase


class AIVisualStrategy(DomainStrategyBase):
    domain = "ai_visual"
    display_name = "AI 视觉"

    @property
    def template(self) -> dict[str, str]:
        return {
            "【精准角色定义】": (
                "你是一位资深 AI 视觉提示词工程师，"
                "精通{Midjourney/Stable Diffusion/DALL-E 3/可灵/Sora/ComfyUI}工具链，"
                "擅长{商业摄影/概念设计/角色设计/建筑可视化/短视频生成}方向，"
                "熟悉各模型的核心参数语法和关键触发词"
            ),
            "【明确任务边界】": (
                "本次生成目标：{单张图片/系列图片/短视频/动态图像}\n"
                "使用平台：{Midjourney v6.1 / SDXL / DALL-E 3 / 可灵 1.5 / Sora}\n"
                "交付数量：{1张/4张/一组序列}，最终选取{1张}\n"
                "明确排除：\n"
                "  - 不包含 NSFW、血腥暴力、政治敏感内容\n"
                "  - 不模仿在世艺术家的独特风格（版权风险）\n"
                "  - 不生成可识别真实人物肖像（隐私风险）"
            ),
            "【完整上下文输入】": (
                "使用场景：{商业海报/社交媒体配图/产品渲染/概念艺术/IP设计/视频素材}\n"
                "主体描述（越详细越好）：\n"
                "  - 主体：{人/物/场景/抽象概念}\n"
                "  - 外观细节：{材质/纹理/颜色/大小/形状/新旧程度}\n"
                "  - 动作/状态：{动/静/情绪/姿态/交互关系}\n"
                "目标受众/风格预期：{受众感受}，传达的情绪={宁静/震撼/温馨/科技/神秘}\n"
                "参考素材（可选但强烈建议）：\n"
                "  - 风格参考图链接：{URL}\n"
                "  - 参考作品/艺术家/时期（公共领域或版权已过期）：{如 印象派/浮世绘/包豪斯}"
            ),
            "【可量化输出格式】": (
                "输出结构（按此顺序，越靠前的权重越高）：\n"
                "1. 画质标签：{8K/high detail/masterpiece/photorealistic/sharp focus/RAW}\n"
                "2. 风格标签：{photorealistic/anime/oil painting/3D render/cyberpunk…}\n"
                "3. 主体描述：{详细的英文关键词组合，按重要性降序排列}\n"
                "4. 构图/光影：镜头={close-up/medium shot/wide angle} | 光线={golden hour/studio lighting/neon/rim light}\n"
                "5. 色调/氛围：{warm tone/cool tone/muted colors/vibrant/monochromatic/…}\n"
                "6. 负向提示词：{worst quality, low quality, blurry, distorted, extra fingers, watermark, text, signature, NSFW}\n"
                "7. 参数设置（平台特定）：\n"
                "   - MJ: --ar {16:9/1:1/9:16} --stylize {0-1000} --chaos {0-100} --v {版本}\n"
                "   - SD: Steps={20-40}, Sampler={DPM++ 2M Karras/Euler a}, CFG scale={7-12}, Seed={-1}\n"
                "   - 可灵: 时长={5s/10s}, 分辨率={1080P}, 帧率={30fps}"
            ),
            "【强约束规则】": (
                "安全红线：\n"
                "  1. 严禁生成涉及真实人物的 Deepfake 或身份冒用内容\n"
                "  2. 严禁生成儿童色情、暴力极端主义或任何违法内容\n"
                "  3. 严禁生成模仿在世艺术家独特风格的提示词（版权侵犯风险）\n"
                "  4. 商业用途必须确认模型的商用许可范围\n"
                "  5. 生成人物/肖像类内容必须额外声明 AI 生成标识\n"
                "质量底线：\n"
                "  - 主体描述不少于 30 个英文关键词\n"
                "  - 负向提示词不少于 10 个关键排除项"
            ),
            "【校验反馈机制】": (
                "提示词自检清单：\n"
                "1. 关键词是否按权重排序（高权重在前）？\n"
                "2. 主体描述是否包含了 外观+材质+颜色+环境+动作 五个维度？\n"
"3. 风格标签是否有具体指向，而非泛化的”好看”“漂亮”？\n"
                "4. 负向提示词是否覆盖了该模型的常见 artifact（如 MJ6 的 text/SD 的 extra limbs）？\n"
                "5. 纵横比/分辨率是否正确匹配使用场景（横版海报/竖版手机壁纸/方形头像）？\n"
"6. 是否存在互相矛盾的修饰词（如”极简主义+高度细节化”）？\n"
                "调试建议：如出图效果不佳，尝试调整词序、增减权重标记（如 (keyword:1.2) 或 keyword::2）"
            ),
            "【场景化示例】": (
                "完整提示词示例（Midjourney 商业摄影）：\n"
                "```\n"
                "8K, high detail, masterpiece, commercial photography, sharp focus, "
                "a sleek minimalist ceramic coffee cup, matte white glaze, "
                "placed on a warm oak wooden table, morning sunlight streaming through "
                "sheer linen curtains, soft shadows, condensation droplets on cup surface, "
                "a small green succulent plant beside the cup, "
                "cozy modern kitchen in background, shallow depth of field, bokeh effect, "
                "warm tone, natural lighting, golden hour ambiance, 50mm lens, f/1.8\n"
                "--ar 16:9 --stylize 250 --v 6.1\n\n"
                "Negative: worst quality, low quality, blurry, distorted, deformed, "
                "extra fingers, bad anatomy, watermark, text, logo, "
                "harsh lighting, overexposed, oversaturated, cluttered background, "
                "plastic cup, dirty, messy\n"
                "```\n"
                "注意：主体使用英文关键词是行业最佳实践（模型训练数据以英文为主），"
                "模板中的描述说明使用中文以方便理解"
            ),
        }

    @property
    def role_instruction(self) -> str:
        return (
            "你是一位顶级 AI 视觉提示词工程师，恪守以下准则：\n"
            "1. 关键词为王——精准的关键词组合远胜长篇描述，每个词都要为画面贡献信息\n"
            "2. 权重排序——越重要的特征越靠前，主体→风格→构图→光影→色调，按此顺序排列\n"
            "3. 平台适配——不同模型的参数语法和关键触发词不同，提示词必须匹配目标平台\n"
            "4. 质量前置——画质标签（8K/masterpiece/high detail）放在最前面，设定品质基准\n"
            "5. 负向精准——负向提示词不是越多越好，而是精准针对该模型的常见 artifact\n"
            "6. 安全合规——绝不生成涉及 Deepfake、版权侵犯、违法或违背公序良俗的内容\n"
            "主体描述必须使用英文关键词（行业标准），辅助说明可使用中文。"
            "请严格按照结构模板输出，缺失信息用【待补充：字段名】标注。"
        )

    @property
    def rules(self) -> list[dict]:
        return [
            {
                "name": "主体描述过于模糊",
                "check_type": "missing_keyword",
                "keywords": ["人物", "场景", "物体", "建筑", "动物", "材质", "纹理", "颜色", "动作",
                             "portrait", "landscape", "character", "texture", "color", "pose"],
                "severity": "critical",
                "fix_suggestion": "【完整上下文输入】主体描述必须覆盖外观+材质+颜色+环境+动作五个维度，每个维度至少 3 个关键词",
            },
            {
                "name": "缺少风格标签",
                "check_type": "missing_keyword",
                "keywords": ["风格", "画风", "photorealistic", "anime", "3D", "oil painting",
                             "cyberpunk", "minimalist", "watercolor", "sketch", "render"],
                "severity": "critical",
                "fix_suggestion": "【可量化输出格式】必须包含具体风格标签，禁止仅用“好看”“漂亮“等主观模糊描述",
            },
            {
                "name": "缺少负向提示词",
                "check_type": "missing_keyword",
                "keywords": ["negative", "负向", "排除", "不要", "worst quality", "low quality",
                             "blurry", "distorted", "watermark", "NSFW"],
                "severity": "high",
                "fix_suggestion": "【可量化输出格式】必须包含至少 10 个负向关键词，针对性排除目标模型的常见缺陷",
            },
            {
                "name": "缺少平台参数",
                "check_type": "missing_keyword",
                "keywords": ["--ar", "--stylize", "--v", "Steps", "CFG", "Sampler", "Seed",
                             "分辨率", "时长", "帧率", "aspect", "parameter"],
                "severity": "high",
                "fix_suggestion": "【可量化输出格式】必须明确目标平台的技术参数（纵横比/风格权重/采样器/种子值等）",
            },
            {
                "name": "内容安全违规风险",
                "pattern": r"(nude|naked|porn|gore|violence|deepfake|deep fake|裸体|色情|血腥)",
                "check_type": "pattern_violation",
                "severity": "critical",
                "fix_suggestion": "【强约束规则】检测到可能违规的内容请求，必须拒绝生成并说明原因",
            },
            {
                "name": "风格描述矛盾",
                "pattern": r"(极简.*高度细节|minimalist.*highly detailed|写实.*卡通|realistic.*cartoon)",
                "check_type": "pattern_violation",
                "severity": "medium",
                "fix_suggestion": "【校验反馈机制】提示词中存在矛盾的修饰词组合，可能导致生成的图像混乱。请二选一或明确优先级",
            },
            {
                "name": "缺少镜头与光影描述",
                "check_type": "missing_keyword",
                "keywords": ["镜头", "角度", "光线", "焦距", "景深", "构图",
                             "camera", "lighting", "angle", "shot", "depth of field", "composition"],
                "severity": "medium",
                "fix_suggestion": "【可量化输出格式】建议补充镜头规格（焦距/景深/角度）和光线方案，这决定了画面的专业度",
            },
        ]

    @property
    def scoring_weights(self) -> dict[str, float]:
        return {
            "clarity": 0.30,
            "structure": 0.25,
            "redundancy": 0.10,
            "role_setting": 0.15,
            "output_spec": 0.20,
        }
