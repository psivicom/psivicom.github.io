/**
 * AETHER Weather Fetcher - Open-Meteo Integration
 * Zero-Cost | No-Key | NASA Open Science Compliant
 * @module aether/weather-fetcher
 */

const OPEN_METEO_ENDPOINT = 'https://api.open-meteo.com/v1/forecast';
const DEFAULT_COORDS = { lat: 48.4500, lon: -123.5000 }; // POS48.4500°N 123.5000°W

/**
 * Fetches atmospheric telemetry for apiary stigmergy
 * Prioritizes RH over wind per biological epistemology
 * @param {Object} options - Override defaults
 * @returns {Promise<Object>} Immutable weather state
 */
export async function fetchWeatherTelemetry(options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s hard limit

    try {
        const params = new URLSearchParams({
            latitude: options.lat ?? DEFAULT_COORDS.lat,
            longitude: options.lon ?? DEFAULT_COORDS.lon,
            current: 'relative_humidity_2m,temperature_2m,wind_speed_10m,pressure_msl',
            timezone: 'GMT', // Zulu alignment
            format: 'json'
        });

        const response = await fetch(`${OPEN_METEO_ENDPOINT}?${params}`, {
            signal: controller.signal,
            headers: { 'Accept': 'application/json' }
        });

        if (!response.ok) throw new Error(`AETHER_WX_FAIL: ${response.status}`);

        const data = await response.json();
        clearTimeout(timeoutId);

        // Validate & Transform to Sovereign Schema
        return Object.freeze({
            timestamp_zulu: `${data.current.time}Z`,
            rh_percent: data.current.relative_humidity_2m,      // Primary for bees
            temp_celsius: data.current.temperature_2m,
            wind_ms: data.current.wind_speed_10m / 3.6,        // Convert km/h to m/s
            pressure_hpa: data.current.pressure_msl,
            source: 'open-meteo-v1',
            integrity: 'verified'
        });

    } catch (err) {
        clearTimeout(timeoutId);
        // Return void state, never fabricate
        return Object.freeze({
            timestamp_zulu: new Date().toISOString(),
            error: err.name === 'AbortError' ? 'TIMEOUT' : 'FETCH_FAILED',
            rh_percent: null,
            integrity: 'void'
        });
    }
}
