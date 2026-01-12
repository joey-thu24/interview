import os
from dotenv import load_dotenv

load_dotenv()

# --- Database Config ---
# 默认使用 SQLite，但支持通过环境变量覆盖为 TiDB (MySQL protocol)
# 格式示例: mysql+pymysql://user:password@gateway01.region.tidbcloud.com:4000/db_name?ssl_ca=result_from_tidb_console
# 注意：TiDB Serverless 强制要求 SSL，请确保连接串正确包含 ssl_ca 或 ssl_verify_cert=true 等参数
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./interview.db")

# --- Security Config ---
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-it")

# --- AI Config ---
# 建议用户在根目录创建 .env 文件: OPENAI_API_KEY=sk-...
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo") # MVP阶段可以用更便宜的模型
