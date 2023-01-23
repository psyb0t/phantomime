import docker
import logging
from . import utils
from . import decorators

_log = logging.getLogger(__package__)
_container = None


@decorators._must_have_supported_driver_type
def _start_container(driver_type: str) -> int:
    global _container
    if _container is not None:
        raise Exception("docker container already running")

    client = docker.from_env()
    selenium_hub_port = utils.get_random_ephemeral_port()

    image_name = f"selenium/standalone-{driver_type.lower()}"

    _log.debug(
        f"starting docker container based on {image_name} exposing hub port on {selenium_hub_port}")

    _container = client.containers.run(image_name,
                                       ports={
                                           4444: ('127.0.0.1', selenium_hub_port),
                                           # 7900: ('127.0.0.1', 7900)
                                       },
                                       shm_size="2g",
                                       detach=True)

    return selenium_hub_port


def _stop_container():
    global _container
    if _container is None:
        return

    _log.debug("stopping docker container")
    _container.stop()

    _log.debug("removing docker container")
    _container.remove()

    _container = None
