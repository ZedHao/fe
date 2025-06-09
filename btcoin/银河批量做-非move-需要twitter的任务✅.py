import argparse
import os
import sys
current_file_path = os.path.abspath(__file__)  # 获取当前文件的绝对路径
current_dir = os.path.dirname(current_file_path)  # 获取当前文件所在的目录
parent_dir = os.path.dirname(current_dir)  # 获取当前目录的父目录
sys.path.insert(0, current_dir)
sys.path.insert(1, parent_dir)

###############################################################################################
from loguru import logger

import helper_random
import helper_logger


import main_twitter


def get_account_list(args) -> list:
    galxe_kyc_list = [
        # "F01",
        # # "F02",
        # "F03",
        # "F04",
        # "F05",
        "F06",
        "F07",
        "F08",
        # "F09",
        # # "F10",暂时推特搞不定了，不知道为什么

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
    ret = galxe_kyc_list

    # 指定一个账号
    if args is not None and args.account_name is not None and len(args.account_name) != 0:
        ret = [args.account_name]

    return ret


def get_campaign_list() -> list:
    """
    已经完成的任务
# 2024/10/24  - 2024/11/01 20:00
# dc任务组需要3天gm，放弃
# 需要护照 BBBAC-BA
# 'Cysic/GCnwUtVMZN',


# 答题和推特，有推荐，无dc，一定做推荐 Every 3 Referral: Get 500 Points
# 'Vana/GCMintxk3n', 过期了

# 需要后续手动加dc频道
# "Aligned/GCEbHtK5DY", 过期了
    """
    ret = [
        # notice 尽快每次多跑几个任务，因为不用频繁切换推特账号，可能就不容易封号



        # 全是推特
        # 'CORN/GC5DztVtDu', 建议别脚本了，直接前端模拟
        # 'CORN/GCSqatKNRX', 建议别脚本了，直接前端模拟




        # 推特和dc，需要护照 # 低优
        # 'LagrangeLabs/GCvBgtVAeu',
        # 'LagrangeLabs/GCkp7txh6j',  建议别脚本了，直接前端模拟


        # 2024/10/29  - 2024/12/01
        # 需要后续手动加dc频道，不需要银河护照
        # 'SpaceandTimeDB/GCxwBtKJXi', # 低优




    ]
    return ret



if __name__ == '__main__':
    helper_logger.init_logger(os.path.splitext(os.path.basename(__file__))[0])

    parser = argparse.ArgumentParser(description='示例程序')
    parser.add_argument('--account_name', type=str, help='指定账户')
    args = parser.parse_args()
    logger.info(f'args({args})')

    account_list = get_account_list(args)
    campaign_list = get_campaign_list()
    execute_plan = helper_random.build_execute_plan(account_list, campaign_list,is_random_account=False,is_group_campaign=False)

    for account_idx, (cur_account_name, quiz_campaign_list) in enumerate(execute_plan):
        logger.warning(f"前置log任务配置 account_idx({account_idx}) cur_account_name({cur_account_name}) quiz_campaign_list={quiz_campaign_list}")

    main_twitter.main(execute_plan)
