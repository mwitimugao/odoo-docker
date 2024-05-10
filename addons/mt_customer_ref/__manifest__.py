{
    'name': "Auto Customer Reference",
    'version': '1.0',
    'license': 'LGPL-3',
    'depends': ['base','sale'],
    'author': "Muri Technologies",
'website': "https://www.muritechnologies.com",
    'sequence': -2001,
    'category': 'Sales',
    'description': """
    This will generate a unique customer number in the Customer Ref field in Customers
    """,
    # data files always loaded at installation
    'data': [
        'data/mt_customer_ref_sequence.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
    ],
    'application': False,
    'installable': True,
    'auto_install': False
}
