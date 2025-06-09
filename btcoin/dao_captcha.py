from loguru import logger

import helper_session
import helper_sleep


class DaoCaptcha:
    # 每个dao都单独的session
    def __init__(self, proxy: str, header: dict = None):
        self.__session = helper_session.new_session(proxy=proxy, header=header)
        self.TWO_CAPTCHA_API_KEY = '0b9198c96b62e6d69518f9a0ceae3af6'

    def create_task_for_galxe_with_retry(self):
        retries = 3  # 最大重试次数
        for attempt in range(retries):
            try:
                return self.__create_task_for_galxe()

            except Exception as e:
                # 不能写 requests.exceptions.JSONDecodeError，而是要写Expecting value: line 1 column 1
                if 'Expecting value' in str(e) or \
                        'Bad request to 2Captcha' in str(e) or \
                        'Extra data' in str(e):
                    logger.warning(f" 尝试第 {attempt + 1} 次 e={e}")
                    if attempt < retries - 1:
                        helper_sleep.calculate_backoff_time_and_sleep(attempt, '__create_task_for_galxe 重试中')  # 计算等待时间并等待
                    else:
                        logger.error(f" 最大重试次数已达，仍不成功。e={e}")
                        raise
                else:
                    logger.error(f" 请求失败 e={e}")
                    # 简洁性：如果我们使用 raise e，会重新创建一个异常对象，导致原始异常的堆栈跟踪丢失。因此，直接使用 raise 更加适合在捕获异常后再次抛出。
                    raise  # 其他请求异常，不重试

    # 创建任务，获取任务id
    def __create_task_for_galxe(self):
        url = 'https://api.2captcha.com/createTask'

        payload = {
            "clientKey": self.TWO_CAPTCHA_API_KEY,
            "task": {
                "type": "GeeTestTaskProxyless",
                "websiteURL": "https://galxe.com",
                # GeeTest这类验证码的版本，那么银河就是用的4版本
                "version": 4,
                "initParameters": {
                    # 什么意思
                    # 它标识了 https://galxe.com 网站的 GeeTest 验证码配置。这个 ID 需要在创建验证码任务时传递给 2Captcha API
                    # 不会怎么查一个新网站的captcha_id，只能是说先用着，后面再说
                    "captcha_id": "244bcb8b9846215df5af4c624a750db4"
                }
            }
        }
        response = self.__session.post(url=url, json=payload).json()
        logger.info(f' response({response}')

        if 'errorId' in response and response['errorId'] != 0:
            if response['errorId'] == 10:
                raise Exception(f'没钱啦!! response({response})')
            else:
                raise Exception(f'创建验证码任务失败 response({response})')

        if not response['errorId']:
            return response['taskId']

    def get_task_result_for_galxe_with_retry(self, task_id):
        retries = 3  # 最大重试次数
        for attempt in range(retries):
            try:
                return self.__get_task_result_for_galxe(task_id)

            except Exception as e:
                # requests.exceptions.JSONDecodeError居然不在str(e)里面，而是要Expecting value: line 1 column 1
                if 'Expecting value' in str(e) or \
                        'Extra data' in str(e):
                    logger.warning(f" 尝试第 {attempt + 1} 次 e={e}")
                    if attempt < retries - 1:
                        helper_sleep.calculate_backoff_time_and_sleep(attempt, '__create_task_for_galxe 重试中')  # 计算等待时间并等待
                    else:
                        logger.error(f" 最大重试次数已达，仍不成功。e={e}")
                        raise
                else:
                    logger.error(f" 请求失败 e={e}")
                    # 简洁性：如果我们使用 raise e，会重新创建一个异常对象，导致原始异常的堆栈跟踪丢失。因此，直接使用 raise 更加适合在捕获异常后再次抛出。
                    raise  # 其他请求异常，不重试

    # 获取任务的识别结果
    def __get_task_result_for_galxe(self, task_id):
        url = 'https://api.2captcha.com/getTaskResult'

        payload = {
            "clientKey": self.TWO_CAPTCHA_API_KEY,
            "taskId": task_id
        }

        headers = {
            'content-type': 'text/plain; charset=utf-8'
        }

        response = self.__session.post(url=url, json=payload, headers=headers).json()
        logger.info(f' end. response={response} task_id={task_id}')

        if 'errorId' in response and response['errorId'] != 0:
            raise Exception(f'获取验证码失败 response={response} task_id={task_id}')

        return response
