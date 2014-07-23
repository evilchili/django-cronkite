class JobIsLocked(Exception):
    """
    Thrown when run() is called on a job instance that is locked.
    """
    pass
