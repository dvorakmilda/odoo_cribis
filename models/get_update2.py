import requests
import uuid
import datetime
import xmltodict
import html
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from dateutil import parser


class Cribis():
    def __init__(self):
        self.login='asg-T2T'
        self.password='Ac7.UG'
#        self.PId= "CribisCZ_GetUpdates2"
#        self.PNs= "urn:crif-cribiscz-GetUpdates2:2012-08-31"

        self.day=datetime.datetime.today()-datetime.timedelta(days=7)
        self.day_string=self.day.strftime('%Y-%m-%d')

        self.url="https://ws.cribis.cz/CribisCZWS.asmx"

    def call_cribis(self):
        body = '<?xml version="1.0" encoding="utf-8"?>' + \
            '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">' + \
            '<soap:Header>' + \
            '<Message GId="' + str(uuid.uuid4()) + '" MId="' + str(uuid.uuid4()) + '" MTs="' + datetime.datetime.utcnow().isoformat() + '" xmlns="urn:crif-message:2006-08-23">' + \
            '<C UD="" UId="' + self.login + '" UPwd="' + self.password + '"/>' + \
            '<P SId="SCZ" PId="CribisCZ_GetUpdates2" PNs="urn:crif-cribiscz-GetUpdates2:2012-08-31"/>' + \
            '<Tx TxNs="urn:crif-messagegateway:2006-08-23"/>' + \
            '</Message>' + \
            '</soap:Header>' + \
            '<soap:Body>' + \
            '<MGRequest xmlns="urn:crif-messagegateway:2006-08-23">' + \
            html.escape('<GetUpdates2Input Country="W" Date1="' + self.day_string + '" Language="CZ" NegativeInfo="true" Relations="true" CompanyEvents="true" FinancialFigures="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:crif-cribiscz-GetUpdates2:2012-08-31"/>') + \
            '</MGRequest>' + \
            '</soap:Body>' + \
            '</soap:Envelope>'

        headers = {"User-Agent": "asg-soap/0.0.1",
                "Content-Length": str(len(body)),
                "Accept": "text/xml",
                "Content-Type": "text/xml; charset=utf-8"
                }

        call=requests.post(self.url,data=body,headers=headers)
        string_xml=call.text
        tree=xmltodict.parse(string_xml)
        data=tree['soap:Envelope']['soap:Body']['MGResponse'].get('#text')
        data_tree=xmltodict.parse(data)
        print(data_tree)
#        company_identification=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['CompanyIdentification']
#        key_information=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['KeyInformation']
#        financial_ratios=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['FinancialRatios']
#        company_rating_calculation_response=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['CompanyRatingCalculationResponse']
#        key_results_warning=company_rating_calculation_response=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['KeyResultsWarning']
"""
        self.data_odoo=[{'report_date':parser.parse(company_identification.get('ReportDate')),
                    'ent_id':company_identification.get('Ent_id'),
                    'index_cribis_level':company_rating_calculation_response.get('IndexCribis10Level')
                    }]

        print(self.data_odoo)
        return self.data_odoo
"""

if __name__ == "__main__":
    cribis=Cribis()
    call=cribis.call_cribis()

