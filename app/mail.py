"""Amazon SES send path — deployment smoke test only.

`docs/specs/SPEC_outbound_mail.md` specifies the production mail layer: suppression
checked before the transport (§14), an invitation record written before the send
(§12), content resolved from versioned templates in the System table (§8), delivery
reported as events (§13). None of that exists yet.

This module is only the bottom of that design — the transport call itself — exposed
so a deployment can prove three things: the task role can reach SES, the sender
identity is verified, and mail leaves the container. It is *not* the send contract
of §11, and nothing in the application should grow to depend on it.

Two rules of the specification are honoured here because they are properties of
message construction rather than of the layer above it:

  §9  header safety — a header value containing CR or LF is refused, never sanitized
  §6  the `From` header is composed from the configured identity, not from a caller

Transport error text is returned to the caller, which §11 forbids for the real send
path because the text may echo the rendered body and therefore the magic-link token.
It is acceptable here, and only here, because this path renders no token — the body
is the literal string the caller asked for. A real send must not copy this.
"""
from __future__ import annotations

import re

from .config import settings

_ADDR_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class MailError(RuntimeError):
    """The send was refused before the transport, or by it."""


def _check_header(value: str, label: str) -> str:
    """§9: refuse a header value containing a line break. Never transform it."""
    if "\r" in value or "\n" in value:
        raise MailError(f"{label} contains a line break")
    return value


def _check_display_name(value: str, label: str) -> str:
    _check_header(value, label)
    if '"' in value:
        raise MailError(f"{label} contains a quotation mark")
    return value


def _check_address(value: str, label: str) -> str:
    _check_header(value, label)
    value = value.strip()
    # §9: no network lookup. Syntax only.
    if not _ADDR_RE.match(value):
        raise MailError(f"{label} is not a syntactically valid e-mail address")
    return value


def from_header() -> str:
    """The `From` header value composed from configuration (§6)."""
    sender = _check_address(settings.mail_from, "fromEmail")
    name = _check_display_name(settings.mail_from_name, "fromName")
    return f'"{name}" <{sender}>' if name else sender


def send_email(to: str, subject: str, body: str) -> str:
    """Send one plain-text message through SES. Returns the provider message id.

    Raises MailError for a refused or failed send. Note that the real send operation
    of §11 returns an outcome and does not raise; this one raises because it has no
    invitation record to record an outcome on.
    """
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError

    recipient = _check_address(to, "recipient")
    sender = _check_address(settings.mail_from, "fromEmail")
    _check_header(subject, "subject")

    message = {
        "Simple": {
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
        }
    }
    kwargs = {
        "FromEmailAddress": from_header(),
        "Destination": {"ToAddresses": [recipient]},
        "Content": message,
    }
    if settings.mail_reply_to:
        kwargs["ReplyToAddresses"] = [_check_address(settings.mail_reply_to, "replyToEmail")]

    client = boto3.client("sesv2", region_name=settings.ses_region)
    try:
        resp = client.send_email(**kwargs)
    except ClientError as e:
        err = e.response.get("Error", {})
        raise MailError(f"{err.get('Code', 'ClientError')}: {err.get('Message', '')}") from e
    except BotoCoreError as e:
        raise MailError(type(e).__name__) from e
    return resp["MessageId"]
