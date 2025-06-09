import asyncio
import os
import sys
current_file_path = os.path.abspath(__file__)  # 获取当前文件的绝对路径
current_dir = os.path.dirname(current_file_path)  # 获取当前文件所在的目录
parent_dir = os.path.dirname(current_dir)  # 获取当前目录的父目录
sys.path.insert(0, current_dir)
sys.path.insert(1, parent_dir)

###############################################################################################

import helper_random
import helper_logger
import main_movement_aptos_once


if __name__ == '__main__':
    helper_logger.init_logger( os.path.splitext(os.path.basename(__file__))[0])

    account_list = [
    ]

    # 要执行的任务
    campaign_list = [
        'hypervative_dex'
    ]
    execute_plan = helper_random.build_execute_plan(account_list,campaign_list,is_random_account=True,is_group_campaign=False)

    asyncio.run(main_movement_aptos_once.main(execute_plan))
