#!/usr/bin/env python3
"""Free, no-key data for the daily brief: weather and market quotes.

Python 3.9+ standard library only. Prints JSON so any agent can read it.
Runtime and data errors are JSON on stdout with a nonzero exit status;
command-line syntax errors use argparse on stderr.

  python3 brief_data.py weather --place "Boston, MA" [--units f|c]
  python3 brief_data.py weather --lat 42.36 --lon -71.06 --tz America/New_York
  python3 brief_data.py markets --symbols "^GSPC,^IXIC,^DJI,BTC-USD,AAPL"

Weather comes from Open-Meteo (https://open-meteo.com), free for
non-commercial use. For commercial use, add --commercial and set
OPEN_METEO_API_KEY in the environment for the customer endpoints. Never put
the key in a settings file or command argument. Quotes come from Yahoo Finance's public chart endpoint,
which is unofficial and can change or rate-limit without notice; when it
fails, the script says so and the agent falls back to a web search.
"""

import argparse
import json
import math
import os
import sys
import unicodedata
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import urllib.error
import urllib.parse
import urllib.request

UA = "daily-brief/1.0 (+https://github.com/Boston617Delta/daily-brief)"

# WMO weather codes used by Open-Meteo, trimmed to plain words.
WMO = {
    0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "freezing fog",
    51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    56: "freezing drizzle", 57: "freezing drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    66: "freezing rain", 67: "freezing rain",
    71: "light snow", 73: "snow", 75: "heavy snow", 77: "snow grains",
    80: "rain showers", 81: "rain showers", 82: "violent rain showers",
    85: "snow showers", 86: "heavy snow showers",
    95: "thunderstorms", 96: "thunderstorms with hail", 99: "thunderstorms with hail",
}


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)


class DataError(ValueError):
    """A data problem safe to describe without request URLs or credentials."""


def error_message(error):
    if isinstance(error, urllib.error.HTTPError):
        code = error.code
        error.close()
        return f"data service returned HTTP {code}"
    if isinstance(error, (urllib.error.URLError, TimeoutError, OSError)):
        return "data service could not be reached; try web search"
    if isinstance(error, DataError):
        return str(error)
    return "data service returned invalid or incomplete data"


def normalized(value):
    text = unicodedata.normalize("NFKD", str(value)).casefold()
    return "".join(c for c in text if c.isalnum() and not unicodedata.combining(c))


def open_meteo_url(host, path, params, commercial=False):
    params = dict(params)
    if commercial:
        key = os.environ.get("OPEN_METEO_API_KEY")
        if not key:
            raise DataError("commercial weather requires OPEN_METEO_API_KEY in the environment")
        host = "customer-" + host
        params["apikey"] = key
    return f"https://{host}{path}?{urllib.parse.urlencode(params)}"


def geocode(place, commercial=False):
    parts = [part.strip() for part in place.split(",")]
    if not parts[0] or any(not part for part in parts[1:]):
        raise DataError("use a city, optionally followed by region and country")
    # Fetch candidates, then require every supplied qualifier to match exactly.
    data = get_json(open_meteo_url("geocoding-api.open-meteo.com", "/v1/search",
                    {"name": parts[0], "count": 100, "format": "json", "language": "en"},
                    commercial))
    results = data.get("results") or []
    aliases = {"usa": "us", "unitedstatesofamerica": "us", "uk": "gb", "greatbritain": "gb"}
    qualifiers = [aliases.get(normalized(p), normalized(p)) for p in parts[1:]]
    matches = []
    for result in results:
        labels = {normalized(result.get(k, "")) for k in ("admin1", "admin2", "country", "country_code")}
        labels.add(normalized(_region_code(result)))
        if all(q in labels for q in qualifiers):
            matches.append(result)
    # A single state/province abbreviation takes precedence over a country code.
    if len(qualifiers) == 1:
        state_matches = [r for r in matches if normalized(_region_code(r)) == qualifiers[0]]
        if state_matches:
            matches = state_matches
    if not matches:
        raise DataError(f"place or region not found: {place}; check the name or use coordinates")
    # The provider also returns prefix matches and indexed landmarks. Prefer
    # the city itself over Boston Hill, an airport, or an address alias.
    exact = [r for r in matches if normalized(r.get("name", "")) == normalized(parts[0])]
    if exact:
        matches = exact
    if len(matches) > 1:
        candidates = [", ".join(str(r.get(k, "")) for k in ("name", "admin1", "country_code"))
                      for r in matches[:5]]
        raise DataError("ambiguous place; add a region/country or use coordinates. Matches: "
                        + "; ".join(candidates))
    return matches[0]


