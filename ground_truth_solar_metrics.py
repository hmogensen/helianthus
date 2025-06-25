#!/usr/bin/env python3

from pathlib import Path
import requests
from datetime import datetime, timedelta
import time
import os
import json

def get_sun_times(lat, lng, start_date, end_date, timezone=None, delay=0.1):
    """
    Get sunrise/sunset times for GPS coordinates and date range.
    
    Args:
        lat: Latitude in decimal degrees
        lng: Longitude in decimal degrees  
        start_date: Start date as datetime or 'YYYY-MM-DD' string
        end_date: End date as datetime or 'YYYY-MM-DD' string
        timezone: Optional timezone string (e.g. 'America/New_York')
        delay: Delay between API calls in seconds
        
    Returns:
        List of tuples: [(date, sunrise_hour, sunset_hour), ...]
        Hours are in decimal format (e.g. 6.5 = 6:30 AM)
    """
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    cache_dir = Path(os.path.expanduser("~")) / "cache" / "sun_times_cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    tz_str = timezone.replace('/', '_') if timezone else "UTC"

    cache_filename = f"sun_times_{lat}_{lng}_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}_{tz_str}.json"
    cache_path = os.path.join(cache_dir, cache_filename)
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
                print("Loading solar data from cache")
                return [(item['date'], item['sunrise'], item['sunset']) for item in cached_data]
        except:
            pass
    print("Downloading solar data from internet")
    
    results = []
    current_date = start_date
    
    while current_date <= end_date:
        params = {
            'lat': lat,
            'lng': lng,
            'date': current_date.strftime('%Y-%m-%d'),
            'formatted': 0
        }
        
        if timezone:
            params['tzid'] = timezone
        
        try:
            response = requests.get('https://api.sunrise-sunset.org/json', params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == 'OK':
                results_data = data['results']
                
                sunrise_str = results_data['sunrise']
                sunset_str = results_data['sunset']
                
                if timezone:
                    sunrise_dt = datetime.fromisoformat(sunrise_str.replace('Z', ''))
                    sunset_dt = datetime.fromisoformat(sunset_str.replace('Z', ''))
                else:
                    sunrise_dt = datetime.fromisoformat(sunrise_str.replace('Z', '+00:00'))
                    sunset_dt = datetime.fromisoformat(sunset_str.replace('Z', '+00:00'))
                
                sunrise_hour = sunrise_dt.hour + sunrise_dt.minute/60 + sunrise_dt.second/3600
                sunset_hour = sunset_dt.hour + sunset_dt.minute/60 + sunset_dt.second/3600
                
                results.append((current_date.strftime('%Y-%m-%d'), sunrise_hour, sunset_hour))
                
        except:
            pass
        
        current_date += timedelta(days=1)
        if delay > 0:
            time.sleep(delay)
    
    cache_data = [{'date': date, 'sunrise': sunrise, 'sunset': sunset} for date, sunrise, sunset in results]
    try:
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)
    except:
        pass
    
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 5:
        lat = float(sys.argv[1])
        lng = float(sys.argv[2])
        start = sys.argv[3]
        end = sys.argv[4]
        tz = sys.argv[5] if len(sys.argv) > 5 else None
        
        data = get_sun_times(lat, lng, start, end, tz)
        for date, sunrise, sunset in data:
            print(f"{date}: sunrise {sunrise:.2f}, sunset {sunset:.2f}")
    else:
        print("Usage: python sun_fetcher.py lat lng start_date end_date [timezone]")