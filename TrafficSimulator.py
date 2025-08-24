## Stress test script for a Java application with various endpoints.

from asyncio import CancelledError, sleep, create_task, run, gather, Event, Lock
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
            "endpoint_instant": 0,
            "endpoint_stream": 0,
            "endpoint_fail": 0,
            "endpoint_exception": 0,
            "batch": 0
        }
        self.lock = Lock()


    async def increment(self, key: str):
        """Increment the count for a specific key."""
        async with self.lock:
            if key in self.counts:
                self.counts[key] += 1
            else:
                raise KeyError(f"Invalid key: {key}")
    
    async def get(self, key: str, for_assignment: bool = False) -> int:
        """Get the count for a specific key."""
        async with self.lock:
            if key in self.counts:
                if for_assignment:
                    self.counts[key] += 1
                return self.counts[key]
            else:
                raise KeyError(f"Invalid key: {key}")
    

    async def log_to_file(self, start_time: datetime, end_time: datetime, elapsed_str: str):
        with open("request_count.log", "a") as f:
            f.write("======================================================\n")
            f.write(f"# Log Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Elapsed Time: {elapsed_str}\n")
            f.write(f"Total Batches: {self.counts['batch']}\n")
            f.write(f"Total Requests: {self.counts['total_request']}\n")
            f.write(f"Failed Requests: {self.counts['failed_request']}\n")
            f.write(f"Endpoint Sleep Requests: {self.counts['endpoint_sleep']}\n")
            f.write(f"Endpoint Instant Requests: {self.counts['endpoint_instant']}\n")
            f.write(f"Endpoint Stream Requests: {self.counts['endpoint_stream']}\n")
            f.write(f"Endpoint Fail Requests: {self.counts['endpoint_fail']}\n")
            f.write(f"Endpoint Exception Requests: {self.counts['endpoint_exception']}\n\n")

