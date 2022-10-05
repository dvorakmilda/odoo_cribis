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

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    business_id = fields.Char()
    cribis_ent_id = fields.Integer(string='')
    

    def cribis_get_portfolio(self):
   
        PId= "CribisCZ_GetPortfolio"
        PNs= "urn:crif-cribiscz-GetPortfolio:2011-09-01"
        MGRequest='<GetPortfolioInput xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:crif-cribiscz-GetPortfolio:2011-09-01"/>'
        CRIBIS_LOGIN=  self.user.company.cribis_login
        CRIBIS_PASSWORD= self.user.company.cribis_password


        message = '<Message GId="' + \
            str(uuid.uuid4())+ \
            '" MId="' + \
            str(uuid.uuid4()) + \
            '" MTs="' + \
            datetime.datetime.utcnow().isoformat() + \
            '" xmlns="urn:crif-message:2006-08-23">' + \
            '<C UD="" UId="' + \
            CRIBIS_LOGIN + \
            '" UPwd="' + \
            CRIBIS_PASSWORD + \
            '"/>' + \
            '<P SId="SCZ" PId="'+PId+'" PNs="'+PNs+'"/>' + \
            '<Tx TxNs="urn:crif-messagegateway:2006-08-23"/>' + \
            "</Message>"
        html_req=html.escape(MGRequest)
        body = '<?xml version="1.0" encoding="utf-8"?>' + \
            '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">' + \
            "<soap:Header>" + \
            message + \
            "</soap:Header>" + \
            "<soap:Body>" + \
            '<MGRequest xmlns="urn:crif-messagegateway:2006-08-23">' + \
             html_req+ \
            "</MGRequest>" + \
            "</soap:Body>" + \
            "</soap:Envelope>"

        headers = {"User-Agent": "asg-soap/0.0.1",
                "Content-Length": str(len(body)),
                "Accept": "text/xml",
                "Content-Type": "text/xml; charset=utf-8"
                }

        call=requests.post(self.url,data=body,headers=headers)
        string_xml=call.text
        tree=xmltodict.parse(string_xml)
        data=tree['soap:Envelope']['soap:Body']['MGResponse'].get('#text')
        data_tree=xmltodict.parse(data)['GetPortfolioOutput']['Portfolio']['Company']
        cribis_data=[]
        for i in data_tree:
            country_id=self.env['res.country'].search([('code','like', i.get('@CountryCode') )])
            data_odoo=[{'name':i.get('@Name'),
                        'business_id': i.get('@Ic'),
                        'country_code': country_id,
                        'activation_date':parser.parse(i.get('@ActivationDate')),
                        'ent_id':int(i.get('@Ent_id')),
                        }]
            cribis_data.append(data_odoo)
        print(cribis_data)


