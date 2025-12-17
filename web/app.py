"""
Flask web application for Teaching Software Manager.
Provides a user-friendly interface for managing software and modules.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file, session
from config_loader import ConfigLoader
from email_notifier import EmailNotifier
from excel_sync import ExcelSyncManager
from config_writer import ConfigWriter
import yaml
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.getenv('SECRET_KEY', 'teaching-software-manager-secret')

# Admin password from environment
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

def require_auth(f):
    """Decorator to protect routes - require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Load configuration
config_loader = ConfigLoader()
email_notifier = EmailNotifier(config_loader)

excel_sync = ExcelSyncManager(config_loader)
config_writer = ConfigWriter()

def reload_config():
    """Reload configuration after changes."""
    global config_loader, email_notifier, excel_sync
    config_loader = ConfigLoader()
    email_notifier = EmailNotifier(config_loader)
    excel_sync = ExcelSyncManager(config_loader)

@app.template_filter('instructor_name')
def instructor_name_filter(instructor_id):
    """Convert instructor ID to name."""
    try:
        instructor = config_loader.get_instructor(instructor_id)
        return instructor.get('name', instructor_id)
    except:
        return instructor_id


@app.route('/')
def index():
    """Home page with overview."""
    instructors = config_loader.get_instructors()
    modules = config_loader.get_modules()
    
    return render_template('index.html', 
                         instructors_count=len(instructors),
                         modules_count=len(modules),
                         instructors=instructors,
                         modules=modules)


@app.route('/instructors')
def view_instructors():
    """List all instructors."""
    instructors = config_loader.get_instructors()
    modules = config_loader.get_modules()
    return render_template('instructors.html', instructors=instructors, all_modules=modules)


@app.route('/instructor/<instructor_id>')
def view_instructor(instructor_id):
    """View details for a specific instructor."""
    try:
        instructor = config_loader.get_instructor(instructor_id)
        modules = config_loader.get_instructor_module_details(instructor_id)
        return render_template('instructor_detail.html', 
                             instructor_id=instructor_id,
                             instructor=instructor,
                             modules=modules)
    except ValueError as e:
        flash(f"Error: {e}", 'error')
        return redirect(url_for('view_instructors'))


@app.route('/modules')
def view_modules():
    """List all modules."""
    modules = config_loader.get_modules()
    instructors = config_loader.get_instructors()
    return render_template('modules.html', modules=modules, all_instructors=instructors)


@app.route('/module/<module_id>')
def view_module(module_id):
    """View details for a specific module."""
    try:
        module = config_loader.get_module(module_id)
        module['id'] = module_id
        software = module.get('software', [])
        return render_template('module_detail.html', 
                             module_id=module_id,
                             module=module,
                             software=software)
    except ValueError as e:
        flash(f"Error: {e}", 'error')
        return redirect(url_for('view_modules'))


@app.route('/reports')
def view_reports():
    """View reports page."""
    instructors = config_loader.get_instructors()
    return render_template('reports.html', instructors=instructors)


@app.route('/verification')
def view_verification():
    """Verification page for managing software and OS per instructor-module."""
    instructors = config_loader.get_instructors()
    modules = config_loader.get_modules()
    return render_template('verification.html', instructors=instructors, modules=modules)


