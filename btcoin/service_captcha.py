import time

import dao_captcha
from loguru import logger

import service_account_evm
import helper_sleep


class ServiceCaptcha:
    def __init__(self, cur_account: service_account_evm.Account):
        # 只需要代理就够了
        self.__dao_captcha = dao_captcha.DaoCaptcha(cur_account.proxy,cur_account.header)

    def get_captcha_for_galxe_wrapper(self):

        retries = 6  # 最大重试次数
        for attempt in range(retries):
            try:
                # 成功就直接return
                return self.get_captcha_for_galxe()
            except Exception as e:
                if 'Workers could not solve the Captcha' in str(e) or \
                        'Connection reset by peer' in str(e):
                    logger.warning(f"get_captcha_for_galxe_wrapper 去做重试的第({attempt + 1})次，e({e})")
                    if attempt < retries - 1:
                        helper_sleep.calculate_backoff_time_and_sleep(attempt, 'get_captcha_for_galxe_wrapper 重试中')  # 计算等待时间并等待
                    else:
                        logger.error(f"get_captcha_for_galxe_wrapper 最大重试次数已达，仍不成功。e({e})")
                        raise
                else:
                    logger.error(f"get_captcha_for_galxe_wrapper 失败,e({e})")
                    # 简洁性：如果我们使用 raise e，会重新创建一个异常对象，导致原始异常的堆栈跟踪丢失。因此，直接使用 raise 更加适合在捕获异常后再次抛出。
                    raise  # 其他请求异常，不重试





    def get_captcha_for_galxe(self):
        task_id = self.__dao_captcha.create_task_for_galxe_with_retry()
        logger.info(f' Created task_id={task_id}')

        total_time = 0
        timeout = 360

        while True:
            response = self.__dao_captcha.get_task_result_for_galxe_with_retry(task_id)

            if response['status'] == 'ready':
                logger.info(f' Captcha 完成了, total_time={total_time}')

                captcha_data = response['solution']

                # 组层一个dict返回
                return {
                    "lotNumber": captcha_data['lot_number'],
                    "passToken": captcha_data['pass_token'],
                    "genTime": captcha_data['gen_time'],
                    "captchaOutput": captcha_data['captcha_output'],
                }
            else:
                logger.info(f' Captcha is not ready yet, 继续等待 total_time={total_time}')

            total_time += 10
            time.sleep(10)

            if total_time > timeout:
                # 看2cap界面，之前有一次168秒才解决
                # 可能是偶尔验证码服务挂了
                raise Exception('get_captcha_for_galxe Can`t get captcha solve in 360 second')
