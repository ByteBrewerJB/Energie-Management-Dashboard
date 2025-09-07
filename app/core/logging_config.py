import logging
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            log_record['timestamp'] = record.created
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

def setup_logging():
    logger = logging.getLogger("joulejournal")
    logger.setLevel(logging.INFO)
    logHandler = logging.StreamHandler()
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers = [logHandler]
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers = [logHandler]
