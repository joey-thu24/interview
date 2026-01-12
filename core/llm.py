from langchain_openai import ChatOpenAI
from core.config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME

def get_llm():
    """
    获取配置好的 LLM 实例
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found. Please set it in .env file.")
    
    # 硅基流动 (SiliconFlow) 特定参数配置
    # 注意：OpenAI 官方 SDK 不支持 top_k 和 min_p 直接作为参数，需要放入 extra_body 中
    model_kwargs = {
        "frequency_penalty": 0.5,
        "extra_body": {
            "top_k": 50,
            "min_p": 0.05,
        }
    }

    return ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=OPENAI_API_KEY,
        openai_api_base=OPENAI_BASE_URL,
        temperature=0.7,
        model_kwargs=model_kwargs
    )
