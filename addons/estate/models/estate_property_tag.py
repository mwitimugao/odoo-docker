# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from odoo import fields, models



class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Muri Estate Property Tags"
    _order = "name"

    name = fields.Char(
        string='Property Tag',
        required=True)
    color = fields.Integer()
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The tag name already exists')
    ]

