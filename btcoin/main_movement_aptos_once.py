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


@logger.catch
async def main(execute_plan_account_and_campaign):
    cur_service_account_record_v2 = service_account_record_v2.ServiceAccountRecordV2()

    all_accounts_aptos_map = service_account_aptos_storage.get_all_accounts_aptos_map()

    all_accounts_evm_map= service_account_evm_storage.get_all_accounts_evm_map()


    cur_ServiceAccountHeader = service_account_header.ServiceAccountHeader()
    all_account_header_map = cur_ServiceAccountHeader.get_all_accounts_map()
    cur_ServiceAccountHeader.close()


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
        cur_account_aptos = service_account_aptos.ServiceAccountAptos(account_name=cur_account_aptos_storage.name,
                                                                      private_key=encode_decode.decode(cur_password, cur_account_aptos_storage.private_key),
                                                                      chain_config=rpc_config.MovementAptosTestNetV2ChainConfig,
                                                                      )

        cur_ServiceGalxe = service_galxe.get_service_instance(cur_account_evm)

        return cur_account_aptos, cur_ServiceGalxe

    if cur_service_account_record_v2.is_exist_for_all_account_all_event(
            [tmp[0] for tmp in execute_plan_account_and_campaign],
            [tmp[1] for tmp in execute_plan_account_and_campaign],
    ):
        logger.warning(f"main 所有账号的所有任务都已经完成了，不需要再做了")
        return

    # cur_password = helper_get_password.get_password()
    cur_password = "Android123!"

    success_account_count = 0
    for account_idx, (cur_account_name, cur_todo_campaign_list) in enumerate(execute_plan_account_and_campaign):
        logger.warning(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.warning(f"!!!!!!!!!!!! 开始一个账号 cur_account_name({cur_account_name})  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.warning(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        for campaign_list_idx, const_new_event in enumerate(cur_todo_campaign_list):
            logger.warning(f"########################################################################################")
            logger.warning(f"## 开始一个任务 cur_account_name({cur_account_name}) const_new_event({const_new_event}) ##############")
            logger.warning(f"########################################################################################")

            cur_account_aptos, cur_ServiceGalxe = get_service_instance(cur_account_name)


            try:
                did_online = await  cur_ServiceGalxe.galxe_aptos_dispatcher(const_new_event, cur_account_aptos)
            except  Exception as e:
                # 仅仅记录日志，不要处理
                logger.critical(f"{cur_account_aptos.aptos_log_account_name()} 完成const_new_event({const_new_event})这个任务失败 e({e})")
                raise

            if did_online:

                success_account_count = success_account_count + 1

                helper_sleep.wait_with_wide_range(30, 90, "每1个任务之间")

                if success_account_count % 6 == 0:
                    helper_sleep.wait_a_bit(3 * 60, "每6个任务之间，多等等")
