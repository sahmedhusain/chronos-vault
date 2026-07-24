import os
import sys
import time
import tarfile
from datetime import datetime

LOG_FILE = os.path.join("logs", "backup_service.log")
SCHEDULE_FILE = "backup_schedules.txt"
BACKUPS_DIR = "backups"

def log_message(message):
    try:
        os.makedirs("logs", exist_ok=True)
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass

def parse_time(time_str):
    try:
        parts = time_str.split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except Exception:
        return None

def perform_backup(path_to_save, backup_name):
    try:
        os.makedirs(BACKUPS_DIR, exist_ok=True)
        tar_filename = f"{backup_name}.tar"
        tar_path = os.path.join(BACKUPS_DIR, tar_filename)
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(path_to_save, arcname=os.path.basename(path_to_save))
        log_message(f"Backup done for {path_to_save} in backups/{tar_filename}")
        return True
    except Exception as e:
        log_message(f"Error: failed backup for {path_to_save}: {e}")
        return False

def check_and_run_schedules():
    try:
        if not os.path.exists(SCHEDULE_FILE):
            return
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute
        with open(SCHEDULE_FILE, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        remaining_lines = []
        for line in lines:
            try:
                parts = line.split(";")
                if len(parts) != 3:
                    continue
                path_to_save = parts[0].strip()
                time_str = parts[1].strip()
                backup_name = parts[2].strip()
                sched_minutes = parse_time(time_str)
                if sched_minutes is None:
                    continue
                if sched_minutes == current_minutes:
                    perform_backup(path_to_save, backup_name)
                elif sched_minutes > current_minutes:
                    remaining_lines.append(line)
            except Exception:
                pass
        with open(SCHEDULE_FILE, "w") as f:
            for rline in remaining_lines:
                f.write(rline + "\n")
    except Exception:
        pass

def main():
    while True:
        try:
            check_and_run_schedules()
        except Exception:
            pass
        time.sleep(45)

if __name__ == "__main__":
    main()
