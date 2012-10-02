# coding=utf-8
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import simplejson


class Command(BaseCommand):

    def execute(self, *args, **kwargs):
        # Etherpad-lite's default configuration
        conf = {
            "ip": "0.0.0.0",
            "port": 9001,
            'databaseAlias': 'default',
            "defaultPadText": "",
            "requireSession": False,
            "editOnly": False,
            "minify": True,
            "maxAge": 6 * 60 * 60 * 1000,
            "abiword": None,
            "loglevel": "INFO"
        }

        conf.update(getattr(settings, 'ETHERPAD_CONFIGURATION', {}))

        # TODO: "Classic" database definition, i.e. DATABASE_ENGINE etc.
        # Dict-style database definition
        if 'databaseAlias' in conf and not 'dbType' in conf:
            if conf['databaseAlias'] in settings.DATABASES:
                dbconf = settings.DATABASES[conf['databaseAlias']]
                conf['dbSettings'] = {}
                engine = dbconf['ENGINE']

                if engine == 'django.db.backends.sqlite3':
                    conf['dbType'] = 'sqlite'
                    conf['dbSettings']['filename'] = dbconf['NAME']

                if engine == 'django.db.backends.mysql':
                    conf['dbType'] = 'mysql'
                    conf['dbSettings']['database'] = dbconf['NAME']
                    conf['dbSettings']['user'] = dbconf['USER']
                    conf['dbSettings']['password'] = dbconf['PASSWORD']
                    conf['dbSettings']['host'] = dbconf['HOST']

                if engine == 'django.contrib.gis.db.backends.postgis' or \
                        engine == 'django.db.backends.postgresql_psycopg2':
                    conf['dbType'] = 'postgres'
                    conf['dbSettings']['database'] = dbconf['NAME']
                    conf['dbSettings']['user'] = dbconf['USER']
                    conf['dbSettings']['password'] = dbconf['PASSWORD']
                    conf['dbSettings']['host'] = dbconf['HOST']
            del conf['databaseAlias']
        print simplejson.dumps(conf, indent=4 * ' ')
