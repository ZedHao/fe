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
import helper_random
import model_campaign_list

import helper_logger

from loguru import logger

import main_quiz


def get_account_list(args) -> list:
    """
    已经完成quiz的账号
"PY01",
"PY02",
"PY03",


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

"ZHU11",#done
"ZHU12",#done
"ZHU13",#done
"ZHU14",#done
"ZHU15",#done
"ZHU16",#done
"ZHU17",#done
"ZHU18",#done
"ZHU19",#done
"ZHU20",#done

"ZHU21",
"ZHU22",
"ZHU23",
"ZHU24",
"ZHU25",
"ZHU26",
"ZHU27",
"ZHU28",
"ZHU29",
"ZHU30",

"ZHU31",
"ZHU32",
"ZHU33",
"ZHU34",
"ZHU35",
"ZHU36",
"ZHU37",
"ZHU38",
"ZHU39",
"ZHU40",

    """

    ret = [
        "PY04",
        "PY05",

        "F11",
        "F12",
        "F13",
        "F14",
        "F15",
        "F16",
        "F17",
        "F18",
        "F19",
        "F20",

    ]

    # 指定一个账号
    if args is not None and args.account_name is not None and len(args.account_name) != 0:
        ret = [args.account_name]

    return ret


def get_campaign_list() -> list:
    ret = model_campaign_list.quiz_campaign_list

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
