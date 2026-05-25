from abc import ABC, abstractmethod

class FeedLoader(ABC):
    def __init__(self, parameters=None, jobid=None):
        self.parameters = parameters or {}
        self.jobid = jobid

    @abstractmethod
    def bronze_load(self):
        """Fetch raw data and return it."""
        pass

    @abstractmethod
    def silver_transform(self, raw_data):
        """Transform raw data into silver format."""
        pass

    def log(self, message):
        print(f"[Job {self.jobid}] {message}")