class TrafficSimulator:
    def __init__(self, client: AsyncClient):
        self.client = client
        self.count = Count()
        self.start_time = datetime.now()
        self.wait_event = Event()
        self.service_url = "http://localhost:5050"

    async def generate_random_request_method(self) -> str:
        """Generate a random request method."""
        return choice(["GET", "POST", "GET", "GET", "GET"])
        

    async def get_request(self, url: str) -> None:
        await self.client.get(url, timeout=Timeout(1.0))
        

    async def post_request(self, url: str) -> None:
        await self.client.post(url, timeout=Timeout(1.0))
        

    async def send_to_sleep(self, current_request_number: int):

        url: str = f"{self.service_url}/sleep/{{}}"
        wait_time: float = round(random() * 2, 2)  # Random wait time between 0 and 1 second

        try:
            await self.get_request(url.format(wait_time))
            log_info(f"##### {current_request_number}. Sleep request sent successfully with wait time: {wait_time} seconds")
        except Exception as e:
            log_error(f"===== {current_request_number}. Sleep request error: {e}")
            await self.count.increment("failed_request")
        finally:
            await self.count.increment("endpoint_sleep")

    async def send_to_instant(self, current_request_number: int):

        url: str = f"{self.service_url}/instant"

        try:
            if await self.generate_random_request_method() == "GET":
                await self.get_request(url)
                log_info(f"##### {current_request_number}. Instant [GET] request sent successfully")
            else:
                await self.post_request(url)
                log_info(f"##### {current_request_number}. Instant [POST] request sent successfully")

        except Exception as e:
            await self.count.increment("failed_request")
            log_error(f"===== {current_request_number}. Instant request error: {e}")
        finally:
            await self.count.increment("endpoint_instant")
            
    async def get_random_parameters(self) -> tuple[int, int, int]:
        sizeMb: int = randint(1, 10)
        chunkKb: int = choice([256, 512, 1024, 2048, 4096, 8192])
        bytesPerSecond: int = choice([3*1024*1024, 5*1024*1024, 7*1024*1024, 10*1024*1024])

        return sizeMb, chunkKb, bytesPerSecond

    async def send_to_stream(self, current_request_number: int) -> None:
        sizeMb, chunkKb, bytesPerSecond = await self.get_random_parameters()

        url: str = f"{self.service_url}/stream?sizeMb={sizeMb}&chunkKb={chunkKb}&bytesPerSec={bytesPerSecond}"

        try:
            if await self.generate_random_request_method() == "GET":
                await self.get_request(url)
                log_info(f"##### {current_request_number}. Stream [GET] request sent successfully")
            else:
                await self.post_request(url)
                log_info(f"##### {current_request_number}. Stream [POST] request sent successfully")

        except Exception as e:
            log_error(f"===== {current_request_number}. Stream request error: {e}")
            await self.count.increment("failed_request")
        finally:
            await self.count.increment("endpoint_stream")


    async def send_to_fail(self, wait_event: Event):

        url: str = f"{self.service_url}/fail-request"

        while not wait_event.is_set():
            current_request_number: int = await self.count.get("total_request", True)
            sleep_time: float = randint(5, 10)
            try:
                await self.get_request(url)
                await self.count.increment("endpoint_fail")
                log_info(f"{current_request_number}. Fail request sent successfully")
            except Exception as e:
                await self.count.increment("failed_request")
                log_error(f"===== {current_request_number}. Fail request error: {e}")
            finally:
                await sleep(sleep_time)


    async def send_to_exception(self, wait_event: Event):
        url: str = f"{self.service_url}/raise-exception"

        while not wait_event.is_set():
            current_request_number: int = await self.count.get("total_request", True)
            sleep_time: float = randint(5, 10)
            try:
                await self.get_request(url)
                await self.count.increment("endpoint_exception")
                log_info(f"{current_request_number}. Exception request sent successfully")
            except Exception as e:
                await self.count.increment("failed_request")
                log_error(f"===== {current_request_number}. Exception request error: {e}")
            finally:
                await sleep(sleep_time)


    async def update_progress(self, time: int, task_id: TaskID, progress: Progress) -> None:
        log_info(f"Timer started for {time} seconds")
        frame: float = 0.3
        for _ in range(int(time / frame)):
            await sleep(frame)
            progress.update(task_id, advance=frame)
            desc = await self.get_pbar_description()
            progress.console.clear()
            progress.console.print(desc)
            progress.refresh()
        else:
            progress.update(task_id, completed= time)

    async def timer(self, time: int, wait_event: Event) -> None:
        log_info(f"Timer started for {time} seconds")
        await sleep(time)
        log_info("Timer finished")

        wait_event.set()


    async def batch_of_sleep(self, batch_size: int) -> list:
        log_info(f"Sending batch of {batch_size} SLEEP requests")
        batch: list = []

        for _ in range(batch_size):
            batch.append(self.send_to_sleep(await self.count.get("total_request", True)))

        return batch


    async def batch_of_instant(self, batch_size: int) -> list:
        log_info(f"Sending batch of {batch_size} Instant requests")
        batch: list = []

        for _ in range(batch_size):
            batch.append(self.send_to_instant(await self.count.get("total_request", True)))

        return batch


    async def batch_of_stream(self, batch_size: int) -> list:

        log_info(f"Sending batch of {batch_size} Stream requests")
        batch: list = []

        for _ in range(batch_size):
            batch.append(self.send_to_stream(await self.count.get("total_request", True)))

        return batch


    async def get_random_batch_size(self) -> int:
        """Generate a random batch size between 0 and 15."""
        return choice(range(0, 15))


    async def send_batch(self) -> None:

        sleep_batch: list = await self.batch_of_sleep(await self.get_random_batch_size())
        instant_batch: list = await self.batch_of_instant(await self.get_random_batch_size())
        stream_batch: list = await self.batch_of_stream(await self.get_random_batch_size())

        await gather(*sleep_batch, *instant_batch, *stream_batch)

    async def log_data(self) -> None:
        """Log the current state of the count."""
        log_info("Logging current state...")
        log_info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        end_time = datetime.now()
        log_info(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        elapsed = end_time - self.start_time
        elapsed_str = str(elapsed).split('.')[0]
        log_info(f"Elapsed Time: {elapsed_str}")
        
        log_info(f"Total Batches: {await self.count.get('batch')}")
        log_info(f"Total Requests: {await self.count.get('total_request')}")
        log_info(f"Failed Requests: {await self.count.get('failed_request')}")
        log_info(f"Endpoint Sleep Requests: {await self.count.get('endpoint_sleep')}")
        log_info(f"Endpoint Instant Requests: {await self.count.get('endpoint_instant')}")
        log_info(f"Endpoint Stream Requests: {await self.count.get('endpoint_stream')}")
        log_info(f"Endpoint Fail Requests: {await self.count.get('endpoint_fail')}")
        log_info(f"Endpoint Exception Requests: {await self.count.get('endpoint_exception')}")

        await self.count.log_to_file(self.start_time, end_time, elapsed_str)

    async def get_pbar_description(self) -> str:
        return "\n".join([
            f"Total Batch: {await self.count.get('batch')}",
            f"Total Requests: {await self.count.get('total_request')}",
            f"Failed Requests: {await self.count.get('failed_request')}",
            f"Endpoint Sleep: {await self.count.get('endpoint_sleep')}",
            f"Endpoint instant: {await self.count.get('endpoint_instant')}",
            f"Endpoint Stream: {await self.count.get('endpoint_stream')}",
            f"Endpoint Fail: {await self.count.get('endpoint_fail')}",
            f"Endpoint Exception: {await self.count.get('endpoint_exception')}",
        ])

    async def start(self) -> None:

        log_info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        TIME: int = 1800

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
        progress.console.clear()  # Clear the console before starting the progress bar
        with Live(progress, refresh_per_second=1) as _:
            create_task(self.timer(TIME, wait_event))
            create_task(self.update_progress(TIME, task_id, progress))
            create_task(self.send_to_fail(wait_event))
            create_task(self.send_to_exception(wait_event))

            log_info("Starting to send batches of requests...")

            while not wait_event.is_set():
                try:
                    await self.send_batch()
                    elapsed_time = datetime.now() - self.start_time
                    elapsed_str = str(elapsed_time).split('.')[0]  # Remove microseconds
                    log_info(f"\n@@@@@@@ Batch {await self.count.get('batch')} Successful. Current requests count: {await self.count.get('total_request')}, elapsed time: {elapsed_str}\n")

                except Exception as e:
                    log_error(f"(())(())Error in Batch {await self.count.get('batch')}: {e}")

                finally:
                    # Sleep for a short time to avoid overwhelming the server
                    await sleep(.1)
                    await self.count.increment("batch")

            else:
                log_info("Wait Event is set, stopping all tasks.")
                log_info("======================================================")
                await self.log_data()


async def main():
    async with AsyncClient() as client:
        try:
            traffic_simulator = TrafficSimulator(client)
            await traffic_simulator.start()
        except CancelledError:
            log_info("Operation cancelled, stopping all tasks.")
            await traffic_simulator.log_data()


if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        exit(0)