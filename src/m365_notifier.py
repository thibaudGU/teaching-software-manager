import json
from typing import Dict, Optional

try:
    import requests  # type: ignore
except Exception:
    requests = None  # graceful fallback if not installed

try:
    import msal  # type: ignore
except Exception:
    msal = None  # graceful fallback if not installed

from config_loader import ConfigLoader


class M365Notifier:
    """
    Microsoft 365 Graph notifier for posting reminders to Microsoft Teams.
    Supports:
    - Posting messages to a specific Team channel
    - (Optionally) sending 1:1 chats to users if allowed by DSI/perms
    """

    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.m365_config = config_loader.get_m365_config()
        self.email_config = config_loader.get_email_config()

        self.enabled = bool(self.m365_config.get("enabled", False))
        self.tenant_id = self.m365_config.get("tenant_id")
        self.client_id = self.m365_config.get("client_id")
        self.client_secret = self.m365_config.get("client_secret")
        self.team_id = self.m365_config.get("team_id")
        self.channel_id = self.m365_config.get("channel_id")
        self.allow_user_chats = bool(self.m365_config.get("allow_user_chats", False))

        # Web app base URL for deep-links in messages
        self.app_base_url = self.email_config.get("app_base_url", "http://localhost:5000")
        self._libs_ok = requests is not None and msal is not None

    def _get_token(self) -> Optional[str]:
        if not self.enabled:
            return None
        if not self._libs_ok:
            raise RuntimeError("MSAL/requests not installed. Run: pip install msal requests")
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            return None

        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=authority,
        )
        scopes = ["https://graph.microsoft.com/.default"]
        result = app.acquire_token_silent(scopes=scopes, account=None)
        if not result:
            result = app.acquire_token_for_client(scopes=scopes)
        if "access_token" in result:
            return result["access_token"]
        raise RuntimeError(f"Failed to acquire Graph token: {result}")

    def _graph_post(self, url: str, token: str, payload: Dict) -> Dict:
        if not self._libs_ok:
            raise RuntimeError("requests not installed. Run: pip install requests")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
        if not resp.ok:
            raise RuntimeError(f"Graph POST {url} failed: {resp.status_code} {resp.text}")
        return resp.json() if resp.text else {}

    def _format_message_html(self, instructor_id: str, subject: str, body_html: str) -> str:
        review_url = f"{self.app_base_url}/instructor/{instructor_id}"
        button = (
            f'<p><a href="{review_url}" '
            f'style="display:inline-block;padding:10px 14px;background:#6264A7;color:#fff;'
            f'text-decoration:none;border-radius:4px;">Ouvrir l\'interface</a></p>'
        )
        return f"<h3>{subject}</h3>{body_html}{button}"

    def send_to_channel(self, instructor_id: str, to_display: str, subject: str, body_html: str,
                        dry_run: bool = True) -> Dict:
        """
        Post a message to a specific Teams channel with deep-link to the instructor page.
        Returns a preview dict in dry_run, or Graph response on success.
        """
        content = self._format_message_html(instructor_id, subject, body_html)
        preview = {
            "target": "teams_channel",
            "team_id": self.team_id,
            "channel_id": self.channel_id,
            "to": to_display,
            "subject": subject,
            "content_html": content,
        }

        if dry_run or not self.enabled:
            return {"success": True, "preview": preview}

        if not (self.team_id and self.channel_id):
            raise RuntimeError("M365 config missing team_id/channel_id")

        token = self._get_token()
        url = (
            f"https://graph.microsoft.com/v1.0/teams/{self.team_id}/"
            f"channels/{self.channel_id}/messages"
        )
        payload = {
            "subject": subject,
            "body": {
                "contentType": "html",
                "content": content,
            },
        }
        res = self._graph_post(url, token, payload)
        return {"success": True, "graph_response": res}
