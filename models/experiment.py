from tensorflow.keras.models import Model
from os.path import isfile, dirname, realpath
from _datetime import datetime
import sqlite3
from sqlite3 import Error
from glob import glob


class DataSource:

    _migrations = '/sql_migrations/*.sql'
    __dbs = {}

    @staticmethod
    def get_instance(db_file):
        if db_file not in DataSource.__dbs.keys():
            _instance = DataSource(db_file)
            DataSource.__dbs.update({db_file: _instance})
            return _instance
        return DataSource.__dbs[db_file]

    def __init__(self, db_file=None):

        new_db = False if isfile(db_file) else True

        try:
            self._conn = sqlite3.connect(db_file)
        except Error as e:
            print(sqlite3.version, '\n', e)

        self.c = self._conn.cursor()

        if new_db:
            [self._migrate(sql_file) for sql_file in glob(dirname(realpath(__file__)) + DataSource._migrations)]

    def _migrate(self, sql_file):
        if isfile(sql_file):
            with open(sql_file, 'r') as queries:
                self.c.executescript(queries.read())
        else:
            print(sql_file, "not found, please check your installation")

    def commit(self):
        self._conn.commit()


class RsModel(Model):

    def __init__(self, db_file=None):
        if db_file:
            self.ds = DataSource.get_instance(db_file)
            self.persistence = True
            self.model_info = None
            self.id = None
        else:
            self.persistence = False

    def initialize(self, inputs, outputs):
        super().__init__(inputs, outputs)

    def get_all(self):
        sql = '''SELECT * FROM models ORDER BY date_modified LIMIT 100'''
        self.ds.c.execute(sql)
        return self.ds.c.fetchall()
    def load_by_name(self, name):
        sql = '''SELECT * FROM models where name=? '''
        self.ds.c.execute(sql, name)
        model = self.ds.c.fetchone()
        if model:
            self.model_info = model
        else:
            print("No module by the name ", name, "in the database")

    def load_by_id(self, model_id):
        sql = '''SELECT * FROM models where id=? '''
        self.ds.c.execute(sql, model_id)
        model = self.ds.c.fetchone()
        if model:
            self.model_info = model
        else:
            print("No module by the id ", model_id, "in the database")

    def save_db(self, model_info):
        timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        sql = ''' INSERT INTO models (name, description, input_shape, classes, palette, date_created,
        date_modified) VALUES (?, ?, ?, ?, ?, ?, ?) '''

        values = (model_info['name'],  model_info['description'],  parse_tuple(model_info['input_shape']),
                  parse_tuple(model_info['classes']), parse_tuple(model_info['palette']), timestamp, timestamp)

        self.ds.c.execute(sql, values)
        self.ds.commit()
        self.id = self.ds.c.lastrowid

    def add_experiment(self, exp_info):
        return Experiment(self.ds, exp_info, self.id)


class Experiment:

    def __init__(self, ds, exp_info, model_id):
        self.ds = ds
        self.id = self.save(exp_info, model_id)

    def add_result(self, result_info):

        sql = ''' INSERT INTO results ( status, train_loss, val_loss, train_accuracy, val_accuracy, experiment_id)
         VALUES (?, ?, ?, ?, ?, ?) '''

        values = (result_info['status'], result_info['train_loss'], result_info['val_loss'],
                  result_info['train_accuracy'], result_info['val_accuracy'], self.id)

        self.ds.c.execute(sql, values)
        self.ds.commit()
        return self.ds.c.lastrowid

    def save(self, exp_info, model_id):

        sql = ''' INSERT INTO experiments (train_size, val_size, epochs, batch_size, loss_function, training_time,
         save_location, model_id)  VALUES (?, ?, ?, ?, ?, ?, ?, ?) '''

        values = (exp_info['train_size'], exp_info['val_size'], exp_info['epochs'], exp_info['batch_size'],
                  exp_info['loss_function'], exp_info['training_time'], exp_info['save_location'], model_id)

        self.ds.c.execute(sql, values)
        self.ds.commit()
        return self.ds.c.lastrowid


def parse_tuple(t):
    return ' '.join(map(str, t))


