import asyncio

async def greet(name, delay):
    await asyncio.sleep(delay)
    print(f"Hello {name}")

async def main():
    await asyncio.gather(
        greet("patient", 2),
        greet("doctor", 1)
    )

asyncio.run(main())