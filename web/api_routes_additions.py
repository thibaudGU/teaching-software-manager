# Nouveaux endpoints API à ajouter dans app.py avant @app.route('/api/summary-report')

@app.route('/api/instructor-report-html/<instructor_id>')
def get_instructor_report_html(instructor_id):
    """Get HTML report for an instructor (API)."""
    try:
        instructor = config_loader.get_instructor(instructor_id)
        html_report = email_notifier.generate_instructor_report_html(instructor_id)
        return jsonify({
            'success': True,
            'html': html_report,
            'instructor_name': instructor['name'],
            'email': instructor['email']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/export-reminders-csv', methods=['POST'])
def export_reminders_csv():
    """Export reminders as CSV for manual sending."""
    try:
        data = request.json
        instructor_ids = data.get('instructor_ids', [])
        
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Nom', 'Email', 'Objet', 'Message_HTML', 'Lien_Rapport'])
        
        for inst_id in instructor_ids:
            instructor = config_loader.get_instructor(inst_id)
            html_report = email_notifier.generate_instructor_report_html(inst_id)
            subject = f"Rappel: Révision Logiciels - {instructor['name']}"
            report_link = f"http://localhost:5000/instructor/{inst_id}"
            
            writer.writerow([
                instructor['name'],
                instructor['email'],
                subject,
                html_report.replace('\n', ' ').replace('\r', ''),
                report_link
            ])
        
        output.seek(0)
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv; charset=utf-8',
            'Content-Disposition': 'attachment; filename=rappels_enseignants.csv'
        }
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/get-instructor-emails', methods=['POST'])
def get_instructor_emails():
    """Get list of instructor emails."""
    try:
        data = request.json
        instructor_ids = data.get('instructor_ids', [])
        
        emails = []
        for inst_id in instructor_ids:
            instructor = config_loader.get_instructor(inst_id)
            emails.append(instructor['email'])
        
        return jsonify({
            'success': True,
            'emails': emails
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
