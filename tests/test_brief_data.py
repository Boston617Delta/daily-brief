"""Offline regression checks for locations, market dates, and safe JSON errors."""
import contextlib
from datetime import datetime
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import urllib.error
import urllib.parse

SCRIPT = Path(__file__).resolve().parents[1] / 'skill/daily-brief/scripts/brief_data.py'
SPEC = importlib.util.spec_from_file_location('brief_data', SCRIPT)
brief = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(brief)


def stamp(iso):
    return int(datetime.fromisoformat(iso.replace('Z', '+00:00')).timestamp())


def chart(price=120, as_of='2026-11-03T16:00:00Z', dates=None, closes=None,
          zone='America/New_York', kind='EQUITY'):
    dates = dates or ['2026-10-30T13:30:00Z', '2026-11-02T14:30:00Z', '2026-11-03T14:30:00Z']
    return {'chart': {'result': [{
        'meta': {'regularMarketPrice': price, 'regularMarketTime': stamp(as_of),
                 'exchangeTimezoneName': zone, 'instrumentType': kind, 'currency': 'USD',
                 'chartPreviousClose': 80},
        'timestamp': [stamp(date) for date in dates],
        'indicators': {'quote': [{'close': [100, 110, 120] if closes is None else closes}]},
    }]}}


def location(name, region, country, code):
    return {'name': name, 'admin1': region, 'country': country, 'country_code': code,
            'latitude': 42.36, 'longitude': -71.06, 'timezone': 'America/New_York'}


class LocationTests(unittest.TestCase):
    def locate(self, place, results):
        with patch.object(brief, 'get_json', return_value={'results': results}):
            return brief.geocode(place)

    def test_boston_state_code(self):
        ma = location('Boston', 'Massachusetts', 'United States', 'US')
        self.assertEqual(self.locate('Boston, MA', [location('Boston', 'England', 'United Kingdom', 'GB'), ma]), ma)

    def test_region_and_country_both_required(self):
        ma = location('Cambridge', 'Massachusetts', 'United States', 'US')
        self.assertEqual(self.locate('Cambridge, MA, USA', [location('Cambridge', 'England', 'United Kingdom', 'GB'), ma]), ma)

    def test_non_us_country(self):
        pt = location('Lisbon', 'Lisbon District', 'Portugal', 'PT')
        self.assertEqual(self.locate('Lisbon, Portugal', [pt]), pt)

    def test_canadian_province_and_country(self):
        toronto = location('Toronto', 'Ontario', 'Canada', 'CA')
        self.assertEqual(self.locate('Toronto, ON, Canada', [toronto]), toronto)
        self.assertEqual(self.locate('Toronto, ON', [toronto]), toronto)

    def test_all_canadian_provinces_and_territories(self):
        regions = {'Alberta': 'AB', 'British Columbia': 'BC', 'Manitoba': 'MB',
                   'New Brunswick': 'NB', 'Newfoundland and Labrador': 'NL',
                   'Northwest Territories': 'NT', 'Nova Scotia': 'NS', 'Nunavut': 'NU',
                   'Ontario': 'ON', 'Prince Edward Island': 'PE', 'Québec': 'QC',
                   'Saskatchewan': 'SK', 'Yukon': 'YT'}
        for region, code in regions.items():
            result = location('Sample City', region, 'Canada', 'CA')
            with self.subTest(region=region):
                self.assertEqual(self.locate(f'Sample City, {code}, Canada', [result]), result)

    def test_wrong_canadian_province_is_rejected(self):
        with self.assertRaises(brief.DataError):
            self.locate('Toronto, BC, Canada', [location('Toronto', 'Ontario', 'Canada', 'CA')])

    def test_country_alias(self):
        uk = location('Cambridge', 'England', 'United Kingdom', 'GB')
        self.assertEqual(self.locate('Cambridge, UK', [uk]), uk)

    def test_qualifier_never_ignored(self):
        with self.assertRaises(brief.DataError):
            self.locate('Paris, DefinitelyNotARegion', [location('Paris', 'Ile-de-France', 'France', 'FR')])

    def test_no_substring_country_match_for_state(self):
        ca = location('San Jose', 'California', 'United States', 'US')
        self.assertEqual(self.locate('San Jose, CA', [location('San Jose', 'San Jose', 'Costa Rica', 'CR'), ca]), ca)

    def test_exact_city_beats_landmarks_and_prefix_matches(self):
        for name, region, country, code, landmarks in [
            ('Boston', 'Massachusetts', 'United States', 'US', ['Boston Hill', 'Boston Neck']),
            ('Lisbon', 'Lisbon District', 'Portugal', 'PT', ['Aquarium Lisbon', 'Lisbon-Portela Airport']),
            ('Cambridge', 'Massachusetts', 'United States', 'US', ['Allston', 'Cambridgeport']),
        ]:
            city = location(name, region, country, code)
            results = [location(landmark, region, country, code) for landmark in landmarks] + [city]
            with self.subTest(name=name):
                self.assertEqual(self.locate(f'{name}, {region}, {country}', results), city)

    def test_ambiguous_place_requires_clarification(self):
        with self.assertRaisesRegex(brief.DataError, 'ambiguous'):
            self.locate('Cambridge', [location('Cambridge', 'England', 'United Kingdom', 'GB'),
                                      location('Cambridge', 'Massachusetts', 'United States', 'US')])

    def test_no_results(self):
        with self.assertRaises(brief.DataError):
            self.locate('NotARealCityZXQ987654', [])


