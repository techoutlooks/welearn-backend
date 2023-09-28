from __future__ import absolute_import, unicode_literals

import os
from datetime import timedelta

from celery import Celery

# set the default Django settings module for the 'celery' program.
# https://stackoverflow.com/questions/4763072/why-cant-it-find-my-celery-config-file/40831283
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'welearn.settings')


app = Celery('welearn',
             broker='amqp://',
             backend='amqp://',
             include=['books.tasks']
             )

# Optional configuration, see the application user guide.
app.conf.update(
    beat_schedule={
        'revoke-expired-loans': {
            'task': 'books.tasks.revoke_expired_loans_task',
            'schedule': timedelta(minutes=1),
        },
        'collect-vouchers': {
            'task': 'tess_pay.tasks.collect_vouchers_task'
        }
    }
)
