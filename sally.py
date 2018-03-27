# -*- coding: UTF-8 -*-

import os
import sys
import csv
import unicodecsv
from datetime import datetime
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
from collections import defaultdict
from xml.etree import ElementTree as et
import traceback

COLUMNS = {u'identifier': 'COTE = identifier',
           u'title': 'Titre de l\'article',
           u'date': 'Date',
           u'language': 'Langue'
           }

# Sally


class Sally(object):
    log_in_console = False

    def __init__(self, working_folder, csv_bordereau, console_log=True):
        self.log_in_console = console_log
        pdf_list = self.get_working_folder_pdf_files_list(working_folder)
        csv_datas = self.validate_and_get_datas_from_csv_input(csv_bordereau)
        if csv_datas is False:
            self.write_logs(u"# Arrêt de l'analyse")
            return

        files_list = self.get_files_info_list(pdf_list, csv_datas)
        self.write_report_csv(files_list, working_folder)
        self.write_controle_pdf_csv(files_list, working_folder)

    def get_files_info_list(self, pdf_list, csv_datas):
        files_list = []
        self.write_logs(u"# Récupération des métadonnées ...")
        for id, pdf in enumerate(pdf_list):
            self.write_logs(u" Récupération des métadonnées "+str(id+1)+u"/"+str(len(pdf_list)))
            pdf_file = FileDescriptor(pdf)
            files_list.append(pdf_file)

        self.write_logs(u"# Vérification des métadonnées ...")
        for id, file in enumerate(files_list):
            self.write_logs(u" Vérification des métadonnées "+str(id+1)+u"/"+str(len(files_list)))
            file.validate_file(csv_datas)

        return files_list

    def get_working_folder_pdf_files_list(self, working_folder):
        files_list = []
        self.write_logs(u"# Recherche des fichiers pdf ...")
        for root, dirs, files in os.walk(working_folder):
            for file in files:
                file_path = (os.path.join(root, file)).replace(u"\\", u"/")
                filename, file_extension = os.path.splitext(file_path)
                if file_extension == u".pdf":
                    files_list.append(file_path)
        print(u" "+str(len(files_list))+u" fichiers pdf trouvés")

        return files_list

    def validate_and_get_datas_from_csv_input(self, csv_bordereau):
        f = open(csv_bordereau)
#        for i in range(4):
#            print i
#            line = f.next()
#            print line

        reader = unicodecsv.DictReader(f, delimiter=',')
        dict_first_line = reader.unicode_fieldnames
        if not self.check_csv_header(dict_first_line):
            print(
                u"# Les intitulés de colonnes (ligne 9) du fichier csv indiqué sont erronnés, veuillez les vérifier. "
                u"De même, assurez-vous que le fichier soit bien en utf-8.")
            return False
        # csv_datas = []
        # for row in reader:
        #     csv_datas.append(row[COLUMNS[u'identifier']])
        # return csv_datas
        csv_datas = {}
        for row in reader:
            csv_datas[row[COLUMNS[u'identifier']]] = {u'title':row[COLUMNS[u'title']], u'date':row[COLUMNS[u'date']], u'language':row[COLUMNS[u'language']]}
        return csv_datas

    @staticmethod
    def check_csv_header(headers):
        dict = {
            u'identifier': False,
            u'title': False,
            u'language': False,
            u'date': False,
        }
        for head in headers:
            if head in COLUMNS.values():
                dict[COLUMNS.keys()[COLUMNS.values().index(head)]] = True

        return all(value is True for value in dict.values())

    @staticmethod
    def write_report_csv(files_list, working_folder):
        print(u"# Écriture du fichier report_sally.csv ...")
        f = open(working_folder+'report_sally.csv', 'wb')
        fieldnames = ['Nom du fichier', 'isLisible', 'isValide', 'sameDate', 'sameLanguage', 'sameTitle', 'Date',
                      'Identifier', 'Langue', 'Title']
        fieldnames = ['Nom du fichier', 'FichierValide', 'PDFValide', 'VersionPDF', 'Identifiant_existe', 'Date_identique', 'Titre identique', 'Langue_identique', 'Date_pdf', 'Identifier_pdf', 'Langue_pdf', 'Titre_pdf']
        writer = unicodecsv.DictWriter(f, delimiter=',', fieldnames=fieldnames)
        writer.writeheader()

        for file in files_list:
            writer.writerow(
            {'Nom du fichier': file.filename, 'FichierValide': file.file_is_valid, 'PDFValide': file.pdf_version_is_valid,
             'VersionPDF': file.pdf_version, 'Identifiant_existe': file.valid_identifier, 'Date_identique': file.sameDate,
             'Titre identique': file.sameTitle,
            'Langue_identique': file.sameLangue, 'Date_pdf': file.date, 'Identifier_pdf': file.identifier,
             'Langue_pdf': file.language, 'Titre_pdf': file.title})
        print(u" Fichier report_sally.csv créé")

    @staticmethod
    def write_controle_pdf_csv(files_list, working_folder):
        print(u"# Écriture du fichier controle_pdf_sally.csv ...")
        f = open(working_folder+'controle_pdf_sally.csv', 'wb')
        writer = unicodecsv.writer(f, delimiter=",")
        writer.writerow([u"Bibliothèque de SCIENCES PO (Paris)", u"Total des erreurs majeures du format PDF",
                         u"Validation du contrôle du format PDF"])
        cpt_error = 0
        for file in files_list:
            if file.file_is_valid is False:
                cpt_error += 1
        writer.writerow([u'Prestataire : Azentis', str(cpt_error)])
        writer.writerow([u''])
        writer.writerow([u'Nbre de volumes : ' + str(len(files_list))])
        writer.writerow([u''])
        writer.writerow([u''])
        writer.writerow([u''])
        writer.writerow([u''])
        writer.writerow([u'N° identifiant', u'Nombre de fichiers à contrôler', u'Fichier validé', u'Fichier validé (bool) 0=ok/1=nok'])

        for file in files_list:
            writer.writerow([file.identifier, u'1', u"Non" if file.file_is_valid is False else u"Oui", u"1" if file.file_is_valid is False else u"0"])

        print(u" Fichier controle_pdf_sally.csv créé")

    def write_logs(self, string):
        if self.log_in_console:
            print(string)


