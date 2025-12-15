"""
Test script to validate the Teaching Software Manager installation.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        import yaml
        print("  ✓ PyYAML")
    except ImportError as e:
        print(f"  ✗ PyYAML: {e}")
        return False
    
    try:
        import flask
        print("  ✓ Flask")
    except ImportError as e:
        print(f"  ✗ Flask: {e}")
        return False
    
    try:
        from config_loader import ConfigLoader
        print("  ✓ ConfigLoader")
    except ImportError as e:
        print(f"  ✗ ConfigLoader: {e}")
        return False
    
    try:
        from email_notifier import EmailNotifier
        print("  ✓ EmailNotifier")
    except ImportError as e:
        print(f"  ✗ EmailNotifier: {e}")
        return False
    
    return True


def test_config_file():
    """Test that configuration file exists and is valid."""
    print("\nTesting configuration file...")
    
    try:
        from config_loader import ConfigLoader
        loader = ConfigLoader()
        
        is_valid, errors = loader.validate_config()
        
        if is_valid:
            print("  ✓ Configuration file is valid")
            return True
        else:
            print("  ✗ Configuration validation errors:")
            for error in errors:
                print(f"    - {error}")
            return False
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_config_content():
    """Test that configuration has expected content."""
    print("\nTesting configuration content...")
    
    try:
        from config_loader import ConfigLoader
        loader = ConfigLoader()
        
        instructors = loader.get_instructors()
        modules = loader.get_modules()
        
        print(f"  ✓ Found {len(instructors)} instructors")
        print(f"  ✓ Found {len(modules)} modules")
        
        # Check for at least one instructor and module
        if instructors and modules:
            first_inst = list(instructors.values())[0]
            first_mod = list(modules.values())[0]
            
            print(f"    - Sample instructor: {first_inst.get('name', 'N/A')}")
            print(f"    - Sample module: {first_mod.get('name', 'N/A')}")
            
            return True
        else:
            print("  ⚠ Configuration is valid but may need content")
            return True
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_email_config():
    """Test email configuration."""
    print("\nTesting email configuration...")
    
    try:
        from config_loader import ConfigLoader
        loader = ConfigLoader()
        
        email_config = loader.get_email_config()
        
        if email_config.get('enabled'):
            print("  ✓ Email notifications enabled")
            print(f"    - SMTP Server: {email_config.get('smtp_server')}")
            print(f"    - SMTP Port: {email_config.get('smtp_port')}")
            
            # Check for credentials
            import os
            if os.getenv('EMAIL_USERNAME') and os.getenv('EMAIL_PASSWORD'):
                print("  ✓ Email credentials found in environment")
            else:
                print("  ⚠ Email credentials not found in environment (set EMAIL_USERNAME and EMAIL_PASSWORD)")
        else:
            print("  ℹ Email notifications disabled")
        
        return True
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_web_app_structure():
    """Test that web application structure exists."""
    print("\nTesting web application structure...")
    
    base_dir = Path(__file__).parent
    
    required_dirs = [
        'templates',
        'static',
        'web',
        'src',
        'config'
    ]
    
    required_files = [
        'web/app.py',
        'config/teaching_software.yml',
        'requirements.txt',
        'README.md'
    ]
    
    all_good = True
    
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ (missing)")
            all_good = False
    
    for file_name in required_files:
        file_path = base_dir / file_name
        if file_path.exists():
            print(f"  ✓ {file_name}")
        else:
            print(f"  ✗ {file_name} (missing)")
            all_good = False
    
    return all_good


def main():
    """Run all tests."""
    print("=" * 60)
    print("Teaching Software Manager - Installation Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Configuration File", test_config_file()))
    results.append(("Configuration Content", test_config_content()))
    results.append(("Email Configuration", test_email_config()))
    results.append(("Web App Structure", test_web_app_structure()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:<30} {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! Ready to use.")
        print("\nNext steps:")
        print("  1. Configure email (optional): Set EMAIL_USERNAME and EMAIL_PASSWORD")
        print("  2. Start web app: python web/app.py")
        print("  3. Visit: http://localhost:5000")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
