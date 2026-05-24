# -*- coding: utf-8 -*-
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    use_json_printer = fields.Boolean(
        string="JSON Printer",
        default=True,
        help=(
            "Send structured JSON to hw_proxy instead of rendering the receipt "
            "to a PNG image. Reduces serial write time from ~4.8 s to ~0.2 s."
        ),
    )
    hw_proxy_json_url = fields.Char(
        string="hw_proxy URL",
        help=(
            "URL of the hw_proxy service, e.g. http://192.168.1.100:9002. "
            "Leave blank to auto-detect (same hostname, port 9002)."
        ),
    )
    receipt_char_size = fields.Selection(
        selection=[('1', 'Normal'), ('2', 'Large')],
        string="Receipt Font Size",
        default='1',
        help="Character size for all receipt content. Use 'Large' for clients with vision issues.",
    )

    def _load_pos_data(self, data):
        """Inject custom fields into the POS session config payload."""
        result = super()._load_pos_data(data)
        if result.get('data'):
            config = self.env['pos.config'].browse(result['data'][0]['id'])
            result['data'][0]['use_json_printer'] = config.use_json_printer
            result['data'][0]['hw_proxy_json_url'] = config.hw_proxy_json_url or ''
            result['data'][0]['receipt_char_size'] = int(config.receipt_char_size or '1')
        return result
