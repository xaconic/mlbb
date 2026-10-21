"""Server-side client for the public MLBB nickname lookup endpoint."""

import json
import logging
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


logger = logging.getLogger(__name__)
API_URL = "https://api.isan.eu.org/nickname/ml"
ALT_API_URL = "https://api.isan.eu.org/nickname"
TIMEOUT_SECONDS = 8
USER_AGENT = "Mozilla/5.0 (compatible; MLBBPlayerManager/1.0)"


class LookupError(Exception):
    """A safe, user-facing MLBB lookup failure."""

    def __init__(self, message, status=502):
        self.message = message
        self.status = status
        super().__init__(message)


def _validate_identifier(value, label):
    value = str(value or "").strip()
    invalid_message = f"Please enter a valid {label}."
    if not value or not value.isdecimal() or int(value) <= 0:
        raise LookupError(invalid_message, status=400)
    number = int(value)
    maximum = 2**63 - 1 if label == "Player ID" else 2**31 - 1
    if number > maximum:
        raise LookupError(invalid_message, status=400)
    return number


def _normalize_player(payload, player_id, server_id):
    """Validate the nickname response and return supported player fields."""
    unexpected = "The MLBB lookup service returned an unexpected response."
    if not isinstance(payload, dict):
        raise LookupError(unexpected)
    if payload.get("success") is False:
        raise LookupError(
            "Player not found. Please check the Player ID and Server ID.",
            status=404,
        )
    if payload.get("success") is not True:
        logger.warning("MLBB nickname service returned an undocumented response")
        raise LookupError(unexpected)

    returned_id = payload.get("id")
    returned_server = payload.get("server")
    if returned_id is None or returned_server is None:
        raise LookupError(unexpected)
    for returned, requested in ((returned_id, player_id), (returned_server, server_id)):
        if returned is not None:
            try:
                matches_request = not isinstance(returned, bool) and int(returned) == requested
            except (TypeError, ValueError):
                matches_request = False
            if not matches_request:
                logger.warning("MLBB nickname service returned mismatched identifiers")
                raise LookupError(unexpected)

    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        logger.warning("MLBB nickname service response omitted a valid name")
        raise LookupError(unexpected)

    def optional_text(*keys):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    def optional_integer(*keys):
        for key in keys:
            value = payload.get(key)
            if value is None or isinstance(value, bool):
                continue
            try:
                number = int(str(value).strip())
            except (TypeError, ValueError):
                continue
            if number >= 0:
                return number
        return None

    def optional_percentage(*keys):
        for key in keys:
            value = payload.get(key)
            if value is None or isinstance(value, bool):
                continue
            try:
                percentage = float(str(value).strip().rstrip('%'))
            except (TypeError, ValueError):
                continue
            if 0 <= percentage <= 100:
                return percentage
        return None

    return {
        "player_id": player_id,
        "server": server_id,
        "ign": name.strip(),
        "main_role": optional_text("main_role", "mainRole", "role"),
        "current_rank": optional_text("current_rank", "currentRank"),
        "highest_rank": optional_text("highest_rank", "highestRank"),
        "current_stars": optional_integer("current_stars", "currentStars"),
        "highest_stars": optional_integer("highest_stars", "highestStars"),
        "win_rate": optional_percentage("win_rate", "winRate"),
        "level": optional_integer("level"),
        "avatar": optional_text("avatar", "avatar_url", "avatarUrl"),
    }


def _request_lookup(player_id, server_id):
    """Attempt the primary and fallback MLBB lookup endpoints."""
    candidates = [
        (
            f"{API_URL}?{urlencode({'id': player_id, 'server': server_id})}",
            {"Accept": "application/json", "User-Agent": USER_AGENT},
        ),
        (
            f"{API_URL}?{urlencode({'player_id': player_id, 'server_id': server_id})}",
            {"Accept": "application/json", "User-Agent": USER_AGENT},
        ),
        (
            f"{ALT_API_URL}?{urlencode({'id': player_id, 'server': server_id})}",
            {"Accept": "application/json", "User-Agent": USER_AGENT},
        ),
    ]
    last_error = None
    for url, headers in candidates:
        request = Request(url, headers=headers, method="GET")
        try:
            with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                if response.status == 404:
                    raise LookupError(
                        "Player not found. Please check the Player ID and Server ID.",
                        status=404,
                    )
                if response.status < 200 or response.status >= 300:
                    logger.warning("MLBB nickname service returned HTTP %s for %s", response.status, url)
                    last_error = LookupError(
                        "MLBB lookup service is temporarily unavailable.",
                        status=503,
                    )
                    continue
                try:
                    payload = json.loads(response.read().decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    raise LookupError(
                        "The MLBB lookup service returned an unexpected response."
                    ) from None
                return payload
        except HTTPError as error:
            if error.code == 404:
                raise LookupError(
                    "Player not found. Please check the Player ID and Server ID.",
                    status=404,
                ) from None
            logger.warning("MLBB nickname service returned HTTP %s for %s", error.code, url)
            last_error = LookupError(
                "The MLBB lookup provider returned HTTP %s." % error.code,
                status=502 if error.code not in (429, 503) else 503,
            )
            if error.code in (401, 403, 429, 500, 502, 503):
                continue
            raise last_error from None
        except (TimeoutError, socket.timeout):
            raise LookupError(
                "MLBB lookup request timed out. Please try again.", status=504
            ) from None
        except URLError as error:
            if isinstance(error.reason, (TimeoutError, socket.timeout)):
                raise LookupError(
                    "MLBB lookup request timed out. Please try again.", status=504
                ) from None
            logger.warning("MLBB nickname service connection failed for %s: %s", url, error.reason)
            last_error = LookupError(
                "The MLBB lookup service is temporarily unavailable. Please try again.",
                status=503,
            )
            continue
        except OSError as error:
            logger.warning("MLBB nickname service request failed for %s: %s", url, error)
            last_error = LookupError(
                "The MLBB lookup service is temporarily unavailable. Please try again.",
                status=503,
            )
            continue

    if last_error is not None:
        raise last_error
    raise LookupError("The MLBB lookup service is temporarily unavailable. Please try again.", status=503)


def lookup_player(player_id, server_id):
    """Look up a player's nickname without credentials or API keys."""
    player_id = _validate_identifier(player_id, "Player ID")
    server_id = _validate_identifier(server_id, "Server ID")
    payload = _request_lookup(player_id, server_id)
    return _normalize_player(payload, player_id, server_id)
