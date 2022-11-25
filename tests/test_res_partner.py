from unittest.mock import patch
from odoo.tests.common import Form
from odoo.tests import TransactionCase


def _validate_czech_company_id_mock(*args, **kwargs):
    return True

def _ares_mock(*args, **kwargs):
    return {
        'legal': {
            'company_name': 'Optimal 4 s.r.o.',
            'company_id': '26200031',
            'company_vat_id': 'CZ26200031',
            'legal_form': '101'
        },
        'address': {
            'region': 'Nymburk',
            'city': 'Lysá nad Labem',
            'city_part': 'Lysá nad Labem',
            'street': 'Masarykova 457',
            'zip_code': '28922'
        }
    }

class TestAssetTypes(TransactionCase):
    def test_onchange_business_id_name(self):
        country_id = self.env.ref('base.cz')
        with patch('odoo.addons.odoo_cribis.res_partner.call_ares', _ares_mock):
            with patch('odoo.addons.odoo_cribis.models.res_partner.validate_czech_company_id', _validate_czech_company_id_mock):
                form_class = Form(self.env['res.partner'])
                form_class.country_id = country_id
                form_class.business_number = '26200031'

                self.assertEqual(form_class.name, 'Optimal 4 s.r.o.')
                self.assertEqual(form_class.vat, 'CZ26200031')
