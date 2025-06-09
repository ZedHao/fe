import argparse
import os
import sys

current_file_path = os.path.abspath(__file__)  # 获取当前文件的绝对路径
current_dir = os.path.dirname(current_file_path)  # 获取当前文件所在的目录
parent_dir = os.path.dirname(current_dir)  # 获取当前目录的父目录
sys.path.insert(0, current_dir)
sys.path.insert(1, parent_dir)
# if current_dir not in sys.path:
# sys.path.insert(0, current_dir)
# if parent_dir not in sys.path:
# sys.path.insert(0, parent_dir)


###############################################################################################

import helper_logger
import service_account_header

import service_account_evm_storage
import service_galxe

import service_account_evm

from loguru import logger

import encode_decode



@logger.catch
def main(account_list: list, campaign_list: list):

    all_accounts_evm_map = service_account_evm_storage.ServiceAccountEVMStorage().get_all_accounts_evm_map()
    all_account_header_map = service_account_header.ServiceAccountHeader().get_all_accounts_map()

    # cur_password = helper_get_password.get_password()
    cur_password = "Android123!"

    for account_idx, cur_account_name in enumerate(account_list):
        logger.warning(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.warning(f"!!!!!!!!!!!!!! 开始一个账号 account_idx({account_idx}) cur_account_name({cur_account_name})!!!!!!!")
        logger.warning(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        for campaign_list_idx, cur_campaign_str in enumerate(campaign_list):
            logger.warning(f"###########################################################################################")
            logger.warning(f"############# 开始一个任务 cur_campaign_str({cur_campaign_str}) #############################")
            logger.warning(f"###########################################################################################")

            const_new_event = cur_campaign_str
            campaign_id = cur_campaign_str.split("/")[1]
            logger.info(f"main start campaign_list_idx({campaign_list_idx}) cur_campaign_str({cur_campaign_str}) campaign_id({campaign_id})")

            cur_account = all_accounts_evm_map[cur_account_name]
            logger.info(f"main account_idx({account_idx}) one_account_info={cur_account.name} campaign_id({campaign_id})")

            if cur_account_name in all_account_header_map:
                cur_header = all_account_header_map[cur_account_name]
            else:
                raise Exception(f"main 没有找到对应的header cur_account_name({cur_account_name}) campaign_id({campaign_id})")

            cur_account = service_account_evm.Account(account_name=cur_account.name,
                                                      private_key=encode_decode.decode(cur_password, cur_account.private_key),
                                                      cur_header=cur_header
                                                      )
            logger.info(f"main account_idx({account_idx}) new一个号 one_account_info={cur_account.log_info()} campaign_id({campaign_id})")

            cur_ServiceGalxe = service_galxe.get_service_instance(cur_account)
            is_already_claimed_campaign = cur_ServiceGalxe.already_claimed_campaign(campaign_id)
            logger.success(f'is_already_claimed_campaign({is_already_claimed_campaign}) campaign_id({campaign_id}) cur_account_name({cur_account_name})')


def get_account_list(args) -> list:
    galxe_kyc_list_v1 = [
        "F01",
        "F02",
        "F03",
        "F04",
        "F05",
        "F06",
        "F07",
        "F08",
        "F09",
        "F10",
        "ZHU01",
        "ZHU02",
        "ZHU03",
        "ZHU04",
        "ZHU05",
        "ZHU06",
        "ZHU07",
        "ZHU08",
        "ZHU09",
        "ZHU10",
        "ZHU11",
        "ZHU12",
        "ZHU13",
        "ZHU14",

    ]

    ret = galxe_kyc_list_v1

    # 指定一个账号
    if args is not None and args.account_name is not None and len(args.account_name) != 0:
        ret = [args.account_name]

    return ret


def get_campaign_list() -> list:
    ret = [
        'Razor/GCFAttvPoC'
    ]

    return ret


if __name__ == '__main__':
    helper_logger.init_logger(os.path.splitext(os.path.basename(__file__))[0])

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--account_name', type=str, help='指定账户')
    args = parser.parse_args()
    logger.info(f'args({args})')

    account_list = get_account_list(args)
    campaign_list = get_campaign_list()

    main(account_list, campaign_list)
