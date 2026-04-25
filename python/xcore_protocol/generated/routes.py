"""Generated canonical route descriptors."""

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

from .chat import (
    ChatMessageV1,
    ChatGlobalV1,
    ChatDiscordIngressCommandV1,
    ServerActionV1,
    PlayerJoinLeaveV1,
    ServerHeartbeatV1,
)

@dataclass(frozen=True, slots=True)
class RouteResponseDescriptor:
    messageType: str
    messageVersion: int
    payloadType: type[Any]
    stream: str


@dataclass(frozen=True, slots=True)
class RouteDescriptor:
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
    response: RouteResponseDescriptor | None = None

MAPS_LIST_REQUEST_V1 = RouteDescriptor(
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
    response=RouteResponseDescriptor(
        messageType='maps.list.response',
        messageVersion=1,
        payloadType=MapsListResponseV1,
        stream='xcore:rpc:resp:{requester}',
    ),
)

MAPS_REMOVE_REQUEST_V1 = RouteDescriptor(
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
    response=RouteResponseDescriptor(
        messageType='maps.remove.response',
        messageVersion=1,
        payloadType=MapsRemoveResponseV1,
        stream='xcore:rpc:resp:{requester}',
    ),
)

MAPS_LOAD_COMMAND_V1 = RouteDescriptor(
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

CHAT_MESSAGE_V1 = RouteDescriptor(
    family='chat',
    methodName='chatMessageV1Route',
    messageType='chat.message',
    messageVersion=1,
    payloadType=ChatMessageV1,
    kind='event',
    stream='xcore:evt:chat:message',
    targetScope='broadcast',
    ttlMs=60000,
    replayable=True,
    idempotentConsumerRecommended=False,
    owner='chat',
    response=None,
)

CHAT_GLOBAL_V1 = RouteDescriptor(
    family='chat',
    methodName='chatGlobalV1Route',
    messageType='chat.global',
    messageVersion=1,
    payloadType=ChatGlobalV1,
    kind='event',
    stream='xcore:evt:chat:global',
    targetScope='broadcast',
    ttlMs=60000,
    replayable=True,
    idempotentConsumerRecommended=False,
    owner='chat',
    response=None,
)

CHAT_DISCORD_INGRESS_COMMAND_V1 = RouteDescriptor(
    family='chat',
    methodName='chatDiscordIngressCommandV1Route',
    messageType='chat.discord-ingress.command',
    messageVersion=1,
    payloadType=ChatDiscordIngressCommandV1,
    kind='command',
    stream='xcore:cmd:discord-message:{server}',
    targetScope='server',
    ttlMs=60000,
    replayable=False,
    idempotentConsumerRecommended=True,
    owner='chat',
    response=None,
)

SERVER_ACTION_V1 = RouteDescriptor(
    family='chat',
    methodName='serverActionV1Route',
    messageType='server.action',
    messageVersion=1,
    payloadType=ServerActionV1,
    kind='event',
    stream='xcore:evt:server:action',
    targetScope='broadcast',
    ttlMs=60000,
    replayable=True,
    idempotentConsumerRecommended=False,
    owner='server-runtime',
    response=None,
)

PLAYER_JOIN_LEAVE_V1 = RouteDescriptor(
    family='chat',
    methodName='playerJoinLeaveV1Route',
    messageType='player.join-leave',
    messageVersion=1,
    payloadType=PlayerJoinLeaveV1,
    kind='event',
    stream='xcore:evt:player:joinleave',
    targetScope='broadcast',
    ttlMs=60000,
    replayable=True,
    idempotentConsumerRecommended=False,
    owner='player-session',
    response=None,
)

SERVER_HEARTBEAT_V1 = RouteDescriptor(
    family='chat',
    methodName='serverHeartbeatV1Route',
    messageType='server.heartbeat',
    messageVersion=1,
    payloadType=ServerHeartbeatV1,
    kind='event',
    stream='xcore:evt:server:heartbeat',
    targetScope='broadcast',
    ttlMs=60000,
    replayable=True,
    idempotentConsumerRecommended=False,
    owner='server-runtime',
    response=None,
)

ROUTES_BY_MESSAGE: dict[tuple[str, int], RouteDescriptor] = {
    ('maps.list.request', 1): MAPS_LIST_REQUEST_V1,
    ('maps.remove.request', 1): MAPS_REMOVE_REQUEST_V1,
    ('maps.load.command', 1): MAPS_LOAD_COMMAND_V1,
    ('chat.message', 1): CHAT_MESSAGE_V1,
    ('chat.global', 1): CHAT_GLOBAL_V1,
    ('chat.discord-ingress.command', 1): CHAT_DISCORD_INGRESS_COMMAND_V1,
    ('server.action', 1): SERVER_ACTION_V1,
    ('player.join-leave', 1): PLAYER_JOIN_LEAVE_V1,
    ('server.heartbeat', 1): SERVER_HEARTBEAT_V1,
}

MapsRouteResponseDescriptor = RouteResponseDescriptor
MapsRouteDescriptor = RouteDescriptor
MAPS_ROUTES_BY_MESSAGE = ROUTES_BY_MESSAGE

__all__ = [
    "MAPS_LIST_REQUEST_V1",
    "MAPS_REMOVE_REQUEST_V1",
    "MAPS_LOAD_COMMAND_V1",
    "CHAT_MESSAGE_V1",
    "CHAT_GLOBAL_V1",
    "CHAT_DISCORD_INGRESS_COMMAND_V1",
    "SERVER_ACTION_V1",
    "PLAYER_JOIN_LEAVE_V1",
    "SERVER_HEARTBEAT_V1",
    "RouteDescriptor",
    "RouteResponseDescriptor",
    "ROUTES_BY_MESSAGE",
    "MapsRouteDescriptor",
    "MapsRouteResponseDescriptor",
    "MAPS_ROUTES_BY_MESSAGE",
]
