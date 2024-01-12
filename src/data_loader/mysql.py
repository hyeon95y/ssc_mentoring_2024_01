import multiprocessing
import os
from datetime import datetime
from time import time
from typing import Any

import dask.dataframe as dd
import pandas as pd
import sqlalchemy as db

from project_paths import CACHED_PATH

NUM_CPU_COUNT = multiprocessing.cpu_count()
DATE_TODAY = datetime.today().strftime("%Y_%m_%d")


def timer(func):
    """_summary_

    Args:
        func (_type_): _description_
    """

    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f"Executed in {(t2-t1):.4f}s")
        return result

    return wrap_func


class MySQLDataLoader:
    def __init__(
        self, backend="pandas", cached_path=CACHED_PATH, cached_date=DATE_TODAY
    ):
        self._backend = backend
        self._cached_path = cached_path
        self._cached_date = cached_date

    def _get_connection(self, db_name: str):
        db_url = self._get_url(db_name)
        engine = db.create_engine(db_url)
        connection = engine.connect()
        return connection

    def _get_column_names(self, engine, db_name: str):
        metadata = db.MetaData()
        table = db.Table(
            db_name,
            metadata,
            autoload=True,
            autoload_with=engine,
        )
        return table.columns.keys()

    def execute_query(self, db_name: str, query: str) -> pd.DataFrame:
        connection = self._get_connection(db_name)
        result = connection.execute(query)

        data = pd.DataFrame(result.fetchall(), columns=result._metadata.keys)

        return data

    def _get_url(self, db_name: str) -> str:
        """_summary_

        Args:
            db_name (str): _description_

        Returns:
            str: _description_
        """
        from _secrets import MySQL_ID, MySQL_IP, MySQL_PW

        db_url = f"mysql+pymysql://{MySQL_ID}:{MySQL_PW}@{MySQL_IP}/{db_name}"
        return db_url

    def get_engine(self, db_name: str) -> Any:
        db_url = self._get_url(db_name)

        engine = db.create_engine(db_url, echo=False, pool_size=NUM_CPU_COUNT)
        return engine

    def _get_engine_connection_table(self, db_name: str, table_name: str) -> Any:
        """_summary_

        Args:
            db_name (str): _description_
            table_name (str): _description_

        Returns:
            Any: _description_
        """

        db_url = self._get_url(db_name)

        engine = db.create_engine(db_url, echo=False, pool_size=NUM_CPU_COUNT)
        connection = engine.connect()

        metadata = db.MetaData(engine)
        table = db.Table(
            table_name,
            metadata,
            autoload=True,
            autoload_with=engine,
        )

        return engine, connection, table

    def describe(self, db_name: str, table_name: str):
        num_of_rows = self.get_nums_rows(db_name, table_name)
        data_sample = self.load_table(db_name, table_name, limit=5)

        print(f"{db_name}.{table_name} has {num_of_rows} rows")
        display(data_sample)

        return

    def get_nums_rows(self, db_name: str, table_name: str) -> int:
        """_summary_

        Args:
            db_name (str): _description_
            table_name (str): _description_

        Returns:
            int: _description_
        """

        def _get_query():
            query = db.select(db.func.count(table.columns[0]))
            return query

        def _to_int(data) -> int:
            return int(data[0][0])

        def _postprocess(data) -> Any:
            data = _to_int(data)
            return data

        engine, connection, table = self._get_engine_connection_table(
            db_name,
            table_name,
        )
        query = _get_query()
        data = self._execute(connection, query, _postprocess)

        return data

    def load_table(
        self,
        db_name: str,
        table_name: str,
        columns: list = None,
        limit: int = None,
        use_cached=True,
        desc=True,
        desc_by=None,
    ) -> pd.DataFrame:
        """_summary_

        Args:
            db_name (str): _description_
            table_name (str): _description_
            limit (int, optional): _description_. Defaults to None.
            use_cached (bool, optional): _description_. Defaults to True.
            desc (bool, optional): _description_. Defaults to True.
            desc_by (_type_, optional): _description_. Defaults to None.

        Returns:
            pd.DataFrame: _description_
        """

        def _get_query(limit: int):
            if columns is None:
                query = table.select()
            else:
                query = table.select()
            if (desc is True) & (desc_by is not None):
                query = query.order_by(
                    table.columns[desc_by].desc(),
                )
            else:
                pass

            if limit is None:
                pass
            else:
                query = query.limit(limit)

            return query

        def _postprocess(data) -> Any:
            if self._backend == "pandas":
                data = pd.DataFrame(data, columns=table.columns.keys())
            elif self._backend == "dask":
                data = pd.DataFrame(data, columns=table.columns.keys())
                data = dd.from_pandas(data, npartitions=NUM_CPU_COUNT)
            else:
                raise NotImplementedError
            return data

        cached_filepath = self._get_cached_filepath(db_name, table_name, limit)
        if use_cached is True and os.path.exists(cached_filepath):
            data = self._load_cached(cached_filepath, self._backend)
        else:
            engine, connection, table = self._get_engine_connection_table(
                db_name,
                table_name,
            )
            query = _get_query(limit)
            data = self._execute(connection, query, _postprocess)
            self._save_cache(data, cached_filepath, self._backend)

        return data

    @timer
    def _execute(self, connection, query, _postprocess):
        """_summary_

        Args:
            connection (_type_): _description_
            query (_type_): _description_
            _postprocess (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            data = connection.execute(query, verbose=0).fetchall()
            data = _postprocess(data)
        except Exception as e:
            print(e)
            data = None
        return data

    def _get_cached_filepath(self, db_name: str, table_name: str, limit: int) -> str:
        """_summary_

        Args:
            db_name (str): _description_
            table_name (str): _description_
            limit (int): _description_

        Returns:
            str: _description_
        """
        date = self._cached_date
        filetype = "parquet"

        cached_filename = (
            f"{self._backend}_{db_name}_{table_name}_{date}_{str(limit)}.{filetype}"
        )
        cached_filepath = os.path.join(self._cached_path, cached_filename)
        return cached_filepath

    def _save_cache(self, data, cached_filepath, backend: str):
        """_summary_

        Args:
            data (_type_): _description_
            cached_filepath (_type_): _description_
            backend (str): _description_
        """
        if backend == "pandas":
            data.to_parquet(cached_filepath)
        elif backend == "dask":
            data.to_parquet(cached_filepath, schema="infer")
        return

    @timer
    def _load_cached(self, cached_filepath, backend: str):
        """_summary_

        Args:
            cached_filepath (_type_): _description_
            backend (str): _description_

        Returns:
            _type_: _description_
        """
        date = self._cached_date
        print(f"Using cached data at {date}")
        if backend == "pandas":
            data = pd.read_parquet(cached_filepath)
        elif backend == "dask":
            data = dd.read_parquet(
                f"{cached_filepath}/*",
                blocksize=NUM_CPU_COUNT,
            )

        return data
