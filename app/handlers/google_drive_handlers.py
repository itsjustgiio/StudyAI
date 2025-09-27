# google_drive_handler.py
import flet as ft
import threading
from typing import Any, List, Dict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Your integrations
from integrations.oauth import get_credentials
from integrations.drive_api import MIME, list_files, download_file


class GoogleDriveHandler:
    def __init__(self, page: ft.Page):
        self.page = page
        self.is_connected = False
        self.user_credentials = None
        self.drive_service = None

    # ------------------ Connect (threaded) ------------------

    def connect_drive(self, e: Any = None):
        """Spawn a background thread so UI stays responsive."""
        self._show_message("🔗 Opening Google Sign-In...")
        threading.Thread(target=self._do_connect, daemon=True).start()

    def _do_connect(self):
        try:
            creds = get_credentials()  # opens browser; returns when finished
            self.user_credentials = creds
            # Optional: you can skip building drive_service since drive_api uses its own _svc()
            self.drive_service = build("drive", "v3", credentials=creds)
            self.is_connected = True

            # update UI back on main thread
            def after_connect():
                self._show_message("✅ Connected to Google Drive")
                # (Optional) immediately open the picker; or keep behind a button
                # self.browse_drive()

            self.page.call_from_main_thread(after_connect)

        except HttpError as he:
            self.page.call_from_main_thread(
                lambda: self._show_message(f"❌ Google API error: {he}", success=False)
            )
        except Exception as ex:
            self.page.call_from_main_thread(
                lambda: self._show_message(f"❌ Connection error: {ex}", success=False)
            )

    # ------------------ Browse & Download ------------------
    def download_notes(self, e: Any = None):
    # """
    #     Opens a Drive file picker (PDF/Docs/Slides/Sheets) and downloads the selected file.
    #     Requires that the user has already connected Google Drive.
    # """
        if not self._check_connection():
            return
        self._open_drive_picker_and_download()

    def _open_drive_picker_and_download(self):
        """List files via drive_api and render a picker dialog; download on selection."""
        try:
            payload = list_files(
                q_text=None,
                mime_in=[MIME["pdf"], MIME["gdoc"], MIME["gslide"], MIME["gsheet"]],
                page_size=50,
            )
            files = payload.get("files", [])
            if not files:
                self._show_message("📭 No Drive files found")
                return

            # Handler for clicking a file in the list
            def on_pick(file_obj):
                # Download on a background thread so the UI doesn't freeze
                def _do_download():
                    try:
                        local_path = download_file(
                            file_id=file_obj["id"],
                            dest_path="./data/textbooks/"  # change folder if you want
                        )
                        self.page.call_from_main_thread(
                            lambda: self._show_message(f"✅ Downloaded: {file_obj['name']}\n→ {local_path}")
                        )
                    except Exception as ex:
                        self.page.call_from_main_thread(
                            lambda: self._show_message(f"❌ Download failed: {ex}", success=False)
                        )
                    finally:
                        # Close the dialog on the UI thread
                        def _close():
                            if self.page.dialog:
                                self.page.dialog.open = False
                                self.page.update()
                        self.page.call_from_main_thread(_close)

                import threading
                threading.Thread(target=_do_download, daemon=True).start()

            # Build dialog list
            items = [
                ft.ListTile(
                    leading=ft.Icon(ft.icons.INSERT_DRIVE_FILE_ROUNDED),
                    title=ft.Text(f["name"]),
                    subtitle=ft.Text(f'{f["mimeType"]} • {f.get("modifiedTime","")}'),
                    on_click=(lambda ev, file=f: on_pick(file)),
                )
                for f in files
            ]

            dlg = ft.AlertDialog(
                title=ft.Text("Select a Drive file to download"),
                content=ft.Column(items, scroll=ft.ScrollMode.AUTO, width=520, height=420),
            )
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()

        except Exception as ex:
            self._show_message(f"❌ Could not list files: {ex}", success=False)


    def browse_drive(self, e: Any = None):
        """Open a Drive file picker and let the user download a file."""
        if not self._check_connection():
            return
        self._show_drive_files_dialog()

    def _show_drive_files_dialog(self):
        """Fetch Drive files (PDF/Docs/Slides/Sheets) and show a picker dialog."""
        try:
            payload = list_files(
                q_text=None,
                mime_in=[MIME["pdf"], MIME["gdoc"], MIME["gslide"], MIME["gsheet"]],
                page_size=50,
            )
            files = payload.get("files", [])
            if not files:
                self._show_message("📭 No Drive files found")
                return

            def on_pick(file_obj: Dict):
                try:
                    path = download_file(file_id=file_obj["id"], dest_path="./data/textbooks/")
                    self._show_message(f"✅ Downloaded: {file_obj['name']}\n→ {path}")
                except Exception as ex:
                    self._show_message(f"❌ Download failed: {ex}", success=False)
                finally:
                    self.page.dialog.open = False
                    self.page.update()

            items = [
                ft.ListTile(
                    leading=ft.Icon(ft.icons.INSERT_DRIVE_FILE_ROUNDED),
                    title=ft.Text(f["name"]),
                    subtitle=ft.Text(f'{f["mimeType"]} • {f.get("modifiedTime","")}'),
                    on_click=(lambda ev, file=f: on_pick(file)),
                )
                for f in files
            ]

            dlg = ft.AlertDialog(
                title=ft.Text("Select a Drive file to download"),
                content=ft.Column(items, scroll=ft.ScrollMode.AUTO, width=520, height=420),
            )
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()

        except Exception as ex:
            self._show_message(f"❌ Could not list files: {ex}", success=False)

    # ------------------ Utilities ------------------

    def _show_message(self, message: str, success: bool = True):
        color = "#66A36C" if success else "#6A2830"
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text(message), bgcolor=color))
        self.page.update()

    def _check_connection(self) -> bool:
        if not self.is_connected:
            self._show_message("⚠️ Please connect to Google Drive first", success=False)
            return False
        return True







