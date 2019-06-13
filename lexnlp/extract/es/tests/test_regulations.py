from unittest import TestCase
from lexnlp.extract.es.regulations import parser, get_regulations
from lexnlp.tests.test_utils import load_resource_document, annotate_text, save_test_document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestParseSpanishLawsRegulations(TestCase):
    def test_parse_comision(self):
        text = "Las instituciones de banca múltiple que se ubiquen en lo dispuesto en esta fracción, deberán " + \
               "entregar a la Comisión Nacional Bancaria y de Valores, la información y documentación que acredite " + \
               "satisfacer lo antes señalado, dentro de los quince días hábiles siguientes a que se encuentren en dicho supuesto."

        ret = parser.parse(text)
        self.assertEqual(2, len(ret))
        reg = ret[1]
        self.assertEqual('Spain', reg.country)
        self.assertEqual('Comisión Nacional Bancaria y de Valores', reg.name)

        text = "Tampoco se considerarán operaciones de banca y crédito la captación de recursos del público " + \
               "mediante la emisión de instrumentos inscritos en el Registro Nacional de Valores, colocados " + \
               "mediante oferta pública incluso cuando dichos recursos se utilicen para el otorgamiento de " + \
               "financiamientos de cualquier naturaleza."
        ret = parser.parse(text)
        self.assertEqual(1, len(ret))
        reg = ret[0]
        self.assertEqual('Registro Nacional de Valores', reg.name)

    def test_parse_ley_del(self):
        text = "Para efectos de lo previsto en la presente Ley, por inversionistas institucionales se entenderá a las " +\
               "instituciones de seguros y de fianzas, únicamente cuando inviertan sus reservas técnicas; a las " +\
               "sociedades de inversión comunes y a las especializadas de fondos para el retiro; a los fondos de " +\
               "pensiones o jubilaciones de personal, complementarios a los que establece la Ley del Seguro Social " +\
               "y de primas de antigüedad, que cumplan con los requisitos señalados en la Ley del Impuesto sobre " +\
               "la Renta, así como a los demás inversionistas institucionales que autorice expresamente la " +\
               "Secretaría de Hacienda y Crédito Público."
        ret = parser.parse(text)
        self.assertEqual(4, len(ret))

        reg_items = list(get_regulations(text))
        name = reg_items[0]["tags"]["External Reference Text"]
        self.assertEqual("instituciones de seguros y de fianzas", name)

    def test_parse_large_text(self):
        text = load_resource_document('lexnlp/extract/es/sample_es_regulations.txt', 'utf-8')
        ret = parser.parse(text)
        self.assertGreater(len(ret), 100)
        html = annotate_text(text, ret)
        save_test_document('sample_es_regulations.html', html)