@app.route('/api/instructor/<instructor_id>/report')
def get_instructor_report(instructor_id):
    """Get HTML report for an instructor (API)."""
    try:
        html_report = email_notifier.generate_instructor_report_html(instructor_id)
        return jsonify({
            'success': True,
            'html': html_report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/send-reminder/<instructor_id>', methods=['POST'])
def send_reminder(instructor_id):
    """Send a review reminder email to an instructor (API)."""
    try:
        dry_run = request.json.get('dry_run', True)
        smtp_username = request.json.get('smtp_username', '')
        smtp_password = request.json.get('smtp_password', '')
        
        instructor = config_loader.get_instructor(instructor_id)
        subject = f"Vérification des logiciels d'enseignement - {instructor['name']}"
        
        result = email_notifier.send_reminder(
            instructor_id=instructor_id,
            subject=subject,
            dry_run=dry_run,
            smtp_username=smtp_username if not dry_run else None,
            smtp_password=smtp_password if not dry_run else None
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/summary-report')
def get_summary_report():
    """Get summary report (API)."""
    try:
        report = email_notifier.generate_summary_report()
        return jsonify({
            'success': True,
            'report': report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/settings')
def view_settings():
    """View settings page."""
    email_config = config_loader.get_email_config()
    report_config = config_loader.get_report_config()
    
    return render_template('settings.html',
                         email_config=email_config,
                         report_config=report_config)


@app.route('/health')
def health_check():
    """Health check endpoint."""
    try:
        # Validate configuration
        is_valid, errors = config_loader.validate_config()
        
        return jsonify({
            'status': 'healthy' if is_valid else 'degraded',
            'valid_config': is_valid,
            'errors': errors if errors else None,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# ========== AUTH ROUTES ==========

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler."""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['authenticated'] = True
            flash('Authentification réussie', 'success')
            return redirect(url_for('index'))
        else:
            flash('Mot de passe incorrect', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout handler."""
    session.pop('authenticated', None)
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('login'))


# ========== EDIT ROUTES ==========

@app.route('/api/instructor/add', methods=['POST'])
@require_auth
def add_instructor():
    """Add a new instructor (API)."""
    try:
        data = request.json
        instructor_id = data.get('id')
        instructor_data = {
            'name': data.get('name'),
            'email': data.get('email'),
            'department': data.get('department', ''),
            'modules': data.get('modules', [])
        }
        
        success = config_writer.add_instructor(instructor_id, instructor_data)
        
        if success:
            # Enforce single-responsibility: reassign listed modules to this instructor
            try:
                modules_to_assign = instructor_data.get('modules', []) or []
                if modules_to_assign:
                    # Remove module from all other instructors and set module's instructor_id
                    all_instructors = config_loader.get_instructors()
                    for mod_id in modules_to_assign:
                        # Remove from others
                        for inst_id, inst_data in all_instructors.items():
                            if inst_id != instructor_id:
                                mods = inst_data.get('modules', [])
                                if mod_id in mods:
                                    mods.remove(mod_id)
                                    config_writer.update_instructor(inst_id, {'modules': mods})
                        # Set module's instructor_id to this instructor
                        try:
                            config_writer.update_module(mod_id, {'instructor_id': instructor_id})
                        except Exception:
                            pass
            except Exception:
                pass

            reload_config()
            return jsonify({'success': True, 'message': 'Enseignant ajouté avec succès'})
        else:
            return jsonify({'success': False, 'error': "Cet ID ou cet email existe déjà"}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/instructor/<instructor_id>/update', methods=['POST'])
@require_auth
def update_instructor(instructor_id):
    """Update an instructor (API)."""
    try:
        data = request.json
        instructor_data = {}
        
        if 'name' in data:
            instructor_data['name'] = data['name']
        if 'email' in data:
            instructor_data['email'] = data['email']
        if 'department' in data:
            instructor_data['department'] = data['department']
        if 'modules' in data:
            instructor_data['modules'] = data['modules']
        
        success = config_writer.update_instructor(instructor_id, instructor_data)
        
        if success:
            # If modules updated, enforce single-responsibility
            try:
                if 'modules' in data:
                    new_modules = data.get('modules', []) or []
                    # Remove these modules from any other instructor and set module's instructor_id
                    all_instructors = config_loader.get_instructors()
                    for mod_id in new_modules:
                        for inst_id, inst_data in all_instructors.items():
                            if inst_id != instructor_id:
                                mods = inst_data.get('modules', [])
                                if mod_id in mods:
                                    mods.remove(mod_id)
                                    config_writer.update_instructor(inst_id, {'modules': mods})
                        try:
                            config_writer.update_module(mod_id, {'instructor_id': instructor_id})
                        except Exception:
                            pass
                    # For modules removed from this instructor, clear instructor_id
                    try:
                        current_inst = config_loader.get_instructor(instructor_id)
                        old_modules = current_inst.get('modules', [])
                        removed = [m for m in old_modules if m not in new_modules]
                        for mod_id in removed:
                            config_writer.update_module(mod_id, {'instructor_id': ''})
                    except Exception:
                        pass
            except Exception:
                pass

            reload_config()
            return jsonify({'success': True, 'message': 'Enseignant modifié avec succès'})
        else:
            return jsonify({'success': False, 'error': "Enseignant non trouvé ou email déjà utilisé"}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/instructor/<instructor_id>/delete', methods=['POST'])
@require_auth
def delete_instructor(instructor_id):
    """Delete an instructor (API)."""
    try:
        success = config_writer.delete_instructor(instructor_id)
        
        if success:
            reload_config()
            return jsonify({'success': True, 'message': 'Enseignant supprimé avec succès'})
        else:
            return jsonify({'success': False, 'error': 'Enseignant non trouvé'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/module/add', methods=['POST'])
@require_auth
def add_module():
    """Add a new module (API)."""
    try:
        data = request.json
        module_id = data.get('id')
        
        # Vérifier si l'ID existe déjà
        try:
            existing = config_loader.get_module(module_id)
            return jsonify({'success': False, 'error': 'Cet ID de module existe déjà'}), 400
        except ValueError:
            pass  # L'ID n'existe pas, on peut continuer
        
        module_data = {
            'name': data.get('name'),
            'description': data.get('description', ''),
            'semester': data.get('semester', ''),
            'year': int(data.get('year', 1)),
            'code': data.get('code', ''),
            'os_required': data.get('os_required', []),
            'software': data.get('software', []),
            'instructor_id': data.get('instructor_id', '')
        }
        
        success = config_writer.add_module(module_id, module_data)

        if success:
            # Si un enseignant est assigné, appliquer l'unicité
            instructor_id = data.get('instructor_id')
            if instructor_id:
                try:
                    # Retirer le module de tous les autres enseignants
                    all_instructors = config_loader.get_instructors()
                    for inst_id, inst_data in all_instructors.items():
                        mods = inst_data.get('modules', [])
                        if module_id in mods and inst_id != instructor_id:
                            mods.remove(module_id)
                            config_writer.update_instructor(inst_id, {'modules': mods})

                    # Ajouter le module à l'enseignant cible s'il n'y est pas
                    target = config_loader.get_instructor(instructor_id)
                    target_mods = target.get('modules', [])
                    if module_id not in target_mods:
                        target_mods.append(module_id)
                        config_writer.update_instructor(instructor_id, {'modules': target_mods})
                except ValueError:
                    pass  # Enseignant non trouvé, ignorer
            
            reload_config()
            return jsonify({'success': True, 'message': 'Module ajouté avec succès'})
        else:
            return jsonify({'success': False, 'error': 'Cet ID ou code de module existe déjà'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/module/<module_id>/update', methods=['POST'])
@require_auth
def update_module(module_id):
    """Update a module (API)."""
    try:
        data = request.json
        module_data = {}
        
        if 'name' in data:
            module_data['name'] = data['name']
        if 'description' in data:
            module_data['description'] = data['description']
        if 'semester' in data:
            module_data['semester'] = data['semester']
        if 'year' in data:
            module_data['year'] = int(data['year'])
        if 'code' in data:
            module_data['code'] = data['code']
        if 'os_required' in data:
            module_data['os_required'] = data['os_required']
        if 'instructor_id' in data:
            module_data['instructor_id'] = data['instructor_id']
        
        success = config_writer.update_module(module_id, module_data)

        if success:
            # Gérer l'assignation bidirectionnelle avec l'enseignant
            new_instructor_id = data.get('instructor_id')
            
            # Trouver l'ancien enseignant qui avait ce module et le retirer de sa liste
            all_instructors = config_loader.get_instructors()
            for inst_id, instructor in all_instructors.items():
                modules = instructor.get('modules', [])
                if module_id in modules:
                    if inst_id != new_instructor_id:
                        modules.remove(module_id)
                        config_writer.update_instructor(inst_id, {'modules': modules})
            
            # Ajouter le module au nouvel enseignant
            if new_instructor_id:
                try:
                    instructor = config_loader.get_instructor(new_instructor_id)
                    modules = instructor.get('modules', [])
                    if module_id not in modules:
                        modules.append(module_id)
                        config_writer.update_instructor(new_instructor_id, {'modules': modules})
                except ValueError:
                    pass  # Enseignant non trouvé

        if success:
            reload_config()
            return jsonify({'success': True, 'message': 'Module modifié avec succès'})
        else:
            return jsonify({'success': False, 'error': 'Module non trouvé ou code déjà utilisé'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/module/<module_id>/delete', methods=['POST'])
@require_auth
def delete_module(module_id):
    """Delete a module (API)."""
    try:
        success = config_writer.delete_module(module_id)
        
        if success:
            reload_config()
            return jsonify({'success': True, 'message': 'Module supprimé avec succès'})
        else:
            return jsonify({'success': False, 'error': 'Module non trouvé'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/module/<module_id>/software/add', methods=['POST'])
@require_auth
def add_software(module_id):
    """Add software to a module (API)."""
    try:
        data = request.json
        software_data = {
            'name': data.get('name'),
            'purpose': data.get('purpose', ''),
            'category': data.get('category', ''),
            'version': data.get('version', 'Latest'),
            'notes': data.get('notes', ''),
            'critical': data.get('critical', False),
            'verified_by': data.get('verified_by', ''),
            'os_supported': data.get('os_supported', [])
        }
        
        success = config_writer.add_software_to_module(module_id, software_data)
        
        if success:
            reload_config()
            return jsonify({'success': True, 'message': 'Logiciel ajouté avec succès'})
        else:
            return jsonify({'success': False, 'error': 'Module non trouvé'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/module/<module_id>/software/<software_name>/update', methods=['POST'])
@require_auth
def update_software(module_id, software_name):
    """Update software in a module (API)."""
    try:
        data = request.json
        software_data = {}
        
        if 'purpose' in data:
            software_data['purpose'] = data['purpose']
        if 'category' in data:
            software_data['category'] = data['category']
        if 'version' in data:
            software_data['version'] = data['version']
        if 'notes' in data:
            software_data['notes'] = data['notes']
        if 'critical' in data:
            software_data['critical'] = data['critical']
        if 'verified_by' in data:
            software_data['verified_by'] = data['verified_by']
        if 'os_supported' in data:
            software_data['os_supported'] = data['os_supported']
        
        software_data['last_verified'] = datetime.now().strftime('%Y-%m-%d')
        
        success = config_writer.update_software_in_module(module_id, software_name, software_data)
        
        if success:
            reload_config()
            return jsonify({'success': True, 'message': 'Logiciel modifié avec succès'})
        else:
            return jsonify({'success': False, 'error': 'Logiciel non trouvé'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/module/<module_id>/software/<software_name>/delete', methods=['POST'])
@require_auth
def delete_software(module_id, software_name):
    """Delete software from a module (API)."""
    try:
        success = config_writer.delete_software_from_module(module_id, software_name)
        
        if success:
            reload_config()
            return jsonify({'success': True, 'message': 'Logiciel supprimé avec succès'})
        else:
            return jsonify({'success': False, 'error': 'Logiciel non trouvé'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/excel/export', methods=['POST'])
@require_auth
def excel_export():
    """Export YAML config to Excel file."""
    try:
        success, message = excel_sync.export_to_excel()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/excel/import', methods=['POST'])
@require_auth
def excel_import():
    """Import data from Excel file to YAML config."""
    try:
        success, message = excel_sync.import_from_excel()
        if success:
            reload_config()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/excel/status', methods=['GET'])
def excel_status():
    """Get sync status between YAML and Excel."""
    try:
        status = excel_sync.get_sync_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/excel/download')
def excel_download():
    """Serve the Excel file for download."""
    try:
        path = excel_sync.excel_path
        if not path.exists():
            return jsonify({'success': False, 'error': 'Excel file not found'}), 404
        return send_file(str(path), as_attachment=True, download_name=path.name)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return render_template('500.html', error=str(error)), 500


if __name__ == '__main__':
    # Check configuration validity
    is_valid, errors = config_loader.validate_config()
    
    if not is_valid:
        print("[!] Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nStarting application anyway...\n")
    else:
        print("[OK] Configuration is valid\n")
    
    # Create Excel file if it doesn't exist
    excel_sync._ensure_excel_exists()
    print("[OK] Excel file ready at", excel_sync.excel_path)
    
    # Start the Flask development server
    print("Starting Teaching Software Manager web interface...")
    print("Visit: http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
