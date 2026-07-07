import os
import datetime
import json

class DataPublisher:
    def __init__(self, local_output_dir: str = "crawling_result"):
        self.local_output_dir = local_output_dir
        os.makedirs(self.local_output_dir, exist_ok=True)

    def produce_message(self, key: str, value: dict) -> bool:
        try:
            file_name = os.path.join(
                self.local_output_dir,
                datetime.datetime.now().strftime("%Y-%m-%d") + ".jsonl"
            )
            with open(file_name, "a", encoding="utf-8") as f:
                f.write(json.dumps(value, default=str, ensure_ascii=False) + "\n")
            print(f"[INFO] Crawling result saved locally -> {file_name} (key={key})")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to write local crawling result: {e}")
            raise e
