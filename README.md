# Teaching Software Manager

A comprehensive system for managing, tracking, and verifying software requirements for university teaching modules.

## Features

✅ **Centralized Configuration** - YAML-based configuration for all instructors, modules, and software  
✅ **Web Interface** - User-friendly Flask web application for viewing and managing data  
✅ **Excel Sync** - Export/import data to/from Excel files on OneDrive for collaboration  
✅ **Email Notifications** - Automatic reminder emails to instructors (if SMTP available)  
✅ **Report Generation** - Generate HTML reports for documentation  
✅ **Version Tracking** - Track software versions and last verified dates  
✅ **Cloud Deployment** - Deploy to Render.com (free, always available)  
✅ **CLI Tool** - Command-line interface for automation and scripting  

## Project Structure

```
teaching-software-manager/
├── config/
│   └── teaching_software.yml          # Main configuration file
├── src/
│   ├── config_loader.py               # Configuration management
│   └── email_notifier.py              # Email and report generation
├── web/
│   └── app.py                         # Flask web application
├── templates/                         # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── instructors.html
│   ├── instructor_detail.html
│   ├── modules.html
│   ├── module_detail.html
│   ├── reports.html
│   ├── settings.html
│   ├── 404.html
│   └── 500.html
├── static/
│   └── style.css                      # CSS stylesheet
├── cli.py                             # Command-line interface
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## Installation

### 1. Clone or Download the Project

```bash
cd teaching-software-manager
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Email (Optional)

To enable automatic email notifications, set environment variables:

**Windows PowerShell:**
```powershell
$env:EMAIL_USERNAME = "your-email@univ-lr.fr"
$env:EMAIL_PASSWORD = "your-password"
```

**Linux/macOS:**
```bash
export EMAIL_USERNAME="your-email@univ-lr.fr"
export EMAIL_PASSWORD="your-password"
```

Or create a `.env` file:
```
EMAIL_USERNAME=your-email@univ-lr.fr
EMAIL_PASSWORD=your-password
```

## Usage

### Web Application

Start the Flask web server:

```bash
python web/app.py
```

Then open http://localhost:5000 in your browser.

**Features:**
- View all instructors and their assigned modules
- Browse software requirements per module
- Generate and review instructor reports
- **Export/Import Excel files** for collaboration on OneDrive
- Send test emails or real review reminders
- Check sync status between YAML and Excel
- Configure system settings

### Excel Synchronization

Export your data to Excel, share it on OneDrive, and import updates back:

1. **Export** : Reports → "📊 Synchronisation Excel" → "Exporter vers Excel"
2. **Share** : Copy `teaching_software.xlsx` to your OneDrive shared folder
3. **Edit** : Anyone with access can edit the Excel file
4. **Import** : Back in the app → "Importer depuis Excel"

See [EXCEL_SYNC_GUIDE.md](EXCEL_SYNC_GUIDE.md) for detailed instructions.

### Cloud Deployment (Render)

Deploy to Render for 24/7 availability (free tier):

1. Push code to GitHub
2. Connect GitHub repo to Render.com
3. Set environment variables
4. Auto-deploy on every push

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for step-by-step guide.

### Command-Line Interface

Validate configuration:
```bash
python cli.py validate
```

List instructors:
```bash
python cli.py list instructors
```

List modules:
```bash
python cli.py list modules
```

Generate summary report:
```bash
python cli.py report summary
```

Generate instructor report:
```bash
python cli.py report instructor prof_001 --output report.html
```

Send test emails to all instructors:
```bash
python cli.py send --dry-run
```

Send real emails:
```bash
python cli.py send --real
```

Send email to specific instructor:
```bash
python cli.py send --instructor prof_001
```

### Configuration File

Edit `config/teaching_software.yml` to:

1. **Add/remove instructors:**
```yaml
instructors:
  prof_001:
    name: "Dr. Jean Dupont"
    email: "jean.dupont@univ-lr.fr"
    department: "Informatique"
    modules:
      - "web_development"
      - "databases"
```

