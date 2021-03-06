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
        self.PId= "CribisCZ_GetPortfolio"
        self.PNs= "urn:crif-cribiscz-GetPortfolio:2011-09-01"
        self.MGRequest='<GetPortfolioInput xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:crif-cribiscz-GetPortfolio:2011-09-01"/>'
        self.url="https://ws.cribis.cz/CribisCZWS.asmx"

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
        data=tree['soap:Envelope']['soap:Body']['MGResponse'].get('#text')
        data_tree=xmltodict.parse(data)['GetPortfolioOutput']['Portfolio']['Company']
        self.cribis_data=[]
        for i in data_tree:
            country_id=self.env['res.country'].search([('code','like', i.get('@CountryCode') )])
            data_odoo=[{'name':i.get('@Name'),
                        'business_id': i.get('@Ic'),
                        'country_code': country_id,
                        'activation_date':parser.parse(i.get('@ActivationDate')),
                        'ent_id':int(i.get('@Ent_id')),
                        }]
            self.cribis_data.append(data_odoo)
        print (self.cribis_data)
        return self.cribis_data


if __name__ == "__main__":
    cribis=Cribis()
    call=cribis.call_cribis()








"""
<wsdl:definitions xmlns:i0="urn:crif-messagegateway:2006-08-23" xmlns:tm="http://microsoft.com/wsdl/mime/textMatching/" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:mime="http://schemas.xmlsoap.org/wsdl/mime/" xmlns:tns="http://tempuri.org/" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:s="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://schemas.xmlsoap.org/wsdl/soap12/" xmlns:http="http://schemas.xmlsoap.org/wsdl/http/" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" targetNamespace="http://tempuri.org/">
<wsdl:import namespace="urn:crif-messagegateway:2006-08-23" location="https://ws.cribis.cz/CribisCZWS.asmx?wsdl=wsdl1"/>
<wsdl:types>
<s:schema targetNamespace="http://tempuri.org/">
<s:import schemaLocation="https://ws.cribis.cz/CribisCZWS.asmx?schema=schema1" namespace="urn:crif-messagegateway:2006-08-23"/>
<s:import schemaLocation="https://ws.cribis.cz/CribisCZWS.asmx?schema=schema2" namespace="urn:crif-message:2006-08-23"/>
</s:schema>
</wsdl:types>
<wsdl:service name="CribisCZWS">
<wsdl:port name="ServiceSoap" binding="i0:ServiceSoap">
<soap:address location="https://ws.cribis.cz/CribisCZWS.asmx"/>
</wsdl:port>
<wsdl:port name="ServiceSoap1" binding="i0:ServiceSoap1">
<soap12:address location="https://ws.cribis.cz/CribisCZWS.asmx"/>
</wsdl:port>
</wsdl:service>
</wsdl:definitions>

"""