"""
Sector definitions and watchlists
"""

SECTORS = {
    'Technology': {
        'name': 'Technology',
        'watchlist_file': 'technology.txt',
        'description': 'Software, hardware, semiconductors, IT services'
    },
    'Healthcare': {
        'name': 'Healthcare',
        'watchlist_file': 'healthcare.txt',
        'description': 'Pharmaceuticals, biotech, medical devices, healthcare services'
    },
    'Energy': {
        'name': 'Energy',
        'watchlist_file': 'energy.txt',
        'description': 'Oil & gas, renewables, energy services'
    },
    'Financials': {
        'name': 'Financials',
        'watchlist_file': 'financials.txt',
        'description': 'Banks, insurance, payments, financial services'
    },
    'Consumer': {
        'name': 'Consumer',
        'watchlist_file': 'consumer.txt',
        'description': 'Retail, restaurants, consumer goods'
    },
    'Communications': {
        'name': 'Communications',
        'watchlist_file': 'communications.txt',
        'description': 'Telecom, media, entertainment, internet services'
    }
}

def get_sector_watchlist_path(sector_name: str) -> str:
    """Get the full path to a sector's watchlist file"""
    import os
    from pathlib import Path
    
    base_dir = Path(__file__).parent.parent
    watchlist_file = SECTORS.get(sector_name, {}).get('watchlist_file', 'technology.txt')
    return os.path.join(base_dir, 'watchlists', watchlist_file)

def load_watchlist(watchlist_path: str) -> list:
    """Load symbols from a watchlist file"""
    try:
        with open(watchlist_path, 'r') as f:
            content = f.read()
            # Split by comma and newline, strip whitespace
            symbols = [s.strip() for s in content.replace('\n', ',').split(',') if s.strip()]
            return symbols
    except FileNotFoundError:
        print(f"Watchlist file not found: {watchlist_path}")
        return []
