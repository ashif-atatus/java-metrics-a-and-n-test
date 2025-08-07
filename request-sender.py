## Stress test script for a Java application with various endpoints.

from asyncio import sleep, create_task, run, gather, Event
from datetime import datetime
from httpx import AsyncClient, Timeout
from logging import info, error , basicConfig, getLogger
from random import randint, random, seed
from secrets import choice
from sys import exit
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TaskID
)
from rich.live import Live

LOG_LEVEL: str = "CRITICAL"  # Set the desired log level

basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s") # Configure logging
getLogger("httpx").setLevel("ERROR")  # Suppress httpx logs

def log_info(message: str) -> None:
    """Log an info message."""
    info(message)

def log_error(message: str) -> None:
    """Log an error message."""
    error(message)

class Count:
    def __init__(self):
        self.counts = {
            "total_request": 0,
            "failed_request": 0,
            "endpoint_sleep": 0,
            "endpoint_test1": 0,
            "endpoint_test2": 0,
            "endpoint_fail": 0,
            "endpoint_exception": 0,
            "batch": 0
        }

    def increment(self, key: str):
        """Increment the count for a specific key."""
        if key in self.counts:
            self.counts[key] += 1
        else:
            raise KeyError(f"Invalid key: {key}")
    
    def get(self, key: str) -> int:
        """Get the count for a specific key."""
        if key in self.counts:
            return self.counts[key]
        else:
            raise KeyError(f"Invalid key: {key}")
    

    def log_to_file(self, start_time: datetime, end_time: datetime, elapsed_str: str):
        with open(f"request_count.log", "a") as f:
            f.write("======================================================\n")
            f.write(f"# Log Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Elapsed Time: {elapsed_str}\n")
            f.write(f"Total Batches: {self.counts['batch']}\n")
            f.write(f"Total Requests: {self.counts['total_request']}\n")
            f.write(f"Failed Requests: {self.counts['failed_request']}\n")
            f.write(f"Endpoint Sleep Requests: {self.counts['endpoint_sleep']}\n")
            f.write(f"Endpoint Test1 Requests: {self.counts['endpoint_test1']}\n")
            f.write(f"Endpoint Test2 Requests: {self.counts['endpoint_test2']}\n")
            f.write(f"Endpoint Fail Requests: {self.counts['endpoint_fail']}\n")
            f.write(f"Endpoint Exception Requests: {self.counts['endpoint_exception']}\n\n")



async def generate_random_request_method() -> str:
    """Generate a random request method."""
    return choice(["GET", "POST", "GET", "GET", "GET"])
    

async def get_request(client: AsyncClient, url: str) -> None:
    try:
        await client.get(url, timeout=Timeout(1.0))
    except Exception as e:
        raise e
    

async def post_request(client: AsyncClient, url: str) -> None:
    try:
        await client.post(url, timeout=Timeout(1.0))
    except Exception as e:
        raise e
    

async def send_to_sleep(client: AsyncClient, count: Count, current_request_number: int):

    url: str = "http://localhost:5050/sleep/{}"
    wait_time: float = round(random(), 2)  # Random wait time between 0 and 1 second

    try:
        await get_request(client, url.format(wait_time))
        log_info(f"##### {current_request_number}. Sleep request sent successfully with wait time: {wait_time} seconds")
    except Exception as e:
        log_error(f"===== {current_request_number}. Sleep request error: {e}")
        count.increment("failed_request")
    finally:
        count.increment("total_request")
        count.increment("endpoint_sleep")

async def send_to_test1(client: AsyncClient, count: Count, current_request_number: int):

    url: str = "http://localhost:5050/test1"

    try:
        if await generate_random_request_method() == "GET":
            await get_request(client, url)
            log_info(f"##### {current_request_number}. Test1 [GET] request sent successfully")
        else:
            await post_request(client, url)
            log_info(f"##### {current_request_number}. Test1 [POST] request sent successfully")

    except Exception as e:
        count.increment("failed_request")
        log_error(f"===== {current_request_number}. Test1 request error: {e}")
    finally:
        count.increment("endpoint_test1")
        count.increment("total_request")


async def send_to_test2(client: AsyncClient, count: Count, current_request_number: int):

    url: str = "http://localhost:5050/test2"

    try:
        if await generate_random_request_method() == "GET":
            await get_request(client, url)
            log_info(f"##### {current_request_number}. Test2 [GET] request sent successfully")
        else:
            await post_request(client, url)
            log_info(f"##### {current_request_number}. Test2 [POST] request sent successfully")

    except Exception as e:
        log_error(f"===== {current_request_number}. Test2 request error: {e}")
        count.increment("failed_request")
    finally:
        count.increment("endpoint_test2")
        count.increment("total_request")


async def send_to_fail(client: AsyncClient, wait_event: Event, count: Count):
    
    url: str = "http://localhost:5050/fail-request"

    while not wait_event.is_set():
        current_request_number: int = count.get("total_request")
        sleep_time: float = randint(5, 10)
        try:
            await get_request(client, url)
            count.increment("endpoint_fail")
            log_info(f"{current_request_number}. Fail request sent successfully")
        except Exception as e:
            count.increment("failed_request")
            log_error(f"===== {current_request_number}. Fail request error: {e}")
        finally:
            count.increment("total_request")
            await sleep(sleep_time)


async def send_to_exception(client: AsyncClient, wait_event: Event, count: Count):
    url: str = "http://localhost:5050/raise-exception"

    while not wait_event.is_set():
        current_request_number: int = count.get("total_request")
        sleep_time: float = randint(5, 10)
        try:
            await get_request(client, url)
            count.increment("endpoint_exception")
            log_info(f"{current_request_number}. Exception request sent successfully")
        except Exception as e:
            count.increment("failed_request")
            log_error(f"===== {current_request_number}. Exception request error: {e}")
        finally:
            count.increment("total_request")
            await sleep(sleep_time)


