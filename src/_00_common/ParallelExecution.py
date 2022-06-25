# using pathos.multiprocessing instead of multiprocessing, so that method functions can be used
# - https://stackoverflow.com/questions/3288595/multiprocessing-how-to-use-pool-map-on-a-function-defined-in-a-class

import logging
from pathos.multiprocessing import ProcessingPool as Pool
from time import time, sleep
from typing import Generic, TypeVar, List, Callable, Optional, Tuple

IT = TypeVar("IT")  # input type of the list to split
PT = TypeVar("PT")  # processed type of the list to split
OT = TypeVar("OT")  # PostProcessed Type


class ParallelExecutor(Generic[IT, PT, OT]):
    """
    this helper class supports in parallel processing of entries that are provided as a list, for instance to
    download and process data.. like downloading and processing sec filing reports.
    It mainly takes care about the following things:
    - it throttles the amount of calls
      for instance, you can define how many call should be made at max within a second. When you download
      content from the SEC, you may only send 10 request per second.
    - retry handling
      especially when reading data from the web, it is normal that some requests might end up with an exception.
      If that happens, the logic retries failed entries.
    - processing in chunks
      you can define the chunksize after which the state is updated. For instance when having to download and process
      a few thousand reports, you can make sure that the current state is stored every 100 reports. Therefore in case
      something "bigger" happens, at least the work that already was done is kept.


    How to use it
    You need to define 3 functions.
    The get_entries_function returnes a list with the entries that need to be processed.
    The process_element_function is the logic that processes a single element from the entries and returns the processed content.
    The post_process_chunk_function receives a list of processed entries. you use this function to update the processed entries,
    so that in the next call to get_entries_function, these entries will not be part of
    """

    def __init__(self,
                processes: int = 8,
                chunksize: int = 100,
                max_calls_per_sec: int = 0,
                intend: str = "    "):
        """
        :param processes: number of parallel processes
        :param chunksize: size of chunk - think of it as a commit
        :param max_calls_per_sec: how many calls may be made per second (for all processes)
        """

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
        """
        set the function which returns the list of the items that have not been processed.
        :param get_entries: function that returns the items to be processed
        """
        self.get_entries_function = get_entries

    def set_process_element_function(self, process_element: Callable[[IT], PT]):
        """
        set the function that processes a single element and returns the processed element
        """
        self.process_element_function = process_element

    def set_post_process_chunk_function(self,  post_process: Callable[[List[PT]], OT]):
        """
        set the function that receives a list of processed elements unad updates the state of these elements.
        accordingly
        :param post_process:
        """
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

        # we retry as long as we were able to process additional entries with in the while loop.
        while (last_missing is None) or (last_missing > len(missing)):
            last_missing = len(missing)
            logging.info(f"{self.intend}missing entries {len(missing)}")

            # break up the list of missing entries in chunks and process every chunk in parallel
            chunk_entries = self.chunksize
            # if chunksize is zero, we just create a single chunk
            if self.chunksize == 0:
                chunk_entries = len(missing)

            for i in range(0, len(missing), chunk_entries):
                chunk = missing[i:i + chunk_entries]
                processed: List[PT] = pool.map(self.process_throttled, chunk)

                # post process the chunk and add the result to the result_list. it is olso ok to return nothing
                result_list.append(self.post_process_chunk_function(processed))
                logging.info(f"{self.intend}commited chunk: {i}")

            # call get_entries_function again to check whether there have been entries that couldn't be processed
            missing = self.get_entries_function()

        return result_list, missing


if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)

    # simple example to use it
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