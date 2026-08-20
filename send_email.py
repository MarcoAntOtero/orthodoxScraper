"""
Drafts and sends an email through YOUR Gmail account, with an optional
file attachment (e.g. the weekly bulletin PDF).

One-time setup required before this will run see the bottom of this
file / the conversation for the Google Cloud Console steps. I
"""

import base64
import mimetypes
import os
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Least-privilege scope: lets this script send mail as you, but can't
# read your inbox, contacts, or anything else. If you ever want a
# broader scope later, delete token.json so it re-prompts for consent.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

CREDENTIALS_PATH = "credentials.json"
TOKEN_PATH = "token.json"


def get_credentials() -> Credentials:
    """
    Loads saved OAuth credentials if present, refreshing them if expired.
    If there's no valid token yet, runs the interactive consent flow --
    this opens your default browser, you log into Google and approve
    access, and the resulting token is saved to TOKEN_PATH for next time.
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"{CREDENTIALS_PATH} not found. You need to download this from "
                    "Google Cloud Console first -- see the setup steps."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    return creds


def build_message(
    sender: str,
    to: str,
    subject: str,
    body: str,
    attachment_path: str | None = None,
    cc: str | None = None,
    bcc: str | None = None,
) -> dict:
    """
    Builds a Gmail API-ready message dict. If attachment_path is given,
    the file is read as raw bytes and attached with the right MIME type
    (guessed from the file extension -- application/pdf for a .pdf file)
    so it shows up as a proper attachment, not inline garbage text.

    cc/bcc each take a single string -- for multiple people, comma-separate
    them yourself: "a@x.com, b@x.com, c@x.com". That's exactly how the
    "To" header already works, and how any email client builds one.
    """
    message = EmailMessage()
    message["To"] = to
    message["From"] = sender
    message["Subject"] = subject
    if cc:
        message["Cc"] = cc
    if bcc:
        message["Bcc"] = bcc
    message.set_content(body)

    if attachment_path:
        mime_type, _ = mimetypes.guess_type(attachment_path)
        maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)
        with open(attachment_path, "rb") as f:
            message.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=os.path.basename(attachment_path),
            )

    # Gmail API wants the whole RFC822 message base64url-encoded.
    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": encoded}


def send_email(
    to: str,
    subject: str,
    body: str,
    attachment_path: str | None = None,
    cc: str | None = None,
    bcc: str | None = None,
) -> None:
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    # "me" is a Gmail API shorthand for "whichever account authorized this token".
    message = build_message(
        sender="me", to=to, subject=subject, body=body,
        attachment_path=attachment_path, cc=cc, bcc=bcc,
    )
    sent = service.users().messages().send(userId="me", body=message).execute()
    print(f"Sent. Message ID: {sent['id']}")


if __name__ == "__main__":
    send_email(
        to="oterom935@gmail.com",
        cc="marco.otero@gwmail.gwu.edu",
        subject="Vespers Variable",
        body="Attached is this week's bulletin.",
        attachment_path="output.pdf",
    )
