import asyncio
import os
import sys


current_file_path = os.path.abspath(__file__)  # 获取当前文件的绝对路径
current_dir = os.path.dirname(current_file_path)  # 获取当前文件所在的目录
parent_dir = os.path.dirname(current_dir)  # 获取当前目录的父目录
sys.path.insert(0, current_dir)
sys.path.insert(1, parent_dir)


###############################################################################################
import random

from loguru import logger

import helper_logger
import helper_sleep
import encode_decode
import rpc_config

import service_account_header
import service_account_record_v2
import service_galxe
import service_account_evm_storage
import service_account_evm
import service_account_aptos_storage
import service_account_aptos


# 使用 logger.catch 捕获异常并记录
# 它可以捕获未处理的异常并自动记录到日志文件中。即使程序终止，异常信息也会被记录下来。
@logger.catch
async def main(galxe_kyc_list: list[str]):

    all_accounts_aptos_map = service_account_aptos_storage.ServiceAccountAptosStorage().get_all_accounts_aptos_map()
    all_accounts_evm_map = service_account_evm_storage.ServiceAccountEVMStorage().get_all_accounts_evm_map()
    all_account_header_map = service_account_header.ServiceAccountHeader().get_all_accounts_map()

    def get_service_instance(cur_account_name) -> (service_account_aptos.ServiceAccountAptos, service_galxe.ServiceGalxe):
        logger.warning(f"echelon start cur_account_name({cur_account_name})")

        cur_account_evm_storage = all_accounts_evm_map[cur_account_name]
        logger.info(f"echelon cur_account_evm_storage={cur_account_evm_storage}")
        assert cur_account_evm_storage is not None

        cur_account_aptos_storage = all_accounts_aptos_map[cur_account_name]
        logger.info(f"echelon cur_account_aptos_storage={cur_account_aptos_storage}")
        assert cur_account_aptos_storage is not None

        cur_header = all_account_header_map[cur_account_name]
        logger.info(f"echelon cur_header={cur_header}")
        assert cur_header is not None

        cur_account_evm = service_account_evm.Account(account_name=cur_account_evm_storage.name,
                                                      private_key=encode_decode.decode(cur_password, cur_account_evm_storage.private_key),
                                                      cur_header=cur_header
                                                      )
        # notice
        # hardcode
        # update
        # TODO 
        cur_account_aptos = service_account_aptos.ServiceAccountAptos(account_name=cur_account_aptos_storage.name,
                                                                      private_key=encode_decode.decode(cur_password, cur_account_aptos_storage.private_key),
                                                                      chain_config=rpc_config.MovementAptosTestNetChainConfig,
                                                                      )

        cur_ServiceGalxe = service_galxe.get_service_instance(cur_account_evm)

        return cur_account_aptos, cur_ServiceGalxe


    # 要执行的任务
    todo_campaign_list = [

        "galxe_echelon_7_day_check",
        "galxe_meridian_7_day_check",

    ]
    random.shuffle(todo_campaign_list)

    # cur_password = helper_get_password.get_password()
    cur_password = "Android123!"

    success_account_count = 0
    for account_idx, cur_account_name in enumerate(galxe_kyc_list):
        logger.warning(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.warning(f"!!!!!!!!!!!!!!     开始一个账号     !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.warning(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        for campaign_list_idx, const_new_event in enumerate(todo_campaign_list):
            logger.warning(f"############################################################")
            logger.warning(f"#############    开始一个任务       ##########################")
            logger.warning(f"############################################################")
            cur_account_aptos, cur_ServiceGalxe = get_service_instance(cur_account_name)


            did_online = await cur_ServiceGalxe.galxe_aptos_dispatcher(const_new_event,cur_account_aptos)


            if did_online:

                helper_sleep.wait_with_wide_range(60, 70, "每1个任务之间")

                success_account_count = success_account_count + 1
                if success_account_count % 6 == 0:
                    helper_sleep.wait_a_bit(3 * 60, "每6个任务之间，多等等")


if __name__ == '__main__':
    # 获取当前文件的名称（不包含扩展名）
    helper_logger.init_logger(os.path.splitext(os.path.basename(__file__))[0])

    galxe_kyc_list = [
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

        "PY01",
        "PY02",
        "PY03",
        "ZHU15",
        "ZHU16",
        "ZHU17",
        "ZHU18",
        "ZHU19",
        # "ZHU20", #太傻逼了，一直无法领水等等吧
        "ZHU21",
        "ZHU22",
    ]
    random.shuffle(galxe_kyc_list)
    # 每次只做部分号
    # galxe_kyc_list = random.sample(galxe_kyc_list, 15)
    asyncio.run(main(galxe_kyc_list))
