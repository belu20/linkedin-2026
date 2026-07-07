import urllib.parse
import random

class TargetManager:
    def __init__(self, client_id: int):
        self.client_id = client_id

    def get_targets(self, keywords: list) -> list:
        datastore = []
        count_target = 0
        list_target = list(keywords)
        random.shuffle(list_target)

        for query in list_target:
            count_target += 1
            keyword = urllib.parse.quote(query)
            scroll = False

            print(f"[DEBUG] [{count_target}] Query search: {urllib.parse.unquote(keyword)}")
            
            datastore.append({
                "keyword": keyword,
                "scroll": scroll,
                "client_id": str(self.client_id)
            })
        random.shuffle(datastore)
        return datastore
