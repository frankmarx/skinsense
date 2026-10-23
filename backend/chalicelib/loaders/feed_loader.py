from abc import ABC, abstractmethod

class FeedLoader(ABC):
    def __init__(self, datasource_id: str):
        self.datasource_id = datasource_id

    @abstractmethod
    def extract(self):
        pass

    @abstractmethod
    def bronze_load(self, raw_data, job_id: str):
        pass

    @abstractmethod
    def silver_transform(self, raw_data, job_id: str):
        pass

    def log(self, message):
        # We can route this to the logger if needed, or app log
        print(message)
