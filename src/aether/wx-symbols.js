/**
 * AETHER Weather Symbol Registry
 * Maps telemetry states to Unicode glyphs
 */

export const WX_SYMBOLS = Object.freeze({
    SAT: '🛰️',
    POS: '📍',
    ELEV: '⬆️',
    RH_ACTIVE: '💧',
    RH_VOID: '∅',
    WIND: '🌬️',
    TEMP: '🌡️',
    PRESSURE: '⏲️'
});

/**
 * Returns appropriate symbol based on data integrity
 * @param {string} field - Telemetry field name
 * @param {*} value - Field value
 * @returns {string} Unicode glyph
 */
export function getWxSymbol(field, value) {
    if (value === null || value === undefined) {
        return field === 'rh_percent' ? WX_SYMBOLS.RH_VOID : '—';
    }

    switch (field) {
        case 'rh_percent': return WX_SYMBOLS.RH_ACTIVE;
        case 'wind_ms': return WX_SYMBOLS.WIND;
        case 'temp_celsius': return WX_SYMBOLS.TEMP;
        case 'pressure_hpa': return WX_SYMBOLS.PRESSURE;
        default: return '●';
    }
}
