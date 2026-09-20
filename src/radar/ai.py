import json
import re

from src.ai import get_client
from src.config import GEMINI_MODEL


# ============================================================
# CONSTANTS
# ============================================================

VALID_TYPES = {
    "AI_MODEL",
    "DEV_TOOL",
    "GITHUB_REPO",
    "RELEASE",
    "LANGUAGE",
    "FRAMEWORK",
    "PACKAGE",
    "PAPER",
    "SECURITY",
    "OTHER",
}


SCORE_KEYS = [
    "relevance_score",
    "novelty_score",
    "quality_score",
    "momentum_score",
    "importance_score",
]


# ============================================================
# JSON PARSER
# ============================================================

def extract_json(text: str) -> dict:
    """
    Gemini đôi khi trả JSON trong markdown code block.

    Ví dụ:

    ```json
    {...}
    ```

    Hàm này loại bỏ markdown trước khi json.loads().
    """

    if not text:
        raise ValueError(
            "Gemini trả response rỗng."
        )

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
# BOOLEAN NORMALIZER
# ============================================================

def normalize_bool(value) -> bool:
    """
    Tránh trường hợp:

    bool("false") == True

    nếu model lỡ trả string.
    """

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return value != 0

    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "1",
            "yes",
            "y",
        }

    return False


# ============================================================
# SCORE NORMALIZATION
# ============================================================

def _to_float(value) -> float:
    try:
        return float(value)

    except (TypeError, ValueError):
        return 0.0


def _clamp_score(value: float) -> float:
    return round(
        max(
            0.0,
            min(
                10.0,
                value,
            ),
        ),
        2,
    )


def normalize_scores(
    data: dict,
) -> dict:
    """
    Gemini phải trả score theo thang 0-10.

    Tuy nhiên đôi khi model trả cả bộ score
    theo thang 0-1:

        relevance = 0.9
        quality   = 0.8
        momentum  = 0.7
        ...

    Khi TOÀN BỘ score nằm trong 0-1,
    ta coi model đã dùng nhầm scale
    và nhân toàn bộ lên 10.

    Nếu có ít nhất một score > 1,
    ta coi output đã ở thang 0-10.

    Cách này an toàn hơn việc nhân 10
    từng score <= 1 riêng lẻ.
    """

    scores = {
        key: _to_float(
            data.get(key)
        )
        for key in SCORE_KEYS
    }

    values = list(
        scores.values()
    )

    uses_zero_to_one_scale = (
        values
        and max(values) <= 1.0
        and min(values) >= 0.0
        and any(
            value > 0
            for value in values
        )
    )

    if uses_zero_to_one_scale:
        print(
            "[INFO] Gemini returned 0-1 scoring scale. "
            "Normalizing scores to 0-10."
        )

        scores = {
            key: value * 10
            for key, value
            in scores.items()
        }

    for key, value in scores.items():
        data[key] = _clamp_score(
            value
        )

    return data


# ============================================================
# ITEM TYPE NORMALIZATION
# ============================================================

def normalize_item_type(
    candidate: dict,
    ai_data: dict,
) -> str:
    """
    Collector biết dữ liệu đến từ đâu,
    vì vậy item_type_hint đáng tin hơn AI.

    Ví dụ:

    GitHub release collector
        → RELEASE

    Hugging Face model collector
        → AI_MODEL

    Hugging Face Space
        → DEV_TOOL

    GitHub discovery
        → GITHUB_REPO

    AI không được tự đổi RELEASE thành GITHUB_REPO.
    """

    hint = str(
        candidate.get(
            "item_type_hint",
            "OTHER",
        )
    ).upper()


    # Candidate đặc biệt dùng để phát hiện
    # ngôn ngữ lập trình mới.
    if hint == "LANGUAGE_CANDIDATE":
        return "LANGUAGE"


    # Nếu collector đã xác định rõ loại,
    # tin collector.
    if (
        hint in VALID_TYPES
        and hint != "OTHER"
    ):
        return hint


    # Chỉ để AI quyết định khi collector
    # không biết chắc loại dữ liệu.
    ai_type = str(
        ai_data.get(
            "item_type",
            "OTHER",
        )
    ).upper()


    if ai_type not in VALID_TYPES:
        return "OTHER"

    return ai_type


# ============================================================
# RADAR STATUS
# ============================================================

def normalize_radar_status(
    value,
) -> str:

    status = str(
        value or "WATCH"
    ).upper()

    valid = {
        "WATCH",
        "ASSESS",
        "TRIAL",
    }

    if status not in valid:
        return "WATCH"

    return status


# ============================================================
# MAIN AI ANALYZER
# ============================================================