def _region_code(r):
    states = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
        "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
        "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
        "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
        "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
        "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
        "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
        "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
        "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
        "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC",
    }
    provinces = {
        "Alberta": "AB", "British Columbia": "BC", "Manitoba": "MB",
        "New Brunswick": "NB", "Newfoundland and Labrador": "NL",
        "Northwest Territories": "NT", "Nova Scotia": "NS", "Nunavut": "NU",
        "Ontario": "ON", "Prince Edward Island": "PE", "Quebec": "QC",
        "Saskatchewan": "SK", "Yukon": "YT",
    }
    regions = {"US": states, "CA": provinces}.get(r.get("country_code"), {})
    region = normalized(r.get("admin1", ""))
    return next((code for name, code in regions.items() if normalized(name) == region), "")


def weather(args):
    if args.place:
        g = geocode(args.place, args.commercial)
        lat, lon, tz = g["latitude"], g["longitude"], args.tz or g.get("timezone", "auto")
        label = ", ".join(x for x in (g.get("name"), g.get("admin1"), g.get("country_code")) if x)
    else:
        lat, lon, tz, label = args.lat, args.lon, args.tz or "auto", f"{args.lat},{args.lon}"
    imperial = args.units == "f"
    url = open_meteo_url("api.open-meteo.com", "/v1/forecast", {
        "latitude": lat, "longitude": lon, "timezone": tz, "forecast_days": 2,
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
        "hourly": "precipitation_probability",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
                 "precipitation_probability_max,precipitation_sum,sunrise,sunset,uv_index_max",
        "temperature_unit": "fahrenheit" if imperial else "celsius",
        "wind_speed_unit": "mph" if imperial else "kmh",
        "precipitation_unit": "inch" if imperial else "mm",
    }, args.commercial)
    d = get_json(url)
    cur, day = d["current"], d["daily"]

    # Find the wettest hour today so the brief can say "rain likely around 4 PM".
    today = day["time"][0]
    hours = [(t, p) for t, p in zip(d["hourly"]["time"], d["hourly"]["precipitation_probability"])
             if t.startswith(today) and p is not None]
    peak = max(hours, key=lambda h: h[1]) if hours else None

    def day_summary(i):
        return {
            "date": day["time"][i],
            "conditions": WMO.get(day["weather_code"][i], f"code {day['weather_code'][i]}"),
            "high": day["temperature_2m_max"][i],
            "low": day["temperature_2m_min"][i],
            "precip_chance_pct": day["precipitation_probability_max"][i],
            "precip_total": day["precipitation_sum"][i],
        }

    out = {
        "place": label,
        "timezone": d.get("timezone", tz),
        "as_of_local": cur.get("time"),
        "units": "F, mph, inches" if imperial else "C, km/h, mm",
        "now": {
            "temp": cur["temperature_2m"],
            "feels_like": cur["apparent_temperature"],
            "conditions": WMO.get(cur["weather_code"], f"code {cur['weather_code']}"),
            "wind": cur["wind_speed_10m"],
        },
        "today": {**day_summary(0),
                  "sunrise": day["sunrise"][0][-5:], "sunset": day["sunset"][0][-5:],
                  "uv_max": day["uv_index_max"][0],
                  "wettest_hour": {"time": peak[0][-5:], "chance_pct": peak[1]} if peak else None},
        "tomorrow": day_summary(1),
        "source": "Open-Meteo",
        "source_url": "https://open-meteo.com/",
        "attribution": "Weather data: Open-Meteo (CC BY 4.0); locations: GeoNames",
    }
    print(json.dumps(out, indent=2))


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def quote(symbol):
    s = urllib.parse.quote(symbol, safe="")
    d = get_json(f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?range=5d&interval=1d")
    res = (d.get("chart") or {}).get("result")
    if not res:
        raise DataError("no data for this symbol")
    result = res[0]
    meta = result["meta"]
    price = meta.get("regularMarketPrice")
    if not finite_number(price):
        raise DataError("latest price unavailable")
    timestamp = meta.get("regularMarketTime")
    if not finite_number(timestamp):
        raise DataError("quote timestamp unavailable")
    is_crypto = meta.get("instrumentType", "").upper() == "CRYPTOCURRENCY"
    zone_name = "UTC" if is_crypto else meta.get("exchangeTimezoneName")
    try:
        zone = ZoneInfo(zone_name) if zone_name else None
    except ZoneInfoNotFoundError:
        zone = None
    as_of_utc = datetime.fromtimestamp(timestamp, timezone.utc)
    session_date = as_of_utc.astimezone(zone).date() if zone else None
    closes = result["indicators"]["quote"][0].get("close", [])
    times = result.get("timestamp") or []
    # Keep null bars and their dates. A missing current bar must not shift the
    # reference back two sessions; a missing reference stays unknown.
    bars = []
    if zone and len(times) == len(closes):
        for bar_time, close in zip(times, closes):
            if finite_number(bar_time):
                date = datetime.fromtimestamp(bar_time, zone).date()
                bars.append((date, close))
    prior = sorted(((date, close) for date, close in bars if date < session_date), key=lambda bar: bar[0])
    prev_date, prev = prior[-1] if prior else (None, None)
    if not finite_number(prev) or prev <= 0:
        prev = None
    change = None if prev is None else round((price - prev) / prev * 100, 2)
    return {
        "symbol": symbol,
        "name": meta.get("shortName") or meta.get("longName") or symbol,
        "price": price,
        "prev_close": prev,
        "prev_close_date": prev_date.isoformat() if prev_date else None,
        "change_pct": change,
        "currency": meta.get("currency"),
        "as_of_unix": timestamp,
        "as_of_utc": as_of_utc.isoformat(),
        "as_of_local": as_of_utc.astimezone(zone).isoformat() if zone else None,
        "exchange_timezone": zone_name,
        "session_date": session_date.isoformat() if session_date else None,
        "instrument_type": meta.get("instrumentType"),
        "change_basis": "previous UTC daily close" if is_crypto else "previous exchange-session close",
        "reference_note": None if prev is not None else "previous close could not be verified; omit percent change",
        "five_day_closes": [c if finite_number(c) else None for c in closes],
        "daily_bars": [{"date": date.isoformat(), "close": close if finite_number(close) else None}
                       for date, close in bars],
        "source_url": f"https://finance.yahoo.com/quote/{s}/",
    }


def markets(args):
    out = {"quotes": [], "errors": [], "source": "Yahoo Finance chart endpoint (unofficial)"}
    symbols = list(dict.fromkeys(s.strip() for s in args.symbols.split(",") if s.strip()))
    if not symbols:
        raise DataError("provide at least one market symbol")
    for sym in symbols:
        try:
            out["quotes"].append(quote(sym))
        except Exception as e:  # keep going; the agent reports what failed
            out["errors"].append({"symbol": sym, "error": error_message(e)})
    print(json.dumps(out, indent=2))
    if not out["quotes"]:
        sys.exit(1)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    w = sub.add_parser("weather")
    w.add_argument("--place", help='City, e.g. "Boston, MA" or "Lisbon"')
    w.add_argument("--lat", type=float)
    w.add_argument("--lon", type=float)
    w.add_argument("--tz", help="IANA time zone, e.g. America/New_York (default: auto)")
    w.add_argument("--units", choices=["f", "c"], default="f")
    w.add_argument("--commercial", action="store_true",
                   help="Use customer endpoints; requires OPEN_METEO_API_KEY in the environment")
    w.set_defaults(func=weather)

    m = sub.add_parser("markets")
    m.add_argument("--symbols", required=True, help='Comma-separated, e.g. "^GSPC,^IXIC,AAPL,BTC-USD"')
    m.set_defaults(func=markets)

    args = p.parse_args()
    if args.cmd == "weather" and not args.place and (args.lat is None or args.lon is None):
        p.error("weather needs --place or both --lat and --lon")
    try:
        args.func(args)
    except Exception as error:
        print(json.dumps({"error": error_message(error), "command": args.cmd}, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
