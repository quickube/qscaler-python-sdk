from typing import Optional, NoReturn, Union

from pkg.configuration.config import config, ResultsStorages
from pkg.results_storage.redis_results_storage import RedisResultsStorage
from pkg.results_storage.results_storage import ResultsStorage


class ResultsStoragesFactory:

    @staticmethod
    def get_storage(storage: Optional[str] = None) -> Union[ResultsStorage, NoReturn]:
        if storage is None:
            storage = config.storage.type
        if storage == ResultsStorages.REDIS.value:
            return RedisResultsStorage()
        else:
            raise NotImplementedError