def analyze_radar_item(
    candidate: dict,
) -> dict:
    """
    Phân tích một Technology Radar candidate.
    """

    metadata = json.dumps(
        candidate.get(
            "metadata",
            {},
        ),
        ensure_ascii=False,
    )


    prompt = f"""
Bạn là bộ phân tích Technology Radar dành cho một lập trình viên full-stack.

Người dùng đặc biệt quan tâm tới:

- Artificial Intelligence
- LLM
- AI Agents
- Coding Agents
- MCP
- RAG
- AI developer tools

- Go
- Python
- TypeScript
- Rust

- React
- Next.js

- PostgreSQL
- Supabase

- Docker
- Cloudflare
- DevOps

- Backend
- System Design
- Distributed Systems
- Networking
- Cybersecurity

==================================================
INPUT
==================================================

ITEM TYPE HINT:
{candidate.get('item_type_hint')}

SOURCE:
{candidate.get('source_platform')}

TITLE:
{candidate.get('title')}

DESCRIPTION:
{candidate.get('description', '')[:6000]}

METADATA:
{metadata[:5000]}

URL:
{candidate.get('url')}

==================================================
ITEM TYPES
==================================================

AI_MODEL
DEV_TOOL
GITHUB_REPO
RELEASE
LANGUAGE
FRAMEWORK
PACKAGE
PAPER
SECURITY
OTHER

Lưu ý:

ITEM TYPE HINT đến từ collector có cấu trúc.

Nếu hint đã là:

AI_MODEL
DEV_TOOL
GITHUB_REPO
RELEASE
PACKAGE

thì KHÔNG tự ý đổi sang loại khác.

==================================================
SCORING
==================================================

TẤT CẢ SCORE BẮT BUỘC dùng THANG 0 ĐẾN 10.

Ví dụ đúng:

relevance_score = 8.5
novelty_score = 7.0
quality_score = 8.0
momentum_score = 6.5
importance_score = 7.5

KHÔNG dùng thang 0-1.

SAI:

0.85
0.7
0.92

ĐÚNG:

8.5
7.0
9.2


relevance_score:

Mức độ liên quan trực tiếp tới
AI / software engineering / developer workflow.

0:
hoàn toàn không liên quan.

10:
rất liên quan và có khả năng áp dụng trực tiếp.


novelty_score:

Mức độ mới, khác biệt hoặc có ý tưởng đáng chú ý.


quality_score:

Chất lượng kỹ thuật, độ trưởng thành,
documentation, ecosystem hoặc tín hiệu tin cậy.


momentum_score:

Mức độ đang tăng trưởng hoặc nhận được sự chú ý.

Dùng stars, downloads, likes, trending score,
activity hoặc release signal nếu input có cung cấp.


importance_score:

Tầm quan trọng tổng thể của technology signal.


==================================================
RADAR STATUS
==================================================

WATCH

→ mới hoặc thú vị,
nhưng chưa đủ thông tin.


ASSESS

→ đáng nghiên cứu nghiêm túc.


TRIAL

→ đủ hữu ích để thử nghiệm thực tế.


KHÔNG tự chọn ADOPT.

ADOPT chỉ do người dùng quyết định
sau khi đã dùng thực tế.


==================================================
RELEVANCE
==================================================

relevant=false nếu:

- repo demo không đáng kể
- package gần như không liên quan
- AI tool quá sơ sài
- tín hiệu quảng cáo yếu
- project không có giá trị kỹ thuật rõ ràng

==================================================
OUTPUT
==================================================

Trả về CHÍNH XÁC một JSON object.

Không Markdown.
Không giải thích ngoài JSON.

Ví dụ format:

{{
  "relevant": true,

  "item_type": "GITHUB_REPO",

  "category": "AI Agents",

  "relevance_score": 8.5,

  "novelty_score": 7.5,

  "quality_score": 8.0,

  "momentum_score": 7.0,

  "importance_score": 7.5,

  "summary":
    "2-4 câu tiếng Việt mô tả rõ công nghệ này là gì.",

  "why_it_matters":
    "1-3 câu giải thích vì sao nó đáng chú ý với lập trình viên.",

  "radar_status":
    "ASSESS"
}}

Không bịa dữ kiện ngoài input.
"""


    response = (
        get_client()
        .interactions
        .create(
            model=GEMINI_MODEL,
            input=prompt,
        )
    )


    data = extract_json(
        response.output_text
    )


    # ========================================================
    # ITEM TYPE
    # ========================================================

    data["item_type"] = (
        normalize_item_type(
            candidate,
            data,
        )
    )


    # ========================================================
    # SCORE NORMALIZATION
    # ========================================================

    data = normalize_scores(
        data
    )


    # ========================================================
    # BOOLEAN
    # ========================================================

    data["relevant"] = (
        normalize_bool(
            data.get(
                "relevant",
                False,
            )
        )
    )


    # ========================================================
    # RADAR STATUS
    # ========================================================

    data["radar_status"] = (
        normalize_radar_status(
            data.get(
                "radar_status"
            )
        )
    )


    # ========================================================
    # DEFAULT TEXT
    # ========================================================

    data["category"] = (
        str(
            data.get(
                "category"
            )
            or "Other"
        )
    )


    data["summary"] = (
        str(
            data.get(
                "summary"
            )
            or ""
        )
    )


    data["why_it_matters"] = (
        str(
            data.get(
                "why_it_matters"
            )
            or ""
        )
    )


    return data