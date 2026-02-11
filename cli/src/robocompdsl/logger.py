
import logging
from rich.logging import RichHandler

FORMAT = "%(asctime)s [%(filename)s:%(lineno)s - %(funcName)20s()] %(message)s"
logging.basicConfig(
    level=logging.INFO, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

logger = logging.getLogger("robocompdsl")
