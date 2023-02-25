__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List, Pattern, Callable

from lexnlp.extract.common.annotations.duration_annotation import DurationAnnotation


class DurationParser:

    DURATION_MAP = {}

    DURATION_PTN_RE = None  # type:Pattern

    INNER_CONJUNCTIONS = []

    INNER_PUNCTUATION = None  # type:Pattern

    GET_AMOUNTS = None  # type:Callable

    LOCALE = 'en'

    @classmethod
    def get_annotations(
        cls,
        text: str,
        float_digits: int = 4,
    ) -> List[DurationAnnotation]:
        all_ants = cls.get_all_annotations(text, float_digits)
        if len(all_ants) < 2:
            return all_ants

        # group annotations
        # like 5 years, 6 months
        # grouped durations are:
        # - bigger timeframe to less timeframe
        # - are separated by punctuation, spaces and conjunctions only
        ant_group: List[DurationAnnotation] = [all_ants[0]]
        all_grouped: List[List[DurationAnnotation]] = [ant_group]

        for a in all_ants[1:]:
            if cls.check_ant_continues_group(ant_group, a, text):
                ant_group.append(a)
            else:
                ant_group = [a]
                all_grouped.append(ant_group)

        # sum group annotations
        annotations: List = []
        for grp in all_grouped:
            if len(grp) == 1:
                annotations.append(grp[0])
            else:
                summed = cls.sum_annotations(grp)
                annotations.append(summed)
        return annotations

    @classmethod
    def sum_annotations(
        cls,
        ant_group: List[DurationAnnotation],
    ) -> DurationAnnotation:
        coords = (ant_group[0].coords[0], ant_group[-1].coords[1])
        rst: DurationAnnotation = DurationAnnotation(
            coords,
            locale=ant_group[0].locale,
            is_complex=True
        )
        rst.duration_days = sum([d.duration_days for d in ant_group])
        rst.amount = rst.duration_days
        rst.duration_type = ant_group[-1].duration_type
        rst.duration_type_en = ant_group[-1].duration_type_en
        for ant in ant_group:
            if rst.value_dict is None:
                rst.value_dict = {ant.duration_type: float(ant.amount)}
            elif ant.duration_type in rst.value_dict:
                rst.value_dict[ant.duration_type] += float(ant.amount)
            else:
                rst.value_dict[ant.duration_type] = float(ant.amount)
        return rst

    @classmethod
    def check_ant_continues_group(
        cls,
        ant_group: List[DurationAnnotation],
        ant: DurationAnnotation,
        text: str,
    ) -> bool:
        # the following dur should have shorter timeframe than the preceding one
        a: DurationAnnotation = ant_group[-1]
        b: DurationAnnotation = ant
        adr = cls.DURATION_MAP.get(a.duration_type_en or a.duration_type) or 1
        bdr = cls.DURATION_MAP.get(b.duration_type_en or b.duration_type) or 1
        if bdr >= adr:
            return False

        # the captures should be separated by: spaces, punctuation and
        # conjunctions ("and" in any case)
        intext: str = text[a.coords[1]:b.coords[0]].lower()
        for conj in cls.INNER_CONJUNCTIONS:
            intext: str = intext.replace(conj, '')
        intext: str = cls.INNER_PUNCTUATION.sub('', intext)
        return not intext

    @classmethod
    def get_all_annotations(
        cls,
        text: str,
        float_digits: int = 4,
    ) -> List[DurationAnnotation]:
        raise NotImplementedError()
