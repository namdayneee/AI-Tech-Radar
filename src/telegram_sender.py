import socket
import time

import requests
import urllib3.util.connection as urllib3_cn

from src.config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)


# ============================================================
# NETWORK
# ============================================================

# Trên mạng hiện tại IPv6 tới Telegram
# có lúc bị TLS ConnectionResetError.
#
# Ép requests/urllib3 dùng IPv4.
urllib3_cn.allowed_gai_family = (
    lambda: socket.AF_INET
)


# ============================================================
# MESSAGE SPLITTER
# ============================================================

def _split_message(
    text: str,
    max_len: int = 3500,
) -> list[str]:
    """
    Telegram có giới hạn độ dài message.

    Nếu message quá dài:
    tự động chia thành nhiều message nhỏ.
    """

    if len(text) <= max_len:
        return [text]

    chunks = []

    current = ""

    for paragraph in text.split("\n"):

        candidate = (
            f"{current}\n{paragraph}"
        ).strip()

        if len(candidate) <= max_len:

            current = candidate

        else:

            if current:
                chunks.append(current)

            while (
                len(paragraph)
                > max_len
            ):

                chunks.append(
                    paragraph[:max_len]
                )

                paragraph = (
                    paragraph[max_len:]
                )

            current = paragraph

    if current:
        chunks.append(current)

    return chunks


# ============================================================
# RETRY
# ============================================================

def _send_with_retry(
    endpoint: str,
    payload: dict,
    retries: int = 3,
):
    """
    Gửi Telegram có retry.

    Ví dụ:
    attempt 1 fail
    → chờ
    → attempt 2
    """

    last_error = None

    for attempt in range(
        1,
        retries + 1,
    ):

        try:

            response = requests.post(
                endpoint,
                json=payload,
                timeout=30,
            )

            response.raise_for_status()

            return response

        except requests.RequestException as exc:

            last_error = exc

            print(
                "[WARN] Telegram "
                f"attempt "
                f"{attempt}/{retries} "
                f"failed: {exc}"
            )

            if attempt < retries:

                wait_time = (
                    attempt * 2
                )

                print(
                    f"[INFO] Retry in "
                    f"{wait_time}s..."
                )

                time.sleep(
                    wait_time
                )

    raise last_error


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def send_telegram(
    text: str,
):
    """
    Hàm chính để gửi Telegram.
    """

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):

        raise RuntimeError(
            "Thiếu TELEGRAM_BOT_TOKEN "
            "hoặc TELEGRAM_CHAT_ID."
        )

    endpoint = (
        "https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/"
        "sendMessage"
    )

    messages = _split_message(
        text
    )

    for chunk in messages:

        _send_with_retry(
            endpoint,
            {
                "chat_id":
                    TELEGRAM_CHAT_ID,

                "text":
                    chunk,

                "disable_web_page_preview":
                    True,
            },
        )