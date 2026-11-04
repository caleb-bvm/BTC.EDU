"""Read, write and compile gettext catalogs without the GNU gettext binaries.

Django's makemessages and compilemessages need xgettext and msgfmt, which are not
part of the project's Python environment. These helpers cover what the project uses:
msgctxt, plurals, references and the fuzzy flag.
"""
import ast
import io
import re
import struct
import tokenize
from dataclasses import dataclass, field

from django.utils.translation.template import templatize

PYTHON_KEYWORDS = {
    "_": ("msgid",), "gettext": ("msgid",), "gettext_lazy": ("msgid",), "gettext_noop": ("msgid",),
    "ngettext": ("msgid", "plural"), "ngettext_lazy": ("msgid", "plural"),
    "pgettext": ("context", "msgid"), "pgettext_lazy": ("context", "msgid"),
    "npgettext": ("context", "msgid", "plural"), "npgettext_lazy": ("context", "msgid", "plural"),
}


@dataclass
class Entry:
    msgid: str
    msgstr: str = ""
    context: str | None = None
    plural: str | None = None
    plural_strs: list = field(default_factory=list)
    references: list = field(default_factory=list)
    comments: list = field(default_factory=list)
    fuzzy: bool = False

    @property
    def key(self):
        return (self.context, self.msgid, self.plural is not None)

    @property
    def translated(self):
        if self.fuzzy:
            return False
        return bool(self.plural_strs) and all(self.plural_strs) if self.plural is not None else bool(self.msgstr)


def _unquote(line):
    return ast.literal_eval(line)


def read_po(path):
    """Return (header, entries) where entries keeps the file order."""
    if not path.exists():
        return "", []
    entries, header, current, last = [], "", None, None

    def finish():
        nonlocal current, header
        if current is not None:
            if current.msgid == "" and current.context is None:
                header = current.msgstr
            else:
                entries.append(current)
        current = None

    for raw in path.read_text(encoding="utf-8").splitlines() + [""]:
        line = raw.strip()
        if not line:
            finish()
            continue
        if current is None:
            current = Entry(msgid="")
        if line.startswith("#~"):
            current = None
            continue
        if line.startswith("#:"):
            current.references.extend(line[2:].split())
        elif line.startswith("#,"):
            current.fuzzy = "fuzzy" in line
        elif line.startswith("#."):
            current.comments.append(line[2:].strip())
        elif line.startswith("#"):
            continue
        elif line.startswith("msgctxt "):
            current.context, last = _unquote(line[8:]), "context"
        elif line.startswith("msgid_plural "):
            current.plural, last = _unquote(line[13:]), "plural"
        elif line.startswith("msgid "):
            current.msgid, last = _unquote(line[6:]), "msgid"
        elif line.startswith("msgstr["):
            index = int(line[7:line.index("]")])
            while len(current.plural_strs) <= index:
                current.plural_strs.append("")
            current.plural_strs[index] = _unquote(line[line.index("]") + 2:])
            last = ("plural_strs", index)
        elif line.startswith("msgstr "):
            current.msgstr, last = _unquote(line[7:]), "msgstr"
        elif line.startswith('"'):
            value = _unquote(line)
            if isinstance(last, tuple):
                current.plural_strs[last[1]] += value
            else:
                setattr(current, last, getattr(current, last) + value)
    return header, entries


def _quote(text):
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\t", "\\t").replace("\r", "\\r")
    if "\n" not in text.rstrip("\n"):
        return '"%s"' % escaped.replace("\n", "\\n")
    parts = escaped.split("\n")
    lines = ['""'] + ['"%s\\n"' % part for part in parts[:-1]]
    if parts[-1]:
        lines.append('"%s"' % parts[-1])
    return "\n".join(lines)


