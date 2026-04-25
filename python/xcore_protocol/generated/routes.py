"""Generated canonical maps route descriptors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .maps import (
    MapsListRequestV1,
    MapsListResponseV1,
    MapsRemoveRequestV1,
    MapsRemoveResponseV1,
    MapsLoadCommandV1,
)

@dataclass(frozen=True, slots=True)
class MapsRouteResponseDescriptor:
    messageType: str
    messageVersion: int
    payloadType: type[Any]
    stream: str


@dataclass(frozen=True, slots=True)
class MapsRouteDescriptor:
    family: str
    methodName: str
    messageType: str
    messageVersion: int
    payloadType: type[Any]
    kind: str
    stream: str
    targetScope: str
    ttlMs: int
    replayable: bool
    idempotentConsumerRecommended: bool
    owner: str
    response: MapsRouteResponseDescriptor | None = None

MAPS_LIST_REQUEST_V1 = MapsRouteDescriptor(
    family='maps',
    methodName='mapsListRequestV1Route',
    messageType='maps.list.request',
    messageVersion=1,
    payloadType=MapsListRequestV1,
    kind='rpc-request',
    stream='xcore:rpc:req:{server}',
    targetScope='server',
    ttlMs=10000,
    replayable=False,
    idempotentConsumerRecommended=False,
    owner='maps',
    response=MapsRouteResponseDescriptor(
        messageType='maps.list.response',
        messageVersion=1,
        payloadType=MapsListResponseV1,
        stream='xcore:rpc:resp:{requester}',
    ),
)

MAPS_REMOVE_REQUEST_V1 = MapsRouteDescriptor(
    family='maps',
    methodName='mapsRemoveRequestV1Route',
    messageType='maps.remove.request',
    messageVersion=1,
    payloadType=MapsRemoveRequestV1,
    kind='rpc-request',
    stream='xcore:rpc:req:{server}',
    targetScope='server',
    ttlMs=10000,
    replayable=False,
    idempotentConsumerRecommended=True,
    owner='maps',
    response=MapsRouteResponseDescriptor(
        messageType='maps.remove.response',
        messageVersion=1,
        payloadType=MapsRemoveResponseV1,
        stream='xcore:rpc:resp:{requester}',
    ),
)

MAPS_LOAD_COMMAND_V1 = MapsRouteDescriptor(
    family='maps',
    methodName='mapsLoadCommandV1Route',
    messageType='maps.load.command',
    messageVersion=1,
    payloadType=MapsLoadCommandV1,
    kind='command',
    stream='xcore:cmd:maps-load:{server}',
    targetScope='server',
    ttlMs=300000,
    replayable=False,
    idempotentConsumerRecommended=True,
    owner='maps',
    response=None,
)

MAPS_ROUTES_BY_MESSAGE: dict[tuple[str, int], MapsRouteDescriptor] = {
    ('maps.list.request', 1): MAPS_LIST_REQUEST_V1,
    ('maps.remove.request', 1): MAPS_REMOVE_REQUEST_V1,
    ('maps.load.command', 1): MAPS_LOAD_COMMAND_V1,
}

__all__ = [
    "MAPS_LIST_REQUEST_V1",
    "MAPS_REMOVE_REQUEST_V1",
    "MAPS_LOAD_COMMAND_V1",
    "MapsRouteDescriptor",
    "MapsRouteResponseDescriptor",
    "MAPS_ROUTES_BY_MESSAGE",
]
