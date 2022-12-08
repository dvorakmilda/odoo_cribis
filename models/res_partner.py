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
    cribis_index_level = fields.Integer(string='Index')
    cribis_semafor = fields.Integer(string='Stoplights')
    cribis_rc_url = fields.Char(compute='_compute_cribis_rc_url', string='Conection graph', store=True )
    cribis_fl_url = fields.Char(compute='_compute_cribis_fl_url', string='Complete history', store=True)
    cribis_invisible_form_buttons = fields.Boolean(string="cribis_invisible_form_buttons", default=True)
    cribis_index10_level = fields.Integer(string='Index 10', default='0')
    cribis_credit_capacity = fields.Float(string='Credit Capacity')
    cribis_credit_used = fields.Float(string='Credit Used')
    cribis_probability_of_default = fields.Float(string='Probability of Default')
    cribis_end_date = fields.Datetime(string='End Date')
    cribis_revenues = fields.Float(string='Revenues')
    cribis_profitLoss = fields.Float(string='Profit Loss')
    cribis_total_assets = fields.Float(string='Total Assets')
    cribis_turnover_range = fields.Float(string='Turnover Range')
    cribis_main_nace = fields.Char(string='Main NACE')
    cribis_main_okec = fields.Char(string='Main OKEC')
    cribis_employees_range = fields.Char(string='Employees Range')
    cribis_registered_capital = fields.Float(string='Registered Capital')
    cribis_index10_max_rate = fields.Integer(string='cribis_index10_max_rate', default='10')
    cribis_stars = fields.Selection([('na', 'NA'),('poor', 'Poor'),('bad', 'Bad'),('normal', 'Normal'),('good', 'Good'), ('excelent', 'Excelent')], "Index 5", default='na')



    @api.depends('business_id')
    def _compute_cribis_rc_url(self):
        CRIBIS_LOGIN = self.env.user.company_id.cribis_login
        for rec in self:
            rec.cribis_rc_url='https://www2.cribis.cz/Hyperlinks/CertificateLink.aspx?username='+CRIBIS_LOGIN+'&language=cs-CZ&target=RC&output=Limited&country='+str(rec.country_id.code)+'&ico='+ str(rec.business_id)


    @api.depends('business_id')
    def _compute_cribis_fl_url(self):
        CRIBIS_LOGIN = self.env.user.company_id.cribis_login
        for rec in self:
            rec.cribis_fl_url='https://www2.cribis.cz/Hyperlinks/CertificateLink.aspx?username='+CRIBIS_LOGIN+'&language=cs-CZ&target=FL&output=Limited&country='+str(rec.country_id.code)+'&ico='+ str(rec.business_id)



    @api.onchange('business_id')
    def _onchange_bussiness_id(self):
        #neměnit, zatim funguje pouze pro CZ
        czech_country_id = self.env.ref('base.cz').id

        if self.business_id is not False and (len(self.business_id) not in (0, 8)):
            raise UserError(_("Bad number,for CZ must be exactly 8 numbers !"))

        validate_ico = False
        address = False
        if not self.business_id:
            self.cribis_invisible_form_buttons=True
            return
        if self.country_id and self.country_id.id != czech_country_id:
            self.cribis_invisible_form_buttons=True
            return
        else:
            self.cribis_invisible_form_buttons=False
        try:
            validate_ico = validate_czech_company_id(self.business_id)
        except AresConnectionError as ares_err:
            raise UserError(_("Network Connection Error!")) from ares_err
        except Exception as odoo_err:
            raise UserError(_("Business_ID not found!")) from odoo_err

        if validate_ico:
            try:
                ares = call_ares(self.business_id)
                address = ares['address']
                legal = ares['legal']
            except AresConnectionError as ares_err:
                raise UserError(_("Network Connection Error!")) from ares_err
        if address:
            self['name'] = legal.get('company_name')
            self['vat'] = legal.get('company_vat_id')
            self['city'] = address.get('city')
            self['street'] = address.get('street')
            self['zip'] = address.get('zip_code')
            self['country_id'] = czech_country_id
            if address.get('city_part') != self.city:
                self['street2'] = address.get('city_part')
            if address.get('city_town_part') is not None:
                self['city'] = address.get('city_town_part')


    def cribis_get_rc(self):
        return {  'name'     : 'Company relations graph',
                  'type'     : 'ir.actions.act_url',
                  'target'   : 'new',
                  'url'      :  self.cribis_rc_url
               }

    def cribis_get_fl(self):
        return {  'name'     : 'Complete company history',
                  'type'     : 'ir.actions.act_url',
                  'target'   : 'new',
                  'url'      :  self.cribis_fl_url
               }


    def cribis_get_portfolio(self):
        PId= "CribisCZ_GetPortfolio"
        PNs= "urn:crif-cribiscz-GetPortfolio:2011-09-01"
        MGRequest='<GetPortfolioInput xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:crif-cribiscz-GetPortfolio:2011-09-01"/>'
        CRIBIS_LOGIN = self.env.user.company_id.cribis_login
        CRIBIS_PASSWORD = self.env.user.company_id.cribis_password


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

        call=requests.post(self.env.user.company_id.cribis_url,data=body,headers=headers)
        string_xml=call.text
        tree=xmltodict.parse(string_xml)
        data=tree['soap:Envelope']['soap:Body']['MGResponse'].get('#text')
        data_tree=xmltodict.parse(data)['GetPortfolioOutput']['Portfolio']['Company']
        cribis_partner=self.env['res.partner'].search_read([('company_type','=' ,'company')])
        for i in data_tree:
            country_id=self.env['res.country'].search([('code','like', i.get('@CountryCode') )])
            #print (country_id['id'])
            data_odoo={'name':i.get('@Name'),
                    'company_type': 'company',
                    'business_id': i.get('@Ic'),
                    'country_id': country_id['id'],
                    'cribis_activation_date':parser.parse(i.get('@ActivationDate')),
                    'cribis_ent_id':int(i.get('@Ent_id')),
                    'cribis_monitoring': True,
                    'cribis_invisible_form_buttons':True,
                    'cribis_stars':'na'
                    }

            partner_id=self.env['res.partner'].search_read([('business_id','=' ,i.get('@Ic'))])
            #print (partner_id)
            if partner_id:
                for part in partner_id:
                    partner_obj=self.env['res.partner'].browse(part['id'])
                    partner_obj.write(data_odoo)
                    commit=self.env.cr.commit()
            else:
                partner=self.env['res.partner'].create(data_odoo)
                commit=self.env.cr.commit()


    def cribis_get_global_micro_report(self):
        CRIBIS_LOGIN = self.env.user.company_id.cribis_login
        CRIBIS_PASSWORD = self.env.user.company_id.cribis_password
        PId= "CribisCZ_GetGlobalMicroReport"
        PNs= "urn:crif-cribiscz-GetGlobalMicroReport:2014-04-08"

        for rec in self:
            MGRequest='<GetGlobalMicroReportInput  Ico="' + rec.business_id + '" Pdf="false" Currency="CZK" Country="' + rec.country_id.code + '" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:crif-cribiscz-GetGlobalMicroReport:2014-04-08"/>'
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

            call=requests.post(self.env.user.company_id.cribis_url,data=body,headers=headers)
            string_xml=call.text
            tree=xmltodict.parse(string_xml)
            data=tree['soap:Envelope']['soap:Body']['MGResponse'].get('#text')
            data_tree=xmltodict.parse(data)
            company_identification=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['CompanyIdentification']
            key_information=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['KeyInformation']
            financial_ratios=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['FinancialRatios']
            company_rating_calculation_response=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['CompanyRatingCalculationResponse']
            key_results_warning=data_tree['GetGlobalMicroReportOutput']['CompanyGlobalMicroReport']['KeyResultsWarning']

            #company_identification
            report_date = parser.parse(company_identification.get('ReportDate'))
            rec.cribis_report_date = report_date.strftime("%Y-%m-%d %H:%M:%S")
            company_identification.get('EntId').replace("'","")
            rec.cribis_ent_id = int(company_identification.get('EntId').replace("'",""))
            rec.cribis_index_level = int(company_rating_calculation_response.get('IndexCribisLevel').replace("NA","0").replace("'",""))
            rec.cribis_index10_level = int(company_rating_calculation_response.get('IndexCribis10Level').replace("NA","0").replace("'",""))
            rec.cribis_semafor = int(company_identification.get('Semafor').replace("'",""))

            if rec.cribis_index_level==1:
                rec.cribis_stars="poor"
            if rec.cribis_index_level==2:
                rec.cribis_stars="bad"
            if rec.cribis_index_level==3:
                rec.cribis_stars="normal"
            if rec.cribis_index_level==4:
                rec.cribis_stars="good"
            if rec.cribis_index_level==5:
                rec.cribis_stars="excelent"
            if rec.cribis_index_level==0:
                rec.cribis_stars="na"

            #banka
            bank_accounts_list=[]
            bank_accounts_list.append(company_identification.get('BankInfoList'))
            for i in bank_accounts_list:
                val=i['BankInfo']['Value']
                print(val)

            #key_information



            #company_rating_calculation
            if company_rating_calculation_response.get('CreditCapacity'):
                rec.cribis_credit_capacity=float(company_rating_calculation_response.get('CreditCapacity'))*float(company_rating_calculation_response.get('CreditUnit'))
            else:
                rec.cribis_credit_capacity=0
            if company_rating_calculation_response.get('CreditUsed'):
                rec.cribis_credit_used=float(company_rating_calculation_response.get('CreditUsed'))*float(company_rating_calculation_response.get('CreditUnit'))
            else:
                rec.cribis_credit_used=0

            rec.cribis_probability_of_default=float(company_rating_calculation_response.get('ProbabilityOfDefault').replace("NA","0").replace("'",""))


            commit=self.env.cr.commit()



