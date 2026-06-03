from chalicelib.db import SessionLocal
from chalicelib.models.common.job_log_details import JobLogDetails
from chalicelib.models.common.event_log_details import EventLogDetails
import datetime

class JobDetailLogger:
    def __init__(self, job_id, data_source_id, event_name):
        self.job_id = job_id
        self.data_source_id = data_source_id
        self.event_name = event_name
        self.status_map = {}  # Map status string to row primary key

    def create_log_entry(self, status):
        """Creates a new row in job_log_details."""
        with SessionLocal() as db:
            log = JobLogDetails(
                job_id=self.job_id,
                data_source_id=self.data_source_id,
                event_name=self.event_name,
                status=status,
                job_start_time=datetime.datetime.now()
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            self.status_map[status] = log.id
            return log.id

    def update_log_entry(self, status, success=True):
        """Updates an existing row in job_log_details."""
        # If not successful, modify the status string
        final_status = status if success else f"{status} - Failed"
        
        # Get the ID for the base status we were tracking
        log_id = self.status_map.get(status)
        if not log_id:
            raise ValueError(f"No log entry found for status: {status}")

        with SessionLocal() as db:
            log = db.query(JobLogDetails).filter(JobLogDetails.id == log_id).first()
            if log:
                log.status = final_status
                log.job_end_time = datetime.datetime.now()
                db.commit()

class EventDetailLogger:
    def __init__(self, action, job_id):
        self.action = action
        self.job_id = job_id

    def create_log_entry(self):
        """Creates a new row in event_log_details."""
        with SessionLocal() as db:
            log = EventLogDetails(
                job_id=self.job_id,
                action=self.action,
                start_time=datetime.datetime.now()
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            return log.id
