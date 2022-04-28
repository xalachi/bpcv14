# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["barcodes.barcode_events_mixin", "stock.move"]

    sequence = fields.Integer(string="Sequence", default=0)
    sh_inventory_barcode_scanner_is_last_scanned = fields.Boolean(
        string="Last Scanned?")

    def on_barcode_scanned(self, barcode):

        is_last_scanned = False
        sequence = 0
        warm_sound_code = ""

        if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_last_scanned_color:
            is_last_scanned = True

        if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_move_to_top:
            sequence = -1

        if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_warn_sound:
            warm_sound_code = "SH_BARCODE_SCANNER_"

        if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_auto_close_popup:
            warm_sound_code += "AUTO_CLOSE_AFTER_" + \
                str(self.env.user.company_id.sudo(
                ).sh_inventory_barcode_scanner_auto_close_popup) + "_MS&"

        # =============================
        # UPDATED CODE
        move_lines = False

        # INCOMING
        # ===================================
        if self.picking_code in ["incoming"]:
            move_lines = self.move_line_nosuggest_ids

        # OUTGOING AND TRANSFER
        # ===================================
        elif self.picking_code in ["outgoing", "internal"]:
            move_lines = self.move_line_ids

        # UPDATED CODE
        # =============================
        if self.picking_id.state not in ["confirmed", "assigned"]:
            selections = self.picking_id.fields_get()["state"]["selection"]
            value = next((v[1] for v in selections if v[0] ==
                          self.picking_id.state), self.picking_id.state)
            raise UserError(
                _(warm_sound_code + "You can not scan item in %s state.") % (value))
        elif move_lines:
            for line in move_lines:
                is_multi_barcode = self.env.user.has_group(
                    "sh_barcode_scanner_adv.group_sh_barcode_scanner_multi_barcode")
                if self.env.user.company_id.sudo().sh_inventory_barcode_scanner_type == "barcode":

                    is_match_product = False
                    if self.product_id.barcode == barcode:
                        is_match_product = True

                    if not is_match_product and self.product_id.barcode_line_ids and is_multi_barcode:
                        for barcode_line in self.product_id.barcode_line_ids:
                            if barcode_line.name == barcode:
                                is_match_product = True
                                break

                    if is_match_product:
                        similar_lines = move_lines.filtered(
                            lambda ml: ml.product_id == self.product_id)
                        len_similar_lines = len(similar_lines)
                        if len_similar_lines:
                            last_line = similar_lines[len_similar_lines - 1]
                            last_line.qty_done += 1

#                         line.qty_done += 1

                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned

                        if self.quantity_done == self.product_uom_qty + 1:
                            warning_mess = {
                                "title": _("Alert!"),
                                "message": warm_sound_code + "Becareful! Quantity exceed than initial demand!"
                            }
                            return {"warning": warning_mess}
                        break
                    else:
                        raise UserError(
                            _(warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product!"))

                elif self.env.user.company_id.sudo().sh_inventory_barcode_scanner_type == "int_ref":
                    if self.product_id.default_code == barcode:
                        similar_lines = move_lines.filtered(
                            lambda ml: ml.product_id.default_code == barcode)
                        len_similar_lines = len(similar_lines)
                        if len_similar_lines:
                            last_line = similar_lines[len_similar_lines - 1]
                            last_line.qty_done += 1
                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                        if self.quantity_done == self.product_uom_qty + 1:
                            warning_mess = {
                                "title": _("Alert!"),
                                "message": warm_sound_code + "Becareful! Quantity exceed than initial demand!"
                            }
                            return {"warning": warning_mess}
                        break
                    else:
                        raise UserError(
                            _(warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product!"))
                elif self.env.user.company_id.sudo().sh_inventory_barcode_scanner_type == "sh_qr_code":
                    if self.product_id.sh_qr_code == barcode:
                        similar_lines = move_lines.filtered(
                            lambda ml: ml.product_id.sh_qr_code == barcode)
                        len_similar_lines = len(similar_lines)
                        if len_similar_lines:
                            last_line = similar_lines[len_similar_lines - 1]
                            last_line.qty_done += 1
                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                        if self.quantity_done == self.product_uom_qty + 1:
                            warning_mess = {
                                "title": _("Alert!"),
                                "message": warm_sound_code + "Becareful! Quantity exceed than initial demand!"
                            }
                            return {"warning": warning_mess}
                        break
                    else:
                        raise UserError(
                            _(warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product!"))

                elif self.env.user.company_id.sudo().sh_inventory_barcode_scanner_type == "all":
                    is_match_product = False
                    if self.product_id.barcode == barcode or self.product_id.default_code == barcode or self.product_id.sh_qr_code == barcode:
                        is_match_product = True

                    if not is_match_product and self.product_id.barcode_line_ids and is_multi_barcode:
                        for barcode_line in self.product_id.barcode_line_ids:
                            if barcode_line.name == barcode:
                                is_match_product = True
                                break

                    if is_match_product:
                        similar_lines = move_lines.filtered(
                            lambda ml: ml.product_id == self.product_id)
                        len_similar_lines = len(similar_lines)
                        if len_similar_lines:
                            last_line = similar_lines[len_similar_lines - 1]
                            last_line.qty_done += 1

                        self.sequence = sequence
                        self.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned

                        if self.quantity_done == self.product_uom_qty + 1:
                            warning_mess = {
                                "title": _("Alert!"),
                                "message": warm_sound_code + "Becareful! Quantity exceed than initial demand!"
                            }
                            return {"warning": warning_mess}
                        break
                    else:
                        raise UserError(
                            _(warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product!"))

        else:
            raise UserError(
                _(warm_sound_code + "Pls add all product items in line than rescan."))
