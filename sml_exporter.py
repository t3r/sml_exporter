#!/usr/bin/python3

import sys
import logging
from prometheus_client import Gauge, start_http_server
import asyncio
import logging
from sys import argv
from sml import SmlSequence, SmlGetListResponse
from sml.asyncio import SmlProtocol
import yaml

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_file: str) -> any:
    try:
        with open(config_file, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Error loading config file {config_file}: {e}")
        sys.exit(1)

class SmlEvent:
    def __init__(self, metrics):
      self._metrics = metrics

    def event(self, message_body: SmlSequence) -> None:
        assert isinstance(message_body, SmlGetListResponse)
        for val in message_body.get('valList', []):
            name = val.get('objName')
            if name:
                logger.info("OBIS: %s", val)
                target = self._metrics.get(name)
                if target:
                    logger.info("Gauge found for %s", name)
                    value = val.get('value')
                    if value is None:
                        logger.warning("No value found for %s", name)
                    else:
                        factor = target.get('factor', 1)
                        logger.info("Value found for %s: %s with factor %s", name, value, factor)
                        target.get('gauge').set(value * factor)


def main(config: any) -> None:
    logger.setLevel(config.get('log_level', 'WARNING'))
    metrics = {}
    for entry in config.get('metrics', []):
        logger.info(f"Creating gauge for {entry}")
        gauge = Gauge(name=entry['name'],
                      documentation=entry['description'],
                      unit=entry['unit'])
        metrics[entry['obis_name']] = {
            'gauge': gauge,
            'factor': entry.get('factor', 1)
        }

    server_port: int = int(config.get('server', {}).get('port', 9000))
    server_address: str = config.get('server', {}).get('address', '127.0.0.1')
    start_http_server(port=server_port, addr=server_address)
    logger.warning("Server started on %s:%d", server_address, server_port)

    device = config.get('sml', {}).get('device', '/dev/ttyUSB0')
    handler = SmlEvent(metrics)
    proto = SmlProtocol(device)
    logger.warning("Connecting to %s", device)
    proto.add_listener(handler.event, ['SmlGetListResponse'])
    loop = asyncio.get_event_loop()
    loop.run_until_complete(proto.connect(loop))
    loop.run_forever()


if __name__ == '__main__':
    # Read config file from command line argument, default to "config.yml"
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.yml"
    config = load_config(config_file)

    main(config)
