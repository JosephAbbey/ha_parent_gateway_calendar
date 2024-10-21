"""Parent Gateway Calendar calendar platform."""

from __future__ import annotations

import dataclasses
import logging
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any

import pytz
from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEvent,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
)
from .coordinator import CalendarUpdateCoordinator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .api import AsyncConfigEntryAuth

_LOGGER = logging.getLogger(__name__)


def _event_dict_factory(obj: Iterable[tuple[str, Any]]) -> dict[str, str]:
    """Convert CalendarEvent dataclass items to dictionary of attributes."""
    result: dict[str, str] = {}
    for name, value in obj:
        if isinstance(value, datetime | date):
            result[name] = value.isoformat()
        elif value is not None:
            result[name] = str(value)
    return result


@dataclasses.dataclass
class ParentGatewayCalendarEvent(CalendarEvent):
    """Parent Gateway Calendar event."""

    category: str | None = None
    subcategory: str | None = None
    publicapplicabilitylist: list[str] = dataclasses.field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        """Return a dict representation of the event."""
        return {
            **dataclasses.asdict(self, dict_factory=_event_dict_factory),
            "all_day": self.all_day,
            "publicapplicabilitylist": self.publicapplicabilitylist,
        }


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Parent Gateway Calendar platform."""
    api: AsyncConfigEntryAuth = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            ParentGatewayCalendarEntity(
                CalendarUpdateCoordinator(hass, api),
                entry.entry_id,
            )
        ]
    )


class ParentGatewayCalendarEntity(
    CoordinatorEntity[CalendarUpdateCoordinator],
    CalendarEntity,
):
    """A calendar event entity."""

    _attr_name = "Parent Gateway Calendar"
    _attr_has_entity_name = True
    _attr_supported_features = 0

    def __init__(
        self,
        coordinator: CalendarUpdateCoordinator,
        config_entry_id: str,
    ) -> None:
        """Create the Calendar event device."""
        super().__init__(coordinator)
        self._attr_unique_id = config_entry_id

    def _convert_event(
        self,
        tz: (pytz._UTCclass | pytz.StaticTzInfo | pytz.DstTzInfo),
        event: dict[str, Any],
    ) -> ParentGatewayCalendarEvent:
        if event.get("allDay", False) or event.get("isallDay", False):
            return ParentGatewayCalendarEvent(
                uid=event["id"],
                summary=event["title"],
                start=datetime.fromisoformat(event["start"]).astimezone(tz=tz).date(),
                end=datetime.fromisoformat(event["end"]).astimezone(tz=tz).date() + timedelta(days=1),
                description=event["notes"],
                location=event["location"].strip("; "),
                category=event["category"],
                subcategory=event["subcategory"],
                publicapplicabilitylist=list(
                    filter(
                        lambda i: i != "", event["publicapplicabilitylist"].split(", ")
                    )
                ),
            )
        return ParentGatewayCalendarEvent(
            uid=event["id"],
            summary=event["title"],
            start=datetime.fromisoformat(event["start"]).astimezone(tz=tz),
            end=datetime.fromisoformat(event["end"]).astimezone(tz=tz),
            description=event["notes"],
            location=event["location"].strip("; "),
            category=event["category"],
            subcategory=event["subcategory"],
            publicapplicabilitylist=list(
                filter(lambda i: i != "", event["publicapplicabilitylist"].split(", "))
            ),
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the device state attributes."""
        if self.event is None:
            return {}
        return {
            "category": self.event.category,
            "subcategory": self.event.subcategory,
            "publicapplicabilitylist": self.event.publicapplicabilitylist,
        }

    @property
    def offset_reached(self) -> bool:
        """Return whether or not the event offset was reached."""
        tz = pytz.timezone(self.hass.config.time_zone)
        return (
            self.coordinator.upcoming is not None and len(self.coordinator.upcoming) > 0
        ) and (
            datetime.fromisoformat(self.coordinator.upcoming["start"])
            <= datetime.now(tz=tz)
        )

    @property
    def event(self) -> ParentGatewayCalendarEvent | None:
        """Return the next upcoming event."""
        tz = pytz.timezone(self.hass.config.time_zone)
        if self.coordinator.upcoming is not None and len(self.coordinator.upcoming) > 0:
            return self._convert_event(tz, self.coordinator.upcoming[0])
        return None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Get all events in a specific time frame."""
        tz = pytz.timezone(hass.config.time_zone)
        events = await self.coordinator.api.list_events(start_date, end_date)
        return [self._convert_event(tz, event) for event in events]
