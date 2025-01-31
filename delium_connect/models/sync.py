import requests
import json

from odoo import _
from odoo import *
from odoo.addons.delium_connect.utils import logger, dcove_mapper, get_envir
from odoo.exceptions import ValidationError


class Sync(models.Model):
  _name = "delium.sync"
  _description = "Sync module to sync data to Delium"

  odoo_host = fields.Char(string="Odoo Host", required=True)
  sync_token = fields.Char(string="Sync Token Given by the Delium team for integration", required=True)
  database_pass = fields.Char(string="Api Key from odoo", required=True)
  database_user = fields.Char(string="Database User", required=True)
  database_name = fields.Char(string="Database name", required=True)
  store_ids = fields.Many2many('stock.warehouse', 'odoo_sync_stores_rel', 'config_id', 'warehouse_id', string="Stores to Sync", required=True)
  allow_sync = fields.Boolean(string="Allow Sync", required=True, default=True)

  def fetch_subscription_details(self):
    current_partner = self.env.user.partner_id

    self.env.cr.execute("""SELECT external_client_id, domain, api_token FROM delium_subscription """)
    subscription_dict = self.env.cr.dictfetchone()
    if subscription_dict is None:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Subscription details missing."),
        "message": _("No subscription to Delium is found. You must first subscribe and verify it for configuring the sync."),
        "sticky": False,
        "duration": 3000
      })
      return None, None, None
    return subscription_dict['external_client_id'], subscription_dict['domain'], subscription_dict['api_token']

  def register_to_sync(self, current_partner, vals=None):
    if vals is None:
      vals = {}
    self.env.cr.execute("""SELECT warehouse_id FROM odoo_sync_stores_rel """)
    stores = [str(st[0]) for st in self.env.cr.fetchall()]
    request_body = {
      'provider': 'odoo.xml_rpc_connect',
      'odoo_url': vals.get('odoo_host', self.odoo_host),
      'db_name': vals.get('database_name', self.database_name),
      'apikey': vals.get('database_pass', self.database_pass),
      'db_user': vals.get('database_user', self.database_user),
      'stores': json.dumps(stores),
      'allow_sync': vals.get('allow_sync', self.allow_sync)
    }

    external_client_id, domain, sync_token_from_subs = self.fetch_subscription_details()
    headers = {'Content-Type': 'application/json', 'X-SYNC-TOKEN': vals.get('sync_token', sync_token_from_subs)}
    dcove_host = dcove_mapper[get_envir(self.env.cr)]
    res = requests.post(f"{dcove_host}/sync_config/register", verify=False, data=json.dumps(request_body), headers=headers)

    return res, sync_token_from_subs

  @api.model
  def read(self, fields=None, load='_classic_read'):
    records = super(Sync, self).read(fields, load)
    for res in records:
      res['database_pass'] = '*********' if res['database_pass'] is not False else ''
      res['sync_token'] = '*********'
    return records

  @api.model
  def create(self, vals):
    logger.info(f"[delium.sync] [Create] Running create...")
    current_partner = self.env.user.partner_id

    self.env.cr.execute("""SELECT * FROM delium_sync """)
    result = self.env.cr.fetchone()

    if result is not None:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Subscription already exists."),
        "message": _("You can have only one sync config."),
        "sticky": False,
        "duration": 3000
      })
      raise ValidationError("Sync config already exists. You can have only one sync config for the Miner.")


    external_client_id, domain, api_token = self.fetch_subscription_details()
    if not api_token:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Subscription details missing."),
        "message": _("No API token found for the subscription. Please subscribe and verify your subscription for the API token first."),
        "sticky": False,
        "duration": 3000
      })
      raise ValidationError("No API token found for the subscription. Please subscribe and verify your subscription for the API token.")
    else:
      vals['sync_token'] = api_token
      res, _api_token_used = self.register_to_sync(current_partner, vals)
      self.notifs_from_response(current_partner, res)

    return super(Sync, self).create(vals)

  def notifs_from_response(self, current_partner, res):
    if res.status_code == 201:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "success",
        "title": _("Sync is registered."),
        "message": _(res.json()['message']),
        "sticky": False,
        "duration": 3000
      })
    else:
      logger.info("[delium.sync] [Create] Failed to save the sync config")
      response_body = res.json()
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Sync config update failed."),
        "message": _(response_body['message']),
        "sticky": False,
        "duration": 3000
      })

  def write(self, vals):
    logger.info(f"[delium.sync] [Write] Running write...")
    current_partner = self.env.user.partner_id

    external_client_id, domain, api_token = self.fetch_subscription_details()
    if not api_token:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Subscription details missing."),
        "message": _("No API token found for the subscription. Please subscribe and verify your subscription for the API token first."),
        "sticky": False,
        "duration": 3000
      })
    else:
      vals['sync_token'] = api_token
      res, _api_token_used = self.register_to_sync(current_partner, vals)
      self.notifs_from_response(current_partner, res)

    return super(Sync, self).write(vals)

  def update_sync_config(self):
    logger.info("[delium.sync] [Update Sync Config] Updating ...")
    current_partner = self.env.user.partner_id
    response, sync_token_used = self.register_to_sync(current_partner)
    if response.status_code == 201:
      self.sync_token = sync_token_used
