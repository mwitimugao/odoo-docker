# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError, UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Muri Estate Property Offerss"
    _order = "price desc"

    price = fields.Float(string='Price')
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ], string='Status')
    partner_id = fields.Many2one("res.partner", string="Buyer", copy=False, required=True)
    property_id = fields.Many2one("estate.property", string="Property", copy=False, required=True)
    property_type_id = fields.Char(string="Property Type", compute="_compute_property_type_id", store=True)

    _sql_constraints = [
        ('check_offer_price', 'CHECK(price >= 0)',
         'The offer price of a property should be equal or greater than 0')
    ]

    def action_accept_offer(self):
        for record in self:
            for line in record.property_id.offer_ids:
                if line.status=='accepted':
                    raise ValidationError(_("an offer has already been accepted for this property"))
                    return False
            record.status = "accepted"
            record.property_id.partner_id=record.partner_id
            record.property_id.selling_price = record.price
            return True

    def action_reject_offer(self):
        for record in self:
            record.status = "refused"
            record.property_id.partner_id = False
            record.property_id.selling_price = 0.00
            return True

    @api.depends("property_id.property_type_id")
    def _compute_property_type_id(self):
        for record in self:
            record.property_type_id = record.property_id.property_type_id.id


    @api.model
    def create(self, vals):
        if vals.get("property_id") and vals.get("price"):
            prop = self.env["estate.property"].browse(vals["property_id"])
            # We check if the offer is higher than the existing offers
            if prop.offer_ids:
                max_offer = max(prop.mapped("offer_ids.price"))
                if float_compare(vals["price"], max_offer, precision_rounding=0.01) <= 0:
                    raise UserError("The offer must be higher than %.2f" % max_offer)
            prop.state = "offer_received"
        return super().create(vals)