async def update_progress(time: int, wait_event: Event, task_id: TaskID, progress: Progress, count: Count) -> None:
    log_info(f"Timer started for {time} seconds")
    frame: float = 0.3
    for _ in range(int(time / frame)):
        await sleep(frame)
        progress.update(task_id, advance=frame)
        desc = await get_pbar_description(count)
        progress.console.clear()
        progress.console.print(desc)
        progress.refresh()
    else:
        progress.update(task_id, completed= time)

async def timer(time: int, wait_event: Event) -> None:
    log_info(f"Timer started for {time} seconds")
    await sleep(time)
    log_info("Timer finished")

    wait_event.set()


async def batch_of_sleep(client: AsyncClient, batch_size: int, count: Count) -> list:
    log_info(f"Sending batch of {batch_size} SLEEP requests")
    batch: list = []

    for _ in range(batch_size):
        batch.append(send_to_sleep(client, count, count.get("total_request")))

    return batch


async def batch_of_test1(client: AsyncClient, batch_size: int, count: Count) -> list:
    log_info(f"Sending batch of {batch_size} TEST1 requests")
    batch: list = []

    for _ in range(batch_size):
        batch.append(send_to_test1(client, count, count.get("total_request")))

    return batch


async def batch_of_test2(client: AsyncClient, batch_size: int, count: Count) -> list:

    log_info(f"Sending batch of {batch_size} TEST2 requests")
    batch: list = []

    for _ in range(batch_size):
        batch.append(send_to_test2(client, count, count.get("total_request")))

    return batch


async def get_random_batch_size() -> int:
    """Generate a random batch size between 0 and 15."""
    return choice(range(0, 15))


async def send_batch(client: AsyncClient, count: Count) -> None:

    sleep_batch: list = await batch_of_sleep(client, await get_random_batch_size(), count)
    test1_batch: list = await batch_of_test1(client, await get_random_batch_size(), count)
    test2_batch: list = await batch_of_test2(client, await get_random_batch_size(), count)

    await gather(*sleep_batch, *test1_batch, *test2_batch)

async def log_data(count: Count, start_time: datetime) -> None:
    """Log the current state of the count."""
    log_info("Logging current state...")
    log_info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    end_time = datetime.now()
    log_info(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    elapsed = end_time - start_time
    elapsed_str = str(elapsed).split('.')[0]
    log_info(f"Elapsed Time: {elapsed_str}")

    log_info(f"Total Requests: {count.get('total_request')}")
    log_info(f"Failed Requests: {count.get('failed_request')}")
    log_info(f"Endpoint Sleep Requests: {count.get('endpoint_sleep')}")
    log_info(f"Endpoint Test1 Requests: {count.get('endpoint_test1')}")
    log_info(f"Endpoint Test2 Requests: {count.get('endpoint_test2')}")
    log_info(f"Endpoint Fail Requests: {count.get('endpoint_fail')}")
    log_info(f"Endpoint Exception Requests: {count.get('endpoint_exception')}")

    count.log_to_file(start_time, end_time, elapsed_str)

async def get_pbar_description(count: Count) -> str:
    return "\n".join([
        f"Total Batch: {count.get('batch')}",
        f"Total Requests: {count.get('total_request')}",
        f"Failed Requests: {count.get('failed_request')}",
        f"Endpoint Sleep: {count.get('endpoint_sleep')}",
        f"Endpoint Test1: {count.get('endpoint_test1')}",
        f"Endpoint Test2: {count.get('endpoint_test2')}",
        f"Endpoint Fail: {count.get('endpoint_fail')}",
        f"Endpoint Exception: {count.get('endpoint_exception')}",
    ])

async def main(count: Count, start_time: datetime = None) -> None:
    
    log_info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    TIME: int = 500

    seed()  # Initialize random number generator

    wait_event = Event()  

    progress = Progress(
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    )

    task_id: TaskID = progress.add_task("Sending requests", total=TIME)
    
    with Live(progress, refresh_per_second=1) as pbar:
        async with AsyncClient() as client:
            create_task(timer(TIME, wait_event))
            create_task(update_progress(TIME, wait_event, task_id, progress, count))
            create_task(send_to_fail(client, wait_event, count))
            create_task(send_to_exception(client, wait_event, count))    

            log_info("Starting to send batches of requests...")

            while not wait_event.is_set():
                try:
                    await send_batch(client, count)
                    elapsed_time = datetime.now() - start_time
                    elapsed_str = str(elapsed_time).split('.')[0]  # Remove microseconds
                    log_info(f"\n@@@@@@@ Batch {count.get('batch')} Successful. Current requests count: {count.get('total_request')}, elapsed time: {elapsed_str}\n")

                except Exception as e:
                    log_error(f"(())(())Error in Batch {count.get('batch')}: {e}")

                finally:
                    # Sleep for a short time to avoid overwhelming the server
                    await sleep(.1)
                    count.increment("batch")

            else:
                log_info("Wait Event is set, stopping all tasks.")
                log_info("======================================================")
                await log_data(count, start_time)
            

if __name__ == "__main__":
    count: Count = Count() 
    start_time: datetime = datetime.now()
    try:
        run(main(count, start_time))
    except KeyboardInterrupt:
        log_info("=======================================================")
        log_info("Keyboard Interrupt detected. Stopping all tasks...")
        run(log_data(count, start_time))
        exit(0)
