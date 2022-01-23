import logging
import requests
import json
import re
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    whatsapp_msg_id = fields.Char('Whatsapp id')

    @api.model
    def create(self, vals):
        res = super(ProjectTask, self).create(vals)
        try:
            res.send_message_on_whatsapp()
        except Exception as e_log:
            _logger.exception("Exception in creating project task  %s:\n", str(e_log))
        return res

    def cleanhtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def convert_to_html(self, message):
        for data in re.findall(r'\*.*?\*', message):
            message = message.replace(data, "<strong>" + data.strip('*') + "</strong>")
        return message

    def send_message_on_whatsapp(self):
        Param = self.env['res.config.settings'].sudo().get_values()
        res_partner_id = self.env['res.partner'].search([('id', '=', self.user_id.partner_id.id)])
        res_user_id = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_partner_id.mobile:
            if res_partner_id.country_id.phone_code and res_partner_id.mobile:
                msg = ''
                whatsapp_msg_number = res_partner_id.mobile
                whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "")
                whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                    '+' + str(res_partner_id.country_id.phone_code), "")
                phone_exists_url = Param.get('whatsapp_endpoint') + '/checkPhone?token=' + Param.get('whatsapp_token') + '&phone=' + str(
                    res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                phone_exists_response = requests.get(phone_exists_url)
                json_response_phone_exists = json.loads(phone_exists_response.text)
                if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and json_response_phone_exists.get('result') == 'exists':
                    if self.project_id.name:
                        msg += "* " + _("Project") + ":* "+self.project_id.name
                    if self.name:
                        msg += "\n*" + _("Task name") + ":* "+self.name
                    if self.date_deadline:
                        msg+= "\n*" + _("Deadline") + ":* "+str(self.date_deadline)
                    if self.description:
                        if len(self.description) > 11:
                            msg += "\n*" + _("Description") + ":* "+self.cleanhtml(self.description)
                    msg = _("Hello") + " " + res_partner_id.name + "," + "\n" + _("New task assigned to you") + "\n" + msg
                    if res_user_id.has_group('pragmatic_odoo_whatsapp_integration.group_project_enable_signature'):
                        user_signature = self.cleanhtml(res_user_id.signature)
                        msg += "\n\n" + user_signature
                    url = Param.get('whatsapp_endpoint') + '/sendMessage?token=' + Param.get('whatsapp_token')
                    headers = {"Content-Type": "application/json" }
                    tmp_dict = {"phone": "+" + str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code, "body": msg }
                    response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                    if response.status_code == 201 or response.status_code == 200:
                        _logger.info("\nSend Message successfully")
                        response_dict = response.json()
                        self.whatsapp_msg_id = response_dict.get('id')
                        mail_message_obj = self.env['mail.message']
                        comment = "fa fa-whatsapp"
                        body_html = tools.append_content_to_html('<div class = "%s"></div>' % tools.ustr(comment), msg)
                        body_msg = self.convert_to_html(body_html)
                        if self.env['ir.config_parameter'].sudo().get_param('pragmatic_odoo_whatsapp_integration.group_project_display_chatter_message'):
                            mail_message_id = mail_message_obj.sudo().create({
                                'res_id': self.id,
                                'model': 'project.task',
                                'body': body_msg,
                            })
                else:
                    raise UserError(_('Please add valid whatsapp number for %s ') % res_partner_id.name)

    def _assigned_task_done(self):
        project_task_ids = self.env['project.task'].search([('whatsapp_msg_id', '!=', None)])
        Param = self.env['res.config.settings'].sudo().get_values()
        for project_task_id in project_task_ids:
            res_partner_id = self.env['res.partner'].search([('id', '=', project_task_id.user_id.partner_id.id)])
            whatsapp_msg_number = res_partner_id.mobile
            whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "");
            try:
                url = Param.get('whatsapp_endpoint') + '/messages?lastMessageNumber=1&last=true&chatId='+ \
                      str(res_partner_id.country_id.phone_code) +''+whatsapp_msg_number_without_space[-10:] +'@c.us&limit=100&token='+ Param.get('whatsapp_token')
                response = requests.get(url)
                if response.status_code == 201 or response.status_code == 200:
                    _logger.info("\nGet project task successfully")
                    response_dict = response.json()
                    for messages in response_dict['messages']:
                        current_whatsapp_msg_id = project_task_id.whatsapp_msg_id.partition("true_")[2].partition("_")[2]
                        if not messages['quotedMsgId'] == None and current_whatsapp_msg_id in messages['quotedMsgId']:
                            if messages['body'] == 'done' or messages['body'] == 'Done':
                                task_type_done_id = project_task_id.env['project.task.type'].search([('name', '=', 'Done')], limit=1)
                                if task_type_done_id:
                                    stage_id = project_task_id.write({'stage_id': task_type_done_id.id})
            except Exception as e_log:
                _logger.exception("Exception in updating task as done %s:\n", str(e_log))
