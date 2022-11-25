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

class ResPartnerCribis(models.Model):
    _name = "res.partner.cribis"
    _description = 'res.partner.cribis'

    monitor_date = fields.Datetime('monitor_date')
    business_id = fields.Integer('business_id')
    change_list = fields.Char('change_list')
