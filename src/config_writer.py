"""
YAML configuration writer for Teaching Software Manager.
Handles saving changes back to the YAML configuration file.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import shutil


class ConfigWriter:
    """Write and update YAML configuration file."""

    def __init__(self, config_path: str = None):
        """
        Initialize the config writer.
        
        Args:
            config_path: Path to the YAML config file.
        """
        if config_path is None:
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "teaching_software.yml"
        
        self.config_path = Path(config_path)

    def _backup_config(self):
        """Create a backup of the current configuration."""
        backup_path = self.config_path.with_suffix('.yml.backup')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        timestamped_backup = self.config_path.parent / f"teaching_software_{timestamp}.yml.backup"
        
        shutil.copy2(self.config_path, backup_path)
        shutil.copy2(self.config_path, timestamped_backup)
        
        return backup_path

    def _load_config(self) -> Dict[str, Any]:
        """Load the current configuration."""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def add_instructor(self, instructor_id: str, instructor_data: Dict[str, Any]) -> bool:
        """Add a new instructor."""
        try:
            self._backup_config()
            config = self._load_config()
            
            if 'instructors' not in config:
                config['instructors'] = {}
            
            # Empêcher les doublons d'ID
            if instructor_id in config['instructors']:
                return False  # Already exists

            # Empêcher les doublons d'email
            existing_emails = {inst.get('email') for inst in config['instructors'].values()}
            if instructor_data.get('email') in existing_emails:
                return False
            
            instructor_data['last_review'] = datetime.now().strftime('%Y-%m-%d')
            config['instructors'][instructor_id] = instructor_data
            
            self._save_config(config)
            return True
        except Exception as e:
            print(f"Error adding instructor: {e}")
            return False

    def update_instructor(self, instructor_id: str, instructor_data: Dict[str, Any]) -> bool:
        """Update an existing instructor."""
        try:
            self._backup_config()
            config = self._load_config()
            
            if 'instructors' not in config or instructor_id not in config['instructors']:
                return False  # Doesn't exist

            # Empêcher doublon d'email lors de la mise à jour
            if 'email' in instructor_data:
                new_email = instructor_data.get('email')
                for inst_key, inst_val in config['instructors'].items():
                    if inst_key != instructor_id and inst_val.get('email') == new_email:
                        return False
            
            config['instructors'][instructor_id].update(instructor_data)
            
            self._save_config(config)
            return True
        except Exception as e:
            print(f"Error updating instructor: {e}")
            return False

    def delete_instructor(self, instructor_id: str) -> bool:
        """Delete an instructor."""
        try:
            self._backup_config()
            config = self._load_config()
            
            if 'instructors' not in config or instructor_id not in config['instructors']:
                return False  # Doesn't exist
            
            del config['instructors'][instructor_id]
            
            self._save_config(config)
            return True
        except Exception as e:
            print(f"Error deleting instructor: {e}")
            return False

    def add_module(self, module_id: str, module_data: Dict[str, Any]) -> bool:
        """Add a new module."""
        try:
            self._backup_config()
            config = self._load_config()
            
            if 'modules' not in config:
                config['modules'] = {}
            
            # Empêcher doublons d'ID
            if module_id in config['modules']:
                return False  # Already exists

            # Empêcher doublons de code
            new_code = module_data.get('code')
            if new_code:
                for mod_val in config['modules'].values():
                    if mod_val.get('code') == new_code:
                        return False
            
            config['modules'][module_id] = module_data
            
            self._save_config(config)
            return True
        except Exception as e:
            print(f"Error adding module: {e}")
            return False

    def update_module(self, module_id: str, module_data: Dict[str, Any]) -> bool:
        """Update an existing module."""
        try:
            self._backup_config()
            config = self._load_config()
            
            if 'modules' not in config or module_id not in config['modules']:
                return False  # Doesn't exist

            # Empêcher doublon de code lors de la mise à jour
            if 'code' in module_data and module_data.get('code'):
                new_code = module_data.get('code')
                for mod_key, mod_val in config['modules'].items():
                    if mod_key != module_id and mod_val.get('code') == new_code:
                        return False
            
            config['modules'][module_id].update(module_data)
            
            self._save_config(config)
            return True
        except Exception as e:
            print(f"Error updating module: {e}")
            return False

    def delete_module(self, module_id: str) -> bool:
        """Delete a module."""
        try:
            self._backup_config()
            config = self._load_config()
            
            if 'modules' not in config or module_id not in config['modules']:
                return False  # Doesn't exist
            
            del config['modules'][module_id]
            
            # Remove module from instructors
            if 'instructors' in config:
                for inst_data in config['instructors'].values():
                    if 'modules' in inst_data and module_id in inst_data['modules']:
                        inst_data['modules'].remove(module_id)
            
            self._save_config(config)
            return True
        except Exception as e:
            print(f"Error deleting module: {e}")
            return False

    def add_software_to_module(self, module_id: str, software_data: Dict[str, Any]) -> bool:
        """Add software to a module."""
        try:
            self._backup_config()
            config = self._load_config()
            
            if 'modules' not in config or module_id not in config['modules']:
                return False  # Module doesn't exist
            
            if 'software' not in config['modules'][module_id]:
                config['modules'][module_id]['software'] = []

            # Empêcher doublons de nom de logiciel dans le même module
            existing_names = {sw.get('name') for sw in config['modules'][module_id]['software']}
            if software_data.get('name') in existing_names:
                return False
            
            software_data['last_verified'] = datetime.now().strftime('%Y-%m-%d')
            config['modules'][module_id]['software'].append(software_data)
            
            self._save_config(config)
            return True
        except Exception as e:
            print(f"Error adding software: {e}")
            return False

    def update_software_in_module(self, module_id: str, software_name: str, software_data: Dict[str, Any]) -> bool:
        """Update software in a module."""
        try:
            self._backup_config()
            config = self._load_config()
            
            if 'modules' not in config or module_id not in config['modules']:
                return False
            
            if 'software' not in config['modules'][module_id]:
                return False
            
            # Find and update the software
            for idx, software in enumerate(config['modules'][module_id]['software']):
                if software.get('name') == software_name:
                    config['modules'][module_id]['software'][idx].update(software_data)
                    self._save_config(config)
                    return True
            
            return False  # Software not found
        except Exception as e:
            print(f"Error updating software: {e}")
            return False

    def delete_software_from_module(self, module_id: str, software_name: str) -> bool:
        """Delete software from a module."""
        try:
            self._backup_config()
            config = self._load_config()
            
            if 'modules' not in config or module_id not in config['modules']:
                return False
            
            if 'software' not in config['modules'][module_id]:
                return False
            
            # Find and remove the software
            original_length = len(config['modules'][module_id]['software'])
            config['modules'][module_id]['software'] = [
                s for s in config['modules'][module_id]['software']
                if s.get('name') != software_name
            ]
            
            if len(config['modules'][module_id]['software']) < original_length:
                self._save_config(config)
                return True
            
            return False  # Software not found
        except Exception as e:
            print(f"Error deleting software: {e}")
            return False
