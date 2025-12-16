"""
Configuration loader for teaching software management system.
Reads and validates the YAML configuration file.
"""

import os
import yaml
from typing import Dict, List, Any
from pathlib import Path


class ConfigLoader:
    """Load and manage teaching software configuration."""

    def __init__(self, config_path: str = None):
        """
        Initialize the config loader.
        
        Args:
            config_path: Path to the YAML config file. 
                        Defaults to ../config/teaching_software.yml
        """
        if config_path is None:
            # Default to config folder relative to this script
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "teaching_software.yml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load and parse the YAML configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if config is None:
            raise ValueError("Configuration file is empty")
        
        return config

    def get_instructors(self) -> Dict[str, Dict[str, Any]]:
        """Get all instructors."""
        return self.config.get('instructors', {})

    def get_modules(self) -> Dict[str, Dict[str, Any]]:
        """Get all modules."""
        return self.config.get('modules', {})

    def get_instructor(self, instructor_id: str) -> Dict[str, Any]:
        """Get a specific instructor by ID."""
        instructors = self.get_instructors()
        if instructor_id not in instructors:
            raise ValueError(f"Instructor not found: {instructor_id}")
        return instructors[instructor_id]

    def get_module(self, module_id: str) -> Dict[str, Any]:
        """Get a specific module by ID."""
        modules = self.get_modules()
        if module_id not in modules:
            raise ValueError(f"Module not found: {module_id}")
        return modules[module_id]

    def get_instructor_modules(self, instructor_id: str) -> List[str]:
        """Get all module IDs for an instructor."""
        instructor = self.get_instructor(instructor_id)
        return instructor.get('modules', [])

    def get_instructor_module_details(self, instructor_id: str) -> List[Dict[str, Any]]:
        """Get full details of all modules for an instructor."""
        module_ids = self.get_instructor_modules(instructor_id)
        modules = self.get_modules()
        
        result = []
        for module_id in module_ids:
            if module_id in modules:
                module = modules[module_id].copy()
                module['id'] = module_id
                result.append(module)
        
        return result

    def get_email_config(self) -> Dict[str, Any]:
        """Get email configuration."""
        return self.config.get('email_config', {})

    def get_report_config(self) -> Dict[str, Any]:
        """Get report configuration."""
        return self.config.get('report_config', {})



    def get_module_software(self, module_id: str) -> List[Dict[str, Any]]:
        """Get all software for a specific module."""
        module = self.get_module(module_id)
        return module.get('software', [])

    def validate_config(self) -> tuple[bool, List[str]]:
        """
        Validate the configuration file.
        
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check required top-level keys
        required_keys = ['instructors', 'modules']
        for key in required_keys:
            if key not in self.config:
                errors.append(f"Missing required key: {key}")
        
        # Validate instructors
        instructors = self.get_instructors()
        for inst_id, inst_data in instructors.items():
            if 'email' not in inst_data:
                errors.append(f"Instructor {inst_id} missing email")
            if 'modules' not in inst_data:
                errors.append(f"Instructor {inst_id} missing modules list")
            else:
                # Verify referenced modules exist
                modules = self.get_modules()
                for mod_id in inst_data['modules']:
                    if mod_id not in modules:
                        errors.append(f"Instructor {inst_id} references non-existent module: {mod_id}")
        
        # Validate modules
        modules = self.get_modules()
        for mod_id, mod_data in modules.items():
            if 'name' not in mod_data:
                errors.append(f"Module {mod_id} missing name")
            if 'software' not in mod_data:
                errors.append(f"Module {mod_id} missing software list")
            else:
                for idx, soft in enumerate(mod_data['software']):
                    if 'name' not in soft:
                        errors.append(f"Module {mod_id} software #{idx} missing name")
                    if 'purpose' not in soft:
                        errors.append(f"Module {mod_id} software {soft.get('name', '?')} missing purpose")
        
        return len(errors) == 0, errors


if __name__ == "__main__":
    # Test the configuration loader
    try:
        loader = ConfigLoader()
        
        # Validate config
        is_valid, errors = loader.validate_config()
        if is_valid:
            print("✓ Configuration is valid")
        else:
            print("✗ Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
        
        # Display summary
        instructors = loader.get_instructors()
        modules = loader.get_modules()
        
        print(f"\nLoaded {len(instructors)} instructors and {len(modules)} modules")
        
        # Show one instructor's modules
        if instructors:
            first_inst_id = list(instructors.keys())[0]
            first_inst = instructors[first_inst_id]
            print(f"\nExample - {first_inst['name']}:")
            for module in loader.get_instructor_module_details(first_inst_id):
                print(f"  - {module['name']}: {len(module.get('software', []))} software items")
    
    except Exception as e:
        print(f"Error: {e}")
