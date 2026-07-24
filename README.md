# Backup Manager

Backup Manager is a Python-based automated backup system that schedules and executes directory and file backups via command line interface and a background daemon service.

## Project Structure

- `backup_manager.py`: Command-line interface to manage schedule entries, query backup history, and start/stop the background service.
- `backup_service.py`: Daemon service running in an infinite loop that monitors backup schedules and archives files into compressed `.tar` files.
- `backup_schedules.txt`: File storing schedule entries in format `path_to_save;HH:MM;backup_name`.
- `logs/`: Contains `backup_manager.log` and `backup_service.log`.
- `backups/`: Target storage location for compressed `.tar` backup archives.

## Usage

### Create a Schedule
```bash
python3 ./backup_manager.py create "path_to_save;HH:MM;backup_name"
```

### List Schedules
```bash
python3 ./backup_manager.py list
```

### Delete a Schedule
```bash
python3 ./backup_manager.py delete <index>
```

### Start the Background Service
```bash
python3 ./backup_manager.py start
```

### Stop the Background Service
```bash
python3 ./backup_manager.py stop
```

### View Created Backups
```bash
python3 ./backup_manager.py backups
```
