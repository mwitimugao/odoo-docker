# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Muri Estate Properties"
    _order = "id desc"

    name = fields.Char(string='Title', required=True, default="Unknown")
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Post Code')
    date_availability = fields.Date(string='Availability Dates', copy=False,
                                    default=fields.Date.today() + relativedelta(months=+3))
    expected_price = fields.Float(string='Expected Price', digits=(12, 0), required=True,
                                  help='The price expected for the room')
    selling_price = fields.Float(string='Selling Price', readonly=True, digits=(12, 0), copy=False,
                                 help='The price customers will be charged for the room')
    bedrooms = fields.Integer(string='Number of Bedrooms', default=2)
    living_area = fields.Integer(string='Living Area')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage', default=False)
    garden = fields.Boolean(string='Garden', default=False)
    garden_area = fields.Integer(string='Garden Area')
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
    ], string='Garden Orientation')
    last_seen = fields.Datetime("Last Seen", default=fields.Datetime.now)
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled')], default='new', string='Status', required=True)

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, default=lambda self: self.env.user)
    partner_id = fields.Many2one("res.partner", string="Buyer", copy=False)

    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    total_area = fields.Float(compute="_compute_total_area")
    best_offer = fields.Float(compute="_compute_best_offer")
    validity = fields.Integer(string='Validity', default=7)
    date_deadline = fields.Datetime(compute="_compute_date_deadline", inverse="_compute_validity")


    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0)','The expected price of a property should be equal or greater than 0'),
        ('check_selling_price', 'CHECK(selling_price >= 0)','The selling price of a property should be equal or greater than 0')
    ]

    @api.constrains('selling_price','expected_price')
    def _check_selling_price(self):
        for record in self:
            if not float_is_zero(record.selling_price, precision_digits=2):
                if float_compare(record.selling_price, (record.expected_price*0.9), precision_rounding=2) <= 0:
                    raise ValidationError("The selling price must be greater than 90% of the expected price")
                else:
                    print('Selling price is ok')
                    return True



    @api.depends("garden_area", "living_area")
    def _compute_total_area(self):
        self.total_area = self.garden_area + self.living_area

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for record in self:
            record.best_offer = max((l.price for l in record.offer_ids), default=0)

    @api.depends('validity')
    def _compute_date_deadline(self):
        if self.create_date:
            self.date_deadline = self.create_date + relativedelta(days=+self.validity)

    def _compute_validity(self):
        if self.create_date and self.date_deadline:
            self.validity = (self.date_deadline - self.create_date).days
        pass

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden == True:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = ""

    def action_set_sold(self):
        for record in self:
            if record.state == "cancelled":
                raise ValidationError(_("Cancelled properties cannot be sold"))
                return False
            else:
                record.state = "sold"
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Property is marked as sold!!',
                        'type': 'rainbow_man',
                    }
                }
                return True

    def action_set_cancel(self):
        for record in self:
            if record.state == "sold":
                raise ValidationError(_("Sold properties cannot be cancelled"))
                return False
            else:
                record.state = "cancelled"
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Property sale has been cancelled!!',
                    }
                }
                return True

    @api.ondelete(at_uninstall=False)
    def _unlink_except_new_or_cancelled(self):
        for record in self:
            if record.state not in ['new', 'cancelled']:
                raise UserError(_('You can only delete new or cancelled properties.'))


    @api.model
    def create(self, vals):
        print("Real Estate", vals)
        vals['state'] = 'offer_received'
        return super(EstateProperty, self).create(vals)