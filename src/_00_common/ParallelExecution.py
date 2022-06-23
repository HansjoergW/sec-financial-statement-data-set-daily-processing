# using pathos.multiprocessing istead of multiprocessing
# - https://stackoverflow.com/questions/3288595/multiprocessing-how-to-use-pool-map-on-a-function-defined-in-a-class

import logging
from pathos.multiprocessing import ProcessingPool as Pool
from time import time, sleep
from typing import Generic, TypeVar, List, Callable, Optional, Tuple

IT = TypeVar("IT")  # input type of the list to split
PT = TypeVar("PT")  # processed type of the list to split
OT = TypeVar("OT")  # PostProcessed Type


class ParallelExecutor(Generic[IT, PT, OT]):

    def __init__(self,
                processes: int = 8,
                chunksize: int = 100,
                max_calls_per_sec: int = 0,
                intend: str = "    "):

        self.processes = processes
        self.chunksize = chunksize
        self.intend = intend
        self.min_roundtrip_time = 0
        if max_calls_per_sec > 0:
            self.min_roundtrip_time = float(processes) / max_calls_per_sec

        self.get_entries_function: Optional[Callable[[], List[IT]]] = None
        self.process_element_function: Optional[Callable[[IT], PT]] = None
        self.post_process_chunk_function: Optional[Callable[[List[PT]], List[OT]]] = None

    def set_get_entries_function(self, get_entries: Callable[[], List[IT]]):
        self.get_entries_function = get_entries

    def set_process_element_function(self, process_element: Callable[[IT], PT]):
        self.process_element_function = process_element

    def set_post_process_chunk_function(self,  post_process: Callable[[List[PT]], List[OT]]):
        self.post_process_chunk_function = post_process

    def process_throttled(self, data: IT) -> PT:
        start = time()
        result: PT = self.process_element_function(data)
        end = time()
        if self.min_roundtrip_time > 0:
            sleep_time = max(0.0, self.min_roundtrip_time - (end - start))
            sleep(sleep_time)

        return result

    def execute(self) -> Tuple[List[OT], List[IT]]:
        pool = Pool(self.processes)

        last_missing = None
        missing: List[IT] = self.get_entries_function()
        result_list: List[OT] = []

        while (last_missing is None) or (last_missing > len(missing)):
            last_missing = len(missing)
            logging.info(f"{self.intend}missing entries {len(missing)}")

            for i in range(0, len(missing), self.chunksize):
                chunk = missing[i:i + self.chunksize]
                processed: List[PT] = pool.map(self.process_throttled, chunk)
                result_list.append(self.post_process_chunk_function(processed))
                logging.info(f"{self.intend}commited chunk: {i}")

            missing = self.get_entries_function()

        return result_list, missing


if __name__ == '__main__':
    # simple example
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)

    class MyTestClass:
        def __init__(self):
            self.data_list = [str(x) for x in range(500)]
            self.was_read = [False]

        def get_unprocessed_entries(self) -> List[str]:
            if self.was_read[0] == False:
                self.was_read[0] = True
                return self.data_list
            return []

        def process_element(self, input: str) -> str:
            return "0" + str(input)

        def post_process(self, input: List[str]) -> List[str]:
            return input

        def process(self):
            executor = ParallelExecutor[str, str, str](max_calls_per_sec=160)
            executor.set_get_entries_function(self.get_unprocessed_entries)
            executor.set_process_element_function(self.process_element)
            executor.set_post_process_chunk_function(self.post_process)

            print(executor.execute())

    MyTestClass().process()