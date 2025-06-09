import random
import helper_random

from loguru import logger

import helper_session
import helper_sleep
import model_survey


class DaoSurvey:

    def __init__(self,proxy: str, header: dict):
        header.update({
            'origin':'https://app.galxe.com',
            'accept': '*/*',
            'priority': 'u=1, i',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',

        })
        self.__session = helper_session.new_session(proxy=proxy, header=header)


    def upload_picture_with_retry(self, file_path, survey_credential_id ) -> str:
        retries = 3  # 最大重试次数
        for attempt in range(retries):
            try:
                return self._upload_picture(file_path, survey_credential_id)
            except Exception as e:
                if 'Expecting value' in str(e) or \
                        'Connection reset by peer' in str(e):
                    logger.warning(f"__post_wrapper_with_retry 去做重试的第({attempt + 1})次，e({e})")
                    if attempt < retries - 1:
                        helper_sleep.calculate_backoff_time_and_sleep(attempt, '__post_wrapper_with_retry 重试中')  # 计算等待时间并等待
                    else:
                        logger.error(f"__post_wrapper_with_retry 最大重试次数已达，仍不成功。e({e})")
                        raise
                else:
                    logger.error(f"__post_wrapper_with_retry 失败,e({e})")
                    # 简洁性：如果我们使用 raise e，会重新创建一个异常对象，导致原始异常的堆栈跟踪丢失。因此，直接使用 raise 更加适合在捕获异常后再次抛出。
                    raise  # 其他请求异常，不重试


    """
    返回值
    {
    "message": "Your file has been successfully uploaded",
    "url": "https://cdn.galxe.com/galaxy/galxe-survey-user-uploaded-files/436567482669539328/b5d57089-2e84-4fcf-b079-d633b68f7891.png"
    }
    """
    def _upload_picture(self, file_path, survey_credential_id ) -> str:
        logger.info(f'upload_picture start. file_path({file_path}) survey_credential_id({survey_credential_id})')

        url = 'https://api.galxe.com/v1/media/survey/upload'

        files = {
            'media': (   file_path.split('/')[-1] ,    open(file_path, 'rb'),'image/png' ), #
        }

        # 加入 credId 参数
        data = {
            'credId': survey_credential_id,  # 替换为实际的credId
            'space-alias':'survey'
        }


        response_json = self.__session.post(url, files=files, data=data).json()
        logger.info(f'upload_picture response_json({response_json})')

        ret = response_json['url']
        logger.info(f'upload_picture end. ret({ret})')
        return ret