# """
# Google Drive Handler
# Handles Google Drive integration for file storage and synchronization.

# TODO for team members:
# - Set up Google Drive API credentials and authentication
# - Implement OAuth2 flow for user authorization
# - Add file upload/download functionality
# - Implement folder synchronization
# - Add real-time collaboration features
# """

# import flet as ft
# from typing import Any, List, Dict


# class GoogleDriveHandler:
#     """Handles Google Drive integration operations"""
    
#     def __init__(self, page: ft.Page):
#         self.page = page
#         # TODO: Initialize Google Drive API client and credentials
#         self.is_connected = False
#         self.user_credentials = None
#         self.drive_service = None
#         self.sync_folder_id = None
    
#     def connect_drive(self, e: Any = None):
#         """
#         Handle Google Drive connection and authentication
        
#         TODO: Implement the following:
#         1. Set up OAuth2 authentication flow
#         2. Request user authorization
#         3. Store access tokens securely
#         4. Initialize Drive API service
#         5. Update connection status in UI
#         """
#         # Placeholder implementation
#         if not self.is_connected:
#             self._show_message("🔗 Connecting to Google Drive - Ready for implementation!")
            
#             # Example implementation structure:
#             # try:
#             #     credentials = self._authenticate_user()
#             #     if credentials:
#             #         self.drive_service = self._initialize_drive_service(credentials)
#             #         self.is_connected = True
#             #         self._update_connection_status(True)
#             #         self._show_message("✅ Connected to Google Drive")
#             #         self._load_user_folders()
#             #     else:
#             #         self._show_message("❌ Authentication failed", success=False)
#             # except Exception as e:
#             #     self._show_message(f"❌ Connection error: {str(e)}", success=False)
#         else:
#             self._show_message("✅ Already connected to Google Drive")
    
#     def disconnect_drive(self, e: Any = None):
#         """
#         Handle Google Drive disconnection
        
#         TODO: Implement the following:
#         1. Show confirmation dialog
#         2. Clear stored credentials
#         3. Reset connection status
#         4. Clear cached Drive data
#         5. Update UI accordingly
#         """
#         # Placeholder implementation
#         if self.is_connected:
#             self._show_message("🔌 Disconnecting from Google Drive - Ready for implementation!")
            
#             # Example implementation:
#             # if self._confirm_disconnect():
#             #     self._clear_credentials()
#             #     self.is_connected = False
#             #     self.drive_service = None
#             #     self._update_connection_status(False)
#             #     self._clear_drive_cache()
#             #     self._show_message("✅ Disconnected from Google Drive")
#         else:
#             self._show_message("⚠️ Not connected to Google Drive")
    
#     def upload_notes(self, e: Any = None):
#         """
#         Handle uploading notes to Google Drive
        
#         TODO: Implement the following:
#         1. Check connection status
#         2. Get current notes content
#         3. Create or update file on Drive
#         4. Handle upload progress
#         5. Sync with local changes
#         """
#         # Placeholder implementation
#         self._show_message("☁️ Upload Notes - Ready for implementation!")
        
#         # Example implementation:
#         # if self._check_connection():
#         #     notes_content = self._get_current_notes()
#         #     if notes_content:
#         #         file_id = self._upload_to_drive(notes_content, "StudyAI_Notes.txt")
#         #         if file_id:
#         #             self._update_sync_status(file_id)
#         #             self._show_message("✅ Notes uploaded to Drive")
#         #         else:
#         #             self._show_message("❌ Upload failed", success=False)
    
#     def download_notes(self, e: Any = None):
#         """
#         Handle downloading notes from Google Drive
        
