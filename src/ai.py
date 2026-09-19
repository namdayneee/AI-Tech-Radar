import json
import re

from functools import lru_cache

from google import genai

from src.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
)


# ============================================================
# GEMINI CLIENT
# ============================================================

@lru_cache(maxsize=1)
def get_client():
    """
    Tạo duy nhất một Gemini client
    trong suốt vòng đời process.
    """

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "Thiếu GEMINI_API_KEY."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


# ============================================================
# JSON PARSER
# ============================================================

def _extract_json(
    text: str,
) -> dict:
    """
    Gemini đôi khi trả JSON trong
    markdown ```json.

    Hàm này làm sạch trước khi json.loads.
    """

    text = text.strip()

    if text.startswith("```"):

        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

    return json.loads(text)


# ============================================================
# ARTICLE ANALYSIS
# ============================================================

def analyze_article(
    item: dict,
) -> dict:
    """
    Gemini đánh giá một article.

    Output:

    relevant
    category
    importance_score
    summary
    why_it_matters
    """

    prompt = f"""
Bạn là bộ lọc tin AI và công nghệ
cho một lập trình viên phần mềm.

Hãy phân tích bài viết sau.

SOURCE:
{item['source']}

TITLE:
{item['title']}

EXCERPT:
{item.get('raw_excerpt', '')[:4500]}

URL:
{item['url']}


=====================================
CHỦ ĐỀ ƯU TIÊN
=====================================

Ưu tiên cao:

- Artificial Intelligence
- LLM
- Reasoning Models
- AI Agents
- Coding Agents
- Computer Use
- RAG
- MCP
- Multimodal AI

Các công ty / lab:

- OpenAI
- Anthropic
- Google DeepMind
- Google AI
- Microsoft
- NVIDIA
- Hugging Face
- Meta AI
- Mistral

Developer tools:

- Codex
- Cursor
- Claude Code
- GitHub
- VS Code

Software Engineering:

- Web
- Backend
- Frontend
- Database
- System Design
- API
- Programming Languages

Infrastructure:

- Docker
- Kubernetes
- DevOps
- CI/CD
- Cloud
- GPU
- AI Infrastructure

Computer Science:

- Operating Systems
- Networking
- Distributed Systems
- Compiler

Security:

- Cybersecurity
- AI Security

Research:

- nghiên cứu AI quan trọng
- paper mới
- model mới
- benchmark mới
- architecture mới


=====================================
OUTPUT
=====================================

Trả về CHÍNH XÁC một JSON object.

Không Markdown.
Không giải thích ngoài JSON.

Schema:

{{
  "relevant": true,
  "category": "AI|Research|Developer Tools|Programming|Infrastructure|Systems|Security|Other",
  "importance_score": 0.0,
  "summary": "Tóm tắt tiếng Việt 1-3 câu",
  "why_it_matters": "Giải thích ngắn gọn vì sao bài này đáng chú ý với lập trình viên"
}}


=====================================
SCORING
=====================================

9.0 - 10.0

Tin cực kỳ quan trọng:
- model lớn mới
- bước đột phá AI
- sản phẩm ảnh hưởng mạnh tới developer
- thay đổi lớn từ OpenAI / Anthropic /
  Google / NVIDIA
- nghiên cứu có tác động lớn


8.0 - 8.9

Rất quan trọng:
- công cụ developer lớn
- AI Agent quan trọng
- model/research đáng chú ý
- thay đổi hạ tầng AI


7.0 - 7.9

Quan trọng:
- công nghệ mới
- research tốt
- developer tool đáng theo dõi


5.5 - 6.9

Đáng đọc:
- thông tin hữu ích
- xu hướng mới
- cập nhật có giá trị


0 - 5.4

Ít quan trọng hoặc ngoài trọng tâm.


=====================================
RULES
=====================================

- score phải từ 0 đến 10.
- Không bịa thông tin.
- Chỉ sử dụng TITLE + EXCERPT.
- relevant=false nếu bài không đáng kể
  đối với AI/công nghệ/lập trình.
"""

    client = get_client()

    response = (
        client.interactions.create(
            model=GEMINI_MODEL,
            input=prompt,
        )
    )

    data = _extract_json(
        response.output_text
    )

    score = float(
        data.get(
            "importance_score",
            0,
        )
    )

    data[
        "importance_score"
    ] = max(
        0.0,
        min(
            10.0,
            score,
        ),
    )

    data[
        "relevant"
    ] = bool(
        data.get(
            "relevant",
            False,
        )
    )

    return data