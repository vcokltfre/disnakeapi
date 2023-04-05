from os import environ

from disnake import CommandInteraction
from disnake.ext.commands import slash_command  # type: ignore

from disnakeapi import Bot, Cog, Request


class ExampleCog(Cog):
    @Cog.get("/")
    async def index(self, request: Request) -> str:
        return "Hello, world!"

    @slash_command(name="ping")
    async def ping(self, itr: CommandInteraction) -> None:
        await itr.send("Pong!")


bot = Bot(environ["HOST"], int(environ["PORT"]))
bot.add_cog(ExampleCog())
bot.run(environ["TOKEN"])
