# -*- coding: utf-8 -*-
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    indv_receipt_unit_price_no_vat = fields.Boolean(
        string="Individual Ticket: Unit Price (excl. VAT)",
        default=False,
        help=(
            "Show the unit price without VAT in the right column of each "
            "individual product ticket."
        ),
    )
    indv_receipt_unit_price_with_vat = fields.Boolean(
        string="Individual Ticket: Unit Price (VAT incl.)",
        default=False,
        help=(
            "Show the unit price without VAT plus a VAT line and the total "
            "price with VAT included on each individual product ticket."
        ),
    )

    def _load_pos_data(self, data):
        """Inject individual-receipt price flags into the POS config payload."""
        result = super()._load_pos_data(data)
        if result.get("data"):
            config = self.env["pos.config"].browse(result["data"][0]["id"])
            result["data"][0]["indv_receipt_unit_price_no_vat"] = (
                config.indv_receipt_unit_price_no_vat
            )
            result["data"][0]["indv_receipt_unit_price_with_vat"] = (
                config.indv_receipt_unit_price_with_vat
            )
        return result
