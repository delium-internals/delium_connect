import requests

import json
from odoo import *


class Subscription(models.Model):
  _name = "delium.subscription"
  _description = "Subscribe to Delium's The Miner"

  # default fields. not to be shown on form
  licensed_products = fields.Char(string="licensed_products", required=True, default='The Eye', readonly=True)
  vendor_name = fields.Char(string="vendor_name", required=True, default='odoo', readonly=True)
  product_name = fields.Char(string="product_name", required=True, default='odoo', readonly=True)
  use_internal_auth = fields.Char(string="use_internal_auth", required=True, default=True, readonly=True)
  licensing_stores = fields.Char(string="licensing_stores", required=True, default='["*"]', readonly=True)
  env = fields.Char(string="env", required=True, default="prod", selection=[('dev', 'dev'), ('qa', 'qa'), ('prod', 'prod')])

  # Filled on response
  domain = fields.Char(string="domain", readonly=True)
  api_token = fields.Char(string="api_token", readonly=True)
  otp_validated = fields.Char(string="otp_validated", default=False, readonly=True)
  otp_input = fields.Char(string="otp_input")

  external_client_id = fields.Char(string="external_client_id", required=True)
  name = fields.Char(string="name", required=True)
  vertical = fields.Char(string="vertical", required=True, selection=[('cpg', 'CPG'), ('cdit', 'CDIT')])
  country = fields.Char(string="country", required=True)
  user_name = fields.Char(string="user_name", required=True)
  user_phone = fields.Char(string="user_phone", required=True)
  user_email = fields.Char(string="user_email", required=True)
  billing_address = fields.Char(string="billing_address", required=True)
  billing_number = fields.Char(string="billing_number", required=True)
  billing_email = fields.Char(string="billing_email", required=True)
  tax_name = fields.Char(string="tax_name", required=True)
  gst_no = fields.Char(string="gst_no", required=True)

  proboscis_host = fields.Char(string="Proboscis Host")

  @api.onchange('env')
  def _onchange_env(self):
    """Update the proboscis_host field based on the environment selection."""
    if self.env == 'dev':
      self.proboscis_host = 'https://qa.local:9090'
    elif self.env == 'qa':
      self.proboscis_host = 'https://proboscis.delium.dev/api'
    elif self.env == 'prod':
      self.proboscis_host = 'https://proboscis.delium.io/api'


  def prepare_request_body(self):
      return {
        "name": self.name,
        "country": self.country.upper(),
        "licensedProducts": self.licensed_products,
        "productName": self.product_name,
        "vendorName": self.vendor_name,
        "vertical": self.vertical,
        "useInternalAuth": self.use_internal_auth,
        "userName": self.user_name,
        "userPhone": self.user_phone,
        "userEmail": self.user_email,
        "externalClientId": self.external_client_id,
        "countryCode": self.country[:2].upper(),
        "licensingStores": self.licensing_stores,
        "billingAddress": self.billing_address,
        "billingNumber": self.billing_number,
        "billingEmail": self.billing_email,
        "taxName": self.tax_name,
        "gstNo": self.gst_no
      }

  @api.model
  def create(self, vals):
    request_body = self.prepare_request_body()
    headers = {'Content-Type': 'application/json'}
    logger.info()
    res = requests.get(f"{self.proboscis_host}/ext/ephemeral_client/create", verify=False, data=json.dumps(request_body), headers=headers)
    if res.status_code == 200:
      self.env['ir.actions.client'].notify({
        'title': f'Subsciption request recorded. Verification Pending',
        'message': f'Please check your email {self.user_email} for the OTP. Upon verification, your subscription will be complete.',
        'type': 'info',
      })
      response_body = res.json()
      vals['domain'] = response_body['domain']
      vals['otp_validated'] = False
      self.env['ir.actions.client'].reload()
    else:
      return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
          'title': 'Subsciption request failed.',
          'message': 'Please contact support for help.',
          'type': 'danger',
        }
      }
    return super(Subscription, self).create(vals)

  @api.model
  def write(self, vals):
    request_body = self.prepare_request_body()
    headers = {'Content-Type': 'application/json'}
    res = requests.get(f"{self.proboscis_host}/ext/ephemeral_client/create", verify=False, data=json.dumps(request_body), headers=headers)
    if res.status_code == 200:
      response_body = res.json()
      self.env['ir.actions.client'].notify({
        'title': f'Welcome back. Thank you for subscribing again. Verification is pending',
        'message': f'Please check your email {self.user_email} for the OTP. Upon verification, your subscription will be complete.',
        'type': 'info',
      })
      vals['domain'] = response_body['domain']
      vals['otp_validated'] = False
      self.env['ir.actions.client'].reload()
    else:
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
    return super(Subscription, self).write(vals)

  def resend_otp(self):
    res = requests.get(f"{self.proboscis_host}/ext/ephemeral_client/${self.domain}/{self.user_phone}/resend_otp", verify=False)
    if res.status_code == 200:
      return {
          'type': 'ir.actions.client',
          'tag': 'display_notification',
          'params': {
            'title': f'OTP Sent to your email {self.user_email}',
            'message': 'Please check your email for the OTP',
            'type': 'info',
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
    request_body = self.prepare_request_body()
    headers = {'Content-Type': 'application/json'}
    res = requests.get(f"{self.proboscis_host}/ext/ephemeral_client/{self.domain}/{self.user_phone}/{self.otp_input}", verify=False, data=json.dumps(request_body), headers=headers)
    if res.status_code == 200:
      response_body = res.json()
      self.api_token = response_body['apiToken']
      # There's no need to explicitly call self.save() unless you want to force a save immediately.
      self.save()
      return {
        'type': 'ir.actions.client',
        'tag': 'reload',
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

