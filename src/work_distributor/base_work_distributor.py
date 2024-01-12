# isort:imports-stdlib
import multiprocessing
from collections.abc import Callable, Iterable
from multiprocessing import Manager, Pool
from typing import Union

# isort:imports-thirdparty
from tqdm import tqdm

# isort:imports-firstparty

# isort:import-localfolder

INDEX_TO_TEST_DEFAULT = 0


class WorkDistributor:
    def __init__(self):
        pass

    def run_with_progress_bar(
        self,
        func: Callable,
        process_type: str,
        iterable_object: Iterable,
        debug: bool,
        index_to_test: Union[type(None), int] = None,
        *args,
        **kwargs
    ):
        if process_type == "sequential":
            return self._run_sequential_with_progress_bar(
                func=func, iterable_object=iterable_object, *args, **kwargs
            )
        elif process_type == "parallel":
            return self._run_parallel_with_progress_bar(
                func=func, iterable_object=iterable_object, debug=debug, *args, **kwargs
            )
        elif process_type == "test":
            if index_to_test is None:
                index_to_test = INDEX_TO_TEST_DEFAULT
            return self._run_sequential_with_progress_bar(
                func=func,
                iterable_object=[iterable_object[index_to_test]],
                *args,
                **kwargs
            )
        else:
            raise ValueError(
                "process_type should be either sequential or parallel or test"
            )
        return

    def _run_sequential_with_progress_bar(
        self, func: Callable, iterable_object: Iterable, *args, **kwargs
    ):
        result = []
        for item in tqdm(iterable_object):
            result.append(func(**item))

        return result

    def _run_parallel_with_progress_bar(
        self, func: Callable, iterable_object: Iterable, debug: bool, *args, **kwargs
    ):
        # list_to_share=None must be in func
        pool = Pool(multiprocessing.cpu_count())
        pbar = tqdm(total=len(iterable_object))

        def update(*a):
            pbar.update()

        with Manager() as manager:
            list_to_share = manager.list()

            for idx in range(0, len(iterable_object)):
                iterable_object[idx]["list_to_share"] = list_to_share

            for item in iterable_object:
                values = item.values()
                if debug is True:
                    _ = pool.apply_async(func, values, callback=update)
                    _.get()
                else:
                    pool.apply_async(func, values, callback=update)
            pool.close()
            pool.join()
            list_to_share = list(list_to_share)

        return list_to_share
