
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _name = _inherit

    @api.model
    def create(self, vals):
        partner_type = self._context.get('res_partner_search_mode')

        if partner_type == 'customer':
            vals['ref'] = self.env['ir.sequence'].next_by_code('mt.auto.customer.ref')

        return super(ResPartner, self).create(vals)