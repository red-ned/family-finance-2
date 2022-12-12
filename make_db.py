#!/usr/bin/env python

import pdb
import xml.etree.ElementTree as et



class DataBase():
    def __init__(self):
        self._db = None


    def _add_account(self, values):
        id = int(values['id'])
        name = values['name']
        type_id = int(values['typeID'])
        catagory = int(values['catagory'])
        closed = bool(values['closed'])
        cd = bool(values['creditDebit'])
        envelopes = bool(values['envelopes'])

    def _add_account_type(self, values):
        id = int(values['id'])
        name = values['name']

    def _add_envelope(self, values):
        id = int(values['id'])
        name = values['name']
        group_id = int(values['groupID'])
        closed = bool(values['closed'])

    def _add_envelope_line(self, values):
        id = int(values['id'])
        line_item_id = int(values['lineItemID'])
        envelope_id = int(values['envelopeID'])
        description = values['description']
        amount = float(values['amount'])


    def _add_line_type(self, values):
        id = int(values['id'])
        name = values['name']

    def _add_line_item(self, values):
        id = int(values['id'])
        transaction_id = int(values['transactionID'])
        date = values['date']
        type_id = int(values['typeID'])
        account_id = int(values['accountID'])
        description = values['description']

        try:
            confirmation_number = values['confirmationNumber']
        except Exception as e:
            confirmation_number = None

        envelope_id = int(values['envelopeID'])
        complete = values['complete']
        amount = float(values['amount'])
        cd = bool(values['creditDebit'])


    def _add_ofx_line(self, values):
        line_item_id = int(values['lineItemID'])
        account_id = int(values['accountID'])
        fit_id = values['fitID']

        data = values['data']
        data = self._convert_ofx_string_to_dict_str(data)

    def _convert_ofx_string_to_dict_str(self, ofx_str):
        ofx_str = ofx_str.replace('\n', '')
        ofx_str = ofx_str.replace('<STMTTRN>', '')
        ofx_str = ofx_str.replace('</STMTTRN>', '')

        ofx_values = dict()
        for segment in ofx_str.split('<'):
            if segment == '' or segment.startswith('/'):
                continue

            name, value = segment.split('>')
            ofx_values[name] = value

        return str(ofx_values)

    def _get_tag(self, element):
        # Remove the annoying Namespace from every tag.
        tag = element.tag
        if tag.startswith('{http://tempuri.org/ExportDS.xsd}'):
            return tag[33:]

        raise Exception('Unexpected namespace in the tag <{}>'.format(tag))

    def _parse_element(self, element):
        table_name = self._get_tag(element)
        values = {}

        for leaf in element:
            value = leaf.text
            name = self._get_tag(leaf)
            values[name] = value

        if table_name == 'OFXLineItem':
            self._add_ofx_line(values)

        elif table_name == 'LineType':
            self._add_line_type(values)

        elif table_name == 'LineItem':
            self._add_line_item(values)

        elif table_name == 'EnvelopeLine':
            self._add_envelope_line(values)

        elif table_name == 'Account':
            self._add_account(values)

        elif table_name == 'AccountType':
            self._add_account_type(values)

        elif table_name == 'Envelope':
            self._add_envelope(values)

    def make_tables(self):
        self._db = None

    def populate_db_with_xml(self, xml_path):
        tree = et.parse(xml_path)
        root = tree.getroot()

        for element in root:
            self._parse_element(element)



if __name__ == '__main__':
    db = DataBase()
    db.make_tables()
    db.populate_db_with_xml('data/FFdata.xml')
