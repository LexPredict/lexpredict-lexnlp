__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import datetime
import os
import random

from num2words import num2words
from lexnlp.extract.all_locales.languages import Locale
from lexnlp.extract.common.dates import DateParser
from lexnlp.extract.common.dates_classifier_model import build_date_model
from lexnlp.extract.de.date_model import DATE_MODEL_CHARS, MONTH_NAMES, DE_ALPHA_CHAR_SET
from lexnlp.extract.de.dates import MODEL_DATE
from lexnlp.extract.de.de_date_parser import DeDateParser


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

TODAY = datetime.date.today()

WRITTEN_DATE_NUMS = ['ersten', 'zweiten', 'dritten', 'vierten', 'fünften', 'siebten', 'achten',
                     'neunten', 'zehnten', 'elften', 'zwölften', 'dreizehnten', 'vierzehnten',
                     'fünfzehnten', 'sechzehnten', 'siebzehnten', 'achtzehnten', 'neunzehnten']


def setup_date_parser(check_date_string: bool) -> DateParser:
    return DeDateParser(DATE_MODEL_CHARS,
                        enable_classifier_check=check_date_string,
                        locale=Locale('de-DE'),
                        dateparser_settings={'PREFER_DAY_OF_MONTH': 'first',
                                             'STRICT_PARSING': False,
                                             'DATE_ORDER': 'DMY'},
                        classifier_model=MODEL_DATE,
                        alphabet_character_set=DE_ALPHA_CHAR_SET,
                        count_words=True)


def train_default_model(save=True, verbose=False, check_date_strings=False):
    """
    Train default model.
    """
    examples = make_date_samples()

    for j in range(1, 25):
        examples.append((f'mit {j}', []))
        examples.append((f'Leasing mit {j}.500€ Anzahlung', []))

    for j in range(2, 19):
        examples.append((f'{j} Jahren', []))

    # Add random numeric date examples
    add_numeric_date_samples(examples)

    # Output
    output_path = 'test_date_model.pickle'
    if save:
        output_path = os.path.join(MODULE_PATH, 'date_model.pickle')

    parser = setup_date_parser(check_date_strings)
    build_date_model(examples,
                     output_path,
                     lambda date_str: [(d['value'].date(), (d['location_start'], d['location_end']))
                                       for d in parser.get_dates(date_str)],
                     characters=DATE_MODEL_CHARS,
                     alphabet_char_set=DE_ALPHA_CHAR_SET,
                     count_words=True,
                     verbose=verbose)
    if not save:
        os.unlink('test_date_model.pickle')


