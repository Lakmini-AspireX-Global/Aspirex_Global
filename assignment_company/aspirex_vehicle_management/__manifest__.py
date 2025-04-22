{
    'name': 'Vehicle Management',
    'author': 'Aspirex (Pvt) Ltd',
    'version': '18.0.0.1',
    'summary': 'Vehicle Management',
    'description': """Vehicle Management""",
    'website': 'aspirex.com',
    'depends': [
        'base','mail', 'account', # base is a model where we are installing it
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/vehicle_vehicle_views.xml',
        'views/vehicle_vehicle_petrol_views.xml',
        'views/year_year_view.xml', # trailing comma
        'data/ir_sequence_data.xml',
        'views/vehicle_tags_views.xml',
        'views/vehicle_driver_view.xml'
    ],
    'licence': 'LGPL-3',
    'installable': True,
    'application': False,
}