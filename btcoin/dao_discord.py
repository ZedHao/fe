from loguru import logger
from urllib.parse import urlparse, parse_qs

import helper_session
import helper_json


class DaoDiscord:
    def __init__(self, proxy: str, header: dict = None):
        self.__session = helper_session.new_session(proxy=proxy, header=header)

    # 银河
    def get_galxe_verify_token(self, address_evm_prefix_and_lower, state, discord_token):
        DISCORD_AUTH_URL = 'https://discord.com/api/v9/oauth2/authorize'
        GALXE_DISCORD_CLIENT_ID = '947863296789323776'

        params = {
            # 还有个固定参数
            'client_id': GALXE_DISCORD_CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': 'https://galxe.com',
            'scope': 'identify guilds guilds.members.read',
            'state': f'Discord_Auth,{address_evm_prefix_and_lower},false,{state}',
            #    TODO 银河格式的地址
        }
        body = {
            'permissions': '0',
            'authorize': True,
            'integration_type': 0,
            "location_context": {"guild_id": "10000", "channel_id": "10000", "channel_type": 10000},
        }

        headers = {'Authorization': discord_token}

        resp = self.__session.post(DISCORD_AUTH_URL, params=params, json=body, headers=headers).json()
        logger.info(f'DaoDiscord get_galxe_verify_token params={helper_json.helper_json(params)} body={helper_json.helper_json(body)} resp={helper_json.helper_json(resp)}')
        location = resp['location']

        def get_query_param(url: str, name: str):
            values = parse_qs(urlparse(url).query).get(name)
            if values:
                return values[0]
            return None

        token = get_query_param(location, 'code')

        logger.info(f'DaoDiscord get_galxe_verify_token token={token} location={location}')
        return token
