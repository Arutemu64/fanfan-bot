from faststream.nats import JStream
from nats.js.api import RetentionPolicy

stream = JStream(name="stream", retention=RetentionPolicy.WORK_QUEUE)
