import re
from dataclasses import dataclass
from typing import Optional

from aiogram.utils.markdown import hbold, hlink, hitalic
from environs import Env


@dataclass
class DbConfig:
    """
    Database configuration class.
    This class holds the settings for the database, such as host, password, port, etc.

    Attributes
    ----------
    host : str
        The host where the database server is located.
    password : str
        The password used to authenticate with the database.
    user : str
        The username used to authenticate with the database.
    database : str
        The name of the database.
    port : int
        The port where the database server is listening.
    """

    host: str
    password: str
    user: str
    database: str
    port: int = 5432

    # For SQLAlchemy
    def construct_sqlalchemy_url(self, driver="asyncpg", host=None, port=None) -> str:
        """
        Constructs and returns a SQLAlchemy URL for this database configuration.
        """
        # TODO: If you're using SQLAlchemy, move the import to the top of the file!
        from sqlalchemy.engine.url import URL

        if not host:
            host = self.host
        if not port:
            port = self.port
        uri = URL.create(
            drivername=f"postgresql+{driver}",
            username=self.user,
            password=self.password,
            host=host,
            port=port,
            database=self.database,
        )
        return uri.render_as_string(hide_password=False)

    @staticmethod
    def from_env(env: Env):
        """
        Creates the DbConfig object from environment variables.
        """
        host = env.str("DB_HOST")
        password = env.str("POSTGRES_PASSWORD")
        user = env.str("POSTGRES_USER")
        database = env.str("POSTGRES_DB")
        port = env.int("DB_PORT", 5432)
        return DbConfig(
            host=host, password=password, user=user, database=database, port=port
        )


@dataclass
class TgBot:
    """
    Creates the TgBot object from environment variables.
    """

    token: str
    admin_ids: list[int]
    use_redis: bool
    channel_id: int

    @staticmethod
    def from_env(env: Env):
        """
        Creates the TgBot object from environment variables.
        """
        token = env.str("BOT_TOKEN")
        admin_ids = env.list("ADMINS", subcast=int)
        use_redis = env.bool("USE_REDIS")
        channel_id = env.int("CHANNEL_ID")
        return TgBot(token=token, admin_ids=admin_ids, use_redis=use_redis, channel_id=channel_id)


@dataclass
class Payment:
    terminal_key: str
    password: str

    @staticmethod
    def from_env(env: Env):
        terminal_key = env.str("PAYMENT_TERMINAL_KEY")
        password = env.str("PAYMENT_PASSWORD")

        return Payment(terminal_key=terminal_key, password=password)


@dataclass
class Messages:
    """
    A class that processes HTML-formatted messages and replaces HTML tags with appropriate methods.

    Attributes
    ----------
    offer_agreement : str
        The raw HTML message for the offer agreement.
    course_intro : str
        The raw HTML message for the course introduction.
    about_course : str
        The raw HTML message for about the course.
    photo_go_intro : str
        The photo identifier for the Go course introduction.
    photo_about_course : str
        The photo identifier for the about course section.
    """

    offer_agreement: str
    course_intro: str
    about_course: str
    photo_go_intro: str
    photo_about_course: str

    @staticmethod
    def _process_message(message: str) -> str:
        """
        Processes HTML message, using real aiogram formatting functions.
        """

        message = re.sub(r'<b>(.*?)</b>', lambda m: hbold(m.group(1)), message, flags=re.DOTALL)
        message = re.sub(r'<i>(.*?)</i>', lambda m: hitalic(m.group(1)), message, flags=re.DOTALL)
        message = re.sub(r'<a href="(.*?)">(.*?)</a>', lambda m: hlink(m.group(2), m.group(1)), message, flags=re.DOTALL)
        message = message.replace('<br>', '\n')
        message = message.replace('<ul>', '').replace('</ul>', '')
        message = message.replace('<ol>', '').replace('</ol>', '')
        message = message.replace('<li>', '- ').replace('</li>', '\n')

        return message

    @staticmethod
    def from_env(env: Env) -> 'Messages':
        """
        Creates the Messages object from environment variables.

        :param env: The Env object to load environment variables from.

        :return: A Messages object with all messages loaded from environment variables.
        """
        offer_agreement = Messages._process_message(env.str("OFFER_AGREEMENT", default=""))
        course_intro = Messages._process_message(env.str("COURSE_INTRO", default=""))
        about_course = Messages._process_message(env.str("ABOUT_COURSE", default=""))
        photo_go_intro = env.str("PHOTO_GO_INTRO", default="")
        photo_about_course = env.str("PHOTO_ABOUT_COURSE", default="")

        return Messages(
            offer_agreement=offer_agreement,
            course_intro=course_intro,
            about_course=about_course,
            photo_go_intro=photo_go_intro,
            photo_about_course=photo_about_course
        )

@dataclass
class Config:
    """
    The main configuration class that integrates all the other configuration classes.

    This class holds the other configuration classes, providing a centralized point of access for all settings.

    Attributes
    ----------
    tg_bot : TgBot
        Holds the settings related to the Telegram Bot.
    db : Optional[DbConfig]
        Holds the settings specific to the database (default is None).
    redis : Optional[RedisConfig]
        Holds the settings specific to Redis (default is None).
    """

    tg_bot: TgBot
    payment: Payment
    db: Optional[DbConfig] = None
    messages: Optional[Messages] = None


def load_config(path: str = None) -> Config:
    """
    This function takes an optional file path as input and returns a Config object.
    :param path: The path of env file from where to load the configuration variables.
    It reads environment variables from a .env file if provided, else from the process environment.
    :return: Config object with attributes set as per environment variables.
    """

    # Create an Env object.
    # The Env object will be used to read environment variables.
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot.from_env(env),
        payment=Payment.from_env(env),
        db=DbConfig.from_env(env),
        messages=Messages.from_env(env)
    )