2. **Add/modify modules:**
```yaml
modules:
  web_development:
    name: "Web Development Fundamentals"
    description: "HTML, CSS, JavaScript, and backend frameworks"
    semester: "Fall"
    year: 2
    os_required:
      - name: "Windows 10/11"
      - name: "macOS 12+"
    software:
      - name: "Visual Studio Code"
        purpose: "Code editor"
        version: "Latest"
        critical: true
        last_verified: "2025-01-01"
        verified_by: "prof_001"
```

## Email Configuration

### SMTP Server Settings

The system reads email configuration from `config/teaching_software.yml`:

```yaml
email_config:
  enabled: true
  reminder_frequency_months: 3
  smtp_server: "smtp.univ-lr.fr"
  smtp_port: 587
  use_tls: true
  sender_email: "teaching-software-manager@univ-lr.fr"
  sender_name: "Teaching Software Manager"
```

### Authentication

SMTP credentials must be provided as environment variables:
- `EMAIL_USERNAME` - SMTP username (usually your email)
- `EMAIL_PASSWORD` - SMTP password

These are **not stored in the configuration file for security reasons**.

## API Endpoints

The Flask web application provides REST API endpoints:

- `GET /` - Home page
- `GET /instructors` - List all instructors
- `GET /instructor/<id>` - View instructor details
- `GET /modules` - List all modules
- `GET /module/<id>` - View module details
- `GET /reports` - Reports page
- `GET /api/instructor/<id>/report` - Get instructor report HTML
- `POST /api/send-reminder/<id>` - Send email reminder
- `GET /api/summary-report` - Get summary report
- `GET /settings` - Settings page
- `GET /health` - Health check

## Workflow

### Regular Review Cycle (Every 3 months)

1. **System sends reminders** to instructors
2. **Instructors review** their module software lists
3. **Instructors notify administrator** of changes
4. **Administrator updates** `teaching_software.yml`
5. **System validates** the updated configuration

### Adding New Software

1. Open `config/teaching_software.yml`
2. Add software entry to the module:
```yaml
- name: "Software Name"
  purpose: "What is it used for?"
  category: "Category"
  version: "Version number"
  critical: true/false
  notes: "Optional notes"
  last_verified: "2025-01-01"
  verified_by: "instructor_id"
```
3. Run `python cli.py validate` to check
4. Restart web application for changes to take effect

### Removing Deprecated Software

1. Locate the software in `config/teaching_software.yml`
2. Delete its entry or comment it out
3. Run `python cli.py validate`
4. Update instructors about the change

## Troubleshooting

### Email Not Sending

1. Check environment variables are set:
   ```bash
   echo $env:EMAIL_USERNAME  # PowerShell
   echo $EMAIL_USERNAME      # Linux/macOS
   ```

2. Verify SMTP settings in `config/teaching_software.yml`

3. Test with dry-run first:
   ```bash
   python cli.py send --dry-run
   ```

### Configuration Validation Errors

```bash
python cli.py validate
```

This will show all configuration issues.

### Port 5000 Already in Use

Change the port in `web/app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # Change 5000 to 8000
```

## Best Practices

1. **Regular Reviews** - Review software every 3 months
2. **Version Management** - Keep versions current and document changes
3. **Clear Documentation** - Use the "notes" field to explain complex software
4. **Critical Marking** - Mark software as critical only if essential for the module
5. **Backup Configuration** - Version control your `teaching_software.yml` file

## Future Enhancements

- [ ] Add database backend (PostgreSQL)
- [ ] User authentication and role-based access
- [ ] PDF report generation
- [ ] Software dependency tracking
- [ ] License management
- [ ] Installation guide generation
- [ ] Lab environment provisioning

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the configuration file syntax
3. Validate the configuration: `python cli.py validate`

## License

This project is provided as-is for educational use at Université de La Rochelle.

---

**Created:** 2025-01-01  
**Last Updated:** 2025-01-01  
**Version:** 1.0.0
