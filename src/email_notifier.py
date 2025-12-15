"""
Email notification system for teaching software reviews.
Generates and sends email reminders to instructors.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

from config_loader import ConfigLoader


class EmailNotifier:
    """Handle email notifications for software reviews."""

    def __init__(self, config_loader: ConfigLoader):
        """
        Initialize the email notifier.
        
        Args:
            config_loader: Instance of ConfigLoader
        """
        self.config_loader = config_loader
        self.email_config = config_loader.get_email_config()
        
        # Read SMTP credentials from environment variables
        self.smtp_username = os.getenv('EMAIL_USERNAME', '')
        self.smtp_password = os.getenv('EMAIL_PASSWORD', '')

    def generate_instructor_report_html(self, instructor_id: str) -> str:
        """
        Generate an HTML report for an instructor.
        
        Args:
            instructor_id: The instructor's ID
            
        Returns:
            HTML string with the instructor's software review
        """
        instructor = self.config_loader.get_instructor(instructor_id)
        modules = self.config_loader.get_instructor_module_details(instructor_id)
        
        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-bottom: 3px solid #0066cc; }}
                .module {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .module h3 {{ color: #0066cc; margin-top: 0; }}
                .software {{ margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-left: 3px solid #666; }}
                .critical {{ border-left-color: #cc0000; font-weight: bold; }}
                .version {{ color: #666; font-size: 0.9em; }}
                .notes {{ color: #666; font-size: 0.85em; font-style: italic; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; color: #666; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th {{ background-color: #f4f4f4; padding: 10px; text-align: left; border-bottom: 2px solid #ddd; }}
                td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Teaching Software Review Request</h2>
                <p><strong>Dear {instructor['name']}</strong></p>
                <p>Please review the software requirements for your teaching modules below.</p>
                <p>Last review: {instructor.get('last_review', 'N/A')}</p>
            </div>
        """
        
        for module in modules:
            html += f"""
            <div class="module">
                <h3>{module['name']} (Year {module.get('year', '?')}, {module.get('semester', '?')})</h3>
                <p>{module.get('description', '')}</p>
                
                <h4>Operating Systems Required:</h4>
                <ul>
            """
            
            for os in module.get('os_required', []):
                note = f" - {os.get('note', '')}" if 'note' in os else ""
                html += f"<li>{os['name']}{note}</li>"
            
            html += """
                </ul>
                
                <h4>Required Software:</h4>
            """
            
            for software in module.get('software', []):
                critical_class = 'critical' if software.get('critical', False) else ''
                html += f"""
                <div class="software {critical_class}">
                    <strong>{software['name']}</strong>
                    <div class="version">Version: {software.get('version', 'N/A')}</div>
                    <div>{software.get('purpose', '')}</div>
                    {f'<div class="notes">Notes: {software.get("notes", "")}</div>' if software.get('notes') else ''}
                    <div class="version">Last verified: {software.get('last_verified', 'N/A')}</div>
                    {f'<div class="version">Verified by: {software.get("verified_by", "N/A")}</div>' if software.get('verified_by') else ''}
                </div>
                """
            
            html += """
            </div>
            """
        
        # Générer le lien de révision
        base_url = self.email_config.get('app_base_url', 'http://localhost:5000')
        review_url = f"{base_url}/instructor/{instructor_id}"
        
        html += f"""
            <div class="footer">
                <p><strong>📋 Action Required - Comment mettre à jour vos besoins logiciels :</strong></p>
                
                <h3 style="color: #0066cc;">Option 1 : Mise à jour en ligne (Recommandé)</h3>
                <p style="background: #e8f4f8; padding: 15px; border-radius: 5px; border-left: 4px solid #0066cc;">
                    <a href="{review_url}" style="color: #0066cc; text-decoration: none; font-weight: bold; font-size: 1.1em;">
                        🔗 Cliquez ici pour accéder à votre interface de gestion
                    </a><br>
                    <small>Vous pourrez ajouter, modifier ou supprimer des logiciels directement dans l'application web.</small>
                </p>
                
                <h3 style="color: #006600;">Option 2 : Réponse par email</h3>
                <p>Répondez à cet email avec le format suivant :</p>
                <pre style="background: #f4f4f4; padding: 10px; border-radius: 5px; font-size: 0.9em;">
[MODULE: nom_du_module]

AJOUTER:
- Nom du logiciel | Version | Critique (oui/non) | Usage

MODIFIER:
- Nom du logiciel | Nouvelle version | Notes

SUPPRIMER:
- Nom du logiciel | Raison

COMMENTAIRES:
Vos remarques générales ici
                </pre>
                
                <p><strong>Exemple de réponse :</strong></p>
                <pre style="background: #fffff0; padding: 10px; border-radius: 5px; font-size: 0.85em;">
[MODULE: Développement Web]

AJOUTER:
- Node.js | v20.x | oui | Pour le développement JavaScript côté serveur

MODIFIER:
- VS Code | 1.95 | Nouvelle version stable disponible

SUPPRIMER:
- Brackets | Logiciel abandonné, remplacé par VS Code

COMMENTAIRES:
Les étudiants auront besoin de Docker pour les TPs du S2.
                </pre>
                
                <p style="margin-top: 20px; font-size: 0.9em;">
                    <strong>Questions ?</strong> Contact: teaching-software-manager@univ-lr.fr<br>
                    <em>Dernière révision: {instructor.get('last_review', 'Jamais')}</em>
                </p>
            </div>
        </body>
        </html>
        """
        
        return html

    def send_email(self, to_email: str, subject: str, html_body: str, 
                  text_body: str = None) -> bool:
        """
        Send an email via SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML content
            text_body: Plain text fallback (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.email_config.get('enabled', False):
            print("Email notifications are disabled in configuration")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_config.get('sender_email', '')
            msg['To'] = to_email
            
            # Attach plain text and HTML
            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send via SMTP
            smtp_server = self.email_config.get('smtp_server', '')
            smtp_port = self.email_config.get('smtp_port', 587)
            use_tls = self.email_config.get('use_tls', True)
            
            print(f"Connecting to SMTP server: {smtp_server}:{smtp_port}")
            
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                if use_tls:
                    server.starttls()
                
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
            
            print(f"Email sent to {to_email}")
            return True
        
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False

    def send_review_reminders(self, dry_run: bool = True) -> Dict[str, bool]:
        """
        Send review reminder emails to all instructors.
        
        Args:
            dry_run: If True, only print what would be sent (no actual emails)
            
        Returns:
            Dictionary mapping instructor ID to success status
        """
        instructors = self.config_loader.get_instructors()
        results = {}
        
        print(f"\n{'DRY RUN' if dry_run else 'SENDING'} review reminders to {len(instructors)} instructors...\n")
        
        for inst_id, inst_data in instructors.items():
            email = inst_data.get('email', '')
            name = inst_data.get('name', inst_id)
            
            if not email:
                print(f"⚠ Skipping {name}: no email address")
                results[inst_id] = False
                continue
            
            # Generate report
            html_report = self.generate_instructor_report_html(inst_id)
            subject = f"Teaching Software Review Required - {name}"
            
            if dry_run:
                print(f"[DRY RUN] Would send to {email}")
                print(f"  Subject: {subject}")
                print(f"  Preview: {html_report[:100]}...\n")
                results[inst_id] = True
            else:
                success = self.send_email(to_email=email, subject=subject, html_body=html_report)
                results[inst_id] = success
        
        return results

    def generate_summary_report(self) -> str:
        """
        Generate a summary report of all software and modules.
        
        Returns:
            Markdown formatted summary report
        """
        instructors = self.config_loader.get_instructors()
        modules = self.config_loader.get_modules()
        
        report = "# Teaching Software Inventory\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Instructors summary
        report += "## Instructors\n\n"
        for inst_id, inst_data in instructors.items():
            modules_list = ', '.join(inst_data.get('modules', []))
            report += f"- **{inst_data['name']}** ({inst_data['department']})\n"
            report += f"  - Email: {inst_data['email']}\n"
            report += f"  - Modules: {modules_list}\n"
            report += f"  - Last review: {inst_data.get('last_review', 'N/A')}\n\n"
        
        # Modules summary
        report += "## Modules\n\n"
        for mod_id, mod_data in modules.items():
            software_count = len(mod_data.get('software', []))
            critical_count = len([s for s in mod_data.get('software', []) if s.get('critical', False)])
            
            report += f"### {mod_data['name']} (ID: {mod_id})\n"
            report += f"- Year: {mod_data.get('year', '?')}\n"
            report += f"- Semester: {mod_data.get('semester', '?')}\n"
            report += f"- Software: {software_count} items ({critical_count} critical)\n\n"
        
        return report


if __name__ == "__main__":
    # Test the email notifier
    try:
        loader = ConfigLoader()
        notifier = EmailNotifier(loader)
        
        # Generate and display a sample report
        print("Sample instructor report:\n")
        instructors = loader.get_instructors()
        if instructors:
            first_inst_id = list(instructors.keys())[0]
            report = notifier.generate_instructor_report_html(first_inst_id)
            print(report[:500] + "...\n")
        
        # Generate summary
        print("\nSummary report:\n")
        summary = notifier.generate_summary_report()
        print(summary)
        
        # Test email sending (dry run)
        print("\nDry run - sending reminders (no actual emails will be sent):\n")
        notifier.send_review_reminders(dry_run=True)
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
