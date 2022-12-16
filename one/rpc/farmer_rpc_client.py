from __future__ import annotations

from typing import Any, Dict, List, Optional

from one.rpc.farmer_rpc_api import PlotInfoRequestData, PlotPathRequestData
from one.rpc.rpc_client import RpcClient
from one.types.blockchain_format.sized_bytes import bytes32
from one.util.misc import dataclass_to_json_dict


class FarmerRpcClient(RpcClient):
    """
    Client to One RPC, connects to a local farmer. Uses HTTP/JSON, and converts back from
    JSON into native python objects before returning. All api calls use POST requests.
    Note that this is not the same as the peer protocol, or wallet protocol (which run One's
    protocol on top of TCP), it's a separate protocol on top of HTTP that provides easy access
    to the full node.
    """

    async def get_signage_point(self, sp_hash: bytes32) -> Optional[Dict]:
        try:
            return await self.fetch("get_signage_point", {"sp_hash": sp_hash.hex()})
        except ValueError:
            return None

    async def get_signage_points(self) -> List[Dict]:
        return (await self.fetch("get_signage_points", {}))["signage_points"]

    async def get_reward_targets(self, search_for_private_key: bool, max_ph_to_search: int = 500) -> Dict:
        response = await self.fetch(
            "get_reward_targets",
            {"search_for_private_key": search_for_private_key, "max_ph_to_search": max_ph_to_search},
        )
        return_dict = {
            "farmer_target": response["farmer_target"],
            "pool_target": response["pool_target"],
        }
        if "have_pool_sk" in response:
            return_dict["have_pool_sk"] = response["have_pool_sk"]
        if "have_farmer_sk" in response:
            return_dict["have_farmer_sk"] = response["have_farmer_sk"]
        return return_dict

    async def set_reward_targets(self, farmer_target: Optional[str] = None, pool_target: Optional[str] = None) -> Dict:
        request = {}
        if farmer_target is not None:
            request["farmer_target"] = farmer_target
        if pool_target is not None:
            request["pool_target"] = pool_target
        return await self.fetch("set_reward_targets", request)

    async def get_pool_state(self) -> Dict:
        return await self.fetch("get_pool_state", {})

    async def set_payout_instructions(self, launcher_id: bytes32, payout_instructions: str) -> Dict:
        request = {"launcher_id": launcher_id.hex(), "payout_instructions": payout_instructions}
        return await self.fetch("set_payout_instructions", request)

    async def get_harvesters(self) -> Dict[str, Any]:
        return await self.fetch("get_harvesters", {})

    async def get_harvesters_summary(self) -> Dict[str, object]:
        return await self.fetch("get_harvesters_summary", {})

    async def get_harvester_plots_valid(self, request: PlotInfoRequestData) -> Dict[str, Any]:
        return await self.fetch("get_harvester_plots_valid", dataclass_to_json_dict(request))

    async def get_harvester_plots_invalid(self, request: PlotPathRequestData) -> Dict[str, Any]:
        return await self.fetch("get_harvester_plots_invalid", dataclass_to_json_dict(request))

    async def get_harvester_plots_keys_missing(self, request: PlotPathRequestData) -> Dict[str, Any]:
        return await self.fetch("get_harvester_plots_keys_missing", dataclass_to_json_dict(request))

    async def get_harvester_plots_duplicates(self, request: PlotPathRequestData) -> Dict[str, Any]:
        return await self.fetch("get_harvester_plots_duplicates", dataclass_to_json_dict(request))

    async def get_pool_login_link(self, launcher_id: bytes32) -> Optional[str]:
        try:
            return (await self.fetch("get_pool_login_link", {"launcher_id": launcher_id.hex()}))["login_link"]
        except ValueError:
            return None
