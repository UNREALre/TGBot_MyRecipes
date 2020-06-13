#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib.request
import json
import os
import time
from pydub import AudioSegment


class VoiceFile:

    """Класс обрабатывающий голосовые сообщения боту"""

    tg_key: str
    voice_files_folder: str

    def __init__(self, file_id, file_unique_id, duration, mime_type, file_size, tg_key, voice_folder):
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.duration = duration
        self.mime_type = mime_type  # audio/ogg
        self.file_size = file_size

        self.tg_key = tg_key
        self.voice_files_folder = voice_folder

        self._file_url = ''
        self._file_name_ogg = ''
        self._file_name_wav = ''
        self._file_path_ogg = ''
        self._file_path_wav = ''

    def get_file(self):
        self.download_file()
        self.convert_file()

        return self._file_path_wav

    def download_file(self):
        """Скачивает файл, присланный от пользователя по спец URL-ам телеграма"""
        voice_info_url = "https://api.telegram.org/bot{}/getFile?file_id={}".format(self.tg_key, self.file_id)
        with urllib.request.urlopen(voice_info_url) as url:
            voice_file = json.loads(url.read().decode())
            if voice_file['ok']:
                self._file_url = "https://api.telegram.org/file/bot{}/{}"\
                    .format(self.tg_key, voice_file['result']['file_path'])
                self._file_name_ogg = voice_file['result']['file_path'][voice_file['result']['file_path'].rfind('/') + 1:]
                self._file_name_wav = '{}.wav'.format(self.file_id)

                self._file_path_ogg = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "../", self.voice_files_folder,
                                                   self._file_name_ogg)
                self._file_path_wav = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "../", self.voice_files_folder,
                                                   self._file_name_wav)

    def convert_file(self):
        """Конвертирует OGG файл в WAV файл для последующего скармливания scify"""
        with open(self._file_path_ogg, 'wb') as output:
            output.write(urllib.request.urlopen(self._file_url).read())
            ogg_file = AudioSegment.from_ogg(self._file_path_ogg)  # файлы <=1 сек тут не падают
            ogg_file.export(self._file_path_wav, format="wav")

        os.remove(self._file_path_ogg)
