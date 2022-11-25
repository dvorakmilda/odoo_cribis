{
    'name': 'O4 CRIBIS BRIDGE',
    'version': '14.0.1.1.0',
    "sequence": 1,
    'category': 'Partners',
    'summary': 'Adds information from CRIBIS service',
    'website': 'https://www.optimal4.cz',
    'author': 'Optimal4',
    'company': 'Optimal4',
    'description': """
CRIBIS BRIDGE
=================
- Company information from CRIBIS database.

For more information about service and revenew contact info@cribis.cz or visit https://www.cribis.cz

For more information about plugin contact info@optimal4.cz or visit https://www.optimal4.cz

Main functions:
    Get Micro Report
    Set Monitoring
    Get Monitoring
    Company account status
    Company relations new window view
    """,
    'images': [],
    'depends': ['contacts','l10n_cz', 'ks_percent_field',

    ],
    'demo': [
    ],

    'data': [ 'views/res_company_views.xml',
             'views/res_partner_views.xml',
    ],

    'external_dependencies': {'python': ['ares_util', 'xmltodict', 'requests', 'xml']},
    'installable': True,
    'auto_install': False,
    'application': False,
    'licence': ''
}
