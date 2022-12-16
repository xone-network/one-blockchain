from typing import KeysView, Generator

SERVICES_FOR_GROUP = {
    "all": (
        "one_harvester one_timelord_launcher one_timelord one_farmer "
        "one_full_node one_wallet one_data_layer one_data_layer_http"
    ).split(),
    # TODO: should this be `data_layer`?
    "data": "one_wallet one_data_layer".split(),
    "data_layer_http": "one_data_layer_http".split(),
    "node": "one_full_node".split(),
    "harvester": "one_harvester".split(),
    "farmer": "one_harvester one_farmer one_full_node one_wallet".split(),
    "farmer-no-wallet": "one_harvester one_farmer one_full_node".split(),
    "farmer-only": "one_farmer".split(),
    "timelord": "one_timelord_launcher one_timelord one_full_node".split(),
    "timelord-only": "one_timelord".split(),
    "timelord-launcher-only": "one_timelord_launcher".split(),
    "wallet": "one_wallet".split(),
    "introducer": "one_introducer".split(),
    "simulator": "one_full_node_simulator".split(),
    "crawler": "one_crawler".split(),
    "seeder": "one_crawler one_seeder".split(),
    "seeder-only": "one_seeder".split(),
}


def all_groups() -> KeysView[str]:
    return SERVICES_FOR_GROUP.keys()


def services_for_groups(groups) -> Generator[str, None, None]:
    for group in groups:
        for service in SERVICES_FOR_GROUP[group]:
            yield service


def validate_service(service: str) -> bool:
    return any(service in _ for _ in SERVICES_FOR_GROUP.values())