#         TODO: Implement the following:
#         1. Check connection status
#         2. List available notes files
#         3. Download selected file
#         4. Merge with local notes
#         5. Handle conflicts
#         """
#         # Placeholder implementation
#         self._show_message("📥 Download Notes - Ready for implementation!")
        
#         # Example implementation:
#         # if self._check_connection():
#         #     notes_files = self._list_notes_files()
#         #     if notes_files:
#         #         selected_file = self._show_file_selection(notes_files)
#         #         if selected_file:
#         #             content = self._download_from_drive(selected_file['id'])
#         #             self._merge_with_local_notes(content)
#         #             self._show_message("✅ Notes downloaded from Drive")
    
#     def sync_files(self, e: Any = None):
#         """
#         Handle automatic file synchronization
        
#         TODO: Implement the following:
#         1. Check for local changes
#         2. Check for remote changes
#         3. Resolve conflicts if any
#         4. Upload/download as needed
#         5. Update sync timestamps
#         """
#         # Placeholder implementation
#         self._show_message("🔄 Sync Files - Ready for implementation!")
        
#         # Example implementation:
#         # if self._check_connection():
#         #     local_changes = self._check_local_changes()
#         #     remote_changes = self._check_remote_changes()
#         #     
#         #     if local_changes or remote_changes:
#         #         conflicts = self._detect_conflicts(local_changes, remote_changes)
#         #         if conflicts:
#         #             resolution = self._resolve_conflicts(conflicts)
#         #             self._apply_conflict_resolution(resolution)
#         #         
#         #         self._sync_changes(local_changes, remote_changes)
#         #         self._update_sync_timestamp()
#         #         self._show_message("✅ Files synchronized")
#         #     else:
#         #         self._show_message("✅ All files up to date")
    
#     def create_backup(self, e: Any = None):
#         """
#         Handle creating backup of all study materials
        
#         TODO: Implement the following:
#         1. Collect all notes, documents, recordings
#         2. Create timestamped backup folder
#         3. Upload all files to Drive
#         4. Generate backup manifest
#         5. Show backup completion status
#         """
#         # Placeholder implementation
#         self._show_message("💾 Create Backup - Ready for implementation!")
        
#         # Example implementation:
#         # if self._check_connection():
#         #     backup_data = self._collect_all_study_materials()
#         #     backup_folder = self._create_backup_folder()
#         #     
#         #     for file_data in backup_data:
#         #         self._upload_to_backup_folder(file_data, backup_folder)
#         #     
#         #     manifest = self._create_backup_manifest(backup_data)
#         #     self._upload_manifest(manifest, backup_folder)
#         #     self._show_message("✅ Backup created successfully")
    
#     def browse_drive(self, e: Any = None):
#         """
#         Handle browsing Google Drive files
        
#         TODO: Implement the following:
#         1. List Drive folders and files
#         2. Show file browser interface
#         3. Allow file selection and preview
#         4. Enable file operations (copy, move, delete)
#         5. Support folder navigation
#         """
#         # Placeholder implementation
#         self._show_message("📁 Browse Drive - Ready for implementation!")
        
#         # Example implementation:
#         # if self._check_connection():
#         #     files = self._list_drive_files()
#         #     self._show_file_browser(files)
    
#     def _show_message(self, message: str, success: bool = True):
#         """Helper method to show messages"""
#         color = ft.colors.GREEN if success else ft.colors.RED
#         self.page.show_snack_bar(
#             ft.SnackBar(content=ft.Text(message), bgcolor=color)
#         )
    
#     def _check_connection(self) -> bool:
#         """Check if connected to Google Drive"""
#         if not self.is_connected:
#             self._show_message("⚠️ Please connect to Google Drive first", success=False)
#             return False
#         return True
    
#     # TODO: Helper methods for team members to implement
#     # def _authenticate_user(self):
#     #     """Handle OAuth2 authentication flow"""
#     #     # Use google-auth-oauthlib for OAuth2 flow
#     #     # Redirect to Google authorization URL
#     #     # Handle callback with authorization code
#     #     # Exchange code for access token
#     #     pass
#     # 
#     # def _initialize_drive_service(self, credentials):
#     #     """Initialize Google Drive API service"""
#     #     # from googleapiclient.discovery import build
#     #     # service = build('drive', 'v3', credentials=credentials)
#     #     # return service
#     #     pass
#     # 
#     # def _upload_to_drive(self, content: str, filename: str) -> str:
#     #     """Upload file content to Google Drive"""
#     #     pass
#     # 
#     # def _download_from_drive(self, file_id: str) -> str:
#     #     """Download file content from Google Drive"""
#     #     pass
#     # 
#     # def _list_drive_files(self) -> List[Dict]:
#     #     """List files in Google Drive"""
#     #     pass