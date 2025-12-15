"""
Command-line utility scripts for Teaching Software Manager.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config_loader import ConfigLoader
from email_notifier import EmailNotifier
import argparse
from datetime import datetime


def validate_command():
    """Validate the configuration file."""
    try:
        loader = ConfigLoader()
        is_valid, errors = loader.validate_config()
        
        if is_valid:
            print("✓ Configuration is valid")
            return 0
        else:
            print("✗ Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return 1
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


def list_command(args):
    """List instructors or modules."""
    try:
        loader = ConfigLoader()
        
        if args.type == 'instructors':
            instructors = loader.get_instructors()
            print(f"\n{'ID':<15} {'Name':<30} {'Email':<30} {'Modules':<20}")
            print("-" * 95)
            for inst_id, inst_data in instructors.items():
                modules = ', '.join(inst_data.get('modules', []))
                print(f"{inst_id:<15} {inst_data.get('name', '?'):<30} {inst_data.get('email', '?'):<30} {modules:<20}")
        
        elif args.type == 'modules':
            modules = loader.get_modules()
            print(f"\n{'ID':<20} {'Name':<30} {'Year':<5} {'Semester':<10} {'Software':<10}")
            print("-" * 75)
            for mod_id, mod_data in modules.items():
                soft_count = len(mod_data.get('software', []))
                print(f"{mod_id:<20} {mod_data.get('name', '?'):<30} {mod_data.get('year', '?'):<5} {mod_data.get('semester', '?'):<10} {soft_count:<10}")
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


def report_command(args):
    """Generate reports."""
    try:
        loader = ConfigLoader()
        notifier = EmailNotifier(loader)
        
        if args.report_type == 'summary':
            print("\n" + notifier.generate_summary_report())
        
        elif args.report_type == 'instructor' and args.instructor_id:
            html = notifier.generate_instructor_report_html(args.instructor_id)
            # Save to file if requested
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"✓ Report saved to {args.output}")
            else:
                print("HTML Report generated (saved to output file with --output flag)")
                print(f"Length: {len(html)} characters")
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


def send_command(args):
    """Send reminder emails."""
    try:
        loader = ConfigLoader()
        notifier = EmailNotifier(loader)
        
        if args.instructor_id:
            # Send to single instructor
            instructor = loader.get_instructor(args.instructor_id)
            html = notifier.generate_instructor_report_html(args.instructor_id)
            subject = f"Teaching Software Review Required - {instructor['name']}"
            
            success = notifier.send_email(
                to_email=instructor['email'],
                subject=subject,
                html_body=html
            )
            
            return 0 if success else 1
        else:
            # Send to all instructors
            results = notifier.send_review_reminders(dry_run=args.dry_run)
            
            success_count = sum(1 for v in results.values() if v)
            total_count = len(results)
            
            print(f"\n✓ Sent to {success_count}/{total_count} instructors")
            return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Teaching Software Manager - CLI Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py validate                    # Validate configuration
  python cli.py list instructors            # List all instructors
  python cli.py list modules                # List all modules
  python cli.py report summary              # Generate summary report
  python cli.py report instructor prof_001  # Generate instructor report
  python cli.py send --dry-run               # Send test emails to all
  python cli.py send --instructor prof_001  # Send email to specific instructor
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate configuration file')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List instructors or modules')
    list_parser.add_argument('type', choices=['instructors', 'modules'], help='What to list')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate reports')
    report_parser.add_argument('report_type', choices=['summary', 'instructor'], help='Report type')
    report_parser.add_argument('--instructor-id', help='Instructor ID (for instructor reports)')
    report_parser.add_argument('--output', '-o', help='Output file path')
    
    # Send command
    send_parser = subparsers.add_parser('send', help='Send reminder emails')
    send_parser.add_argument('--instructor-id', '-i', help='Send to specific instructor')
    send_parser.add_argument('--dry-run', action='store_true', default=True, help='Simulate sending (default)')
    send_parser.add_argument('--real', action='store_true', dest='real', help='Actually send emails')
    
    args = parser.parse_args()
    
    # Handle dry-run logic
    if hasattr(args, 'real') and args.real:
        args.dry_run = False
    
    # Dispatch to command handlers
    if args.command == 'validate':
        return validate_command()
    elif args.command == 'list':
        return list_command(args)
    elif args.command == 'report':
        return report_command(args)
    elif args.command == 'send':
        return send_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
