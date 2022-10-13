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

class ResCompanyCribis(models.Model):
    _name = "res.company.cribis"
    _description = 'res.company.cribis'

    name = fields.Char(string='Account Type')
    account_type_id = fields.Integer(string='')
    valid_from = fields.Datetime(string='')
    expiration = fields.Datetime(string='')
    remaining = fields.Char(string='')
    obtained = fields.Char(string='')
    unit = fields.Char(string='')

