# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose pos_indv_receipt fields on the POS Settings page.

    Odoo's POS Settings form (res.config.settings) reads and writes
    pos.config fields through ``related`` proxies prefixed with ``pos_``.
    Declaring them here makes the fields available in that view.
    """

    _inherit = "res.config.settings"

    pos_indv_receipt_unit_price_no_vat = fields.Boolean(
        related="pos_config_id.indv_receipt_unit_price_no_vat", readonly=False
    )
    pos_indv_receipt_unit_price_with_vat = fields.Boolean(
        related="pos_config_id.indv_receipt_unit_price_with_vat", readonly=False
    )
