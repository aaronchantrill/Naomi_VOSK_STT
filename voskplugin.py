# -*- coding: utf-8 -*-
import json
import logging
import os.path
from collections import OrderedDict
from naomi import app_utils
from naomi import paths
from naomi import plugin
from naomi import profile
from naomi.run_command import run_command
from naomi.run_command import process_completedprocess
from vosk import Model, KaldiRecognizer
from . import voskvocab


def get_languagemodel_path(path):
    """
    Returns:
        The path of the the pocketsphinx languagemodel file as string
    """
    return os.path.join(path, 'languagemodel')


# This is only required because file.writelines() does not automatically add
# newlines to the lines passed in
def line_generator(items):
    for item in items:
        yield item
        yield "\n"


class VoskSTTPlugin(plugin.STTPlugin):
    """
    The default Speech-to-Text implementation which relies on PocketSphinx.
    """
    _logfile = None

    def __init__(self, *args, **kwargs):
        """
        Initiates Vosk

        Arguments:
        """
        self.logger = logging.getLogger(__name__)

        plugin.STTPlugin.__init__(self, *args, **kwargs)
        self.compile_vocabulary(
            voskvocab.compile_vocabulary
        )
        vosk_model = profile.get(
            ['VOSK STT', 'model'],
            self.get_default_model()
        )
        model = Model(
            vosk_model,
            lang=profile.get(['language'], 'en-US').lower()
        )
        self.rec = KaldiRecognizer(model, 16000)

    @staticmethod
    def get_default_model():
        """
        Returns the default model based on language
        """
        language = profile.get(['language'], 'en-US')
        default_model = 'vosk-model-en-us-0.22'
        if language == "fr-FR":
            default_model = 'vosk-model-fr-0.22'
        elif language == "de-DE":
            default_model = 'vosk-model-de-0.21'
        return default_model

    def settings(self):
        vosk_model = profile.get(
            ['VOSK STT', 'model'],
            os.path.join(
                paths.sub('vosk'),
                self.get_default_model()
            )
        )
        default_model = os.path.basename(vosk_model)
        if not os.path.isdir(os.path.dirname(vosk_model)):
            os.makedirs(os.path.dirname(vosk_model), exist_ok=True)
        if not os.path.isdir(vosk_model):
            # since the model does not exist, download the default to the
            # standard path and unzip it
            source = f"https://alphacephei.com/vosk/models/{default_model}.zip"
            dest = f"{vosk_model}.zip"
            app_utils.download_file(
                source,
                dest
            )
            cmd = [
                'unzip',
                dest,
                '-d', os.path.dirname(vosk_model)
            ]
            completedprocess = run_command(cmd)
            if completedprocess.returncode == 0:
                self.logger.info(process_completedprocess(completedprocess))
            else:
                self.logger.error(process_completedprocess(completedprocess))
        return OrderedDict(
            [
                (
                    ('VOSK STT', 'model'), {
                        'title': self.gettext('VOSK model file'),
                        'description': "".join([
                            self.gettext('This is the VOSK model, downloaded from https://alphacephei.com/vosk/models')
                        ]),
                        'default': vosk_model
                    }
                ),
            ]
        )

    def transcribe(self, fp):
        """
        Performs STT, transcribing an audio file and returning the result.

        Arguments:
            fp -- a file object containing audio data
        """
        fp.seek(44)
        data = fp.read()

        if len(data) == 0:
            return []
        self.rec.AcceptWaveform(data)
        res = json.loads(self.rec.Result())
        result = res['text']
        transcribed = [result] if result != '' else []
        return transcribed
