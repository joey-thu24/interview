import streamlit as st
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from components.ui import load_custom_css
from core.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

st.set_page_config(page_title="Library", page_icon="📚", layout="wide")
load_custom_css()

# --- Login Check ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login from the main page first.")
    st.stop()

st.title("📚 Core Knowledge Library")
st.markdown("Deep technical breakdown instead of rote memorization. Search existing content or ask AI to **Research** a new topic on the spot.")

# Simulated Knowledge Base
DEFAULT_DOCS = {
    # --- 大模型与深度学习 (LLM & DL) ---
    "LLM: Transformer 架构精讲": """
# Transformer：大模型的基石

Transformer 架构（Attention Is All You Need, 2017）彻底改变了 NLP。它是 BERT、GPT 等所有现代大模型的基础。

## 1. 核心组件
### Self-Attention (自注意力机制)
公式：$$Attention(Q, K, V) = softmax(\\frac{QK^T}{\\sqrt{d_k}})V$$
- **直观理解**：计算句子中每个词与其他词的关联度（权重）。
- **Q (Query)**：我想查什么？
- **K (Key)**：文章里有什么标签？
- **V (Value)**：原来的内容是什么？
- **Why $\\sqrt{d_k}$?**：为了防止点积结果过大导致 Softmax 梯度消失。

### Multi-Head Attention (多头注意力)
- 将 Q, K, V 拆分成多个头并行计算。
- **作用**：让模型从不同子空间（语法、语义、指代关系等）捕捉信息。

### Positional Encoding (位置编码)
- Transformer 并行计算，没有 RNN 的时序概念。
- 必须通过正弦/余弦函数注入位置信息，让模型知道“猫吃鼠”和“鼠吃猫”的区别。

## 2. Encoder vs Decoder
- **Encoder-only (如 BERT)**：双向注意力（能看到上下文）。**擅长**：理解、分类、情感分析。
- **Decoder-only (如 GPT)**：单向注意力（Masked, 只能看左边）。**擅长**：生成、续写。
- **Encoder-Decoder (如 T5)**：两头都有。**擅长**：翻译、摘要。
""",

    "LLM: 训练全流程 (Pre-train, SFT, RLHF)": """
# 从 0 到 ChatGPT：大模型训练三部曲

## 第一阶段：预训练 (Pre-training) - "博览群书"
- **目标**：学习语言的统计规律和世界知识。
- **数据**：海量无标注文本（Common Crawl, Wikipedia, Github）。
- **任务**：Next Token Prediction（预测下一个词）。
- **产出**：基座模型（Base Model）。它懂很多知识，但不懂指令，只会续写。

## 第二阶段：有监督微调 (SFT / Instruction Tuning) - "学习规矩"
- **目标**：让模型学会听懂人类指令。
- **数据**：高质量的 `(Prompt, Response)` 对。
- **产出**：对话模型（Chat Model）。它能回答问题，但可能胡说八道或不礼貌。

## 第三阶段：人类反馈强化学习 (RLHF) - "对齐价值观"
- **步骤 1 (Reward Model)**：让人类对模型生成的多个回答排序，训练一个奖惩模型 (RM)。
- **步骤 2 (PPO)**：用 RM 指导主模型，最大化奖励。
- **产出**：对齐后的模型（Aligned Model）。更安全、有用、诚实 (Helpful, Honest, Harmless)。
""",

    "LLM: 高效微调技术 (PEFT & LoRA)": """
# PEFT: 让个人也能微调大模型

全量微调（Full Fine-tuning）需要更新所有参数，显存成本极高。PEFT（Parameter-Efficient Fine-Tuning）只更新少量参数。

## LoRA (Low-Rank Adaptation)
- **原理**：冻结预训练权重 $W$，在旁路增加两个低秩矩阵 $A$ 和 $B$。
- **公式**：$$h = Wx + BAx$$
- **优势**：
  1. **显存极低**：不仅参数少，更重要的是不需要优化器存储 $W$ 的梯度。
  2. **可插拔**：训练好的 LoRA 权重很小（几十 MB），可以随时切换不同任务的 adapter。
  
## 其他技术
- **P-Tuning / Prompt Tuning**：不改模型参数，只优化输入的 Prompt Embedding。
- **QLoRA**：配合 4-bit 量化技术，进一步降低显存需求（单卡 24G 可微调 30B 模型）。
""",

    "LLM: RAG (检索增强生成)": """
# RAG：解决大模型幻觉与时效性

LLM 有两大痛点：**知识过期**（训练数据截止于过去）和 **幻觉**（一本正经胡说八道）。RAG (Retrieval-Augmented Generation) 是目前的最佳实践。

## 核心流程
1. **Indexing (索引)**：
   - 将私有文档 (PDF, Wiki) 切片 (Chunking)。
   - 调用 Embedding 模型转为向量。
   - 存入向量数据库 (Vector DB)。
   
2. **Retrieval (检索)**：
   - 用户提问 -> 转向量。
   - 在向量库中查找最相似的 Top-K 片段。
   
3. **Generation (生成)**：
   - 将 `用户问题 + 检索到的片段` 拼装进 Prompt。
   - "请根据以下背景知识回答问题：..."
   - LLM 生成最终答案。

## 进阶技巧
- **Re-ranking (重排序)**：检索回来粗排结果后，用精排模型再筛一遍。
- **Hybrid Search**：关键词检索 (BM25) + 语义检索 (Vector) 混合使用。
""",

    "LLM: Agent 与 Tool Use": """
# Agents：大模型的手脚

如果是 Chat 是大脑，Agent 就是给了大脑手和脚，让它能与世界交互。

## 核心范式：ReAct (Reasoning + Acting)
模型在执行任务时，进行内部独白：
1. **Thought**：我需要查询现在的天气。
2. **Action**：调用 `get_weather(city="Beijing")` 工具。
3. **Observation**：工具返回 "25°C, Sunny"。
4. **Thought**：天气不错，可以建议用户出去玩。
5. **Final Answer**：北京今天25度，天气晴朗...

## 常见框架
- **LangChain**：最早的编排框架，Chain 和 Agent 概念普及者。
- **AutoGPT**：自主循环执行任务。
- **OpenAI Assistants API**：官方封装的 Agent 能力（Code Interpreter, Retrieval）。
""",

    # --- 计算机基础 (高频必问) ---
    "OS: 进程 vs 线程 (Process vs Thread)": """
# 进程与线程：操作系统面试必问

## 核心区别
| 维度 | 进程 (Process) | 线程 (Thread) |
|:---|:---|:---|
| **定义** | 资源分配的最小单位 | CPU 调度的最小单位 |
| **内存** | 独立地址空间，互不干扰 | 共享进程的堆(Heap)和数据段，独有栈(Stack) |
| **开销** | 创建/切换开销大 | 开销小 (轻量级) |
| **通信** | 困难 (IPC: 管道, 消息队列, 共享内存) | 容易 (直接读写共享变量) |
| **健壮性** | 进程挂了不影响其他进程 | 一个线程崩了可能导致整个进程崩 (SegFault) |

## Python GIL (全局解释器锁)
这是一道 Python 岗位必问。
- **现象**：多线程 Python 跑满 CPU 也只能用 1 个核。
- **原因**：CPython 解释器为了内存安全，同一时刻只允许一个线程执行字节码。
- **破解**：计算密集型任务使用 `multiprocessing` (多进程)；IO 密集型任务 (爬虫) 用多线程或协程 (`asyncio`) 依然有效。
""",
    
    "Network: TCP 三次握手与四次挥手": """
# TCP 核心机制

## 三次握手 (建立连接)
1. **SYN**: 客户端发包 "我想连你" (seq=x)。
2. **SYN + ACK**: 服务端回包 "好的，我也想连你" (ack=x+1, seq=y)。
3. **ACK**: 客户端回包 "收到了" (ack=y+1)。
**为什么是三次？** 为了防止已失效的连接请求突然传到服务端，造成资源浪费；同时确认双方的收发能力都正常。

## 四次挥手 (断开连接)
1. **FIN**: 客户端 "我发完了" (主动关闭)。
2. **ACK**: 服务端 "知道了"，但可能还有数据没发完 (进入 Close-Wait)。
3. **FIN**: 服务端 "我也发完了" (被动关闭)。
4. **ACK**: 客户端 "好的，拜拜" (进入 Time-Wait，等待 2MSL 以确保服务端收到了最后的 ACK)。
""",

    "Database: ACID 与 隔离级别": """
# 数据库事务 ACID

## 四大特性
1. **Atomicity (原子性)**：要么全做，要么全不做。**实现**：Undo Log。
2. **Consistency (一致性)**：事务前后数据守恒，符合约束。
3. **Isolation (隔离性)**：并发事务互不干扰。**实现**：锁 + MVCC。
4. **Durability (持久性)**：提交后因断电也不丢失。**实现**：Redo Log。

## MySQL (InnoDB) 隔离级别
1. **Read Uncommitted**：读未提交 (脏读)。
2. **Read Committed (RC)**：读已提交 (不可重复读)。Oracle 默认。
3. **Repeatable Read (RR)**：可重复读 (幻读)。MySQL 默认。**注意**：InnoDB 通过 Next-Key Lock 实际上在 RR 级别解决了大部分幻读。
4. **Serializable**：串行化。慢，但绝对安全。
""",

    "Redis: 高频面试考点": """
# Redis 深度解析

## 1. 为什么快？
- **纯内存操作**。
- **单线程模型**：避免了上下文切换和锁竞争 (Redis 6.0 后网络 IO 变多线程)。
- **IO 多路复用 (Epoll)**：非阻塞 IO。

## 2. 持久化 (RDB vs AOF)
- **RDB (快照)**：定时的二进制文件。恢复快，但会丢数据。
- **AOF (日志)**：追加写命令。数据全，文件大，恢复慢。
- **混合持久化**：结合两者优点 (Redis 4.0+)。

## 3. 缓存异常场景
- **缓存穿透**：查不存在的数据，请求直打数据库。**解法**：布隆过滤器, 缓存空值。
- **缓存击穿**：热点 Key 过期，并发请求压垮 DB。**解法**：互斥锁, 逻辑过期(不设 TTL)。
- **缓存雪崩**：大量 Key 同时过期。**解法**：随机 TTL, 集群预热。
"""
}

