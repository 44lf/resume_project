import os
import json
import re
import httpx
from dotenv import load_dotenv

load_dotenv()

def _extract_json(text: str) -> dict:
    """
    尽量从模型输出里抠出 JSON 对象。
    """
    text = text.strip()
    # 优先抓 ```json ... ```
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    if m:
        return json.loads(m.group(1))

    # 再抓第一个 { ... } 块
    m = re.search(r"(\{.*\})", text, flags=re.S)
    if m:
        return json.loads(m.group(1))

    # 最后尝试直接 parse
    return json.loads(text)


def _normalize_result(d: dict) -> dict:
    """
    把字段名统一到你的 screening_resumes 需要的 key。
    """
    def pick(*keys):
        for k in keys:
            if k in d and d[k] not in ("", None):
                return d[k]
        return None

    skills_value = d.get("skills") or d.get("skill_list")
    if isinstance(skills_value, str):
        # 尝试用逗号/换行拆分
        skills_value = [
            s.strip() for s in re.split(r"[,\n;，；]", skills_value) if s.strip()
        ]

    out = {
        "name": pick("name", "姓名"),
        "school": pick("school", "毕业院校", "院校"),
        "major": pick("major", "专业"),
        "degree": pick("degree", "学位", "学历"),
        "grad_year": pick("grad_year", "毕业年份", "毕业时间"),
        "phone": pick("phone", "mobile", "手机号", "手机"),
        "email": pick("email", "邮箱"),
        "skills": skills_value or [],
    }

    # grad_year 尝试转 int
    gy = out["grad_year"]
    if isinstance(gy, str):
        m = re.search(r"(19|20)\d{2}", gy)
        out["grad_year"] = int(m.group(0)) if m else None

    return out


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
- name
- school
- major
- degree
- grad_year（毕业年份，整数）
- phone
- email
- skills（数组，列出简历中的关键技能）

缺失填 null。

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
