import datetime
import json
import os
import time
import pytz

class Logger:
    def __init__(self, service_name: str, vm_name: str, log_status_value):
        self.service_name = service_name
        self.vm_name = vm_name
        self.log_status_value = log_status_value
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
        self._logic_list = {
            0000: {"code": "Crawling Summary", "level": "INFO"},
            4401: {"code": "No Ready Cookie", "level": "Warning"},
            4402: {"code": "Missing Configuration", "level": "Warning"},
            4403: {"code": "Requested Resource Not Found", "level": "Warning"},
            4404: {"code": "Target Restricted", "level": "Warning"},
            4501: {"code": None, "level": "Error"},
            4502: {"code": "Credentials Expired", "level": "Error"},
            4503: {"code": "Failed to Store Data in Object Storage", "level": "Error"},
            4504: {"code": "Account Blocked", "level": "Error"},
            4601: {"code": "Database Connection Refused", "level": "Critical"},
            4602: {"code": "No Route to Database Host", "level": "Critical"},
            4603: {"code": "API Request Failed", "level": "Critical"},
            4604: {"code": "Connection to Queue Failed", "level": "Critical"},
            4605: {"code": "Queue Operation Failed", "level": "Critical"},
        }

    def generate_log(self, status: int, message: str, task: str, data: dict, start_time: float):
        self.log_status_value.value = status
        log = self._logic_list.get(status, {"code": None, "level": None})
        
        duration = round((time.time() - start_time) * 1000)
        time_utc_now = datetime.datetime.now(pytz.utc)
        time_local_id = time_utc_now.astimezone(pytz.timezone('Asia/Jakarta'))
        
        hasil = {
            "target": "GRAFANA",
            "timestamp": {
                "utc": str(time_utc_now),
                "local_time": str(time_local_id)
            },
            "service": self.service_name,
            "version": "search",
            "level": log["level"],
            "task": task,
            "status": status,
            "code": log["code"],
            "message": message,
            "duration_ms": duration,
            "data": data
        }
        
        log_file_path = os.path.join(self.log_dir, f"{self.vm_name}.log")
        with open(log_file_path, "a") as f:
            f.write(json.dumps(hasil) + "\n")
