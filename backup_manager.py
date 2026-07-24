import sys
import os
import signal
import subprocess
from datetime import datetime

LOG_FILE = os.path.join("logs", "backup_manager.log")
SCHEDULE_FILE = "backup_schedules.txt"
PID_FILE = ".backup_service.pid"
BACKUPS_DIR = "backups"

def log_message(message):
    try:
        os.makedirs("logs", exist_ok=True)
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass

def is_valid_time(time_str):
    try:
        parts = time_str.split(":")
        if len(parts) != 2:
            return False
        h, m = int(parts[0]), int(parts[1])
        if len(parts[0]) != 2 or len(parts[1]) != 2:
            return False
        return 0 <= h <= 23 and 0 <= m <= 59
    except Exception:
        return False

def is_valid_schedule(schedule_str):
    try:
        parts = schedule_str.split(";")
        if len(parts) != 3:
            return False
        path_str, time_str, name_str = parts[0].strip(), parts[1].strip(), parts[2].strip()
        if not path_str or not name_str:
            return False
        return is_valid_time(time_str)
    except Exception:
        return False

def get_service_pid():
    try:
        if os.path.exists(PID_FILE):
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)
                return pid
            except OSError:
                if os.path.exists(PID_FILE):
                    os.remove(PID_FILE)
        output = subprocess.check_output(["ps", "-A", "-o", "pid,command"], text=True)
        for line in output.splitlines():
            if "backup_service.py" in line and "python" in line:
                pid = int(line.strip().split()[0])
                if pid != os.getpid():
                    with open(PID_FILE, "w") as f:
                        f.write(str(pid))
                    return pid
    except Exception:
        pass
    return None

def cmd_create(schedule_str):
    try:
        if not is_valid_schedule(schedule_str):
            log_message(f"Error: malformed schedule: {schedule_str}")
            return
        with open(SCHEDULE_FILE, "a") as f:
            f.write(schedule_str.strip() + "\n")
        log_message(f"New schedule added: {schedule_str.strip()}")
    except Exception:
        log_message(f"Error: malformed schedule: {schedule_str}")

def cmd_list():
    try:
        if not os.path.exists(SCHEDULE_FILE):
            log_message("Error: can't find backup_schedules.txt")
            return
        with open(SCHEDULE_FILE, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        for idx, line in enumerate(lines):
            print(f"{idx}: {line}")
        log_message("Show schedules list")
    except Exception:
        log_message("Error: can't find backup_schedules.txt")

def cmd_delete(index_str):
    try:
        if not os.path.exists(SCHEDULE_FILE):
            log_message("Error: can't find backup_schedules.txt")
            return
        with open(SCHEDULE_FILE, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        idx = int(index_str)
        if idx < 0 or idx >= len(lines):
            log_message(f"Error: can't find schedule at index {index_str}")
            return
        lines.pop(idx)
        with open(SCHEDULE_FILE, "w") as f:
            for line in lines:
                f.write(line + "\n")
        log_message(f"Schedule at index {idx} deleted")
    except Exception:
        log_message(f"Error: can't find schedule at index {index_str}")

def cmd_start():
    try:
        pid = get_service_pid()
        if pid is not None:
            log_message("Error: backup_service already running")
            return
        service_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup_service.py")
        proc = subprocess.Popen([sys.executable, service_script], start_new_session=True)
        with open(PID_FILE, "w") as f:
            f.write(str(proc.pid))
        log_message("backup_service started")
    except Exception:
        log_message("Error: can't start backup_service")

def cmd_stop():
    try:
        pid = get_service_pid()
        if pid is None:
            log_message("Error: can't stop backup_service")
            return
        os.kill(pid, signal.SIGTERM)
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        log_message("backup_service stopped")
    except Exception:
        log_message("Error: can't stop backup_service")

def cmd_backups():
    try:
        if not os.path.exists(BACKUPS_DIR):
            log_message("Error: can't find backups directory")
            return
        files = os.listdir(BACKUPS_DIR)
        for fname in sorted(files):
            print(fname)
        log_message("Show backups list")
    except Exception:
        log_message("Error: can't find backups directory")

def main():
    try:
        if len(sys.argv) < 2:
            log_message("Error: unknown command")
            return
        cmd = sys.argv[1]
        if cmd == "create":
            if len(sys.argv) < 3:
                log_message("Error: malformed schedule: ")
            else:
                cmd_create(sys.argv[2])
        elif cmd == "list":
            cmd_list()
        elif cmd == "delete":
            if len(sys.argv) < 3:
                log_message("Error: can't find schedule at index ")
            else:
                cmd_delete(sys.argv[2])
        elif cmd == "start":
            cmd_start()
        elif cmd == "stop":
            cmd_stop()
        elif cmd == "backups":
            cmd_backups()
        else:
            log_message("Error: unknown command")
    except Exception:
        log_message("Error: unknown command")

if __name__ == "__main__":
    main()
