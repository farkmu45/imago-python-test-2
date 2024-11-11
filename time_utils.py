from datetime import datetime, timedelta
import re

def parse_detik_datetime(date_string: str) -> datetime:
    """
    Parse detik.com date formats into datetime object.
    Handles both absolute dates ("Kamis, 18 Jul 2024 11:15 WIB")
    and relative dates ("16 jam yang lalu", "1 menit yang lalu")
    
    Args:
        date_string: String containing the date in Detik format
        
    Returns:
        datetime object
    """
    # Clean the input
    date_string = date_string.strip()
    
    # Handle relative time expressions
    relative_pattern = r'(\d+)\s+(detik|menit|jam|hari|minggu|bulan|tahun)\s+yang\s+lalu'
    match = re.match(relative_pattern, date_string, re.IGNORECASE)
    
    if match:
        amount = int(match.group(1))
        unit = match.group(2).lower()
        
        # Create a mapping for time units
        units = {
            'detik': lambda x: timedelta(seconds=x),
            'menit': lambda x: timedelta(minutes=x),
            'jam': lambda x: timedelta(hours=x),
            'hari': lambda x: timedelta(days=x),
            'minggu': lambda x: timedelta(weeks=x),
            'bulan': lambda x: timedelta(days=x*30),  # Approximate
            'tahun': lambda x: timedelta(days=x*365)  # Approximate
        }
        
        if unit in units:
            return datetime.now() - units[unit](amount)
    
    # Handle absolute dates
    # First, create a mapping for Indonesian month names
    month_mapping = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
        'Mei': '05', 'Jun': '06', 'Jul': '07', 'Ags': '08',
        'Sep': '09', 'Okt': '10', 'Nov': '11', 'Des': '12'
    }
    
    # Extract date components using regex
    absolute_pattern = r'(?:[A-Za-z]+,\s+)?(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\s+(\d{1,2}):(\d{1,2})'
    match = re.match(absolute_pattern, date_string)
    
    if match:
        day, month, year, hour, minute = match.groups()
        month = month_mapping.get(month[:3], '01')  # Get first 3 chars of month
        
        # Create datetime string in format that datetime can parse
        datetime_str = f"{year}-{month}-{day.zfill(2)} {hour.zfill(2)}:{minute.zfill(2)}:00"
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    
    # If no pattern matches, raise an error
    raise ValueError(f"Unable to parse date string: {date_string}")