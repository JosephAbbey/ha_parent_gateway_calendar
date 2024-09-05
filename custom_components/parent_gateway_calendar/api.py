"""API for Parent Gateway Calendar."""

import logging
from datetime import datetime
from typing import Any, Literal

import requests
import requests.utils
from homeassistant.core import HomeAssistant

from .exceptions import ParentGatewayCalendarApiError


def headers() -> dict[str, str]:
    """Return headers for Parent Gateway Calendar API requests."""
    return {
        "Accept": "application/json",
    }


_LOGGER = logging.getLogger(__name__)


def _raise_if_error(result: Any | dict[str, Any]) -> None:
    """Raise a ParentGatewayCalendarApiError if the response contains an error."""
    if not (isinstance(result, list | dict)):
        msg = f"Parent Gateway Calendar API replied with unexpected response: {result}"
        raise ParentGatewayCalendarApiError(msg)
    if (isinstance(result, dict)) and (error := result.get("error")):
        if isinstance(error, dict):
            message = error.get("message", "Unknown Error")
            msg = f"Parent Gateway Calendar API response: {message}"
            raise ParentGatewayCalendarApiError(msg)
        if isinstance(error, str):
            msg = f"Parent Gateway Calendar API response: {error}"
            raise ParentGatewayCalendarApiError(msg)
        msg = f"Parent Gateway Calendar API response: {error}"
        raise ParentGatewayCalendarApiError(msg)


class AsyncConfigEntryAuth:
    """Provide Parent Gateway Calendar tied to a config entry."""

    def __init__(self, hass: HomeAssistant, domain: str) -> None:
        """Initialize Parent Gateway Calendar Auth."""
        self._hass = hass
        self._domain = domain

    async def list_events(self, start: datetime, end: datetime) -> list[dict[str, Any]]:
        """Get this week's events."""
        cachebuster = datetime.now().timestamp()  # noqa: DTZ005
        start_encoded = requests.utils.quote(start.isoformat())
        end_encoded = requests.utils.quote(end.isoformat())
        return await self._execute(
            "GET",
            f"https://{self._domain}/calendar/handlers/getcalendar.ashx?cachebuster={cachebuster}&start={start_encoded}&end={end_encoded}",
        )

    async def _execute(
        self,
        method: (Literal["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"]),
        path: str,
        json: Any | None = None,
    ) -> Any:
        try:
            result = await self._hass.async_add_executor_job(
                lambda: requests.request(
                    method,
                    path,
                    json=json,
                    headers=headers(),
                    timeout=10,
                )
            )
        except requests.ConnectionError as err:
            msg = "Could not connect to Parent Gateway Calendar API"
            raise ParentGatewayCalendarApiError(msg) from err
        except requests.Timeout as err:
            msg = "Timeout connecting to Parent Gateway Calendar API"
            raise ParentGatewayCalendarApiError(msg) from err
        r = None
        try:
            r = result.json()
        except requests.JSONDecodeError:
            r = result.text
        if r:
            _raise_if_error(r)
        return r
