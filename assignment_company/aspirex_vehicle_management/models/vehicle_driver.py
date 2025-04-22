from odoo import api, fields, models,_

class VehicleDriver(models.Model):
    _name='vehicle.driver'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Vehicle Driver'

    vehicle_id = fields.Many2one(comodel_name='vehicle.vehicle',string='Vehicle id')
    name = fields.Char(string='Driver Name',required=True)
    age = fields.Integer(string='Age')
    mobile = fields.Char(string='Mobile',required=True)
    email = fields.Char(string='Email',required=True)