def make_date_samples():
    examples = [("""Spätestens am 01.06.2017""", [datetime.date(2017, 6, 1)]),
                ("""Datum: 1. Juni 2017""", [datetime.date(2017, 6, 1)]),
                ("""Wird bis Juni 2017 abgeschlossen sein""", [datetime.date(2017, 6, 1)]),
                ("""Wird bis Juni abgeschlossen sein""", [datetime.date(2017, 6, 1)]),
                ("""Wird bis zum 1. Juni 2017 abgeschlossen sein""", [datetime.date(2017, 6, 1)]),
                ("""Wird bis zum 1 Juni 2017 abgeschlossen sein""", [datetime.date(2017, 6, 1)]),
                ("""Wird bis zum 1 Juni, 2017 abgeschlossen sein""", [datetime.date(2017, 6, 1)]),
                ("""Wird bis zum ersten Juni 2017 abgeschlossen sein""", [datetime.date(2017, 6, 1)]),
                ("""Abschnitt über 6.25""", []),
                ("""Ausfertigungsdatum: 23.05.1975 Vollzitat:""", [datetime.date(1975, 5, 23)]),
                ('Commencement Date: 09/12/2022.', [datetime.date(2022, 12, 9)]),
                (
                    """Alle Arbeiten sind gemäß der WDD-Skizze vom 15. März 2005 und Hansen durchzuführen
                     Mechanische COR.""",
                    [datetime.date(2005, 3, 15)]),
                (
                    """Cost Plus Incentive-Bauvertrag mit JH Kelly LLC Am 8. August 2007 hat Hoku Materials,
                     Inc. hat mit JH Kelly LLC. Oder JH einen Bauvertrag, den Bauvertrag, geschlossen
                     Kelly, für Bauleistungen für den Bau einer Polysilicium-Produktionsanlage mit einem
                     Jahreskapazität von 2.000 Tonnen.""",
                    [datetime.date(2007, 8, 8)]),
                (
                    """INSGESAMT 35.842.000 PROJEKTANFORDERUNGEN 1.281.000 BAUKONTINGENZ 1.075.000 ANHÄNGER
                     UMZUGSZULAGE 50.000 ZEITPLANANPASSUNG 357.000 Hebezeug- / Aufzugsbetreiber 104.000 ALLGEMEINES
                     BEDINGUNGEN 1.481.000 GEBÜHR 1.306.000 G. C. ZAHLUNGS- UND LEISTUNGSBINDUNG 204.000 - -------------
                     ================================================== ================================================
                     GESAMTBAUKOSTEN 41.700.000 - -----------------
                     ================================================== ========== ==================
                     =================""",
                    []),
                ("""4-7-98 Datum Datum""", [datetime.date(1998, 4, 7)]),
                ("""4/7/98 Datum Datum""", [datetime.date(1998, 4, 7)]),
                (
                    """Diese monatliche Wartungs- und Supportvereinbarung hat eine anfängliche Laufzeit von sechs (6) 
                     Monaten. Die Vereinbarung verlängert sich dann automatisch um weitere zwölf (12) Monate
                     Preise und Bedingungen, sofern US / INTELICOM nicht schriftlich mitgeteilt wird, dass der 
                     Lizenznehmer beabsichtigt, zu kündigen Die Vereinbarung ist bis spätestens 1. September 1998
                     eingegangen. Es sei denn, der Lizenznehmer beschließt, diese zu stornieren
                     Vereinbarung am Ende der ersten sechs Monate wird die "anfängliche Laufzeit" der Vereinbarung sein
                     bis 30. September 1999.""",
                    [datetime.date(1998, 9, 1), datetime.date(1999, 9, 30)]),
                (
                    """KLASSIFIZIERUNG GERADE ZEIT & EINE HÄLFTE DOPPELTE ZEIT PIPEFITTERS LOCAL # 26 LV
                     ZONE 5,6,7""",
                    []),
                (
                    """Aktion NBBB-Meilensteintermine - Alle AFC-Daten erforderlich Eigentümer Allgemeine Vereinbarung 
                       Gefroren [*]
                    Jensen / Eigentümer Stahldesign Hauptdeck und darunter [*] Jensen / Eigentümer Allgemeine 
                       Anordnung [*]
                    Jensen / Eigentümer Tonnage Öffnungen [*] Jensen / Eigentümer Elektrische Einleitung [*] Eigentümer
                    Zeitplan für die Innenausstattung [*] Grundrisse des Eignerraums Kabinen [*] Raum für 
                       den Eignerservice des Eigentümers
                    Layouts [*] Grundrisse für den öffentlichen Raum des Eigentümers [*] Jensen / Eigentümer 
                       GW-Rohrleitungsdiagramme [*]
                    Jensen / Eigentümer BW-Rohrleitungsdiagramme [*] Jensen / Eigentümer PW-Rohrleitungsdiagramme [*] 
                       Jensen / Eigentümer
                    Brandleitungsleitungsdiagramme [*] Jensen / Owner Steel Design Module 4 und 5 [*]
                    Jensen / Besitzer Stahlkonstruktionsmodule 6,7,8 [*] Jensen / Besitzer Feuerzonen [*] 
                       Jensen / Besitzer
                    Wärmelastdaten (inkl. OFE) [*] Besitzer Besitzer Ausrüstungsinformationen / Wärmelastdaten [*]
                    Jensen / Owner Main Wireway Routing [*] NBBBJensen FGS-Diagramm [*] NBBBJensen PAGA
                    Diagramm [*] NBBBJensen Telefon Diagramm [*]""",
                    []),
                ("""9.6.6,9,8.2,9.9.3,9.10.1,9.103, 12.3""", []),
                (
                    """JETZT DAHER für eine gute und wertvolle Gegenleistung, deren Erhalt und Hinlänglichkeit davon 
                    sind Hiermit wird vereinbart, dass sich die Parteien wie folgt einig sind: 1. Lizenzgewährung. 
                    NECTAR gewährt hiermit Siboney eine exklusive Lizenz und ein exklusives Recht in den Vereinigten 
                    Staaten, ihren Territorien und Besitztümern, um abgeleitete Werke des "MathTrek 1,2,3", 
                    "MathTrek 4,5,6" und "MathTrek 1,2,3" zu verwenden, zu überarbeiten, zu modifizieren und zu 
                    erstellen Softwareprogrammreihe "Math Trek 7,8,9" (die "lizenzierte Software") zur Verwendung auf 
                    Macintosh und Windows-Betriebssysteme und zum Umpacken, Herstellen, Vermarkten, Verteilen, 
                    Verkaufen, Leasing, Lizenzierung und Unterlizenzierung dieser überarbeiteten und / oder 
                    modifizierten lizenzierten Software. Solche Überarbeitungen,
                    Modifikationen und abgeleitete Werke werden hier als "modifizierte Software" bezeichnet. Das 
                    Vorstehende Lizenzen an Siboney unterliegen dem in Abschnitt 2 genannten Recht von NECTAR und allen 
                    anderen Lizenzen, die NECTAR zuvor Endbenutzern der lizenzierten Software gewährt hat. Siboney soll 
                    haben Keine anderen Rechte an der lizenzierten oder modifizierten Software als in dieser 
                    Vereinbarung festgelegt. NECTAR konsultiert Siboney diesbezüglich auf begründete Anfrage von Siboney
                    Überarbeitungen, Modifikationen und dergleichen sowie alle Überarbeitungen und dergleichen 
                    unterliegen Die Genehmigung von NECTAR, die nicht unangemessen zurückgehalten werden darf. NECTAR 
                    erhält eine (1) Kopie von jedem kommerziellen Produkt, das gemäß dieser Lizenz erstellt wurde.""",
                    []),
                (
                    """NECTAR gewährt Siboney hiermit eine exklusive Lizenz und ein Recht in den Vereinigten Staaten
                     Territorien und Besitztümer, um abgeleitete Werke der zu verwenden, zu überarbeiten, zu 
                     modifizieren und zu erstellen Softwareprogrammreihen "MathTrek 1,2,3", "MathTrek 4,5,6" und 
                     "Math Trek 7,8,9" (die "Lizenzierten") Software ") zur Verwendung unter Macintosh- und 
                     Windows-Betriebssystemen sowie zum Umpacken, Herstellen, solche überarbeiteten und / oder 
                     modifizierten Lizenzen vermarkten, vertreiben, verkaufen, leasen, lizenzieren und unterlizenzieren
                     Software.""",
                    []),
                (
                    """27.1 Inverzugsetzung 1-71 27.2 Verzug des Auftragnehmers 1-72 27.3 Bewertung zum Datum von
                     Kündigung 1-72 27.4 Zahlung nach Kündigung 1-72 27.5 Auswirkung auf die Haftung für Verspätung 
                     1-72 27.6 Verzug des Arbeitgebers 1-73 27.7 Entfernen der Ausrüstung des Auftragnehmers 1-73 27.8 
                     Zahlung bei Kündigung für die Standardeinstellung des Arbeitgebers 1-73""",
                    []),
                (
                    """30.1 Zoll, Einfuhrzölle und Steuern 1-74 30.2 Zollabfertigung 1-75 30.3 Steuern
                       1-75 30.4 Zölle und Steuern auf die Ausrüstung des Auftragnehmers 1-75""",
                    []),
                ("""3.18.1, 6.1.1, 7.3.6, 8,2.1, 9.3.2, 9.8.4, 9.9.1,""", []),
                ("""OCIP Credits insgesamt 19.867.980""", []),
                ("""3.11,42.8,7, 8.3.1, 9.3.1.1, 11.4.9""", []),
                (
                    """Änderungsanforderungsformular: 122 Benachrichtigung über Entwurfsaktion: DAN / 0007 Erhöhung auf 
                    Garantiert Maximaler Preis: HK $ 250.000 / USD 32.052 12. Check-in und Lagerort des Mantels Ort: 
                    Erster Stock, Besprechungsräume Neben der Hauptbesprechung befindet sich ein separater Garderobe- 
                    und Aufbewahrungsbereich Zimmer im ersten Stock GL 20 / V-T. Änderungsanforderungsformular: 123 
                    Benachrichtigung über Entwurfsaktion: DAN / 0014 Erhöhung auf den garantierten Höchstpreis: HK 
                    $ 50.000 / USD 6.410 13. Hotelregistrierung Schalterstandort: Hotel Hauptregistrierungsschalter 
                    Bereitstellung zusätzlicher Lüfter für die Hauptregistrierungszähler zur Erfüllung der 
                    Kühlanforderungen von IT-Geräten. Antragsformular ändern:
                    125 Design Action Notification: DAN / 0046 Erhöhung auf den garantierten Höchstpreis: HK $ 76.000 /
                    USD 9,744 14. Büro / Speisekammer des VIP-Managers Ort: Erdgeschoss, VIP-Bereich Das private 
                    Restaurant Der Raum zum VIP-Casino wird gelöscht und durch ein VIP-Manager-Büro, eine trockene 
                    Speisekammer und ersetzt Verbindungskorridor. Änderungsanforderungsformular: 126 Benachrichtigung 
                    über Entwurfsaktion: DAN / 0019 Erhöhen auf der garantierte Höchstpreis: HK $ 67.000 / USD 8.590""",
                    []),
                ("""5,397,150""", []),
                (
                    """Kläger O2 Micro International Limited und Beklagte Monolithic Power Systems, Inc. (MPS),
                    Michael Hsing, Advanced Semiconductor Manufacturing Company, Ltd. (ASMC), ASUSTeK Computer,
                    Inc. und Compal Electronics, Inc. (zusammen Beklagte) bestreiten die Bedeutung von Begriffen und
                    Ausdrücke, die im US-Patent Nr. 6,259,615 von 02 Micro (das 615-Patent) und im US-Patent Nr. 625 
                    verwendet werden. 6,396,722 (das '722-Patent) und sein US-Patent Nr. 6,804,129 (das' 129-Patent) 
                    .1 02 Micro fordert den Gerichtshof auf, die zuvor von diesem Gerichtshof und von
                    das Gericht des östlichen Bezirks von Texas. Die Angeklagten fordern den Gerichtshof auf, ihren 
                    Bauvorschlag anzunehmen von zwei umstrittenen Phrasen. Darüber hinaus beantragt O2 Micro eine 
                    zusammenfassende Beurteilung auf der Grundlage von Sicherheiten estoppel. Die Angeklagten lehnen 
                    den Antrag und die Gegenbewegung zur zusammenfassenden Beurteilung ab. O2 Micro ist dagegen
                    ihren Antrag auf summarische Beurteilung. Die Angelegenheit wurde am 27. Oktober 2006 verhandelt
                    In den Papieren der Parteien, den darin angeführten Beweismitteln und der mündlichen Verhandlung 
                    legt der Gerichtshof die umstrittene Begriffe und Ausdrücke wie unten dargelegt. Darüber hinaus 
                    lehnt der Gerichtshof den Antrag von O2 Micro ab für ein zusammenfassendes Urteil und gewährt 
                    teilweise den Antrag der Beklagten auf ein zusammenfassendes Urteil und lehnt ihn ab
                    Teil. HINTERGRUND I. In Rede stehende Patente Die Patente 615, 722 und 129 sind alle berechtigt:
                    "Hocheffizienter adaptiver DC / AC-Wandler." Sie beziehen sich auf dieselbe Technologie: die
                    Das 129-Patent ist eine Fortsetzung des 722-Patents""",
                    [datetime.date(2006, 10, 27)]),
                ("""6,396,722 (the ‘722 patent) and its U.S. Patent No.""", []),
                (
                    """Japanisches Restaurant Nudel Restaurant Italienisches Restaurant Änderungsantragsformular: 130 
                     Design Aktionsbenachrichtigung: DAN / 008 Erhöhung auf den garantierten Höchstpreis: HK $ 75.075 / 
                     USD 9.625 17. Gekühlte Weinschränke Lage: Erster Stock, italienisches Restaurant Gekühlte 
                     Weinkühler (4nr) sind im italienischen Restaurant inbegriffen. Diese sind in Mühlen auf der 
                     Rückseite von unterzubringen die Getränkebar.""",
                    []),
                (
                    """ABTEILUNG 10 ABTEILUNG 10 - SPEZIALITÄTEN 10000 Erlaubnis zur Installation des vom Eigentümer 
                    versorgten zusammengekauerten Bereichs
                    Sicherheitselemente 3.000 10100 Markierungsschilder 119.000 10160 Toilettenräume aus Metall 
                    45.000 10500 Metall Schließfächer mit 10160 10520 Feuerlöschern und Schränken 6.000 10810 
                    Toilettenzubehör mit 10160 10950 Bauspezialitäten - Zulage für Eckschutz 41.000 ABTEILUNG 11 
                    ABTEILUNG 11 - AUSRÜSTUNG 11130 Projektionswände mit 10100 11160 Ladedockausrüstung NIC von Base 
                    Bldg. 11400 Lebensmittel Serviceausrüstung 838.000 11601 Laborabzüge mit 12345 11604 
                    Laborarmaturen mit 12345 11605 Installationszuschlag für Laborgeräte 78.000 ABTEILUNG 12 
                    ABTEILUNG 12 - MÖBEL 12345 Labor Fallarbeit 2.860.000 12514 Vertikaljalousien 12515 Rollos 
                    110.000 12670 Eingang Matten 2.000 12710 Feste Sitzplätze 70.000 ABTEILUNG 13 ABTEILUNG 13 - 
                    SONDERBAU 13038 Kontrollierte Temperaturräume 145.000 ABTEILUNG 14 ABTEILUNG 14 - 
                    VERTIKALER TRANSPORT 14100 Aufzüge
                    690.000 14200 Getriebeaufzüge mit 14100 14400 Handicap-Hebebühne 18.000 ABTEILUNG 15 ABTEILUNG 15 -
                    MECHANICAL 15300 Brandschutz 698.000 15420 Sanitär 3.150.000 15600 HVAC 9.773.000 AHU
                    Vor dem Kauf 1.438.000 15900 Gebäudesteuerungssystem 1.169.000 ABTEILUNG 16 ABTEILUNG 16 -
                    ELEKTRISCHE 16100 Elektrik 7.025.000 16500 Archetechurale Beleuchtungskörper mit 16100 16700
                    Tele / Daten 839.000 18000 Inbetriebnahme mit Handel ================= 
                    ============================================================= ================== 
                    =================""",
                    []),
                (
                    """Zum 15. März, 2016 verfügte Premier Pacific Construction, Inc. über 5.169.000 Stammaktien
                     hervorragend.""",
                    [datetime.date(2016, 3, 15)]),
                (
                    """2.13 EIGENKAPITAL. Zusätzlich zu den erforderlichen Aktienfonds hat der Kreditnehmer die 
                     folgenden Beträge verwendet für Bauzwecke bei den folgenden Projekten und solche Beträge werden 
                     nicht erstattet von Der Erlös des Darlehens: Aversana 13.144.901,00 USD Savona 8.681.981,00 USD 
                     Grande Isle I & II 7.073.050,00""",
                    []),
                (
                    """1. Der umfassende feste, einseitige Baupreis für dieses Projekt beträgt RMB ￥ 500 / m²
                     Truthahn (einschließlich der Sicherheitsbaugebühr und ￥ 20 / m² unvorhersehbarer Gebühr). 
                     Der Vertrag Der Preis wird vorläufig auf 36.810.000 RMB festgelegt (in Worten: Sechsunddreißig 
                     Millionen und achthundert und Zehntausend Yuan). Unabhängig vom Grund wird der Preis nicht 
                     angepasst. Der Bau Das Gebiet unterliegt zum Zeitpunkt der Zahlung den Kartendaten der 
                     Wohnungsbehörde.""",
                    []),
                (
                    """Der Vertragspreis wird vorläufig auf 36.810.000 RMB festgelegt (in Worten: Sechsunddreißig 
                       Millionen und Achthundertzehntausend Yuan).""",
                    []),
                ("""Gesamt 6.576.210,93 Darlehen       11.12.2007 10.000.000,00""",
                 [datetime.date(2007, 12, 11)]),
                (
                    """Der Vertragspreis beträgt USD 70.016.819- (70 Millionen, Sechzehntausend, Achthundert und
                     Neunzehn).""",
                    []),
                (
                    """Vertragspreis: Der Vertragspreis des BOHRERS, einschließlich des Bohrausrüstungspakets
                     und das Unterwasser-Ausrüstungspaket ist US-Dollar fünfhundertsiebenundfünfzig Millionen
                     (USD 557.000.000,00) zuzüglich oder abzüglich des Betrags, falls vorhanden, gemäß Ziffer 3 
                     unten (der "VERTRAGSPREIS"), einschließlich der PC-Summe, Nettoforderungen von BUILDER, die 
                     exklusiv sind KÄUFERZUBEHÖR.""",
                    []),
                (
                    """59. Erhöhen Sie 5no. der Türbreite Ort: Erster Stock, Servicelift Lobby Die Öffnungsweite
                    Die Anzahl der 5-nr-Türen in der Lobby des Servicelifts wird erhöht, um den Zugang für den 
                    Reinigungsservice zu erleichtern Servicewagen. Änderungsanforderungsformular: 192 
                    Entwurfsaktionsbenachrichtigung: DAN / 0053 Erhöhung auf Garantierter Höchstpreis: Null 60. Upgrade 
                    Lift Lobby beendet Standort: Parkhaus Die Innenausstattung des Aufzugs und der Aufzugslobby auf dem 
                    Parkplatz wurde von einer „Rückseite des Hauses“ aufgewertet. zu einem "Front of House" -Standard 
                    und Klimaanlage wird in die Lobbys eingeführt. Änderungsanforderung Formular: 194 Design Action 
                    Benachrichtigung: DAN / 0060 Erhöhung auf den garantierten Höchstpreis: HK $
                    800.000 / USD 102.565 61. Überarbeitetes Layout des Eingangs des Personals Ort: Podium Externer 
                    Eingang Das interne Layout des Personaleintrags wurde überarbeitet, um einen separaten Eintrag in 
                    die Einstellung aufzunehmen Büro mit Zugangs- / Ausgangskontrolle durch automatische Drehkreuze. 
                    Änderungsanforderungsformular: 196 Design Aktionsbenachrichtigung: DAN / 0068 Erhöhung auf den 
                    garantierten Höchstpreis: Null 62. Festzeltzeichen Fundament Standort: North West Corner of Site Das 
                    Stahlbetonfundament für den Wynn Das Festzelt wird dem Arbeitsumfang des Auftragnehmers hinzugefügt. 
                    Änderungsanforderungsformular: 197 Entwurfsaktion Benachrichtigung: DAN / 0061 Erhöhung auf den 
                    garantierten Höchstpreis: HK $ 8.000.000 / USD 1.025.641""",
                    []),
                (
                    """Kurzfristige Verbindlichkeiten Derzeitige Fälligkeiten langfristiger Verbindlichkeiten 745 USD 
                    1.130 USD Verbindlichkeiten aus Lieferungen und Leistungen 100.816 90.111 Abrechnungen, die die 
                    Kosten und das geschätzte Ergebnis übersteigen 87.149 57.412 Rückstellungen
                    und sonstige kurzfristige Verbindlichkeiten 81.311 82.924 Summe kurzfristige Verbindlichkeiten 
                    270.021 231.577 Langfristig Schulden 138.364 63.891 Sonstige langfristige Verbindlichkeiten 9.607 
                    6.370 Latente Ertragsteuern 31.540 31.540 Verpflichtungen und Eventualverbindlichkeiten Eigenkapital
                    Vorzugsaktien, Nennwert 0,01 USD, genehmigt 3.000.000 Aktien, keine im Umlauf - - Stammaktien, 
                    Nennwert 0,01 USD, genehmigt 100.000.000 Anteile; ausgegebene und ausstehende 41.107.224 Aktien im 
                    Jahr 2001 und 40.881.908 im Jahr 2000 411 409 Kapitalrücklage 61.421 56.381 Gewinnrücklagen 338.066 
                    330.172 Kumulierte Sonstige Gesamtverlust (112) - 399.786 386.962 Unverdiente Entschädigung (13.818)
                    (9.198) 385.968 377.764 $ 835.500 $ 711.142 ========= ========= </TABLE>""",
                    []),
                (
                    """Mieterverbesserungen / Vanille (559.150) (356.250) (198.400) (32.000) (1.922.139) (1.928.150)
                     6.011 Leasingprovisionen (26.348) (55.250) (45.435) (54.500) (301.065) (394.900) 93.835
                     Renovierung und Ersatz 0 0 0 0 (218.536) (200.000) (18.536) GESAMTKAPITAL (585.498)
                     (411.500) (243.835) (86.500) (2.441.740) 2.523.050 81.310""",
                    []),
                (
                    """Strom und Daten für zusätzliche Geldautomaten Standort: Podiumsbereiche Strom- und 
                       Datenbestimmungen sind für zusätzliche Geldautomaten an folgenden Standorten enthalten: 
                       Chinesisches Restaurant - 1nr Food Court - 1nr Retail Promenade - 2nr Staff Dining - 2nr 
                       Änderungsanforderungsformular: 133 Design Action Benachrichtigung: DAN / 0015 Erhöhung auf den 
                       garantierten Höchstpreis: HK $ 30.000 / USD 3.831 19.""",
                    []),
                ("""Überarbeiteter MCA-OCIP-Abzug 26.236.418 Bei Kreditanpassungen einvernehmlich vereinbart 
                    (2.000.000     )""",
                 []),
                (
                    """Prozent (66 2/3%) des ausstehenden Kapitalbetrags des von Non-Defaulting gehaltenen Kredits
                     Kreditgeber.""",
                    []),
                (
                    """ERFORDERLICHE Leihgeber. Ab jedem Zeitpunkt der Feststellung vor Beendigung der Verpflichtungen,
                     Kreditgeber (ausgenommen säumige Kreditgeber), deren aggregierte Kreditprozentsätze mindestens 
                     ausmachen Sechsundsechzig und zwei Drittel Prozent (66 2/3%) der von nicht säumigen Kreditgebern 
                     gehaltenen Verpflichtungen. Wie von jedem Datum der Feststellung, das nach Beendigung der 
                     Verpflichtungen eintritt, Kreditgeber (ohne säumige Kreditgeber) mit mindestens sechsundsechzig 
                     und zwei Dritteln Prozent (66 2/3%) des ausstehenden Kapitalbetrags des von nicht säumigen 
                     Kreditgebern gehaltenen Kredits.""",
                    []),
                (
                    """22.1 Definition höherer Gewalt 1-64 22.2 Auswirkung höherer Gewalt 1-64 22.3 Bekanntmachung von
                     Vorkommen 1-64 22.4 Fortsetzung der Leistung 1-65 22.5 Zusätzliche Kosten durch höhere Gewalt
                     1-65 22.6 Durch höhere Gewalt verursachter Schaden 1-65 22.7 Beendigung infolge höherer Gewalt
                     1-65 22.8 Zahlung bei Beendigung der Gewalt 1-65 Höhere Gewalt 22.9 Befreiung von der Leistung 1-66 
                     22.10 Höhere Gewalt, die die 1-66 Pflichten des Ingenieurs beeinflusst""",
                    []),
                ("""19.1 Verfahren 1-61 19.2 Bewertung 1-62""", []),
                (
                    """18.1 Antragsmethoden 1-57 18.2 Ausstellung der Zahlungsbescheinigung 1-57 18.3 Korrekturen
                     zu Zahlungsbescheinigungen 1-58 18.4 Zahlung 1-58 18.5 Zahlungsverzug 1-58 18.6 Abhilfemaßnahmen am
                     Nichtzertifizierung oder Zahlung 1-58 18.7 Antrag auf endgültige Zahlungsbescheinigung 1-59
                     18.8 Ausstellung der endgültigen Zahlungsbescheinigung 1-59 18.9 Endgültige Zahlungsbescheinigung 
                     abschließend 1-60 18.10 Vorauszahlung 1-60 18.11 Vorauszahlungsgarantie 1-60 18.12 
                     Zahlungsbedingungen 1-60 18.13 Aufbewahrung 1-61""",
                    []),
                ("""56 vom 22. März 1983; Seismic Code durch Executive Decreto No.""", [datetime.date(1983, 3, 22)]),
                (
                    """16.1 Recht des Ingenieurs, 1-53 zu variieren 16.2 Abweichung von mehr als 5% 1-54 16.3 
                     Änderungsreihenfolge Verfahren 1-54 16.4 Uneinigkeit über die Anpassung des Vertragspreises 1-55 
                     16.5 Änderung am Herstellung und Zeichnungen 1-55 16.6 Auftragnehmer zum Fortfahren 1-56 16.7 
                     Kostenaufzeichnungen 1-56 16.8 Monatliche Abweichungserklärung 1-56""",
                    []),
                (
                    """2.1.1, 3.3.3, 3.12.4, 3.12.8, 3.12.10, 4.1.2, 4.2.1, 4.2.2, 4.2.3, 4.2.6, 4.2.7, 4.2.10, 
                    4,2.12, 4.2.13, 4.4, 5.2.1, 7.4, 9.4.2, 9.6.4, 9.6.6""",
                    []),
                (
                    """11.1 Hinweis auf Tests 1-41 11.2 Zeit für Tests 1-41 11.3 Verzögerte Tests 1-42 11.4 
                     Einrichtungen für Tests nach Abschluss 1-42 11.5 Bekanntmachung der Testergebnisse 1-42 11.6
                     Erneutes Testen 1-42 11.7 Nichtübereinstimmung als zum Ergebnis von Test 1-43 11.8 Folgen des 
                     Nichtbestehens der Tests 1-43 nach Abschluss 11.9 Test Zertifikat 1-43 11.10 Prüfung durch die 
                     Betreiber des Arbeitgebers 1-44""",
                    []),
                (
                    """Alle Mitteilungen, Zustimmungen, Anfragen und sonstigen Mitteilungen im Rahmen dieser 
                      Vereinbarung müssen schriftlich erfolgen gelten als ordnungsgemäß erteilt, wenn (a) per Hand 
                      geliefert, (b) per Fernkopierer (mit Quittung) versandt wird bestätigt), sofern eine Kopie in der 
                      in Ziffer (c) oder (c) angegebenen Weise versandt wird, wenn vom Adressaten erhalten, wenn sie 
                      von DHL, Federal Express, Airborne Express oder anderen allgemein gesendet werden
                      anerkannter internationaler Express-Lieferservice (Quittung angefordert), jeweils an die
                      geeignete Adressen und Telecopier-Nummern, die unten angegeben sind (oder an solche anderen 
                      Adressen und Telecopier-Nummern als Partei können sich durch Mitteilung an die anderen Parteien 
                      als solche bezeichnen: (i) Wenn an CCKK: SoftBank Corp. 3-42-3 Nihonbashi-Hamacho Chuo-ku 
                      Tokio 103 Japan Telecopier No.""",
                    []),
                ("""4.2.2, 4.2.9, 4.3,4, 9.4.2, 9.8.3, 9.9.2, 9.10.1, 13.5""", []),
                ("""Größe 19 1/2" L x 7/8" H.""", []),
                (
                    """3. Die Lieferung des Schiffes wird verschoben und der überarbeitete Liefertermin ist der 30. Juli
                     2017. Die Vertragsparteien erörtern und vereinbaren nach Durchführung dieses Änderungsantrags Nr. 1
                     die notwendige Änderungen am Programm (d. h. Ziffer 4.1 des Vertrags), um die
                     überarbeitetes Lieferdatum. Soweit sich die Vertragsparteien noch nicht einig sind oder sich nicht 
                     darauf geeinigt haben, ist dies erforderlich Änderungen am Programm, alle Verweise auf das Programm 
                     im Vertrag gelten für die Grundlage, dass (1) KD7 (Beginn des Inbetriebnahmeprozesses) auf den 31. 
                     Oktober 2016 überarbeitet wird und (2) KD 11 (Lieferung des Schiffes) wird auf den 30. Juli 2017 
                     sowie alle anderen Meilensteine und Schlüsseldaten überarbeitet sind unwirksam.""",
                    [datetime.date(2017, 7, 30), datetime.date(2016, 10, 31)]),
                ("""""", []),
                ('''Leasing ohne Anzahlung: Monatliche Rate 300€, Laufzeit 36 Monaten, Gesamtkosten 10.800€''', []),
                ('''14 Monaten''', []),
                ('''Laufzeit 36 Monaten''', []),
                ('''mit 2''', []),
                ('''mit 16''', []),
                ('''als 1 Jahr beträgt''', []),
                ('''als 2 Jahre betragen''', []),
                ('''als 3 Jahre betragen''', []),
                ('''1 Jahr nach Inkrafttreten dieser Richtlinie.''', []),
                ('''Nach 1 Jahr werden die Positionslisten automatisch gelöscht.''', []),
                ('''Der Vertrag beginnt mit dem Moment zu laufen, in dem der Vermieter / Mieter seine 
                    Unterschriften darauf gemacht hat. Wenn die Mietdauer mehr als 1 Jahr beträgt, ist eine staatliche 
                    Registrierung des Vertrags erforderlich.''', []),
                ('''Leasing ohne Anzahlung: Monatliche Rate 300€, Laufzeit 36 Monaten, Gesamtkosten
                    10.800€
                    Leasing mit 2.500€ Anzahlung: Monatliche Rate 230,55€, Laufzeit 36 Monate,
                    Gesamtkosten 10.800€
                    Durch eine Sonderzahlung wird die monatliche Belastung gesenkt, das Risiko für
                    den Leasinggeber sinkt.''', []),
                ('1 Jahr', []),
                ('mit', []),
                ('''14 Monaten''', []),
                ('''Laufzeit 36 Monaten''', []),
                ('''mit 2''', []),
                ('''mit 1''', []),
                ('''mit ersten''', []),
                ('''mit dritten''', []),
                ('''mit 16''', []),
                ('''der vierte Juli''', [datetime.date(TODAY.year, 7, 4)]),
                ('''der dritte März''', [datetime.date(TODAY.year, 3, 3)]),
                ('''achtzehnter Mai''', [datetime.date(TODAY.year, 5, 18)]),
                ('''29. März 2017''', [datetime.date(2017, 3, 29)]),
                ('''der dritte März''', [datetime.date(TODAY.year, 3, 3)]),
                ('''der vierte Juni''', [datetime.date(TODAY.year, 6, 4)]),
                ('''24 Stunden 5''', []),
                ('''6 Stunden''', []),
                ('''1 Stunde''', []),
                ('''- Definitiver Leasing-Entscheid innert 24 Stunden 5.''', []),
                ('''zuletzt geändert durch Art. 39 G v. 29.3.2017 I 626''',
                 [datetime.date(2017, 3, 29)]),
                ('''Leasing mit 2.500€ Anzahlung: Monatliche Rate 230,55€''', []),
                ('''Soldaten auf Zeit in der Fassung der Bekanntmachung vom 16. Mai 2002 (BGBl. I S. 1778)''',
                 [datetime.date(2002, 5, 16)]),
                ('''Planet mit 3 Satelliten''', []),
                ('''Wenn der Mietvertrag im September 2015 beginnt, wann sollte der Mieter 
                    seine erste Betriebskostenabrechnung vom Vermieter erhalten?''',
                 [datetime.date(2015, 9, 1)]),
                ('''Was passiert, wenn das Gebäude am 01.10.2015 verkauft wird''',
                 [datetime.date(2015, 10, 1)]),
                ('''am siebzehnten Oktober eintausendneunhundertdreiundachtzig''',
                 [datetime.date(1983, 10, 17)]),
                ('''am sechzehnten November 2001''', [datetime.date(2001, 11, 16)]),
                ('Commencement Date: 09/12/2022.', [datetime.date(2022, 12, 9)]),
                ('Anfangsdatum: 27/02/2023', [datetime.date(2023, 2, 27)]),
                ('Anfangsdatum: 11/11/1993', [datetime.date(1993, 11, 11)])]  #
    return examples


