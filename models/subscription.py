import requests

import json
from odoo import _
from odoo import *
from odoo.addons.odeosync.utils import logger, proboscis_mapper
from odoo.exceptions import ValidationError, UserError


class Subscription(models.Model):
  _name = "delium.subscription"
  _description = "Subscribe to Delium's The Miner"

  # default fields. not to be shown on form
  licensed_products = fields.Char(string="Licensed Products", required=True, default='The Eye', readonly=True)
  vendor_name = fields.Char(string="Vendor Name", required=True, default='odoo', readonly=True)
  product_name = fields.Char(string="Product Name", required=True, default='odoo', readonly=True)
  use_internal_auth = fields.Char(string="Use Internal Auth", required=True, default=True, readonly=True)


  # Filled on response
  domain = fields.Char(string="Domain", readonly=True)
  api_token = fields.Char(string="Api Token", readonly=True)
  otp_validated = fields.Boolean(string="Otp Validated", default=False, readonly=True)
  otp_input = fields.Char(string="OTP: ")

  external_client_id = fields.Char(string="External Client Id", required=True)
  name = fields.Char(string="Name", required=True)
  vertical = fields.Selection(string="Vertical", required=True, selection=[('CPG', 'CPG'), ('CDIT', 'CDIT')], default='CPG')
  country = fields.Selection(string="Country", required=True, selection=[('INDIA', 'INDIA')], default='INDIA')
  user_name = fields.Char(string="User Name", required=True)
  user_phone = fields.Char(string="User Phone", required=True)
  user_email = fields.Char(string="User Email", required=True)
  billing_address = fields.Char(string="Billing Address", required=True)
  billing_number = fields.Char(string="Billing Number", required=True)
  billing_email = fields.Char(string="Billing Email", required=True)
  tax_name = fields.Selection(string="Tax Name", required=True, selection=[('GST_L', 'GST_L'), ('GST_R', 'GST_R')], default='GST_L')
  gst_no = fields.Char(string="Gst No", required=True)


  def prepare_request_body(self, vals=None):
    if vals is None:
      vals = {}
    logger.info("======================")
    logger.info(f"Vals: {vals}")
    logger.info("======================")
    body = {
      "name": vals.get('name', self.name),
      "country": vals.get('country', self.country).upper(),
      "licensedProducts": [vals.get('licensed_products', self.licensed_products)],
      "productName": vals.get('product_name', self.product_name),
      "vendorName": vals.get('vendor_name', self.vendor_name),
      "vertical": vals.get('vertical', self.vertical).lower(),
      "useInternalAuth": vals.get('use_internal_auth', self.use_internal_auth),
      "userName": vals.get('user_name', self.user_name),
      "userPhone": vals.get('user_phone', self.user_phone),
      "userEmail": vals.get('user_email', self.user_email),
      "externalClientId": f"odoo{vals.get('external_client_id', self.external_client_id)}",
      "countryCode": vals.get('country', self.country)[:2].upper(),
      "licensingStores": ["*"],
      "billingAddress": vals.get('billing_address', self.billing_address),
      "billingNumber": vals.get('billing_number', self.billing_number),
      "billingEmail": vals.get('billing_email', self.billing_email),
      "taxName": vals.get('tax_name', self.tax_name),
      "gstNo": vals.get('gst_no', self.gst_no)
    }
    logger.info(f"Body: {body}")
    return body

  def get_envir(self):
    self.env.cr.execute("""SELECT envir FROM delium_environment""")
    env_dict = self.env.cr.dictfetchone()
    if env_dict is None:
      return 'dev'
    return env_dict['envir']

  def subscribe(self, vals=None):
    request_body = self.prepare_request_body(vals)
    headers = {'Content-Type': 'application/json'}
    proboscis_host = proboscis_mapper[self.get_envir()]
    res = requests.post(f"{proboscis_host}/ext/ephemeral_client/create", verify=False, data=json.dumps(request_body), headers=headers)
    return res


  @api.model
  def create(self, vals):
    logger.info("[delium.subscription] [Create] Running create method ...")
    current_partner = self.env.user.partner_id

    self.env.cr.execute("""SELECT * FROM delium_subscription """)
    result = self.env.cr.fetchone()

    if result is not None:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Subscription already exists."),
        "message": _("You can have only one subscription to the Miner."),
        "sticky": False,
        "duration": 3000
      })
      raise ValidationError("Subscription already exists. You can have only one subscription to the Miner.")

    # Set defaults
    vals['licensed_products'] = 'The Eye'
    vals['vendor_name'] = 'odoo'
    vals['product_name'] = 'odoo'
    vals['use_internal_auth'] = True

    res = self.subscribe(vals)

    if res.status_code == 200:
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "success",
        "title": _("Subsciption request recorded. Verification Pending"),
        "message": _(res.json()['message']),
        "sticky": False,
        "duration": 3000
      })
      response_body = res.json()
      logger.info("[delium.subscription] [Create] Response Body on create: ")
      logger.info(response_body)
      vals['domain'] = response_body['domain']
      vals['otp_validated'] = False

    else:
      logger.info("[delium.subscription] [Create] Subscribing to The Miner failed.")
      response_body = res.json()
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Subsciption request failed."),
        "message": _(response_body['message']),
        "sticky": False,
        "duration": 3000
      })

    return super(Subscription, self).create(vals)


  @api.model
  def write(self, vals):
    logger.info("[delium.subscription] [Write] Running write method... ")
    current_partner = self.env.user.partner_id

    # Do not allow any changes if api token or domain exists.
    self.env.cr.execute("""SELECT api_token, domain, external_client_id FROM delium_subscription """)
    db_fields = self.env.cr.fetchone()
    api_token_from_db, domain_from_db, external_client_id_from_db = db_fields
    if api_token_from_db is not None:
      logger.info("[delium.subscription] [Write] API token already exists. No more operations performed on subscription.")
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Subscription complete and verified."),
        "message": _(
          "Your subscription details are saved and verified. Edits are not allowed. Contact support to perform any changes."),
        "sticky": False,
        "duration": 3000
      })
      return

    if domain_from_db is not None:
      if vals.get('external_client_id', self.external_client_id) != self.external_client_id:
        logger.info("[delium.subscription] [Write] Already subscribed with a different external client ID. Only one subscription is allowed")
        self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
          "type": "danger",
          "title": _("Already subscribed."),
          "message": _("Already subscribed with a different external client ID. Only one subscription is allowed"),
          "sticky": False,
          "duration": 3000
        })
        return
      vals['external_client_id'] = self.external_client_id
      logger.info("[delium.subscription] [Write] Already subscribed and domain exists in DB. Exiting the write method...")
      return super(Subscription, self).write(vals)

    res = self.subscribe(vals)
    if res.status_code == 200:
      response_body = res.json()
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "success",
        "title": _('Subscription success'),
        "message": _(response_body['message']),
        "sticky": False,
        "duration": 3000
      })
      self.domain = response_body['domain']
      self.otp_validated = False
    else:
      logger.info("[delium.subscription] [Write] Subscribing to The Miner failed.")
      response_body = res.json()
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "danger",
        "title": _("Subsciption request failed."),
        "message": _(response_body['message']),
        "sticky": False,
        "duration": 3000
      })

    return super(Subscription, self).write(vals)

  def resend_otp(self):
    logger.info("[delium.subscription] [Resend OTP] Resending OTP ...")
    if self.api_token:
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Already verified',
          'message': "Your verification is already complete.",
          'type': 'danger',
        }
      }

    if not self.domain:
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Cannot Send OTP',
          'message': 'OTP for verification can be sent only after subscribing. Save the subscription details to begin the verification.',
          'type': 'danger',
        }
      }
    proboscis_host = proboscis_mapper[self.get_envir()]
    res = requests.post(f"{proboscis_host}/ext/ephemeral_client/{self.domain}/{self.user_phone}/resend_otp", verify=False)
    if res.status_code == 200:
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': f'OTP Sent to your email {self.user_email}',
          'message': 'Please check your email for the OTP',
          'type': 'success',
        }
      }
    else:
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Failed to send OTP.',
          'message': 'Please contact support.',
          'type': 'danger',
        }
      }

  def verify_otp(self):
    logger.info("[delium.subscription] [Verify OTP] Verifying OTP ...")
    if self.api_token:
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Already verified',
          'message': "Your verification is already complete.",
          'type': 'danger',
        }
      }

    if not self.domain:
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Cannot Verify OTP',
          'message': 'OTP verification can be done only after subscribing. Save the subscription details to begin the verification.',
          'type': 'danger',
        }
      }

    current_partner = self.env.user.partner_id

    self.env.cr.execute("""SELECT api_token, domain FROM delium_subscription """)
    db_fields = self.env.cr.fetchone()
    api_token_from_db, domain_from_db = db_fields
    if api_token_from_db is not None:
      logger.info("[Resubscribe] API token already exists. No more operations allowed on subscription.")
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "info",
        "title": _("Subscription & Verification complete."),
        "message": _("Your subscription is verified already."),
        "sticky": False,
        "duration": 3000
      })
      return

    request_body = self.prepare_request_body()
    headers = {'Content-Type': 'application/json'}
    proboscis_host = proboscis_mapper[self.get_envir()]
    res = requests.post(f"{proboscis_host}/ext/ephemeral_client/{self.domain}/{self.user_phone}/{self.otp_input}", verify=False, data=json.dumps(request_body), headers=headers)
    if res.status_code == 200:
      response_body = res.json()
      self.api_token = response_body['apiToken']
      self.otp_validated = True
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'OTP verification passed',
          'message': "Congratualtions ! Your subscription has been verified. You can now register for a sync.",
          'type': 'success',
        }
      }
    else:
      response_body = res.json()
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'OTP verification failed',
          'message': response_body['message'],
          'type': 'danger',
        }
      }

  def resubscribe(self):
    logger.info("[delium.subscription] [Resubscribe] Resubscribing ...")
    current_partner = self.env.user.partner_id

    self.env.cr.execute("""SELECT api_token, domain FROM delium_subscription """)
    db_fields = self.env.cr.fetchone()
    api_token_from_db, domain_from_db = db_fields
    if api_token_from_db is not None:
      logger.info("[Resubscribe] API token already exists. No more operations allowed on subscription.")
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "info",
        "title": _("No more edits allowed"),
        "message": _("Your subscription details are saved and verified. Contact support to perform any more changes."),
        "sticky": False,
        "duration": 3000
      })
      return

    if domain_from_db is not None:
      logger.info("[delium.subscription] [Resubscribe] Subscription already exists.")
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "info",
        "title": _("Already subscribed. Verification Pending"),
        "message": _("You have already subscribed. Verification is pending. Use the Resend OTP button to generate a new OTP."),
        "sticky": False,
        "duration": 3000
      })
      return

    res = self.subscribe()
    if res.status_code == 200:
      response_body = res.json()
      self.env["bus.bus"]._sendone(current_partner, "simple_notification", {
        "type": "success",
        "title": _('Subscription success'),
        "message": _(response_body['message']),
        "sticky": False,
        "duration": 3000
      })
      self.domain = response_body['domain']
      self.otp_validated = False
    else:
      logger.info("[delium.subscription] [Resubscribe] Subscribing to The Miner failed.")
      response_body = res.json()

      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Subscription request failed.',
          'message': response_body['message'],
          'type': 'danger',
        }
      }
