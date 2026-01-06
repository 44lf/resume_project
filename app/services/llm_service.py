import os
import json
import re
import httpx
from dotenv import load_dotenv

load_dotenv()


async def extract_resume_info(text: str) -> dict:
    """
    输入：简历文本
    输出：结构化 dict
    """
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("未设置 LLM_API_KEY")

    prompt = f"""
请从下面简历文本中提取信息，并只输出 JSON：

字段：
name, school, major, degree, grad_year, phone, email, skills

简历文本：
{text}
""".strip()

    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()

        content = resp.json()["choices"][0]["message"]["content"]

    # 直接找第一个 { ... }
    match = re.search(r"\{.*\}", content, re.S)
    if not match:
        raise ValueError("模型未返回 JSON")

    data = json.loads(match.group())

    # 简单清洗
    skills = data.get("skills", [])
    if isinstance(skills, str):
        skills = [s.strip() for s in re.split(r"[,\n]", skills) if s.strip()]

    grad_year = data.get("grad_year")
    if isinstance(grad_year, str):
        m = re.search(r"(19|20)\d{2}", grad_year)
        grad_year = int(m.group()) if m else None

    return {
        "name": data.get("name"),
        "school": data.get("school"),
        "major": data.get("major"),
        "degree": data.get("degree"),
        "grad_year": grad_year,
        "phone": data.get("phone"),
        "email": data.get("email"),
        "skills": skills,
    }
