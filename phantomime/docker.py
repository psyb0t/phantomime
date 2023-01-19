import docker
import logging
from . import utils

_log = logging.getLogger(__package__)
_container = None


def start_container(driver: str, selenium_hub_port: int) -> int:
    if _container is not None:
        raise Exception("docker container already running")

    client = docker.from_env()
    selenium_hub_port = utils.get_random_ephemeral_port()

    image_name = f"selenium/standalone-{driver}: latest"

    _log.debug(
        f"starting docker container based on {image_name} exposing hub port on {selenium_hub_port}")

    global _container
    _container = client.containers.run(image_name,
                                       ports={4444: (
                                           '127.0.0.1', selenium_hub_port)},
                                       detach=True)

    return selenium_hub_port


def stop_container():
    if _container is None:
        return

    _log.debug("stopping docker container")
    _container.stop()

    _log.debug("removing docker container")
    _container.remove()

    global _container
    _container = None
