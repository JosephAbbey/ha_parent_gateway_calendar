"""API for Parent Gateway Calendar."""

import logging
from typing import Any, Literal
from datetime import datetime

from homeassistant.core import HomeAssistant

import requests

from .exceptions import ParentGatewayCalendarApiError


def headers():
    """Return headers for Parent Gateway Calendar API requests."""
    return {
        "Accept": "application/json",
    }


_LOGGER = logging.getLogger(__name__)


def _raise_if_error(result: Any | dict[str, Any]) -> None:
    """Raise a ParentGatewayCalendarApiError if the response contains an error."""
    if not (isinstance(result, list) or isinstance(result, dict)):
        raise ParentGatewayCalendarApiError(
            f"Parent Gateway Calendar API replied with unexpected response: {result}"
        )
    if (isinstance(result, dict)) and (error := result.get("error")):
        if isinstance(error, dict):
            message = error.get("message", "Unknown Error")
            raise ParentGatewayCalendarApiError(
                f"Parent Gateway Calendar API response: {message}"
            )
        if isinstance(error, str):
            raise ParentGatewayCalendarApiError(
                f"Parent Gateway Calendar API response: {error}"
            )
        raise ParentGatewayCalendarApiError(
            f"Parent Gateway Calendar API response: {error}"
        )


class AsyncConfigEntryAuth:
    """Provide Parent Gateway Calendar tied to a config entry."""

    def __init__(self, hass: HomeAssistant, domain: str) -> None:
        """Initialize Parent Gateway Calendar Auth."""
        self._hass = hass
        self._domain = domain

    async def list_events(self, start: datetime, end: datetime):
        """Get this week's events."""
        cachebuster = datetime.now().timestamp()
        start_encoded = requests.utils.quote(start.isoformat())
        end_encoded = requests.utils.quote(end.isoformat())
        response = await self._execute(
            "GET",
            f"https://{self._domain}/calendar/handlers/getcalendar.ashx?cachebuster={cachebuster}&start={start_encoded}&end={end_encoded}",
        )
        return response

    async def _execute(
        self,
        method: (
            Literal["GET"]
            | Literal["POST"]
            | Literal["PUT"]
            | Literal["DELETE"]
            | Literal["OPTIONS"]
            | Literal["PATCH"]
            | Literal["HEAD"]
        ),
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
            raise ParentGatewayCalendarApiError(
                "Could not connect to Parent Gateway Calendar API"
            ) from err
        except requests.Timeout as err:
            raise ParentGatewayCalendarApiError(
                "Timeout connecting to Parent Gateway Calendar API"
            ) from err
        r = None
        try:
            r = result.json()
        except requests.JSONDecodeError:
            r = result.text
        if r:
            _raise_if_error(r)
        return r
