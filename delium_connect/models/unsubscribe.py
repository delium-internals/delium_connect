import requests
import json

from odoo import _
from odoo import *
from odoo.addons.delium_connect.utils import *
from odoo.exceptions import ValidationError


class Unsubscribe(models.Model):
  _name = "delium.unsubscribe"
  _description = "Unsubscribe module to stop subscription to Delium"

  external_client_id = fields.Char(string="external_client_id", required=True)
  phone_for_unsubscribe = fields.Char(string="Phone Number", required=True)
  unsubscribe_otp_input = fields.Char(string="OTP")
  unsubscribe_reason = fields.Char(string="Reason", required=True)
  status = fields.Char(default="subscribed")

  def fetch_subscription_details(self):
    current_partner = self.env.user.partner_id

    self.env.cr.execute("""SELECT external_client_id, domain, api_token FROM delium_subscription """)
    subscription_dict = self.env.cr.dictfetchone()
    if subscription_dict is None:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Subscription details missing."),
        "message": _("No subscription to Delium is found."),
        "sticky": False,
        "duration": 3000
      })
      return None, None, None
    return subscription_dict['external_client_id'], subscription_dict['domain'], subscription_dict['api_token']

  def notifs_from_response(self, current_partner, res):
    if res.status_code == 200:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "success",
        "title": _("Unsubscription initiated."),
        "message": _(res.json()['message']),
        "sticky": False,
        "duration": 3000
      })
    else:
      logger.info("[delium.unsubscribe] [Create] Failed to initiate unsubscribe")
      response_body = res.json()
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Unsubscribing initiate failed."),
        "message": _(response_body['message']),
        "sticky": False,
        "duration": 3000
      })

  @api.model
  def create(self, vals):
    logger.info("[delium.unsubscribe] [Create] Running create method ...")
    current_partner = self.env.user.partner_id

    external_client_id, domain, api_token = self.fetch_subscription_details()
    self.env.cr.execute("""SELECT * FROM delium_unsubscribe """)
    result = self.env.cr.fetchone()

    if result is not None:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Unsubscribe already initiated"),
        "message": _("Retry with the existing unsubscribe entry."),
        "sticky": False,
        "duration": 3000
      })
      raise ValidationError("Already initiated. Retry with the existing unsubscribe entry.")

    if not api_token:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Subscription details missing."),
        "message": _("No valid subscription to unsubscribe from."),
        "sticky": False,
        "duration": 3000
      })
      raise ValidationError("No valid subscription to unsubscribe from.")
    else:
      vals['external_client_id'] = external_client_id
      res = self.do_initiate_unsubscribe(api_token, vals)
      self.notifs_from_response(current_partner, res)

    return super(Unsubscribe, self).create(vals)

  @api.model
  def write(self, vals):
    logger.info("[delium.unsubscribe] [Write] Running write method ...")
    current_partner = self.env.user.partner_id

    self.env.cr.execute("""SELECT * FROM delium_unsubscribe WHERE status = 'unsubscribed'""")
    result = self.env.cr.fetchone()

    if result is not None:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Already unsubscribed."),
        "message": _("Nothing to do."),
        "sticky": False,
        "duration": 3000
      })
      return

    external_client_id, domain, api_token = self.fetch_subscription_details()
    if not api_token:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Subcsription details missing."),
        "message": _("Nothing to unsubscribe from."),
        "sticky": False,
        "duration": 3000
      })

    return super(Unsubscribe, self).write(vals)

  def initiate_unsubscribe(self):
    current_partner = self.env.user.partner_id
    external_client_id, domain, api_token = self.fetch_subscription_details()
    if not api_token:
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Subscription details missing.',
          'message': 'No API token found for the subscription. Please subscribe and verify your subscription for the API token first.',
          'type': 'danger',
        }
      }

    res = self.do_initiate_unsubscribe(api_token)
    if res.status_code == 200:
      response_body = res.json()
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "success",
        "title": _('OTP sent for unsubscribing'),
        "message": _(response_body['message']),
        "sticky": False,
        "duration": 3000
      })
      self.status = "initiated"
    else:
      logger.info("[delium.unsubscribe] [UnsubscribeInitiate] Initiate unsubscribe failed.")
      response_body = res.json()
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Unsubscription request failed.',
          'message': response_body['message'],
          'type': 'danger',
        }
      }

  def do_initiate_unsubscribe(self, api_token, vals=None):
    if vals is None:
      vals = {}
    headers = {'Content-Type': 'application/json', 'X-DELIUM-API-TOKEN': api_token}
    phone_for_unsubscribe = vals.get('phone_for_unsubscribe', self.phone_for_unsubscribe)
    proboscis_host = proboscis_mapper[get_envir(self.env.cr)]
    res = requests.post(f"{proboscis_host}/ext/ephemeral_client/initiate_demote/{phone_for_unsubscribe}", verify=False, headers=headers)
    return res

  def unsubscribe(self):
    current_partner = self.env.user.partner_id
    external_client_id, domain, api_token = self.fetch_subscription_details()
    if not api_token:
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Subscription details missing.',
          'message': 'No API token found for the subscription. Please subscribe and verify your subscription for the API token first.',
          'type': 'danger',
        }
      }

    headers = {'Content-Type': 'application/json', 'X-DELIUM-API-TOKEN': api_token}
    phone_for_unsubscribe = self.phone_for_unsubscribe
    otp_for_demote = self.unsubscribe_otp_input
    proboscis_host = proboscis_mapper[get_envir(self.env.cr)]
    body = {
      "reason": self.unsubscribe_reason
    }

    res = requests.post(f"{proboscis_host}/ext/ephemeral_client/demote/{phone_for_unsubscribe}/{otp_for_demote}", verify=False, data=json.dumps(body), headers=headers)

    if res.status_code == 200:
      # Delete the sync configs
      sync_configs = self.env["delium.sync"].search([])
      headers = {'Content-Type': 'application/json', 'X-SYNC-TOKEN': vals.get('sync_token', api_token)}
      dcove_host = dcove_mapper[get_envir(self.env.cr)]
      sync_res = requests.post(f"{dcove_host}/sync_config/deregister", verify=False, headers=headers)
      if sync_res.status_code == 200:
        if sync_configs:
          sync_configs.unlink()
        # Delete the subscription details.
        subscription = self.env["delium.subscription"].search([])
        if subscription:
          subscription.unlink()
        self.status = "unsubscribed"
        return {
          'type': 'ir.actions.client',
          'tag': 'display_notification',
          'params': {
            'title': 'Unsubscription completed.',
            'message': "Sorry to see you go. Please write to us about how we can improve the product to sales@delium.co.",
            'type': 'danger',
          }
        }
      else:
        logger.info("[delium.unsubscribe] [Unsubscribe] Unsubscribe failed.")
        response_body = res.json()
        return {
          'type': 'ir.actions.client',
          'tag': 'display_notification',
          'params': {
            'title': 'Unsubscription failed.',
            'message': response_body['message'],
            'type': 'danger',
          }
        }
    else:
      logger.info("[delium.unsubscribe] [Unsubscribe] Unsubscribe failed.")
      response_body = res.json()
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Unsubscription failed.',
          'message': response_body['message'],
          'type': 'danger',
        }
      }
