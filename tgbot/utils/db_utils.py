from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_session_pool
from tgbot.config import Config


async def get_repo_generator(config: Config):
    session_pool = await create_session_pool(config.db)
    async with session_pool() as session:
        yield RequestsRepo(session)

async def get_repo(config: Config) -> RequestsRepo:
    async for repo in get_repo_generator(config):
        return repo