"""
    ~~~~~~

    Parses XMP metadata from PDF files.

    By Matt Swain. Released under the MIT license.
"""

RDF_NS = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
XML_NS = '{http://www.w3.org/XML/1998/namespace}'
NS_MAP = {
    'http://www.w3.org/1999/02/22-rdf-syntax-ns#'    : 'rdf',
    'http://purl.org/dc/elements/1.1/'               : 'dc',
    'http://ns.adobe.com/xap/1.0/'                   : 'xap',
    'http://ns.adobe.com/pdf/1.3/'                   : 'pdf',
    'http://ns.adobe.com/xap/1.0/mm/'                : 'xapmm',
    'http://ns.adobe.com/pdfx/1.3/'                  : 'pdfx',
    'http://prismstandard.org/namespaces/basic/2.0/' : 'prism',
    'http://crossref.org/crossmark/1.0/'             : 'crossmark',
    'http://ns.adobe.com/xap/1.0/rights/'            : 'rights',
    'http://www.w3.org/XML/1998/namespace'           : 'xml'
}


class XmpParser(object):
    """
    Parses an XMP string into a dictionary.

    Usage:

        parser = XmpParser(xmpstring)
        meta = parser.meta
    """

    def __init__(self, xmp):
        self.tree = et.XML(xmp)
        self.rdftree = self.tree.find(RDF_NS+'RDF')

    @property
    def meta(self):
        """ A dictionary of all the parsed metadata. """
        meta = defaultdict(dict)
        for desc in self.rdftree.findall(RDF_NS+'Description'):
            for el in desc.getchildren():
                ns, tag = self._parse_tag(el)
                value = self._parse_value(el)
                meta[ns][tag] = value
        return dict(meta)

    @staticmethod
    def _parse_tag(el):
        """ Extract the namespace and tag from an element. """
        ns = None
        tag = el.tag
        if tag[0] == "{":
            ns, tag = tag[1:].split('}', 1)
            if ns in NS_MAP:
                ns = NS_MAP[ns]
        return ns, tag

    @staticmethod
    def _parse_value(el):
        """ Extract the metadata value from an element. """
        if el.find(RDF_NS+'Bag') is not None:
            value = []
            for li in el.findall(RDF_NS+'Bag/'+RDF_NS+'li'):
                value.append(li.text)
        elif el.find(RDF_NS+'Seq') is not None:
            value = []
            for li in el.findall(RDF_NS+'Seq/'+RDF_NS+'li'):
                value.append(li.text)
        elif el.find(RDF_NS+'Alt') is not None:
            value = {}
            for li in el.findall(RDF_NS+'Alt/'+RDF_NS+'li'):
                value[li.get(XML_NS+'lang')] = li.text
        else:
            value = el.text
        return value


