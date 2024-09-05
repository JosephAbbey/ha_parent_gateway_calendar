"""Exceptions for Parent Gateway Calendar api calls."""

from homeassistant.exceptions import HomeAssistantError


class ParentGatewayCalendarApiError(HomeAssistantError):
    """Error talking to the Parent Gateway Calendar API."""
