import logging

logger = logging.getLogger(__name__)

proboscis_mapper = {
  'dev': 'https://qa.local:9090',
  'qa': 'https://proboscis.delium.dev/api',
  'prod': 'https://proboscis.delium.io/api'
}


dcove_mapper = {
  'dev': 'http://localhost:7777',
  'qa': 'https://dcove.delium.dev',
  'prod': 'https://dcove.delium.io'
}


def get_envir(cr):
  cr.execute("""SELECT envir FROM delium_environment""")
  env_dict = cr.dictfetchone()
  if env_dict is None:
    return 'dev'
  return env_dict['envir']