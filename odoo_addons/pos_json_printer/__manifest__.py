# -*- coding: utf-8 -*-
{
    'name': 'POS JSON Printer',
    'version': '18.0.0.12.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Send structured JSON to hw_proxy instead of a PNG image — 25× smaller payload.',
    'description': """
Replaces the default Odoo POS receipt pipeline (HTML → canvas → base64 PNG → hw_proxy)
with a direct JSON POST to the hw_proxy /print_receipt_json endpoint.

Result: ~2-4 KB payload vs ~56 KB, reducing serial write time from ~4.8 s to ~0.2 s
at 115 200 baud on a Posiflex PP6800 (or any 80 mm ESC/POS serial printer).

Configuration:
  POS Settings → Printers → Enable "JSON Printer" and set the hw_proxy URL.
  If the URL is left blank the addon defaults to the same hostname on port 9001 (Traefik hw entryPoint).
    """,
    'author': 'Eli Serra',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_config_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_json_printer/static/src/js/pos_json_printer.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
