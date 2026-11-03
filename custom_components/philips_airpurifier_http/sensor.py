"""Sensor entities for readings of a Philips air purifier.

The fan entity already polls the device; these sensors only mirror its
readings, so they do not talk to the device themselves.
"""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONF_HOST,
    CONF_NAME,
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfTime,
)

from .const import (
    ATTR_ALLERGEN_INDEX,
    ATTR_CARBON_FILTER,
    ATTR_HEPA_FILTER,
    ATTR_HUMIDITY,
    ATTR_PM25,
    ATTR_PRE_FILTER,
    ATTR_TARGET_HUMIDITY,
    ATTR_TEMPERATURE,
    ATTR_WATER_LEVEL,
    ATTR_WICK_FILTER,
    DATA_PHILIPS_FANS,
)

SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=ATTR_PM25,
        name="PM2.5",
        device_class=SensorDeviceClass.PM25,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_ALLERGEN_INDEX,
        name="Allergen index",
        icon="mdi:flower-pollen",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_HUMIDITY,
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_TARGET_HUMIDITY,
        name="Target humidity",
        icon="mdi:water-percent",
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key=ATTR_TEMPERATURE,
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_WATER_LEVEL,
        name="Water level",
        icon="mdi:cup-water",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_PRE_FILTER,
        name="Pre-filter",
        icon="mdi:air-filter",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_HEPA_FILTER,
        name="HEPA filter",
        icon="mdi:air-filter",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_CARBON_FILTER,
        name="Carbon filter",
        icon="mdi:air-filter",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_WICK_FILTER,
        name="Wick filter",
        icon="mdi:water-opacity",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up sensors for a fan created by the fan platform (via discovery)."""
    if discovery_info is None:
        return

    host = discovery_info[CONF_HOST]
    fan = next(
        (f for f in hass.data.get(DATA_PHILIPS_FANS, []) if f.host == host), None
    )
    if fan is None:
        return

    async_add_entities(
        PhilipsAirPurifierSensor(fan, discovery_info[CONF_NAME], host, description)
        for description in SENSORS
    )


class PhilipsAirPurifierSensor(SensorEntity):
    """A single reading of the air purifier, mirrored from the fan entity."""

    _attr_should_poll = False

    def __init__(self, fan, fan_name, host, description: SensorEntityDescription):
        self.entity_description = description
        self._fan = fan
        self._attr_name = f"{fan_name} {description.name}"
        self._attr_unique_id = f"{host}_{description.key}"

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self._fan.add_update_listener(self.async_write_ha_state))

    @property
    def available(self) -> bool:
        return self._fan.available and self._raw_value is not None

    @property
    def native_value(self):
        value = self._raw_value
        if value is None:
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            return value
        return int(number) if number.is_integer() else number

    @property
    def _raw_value(self):
        return self._fan.extra_state_attributes.get(self.entity_description.key)
