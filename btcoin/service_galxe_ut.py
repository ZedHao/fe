import os

import helper_get_password
import helper_json
import helper_logger

import service_account_evm
import service_account_header
import service_account_twitter


import encode_decode
import service_galxe
from loguru import logger


# notice 链接推特成功！
def ut_link_twitter():
    helper_logger.init_logger(os.path.splitext(os.path.basename(__file__))[0])

    # 从db读一个元素出来 new account实例
    password = "!"
    cur_service = service_account_evm.EVMAccountManager()
    one_account_info = cur_service.get_account_by_name('GIT01')

    one_account_info_decode = {
        "name": one_account_info.name,
        "address": one_account_info.address,
        "mnemonic": encode_decode.decode(password, one_account_info.mnemonic),
        "private_key": encode_decode.decode(password, one_account_info.private_key)}

    logger.info(f"one_account_info_decode={one_account_info_decode.get('name')}")

    cur_account = service_account_evm.Account(account_name=one_account_info_decode["name"],
                                  address=one_account_info_decode["address"],
                                  private_key=one_account_info_decode["private_key"],
                                  twitter_auth_token='52e16f4bf99d0fd584df4097e2f313d7f67494a2'

                                  )

    cur_ServiceGalxe = service_galxe.ServiceGalxe(cur_account)

    cur_ServiceGalxe.link_twitter()


# notice 链接dc失败并且放弃了
def ut_link_discord():
    helper_logger.init_logger()

    # 从db读一个元素出来 new account实例
    password = "!"
    cur_service = service_account_evm.EVMAccountManager()
    one_account_info = cur_service.get_account_by_name('GIT01')

    one_account_info_decode = {
        "name": one_account_info.name,
        "address": one_account_info.address,
        "mnemonic": encode_decode.decode(password, one_account_info.mnemonic),
        "private_key": encode_decode.decode(password, one_account_info.private_key)}

    logger.info(f"one_account_info_decode={one_account_info_decode.get('name')}")

    cur_account = service_account_evm.Account(account_name=one_account_info_decode["name"],
                                  address=one_account_info_decode["address"],
                                  private_key=one_account_info_decode["private_key"],
                                  discord_token='MTI1MDUxODkyNTYzNzMyMDczOA.GI33mg.Uod5n4bJg3P4XcvbEAT1-5O7s4gdLlbFVMa33k'

                                  )

    cur_ServiceGalxe = service_galxe.ServiceGalxe(cur_account)

    """
    使用Android设备注册 | 全球随机IP | 短信已验证 | 邮箱已验证 | 随机头像
    账号格式：邮箱：邮箱密码：账户密码：TOKEN
    NadineKnappQrYvw1W@faunmail.com----Fvwmk.MCUNR.----9Wimdnh1JvOp2.----MTI1MDUxODkyNTYzNzMyMDczOA.GI33mg.Uod5n4bJg3P4XcvbEAT1-5O7s4gdLlbFVMa33k


    """
    cur_ServiceGalxe.link_discord()


def ut_complete_campaign():
    helper_logger.init_logger()
    account_name = "GIT05"
    cur_service_account_twitter = service_account_twitter.ServiceAccountTwitter()
    cur_account_twitter = cur_service_account_twitter.get_account_by_name(account_name)



    # 从db读一个元素出来 new account实例
    password = "!"
    cur_service_evm_account = service_account_evm.ServiceEVMAccount()
    cur_account = cur_service_evm_account.get_account_by_name_after_decode( account_name,password)

    # one_account_info_decode = {
    #     "name": one_account_info.name,
    #     "address": one_account_info.address,
    #     "mnemonic": encode_decode.decode(password, one_account_info.mnemonic),
    #     "private_key": encode_decode.decode(password, one_account_info.private_key)}

    logger.info(f"one_account_info={cur_account.name}")

    cur_account = service_account_evm.Account(account_name=cur_account.name,
                                  address=cur_account.address,
                                  private_key=cur_account.private_key,
                                  twitter_auth_token=cur_account_twitter.auth_token
                                  )

    cur_ServiceGalxe = service_galxe.ServiceGalxe(cur_account)

    # GC433ttn6N 是熊链的一次性的任务
    # https://app.galxe.com/quest/Movement/GCZkTtx9hF  这是move的每天签到50分的任务  notice  成功！！
    # https://app.galxe.com/quest/Movement/GCr62tvWhX  这是move的看网页和关注space的任务。 notice  成功！！
    # https://app.galxe.com/quest/Movement/GCBiQtgo1C  这是move的看网页，答题，推特关注，space关注的任务  notice  成功！！
    campaign_id = 'GCBiQtgo1C'
    cur_ServiceGalxe.complete_campaign(campaign_id)
    cur_ServiceGalxe.claim_campaign(campaign_id)



if __name__ == '__main__':
    pass
