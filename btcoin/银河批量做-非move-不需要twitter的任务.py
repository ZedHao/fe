import os
import sys
current_file_path = os.path.abspath(__file__)  # 获取当前文件的绝对路径
current_dir = os.path.dirname(current_file_path)  # 获取当前文件所在的目录
parent_dir = os.path.dirname(current_dir)  # 获取当前目录的父目录
sys.path.insert(0, current_dir)
sys.path.insert(1, parent_dir)


###############################################################################################

from loguru import logger

import model_galxe_kyc_list

import helper_logger
import helper_random



import main_quiz





def get_account_list():
    return  model_galxe_kyc_list.all_galxe_kyc_list

def get_campaign_list():
    """
任务记录
# 9-10 玉米cron的任务
"CORN/GChphtxYjE",
"CORN/GCh8dtxXmc",
 'CORN/GCTcbtKxoc', #完成了


"burnt/GCxLutxvCN", #手动去做dc
# "pufferfinance/GCcVntxZAi" #手动去做dc   TODO 有推特必须看着搞，暂时算了

'burnt/GCLqPtKH7H'


'MapleStoryUniverse/GCJGhtVkin',  # 冒险岛第十季答题 #完成了

    """

    quiz_campaign_list = [


    ]
    return quiz_campaign_list


if __name__ == '__main__':
    helper_logger.init_logger(os.path.splitext(os.path.basename(__file__))[0])


    account_list = get_account_list()
    quiz_campaign_list = get_campaign_list()
    execute_plan = helper_random.build_execute_plan(account_list, quiz_campaign_list,is_random_account=True,is_group_campaign=True)

    for account_idx, (cur_account_name, quiz_campaign_list) in enumerate(execute_plan):
        logger.warning(f"前置log所有的执行计划 account_idx({account_idx}) cur_account_name({cur_account_name}) quiz_campaign_list={quiz_campaign_list}")




    main_quiz.main(execute_plan)
