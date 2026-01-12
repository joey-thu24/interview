# 预置的黄金学习路线图模板
# 这些内容可以是人工精选的，不仅包含知识点，还可以包含具体的参考书籍/链接

ROADMAP_TEMPLATES = {
    "后端开发工程师 (通用)": {
        "phases": [
            {
                "phase_name": "阶段一：语言核心与规范",
                "duration": "7天",
                "goals": ["掌握语言高级特性", "理解内存管理模型"],
                "key_topics": ["并发编程 (Thread/Coroutine)", "GC 机制与调优", "设计模式 (单例/工厂/策略)"]
            },
            {
                "phase_name": "阶段二：中间件深水区 (高频考点)",
                "duration": "10天",
                "goals": ["理解 Redis/MySQL 原理", "掌握消息队列场景"],
                "key_topics": ["MySQL 索引与锁机制", "Redis 持久化与缓存雪崩", "Kafka/RabbitMQ 消息丢失解决方案"]
            },
            {
                "phase_name": "阶段三：系统设计与微服务",
                "duration": "7天",
                "goals": ["具备基础架构设计能力", "解决分布式问题"],
                "key_topics": ["CAP 理论与 BASE", "分布式锁实现", "短链接系统/秒杀系统设计"]
            }
        ]
    },
    "AI 算法工程师 (校招)": {
        "phases": [
            {
                "phase_name": "阶段一：数学与机器学习基础",
                "duration": "10天",
                "goals": ["推导核心公式", "理解经典模型"],
                "key_topics": ["线性代数/概率论复习", "SVM/XGBoost 原理推导", "特征工程方法论"]
            },
            {
                "phase_name": "阶段二：深度学习与 Transformer",
                "duration": "14天",
                "goals": ["掌握 NLP/CV 核心架构", "能够复现 demo"],
                "key_topics": ["CNN/RNN/LSTM", "Attention 机制详解", "Transformer/BERT/GPT 架构演进"]
            },
            {
                "phase_name": "阶段三：Paper 阅读与垂类微调",
                "duration": "7天",
                "goals": ["跟进前沿", "掌握微调技术"],
                "key_topics": ["LoRA/P-Tuning 微调", "RAG 检索增强生成", "LangChain 应用开发"]
            }
        ]
    },
    "计算机科学基础 (CS Base)": {
        "phases": [
            {
                "phase_name": "阶段一：操作系统与网络核心",
                "duration": "14天",
                "goals": ["深入理解进程/线程模型", "掌握 TCP/IP 协议栈"],
                "key_topics": ["进程调度算法", "死锁产生与预防", "TCP 三次握手/四次挥手详解", "HTTPS 加密原理", "I/O 多路复用 (select/epoll)"]
            },
            {
                "phase_name": "阶段二：数据结构与算法攻坚",
                "duration": "21天",
                "goals": ["掌握常用数据结构", "能够手写核心算法"],
                "key_topics": ["红黑树/B+树原理", "图论基础 (DFS/BFS/最短路径)", "动态规划 (DP) 解题套路", "LRU Cache 实现", "Top K 问题"]
            },
             {
                "phase_name": "阶段三：编译原理与体系结构 (进阶)",
                "duration": "10天",
                "goals": ["理解代码如何运行", "了解 CPU 指令执行"],
                "key_topics": ["词法/语法分析基础", "AST 抽象语法树", "CPU 缓存一致性 (MESI)", "指令流水线"]
            }
        ]
    }
}

def get_template_names():
    return list(ROADMAP_TEMPLATES.keys())

def get_template(name):
    return ROADMAP_TEMPLATES.get(name)
