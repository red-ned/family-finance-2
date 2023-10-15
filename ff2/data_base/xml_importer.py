from xml.etree import ElementTree


class XmlImporter():
    def __init__(self, data_base):
        self._db = data_base

        self._line_type_id_none = self._db.get_id_of_line_type(' ')
        self._line_type_id_refund = self._db.get_id_of_line_type('Refund')
        self._line_type_id_transfer = self._db.get_id_of_line_type('Transfer')

        self._line_complete_id_pending = self._db.get_id_of_line_complete('Pending')
        self._line_complete_id_cleared = self._db.get_id_of_line_complete('Cleared')
        self._line_complete_id_reconsiled = self._db.get_id_of_line_complete('Reconciled')

        self._account_id_none = self._db.get_id_of_account(' ')


    def _add_account(self, values):
        id_ = int(values['id'])
        name = values['name']
        # Ignore the origional type id. Use catagory as the new type id.
        #type_id = int(values['typeID'])
        type_id = int(values['catagory'])
        closed = self._fix_bool(values['closed'])
        cd = self._fix_bool(values['creditDebit'])
        envelopes = self._fix_bool(values['envelopes'])

        if id_ <= 0:
            # Skip the old special accounts.
            # Only using the new special 0 NONE account.
            return

        try:
            self._db.add_account(id_=id_, name=name, account_type_id=type_id,
                    closed=closed, credit_debit=cd, envelopes=envelopes)

        except Exception as e:
            print('Add Account FAILED. <{}> from {}'.format(e, values))

    def _add_envelope(self, values):
        id_ = int(values['id'])
        name = values['name']
        #group_id = int(values['groupID'])
        favorite_account_id = 0
        closed = self._fix_bool(values['closed'])

        if id_ <= 0:
            # Skip the old special envelopes.
            # Only using the new special 0 NONE envelope.
            return

        try:
            self._db.add_envelope(
                    id_=id_,
                    name=name,
                    favorite_account_id=favorite_account_id,
                    closed=closed
                    )

        except Exception as e:
            print('Add Envelope FAILED. <{}> from {}'.format(e, values))

    def _add_envelope_item(self, values):
        id_ = int(values['id'])
        line_item_id = int(values['lineItemID'])
        envelope_id = int(values['envelopeID'])
        description = values.get('description', '')
        amount = float(values['amount'])

        if description is None:
            description = ''

        self._db.add_envelope_item(
                id_=id_,
                line_item_id=line_item_id,
                envelope_id=envelope_id,
                description=description,
                amount=amount
            )

    def _add_line_item(self, values):
        id_ = int(values['id'])
        transaction_id = int(values['transactionID'])
        date = values['date']
        line_type_id = self._fix_line_type_id(values['typeID'])
        account_id = self._fix_account_id(values['accountID'])
        description = values.get('description', '')
        confirmation_number = values.get('confirmationNumber', '')
        #envelope_id = values['envelopeID']
        line_complete_id = self._int_from_complete(values['complete'])
        amount = float(values['amount'])
        cd = self._fix_bool(values['creditDebit'])

        if description is None:
            description = ''

        description = description.strip()

        if confirmation_number:
            confirmation_number = confirmation_number.strip()

        if confirmation_number:
            description = '{} - ({})'.format(description, confirmation_number)

        self._db.add_line_item(
                id_=id_,
                transaction_id=transaction_id,
                date=date,
                line_type_id=line_type_id,
                account_id=account_id,
                description=description,
                line_complete_id=line_complete_id,
                amount=amount,
                credit_debit=cd
                )

    def _add_ofx_item(self, values):
        line_item_id = int(values['lineItemID'])
        account_id = int(values['accountID'])
        fit_id = values['fitID']

        data_dict = self._convert_ofx_string_to_dict(values['data'])
        data_str = str(data_dict)

        memo = data_dict.get('NAME', '') + ' ' + data_dict.get('MEMO', '')
        memo = memo.strip()

        self._db.add_ofx_item(
                line_item_id=line_item_id,
                account_id=account_id,
                fit_id=fit_id,
                memo=memo,
                data=data_str
                )

    def _convert_ofx_string_to_dict(self, ofx_str):
        ofx_str = ofx_str.replace('\n', '')
        ofx_str = ofx_str.replace('<STMTTRN>', '')
        ofx_str = ofx_str.replace('</STMTTRN>', '')

        ofx_values = dict()
        for segment in ofx_str.split('<'):
            if segment == '' or segment.startswith('/'):
                continue

            name, value = segment.split('>')
            ofx_values[name] = value

        return ofx_values

    def _fix_account_id(self, value):
        value = int(value)

        if value == -1:
            return self._account_id_none

        return value

    def _fix_bool(self, value):
        if value == 'true':
            return 1

        if value == 'false':
            return 0

        raise Exception('Unexpected bool <{}>'.format(value))

    def _fix_complete(self, value):
        if value == ' ':
            return self._line_complete_id_pending

        if value == 'C':
            return self._line_complete_id_cleared

        if value == 'R':
            return self._line_complete_id_reconsiled

        raise Exception('Unexpected bool <{}>'.format(value))

    def _fix_line_type_id(self, value):
        value = int(value)

        if value in (-1, 9):
            # Change old type_id -1 (NULL) and 9 (Erase Me) to new (NONE) value
            return self._line_type_id_none

        if value == 8:
            # Change old type_id 8 (Refund) to new value
            return self._line_type_id_refund

        if value == 4:
            # Change old type_id 4 (Transfer) to new value
            return self._line_type_id_transfer

        return value

    def _get_tag(self, element):
        # Remove the annoying Namespace from every tag.
        tag = element.tag
        if tag.startswith('{http://tempuri.org/ExportDS.xsd}'):
            return tag[33:]

        raise Exception('Unexpected namespace in the tag <{}>'.format(tag))

    def _get_values_from_element(self, element):
        values = dict()

        for leaf in element:
            value = leaf.text
            name = self._get_tag(leaf)
            values[name] = value

        return values

    def _int_from_complete(self, value):
        if value == 'R':
            # Reconsiled
            return 2

        if value == 'C':
            # Complete
            return 1

        if value == ' ':
            # Incomplete
            return 0

        return value

    def _parse_element(self, element):
        table_name = self._get_tag(element)
        values = self._get_values_from_element(element)

        if table_name == 'LineItem':
            self._add_line_item(values)

        elif table_name == 'EnvelopeLine':
            self._add_envelope_item(values)

        elif table_name == 'Account':
            self._add_account(values)

        elif table_name == 'Envelope':
            self._add_envelope(values)

        #elif table_name == 'LineType':
            #self._add_line_type(values)

        #elif table_name == 'EnvelopeGroup':
            #self._add_account_type(values)

        #elif table_name == 'AccountType':
            #self._add_account_type(values)

        elif table_name == 'OFXLineItem':
            self._add_ofx_item(values)

        else:
            print(table_name, values)


    def import_from_xml(self, xml_path):
        tree = ElementTree.parse(xml_path)
        root = tree.getroot()

        print('Populating DB with data from data/FFdata.xml')
        for element in root:
            self._parse_element(element)

        self._db.commit()

        input('Press Enter to continue.')
