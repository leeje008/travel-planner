"""core.utils.text - 텍스트 정규화 유틸리티.

Unicode NFC 정규화로 한국어 자모 분리 문제를 방지합니다.
"""

import re
import unicodedata


def normalize_text(text: str) -> str:
    """텍스트를 NFC 정규화 + 공백 정규화합니다.

    - Unicode NFC 정규화 (한국어 자모 분리 방지)
    - 연속 공백을 단일 공백으로 축소
    - 양쪽 공백 제거

    Args:
        text: 원본 텍스트.

    Returns:
        정규화된 텍스트.
    """
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_place_name(name: str) -> str:
    """장소명에서 괄호 내용 및 특수문자를 제거합니다.

    예: "성산일출봉 (UNESCO)" → "성산일출봉"
        "카페*드*플로르" → "카페드플로르"

    Args:
        name: 원본 장소명.

    Returns:
        정리된 장소명.
    """
    # 괄호 내용 제거: (), [], 【】
    name = re.sub(r"[(\[【].*?[)\]】]", "", name)
    # 특수문자 제거 (한글, 영문, 숫자, 공백만 남김)
    name = re.sub(r"[^\w\s가-힣a-zA-Z0-9]", "", name)
    return normalize_text(name)


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """텍스트를 지정 길이로 잘라냅니다.

    Args:
        text: 원본 텍스트.
        max_length: 최대 길이 (suffix 포함).
        suffix: 말줄임 표시.

    Returns:
        잘린 텍스트. max_length 이하이면 원본 그대로 반환.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def is_korean(text: str) -> bool:
    """텍스트에 한국어가 포함되어 있는지 확인합니다.

    Args:
        text: 확인할 텍스트.

    Returns:
        한국어 문자가 하나라도 있으면 True.
    """
    return bool(re.search(r"[가-힣ㄱ-ㅎㅏ-ㅣ]", text))
