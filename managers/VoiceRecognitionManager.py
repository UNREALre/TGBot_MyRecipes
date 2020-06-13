import os
import warnings
import numpy as np
from classes.ModelHMM import ModelHMM
from scipy.io import wavfile
from python_speech_features import mfcc


def build_models(input_folder):
    """Создает модель для каждого слова"""
    # Переменная для хранения всех моделей для каждого слова
    speech_models = []

    # Анализ входного каталога
    for dirname in os.listdir(input_folder):
        # Получаем подпапку
        subfolder = os.path.join(input_folder, dirname)
        if not os.path.isdir(subfolder):
            continue

        # Извлечение метки
        label = subfolder[subfolder.rfind('\\') + 1:]

        # Переменная для хранения тренировочных данных
        X = np.array([])

        # Создаем список файлов для тренировки моделей.
        training_files = [x for x in os.listdir(subfolder) if x.endswith('.wav')]

        # Проходимся по тренировочным файлам и строим модели
        for filename in training_files:
            # Извлекаем путь к текущему файлу
            filepath = os.path.join(subfolder, filename)

            # Читаем аудиосигнал из файла
            sampling_freq, signal = wavfile.read(filepath)

            # Извлекаем MFCC-признаки
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                features_mfcc = mfcc(signal, sampling_freq)

            # Присоединим точку данных к переменной X
            if len(X) == 0:
                X = features_mfcc
            else:
                X = np.append(X, features_mfcc, axis=0)

            # Создание HMM-модели
            model = ModelHMM()

            # Обучение модели, используя тренировочные данные
            model.train(X)

            # Сохранение модели для текущего слова
            speech_models.append((model, label))

            # Сброс переменной
            model = None

    return speech_models


def run_test(test_files, speech_models):
    """Функция для тестирования входных данных"""
    # Классификация входных данных
    for test_file in test_files:
        # Чтение входного файла
        sampling_freq, signal = wavfile.read(test_file)

        # Извлечение MFCC признаков
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            features_mfcc = mfcc(signal, sampling_freq)

        # Переменные для хранения максимальной оценки и выходной метки
        max_score = -float('inf')
        output_label = predicted_label = None

        # Выполняем итерации по моделям, чтобы выбрать наилучшую
        # Прогоняем текущий вектор призанков через каждую HMM-модель
        # выбирая ту из них, которая получит наивысшую оценку
        for item in speech_models:
            model, label = item

            # Вычислим оценку и сравним ее с максимальной оценкой
            score = model.compute_score(features_mfcc)
            if score > max_score:
                max_score = score
                predicted_label = label

        return predicted_label


def fire_recognition(file_path, speech_models):
    test_files = [file_path]
    return run_test(test_files, speech_models)
