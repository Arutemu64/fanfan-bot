from datetime import timedelta

from faststream.nats import JStream

stream = JStream(name="stream", max_age=timedelta(hours=2).seconds)
