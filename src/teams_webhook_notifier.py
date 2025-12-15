"""
Teams Webhook notifier for sending reminders to Microsoft Teams.
Uses Incoming Webhook (no authentication needed, you control the URL).
"""

import json
from typing import Dict, Optional
import requests

from config_loader import ConfigLoader


class TeamsWebhookNotifier:
    """
    Send messages to Microsoft Teams via Incoming Webhook.
    Simple one-way notification system (no Graph API needed).
    """

    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.teams_config = config_loader.get_teams_config()
        self.email_config = config_loader.get_email_config()
        
        self.webhook_url = self.teams_config.get("webhook_url")
        self.enabled = bool(self.webhook_url)
        self.app_base_url = self.email_config.get("app_base_url", "http://localhost:5000")

    def _build_card(self, instructor_id: str, instructor_name: str, subject: str, 
                    module_count: int) -> Dict:
        """Build an Adaptive Card for Teams."""
        review_url = f"{self.app_base_url}/instructor/{instructor_id}"
        
        card = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": subject,
            "themeColor": "0078D4",
            "sections": [
                {
                    "activityTitle": "🔍 Revue des Logiciels d'Enseignement",
                    "activitySubtitle": f"Demandé à : {instructor_name}",
                    "text": f"Veuillez vérifier et mettre à jour vos besoins logiciels pour **{module_count} module(s)**.",
                    "markdown": True
                }
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "📋 Mettre à jour maintenant",
                    "targets": [
                        {
                            "os": "default",
                            "uri": review_url
                        }
                    ]
                }
            ]
        }
        return card

    def send_reminder(self, instructor_id: str, instructor_name: str, subject: str, 
                     module_count: int, dry_run: bool = True) -> Dict:
        """
        Send a Teams reminder message.
        
        Args:
            instructor_id: ID of the instructor
            instructor_name: Display name
            subject: Message subject
            module_count: Number of modules assigned
            dry_run: If True, return preview without sending
            
        Returns:
            Dict with success status and preview/response
        """
        card = self._build_card(instructor_id, instructor_name, subject, module_count)
        
        preview = {
            "target": "teams_webhook",
            "to": instructor_name,
            "subject": subject,
            "card": card
        }
        
        if dry_run or not self.enabled:
            return {"success": True, "preview": preview}
        
        if not self.webhook_url:
            return {"success": False, "error": "Teams webhook URL not configured"}
        
        try:
            response = requests.post(
                self.webhook_url,
                json=card,
                timeout=10
            )
            if response.ok:
                return {"success": True, "message": "Message envoyé à Teams"}
            else:
                return {"success": False, "error": f"Teams API error: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to send Teams message: {str(e)}"}

    def send_bulk_reminders(self, reminders: list, dry_run: bool = True) -> Dict:
        """
        Send multiple reminders in bulk.
        
        Args:
            reminders: List of dicts with {instructor_id, instructor_name, subject, module_count}
            dry_run: If True, return previews without sending
            
        Returns:
            Dict with results and previews
        """
        results = []
        previews = []
        
        for reminder in reminders:
            result = self.send_reminder(
                reminder['instructor_id'],
                reminder['instructor_name'],
                reminder['subject'],
                reminder['module_count'],
                dry_run=dry_run
            )
            results.append(result)
            if dry_run and result.get('preview'):
                previews.append(result['preview'])
        
        return {
            "success": all(r.get('success') for r in results),
            "count": len(reminders),
            "results": results,
            "previews": previews
        }
