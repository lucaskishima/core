# Reprodutor de estados de alerta

import asyncio
from collections.abc import Iterable
from typing import Any

from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import Context, HomeAssistant, State

from .const import DOMAIN, LOGGER

VALID_STATES = {STATE_ON, STATE_OFF}

# Reprodutor de um único estado
async def _async_reproduce_state(
    hass: HomeAssistant,
    state: State,
    *,
    context: Context | None = None,
    reproduce_options: Any = None
):
    if (cur_state := hass.states.get(state.entity_id)) is None:
        LOGGER.warning("Não foi possível encontrar a entidade %s", state.entity_id)
        return

    if state.state not in VALID_STATES:
        LOGGER.warning(
            "Estado inválido especificado para %s: %s", state.entity_id, state.state
        )
        return

    # Retorna se já estiver no estado desejado
    if cur_state.state == state.state:
        return

    service_data = {ATTR_ENTITY_ID: state.entity_id}

    if state.state == STATE_ON:
        service = SERVICE_TURN_ON

    elif state.state == STATE_OFF:
        service = SERVICE_TURN_OFF

    await hass.services.async_call(
        DOMAIN, service, service_data, context=context, blocking=True
    )

# Reprodutor de vários estados
async def async_reproduce_states(
    hass: HomeAssistant,
    states: Iterable[State],
    *,
    context: Context | None = None,
    reproduce_options: Any = None
):
    # Reprodutor de estados em paralelo
    await asyncio.gather(
        *(
            _async_reproduce_state(
                hass, state, context=context, reproduce_options=reproduce_options
            )
            for state in states
        )
    )