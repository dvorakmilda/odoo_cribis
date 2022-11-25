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
        self.ico='49496182'
        self.country='CZ'
        self.PId= "CribisCZ_AddToPortfolio"
        self.PNs= "urn:crif-cribiscz-PortfolioManagement:2011-09-01"
        self.MGRequest='<PortfolioManagementInput Ico="' + self.ico + '" Country="' + self.country + '" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:crif-cribiscz-PortfolioManagement:2011-09-01"/>'

        self.url="https://ws.cribis.cz/CribisCZWS.asmx"

        add_action='AddTo'
        remove_action='RemoveFrom'

    def call_cribis(self):
            message = '<Message GId="' + \
            str(uuid.uuid4())+ \
            '" MId="' + \
            str(uuid.uuid4()) + \
            '" MTs="' + \
            datetime.datetime.utcnow().isoformat() + \
            '" xmlns="urn:crif-message:2006-08-23">' + \
            '<C UD="" UId="' + \
            self.login + \
            '" UPwd="' + \
            self.password + \
            '"/>' + \
            '<P SId="SCZ" PId="'+self.PId+'" PNs="'+self.PNs+'"/>' + \
            '<Tx TxNs="urn:crif-messagegateway:2006-08-23"/>' + \
            "</Message>"
            html_req=html.escape(self.MGRequest)

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

            data=tree['soap:Envelope']['soap:Header']['MessageResponse']['P']['R'].get('@D')
#            data_tree=xmltodict.parse(data)['GetPortfolioOutput']['Portfolio']['Company']
            #console.log(result['soap:Envelope']['soap:Header'].MessageResponse.P.R['$'].D);
            print (data)

if __name__ == "__main__":
    cribis=Cribis()
    call=cribis.call_cribis()