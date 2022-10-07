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
    
    business_id = fields.Char(string='ICO')
    cribis_activation_date= fields.Datetime(string='Monitoring activation')
    cribis_report_date=fields.Datetime(string='Actual report date')
    cribis_monitoring = fields.Boolean(string='Monitoring cribis')
    cribis_ent_id = fields.Integer(string='')
    cribis_index_level = fields.Integer(string='Index10')
    cribis_semafor = fields.Char(string='Semafor')

    def cribis_get_portfolio(self):
   
        PId= "CribisCZ_GetPortfolio"
        PNs= "urn:crif-cribiscz-GetPortfolio:2011-09-01"
        MGRequest='<GetPortfolioInput xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:crif-cribiscz-GetPortfolio:2011-09-01"/>'
        cribis_company=self.env['res.company'].search_read([('id', '=', 1)])[0]
        CRIBIS_LOGIN = cribis_company.get('cribis_login')
        CRIBIS_PASSWORD = cribis_company.get('cribis_password')

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

        call=requests.post(cribis_company.get('cribis_url'),data=body,headers=headers)
        string_xml=call.text
        tree=xmltodict.parse(string_xml)
        data=tree['soap:Envelope']['soap:Body']['MGResponse'].get('#text')
        data_tree=xmltodict.parse(data)['GetPortfolioOutput']['Portfolio']['Company']
        cribis_partner=self.env['res.partner'].search_read([('company_type','=' ,'company')])
        for i in data_tree:
            country_id=self.env['res.country'].search([('code','like', i.get('@CountryCode') )])
            print (country_id['id'])
            data_odoo={'name':i.get('@Name'),
                    'company_type': 'company',
                    'business_id': i.get('@Ic'),
                    'country_id': country_id['id'],
                    'cribis_activation_date':parser.parse(i.get('@ActivationDate')),
                    'cribis_ent_id':int(i.get('@Ent_id')),
                    'cribis_monitoring': True,
                    }

            partner_id=self.env['res.partner'].search_read([('business_id','=' ,i.get('@Ic'))])
            print (partner_id)
            if partner_id:
                for part in partner_id:
                    partner_obj=self.env['res.partner'].browse(part['id'])
                    partner_obj.write(data_odoo)
                    commit=self.env.cr.commit()
            else:
                partner=self.env['res.partner'].create(data_odoo)
                commit=self.env.cr.commit()

            #commit=self.env.cr.commit()
        #načíst organizace podle ičo

        #podívat se podle ico jaký organizace mám v odoo

        #když existuje organizace, tak u



    def cribis_get_global_micro_report(self):

        cribis_company=self.env['res.company'].search_read([('id', '=', 1)])[0]
        CRIBIS_LOGIN = cribis_company.get('cribis_login')
        CRIBIS_PASSWORD = cribis_company.get('cribis_password')
        PId= "CribisCZ_GetGlobalMicroReport"
        PNs= "urn:crif-cribiscz-GetGlobalMicroReport:2014-04-08"
        country='CZ'

        for rec in self:

            MGRequest='<GetGlobalMicroReportInput  Ico="' + rec.business_id + '" Pdf="false" Currency="CZK" Country="' + country + '" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:crif-cribiscz-GetGlobalMicroReport:2014-04-08"/>'
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
                '<P SId="SCZ" PId="'+ PId+'" PNs="'+ PNs+'"/>' + \
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

            call=requests.post(cribis_company.get('cribis_url'),data=body,headers=headers)
            string_xml=call.text
            tree=xmltodict.parse(string_xml)
            data=tree['soap:Envelope']['soap:Body']['MGResponse'].get('#text')
            data_tree=xmltodict.parse(data)
            company_identification=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['CompanyIdentification']
            key_information=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['KeyInformation']
            financial_ratios=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['FinancialRatios']
            company_rating_calculation_response=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['CompanyRatingCalculationResponse']
            key_results_warning=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['KeyResultsWarning']

            data_odoo=[({'cribis_report_date': parser.parse(company_identification.get('ReportDate')),
                        'cribis_ent_id': company_identification.get('EntId'),
                        'cribis_index_level': company_rating_calculation_response.get('IndexCribis10Level'),
                        'cribis_semafor': company_identification.get('Semafor'),
                        })]


            print(data_odoo, rec)

            #commit=self.env.cr.commit()

