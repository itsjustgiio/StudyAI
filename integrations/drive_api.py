# drive_api.py
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

from oauth import get_credentials

# Common mime types you may care about
MIME = {
    "pdf": "application/pdf",
    "gdoc": "application/vnd.google-apps.document",
    "gslide": "application/vnd.google-apps.presentation",
    "gsheet": "application/vnd.google-apps.spreadsheet",
    "gfile": "application/vnd.google-apps.file",  # generic g-app
}

def _svc():
    creds = get_credentials()
    return build("drive", "v3", credentials=creds)

def list_files(q_text: Optional[str] = None,
               mime_in: Optional[List[str]] = None,
               page_token: Optional[str] = None,
               page_size: int = 25) -> Dict:
    """
    Return minimal metadata your UI can render quickly.
    """
    drive = _svc()

    # Build Drive query string
    q_parts = ["trashed = false"]
    if q_text:
        # full-text search (name & content where supported)
        escaped_text = q_text.replace("'", "\\'")
        q_parts.append(f"name contains '{escaped_text}'")
    if mime_in:
        mimes = " or ".join([f"mimeType = '{m}'" for m in mime_in])
        q_parts.append(f"({mimes})")

    query = " and ".join(q_parts)

    resp = drive.files().list(
        q=query,
        spaces="drive",
        pageSize=page_size,
        pageToken=page_token,
        fields="nextPageToken, files(id, name, mimeType, modifiedTime, size, iconLink, owners(displayName))",
        orderBy="modifiedTime desc"
    ).execute()

    return {
        "nextPageToken": resp.get("nextPageToken"),
        "files": [
            {
                "id": f["id"],
                "name": f["name"],
                "mimeType": f["mimeType"],
                "modifiedTime": f.get("modifiedTime"),
                "size": f.get("size"),
                "icon": f.get("iconLink"),
                "owner": (f.get("owners") or [{}])[0].get("displayName")
            }
            for f in resp.get("files", [])
        ]
    }

def download_file(file_id: str, dest_path: str) -> str:
    """
    Download a Drive file to dest_path.
    - If it's a Google Doc/Slide/Sheet, export to PDF first.
    - If it's a binary (e.g., PDF), download as-is.
    Returns the final local path.
    """
    drive = _svc()

    meta = drive.files().get(fileId=file_id, fields="name, mimeType").execute()
    name = meta["name"]
    mime = meta["mimeType"]

    # Decide how to fetch
    if mime == MIME["gdoc"]:
        export_mime = MIME["pdf"]
        request = drive.files().export_media(fileId=file_id, mimeType=export_mime)
        out_path = _ensure_ext(dest_path, ".pdf", default_name=name)
    elif mime == MIME["gslide"]:
        export_mime = MIME["pdf"]
        request = drive.files().export_media(fileId=file_id, mimeType=export_mime)
        out_path = _ensure_ext(dest_path, ".pdf", default_name=name)
    elif mime == MIME["gsheet"]:
        export_mime = MIME["pdf"]
        request = drive.files().export_media(fileId=file_id, mimeType=export_mime)
        out_path = _ensure_ext(dest_path, ".pdf", default_name=name)
    else:
        # regular file (e.g., application/pdf)
        request = drive.files().get_media(fileId=file_id)
        # Keep original name if dest_path is a directory
        out_path = _join_with_name(dest_path, name)

    # Stream to disk
    fh = io.FileIO(out_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        # Optional: print(f"Download {int(status.progress()*100)}%")

    fh.close()
    return out_path

# ---- helpers ----
import os
def _ensure_ext(dest: str, ext: str, default_name: str) -> str:
    if dest.endswith(os.sep) or os.path.isdir(dest):
        os.makedirs(dest, exist_ok=True)
        base = os.path.splitext(default_name)[0] + ext
        return os.path.join(dest, base)
    root, _ = os.path.splitext(dest)
    return root + ext

def _join_with_name(dest: str, name: str) -> str:
    if dest.endswith(os.sep) or os.path.isdir(dest):
        os.makedirs(dest, exist_ok=True)
        return os.path.join(dest, name)
    return dest