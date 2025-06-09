import asyncio
import os
import sys

import helper_random

current_file_path = os.path.abspath(__file__)  # 获取当前文件的绝对路径
current_dir = os.path.dirname(current_file_path)  # 获取当前文件所在的目录
parent_dir = os.path.dirname(current_dir)  # 获取当前目录的父目录
sys.path.insert(0, current_dir)
sys.path.insert(1, parent_dir)

###############################################################################################

import helper_logger
from loguru import  logger

import main_movement_aptos_once


def get_account_list(args)->list:


    galxe_kyc_list_v2 = [
        "F01",
        "F08",
        "F07",
        "F06",
        "ZHU03",
    ]
    ret = galxe_kyc_list_v2

    # 指定一个账号
    if args is not None and args.account_name is not None and len(args.account_name) != 0:
        ret = [args.account_name]

    return  ret

def get_campaign_list()->list:
    ret= ['tx_25_times']
    return ret




if __name__ == '__main__':
    helper_logger.init_logger(os.path.splitext(os.path.basename(__file__))[0])


    account_list = get_account_list(None)
    campaign_list = get_campaign_list()
    execute_plan=helper_random.build_execute_plan(account_list,campaign_list,is_random_account=True,is_group_campaign=False)
    for account_idx, (cur_account_name, quiz_campaign_list) in enumerate(execute_plan):
        logger.warning(f"前置打印所有的执行计划 account_idx({account_idx}) cur_account_name({cur_account_name}) quiz_campaign_list={quiz_campaign_list}")



    asyncio.run(main_movement_aptos_once.main(execute_plan))
