
import os
import sys
current_file_path = os.path.abspath(__file__)  # 获取当前文件的绝对路径
current_dir = os.path.dirname(current_file_path)  # 获取当前文件所在的目录
parent_dir = os.path.dirname(current_dir)  # 获取当前目录的父目录
sys.path.insert(0, current_dir)
sys.path.insert(1, parent_dir)

###############################################################################################

from loguru import logger
import helper_logger
import asyncio
import helper_random
import main_movement_aptos_once



def get_account_list(args)->list:
    """
确认完成了50次swap的账号

"PY01",
"PY02",
"PY03",
"PY04",
"PY05",


'F05',

'F11',
'F12',
'F13',
'F14',
'F15',
'F16',
'F17',
'F18',
'F19',
'F20',


"ZHU07",
"ZHU10",
"ZHU13", # 手动确认完成了
"ZHU15", # 手动确认完成了


'ZHU22',
'ZHU23',
'ZHU24',
"ZHU25", # 手动确认完成了
'ZHU26',
'ZHU27',
'ZHU28',
'ZHU29',
'ZHU30',
'ZHU31',
'ZHU32',
'ZHU33',
'ZHU34',
'ZHU35',
'ZHU36',
'ZHU37',
'ZHU38',
'ZHU39',
'ZHU40',


    """


    ret = [




    ]

    # 指定一个账号
    if args is not None and args.account_name is not None and len(args.account_name) != 0:
        ret = [args.account_name]

    return  ret

def get_campaign_list()->list:
    """
    GC94ttv9vW 任务id
    """
    ret= ['razor_dex']
    return ret





if __name__ == '__main__':
    helper_logger.init_logger(os.path.splitext(os.path.basename(__file__))[0])

    account_list = get_account_list(None)
    campaign_list = get_campaign_list()
    execute_plan=helper_random.build_execute_plan(account_list,campaign_list,is_random_account=True,is_group_campaign=False)
    for account_idx, (cur_account_name, quiz_campaign_list) in enumerate(execute_plan):
        logger.warning(f"前置log执行计划 account_idx({account_idx}) cur_account_name({cur_account_name}) quiz_campaign_list={quiz_campaign_list}")



    asyncio.run(main_movement_aptos_once.main(execute_plan))
