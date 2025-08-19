import re
from typing import List, Set

SEGMENT_DELIM = re.compile(r"^(={6,}.*)$", re.MULTILINE)

def split_segments(text: str) -> List[str]:
    """
    以連續6個=開頭的行為分隔，保留分隔行，並去除每段首尾空白行。
    """
    text = text.lstrip('\n')
    parts = []
    last = 0
    for m in SEGMENT_DELIM.finditer(text):
        if m.start() > last:
            seg = text[last:m.start()]
            seg = seg.strip('\n')
            if seg:
                parts.append(seg)
        delim = m.group(1)
        last = m.end()
        if delim:
            parts.append(delim)
    if last < len(text):
        seg = text[last:]
        seg = seg.strip('\n')
        if seg:
            parts.append(seg)
    result = []
    buf = ""
    for p in parts:
        if p.startswith("="):
            if buf:
                result.append(buf.lstrip('\n'))
            buf = p
        else:
            buf += "\n" + p
    if buf:
        result.append(buf.lstrip('\n'))
    return result

def deduplicate_segments(segments: List[str]) -> List[str]:
    seen: Set[str] = set()
    result = []
    for seg in segments:
        norm = seg.strip()
        if norm not in seen:
            seen.add(norm)
            result.append(seg)
    return result
