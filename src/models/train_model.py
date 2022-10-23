# -*- coding: utf-8 -*-
import sys

sys.path.append('../src')
sys.path.append('../data')

import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from sklearn.model_selection import train_test_split
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.metrics import mean_squared_error
import config as cfg
import json 
from utils import *



@click.command()
@click.argument('train_data_filepath', type=click.Path(exists=True)) # train C:\Users\User\Desktop\Ivanov_lab1\hse_workshop_classification-main\data\processed\train.pkl
@click.argument('target_data_filepath', type=click.Path(exists=True)) # target C:\Users\User\Desktop\Ivanov_lab1\hse_workshop_classification-main\data\processed\target.pkl
@click.argument('output_model_filepath', type=click.Path()) # C:\Users\User\Desktop\Ivanov_lab1\hse_workshop_classification-main\models
def main(train_data_filepath, target_data_filepath, output_model_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    train = pd.read_pickle(train_data_filepath)
    target = pd.read_pickle(target_data_filepath)

    X_train, X_val, y_train, y_val = train_test_split(train, target, train_size=0.8, random_state=42)

    metrics = {}

    model = CatBoostRegressor(iterations = 10000,
                        verbose = 1000,
                        learning_rate = 0.03,
                        eval_metric = 'RMSE',
                        random_seed = 42,
                        # logging_level = 'Silent',
                        use_best_model = True,
                        loss_function = 'RMSE',
                        od_type = 'Iter',
                        od_wait = 2000,
                        one_hot_max_size = 20,
                        l2_leaf_reg = 100,
                        depth = 3,
                        rsm = 0.6,
                        random_strength = 2,
                        bagging_temperature = 10)

    model.fit(X_train, y_train, eval_set=(X_val, y_val), cat_features=cfg.CAT_COLS)
    save_model(model, output_model_filepath + '/catboost.sav')

    y_pred = model.predict(X_val)
    metrics['rmse'] = mean_squared_error(y_val, y_pred, squared=False)

    with open("metrics_catboost.json", "w") as outfile:
        json.dump(metrics, outfile)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()

# python models/train_model.py '../data/processed/train.pkl' '../data/processed/target.pkl' '../models'
 
# dvc stage add -n train_catboost -d ../data/processed -o ../models python models/train_model.py '../data/processed/train.pkl' '../data/processed/target.pkl' '../models'