from abc import ABC, abstractmethod
from typing import TypeAlias, Iterable, Any

from django.db.models import Model

from services.redis.models_base import DataClassModel, DictModel, HashModel


# TODO: add TypeAlias SQLModel for Model
class BaseRedisTransformer(ABC):
    def dc_models_to_dict_models(self,
                                 dc_model: Iterable[DataClassModel],
                                 ) -> list[DictModel]:
        dict_models = [
            self.dc_model_to_dict_model(model)
            for model in dc_model
        ]
        return dict_models

    @staticmethod
    @abstractmethod
    def dc_model_to_dict_model(dc_model: DataClassModel,
                               ) -> DictModel:
        pass

    def hash_models_to_dc_models(self,
                                 hash_models: Iterable[HashModel],
                                 ) -> list[DataClassModel]:
        dc_models = [
            self.hash_model_to_dc_model(model)
            for model in hash_models
        ]
        return dc_models

    @staticmethod
    @abstractmethod
    def hash_model_to_dc_model(hash_model: HashModel,
                               ) -> DataClassModel:
        pass

    def hash_models_to_dict_models(self,
                                   hash_models: Iterable[HashModel],
                                   ) -> list[DictModel]:
        dc_models = self.hash_models_to_dc_models(hash_models)
        dict_models = self.dc_models_to_dict_models(dc_models)
        return dict_models


class BaseSQLTransformer(ABC):
    @staticmethod
    @abstractmethod
    def sql_model_to_dc_model(sql_model: Model,
                              ) -> DataClassModel:
        pass

    def sql_models_to_dc_models(self,
                                sql_models: Iterable[Model],
                                ) -> list[DataClassModel]:
        dc_models = [
            self.sql_model_to_dc_model(sql_model)
            for sql_model in sql_models
        ]
        return dc_models


class BaseFullTransformer(BaseRedisTransformer, BaseSQLTransformer, ABC):

    def sql_models_to_dict_models(self,
                                  sql_models: Iterable[Model],
                                  ) -> list[DictModel]:
        dict_models = [
            self.sql_model_to_dict_model(sql_model)
            for sql_model in sql_models
        ]
        return dict_models

    def sql_model_to_dict_model(self,
                                sql_model: Model,
                                ) -> DictModel:
        dc_model = self.sql_model_to_dc_model(sql_model)
        dict_model = self.dc_model_to_dict_model(dc_model)

        return dict_model
