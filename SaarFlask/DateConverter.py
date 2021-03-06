from werkzeug.routing import BaseConverter
from datetime import datetime

class DateConverter(BaseConverter):

    def to_python(self, value):
        params = [int(x) for x in value.split('-')]
        return datetime(params[0],params[1],params[2])

    def to_url(self, value):
        return BaseConverter.to_url(str(value))