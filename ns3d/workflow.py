import asyncio

class Workflow:

    async def sleep(self, time):
        await asyncio.sleep(time)

    async def until(self, condition):
        print(f'workflow.until({condition}) - not yet implemented')
