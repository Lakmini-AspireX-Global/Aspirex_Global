from odoo import api, fields, models, _


class ManufacturerPartNumber(models.Model):
    _name = 'manufacturer.part.number'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Manufacturer part number for the product'

    name = fields.Char(string='Manufacturer Part Number', required=True)
