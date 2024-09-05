"""The Parent Gateway Calendar integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from . import api
from .const import DOMAIN, CONF_PARENT_GATEWAY_DOMAIN

PLATFORMS: list[Platform] = [Platform.CALENDAR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Parent Gateway Calendar from a config entry."""
    auth = api.AsyncConfigEntryAuth(
        hass,
        domain=entry.data[CONF_PARENT_GATEWAY_DOMAIN],
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = auth

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
