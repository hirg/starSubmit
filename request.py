import xml.etree.ElementTree as et
from job import Job

class Request(object):
    """An object that represents a single scheduler request"""

    def __init__(self, jobs = []):
        """Initialize some defaults"""
        self.jobs = []
        if isinstance(jobs, Job):
            self.jobs.append( jobs )
        elif isinstance(jobs, list):
            for job in jobs:
                if isinstance(job, Job):
                    self.jobs.append(job)