def add_numeric_date_samples(examples):
    p = 0.01
    for k in range(1970, 2010):
        for j in range(1, 13):
            for i in range(1, 31):
                if random.random() <= p:
                    year = k
                    month = j
                    day = i
                    try:
                        d = datetime.date(year, month, day)
                        n = random.randint(2, 30)
                        d2 = d + datetime.timedelta(days=n)
                        examples.append(("""{0}/{1}/{2}""".format(year, month, day), [d]))
                        examples.append(("""{0}.{1}.{2}""".format(year, month, day), [d]))
                        examples.append(("""bis {0}-{1}-{2}""".format(year, month, day), [d]))
                        examples.append(("bis " + d.strftime("%b %d, %Y"), [d]))
                        examples.append(("am " + d.strftime("%B %d, %Y"), [d]))
                        examples.append(("bis {0} zum {1}".format(d, d2), [d, d2]))
                        examples.append(("bis {0} zum {1}".format(d.strftime("%b d, %Y"), d2.strftime("%b d, %Y")),
                                         [d, d2]))
                        examples.append(("{0} bis {1}".format(d.isoformat(), d2.isoformat()), [d, d2]))
                        examples.append(("{0} bis {1}".format(d.strftime("%b d, %Y"), d2.strftime("%b d, %Y")),
                                         [d, d2]))
                    except ValueError:
                        continue

    for year in (0, 2010, 1981, 2021):
        for prefix in ['', 'der ', 'am ']:
            for num_fmt in ['w', 'd']:
                for month_index, month in enumerate(MONTH_NAMES):
                    for day in range(1, 31):
                        date_year = year or TODAY.year
                        try:
                            date = datetime.date(date_year, month_index + 1, day)
                        except ValueError:
                            continue

                        day_str = get_written_date_num(day) if num_fmt == 'w' else f'{day}.'
                        year_str = f' {year}' if year else ''
                        date_str = f'{prefix}{day_str} {month}{year_str}'
                        examples.append((date_str, [date],))


def get_written_date_num(num: int) -> str:
    if num - 1 < len(WRITTEN_DATE_NUMS):
        return WRITTEN_DATE_NUMS[num - 1]

    date_str = num2words(num, lang='de')
    if num < 20:
        return date_str + 'ten'
    return date_str + 'sten'
