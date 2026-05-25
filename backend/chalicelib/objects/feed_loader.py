from abc import ABC, abstractmethod
from chalicelib.db import get_db
from chalicelib.models import FeedLoaderLog
 
class FeedLoader(ABC):
    jobid: str
    datasource_id: str
    parameters: dict
    current_step: str

    def __init__(self, jobid, datasource_id, parameters=None):
        self.jobid = jobid
        self.datasource_id = datasource_id
        self.parameters = parameters or {}
        self.current_step = "Initialized"

    @abstractmethod
    def extract(self):
        """Fetch raw data from a public API."""
        pass

    @abstractmethod
    def bronze_load(self, raw_data):
        """Load raw data into bronze tables exactly as it comes from the API."""
        pass

    @abstractmethod
    def silver_transform(self):
        """Transform raw data from bronze tables into silver format."""
        pass

    def log(self, message):
        print(f"[Job {self.jobid}] {message}")
        with get_db() as db:
            log_entry = FeedLoaderLog(
                jobid=self.jobid,
                datasource_id=self.datasource_id,
                feed_name=getattr(self, 'feed_name', self.__class__.__name__),
                action=message
            )
            db.add(log_entry)
            db.commit()
