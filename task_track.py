import os
import sys
import win32api
import win32con
import win32security
import wmi
from datetime import datetime

# List of high-impact privileges to check
WATCHED_PRIVILEGES = {
    "SeDebugPrivilege", "SeBackupPrivilege", "SeLoadDriverPrivilege",
    "SeRestorePrivilege", "SeTakeOwnershipPrivilege", "SeTcbPrivilege",
    "SeImpersonatePrivilege", "SeAssignPrimaryTokenPrivilege"
}

def log_to_file(message):
    with open('process_monitor_log.csv', 'a') as fd:
        fd.write(message + '\n')

def get_process_privileges(pid):
    try:
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
        htoken = win32security.OpenProcessToken(hproc, win32con.TOKEN_QUERY)
        privs = win32security.GetTokenInformation(htoken, win32security.TokenPrivileges)

        enabled_privs = []
        for priv_id, flags in privs:
            if flags & (win32con.SE_PRIVILEGE_ENABLED | win32con.SE_PRIVILEGE_ENABLED_BY_DEFAULT):
                priv_name = win32security.LookupPrivilegeName(None, priv_id)
                if priv_name in WATCHED_PRIVILEGES:
                    enabled_privs.append(priv_name)

        return ','.join(enabled_privs) if enabled_privs else 'None'
    except Exception:
        return 'Unavailable'

def monitor():
    header = 'CommandLine,Time,Executable,ParentPID,PID,User,Privileges'
    log_to_file(header)

    c = wmi.WMI()
    process_watcher = c.Win32_Process.watch_for('creation')

    while True:
        try:
            new_process = process_watcher()
            cmdline = new_process.CommandLine or "N/A"
            executable = new_process.ExecutablePath or "N/A"
            parent_pid = new_process.ParentProcessId
            pid = new_process.ProcessId
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                owner_info = new_process.GetOwner()
                proc_owner = f"{owner_info[0]}\\{owner_info[1]}"
            except:
                proc_owner = "N/A"

            privileges = get_process_privileges(pid)

            log_entry = (
                f'"{cmdline}","{timestamp}","{executable}",'
                f'{parent_pid},{pid},"{proc_owner}","{privileges}"'
            )

            print(log_entry)
            print()
            log_to_file(log_entry)

        except Exception as e:
            # Optionally log the error for debugging
            # print(f"Error: {e}")
            pass

if __name__ == '__main__':
    monitor()
