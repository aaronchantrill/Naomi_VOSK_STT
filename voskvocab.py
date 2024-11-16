# -*- coding: utf-8 -*-
import os
import logging
from naomi.coloredformatting import naomidefaults
from naomi import i18n
from naomi import paths
from naomi import profile
from naomi import visualizations


_ = i18n.GettextMixin(i18n.parse_translations(paths.data('locale'))).gettext


def delete_temp_file(file_to_delete):
    if True:
        os.remove(file_to_delete)


def get_corpus_path(path):
    """
    Returns:
        The path of the the pocketsphinx languagemodel file as string
    """
    return os.path.join(path, 'extra.txt')


def get_dictionary_path(path):
    """
    Returns:
        The path of the pocketsphinx dictionary file as string
    """
    return os.path.join(path, 'extra.dic')


def get_verify_keyword():
    return profile.get_arg(
        "verify_keyword",
        profile.get_arg(
            "verify_wakeword",
            profile.get_profile_flag(
                ['passive_stt', 'verify_wakeword'],
                False
            )
        )
    )


def get_keywords():
    keywords = profile.get_arg(
        'keywords',
        profile.get(
            ['keyword'],
            ['Naomi']
        )
    ).copy()
    if isinstance(keywords, str):
        keywords = [keywords]
    return keywords


def compile_vocabulary(directory, phrases):
    """
    Right now, this just writes the phrases to an extra.txt file, then checks
    for any words that are missing from $VOSK_MODEL/graph/words.txt. It
    creates an extra.txt file that can then be used with the compiler to
    generate a new HCLG.fst file. If any words are missing from the current
    vocabulary, the revision file is removed.

    Arguments:
        phrases -- a list of phrases that this vocabulary will contain
    """
    logger = logging.getLogger(__name__)
    corpus_path = get_corpus_path(directory)

    vosk_model = profile.get(
        ['VOSK STT', 'model']
    )
    word_list = os.path.join(vosk_model, 'graph', 'words.txt')

    logger.debug('corpus path: %s' % corpus_path)
    logger.debug('Compiling corpus...')
    vocabulary = compile_languagemodel(phrases, corpus_path)
    logger.debug('Starting dictionary...')
    # check vocabulary to make sure all words appear in the VOSK words.txt
    missing = set()
    with open(word_list, 'r') as f:
        for word in sorted(vocabulary):
            line = f.readline().split()[0].lower()
            while line < word:
                line = f.readline().split()[0].lower()
            if line != word:
                missing.add(word)
    if len(missing):
        # Remove the revision file
        warn(
            _(
                "The VOSK dictionary is missing the following words: {}"
            ).format(missing)
        )
        warn(
            _("You can use the {} file to generate a custom language model using the directions at https://alphacephei.com/vosk/lm").format(corpus_path)
        )
        # Is this plugin being used as the default stt engine?
        if os.path.basename(directory) == "default":
            # Check if "verify_keyword" is enabled
            verify_keyword = get_verify_keyword()
            if profile.get_arg("verify_keyword", False):
                # Check if any of the missing words are used as or in wakewords
                keywords = get_keywords()
                removekeywords = set()
                for keyword in keywords:
                    for word in missing:
                        if word in keyword.lower():
                            warn(
                                _("Because the missing word {} is used in the keyword {}, either {} cannot be used as a keyword or verify_keyword needs to be disabled since the active stt engine would never recognize it.").format(word, keyword, keyword)
                            )
                            warn(
                                _("Removing {} from keywords.").format(keyword)
                            )
                            removekeywords.add(keyword)
                if len(removekeywords):
                    # Remove the revision file
                    os.remove(os.path.join(directory, 'revision'))
                    for keyword in removekeywords:
                        keywords.remove(keyword)
                    if len(keywords) == 0:
                        warn(
                            _("Removing the keywords left no keywords. Restoring keywords and switching off the verify_keyword option")
                        )
                        profile.set_arg("keywords", get_keywords())
                        profile.set_arg("verify_keyword", False)
                    else:
                        warn(
                            _("You may use the keywords {}").format(keywords)
                        )
                        profile.set_arg("keywords", keywords)


def compile_languagemodel(phrases, output_file):
    """
    Creates a corpus file (extra.txt) which can be used to train a new model
    using the Vosk _compile.zip model for the language.

    Arguments:
        text -- the text the languagemodel will be generated from
        output_file -- the path of the file this languagemodel will
                       be written to

    Returns:
        A list of all unique words this vocabulary contains.
    """
    if len(" ".join(phrases).strip()) == 0:
        raise ValueError('No text to compile into languagemodel!')

    logger = logging.getLogger(__name__)

    # Get words from vocab file
    logger.debug("Creating languagemodel file: '%s'" % output_file)
    words = set()
    with open(output_file, 'w') as f:
        for phrase in phrases:
            f.write(f"{phrase.lower()}\n")
            for word in phrase.split():
                if not word.startswith('#') and word not in ('<s>', '</s>'):
                    words.add(word.lower())
    if len(words) == 0:
        logger.warning('Vocab file seems to be empty!')

    return words


def warn(message, logger=None):
    if not logger:
        logger = logging.getLogger(__name__)
    logger.warn(message)
    visualizations.run_visualization(
        "output",
        f"{naomidefaults.B_R}{message}{naomidefaults.sto}",
        timestamp=False
    )
