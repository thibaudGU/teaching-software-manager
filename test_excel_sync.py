import sys
sys.path.insert(0, 'src')
from config_loader import ConfigLoader
from excel_sync import ExcelSyncManager

loader = ConfigLoader()
sync = ExcelSyncManager(loader)
sync._ensure_excel_exists()
print('✓ Excel file created')

status = sync.get_sync_status()
print('✓ YAML:', status['yaml'])
print('✓ Excel file exists:', status['excel_exists'])
print('✓ Excel path:', status['excel_path'])
