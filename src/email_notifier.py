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
        self.last_error: str | None = None

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
                <h2>Vérification des logiciels d'enseignement</h2>
                <p><strong>Bonjour {instructor['name']}</strong></p>
                <p>Merci de vérifier ci-dessous la liste des logiciels requis pour vos modules.</p>
                <p>Dernière vérification: {instructor.get('last_review', 'N/A')}</p>
            </div>
        """
        
        for module in modules:
            html += f"""
            <div class="module">
                <h3>{module['name']} (Année {module.get('year', '?')}, Semestre {module.get('semester', '?')})</h3>
                <p>{module.get('description', '')}</p>
                
                <h4>Systèmes d'exploitation requis :</h4>
                <ul>
            """
            
            for os in module.get('os_required', []):
                note = f" - {os.get('note', '')}" if 'note' in os else ""
                html += f"<li>{os['name']}{note}</li>"
            
            html += """
                </ul>
                
                <h4>Logiciels requis :</h4>
            """
            
            for software in module.get('software', []):
                critical_class = 'critical' if software.get('critical', False) else ''
                html += f"""
                <div class="software {critical_class}">
                    <strong>{software['name']}</strong>
                    <div class="version">Version : {software.get('version', 'N/A')}</div>
                    <div>{software.get('purpose', '')}</div>
                    {f'<div class="notes">Notes : {software.get("notes", "")}</div>' if software.get('notes') else ''}
                    <div class="version">Dernière vérification : {software.get('last_verified', 'N/A')}</div>
                    {f'<div class="version">Vérifié par : {software.get("verified_by", "N/A")}</div>' if software.get('verified_by') else ''}
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
                <p><strong>📋 Mise à jour de vos besoins logiciels :</strong></p>
                
                <h3 style="color: #0066cc;">Mise à jour en ligne (Recommandé)</h3>
                <p style="background: #e8f4f8; padding: 15px; border-radius: 5px; border-left: 4px solid #0066cc;">
                    <a href="{review_url}" style="color: #0066cc; text-decoration: none; font-weight: bold; font-size: 1.1em;">
                        🔗 Cliquez ici pour accéder à votre interface de gestion
                    </a><br>
                    <small>Ajoutez, modifiez ou supprimez vos logiciels directement dans l'application web.</small>
                </p>
                
                <p style="margin-top: 20px; font-size: 0.9em;">
                    <em>Dernière révision: {instructor.get('last_review', 'Jamais')}</em>
                </p>
            </div>
        </body>
        </html>
        """
        
        return html

    def send_email(self, to_email: str, subject: str, html_body: str, 
                  text_body: str = None, smtp_username: str = None, smtp_password: str = None, from_email: str = None) -> bool:
        """
        Send an email via SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML content
            text_body: Plain text fallback (optional)
            smtp_username: SMTP username (if None, uses env var)
            smtp_password: SMTP password (if None, uses env var)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.email_config.get('enabled', False):
            print("Email notifications are disabled in configuration")
            return False
        
        try:
            self.last_error = None
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            # Choose From header: explicit override > smtp username > configured sender
            header_from = from_email or smtp_username or self.email_config.get('sender_email', '')
            msg['From'] = header_from
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
            
            # Use provided credentials or fall back to env vars
            username = smtp_username if smtp_username is not None else self.smtp_username
            password = smtp_password if smtp_password is not None else self.smtp_password
            
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                if use_tls:
                    server.starttls()
                
                if username and password:
                    server.login(username, password)
                
                server.send_message(msg)
            
            print(f"Email sent to {to_email}")
            return True
        
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            self.last_error = str(e)
            return False

    def send_reminder(self, instructor_id: str, subject: str, dry_run: bool = True, 
                     smtp_username: str = None, smtp_password: str = None) -> Dict[str, Any]:
        """
        Send a review reminder to a specific instructor.
        
        Args:
            instructor_id: Instructor ID
            subject: Email subject
            dry_run: If True, return preview without sending
            smtp_username: SMTP username (required if not dry_run)
            smtp_password: SMTP password (required if not dry_run)
            
        Returns:
            Dictionary with success status and preview/message
        """
        try:
            instructor = self.config_loader.get_instructor(instructor_id)
            email = instructor.get('email', '')
            
            if not email:
                return {'success': False, 'error': 'No email address for instructor'}
            
            html_report = self.generate_instructor_report_html(instructor_id)
            
            if dry_run:
                return {
                    'success': True,
                    'preview': {
                        'from': smtp_username or self.email_config.get('sender_email', ''),
                        'to': email,
                        'subject': subject,
                        'html': html_report
                    }
                }
            else:
                if not smtp_username or not smtp_password:
                    return {'success': False, 'error': 'SMTP credentials required'}
                
                success = self.send_email(
                    to_email=email, 
                    subject=subject, 
                    html_body=html_report,
                    smtp_username=smtp_username,
                    smtp_password=smtp_password,
                    from_email=smtp_username
                )
                
                if success:
                    return {'success': True, 'message': f'Email sent to {email}'}
                else:
                    return {'success': False, 'error': self.last_error or 'Failed to send email'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
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
            subject = f"Vérification des logiciels d'enseignement - {name}"
            
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
        
        report = "# Inventaire des logiciels d'enseignement\n\n"
        report += f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Instructors summary
        report += "## Enseignants\n\n"
        for inst_id, inst_data in instructors.items():
            modules_list = ', '.join(inst_data.get('modules', []))
            report += f"- **{inst_data.get('name', inst_id)}**\n"
            report += f"  - Email : {inst_data.get('email', 'N/A')}\n"
            report += f"  - Modules : {modules_list}\n"
            report += f"  - Dernière vérification : {inst_data.get('last_review', 'N/A')}\n\n"
        
        # Modules summary with software list
        report += "## Modules\n\n"
        for mod_id, mod_data in modules.items():
            software = mod_data.get('software', [])
            software_count = len(software)
            critical_count = len([s for s in software if s.get('critical', False)])
            
            report += f"### {mod_data.get('name', mod_id)} (ID: {mod_id})\n"
            report += f"- Année : {mod_data.get('year', '?')}\n"
            report += f"- Semestre : {mod_data.get('semester', '?')}\n"
            report += f"- Logiciels : {software_count} élément(s) ({critical_count} critique(s))\n"
            if software:
                report += "  - Détail des logiciels :\n"
                for soft in software:
                    crit = " (critique)" if soft.get('critical', False) else ""
                    report += f"    * {soft.get('name','?')} - version {soft.get('version','N/A')}{crit} : {soft.get('purpose','')}\n"
            report += "\n"
        
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
