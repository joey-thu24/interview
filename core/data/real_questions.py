# 预置的大厂高频真题库
# 包含：题目、公司、年份、难度、考察点

REAL_QUESTIONS = [
    # --- Python 基础 ---
    {
        "topic": "Python 基础",
        "company": "字节跳动",
        "year": "2024",
        "question": "Python 的 GIL (全局解释器锁) 是什么？它对多线程有什么影响？如何在 CPU 密集型任务中绕过它？",
        "difficulty": "困难",
        "tags": ["GIL", "并发"]
    },
    {
        "topic": "Python 基础",
        "company": "美团",
        "year": "2023",
        "question": "请手写一个 Python 装饰器，实现函数执行时间的统计功能，保留被装饰函数的元数据（wraps）。",
        "difficulty": "中等",
        "tags": ["装饰器", "闭包"]
    },
    {
        "topic": "Python 基础",
        "company": "腾讯",
        "year": "2023",
        "question": "Python 中的迭代器（Iterator）和生成器（Generator）有什么区别？请举例说明 yield from 的用法。",
        "difficulty": "中等",
        "tags": ["迭代器", "生成器"]
    },
    {
        "topic": "Python 基础",
        "company": "阿里云",
        "year": "2024",
        "question": "Python 的内存管理机制是怎样的？请详细解释引用计数和垃圾回收（GC）的分代回收策略。",
        "difficulty": "困难",
        "tags": ["内存管理", "GC"]
    },

    # --- MySQL ---
    {
        "topic": "MySQL",
        "company": "美团",
        "year": "2024",
        "question": "Explain 语句中的 type 字段有哪些值？性能从高到低排序是怎样的？什么情况下会导致索引失效？",
        "difficulty": "中等",
        "tags": ["索引", "调优"]
    },
    {
        "topic": "MySQL",
        "company": "拼多多",
        "year": "2023",
        "question": "MySQL 的 MVCC（多版本并发控制）是如何实现的？Read View 在 RR 和 RC 级别下有什么不同？",
        "difficulty": "困难",
        "tags": ["事务", "MVCC"]
    },
    {
        "topic": "MySQL",
        "company": "字节跳动",
        "year": "2024",
        "question": "B+ 树和 B 树的区别是什么？为什么 MySQL 选择 B+ 树作为索引结构而不是红黑树或 Hash？",
        "difficulty": "中等",
        "tags": ["数据结构", "索引"]
    },
    {
        "topic": "MySQL",
        "company": "快手",
        "year": "2023",
        "question": "Redo Log, Undo Log, Binlog 分别有什么作用？两阶段提交（2PC）的流程是怎样的？",
        "difficulty": "困难",
        "tags": ["日志", "架构"]
    },

    # --- 计算机网络 ---
    {
        "topic": "计算机网络",
        "company": "腾讯",
        "year": "2024",
        "question": "TCP 的三次握手和四次挥手流程是怎样的？为什么挥手需要四次？TIME_WAIT 状态过多的原因和危害？",
        "difficulty": "中等",
        "tags": ["TCP/IP"]
    },
    {
        "topic": "计算机网络",
        "company": "百度",
        "year": "2023",
        "question": "HTTPS 的握手过程（TLS 1.2/1.3）详细描述一下。客户端如何校验证书的合法性？",
        "difficulty": "困难",
        "tags": ["HTTPS", "安全"]
    },
    {
        "topic": "计算机网络",
        "company": "字节跳动",
        "year": "2024",
        "question": "从输入 URL 到页面渲染完成，发生了什么？请从网络协议、DNS 解析、浏览器渲染等角度详细说明。",
        "difficulty": "中等",
        "tags": ["浏览器", "综合"]
    },

    # --- 操作系统 ---
    {
        "topic": "操作系统",
        "company": "蚂蚁金服",
        "year": "2023",
        "question": "进程和线程的区别？进程间通信（IPC）的方式有哪些？哪种效率最高？",
        "difficulty": "中等",
        "tags": ["进程", "线程"]
    },
    {
        "topic": "操作系统",
        "company": "微软",
        "year": "2024",
        "question": "什么是死锁？死锁产生的四个必要条件是什么？如何避免死锁？",
        "difficulty": "中等",
        "tags": ["死锁"]
    },
    {
        "topic": "操作系统",
        "company": "华为",
        "year": "2023",
        "question": "Linux 的零拷贝（Zero Copy）技术原理是什么？sendfile 和 mmap 的区别？",
        "difficulty": "困难",
        "tags": ["Linux", "IO"]
    },

    # --- 系统设计 ---
    {
        "topic": "系统设计",
        "company": "阿里",
        "year": "2024",
        "question": "如何设计一个高并发的秒杀系统？重点解决超卖、流量削峰和数据库压力问题。",
        "difficulty": "困难",
        "tags": ["高并发", "架构"]
    },
    {
        "topic": "系统设计",
        "company": "字节跳动",
        "year": "2024",
        "question": "设计一个短链接生成系统（Short URL Generator）。如何保证短链的唯一性？如何处理海量存储？",
        "difficulty": "中等",
        "tags": ["分布式", "设计"]
    },
    {
        "topic": "系统设计",
        "company": "美团",
        "year": "2023",
        "question": "设计一个分布式 ID 生成器。对比 Snowflake 算法、数据库号段模式、Redis 自增的优缺点。",
        "difficulty": "中等",
        "tags": ["分布式"]
    }
]

def get_real_questions(topic=None):
    if not topic:
        return REAL_QUESTIONS
    return [q for q in REAL_QUESTIONS if q['topic'] == topic]
