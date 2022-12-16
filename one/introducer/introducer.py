import asyncio
import logging
import time
from typing import Any, Callable, Dict, List, Optional

from one.rpc.rpc_server import default_get_connections
from one.server.outbound_message import NodeType
from one.server.server import OneServer
from one.server.introducer_peers import VettedPeer
from one.server.ws_connection import WSOneConnection
from one.util.ints import uint64


class Introducer:
    @property
    def server(self) -> OneServer:
        # This is a stop gap until the class usage is refactored such the values of
        # integral attributes are known at creation of the instance.
        if self._server is None:
            raise RuntimeError("server not assigned")

        return self._server

    def __init__(self, max_peers_to_send: int, recent_peer_threshold: int):
        self.max_peers_to_send = max_peers_to_send
        self.recent_peer_threshold = recent_peer_threshold
        self._shut_down = False
        self._server: Optional[OneServer] = None
        self.log = logging.getLogger(__name__)

    async def _start(self):
        self._vetting_task = asyncio.create_task(self._vetting_loop())

    def _close(self):
        self._shut_down = True
        self._vetting_task.cancel()

    async def _await_closed(self):
        pass
        # await self._vetting_task

    async def on_connect(self, peer: WSOneConnection) -> None:
        pass

    def _set_state_changed_callback(self, callback: Callable):
        # TODO: fill this out?
        pass

    def get_connections(self, request_node_type: Optional[NodeType]) -> List[Dict[str, Any]]:
        return default_get_connections(server=self.server, request_node_type=request_node_type)

    def set_server(self, server: OneServer):
        self._server = server

    async def _vetting_loop(self):
        while True:
            if self._shut_down:
                return None
            try:
                for i in range(60):
                    if self._shut_down:
                        return None
                    await asyncio.sleep(1)
                self.log.info("Vetting random peers.")
                if self._server.introducer_peers is None:
                    continue
                raw_peers = self.server.introducer_peers.get_peers(100, True, 3 * self.recent_peer_threshold)

                if len(raw_peers) == 0:
                    continue

                peer: VettedPeer
                for peer in raw_peers:
                    if self._shut_down:
                        return None

                    now = time.time()

                    # if it was too long ago we checked this peer, check it
                    # again
                    if peer.vetted > 0 and now > peer.vetted_timestamp + 3600:
                        peer.vetted = 0

                    if peer.vetted > 0:
                        continue

                    # don't re-vet peers too frequently
                    if now < peer.last_attempt + 500:
                        continue

                    try:
                        peer.last_attempt = uint64(time.time())

                        self.log.info(f"Vetting peer {peer.host} {peer.port}")
                        r, w = await asyncio.wait_for(
                            asyncio.open_connection(peer.host, int(peer.port)),
                            timeout=3,
                        )
                        w.close()
                    except Exception as e:
                        self.log.warning(f"Could not vet {peer}, removing. {type(e)}{str(e)}")
                        peer.vetted = min(peer.vetted - 1, -1)

                        # if we have failed 6 times in a row, remove the peer
                        if peer.vetted < -6:
                            self.server.introducer_peers.remove(peer)
                        continue

                    self.log.info(f"Have vetted {peer} successfully!")
                    peer.vetted_timestamp = uint64(time.time())
                    peer.vetted = max(peer.vetted + 1, 1)
            except Exception as e:
                self.log.error(e)