from fastapi import FastAPI
from dotenv import load_dotenv
from tortoise.contrib.fastapi import register_tortoise

from app.config.settings import DB_URL, DB_GENERATE_SCHEMAS
from app.routers.screening import router as screening_router

# 1) 加载环境变量
load_dotenv()

# 2) 创建应用
app = FastAPI(title="Resume Screening API")

# 3) 路由
app.include_router(screening_router, prefix="/api", tags=["screening"])

# 4) 数据库初始化
register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["app.db.models"]},
    generate_schemas=DB_GENERATE_SCHEMAS,
    add_exception_handlers=True,
)

# 5) 健康检查
@app.get("/health")
async def health():
    return {"status": "ok"}


