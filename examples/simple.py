from os import environ

from disnakeapi import Bot, Cog, Request


class ExampleCog(Cog):
    @Cog.get("/")
    async def index(self, request: Request) -> str:
        return "Hello, world!"


bot = Bot(environ["HOST"], int(environ["PORT"]))
bot.add_cog(ExampleCog())
bot.run(environ["TOKEN"])