class MarketTests(unittest.TestCase):
    def quote(self, payload):
        with patch.object(brief, 'get_json', return_value=payload):
            return brief.quote('TEST')

    def test_live_session(self):
        result = self.quote(chart())
        self.assertEqual(result['prev_close_date'], '2026-11-02')
        self.assertEqual(result['change_pct'], 9.09)

    def test_missing_current_bar_does_not_shift_reference(self):
        result = self.quote(chart(closes=[100, 110, None]))
        self.assertEqual(result['prev_close'], 110)
        self.assertEqual(result['change_pct'], 9.09)
        self.assertIsNone(result['five_day_closes'][-1])

    def test_missing_reference_is_unknown(self):
        result = self.quote(chart(closes=[100, None, 120]))
        self.assertIsNone(result['prev_close'])
        self.assertIsNone(result['change_pct'])
        self.assertEqual(result['prev_close_date'], '2026-11-02')

    def test_premarket_uses_quote_session_not_new_placeholder(self):
        result = self.quote(chart(price=110, as_of='2026-11-02T21:00:00Z', closes=[100, 110, None]))
        self.assertEqual(result['session_date'], '2026-11-02')
        self.assertEqual(result['prev_close_date'], '2026-10-30')
        self.assertEqual(result['change_pct'], 10)
        self.assertTrue(result['as_of_local'].endswith('-05:00'))

    def test_weekend_or_holiday_retains_actual_quote_date(self):
        result = self.quote(chart(price=110, as_of='2026-05-22T20:00:00Z',
                                 dates=['2026-05-21T13:30:00Z', '2026-05-22T13:30:00Z'], closes=[100, 110]))
        self.assertEqual(result['session_date'], '2026-05-22')
        self.assertEqual(result['prev_close_date'], '2026-05-21')
        self.assertEqual(result['change_pct'], 10)

    def test_crypto_weekend_uses_utc_daily_close(self):
        result = self.quote(chart(price=120, as_of='2026-10-31T04:00:00Z', kind='CRYPTOCURRENCY',
                                 dates=['2026-10-30T00:00:00Z', '2026-10-31T00:00:00Z'], closes=[110, None]))
        self.assertEqual(result['session_date'], '2026-10-31')
        self.assertEqual(result['exchange_timezone'], 'UTC')
        self.assertEqual(result['change_basis'], 'previous UTC daily close')
        self.assertEqual(result['change_pct'], 9.09)

    def test_missing_bar_timestamps_do_not_guess(self):
        data = chart()
        data['chart']['result'][0].pop('timestamp')
        self.assertIsNone(self.quote(data)['change_pct'])

    def test_unknown_timezone_does_not_guess(self):
        result = self.quote(chart(zone='Missing/Zone'))
        self.assertIsNone(result['session_date'])
        self.assertIsNone(result['change_pct'])
        self.assertIsNotNone(result['as_of_utc'])

    def test_zero_reference_does_not_divide(self):
        self.assertIsNone(self.quote(chart(closes=[100, 0, 120]))['change_pct'])

    def test_missing_quote_timestamp_fails(self):
        data = chart()
        data['chart']['result'][0]['meta'].pop('regularMarketTime')
        with self.assertRaises(brief.DataError):
            self.quote(data)

    def test_invalid_price_fails(self):
        for value in (None, float('nan'), float('inf')):
            with self.subTest(value=value), self.assertRaises(brief.DataError):
                self.quote(chart(price=value))


