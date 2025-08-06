from asyncio import sleep, create_task, run, gather, Event
from datetime import datetime
from httpx import AsyncClient, Timeout
from logging import info as log_info, error as log_error, basicConfig, getLogger
from random import randint, random, seed
from secrets import choice

basicConfig(level="INFO", format="%(asctime)s - %(levelname)s - %(message)s") # Configure logging
getLogger("httpx").setLevel("ERROR")  # Suppress httpx logs

class Count:
    def __init__(self, init_value: int):
        self.value = init_value

    def increment(self):
        self.value += 1

    def get_value(self) -> int:
        return self.value


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
    

async def send_to_sleep(client: AsyncClient, count: int):

    url: str = "http://localhost:5050/sleep/{}"
    wait_time: float = round(random(), 2)  # Random wait time between 0 and 1 second

    try:
        await get_request(client, url.format(wait_time))
        log_info(f"##### {count}. Sleep request sent successfully with wait time: {wait_time} seconds")
    except Exception as e:
        log_error(f"##### {count}. Sleep request error: {e}")


async def send_to_test1(client: AsyncClient, count: int):

    url: str = "http://localhost:5050/test1"

    try:
        if await generate_random_request_method() == "GET":
            await get_request(client, url)
        else:
            await post_request(client, url)

        log_info(f"##### {count}. Test1 request sent successfully")

    except Exception as e:
        log_error(f"##### {count}. Test1 request error: {e}")


async def send_to_test2(client: AsyncClient, count: int):

    url: str = "http://localhost:5050/test2"

    try:
        if await generate_random_request_method() == "GET":
            await get_request(client, url)
        else:
            await post_request(client, url)

        log_info(f"##### {count}. Test2 request sent successfully")

    except Exception as e:
        log_error(f"##### {count}. Test2 request error: {e}")


async def send_to_fail(client: AsyncClient, wait_event: Event, count: Count):
    
    url: str = "http://localhost:5050/fail-request"

    while not wait_event.is_set():
        sleep_time: float = randint(5, 10)
        try:
            await get_request(client, url)
            log_info(f"{count.get_value()}. Fail request sent successfully")
        except Exception as e:
            log_error(f"##### {count.get_value()}. Fail request error: {e}")
        finally:
            count.increment()
            await sleep(sleep_time)


async def send_to_exception(client: AsyncClient, wait_event: Event, count: Count):
    url: str = "http://localhost:5050/raise-exception"

    while not wait_event.is_set():
        sleep_time: float = randint(5, 10)
        try:
            await get_request(client, url)
            log_info(f"{count.get_value()}. Exception request sent successfully")
        except Exception as e:
            log_error(f"##### {count.get_value()}. Exception request error: {e}")
        finally:
            count.increment()
            await sleep(sleep_time)  


async def timer(time: int, wait_event: Event) -> None:
    log_info(f"Timer started for {time} seconds")
    await sleep(time)
    log_info("Timer finished")

    wait_event.set()


async def batch_of_sleep(client: AsyncClient, batch_size: int, count: Count) -> list:
    log_info(f"Sending batch of {batch_size} SLEEP requests")
    batch: list = []

    for _ in range(batch_size):
        # create_task(send_to_sleep(client, count.get_value()))
        batch.append(send_to_sleep(client, count.get_value()))
        count.increment()

    return batch


async def batch_of_test1(client: AsyncClient, batch_size: int, count: Count) -> list:
    log_info(f"Sending batch of {batch_size} TEST1 requests")
    batch: list = []

    for _ in range(batch_size):
        batch.append(send_to_test1(client, count.get_value()))
        count.increment()
    
    return batch


async def batch_of_test2(client: AsyncClient, batch_size: int, count: Count) -> list:

    log_info(f"Sending batch of {batch_size} TEST2 requests")
    batch: list = []

    for _ in range(batch_size):
        batch.append(send_to_test2(client, count.get_value()))
        count.increment()

    return batch


async def get_random_batch_size() -> int:
    """Generate a random batch size between 0 and 15."""
    return choice(range(0, 15))


async def send_batch(client: AsyncClient, count: Count) -> list:

    sleep_batch: list = await batch_of_sleep(client, await get_random_batch_size(), count)
    test1_batch: list = await batch_of_test1(client, await get_random_batch_size(), count)
    test2_batch: list = await batch_of_test2(client, await get_random_batch_size(), count)

    await gather(*sleep_batch, *test1_batch, *test2_batch)


async def main():
    start_time: datetime = datetime.now()
    log_info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    TIME: int = 1800 

    seed()  # Initialize random number generator

    wait_event = Event()

    create_task(timer(TIME, wait_event))

    count: Count = Count(1)

    async with AsyncClient() as client:

        create_task(send_to_fail(client, wait_event, count))
        create_task(send_to_exception(client, wait_event, count))    

        batch_count: int = 1

        log_info("Starting to send batches of requests...")

        while not wait_event.is_set():
            try:
                await send_batch(client, count)
                elapsed_time = datetime.now() - start_time
                elapsed_str = str(elapsed_time).split('.')[0]  # Remove microseconds
                log_info(f"\n@@@@@@@ Batch {batch_count} Successful. Current requests count: {count.get_value()}, elapsed time: {elapsed_str}\n")

            except Exception as e:
                log_error(f"Error in Batch {batch_count}: {e}")

            finally:
                # Sleep for a short time to avoid overwhelming the server
                await sleep(.1)
                batch_count += 1

        else:
            log_info("Wait Event is set, stopping all tasks.")
            log_info(f"Total batches sent: {batch_count - 1}")
            log_info(f"Total requests sent: {count.get_value()}")

            log_info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            log_info(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            total_elapsed = datetime.now() - start_time
            total_elapsed_str = str(total_elapsed).split('.')[0]  # Remove microseconds
            log_info(f"Total elapsed time: {total_elapsed_str}")
        

if __name__ == "__main__":
    run(main())
