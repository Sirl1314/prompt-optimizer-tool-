from .base import DomainStrategyBase


class CodeDevStrategy(DomainStrategyBase):
    domain = "code_dev"
    display_name = "代码开发"

    @property
    def template(self) -> dict[str, str]:
        return {
            "【精准角色定义】": (
                '你是一位资深{后端/前端/全栈/算法}工程师，'
                '精通{技术栈名称}，有{年限}年开发经验，'
                '擅长{具体领域如高并发/数据管道/组件库/模型部署}'
            ),
            "【明确任务边界】": (
                '核心任务：{具体要实现的功能或要修的 Bug}\n'
                '范围限定：仅涉及{模块/服务/组件}，不包含{明确排除的内容}\n'
                '交付标准：代码通过{单元测试/集成测试/手工验证}方可视为完成'
            ),
            "【完整上下文输入】": (
                '项目背景：{业务场景，为什么要做这个功能}\n'
                '技术环境：语言版本={Go 1.22/Python 3.12/TypeScript 5.x} | '
                '框架={框架名+版本} | 数据库={类型+版本}\n'
                '关键依赖：{第三方库名称与版本}\n'
                '现有约束：{已有的接口契约/数据模型/命名规范/目录结构}'
            ),
            "【可量化输出格式】": (
                '代码文件：{文件名+路径}，预估行数≤{N}\n'
                '注释要求：每个公开函数必须有 docstring/JSdoc，关键逻辑附行内注释\n'
                '错误处理：所有 I/O 与外部调用必须有 try-catch/error propagation\n'
                '附加产物：{接口文档/数据流图/部署说明}（按需）'
            ),
            "【强约束规则】": (
                '安全红线：禁止硬编码密钥/连接串，参数化所有 SQL 查询，'
                '输入必须做校验与清洗\n'
                '性能底线：{时间复杂度上限如 O(n log n)} | '
                '{内存上限如 512MB} | {接口响应时间上限如 p99<200ms}\n'
                '代码风格：遵循{Google Style/ Airbnb/ PEP8}，'
                '使用{ESLint/Black/rustfmt}自动格式化'
            ),
            "【校验反馈机制】": (
                '自检清单：\n'
                '1. 是否覆盖了所有输入边界（空值/超长/特殊字符）？\n'
                '2. 是否包含至少 2 个正向测试用例 + 1 个异常路径用例？\n'
                '3. 是否存在竞态条件或资源泄露风险？\n'
                '4. 日志/埋点是否足够定位线上问题？\n'
                '如有任一答案为"否"，请在交付前补充'
            ),
            "【场景化示例】": (
                '输入示例：\n'
                '```\n{具体的输入数据或请求示例}\n```\n'
                '期望输出：\n'
                '```\n{期望的返回结果或行为描述}\n```\n'
                '边界情况：当{边界条件}时，应返回{预期行为}'
            ),
        }

    @property
    def role_instruction(self) -> str:
        return (
            '你是一位顶级软件工程师，具备以下专业素养：\n'
            '1. 代码即文档——命名自解释，结构即架构图，注释只写"为什么"不写"是什么"\n'
            '2. 防御式编程——对所有外部输入、网络响应、文件 I/O 做校验，永不信任调用方\n'
            '3. 性能意识——在可读性不降低的前提下，选择最优时间/空间复杂度的实现\n'
            '4. 安全内建——杜绝 OWASP Top 10 漏洞，敏感信息零硬编码\n'
            '5. 可测试性——每个函数职责单一、无副作用，方便编写单元测试\n'
            '请严格按照结构模板输出，模板中的占位符用用户提供的信息填充，'
            '缺失的信息用【待补充：字段名】明确标注，不得自行编造。'
        )

    @property
    def rules(self) -> list[dict]:
        return [
            {
                "name": "角色定义不精准",
                "check_type": "missing_keyword",
                "keywords": ["工程师", "开发", "程序员", "engineer", "developer", "前端", "后端", "全栈", "算法"],
                "severity": "critical",
                "fix_suggestion": '【精准角色定义】必须明确技术栈、经验年限和擅长领域，避免泛化的"程序员"角色',
            },
            {
                "name": "任务边界模糊",
                "check_type": "missing_keyword",
                "keywords": ["范围", "不包含", "边界", "scope", "exclude", "仅涉及"],
                "severity": "critical",
                "fix_suggestion": "【明确任务边界】需声明做什么、不做什么，防止 AI 自行扩展或遗漏",
            },
            {
                "name": "缺少技术上下文",
                "check_type": "missing_keyword",
                "keywords": ["版本", "框架", "数据库", "依赖", "version", "framework", "Python", "Go", "Java", "Node", "React", "Vue"],
                "severity": "high",
                "fix_suggestion": "【完整上下文输入】需提供语言版本、框架名称与版本、关键依赖，缺少上下文将导致代码不可用",
            },
            {
                "name": "输出格式不可量化",
                "check_type": "missing_keyword",
                "keywords": ["行数", "注释", "错误处理", "docstring", "测试", "文件", "路径"],
                "severity": "high",
                "fix_suggestion": "【可量化输出格式】需明确代码文件路径、行数上限、注释标准和错误处理要求",
            },
            {
                "name": "缺少安全与性能约束",
                "check_type": "missing_keyword",
                "keywords": ["安全", "SQL", "注入", "加密", "密钥", "性能", "复杂度", "O(", "内存", "security", "performance"],
                "severity": "critical",
                "fix_suggestion": "【强约束规则】必须包含安全红线（防注入、无硬编码密钥）和性能底线（时间/空间复杂度上限）",
            },
            {
                "name": "缺少校验反馈机制",
                "check_type": "missing_keyword",
                "keywords": ["测试", "边界", "用例", "校验", "自检", "test", "edge case", "验证"],
                "severity": "high",
                "fix_suggestion": "【校验反馈机制】需提供自检清单或测试用例，确保代码在交付前已通过基本验证",
            },
            {
                "name": "代码块未指定语言",
                "pattern": r"```\s*\n",
                "check_type": "pattern_violation",
                "severity": "low",
                "fix_suggestion": "代码块必须标注语言标签（如 ```python），便于 IDE 和文档工具正确渲染",
            },
        ]

    @property
    def scoring_weights(self) -> dict[str, float]:
        return {
            "clarity": 0.20,
            "structure": 0.30,
            "redundancy": 0.10,
            "role_setting": 0.15,
            "output_spec": 0.25,
        }