def write_po(path, header, entries):
    out = ['msgid ""', "msgstr " + _quote(header), ""]
    for entry in entries:
        out.extend("#. " + comment for comment in entry.comments)
        if entry.references:
            out.append("#: " + " ".join(sorted(set(entry.references))))
        if entry.fuzzy:
            out.append("#, fuzzy")
        if entry.context is not None:
            out.append("msgctxt " + _quote(entry.context))
        out.append("msgid " + _quote(entry.msgid))
        if entry.plural is not None:
            out.append("msgid_plural " + _quote(entry.plural))
            for index, value in enumerate(entry.plural_strs or ["", ""]):
                out.append(f"msgstr[{index}] " + _quote(value))
        else:
            out.append("msgstr " + _quote(entry.msgstr))
        out.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8", newline="\n")


def write_mo(path, header, entries):
    """Compile translated entries; untranslated and fuzzy ones fall back to the source text."""
    pairs = {"": header}
    for entry in entries:
        if not entry.translated:
            continue
        key = entry.msgid if entry.context is None else f"{entry.context}\x04{entry.msgid}"
        if entry.plural is not None:
            pairs[f"{key}\x00{entry.plural}"] = "\x00".join(entry.plural_strs)
        else:
            pairs[key] = entry.msgstr
    keys = sorted(pairs, key=lambda item: item.encode("utf-8"))
    ids = b"".join(k.encode("utf-8") + b"\x00" for k in keys)
    strs = b"".join(pairs[k].encode("utf-8") + b"\x00" for k in keys)
    count = len(keys)
    key_start = 7 * 4 + 16 * count
    value_start = key_start + len(ids)
    offsets, key_offset, value_offset = [], 0, 0
    for k in keys:
        key_bytes, value_bytes = k.encode("utf-8"), pairs[k].encode("utf-8")
        offsets.append((len(key_bytes), key_start + key_offset, len(value_bytes), value_start + value_offset))
        key_offset += len(key_bytes) + 1
        value_offset += len(value_bytes) + 1
    output = struct.pack("Iiiiiii", 0x950412DE, 0, count, 7 * 4, 7 * 4 + count * 8, 0, 0)
    output += b"".join(struct.pack("ii", length, offset) for length, offset, _, _ in offsets)
    output += b"".join(struct.pack("ii", length, offset) for _, _, length, offset in offsets)
    path.write_bytes(output + ids + strs)


def _calls_from_tokens(source, origin):
    """Yield (fields, line) for gettext-style calls with literal arguments."""
    tokens = [token for token in tokenize.generate_tokens(io.StringIO(source).readline)
              if token.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT)]
    for index, token in enumerate(tokens):
        names = PYTHON_KEYWORDS.get(token.string) if token.type == tokenize.NAME else None
        if not names or index + 1 >= len(tokens) or tokens[index + 1].string != "(":
            continue
        if index and tokens[index - 1].string in ("def", "."):
            continue
        values, cursor = [], index + 2
        while len(values) < len(names) and cursor < len(tokens):
            parts = []
            while cursor < len(tokens) and tokens[cursor].type == tokenize.STRING:
                parts.append(tokens[cursor].string)
                cursor += 1
            if not parts or any(part.lstrip("rRbBuU")[:1] not in "'\"" or part[:1] in "fF" for part in parts):
                break
            values.append("".join(ast.literal_eval(part) for part in parts))
            if cursor < len(tokens) and tokens[cursor].string == ",":
                cursor += 1
        if len(values) == len(names):
            yield dict(zip(names, values)), token.start[0]


def extract_python(path, relative):
    yield from (
        (fields, f"{relative}:{line}") for fields, line in _calls_from_tokens(path.read_text(encoding="utf-8"), relative)
    )


def extract_template(path, relative):
    source = templatize(path.read_text(encoding="utf-8"), origin=str(path))
    yield from ((fields, f"{relative}:{line}") for fields, line in _calls_from_tokens(source, relative))


PLACEHOLDER = re.compile(r"%\(\w+\)[sdif]|%[sdif]|\{\w*\}")


def placeholders(text):
    return sorted(PLACEHOLDER.findall(text))
