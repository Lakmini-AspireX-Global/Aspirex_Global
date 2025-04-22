from odoo import api, fields, models, _


class StudentTags(models.Model):
    _name = 'vehicle.tags'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Vehicle Tags'

    name = fields.Char(string='Tag Name', required=True)
    colour = fields.Integer(string='Colour')