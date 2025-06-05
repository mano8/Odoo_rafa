# -*- coding: utf-8 -*-
{
    'name': 'POS Indv Receipt',
    'version': '18.0.0.1.11',
    'category': 'Sales/Point of Sale',
    'summary': 'Print individual tickets for each product unit from POS receipts.',
    'description': """
This module extends the Odoo 18.0 Point of Sale functionality by allowing users
to print individual tickets for each unit of a product directly from the receipt screen.
This is particularly useful for bars, parties, or events where individual items
(like drinks or food portions) need separate vouchers or tickets.

Key Features:
- Adds a 'Print Product Tickets' button to the POS Receipt Screen.
- Displays a popup to select products from the current order.
- Prints one ticket per unit of quantity for selected products.
- Tickets use the standard POS receipt header/footer for consistency.
    """,
    'author': 'Eli Serra',
    'depends': [
        'point_of_sale'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            # PoS files
            'pos_indv_receipt/static/src/overrides/**/*',
            'pos_indv_receipt/static/src/app/**/*',
            ('after', 'point_of_sale/static/src/scss/pos.scss', 'pos_indv_receipt/static/src/scss/pos_individual_receipt.scss'),
            'web/static/lib/luxon/luxon.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
