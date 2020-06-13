from hmmlearn import hmm
import numpy as np


class ModelHMM(object):
    """Класс для тренировки HMM"""

    def __init__(self, num_components=4, num_iter=1000):
        self.n_components = num_components
        self.n_iter = num_iter

        # Определяем тип ковариации и тип HMM
        self.cov_type = 'diag'
        self.model_name = 'GaussianHMM'

        # Инициализируем переменную, в которой будут храниться модели для каждого слова
        self.models = []

        # Определяем модель, используя вышеуказанные параметры
        self.model = hmm.GaussianHMM(n_components=self.n_components, covariance_type=self.cov_type, n_iter=self.n_iter)

    def train(self, training_data):
        """
        Метод для обучения модели

        training_data - 2D массив numpy, каждая строка в нем имеет 13 измерений
        :param training_data:
        :return:
        """
        np.seterr(all='ignore')
        cur_model = self.model.fit(training_data)
        self.models.append(cur_model)

    def compute_score(self, input_data):
        """
        Выполнение HMM модели для оценки входных данных

        :param input_data:
        :return:
        """
        return self.model.score(input_data)
