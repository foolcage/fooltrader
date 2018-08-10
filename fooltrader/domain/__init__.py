import logging
from datetime import datetime

from elasticsearch_dsl import DocType

from fooltrader.settings import TIME_FORMAT_MICRO
from fooltrader.utils.utils import to_time_str

logger = logging.getLogger(__name__)


class BaseDocType(DocType):
    def exist(self, index):
        if self.get(id=self['id'], index=index, ignore=404):
            return True
        else:
            return False

    def save(self, using=None, index=None, validate=True, force=True, **kwargs):
        # assign now if no timestamp given
        if not self.timestamp:
            self.timestamp = to_time_str(datetime.now(), time_fmt=TIME_FORMAT_MICRO)

        if force or not self.exist(index=index):
            return super().save(using, index, validate, **kwargs)
        else:
            logger.debug("doc{} exists".format(self['id']))