# Session State for User Docs
if "user_docs" not in st.session_state:
    st.session_state.user_docs = {}

all_docs = {**DEFAULT_DOCS, **st.session_state.user_docs}

# UI Layout
col_list, col_content = st.columns([1, 3])

with col_list:
    st.subheader("📑 知识目录")
    
    # Tool: AI Researcher
    with st.expander("🕵️‍♂️ AI 深度调研员", expanded=True):
        new_topic = st.text_input("输入想调研的课题", placeholder="例如: 扩散模型原理, K8s架构")
        if st.button("生成深度研报", type="primary", use_container_width=True):
             if not new_topic:
                 st.error("请输入主题")
             else:
                 with st.spinner(f"正在全网检索并撰写 '{new_topic}' 的技术内参..."):
                     try:
                         llm = get_llm()
                         prompt = ChatPromptTemplate.from_template("""
你是一名资深技术专家和大学教授。请为主题 "{topic}" 撰写一篇**深度技术内参**。
要求：
1. **结构清晰**：包含 核心概念、底层原理 (源码/数学级)、工业界应用场景、面试高频考察点 (Pros/Cons)。
2. **拒绝浅薄**：不要只写百科简介，要写出"内行看门道"的深度。如果涉及算法，请简要解释关键公式；如果涉及系统，请提及架构取舍。
3. **格式美观**：使用 Markdown，合理使用由标题、列表、代码块。
4. **语言**：使用中文。
                         """)
                         chain = prompt | llm | StrOutputParser()
                         content = chain.invoke({"topic": new_topic})
                         st.session_state.user_docs[new_topic] = content
                         st.rerun()
                     except Exception as e:
                         st.error(f"生成失败: {e}")

    st.markdown("---")
    selected_doc = st.radio("文章列表", list(all_docs.keys()), label_visibility="collapsed")

with col_content:
    if selected_doc:
        st.header(selected_doc)
        st.markdown(all_docs[selected_doc])
        
        # Action Buttons
        c1, c2 = st.columns([1, 6])
        with c1:
            if st.button("🗑️ 删除笔记"):
                 if selected_doc in st.session_state.user_docs:
                     del st.session_state.user_docs[selected_doc]
                     st.rerun()
                 else:
                     st.error("系统预置内容无法删除")
    else:
        st.info("👈 请在左侧选择文章，或使用 AI 调研新知识")
