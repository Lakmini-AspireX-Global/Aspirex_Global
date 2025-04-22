from odoo import models, fields, _

class YearYear(models.Model):
    _name = 'year.year'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Year'
    _order = 'priority desc'

    priority = fields.Selection([
        ('0','Normal'),
        ('1','Low'),
        ('2','High'),
        ('3','Very High')], string='Priority')
    name = fields.Char(string='Owner Id')
    short_code = fields.Char(string='NIC')