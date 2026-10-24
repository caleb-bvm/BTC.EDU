"""OpenTimestamps proofs for certificate fingerprints.

The certificate data file hashes to its SHA-256 fingerprint, so the .ots proof
stamps that file. Calendars return a pending proof at once; hours later the
same calendars return the path to a Bitcoin block header. Anyone can check the
proof with an OpenTimestamps client without trusting BTC.EDU.
"""
import hashlib
import io
import os
from dataclasses import dataclass, field
from urllib.parse import urlsplit

import httpx
from django.conf import settings
from django.db import transaction
from django.utils import timezone

MAGIC = b"\x00OpenTimestamps\x00\x00Proof\x00\xbf\x89\xe2\xe8\x84\xe8\x92\x94"
PENDING = bytes.fromhex("83dfe30d2ef90c8e")
BITCOIN = bytes.fromhex("0588960d73d71901")
UNARY = {0x02: lambda m: hashlib.sha1(m).digest(), 0x03: lambda m: hashlib.new("ripemd160", m).digest(),
         0x08: lambda m: hashlib.sha256(m).digest(),
         0xf2: lambda m: m[::-1], 0xf3: lambda m: m.hex().encode()}
BINARY = {0xf0: lambda m, a: m + a, 0xf1: lambda m, a: a + m}
MAX_MESSAGE = 4096


class ProofError(ValueError):
    pass


def write_varuint(out, value):
    while True:
        byte = value & 0x7f
        value >>= 7
        out.write(bytes([byte | 0x80 if value else byte]))
        if not value:
            return


def read_varuint(data):
    value, shift = 0, 0
    while True:
        chunk = data.read(1)
        if not chunk:
            raise ProofError("Prueba incompleta.")
        value |= (chunk[0] & 0x7f) << shift
        if not chunk[0] & 0x80:
            return value
        shift += 7
        if shift > 63:
            raise ProofError("Número fuera de rango.")


def write_varbytes(out, value):
    write_varuint(out, len(value))
    out.write(value)


def read_varbytes(data, limit=MAX_MESSAGE):
    size = read_varuint(data)
    value = data.read(size)
    if size > limit or len(value) != size:
        raise ProofError("Datos fuera de rango.")
    return value


@dataclass
class Timestamp:
    message: bytes
    attestations: list = field(default_factory=list)  # (tag, payload)
    ops: dict = field(default_factory=dict)  # (tag, argument) -> Timestamp

    def merge(self, other):
        for attestation in other.attestations:
            if attestation not in self.attestations:
                self.attestations.append(attestation)
        for op, stamp in other.ops.items():
            if op in self.ops:
                self.ops[op].merge(stamp)
            else:
                self.ops[op] = stamp

    def walk(self):
        yield self
        for stamp in self.ops.values():
            yield from stamp.walk()


def apply_op(op, message):
    tag, argument = op
    result = BINARY[tag](message, argument) if tag in BINARY else UNARY[tag](message)
    if len(result) > MAX_MESSAGE:
        raise ProofError("Mensaje demasiado largo.")
    return result


def read_timestamp(data, message, depth=0):
    if depth > 256:
        raise ProofError("Prueba demasiado profunda.")
    stamp = Timestamp(message)

    def branch(tag):
        if tag == 0x00:
            kind = data.read(8)
            if len(kind) != 8:
                raise ProofError("Atestación incompleta.")
            stamp.attestations.append((kind, read_varbytes(data)))
            return
        if tag in BINARY:
            op = (tag, read_varbytes(data))
        elif tag in UNARY:
            op = (tag, b"")
        else:
            raise ProofError("Operación desconocida.")
        child = read_timestamp(data, apply_op(op, message), depth + 1)
        if op in stamp.ops:
            stamp.ops[op].merge(child)
        else:
            stamp.ops[op] = child

    tag = data.read(1)
    while tag == b"\xff":
        branch(data.read(1)[0])
        tag = data.read(1)
    if not tag:
        raise ProofError("Prueba incompleta.")
    branch(tag[0])
    return stamp


def write_timestamp(out, stamp):
    attestations = sorted(stamp.attestations)
    ops = sorted(stamp.ops.items())
    if not attestations and not ops:
        raise ProofError("Prueba vacía.")
    entries = [("attestation", item) for item in attestations] + [("op", item) for item in ops]
    for position, (kind, item) in enumerate(entries):
        if position < len(entries) - 1:
            out.write(b"\xff")
        if kind == "attestation":
            out.write(b"\x00" + item[0])
            write_varbytes(out, item[1])
        else:
            (tag, argument), child = item
            out.write(bytes([tag]))
            if tag in BINARY:
                write_varbytes(out, argument)
            write_timestamp(out, child)


def parse_response(content, message):
    data = io.BytesIO(content)
    stamp = read_timestamp(data, message)
    if data.read(1):
        raise ProofError("Respuesta con datos sobrantes.")
    return stamp