def xmp_to_dict(xmp):
    """ Shorthand function for parsing an XMP string into a python dictionary. """
    return XmpParser(xmp).meta


class FileDescriptor(object):
    pdf_version_is_valid = False
    file_is_valid = False
    filename = None
    date = None
    title = None
    identifier = None
    language = None
    valid_date = False
    valid_title = False
    valid_identifier = False
    valid_language = False
    sameLangue = False
    sameDate = False
    sameTitle = False
    pdf_version = None

    def __init__(self, pdf_file_path):
        self.hydrate_metadatas(pdf_file_path)
        self.filename = os.path.basename(pdf_file_path)

    def hydrate_metadatas(self, pdf_file_path):
        pdf_file = self.validate_pdf_format(pdf_file_path)
        if pdf_file:
            parser = PDFParser(pdf_file)

            try:
                doc = PDFDocument(parser)
                metadata = resolve1(doc.catalog['Metadata']).get_data()
                metadatas = xmp_to_dict(metadata)
                try:
                    self.date = metadatas['dc']['date'][0]
                except:
                    pass
                try:
                    self.title = metadatas['dc']['title']['x-default']
                except:
                    pass
                try:
                    self.identifier = metadatas['dc']['identifier']
                except:
                    pass
                try:
                    self.language = metadatas['dc']['language'][0]
                except:
                    pass
            except:
                pass
        else:
            return

    def validate_pdf_format(self, pdf_file_path):
        try:
            pdf_file = open(pdf_file_path, 'rb')
            self.pdf_version = (pdf_file.readline())[5:8]
            if self.pdf_version == "1.4":
                self.pdf_version_is_valid = True
            return pdf_file
        except:
            self.pdf_version_is_valid = False
            return False

    def validate_file(self, csv_datas):
        try:
            csv_date = csv_datas[self.identifier]['date']
        except:
            csv_date = None
        self.valid_date = self.validate_date(csv_date)

        try:
            csv_title = csv_datas[self.identifier]['title']
        except Exception as e:
            print(traceback.format_exc())
            csv_title = None
        self.valid_title = self.validate_title(csv_title)

        try:
            csv_language = csv_datas[self.identifier]['language']
        except:
            csv_language = None
        self.valid_language = self.validate_language(csv_language)

        if self.identifier is not None:
            try:
                if csv_datas[self.identifier]:
                    self.valid_identifier = True
            except Exception as e:
                self.valid_identifier = False

        if all([self.pdf_version_is_valid, self.sameDate, self.sameTitle, self.valid_identifier,
                self.sameLangue]) and all(v is not None for v in [self.filename, self.title,
                                                                      self.identifier, self.language]):
            self.file_is_valid = True

    def validate_title(self, csv_title):
        if csv_title == self.title and csv_title is not None:
            self.sameTitle = True
            return True
        else:
            return False

    def validate_language(self, csv_language):
        if csv_language == self.language and csv_language is not None:
            self.sameLangue = True
            return True
        else:
            return False

    def validate_date(self, csv_date):
        if (csv_date == "" or csv_date == "nd") and (self.date == "0001-01-01" or self.date is None):
            self.sameDate = True
            return False
        try:
            try:
                datetime_date = datetime.strptime(self.date, '%Y-%m-%d')
                datetime_date_csv = datetime.strptime(csv_date, '%Y-%m-%d')
            except:
                try:
                    datetime_date = datetime.strptime(self.date, '%Y-%m')
                    datetime_date_csv = datetime.strptime(csv_date, '%Y-%m')
                except:
                    try:
                        datetime_date = datetime.strptime(self.date, '%Y')
                        datetime_date_csv = datetime.strptime(csv_date, '%Y')
                    except:
                        return False
#            if int(datetime_date.year) < 1950:
#                return False
            if datetime_date == datetime_date_csv:
                self.sameDate = True
                return True
            else:
                return False
        except Exception as e:
            return False


# CSV input checker

if __name__ == '__main__':
    if len(sys.argv) == 3:
        if os.path.exists(sys.argv[1]):
            sally = Sally(sys.argv[1], sys.argv[2])
        else:
            print(u"Le chemin indiqué n'existe pas")
    else:
        print(u"Utilisation : python sally.py path_to_files path_to_bordeau_csv")
