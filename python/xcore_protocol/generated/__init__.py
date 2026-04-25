"""Generated canonical protocol models for the supported subset."""

from .maps import (
    MapsListRequestV1,
    MapsListResponseV1,
    MapsLoadCommandV1,
    MapsRemoveRequestV1,
    MapsRemoveResponseV1,
)
from .chat import (
    ChatDiscordIngressCommandV1,
    ChatGlobalV1,
    ChatMessageV1,
    PlayerJoinLeaveV1,
    ServerActionV1,
    ServerHeartbeatV1,
)
from .routes import (
    MAPS_LIST_REQUEST_V1,
    MAPS_REMOVE_REQUEST_V1,
    MAPS_LOAD_COMMAND_V1,
    CHAT_MESSAGE_V1,
    CHAT_GLOBAL_V1,
    CHAT_DISCORD_INGRESS_COMMAND_V1,
    SERVER_ACTION_V1,
    PLAYER_JOIN_LEAVE_V1,
    SERVER_HEARTBEAT_V1,
    RouteDescriptor,
    RouteResponseDescriptor,
    ROUTES_BY_MESSAGE,
    MapsRouteDescriptor,
    MapsRouteResponseDescriptor,
    MAPS_ROUTES_BY_MESSAGE,
)
from .shared import (
    MapEntryV1,
    MapFileSourceV1,
)

__all__ = [
    "MapEntryV1",
    "MapFileSourceV1",
    "MapsListRequestV1",
    "MapsListResponseV1",
    "MapsLoadCommandV1",
    "MapsRemoveRequestV1",
    "MapsRemoveResponseV1",
    "ChatDiscordIngressCommandV1",
    "ChatGlobalV1",
    "ChatMessageV1",
    "PlayerJoinLeaveV1",
    "ServerActionV1",
    "ServerHeartbeatV1",
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
