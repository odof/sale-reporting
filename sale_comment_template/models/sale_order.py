# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi
#    Copyright 2013-2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from odoo import models, fields, api


class SaleOrder(models.Model):
    """Add text comment"""

    _inherit = "sale.order"

    comment_template1_id = fields.Many2one('base.comment.template',
                                           string='Top Comment Template')
    comment_template2_id = fields.Many2one('base.comment.template',
                                           string='Bottom Comment Template')
    note1 = fields.Html('Top Comment')
    note2 = fields.Html('Bottom Comment')

    @api.onchange('comment_template1_id')
    def _set_note1(self):
        comment = self.comment_template1_id
        if comment:
            self.note1 = (self.note1 or '') + comment.get_value(self.partner_id.id)
            self.comment_template1_id = False

    @api.onchange('comment_template2_id')
    def _set_note2(self):
        comment = self.comment_template2_id
        if comment:
            self.note2 = (self.note2 or '') + comment.get_value(self.partner_id.id)
            self.comment_template2_id = False

    @api.multi
    def _prepare_invoice(self):
        values = super(SaleOrder, self)._prepare_invoice()
        values.update({
            'comment_template1_id': self.comment_template1_id.id,
            'comment_template2_id': self.comment_template2_id.id,
        })
        comments = self.company_id.of_keep_comments
        values.update({
            'note1': comments in (1, 2) and self.note1 or '',
            'note2': comments in (1, 3) and self.note2 or '',
            })
        return values

class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def _auto_init(self):
        """
        of_keep_comments passe de fields.Boolean à fields.Selection
        """
        cr = self._cr
        cr.execute(
            """SELECT DATA_TYPE """
            """FROM INFORMATION_SCHEMA.COLUMNS """
            """WHERE TABLE_NAME = 'res_company'"""
            """      AND COLUMN_NAME = 'of_keep_comments'""")
        type = cr.fetchall()
        company_obj = self.env['res.company']
        set_values = []
        if type and type[0][0] == 'boolean':
            for company in company_obj.search([]):
                set_values.append((company, company.of_keep_comments and 1 or 4))

        super(ResCompany, self)._auto_init()

        if set_values:
            for company, value in set_values:
                company.write({'of_keep_comments': value})

    of_keep_comments = fields.Selection(
        [(4, 'Ne pas garder les commentaires'),
         (1, 'Garder les commentaires'),
         (2, 'Garder le commentaire du haut'),
         (3, 'Garder le commentaire du bas')],
        string=u"(OF) Commentaires devis sur facture", default=1,
        help=u"Permet de récupérer les commentaires du devis sur la facture finale")

class OFSaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    of_keep_comments = fields.Selection(
        [(4, 'Ne pas garder les commentaires'),
         (1, 'Garder les commentaires'),
         (2, 'Garder le commentaire du haut'),
         (3, 'Garder le commentaire du bas')],
        string=u"(OF) Commentaires devis sur facture", default=1,
        help=u"Permet de récupérer les commentaires du devis sur la facture finale",
        related="company_id.of_keep_comments")
