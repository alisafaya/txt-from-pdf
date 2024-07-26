# -*- coding: utf-8 -*-
import re
import unicodedata


"""
from: https://github.com/mattbierbaum/arxiv-public-datasets/blob/f0b8a4fd17e7aeed38465ec00a63eb219fe1672e/arxiv_public_data/fixunicode.py#L92

List of ligatures: https://en.wikipedia.org/wiki/Typographic_ligature

Additional notes:
* Some classes of characters were listed in the original utf8 fixes but I'm not
  sure they don't belong elsewhere (end user processing). In these cases, pass
  through unidecode should normalize them to proper ascii. They are listed here
  with reasoning:

  - Ditch combining diacritics http://unicode.org/charts/PDF/U0300.pdf
    r'[\u0300-\u036F]': ''

  - Ditch chars that sometimes (incorrectly?) appear as combining diacritics
    r'(?:\xa8|[\u02C0-\u02DF])': ''
"""

ligature_table = """
AA, aa	Ꜳ, ꜳ	U+A732, U+A733	&#xA732; &#xA733;
AE, ae	Æ, æ	U+00C6, U+00E6	&AElig; &aelig;
AO, ao	Ꜵ, ꜵ	U+A734, U+A735	&#xA734; &#xA735;
AU, au	Ꜷ, ꜷ	U+A736, U+A737	&#xA736; &#xA737;
AV, av	Ꜹ, ꜹ	U+A738, U+A739	&#xA738; &#xA739;
AV, av 	Ꜻ, ꜻ	U+A73A, U+A73B	&#xA73A; &#xA73B;
AY, ay	Ꜽ, ꜽ	U+A73C, U+A73D	&#xA73C; &#xA73D;
ff	ﬀ	U+FB00	&#xFB00;
ffi	ﬃ	U+FB03	&#xFB03;
ffl	ﬄ	U+FB04	&#xFB04;
fi	ﬁ	U+FB01	&#xFB01;
fl	ﬂ	U+FB02	&#xFB02;
OE, oe	Œ, œ	U+0152, U+0153	&OElig; &oelig;
OO, oo	Ꝏ, ꝏ	U+A74E, U+A74F	&#xA74E; &#xA74F;
st	ﬆ	U+FB06	&#xFB06;
ſt	ﬅ	U+FB05	&#xFB05;
TZ, tz	Ꜩ, ꜩ	U+A728, U+A729	&#xA728; &#xA729;
ue	ᵫ	U+1D6B	&#x1D6B;
VY, vy	Ꝡ, ꝡ	U+A760, U+A761	&#xA760; &#xA761;
db	ȸ	U+0238	&#x238;
dz	ʣ	U+02A3	&#x2A3;
dʑ 	ʥ	U+02A5	&#x2A5;
dʒ 	ʤ	U+02A4	&#x2A4;
fŋ 	ʩ	U+02A9	&#x2A9;
IJ, ij	Ĳ, ĳ	U+0132, U+0133	&#x132; &#x133;
ls	ʪ	U+02AA	&#x2AA;
lz	ʫ	U+02AB	&#x2AB;
lʒ 	ɮ	U+026E	&#x26E;
qp	ȹ	U+0239	&#x239;
tɕ 	ʨ	U+02A8	&#x2A8;
ts	ʦ	U+02A6	&#x2A6;
tʃ 	ʧ	U+02A7	&#x2A7;
ui	ꭐ	U+AB50	&#xAB50;
ui	ꭑ	U+AB51	&#xAB50;
"""

unicode_mapping = {}

for row in ligature_table.split("\n"):
    if row.count("\t") <= 1:
        continue

    unicode_mapping.update(
        {
            u.strip(): unicodedata.normalize("NFKC", a.strip())
            for a, u in zip(*[c.split(",") for c in row.split("\t")[:2]])
        }
    )

unicode_mapping.update(
    {
        # 'ẞ, ß': careful, some use this for \beta
        r"(\B)\u00DF": r"\1ss",
        # Additions (manual normalization that we feel is important)
        # unicode space  u'\xa0'  (not \x{0c} = ^L keep!)
        "\xa0": " ",
        # single + double quotes, dash, and asterisk
        r"[\u2018\u2019]": r"'",
        r"[\u201C\u201D]": r'"',
        r"[\xad\u2014]": r"-",
        r"\xb7": r"*",
        r"\u00A1": r"i",  # inverted exclamation mark to i
    }
)


def fix_unicode(txt: str) -> str:
    """
    Given UTF-8 encoded text, remove typographical ligatures (normalize to true
    non-display character set) and do a general normalization of the unicode
    so that possible redundant characters and simplified to a single set.

    Parameters
    ----------
    txt : unicode string

    Returns
    -------
    output : unicode string
    """
    for search, replace in unicode_mapping.items():
        txt = re.subn(search, replace, txt)[0]
    return unicodedata.normalize("NFKC", txt)
