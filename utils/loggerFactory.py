# ====================
# 로그 생성 클래스
# ====================

import logging
from datetime import datetime
import os


class LoggerFactory(object):
    _LOGGER = None

    @staticmethod
    def create_logger():
        # 루트 로거 생성
        LoggerFactory._LOGGER = logging.getLogger()
        LoggerFactory._LOGGER.setLevel(logging.INFO)

        # log 폴더가 없으면 생성
        if not os.path.exists("./logs"):
            os.makedirs("./logs")

        # 로그 포맷 설정
        formatter = logging.Formatter(
            "[%(asctime)s][%(levelname)s|%(filename)s-%(funcName)s:%(lineno)s] >> %(message)s"
        )

        # 스트림 핸들러 설정
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # 파일 핸들러 설정 (모드를 'a'로 설정)
        log_file_path = "./logs/" + datetime.now().strftime("%Y%m%d") + ".log"
        file_handler = logging.FileHandler(log_file_path, mode="a")
        file_handler.setFormatter(formatter)

        # 핸들러 추가
        LoggerFactory._LOGGER.addHandler(stream_handler)
        LoggerFactory._LOGGER.addHandler(file_handler)

    @classmethod
    def get_logger(cls):
        return cls._LOGGER
