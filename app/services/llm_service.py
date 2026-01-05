# app/services/llm_service.py
# pip install httpx
import json
import os
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
    调用 OpenAI-兼容接口的 Chat Completions，返回 dict：
    {name, school, major, degree, grad_year, phone, email}
    """
    base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
    api_key = os.getenv("LLM_API_KEY", "")
    model = os.getenv("LLM_MODEL", "deepseek-chat")

    if not api_key:
        raise RuntimeError("未设置环境变量 LLM_API_KEY")

    prompt = f"""
你是简历信息抽取助手。请从下面简历文本抽取字段，并严格输出 JSON（只输出 JSON，不要输出其他文字）。

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
        "model": model,
        "messages": [
            {"role": "system", "content": "You extract resume fields and output strict JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 第一次请求
        r = await client.post(f"{base_url.rstrip('/')}/v1/chat/completions", headers=headers, json=payload)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]

        # 尝试解析 JSON；失败则追加“修正”提示再试一次
        try:
            d = _extract_json(content)
            return _normalize_result(d)
        except Exception:
            payload["messages"].append(
                {"role": "user", "content": "你刚才的输出不是合法 JSON。请只输出合法 JSON 对象。"}
            )
            r2 = await client.post(f"{base_url.rstrip('/')}/v1/chat/completions", headers=headers, json=payload)
            r2.raise_for_status()
            content2 = r2.json()["choices"][0]["message"]["content"]
            d2 = _extract_json(content2)
            return _normalize_result(d2)
