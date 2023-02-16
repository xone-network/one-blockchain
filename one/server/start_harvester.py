from __future__ import annotations

import pathlib
import sys
from typing import Any, Dict, Optional

from one.consensus.constants import ConsensusConstants
from one.consensus.default_constants import DEFAULT_CONSTANTS
from one.harvester.harvester import Harvester
from one.harvester.harvester_api import HarvesterAPI
from one.rpc.harvester_rpc_api import HarvesterRpcApi
from one.server.outbound_message import NodeType
from one.server.start_service import RpcInfo, Service, async_run
from one.types.peer_info import PeerInfo
from one.util.one_logging import initialize_service_logging
from one.util.config import load_config, load_config_cli
from one.util.default_root import DEFAULT_ROOT_PATH
from one.util.network import get_host_addr

# See: https://bugs.python.org/issue29288
"".encode("idna")

SERVICE_NAME = "harvester"


def create_harvester_service(
    root_path: pathlib.Path,
    config: Dict[str, Any],
    consensus_constants: ConsensusConstants,
    farmer_peer: Optional[PeerInfo],
    connect_to_daemon: bool = True,
) -> Service[Harvester]:
    service_config = config[SERVICE_NAME]

    overrides = service_config["network_overrides"]["constants"][service_config["selected_network"]]
    updated_constants = consensus_constants.replace_str_to_bytes(**overrides)

    harvester = Harvester(root_path, service_config, updated_constants)
    peer_api = HarvesterAPI(harvester)
    network_id = service_config["selected_network"]
    rpc_info: Optional[RpcInfo] = None
    if service_config["start_rpc_server"]:
        rpc_info = (HarvesterRpcApi, service_config["rpc_port"])
    return Service(
        root_path=root_path,
        config=config,
        node=harvester,
        peer_api=peer_api,
        node_type=NodeType.HARVESTER,
        advertised_port=service_config["port"],
        service_name=SERVICE_NAME,
        server_listen_ports=[service_config["port"]],
        connect_peers=[] if farmer_peer is None else [farmer_peer],
        network_id=network_id,
        rpc_info=rpc_info,
        connect_to_daemon=connect_to_daemon,
    )


async def async_main() -> int:
    # TODO: refactor to avoid the double load
    config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
    service_config = load_config_cli(DEFAULT_ROOT_PATH, "config.yaml", SERVICE_NAME)
    config[SERVICE_NAME] = service_config
    initialize_service_logging(service_name=SERVICE_NAME, config=config)
    farmer_peer = PeerInfo(
        str(get_host_addr(service_config["farmer_peer"]["host"])), service_config["farmer_peer"]["port"]
    )
    service = create_harvester_service(DEFAULT_ROOT_PATH, config, DEFAULT_CONSTANTS, farmer_peer)
    await service.setup_process_global_state()
    await service.run()

    return 0


def main() -> int:
    return async_run(async_main())


if __name__ == "__main__":
    sys.exit(main())
