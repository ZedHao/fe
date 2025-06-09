import service_galxe
import service_account_evm

import helper_sleep
from loguru import logger

import helper_logger
import encode_decode

import service_account_evm_storage


def get_evm_account():
    password = "!"
    cur_service = service_account_evm_storage.EVMAccountManager()
    evm_account_list = cur_service.get_gits_accounts()

    ret = []

    for evm_account in evm_account_list:
        ret.append(
            {"name": evm_account.name,
             "address": evm_account.address,
             "mnemonic": encode_decode.decode(password, evm_account.mnemonic),
             "private_key": encode_decode.decode(password, evm_account.private_key)})

    return ret


import service_account_twitter


def get_twitter_account():
    ret = dict()
    cur_service = service_account_twitter.ServiceAccountTwitter()
    account_twitter_list = cur_service.get_all_account_twitter()
    for account_twitter in account_twitter_list:
        ret[account_twitter.account_name] = {"auth_token": account_twitter.auth_token}

    return ret


import service_account_record

if __name__ == '__main__':

    helper_logger.init_logger()

    evm_account_list = get_evm_account()
    twitter_account_map = get_twitter_account()

    cur_service_account_record = service_account_record.ServiceAccountRecord()
    const_event_bind_twitter = "绑定推特"

    for evm_account in evm_account_list:
        name = evm_account["name"]
        address = evm_account["address"]
        mnemonic = evm_account["mnemonic"]
        private_key = evm_account["private_key"]
        logger.info(f'开始一个新的号!!! name={name} address={address}')

        if name not in twitter_account_map:
            logger.warning(f'还没给这个号买推特 跳过就行 name={name} address={address}')
            continue

        auth_token = twitter_account_map[name]["auth_token"]
        logger.info(f'看看auth_token name={name} auth_token={auth_token}')

        event_exists = cur_service_account_record.event_exists(account_name=name, event_to_check=const_event_bind_twitter)
        if event_exists:
            logger.info(f'用户已绑定推特，skip name={name} address={address}')
            continue

        cur_account = account.Account(account_name=name,
                                      address=address,
                                      private_key=private_key,
                                      twitter_auth_token=auth_token,
                                      )

        cur_service_galxe = service_galxe.ServiceGalxe(cur_account)




        if cur_service_galxe.link_twitter():

            logger.success(f'用户绑定推特成功 name={name} address={address}')
            cur_service_account_record.append_event(account_name=name, new_event=const_event_bind_twitter)
            helper_sleep.sleep_wrap(10, 'for循环间隔10秒')

