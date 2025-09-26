# auth.py
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

TOKEN_FILE = "token.json"
CLIENT_SECRET_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]  # minimal

def get_credentials():
    """Return valid creds or run the browser flow once. No extra side effects."""
    creds = None
    if Path(TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # creds.refresh(Request()) is optional; the client refreshes on first call too.
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            # For desktop demo; replace with your web redirect flow if needed
            creds = flow.run_local_server(port=8765, prompt="consent")
        Path(TOKEN_FILE).write_text(creds.to_json())

    return creds



# from __future__ import annotations
# import os
# import json
# from pathlib import Path

# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build

# # ---- Scopes: least privilege for your use case
# SCOPES = [
#     "https://www.googleapis.com/auth/drive.readonly",  # read user Drive files
#     "https://www.googleapis.com/auth/documents",       # create/edit Docs
# ]

# CLIENT_SECRET_FILE = "client_secret.json"  # downloaded from Cloud Console
# TOKEN_FILE = "token.json"                  # will be created after first auth

# def get_credentials():
#     creds = None
#     if Path(TOKEN_FILE).exists():
#         creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

#     # If no valid creds, perform the local OAuth flow (opens browser)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             # auto-refresh
#             creds.refresh(request=None)  # google-auth handles HTTP by default
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
#             # Runs a loopback server on localhost and opens browser
#             creds = flow.run_local_server(port=8765, prompt="consent")
#         # Save the refreshable token
#         with open(TOKEN_FILE, "w") as f:
#             f.write(creds.to_json())
#     return creds

# def demo_list_drive(creds, page_size=5):
#     drive = build("drive", "v3", credentials=creds)
#     results = drive.files().list(
#         pageSize=page_size,
#         fields="files(id, name, mimeType)"
#     ).execute()
#     files = results.get("files", [])
#     print("\nDrive sample files:")
#     for f in files:
#         print(f"- {f['name']}  ({f['mimeType']})  id={f['id']}")

# def demo_create_doc(creds):
#     docs = build("docs", "v1", credentials=creds)
#     # 1) Create an empty doc
#     doc = docs.documents().create(body={"title": "StudyAI Demo – Generated"}).execute()
#     doc_id = doc.get("documentId")
#     print(f"\nCreated Google Doc: {doc.get('title')} (id={doc_id})")

#     # 2) Insert some content
#     requests = [
#         {"insertText": {"location": {"index": 1}, "text": "## StudyAI Summary\n\n- Topic: Demo\n- Bullet 1\n- Bullet 2\n"}}
#     ]
#     docs.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
#     print("Inserted demo content into the doc.")
#     return doc_id

# if __name__ == "__main__":
#     # Safety checks
#     if not Path(CLIENT_SECRET_FILE).exists():
#         raise FileNotFoundError(
#             "client_secret.json not found. Download it from Google Cloud Console → Credentials."
#         )

#     creds = get_credentials()
#     demo_list_drive(creds)
#     demo_create_doc(creds)
#     print("\n✅ OAuth works. Token saved to token.json (contains refresh token).")
