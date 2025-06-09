import argparse
import os
import sys

current_file_path = os.path.abspath(__file__)  # 获取当前文件的绝对路径
current_dir = os.path.dirname(current_file_path)  # 获取当前文件所在的目录
parent_dir = os.path.dirname(current_dir)  # 获取当前目录的父目录
sys.path.insert(0, current_dir)
sys.path.insert(1, parent_dir)

###############################################################################################
import helper_random
import main_quiz

import helper_logger

from loguru import logger

import model_campaign_list


def get_account_list(args) -> list:
    ret = [
        "ZHU40",
    ]

    # 指定一个账号
    if args is not None and args.account_name is not None and len(args.account_name) != 0:
        ret = [args.account_name]

    return ret


def get_campaign_list() -> list:
    ret = [

        'ZOTH/GCQzvtK7pS'


    ]

    return ret


if __name__ == '__main__':
    helper_logger.init_logger(os.path.splitext(os.path.basename(__file__))[0])

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--account_name', type=str, help='指定账户')
    args = parser.parse_args()
    logger.info(f'args({args})')

    account_list = get_account_list(args)
    quiz_campaign_list = get_campaign_list()

    execute_plan = helper_random.build_execute_plan(account_list, quiz_campaign_list, is_random_account=True, is_group_campaign=True)

    for account_idx, (cur_account_name, quiz_campaign_list) in enumerate(execute_plan):
        logger.warning(f"前置log所有的执行计划 account_idx({account_idx}) cur_account_name({cur_account_name}) quiz_campaign_list={quiz_campaign_list}")

    main_quiz.main(execute_plan)
