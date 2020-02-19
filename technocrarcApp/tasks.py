from __future__ import absolute_import, unicode_literals

from spleeter.separator import Separator
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.urls import reverse
import os
import multiprocessing as mp
from celery.decorators import task
import json



channel_layer = get_channel_layer()

@task(name='split_sound')
def split_sound(channel_name, file_name, stems):
    mp.current_process()._config['daemon'] = False

    separator = Separator(settings.STEMS_OPTION[stems])

    separator.separate_to_file(os.path.join(settings.MEDIA_ROOT, file_name), settings.MEDIA_ROOT)

    path = os.path.join(settings.MEDIA_ROOT, os.path.splitext(file_name)[0])

    for file in os.listdir(path):
        file_url = reverse(
            'technocrarcApp:download',
            kwargs={'dir': os.path.splitext(file_name)[0], 'audio_file': file}
        )
        async_to_sync(channel_layer.send)(channel_name, {'type': 'file.processed', 'file_url': file_url})