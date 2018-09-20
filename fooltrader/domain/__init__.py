import logging
from datetime import datetime

from elasticsearch_dsl import Document

from fooltrader.utils.time_utils import to_time_str, TIME_FORMAT_ISO8601

logger = logging.getLogger(__name__)


class BaseDocument(Document):
    def exist(self, index):
        if self.get(id=self['id'], index=index, ignore=404):
            return True
        else:
            return False

    def save(self, using=None, index=None, validate=True, force=True, **kwargs):
        # assign now if no timestamp given
        if not self.timestamp:
            self.timestamp = to_time_str(datetime.now(), time_fmt=TIME_FORMAT_ISO8601)
        if self.id:
            self.meta['id'] = self.id

        if force or not self.exist(index=index):
            return super().save(using, index, validate, **kwargs)
        else:
            logger.debug("doc{} exists".format(self['id']))
