"""Structure editorial plain text without accepting HTML or changing content."""
import re
from urllib.parse import parse_qs, urlparse

SECTION_TITLES = {"Ejemplo": "example", "Práctica": "practice", "Solución y comprobación": "solution", "Para profundizar": "reference", "Video complementario": "video"}
CODE_BLOCK = re.compile(r"^```([^\n`]*)\n([\s\S]*?)(?:^```[ \t]*$|\Z)", re.MULTILINE)


def video_embed(text):
    """Only YouTube's privacy-enhanced player; never embed an arbitrary URL."""
    for link in re.findall(r"https://[^\s<>]+", text):
        parsed = urlparse(link)
        host = parsed.netloc.lower()
        if host in ("www.youtube.com", "youtube.com") and parsed.path == "/watch":
            identifier = parse_qs(parsed.query).get("v", [""])[0]
        elif host == "youtu.be":
            identifier = parsed.path.lstrip("/")
        else:
            continue
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", identifier):
            return f"https://www.youtube-nocookie.com/embed/{identifier}"
    return ""


def reading_blocks(text):
    blocks, previous = [], 0
    for match in CODE_BLOCK.finditer(text):
        if text[previous:match.start()].strip():
            blocks.append({"code": False, "text": text[previous:match.start()].strip()})
        blocks.append({"code": True, "text": match[2].rstrip("\n"),
                       "language": match[1].strip() if re.fullmatch(r"[a-zA-Z0-9+-]*", match[1].strip()) else ""})
        previous = match.end()
    if text[previous:].strip():
        blocks.append({"code": False, "text": text[previous:].strip()})
    return blocks


def reading_sections(body):
    code = []

    def reserve(match):
        code.append(match[0])
        return f"\x00CODE{len(code) - 1}\x00"

    protected = CODE_BLOCK.sub(reserve, body or "")
    sections = []
    for paragraph in re.split(r"\n\s*\n", protected):
        lines = paragraph.strip().splitlines()
        if not lines:
            continue
        if lines[0] in SECTION_TITLES:
            sections.append({"title": lines[0], "kind": SECTION_TITLES[lines[0]], "text": "\n".join(lines[1:])})
        elif sections and sections[-1]["kind"] != "text":
            sections[-1]["text"] += "\n\n" + paragraph.strip()
        else:
            sections.append({"title": "", "kind": "text", "text": paragraph.strip()})
    for section in sections:
        section["text"] = re.sub(r"\x00CODE(\d+)\x00", lambda match: code[int(match[1])], section["text"])
        section["blocks"] = reading_blocks(section["text"])
        section["embed_url"] = video_embed(section["text"]) if section["kind"] == "video" else ""
    return sections