def proof_file(digest, stamp):
    out = io.BytesIO()
    out.write(MAGIC)
    write_varuint(out, 1)
    out.write(b"\x08" + digest)
    write_timestamp(out, stamp)
    return out.getvalue()


def read_proof_file(content):
    data = io.BytesIO(bytes(content))
    if data.read(len(MAGIC)) != MAGIC or read_varuint(data) != 1 or data.read(1) != b"\x08":
        raise ProofError("No es una prueba OpenTimestamps compatible.")
    digest = data.read(32)
    if len(digest) != 32:
        raise ProofError("Prueba incompleta.")
    stamp = read_timestamp(data, digest)
    if data.read(1):
        raise ProofError("Prueba con datos sobrantes.")
    return digest, stamp


def pending_uris(stamp):
    for node in stamp.walk():
        for kind, payload in node.attestations:
            if kind == PENDING:
                yield node, read_varbytes(io.BytesIO(payload), 1000).decode("utf-8", "replace")


def bitcoin_heights(stamp):
    return sorted({read_varuint(io.BytesIO(payload)) for node in stamp.walk() for kind, payload in node.attestations if kind == BITCOIN})


def allowed_calendar(uri):
    parts = urlsplit(uri)
    return (parts.scheme == "https" and not parts.username and not parts.password and not parts.query and not parts.fragment
            and parts.hostname in settings.CERTIFICATE_OTS_TRUSTED_HOSTS)


def client(transport=None):
    return httpx.Client(timeout=settings.CERTIFICATE_OTS_TIMEOUT, trust_env=False, follow_redirects=False, transport=transport,
                        headers={"Accept": "application/vnd.opentimestamps.v1", "User-Agent": "BTC.EDU"})


def submit(digest, transport=None):
    """Return a .ots file for the digest, or None when no calendar answered."""
    nonce = os.urandom(16)
    root = Timestamp(digest)
    blinded = Timestamp(digest + nonce)
    root.ops[(0xf0, nonce)] = blinded
    commitment = hashlib.sha256(digest + nonce).digest()
    hashed = Timestamp(commitment)
    blinded.ops[(0x08, b"")] = hashed
    answered = []
    with client(transport) as http:
        for calendar in settings.CERTIFICATE_OTS_CALENDARS:
            if not allowed_calendar(calendar):
                continue
            try:
                response = http.post(calendar.rstrip("/") + "/digest", content=commitment)
                if response.status_code != 200 or len(response.content) > 10000:
                    continue
                hashed.merge(parse_response(response.content, commitment))
                answered.append(calendar)
            except (httpx.HTTPError, ValueError):
                continue
    return (proof_file(digest, root), answered) if answered else (None, [])


def upgrade(content, transport=None):
    """Ask each pending calendar for the Bitcoin path; return (proof, changed)."""
    digest, root = read_proof_file(content)
    changed = False
    with client(transport) as http:
        for node, uri in list(pending_uris(root)):
            if not allowed_calendar(uri):
                continue
            try:
                response = http.get(uri.rstrip("/") + "/timestamp/" + node.message.hex())
                if response.status_code != 200 or len(response.content) > 10000:
                    continue
                node.merge(parse_response(response.content, node.message))
                changed = True
            except (httpx.HTTPError, ValueError):
                continue
    return proof_file(digest, root), changed


def describe(record):
    if record is None:
        return {"state": "none"}
    try:
        _, root = read_proof_file(record.proof)
    except ValueError:
        return {"state": "invalid"}
    heights = bitcoin_heights(root)
    return {"state": "confirmed" if heights else "pending", "height": heights[0] if heights else None,
            "calendars": record.calendars, "submitted_at": record.submitted_at}


def stamp_certificate(certificate, transport=None):
    from .certificate_integrity import certificate_intact
    from .models import CertificateTimestamp
    if not settings.CERTIFICATE_TIMESTAMPS or hasattr(certificate, "revocation") or not certificate_intact(certificate):
        return None
    existing = CertificateTimestamp.objects.filter(certificate=certificate).first()
    if existing:
        return existing
    proof, calendars = submit(bytes.fromhex(certificate.fingerprint), transport)
    if proof is None:
        return None
    with transaction.atomic():
        record, _ = CertificateTimestamp.objects.get_or_create(certificate=certificate, defaults={
            "proof": proof, "calendars": calendars, "submitted_at": timezone.now()})
    return record


def upgrade_record(record, transport=None):
    if record.bitcoin_height:
        return record
    try:
        proof, changed = upgrade(record.proof, transport)
        _, root = read_proof_file(proof)
    except (httpx.HTTPError, ValueError):
        return record
    heights = bitcoin_heights(root)
    fields = {"checked_at": timezone.now()}
    if changed:
        fields.update(proof=proof, bitcoin_height=heights[0] if heights else None)
    type(record).objects.filter(pk=record.pk).update(**fields)
    record.refresh_from_db()
    return record
