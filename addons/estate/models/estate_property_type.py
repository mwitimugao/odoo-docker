# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Muri Estate Property Types"
    _order = "sequence, name, id"

    name = fields.Char(
        string='Property Type',
        required=True)
    property_ids = fields.One2many("estate.property", "property_type_id")
    sequence = fields.Integer('Sequence', default=1,
                              help="Used to order property types. Frequently used ones first is better")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id", string="Offers")
    offer_count = fields.Integer(string="Offer Count", compute="_compute_property_offer_count")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The property type already exists')
    ]

    @api.depends("offer_ids")
    def _compute_property_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    def action_view_offers(self):
        #todo
        return