"""
        sql.connect(config.helios, function(err) {
            var CI = result.GetGlobalMicroReportOutput.CompanyGlobalMicroReport.CompanyIdentification;
            var KI = result.GetGlobalMicroReportOutput.CompanyGlobalMicroReport.KeyInformation;
            var FR = result.GetGlobalMicroReportOutput.CompanyGlobalMicroReport.FinancialRatios;
            var CR = result.GetGlobalMicroReportOutput.CompanyGlobalMicroReport.CompanyRatingCalculationResponse;


            //console.log(require('util').inspect(KI, { depth: null }));
            // srovna financni parametry do pole s indexy Id
            /*
            if (FR.SetOfRatios) {
                if (FR.SetOfRatios[0] && FR.SetOfRatios[0].ArrayOfRatios) {
                    var ratios = indexBy('Id', FR.SetOfRatios[0].ArrayOfRatios.Ratio);
				}
            }
    */

            var employees = ''
            if (KI.EmployeesRangeList && KI.EmployeesRangeList.EmployeesRange) {
                if (Array.isArray(KI.EmployeesRangeList.EmployeesRange)) {
                    employees = KI.EmployeesRangeList.EmployeesRange[0].Value
                } else {
                    employees = KI.EmployeesRangeList.EmployeesRange.Value
                }
            }

            var struct = {
                _cribis_EntId: CI.EntId,
                _cribis_ReportDate: "'" + moment(CI.ReportDate).format("YYYY-MM-DD HH:mm:ss") + "'",
                _cribis_Semafor: CI.Semafor,
                _cribis_IndexCribisLevel: (CR.IndexCribisLevel == 'NA') ? -1 : CR.IndexCribisLevel,
                _cribis_IndexCribis10Level: (CR.IndexCribis10Level == 'NA') ? -1 : CR.IndexCribis10Level,
                _cribis_CreditCapacity: (CR.CreditCapacity) ? CR.CreditCapacity * CR.CreditUnit : -1,
                _cribis_CreditUsed: (CR.CreditUsed) ? CR.CreditUsed * CR.CreditUnit : -1,
                _cribis_ProbabilityOfDefault: (CR.ProbabilityOfDefault) ? CR.ProbabilityOfDefault : -1,
                _cribis_EndDate: (FR.SetOfRatios && FR.SetOfRatios[0]) ? "'" + FR.SetOfRatios[0].EndDate + "'" : -1,
                _cribis_Revenues: (KI.BasicEconomicsList && KI.BasicEconomicsList.BasicEconomics && KI.BasicEconomicsList.BasicEconomics[0] && KI.BasicEconomicsList.BasicEconomics[0].Revenues) ? KI.BasicEconomicsList.BasicEconomics[0].Revenues : -1, // Výnosy
                _cribis_ProfitLoss: (KI.BasicEconomicsList && KI.BasicEconomicsList.BasicEconomics && KI.BasicEconomicsList.BasicEconomics[0] && KI.BasicEconomicsList.BasicEconomics[0].ProfitLoss) ? KI.BasicEconomicsList.BasicEconomics[0].ProfitLoss : -1, // Zisk/ztráta
                _cribis_TotalAssets: (KI.BasicEconomicsList && KI.BasicEconomicsList.BasicEconomics && KI.BasicEconomicsList.BasicEconomics[0] && KI.BasicEconomicsList.BasicEconomics[0].TotalAssets) ? KI.BasicEconomicsList.BasicEconomics[0].TotalAssets : -1, // Základní kapitál
				_cribis_TurnoverRange: (KI.TurnoverRangeList && KI.TurnoverRangeList.TurnoverRange[0] && KI.TurnoverRangeList.TurnoverRange[0].Value) ? "'" + KI.TurnoverRangeList.TurnoverRange[0].Value + "'" : -1, // Kategorie obratu

                _cribis_MainNACE: (CI.MainNACE) ? "'" + CI.MainNACE.Code + ' - ' + CI.MainNACE.Description + "'" : "''", // NACE
                _cribis_MainOKEC: (CI.MainOkec) ? "'" + CI.MainOkec.Code + ' - ' + CI.MainOkec.Description + "'" : "''", // OKEČ


                _cribis_EmployeesRange: "'" + employees + "'", // zaměstnanci
                _cribis_RegisteredCapital: (KI.RegisteredCapital) ? KI.RegisteredCapital : -1





"""