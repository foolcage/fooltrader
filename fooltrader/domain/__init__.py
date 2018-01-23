import logging

from elasticsearch_dsl import DocType

logger = logging.getLogger(__name__)


class BaseDocType(DocType):
    def exist(self, index):
        if self.get(id=self['id'], index=index, ignore=404):
            return True
        else:
            return False

    def save(self, using=None, index=None, validate=True, force=True, **kwargs):
        if force or not self.exist(index=index):
            return super().save(using, index, validate, **kwargs)
        else:
            logger.debug("doc{} exists".format(self['id']))
