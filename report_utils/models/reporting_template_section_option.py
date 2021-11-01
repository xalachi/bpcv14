# -*- coding: utf-8 -*-
from odoo import models, fields


def truncate_long_text(text):
    return text[:70] + (text[70:] and '...')


class ReportingCustomTemplateSectionOption(models.Model):
    _name = 'reporting.custom.template.section.option'

    report_id = fields.Many2one('reporting.custom.template')
    field_type = fields.Char(required=True, default='char')
    name_technical = fields.Char()
    name = fields.Char(string="Description")
    value_display = fields.Char(string="Value", compute="_compute_value_display")
    value_char = fields.Char()
    value_text = fields.Text()
    value_boolean = fields.Boolean()
    value_integer = fields.Integer()

    def get_value(self):
        self.ensure_one()
        if self.field_type == "char":
            return self.value_char or ""
        elif self.field_type == "text":
            return self.value_text or ""
        elif self.field_type == "boolean":
            return self.value_boolean
        elif self.field_type == "integer":
            return self.value_integer
        return "Unknown"

    def _compute_value_display(self):
        for rec in self:
            value = rec.get_value()
            if rec.field_type == "boolean":
                value = value and "Yes" or "No"
            if value and rec.field_type == "text":
                value = truncate_long_text(value)
            rec.value_display = str(value)

