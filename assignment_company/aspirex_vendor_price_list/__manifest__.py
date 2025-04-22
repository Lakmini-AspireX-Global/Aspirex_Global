{
    'name': 'Vendor Price List',
    'author': 'Aspirex (Pvt) Ltd',
    'version': '18.0.0.1',
    'summary': 'Vendor Price List',
    'description': """Vendor Price List""",
    'website': 'aspirex.com',
    'depends': [
        'base','product', 'purchase','stock',
    ],
    'data': [
        'views/product_supplierinfo_views.xml',
        'views/manufacturer_manufacturer_view.xml',
        'security/ir.model.access.csv',
        'views/manufacturer_part_number_views.xml',
        'views/purchase_order_line_view.xml',
        'views/stock_move_views.xml'

    ],
    'licence': 'LGPL-3',
    'installable': True,
    'application': False,
}