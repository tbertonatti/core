"""Support for the Hive sensors."""
from datetime import timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HiveEntity
from .const import DOMAIN

PARALLEL_UPDATES = 0
SCAN_INTERVAL = timedelta(seconds=15)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="Battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Hive thermostat based on a config entry."""
    hive = hass.data[DOMAIN][entry.entry_id]
    devices = hive.session.deviceList.get("sensor")
    entities = []
    if devices:
        for description in SENSOR_TYPES:
            for dev in devices:
                if dev["hiveType"] == description.key:
                    entities.append(HiveSensorEntity(hive, dev, description))
    async_add_entities(entities, True)


class HiveSensorEntity(HiveEntity, SensorEntity):
    """Hive Sensor Entity."""

    def __init__(self, hive, hive_device, entity_description):
        """Initialise hive sensor."""
        super().__init__(hive, hive_device)
        self.entity_description = entity_description

    async def async_update(self):
        """Update all Node data from Hive."""
        await self.hive.session.updateData(self.device)
        self.device = await self.hive.sensor.getSensor(self.device)
        self._attr_native_value = self.device["status"]["state"]
