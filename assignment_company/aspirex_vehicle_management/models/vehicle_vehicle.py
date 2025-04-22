from odoo import models, fields, api, _
from datetime import datetime  #  Import datetime


class VehicleVehicle(models.Model):
    _name = 'vehicle.vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # chatter
    _description = 'Vehicle Information'
    #_order = 'priority asc'

    active = fields.Boolean(string='Active', default=True)  # for archive
    vehicleid = fields.Char(string='Vehicle id', tracking=True, reqired=True, default='New', readonly=True)
    name = fields.Char(string='Vehicle Name', required=True, tracking=True)
    license_plate = fields.Char(string='License Plate', tracking=True)
    brand = fields.Char(string='Brand', tracking=True,help="Select brand")
    model = fields.Char(string='Model', tracking=True, help="select model")
    year = fields.Char(string='Manufacture Year', tracking=True)  # when I use Integer -> 2,013
    register_year = fields.Char(string='Register Year', tracking=True)
    owner_id = fields.Many2one(comodel_name='year.year', string='Owner Id', tracking=True)
    # This means that each record in the vehicle.vehicle model can be linked to a single record in
    # year.year model
    # An owner can own multiple vehicles,
    # but each vehicle has only one owner at a time
    purchase_date = fields.Datetime(string='Purchase Date & Time', tracking=True)
    fuel_type = fields.Selection(
        selection=[
            ('petrol', 'Petrol'),  # value member(we use this usually (database name), display member
            ('diesel', 'Diesel'),
            ('electric', 'Electric'),
            ('hybrid', 'Hybrid'),
            ('cng', 'CNG')
        ],
        string="Fuel Type", tracking= True
        # required=True
    )
    priority1 = fields.Selection([
        ('0', 'Low'),
        ('1', 'Urgent'),
        ], string=' ')

    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancelled')], string='Status',
                          tracking=True, default='draft')
    currency_id=fields.Many2one('res.currency',string='Currency Type', tracking=True)
    course_fee = fields.Monetary(string='Amount', tracking=True)
    remark = fields.Html(string='Remarks', tracking=True)
    is_leave = fields.Boolean(string='Booking Status', defualt=False, tracking=True)
    location = fields.Selection([
        ('personal', 'Personal'),
        ('official', 'Official'),
        ('rental', 'Rental')
    ], string='Usage Type', help="Select usage type like personal,official and rental", tracking=True)
    lecturer_id = fields.Many2one('res.users', string = "Owner Name")

    year_code = fields.Char(related='owner_id.short_code', string="NIC", store=True)
    city_name = fields.Char(string='Vehicle Type')
    vehicle_age = fields.Integer(string='Age of the Vehicle', compute='_compute_age')
    image = fields.Image(string='Image', max_width=1024, max_height=1024)

    license = fields.Binary(string='License')
    license_file_name = fields.Char(string='License File Name')
    vehicle_tags_ids = fields.Many2many('vehicle.tags', string='Tags')

    vehicle_vehicle_ids = fields.One2many('vehicle.driver', 'vehicle_id', string='Drivers')

    # _ in the function meaning private function
    @api.onchange('location')
    def _onchange_city_name(self):
        for rec in self:
            rec.city_name= rec.location

    @api.depends('year')
    def _compute_age(self):
        current_year = datetime.now().year
        for rec in self:
            if rec.year:
                try:
                    rec.vehicle_age = current_year - int(rec.year)
                except ValueError:
                    # If `rec.year` is not a valid integer, set vehicle_age to 0 or another default value
                    rec.vehicle_age = 0
            else:
                rec.vehicle_age = 0  # Default value if year is missing

    def action_confirm(self):
        for rec in self: # loop through each record in 'self' (which is usually a recordset
            if rec.state == 'draft': # check if the current state is 'draft'
                rec.state = 'confirm'# change the state to 'confirm'
    def action_cancel(self):
        for rec in self:
            if not rec.state == 'cancel': # If the record is not already 'cancel'
                rec.state = 'cancel'

     # create function (one of the CRUD operations)

    @api.model_create_multi # multiple records
    def create(self, value_list): # value_list -> fields values
        for vals in value_list:
            vals['vehicleid'] = self.env['ir.sequence'].next_by_code('vehicle.sequence') or 'New'
        res = super(VehicleVehicle, self).create(value_list)
        return res

    def write(self, valus):
        res = super(VehicleVehicle, self).write(valus)
        return res

