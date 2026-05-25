# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose pos_json_printer fields on the POS Settings page.

    Odoo's POS Settings form (res.config.settings) reads and writes
    pos.config fields through ``related`` proxies prefixed with ``pos_``.
    Declaring them here makes the fields available in that view.
    """

    _inherit = "res.config.settings"

    pos_use_json_printer = fields.Boolean(
        related="pos_config_id.use_json_printer", readonly=False
    )
    pos_hw_proxy_json_url = fields.Char(
        related="pos_config_id.hw_proxy_json_url", readonly=False
    )
    pos_receipt_char_size = fields.Selection(
        related="pos_config_id.receipt_char_size", readonly=False
    )
