from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from pytz import UTC

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, get_lang
from odoo.tools.float_utils import float_compare, float_round
from odoo.exceptions import UserError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    item = fields.Integer(string='Item No', readonly=True)
    manufacturer_id = fields.Many2one(comodel_name='manufacturer.manufacturer', string='Manufacturer',
                                      help='Manufacturer of the product')
    manufacturer_part_number = fields.Many2one(comodel_name='manufacturer.part.number',
                                               string='Manufacturer Part Number',
                                               help='Part number provided by the manufacturer')
    vendor_part_number = fields.Char(string='Vendor Part Number', help='Vendor Part Number')
    vendor_part_name = fields.Char(string='Vendor Part Name', help='Vendor Part Name')
    confirm_date= fields.Datetime(string='Confirmation Delivery Date', tracking=True)
    date_planned = fields.Datetime(
        string='Requested Delivery Date ', index=True,
        compute="_compute_price_unit_and_date_planned_and_name", readonly=False, store=True,
        help="Delivery date expected from vendor. This date respectively defaults to vendor pricelist lead time then today's date.", tracking=True)

    @api.depends('product_qty', 'product_uom', 'company_id', 'order_id.partner_id')
    def _compute_price_unit_and_date_planned_and_name(self):
        for line in self:
            if not line.product_id or line.invoice_lines or not line.company_id:
                continue
            params = line._get_select_sellers_params()
            seller = line.product_id._select_seller( # seller is the record of the model of product.supplierinfo
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and line.order_id.date_order.date() or fields.Date.context_today(line),
                uom_id=line.product_uom,
                params=params)

            if seller or not line.date_planned:
                line.date_planned = line._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

            # If not seller, use the standard price. It needs a proper currency conversion.
            if not seller:
                line.discount = 0
                unavailable_seller = line.product_id.seller_ids.filtered(
                    lambda s: s.partner_id == line.order_id.partner_id)
                if not unavailable_seller and line.price_unit and line.product_uom == line._origin.product_uom:
                    # Avoid to modify the price unit if there is no price list for this partner and
                    # the line has already one to avoid to override unit price set manually.
                    continue
                po_line_uom = line.product_uom or line.product_id.uom_po_id
                price_unit = line.env['account.tax']._fix_tax_included_price_company(
                    line.product_id.uom_id._compute_price(line.product_id.standard_price, po_line_uom),
                    line.product_id.supplier_taxes_id,
                    line.taxes_id,
                    line.company_id,
                )
                price_unit = line.product_id.cost_currency_id._convert(
                    price_unit,
                    line.currency_id,
                    line.company_id,
                    line.date_order or fields.Date.context_today(line),
                    False
                )
                line.price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places,
                                                                               self.env[
                                                                                   'decimal.precision'].precision_get(
                                                                                   'Product Price')))

            elif seller:
                price_unit = line.env['account.tax']._fix_tax_included_price_company(seller.price,
                                                                                     line.product_id.supplier_taxes_id,
                                                                                     line.taxes_id,
                                                                                     line.company_id) if seller else 0.0
                price_unit = seller.currency_id._convert(price_unit, line.currency_id, line.company_id,
                                                         line.date_order or fields.Date.context_today(line), False)
                price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places,
                                                                          self.env['decimal.precision'].precision_get(
                                                                              'Product Price')))
                line.price_unit = seller.product_uom._compute_price(price_unit, line.product_uom)
                # searches for the most suitable supplierinfo record matching:
                line.discount = seller.discount or 0.0
                line.vendor_part_number = seller.product_code
                line.vendor_part_name = seller.product_name
                line.manufacturer_id = seller.manufacturer_id.id
                line.manufacturer_part_number = seller.manufacturer_part_number.id


            # record product names to avoid resetting custom descriptions
            default_names = []
            vendors = line.product_id._prepare_sellers({})
            product_ctx = {'seller_id': None, 'partner_id': None, 'lang': get_lang(line.env, line.partner_id.lang).code}
            default_names.append(line._get_product_purchase_description(line.product_id.with_context(product_ctx)))
            for vendor in vendors:
                product_ctx = {'seller_id': vendor.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                default_names.append(line._get_product_purchase_description(line.product_id.with_context(product_ctx)))
            if not line.name or line.name in default_names:
                product_ctx = {'seller_id': seller.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                line.name = line._get_product_purchase_description(line.product_id.with_context(product_ctx))

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override the create method to handle batch creation of purchase order lines.
        """
        # Create the order lines in batch
        res = super(PurchaseOrderLine, self).create(vals_list)

        # After batch creation, update line numbers for all created lines
        for line in res:
            line._update_line_numbers()

        return res

    def write(self, vals):
        """
        Override the write method to ensure the line numbers are updated
        when modifying existing records.
        """
        res = super(PurchaseOrderLine, self).write(vals)

        # Update line numbers after write operation
        self._update_line_numbers()

        return res

    def _update_line_numbers(self):
        """
        Updates the line number (item) of each purchase order line.
        This helps maintain correct sequencing of lines.
        """
        if self.order_id:
            # Sort order lines safely by create_date, handling None values
            lines = self.order_id.order_line.sorted(key=lambda r: r.create_date or datetime.min)

            for idx, line in enumerate(lines, start=1):
                if line.item != idx:
                    line.item = idx

    @api.onchange('order_id')
    def _onchange_order_id(self):
        """
        Update line numbers dynamically when the order is changed in the form view.
        """
        # Avoid updating line numbers if there's no change in the order
        if self.order_id:
            self._update_line_numbers()