class OutputTests(unittest.TestCase):
    def run_cli(self, args):
        output, errors = io.StringIO(), io.StringIO()
        with patch('sys.argv', ['brief_data.py', *args]), contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = brief.main()
        self.assertEqual(errors.getvalue(), '')
        return status, json.loads(output.getvalue())

    def test_weather_not_found_json(self):
        with patch.object(brief, 'get_json', return_value={}):
            status, data = self.run_cli(['weather', '--place', 'NotARealCityZXQ987654'])
        self.assertEqual(status, 1)
        self.assertIn('not found', data['error'])

    def test_weather_network_failure_json_without_secret_url(self):
        failure = urllib.error.URLError('https://host/?apikey=PRIVATE_TEST_TOKEN')
        with patch.object(brief, 'get_json', side_effect=failure):
            status, data = self.run_cli(['weather', '--place', 'Boston, MA'])
        self.assertEqual(status, 1)
        self.assertNotIn('PRIVATE_TEST_TOKEN', json.dumps(data))
        self.assertNotIn('https://host', json.dumps(data))

    def test_malformed_weather_response_json(self):
        with patch.object(brief, 'get_json', return_value={}):
            status, data = self.run_cli(['weather', '--lat', '42', '--lon', '-71'])
        self.assertEqual(status, 1)
        self.assertIn('incomplete data', data['error'])

    def test_partial_markets_keep_valid_results(self):
        with patch.object(brief, 'get_json', side_effect=[chart(), urllib.error.HTTPError('https://host', 404, 'missing', {}, None)]):
            status, data = self.run_cli(['markets', '--symbols', 'AAPL,FAKE123'])
        self.assertEqual(status, 0)
        self.assertEqual([q['symbol'] for q in data['quotes']], ['AAPL'])
        self.assertEqual(data['errors'][0]['symbol'], 'FAKE123')
        self.assertIn('404', data['errors'][0]['error'])

    def test_all_market_failures_exit_nonzero(self):
        with patch.object(brief, 'get_json', side_effect=TimeoutError):
            with self.assertRaises(SystemExit) as caught:
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    with patch('sys.argv', ['brief_data.py', 'markets', '--symbols', 'FAKE123']):
                        brief.main()
        self.assertEqual(caught.exception.code, 1)
        self.assertEqual(json.loads(output.getvalue())['quotes'], [])

    def test_empty_symbol_list_json_error(self):
        status, data = self.run_cli(['markets', '--symbols', ', ,'])
        self.assertEqual(status, 1)
        self.assertIn('at least one', data['error'])

    def test_commercial_requires_environment_key(self):
        with patch.dict('os.environ', {}, clear=True):
            status, data = self.run_cli(['weather', '--lat', '42', '--lon', '-71', '--commercial'])
        self.assertEqual(status, 1)
        self.assertIn('OPEN_METEO_API_KEY', data['error'])

    def test_commercial_endpoints_get_key_without_logging_it(self):
        with patch.dict('os.environ', {'OPEN_METEO_API_KEY': 'PRIVATE_TEST_TOKEN'}):
            for host in ['api.open-meteo.com', 'geocoding-api.open-meteo.com']:
                url = brief.open_meteo_url(host, '/v1/search', {'name': 'Boston'}, commercial=True)
                parsed = urllib.parse.urlparse(url)
                self.assertEqual(parsed.hostname, 'customer-' + host)
                self.assertEqual(urllib.parse.parse_qs(parsed.query)['apikey'], ['PRIVATE_TEST_TOKEN'])
                message = brief.error_message(urllib.error.HTTPError(url, 429, 'limited', {}, None))
                self.assertEqual(message, 'data service returned HTTP 429')


if __name__ == '__main__':
    unittest.main()
