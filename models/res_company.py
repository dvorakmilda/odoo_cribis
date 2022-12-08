from odoo import fields, models, api, _
from odoo.exceptions import UserError
from ares_util.ares import call_ares, validate_czech_company_id
from ares_util.exceptions import AresConnectionError
import requests
import uuid
import datetime
import xmltodict
import html
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from dateutil import parser

class ResCompany(models.Model):
    _inherit = "res.company"
    
    business_id = fields.Char()
    cribis_ids = fields.Many2many('res.company.cribis', string='')
    cribis_login = fields.Char(string='', default='asg-T2T')
    cribis_password = fields.Char(string='', default='Ac7.UG')
    cribis_url = fields.Char(string='', default="https://ws.cribis.cz/CribisCZWS.asmx")
    cribis_ftp_address = fields.Char(string='')
    cribis_ftp_login = fields.Char(string='')
    cribis_ftp_password = fields.Char(string='')

    def cribis_get_global_validate_user_output(self):
        CRIBIS_LOGIN = self.env.user.company_id.cribis_login
        CRIBIS_PASSWORD = self.env.user.company_id.cribis_password

        company_obj=self.env['res.company'].browse(self.env.user.company_id.id)

        body = '<?xml version="1.0" encoding="utf-8"?>' + \
            '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">' + \
            '<soap:Header>' + \
            '<Message GId="' + str(uuid.uuid4()) + '" MId="' + str(uuid.uuid4()) + '" MTs="' + datetime.datetime.utcnow().isoformat() + '" xmlns="urn:crif-message:2006-08-23">' + \
            '<C UD="" UId="' + CRIBIS_LOGIN + '" UPwd="' + CRIBIS_PASSWORD + '"/>' + \
            '<P SId="SCZ" PId="CribisCZ_GlobalValidateUser" PNs="urn:crif-cribiscz-GlobalValidateUser:2015-10-21"/>' + \
            '<Tx TxNs="urn:crif-messagegateway:2006-08-23"/>' + \
            '</Message>' + \
            '</soap:Header>' + \
            '<soap:Body>' + \
            '<MGRequest xmlns="urn:crif-messagegateway:2006-08-23">' + \
            html.escape('<GlobalValidateUserInput xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:crif-cribiscz-GlobalValidateUser:2015-10-21"/>') + \
            '</MGRequest>' + \
            '</soap:Body>' + \
            '</soap:Envelope>'


        headers = {"User-Agent": "asg-soap/0.0.1",
                "Content-Length": str(len(body)),
                "Accept": "text/xml",
                "Content-Type": "text/xml; charset=utf-8"
                }

        call=requests.post(self.env.user.company_id.cribis_url,data=body,headers=headers)
        string_xml=call.text
        tree=xmltodict.parse(string_xml)
        data=tree['soap:Envelope']['soap:Body']['MGResponse'].get('#text')
        data_xml=xmltodict.parse(data)
        accounts=data_xml['GlobalValidateUserOutput']['Accounts']['Account']
        for cribis_id in self.env.user.company_id.cribis_ids:
            delete_id=company_obj.write( {'cribis_ids' : [(2,cribis_id)]})
            print(delete_id)
#        delete_cribis_ids=company_obj.write( {'cribis_ids' : [(5,_,_)]})
        commit=self.env.cr.commit()

        for account in accounts:
            data_odoo=[(0,0,{'account_type_id': account.get('AccountTypeId'),
                    'name': account.get('AccountType'),
                    'valid_from': parser.parse(account.get('ValidFrom')),
                    'expiration': parser.parse(account.get('Expiration')),
                    'remaining':account.get('Remaining'),
                    'obtained':account.get('Obtained'),
                    'unit': account.get('Unit')
                    })]
            write_cribis_ids=company_obj.write( {'cribis_ids' : data_odoo })
            commit=self.env.cr.commit()

            print(data_odoo, write_cribis_ids, commit)



