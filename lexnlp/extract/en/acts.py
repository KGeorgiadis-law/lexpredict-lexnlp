import regex as re

from lexnlp.extract.en.utils import NPExtractor


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


act_grammar = r"""
    NBAR:
        {<NN.*|JJ.*|VBN|VBG|CD|\(|\)|,>*<NNP.*>}  # Nouns, Adj-s, brackets, terminated with Nouns
    IN:
        {<CC|IN|,>}   # &, and, of
    SECTION:
        {<JJ|NN><CD><IN><DT>}
    NP:
        {(<SECTION>)?(<NBAR><IN>+)*<NBAR>(<IN><CD>)?}
"""

ACT_NPE = NPExtractor(act_grammar)
ACT_NPE.exception_sym += ['And', 'Of']
ACT_NPE.exception_pos = ['CC']
ACT_RE = re.compile(r'.+?\s+Act(?:\W|$)(?:of\s+\d{4})?')
ACT_PARTS_RE = re.compile(r'(?P<text>(?:section (?P<section>[^\s]+)\s+of\s+the\s+)?(?P<act_name>(?:(?:[A-Z]\w+|[A-Z&]+|and|\d+(?:[a-z]{1,3})?),?\s*)+(?<=\s)Act)(?:\W|$)(?:of (?P<year>\d{4}))?)')


def get_acts(text):
    # may contain multiple Act like "Doe and Jones Act (D&J Act)"
    act_name_containers = [i for i in set(ACT_NPE.get_np(text)) if ACT_RE.search(i)]

    for act_name_container in act_name_containers:
        for act_name in ACT_RE.findall(act_name_container):
            act_name_re = re.compile(re.escape(act_name))
            captures = ACT_PARTS_RE.search(act_name).capturesdict()
            for match in act_name_re.finditer(text):
                location_start, location_end = match.span()
                yield {'location_start': location_start,
                       'location_end': location_end,
                       'act_name': ''.join(captures.get('act_name') or []),
                       'section': ''.join(captures.get('section') or []),
                       'year': ''.join(captures.get('year') or []),
                       'value': ''.join(captures.get('text') or [])}


def get_act_list(*args, **kwargs):
    return list(get_acts(*args, **kwargs))
