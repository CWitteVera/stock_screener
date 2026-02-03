# Deployment Guide

This guide explains how to deploy and use the Swing Trading Screener in different environments.

## Local Development

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for yfinance data)

### Setup
```bash
# Clone repository
git clone https://github.com/CWitteVera/stock_screener.git
cd stock_screener

# Install dependencies
pip install -r requirements.txt

# Run immediately (no configuration needed!)
streamlit run main.py
```

## Production Deployment

### Option 1: Streamlit Cloud (Free)

1. **Fork the repository** on GitHub

2. **Go to** https://streamlit.io/cloud

3. **Deploy:**
   - Click "New app"
   - Select your forked repository
   - Main file: `main.py`
   - Click "Deploy"

4. **Result:** Your app is live at `https://your-app.streamlit.app`

**Pros:** Free, easy, automatic updates  
**Cons:** Public access, limited resources

### Option 2: Docker Container

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t swing-screener .
docker run -p 8501:8501 swing-screener
```

Access at: `http://localhost:8501`

### Option 3: Server Deployment

**For Ubuntu/Debian server:**

```bash
# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip

# Clone and setup
git clone https://github.com/CWitteVera/stock_screener.git
cd stock_screener
pip3 install -r requirements.txt

# Run with systemd (persistent service)
sudo nano /etc/systemd/system/screener.service
```

Service file content:
```ini
[Unit]
Description=Swing Trading Screener
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/stock_screener
ExecStart=/usr/bin/python3 -m streamlit run main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable screener
sudo systemctl start screener
sudo systemctl status screener
```

## CLI-Only Deployment

For servers without GUI:

```bash
# Install dependencies
pip install -r requirements.txt

# Create daily scan cron job
crontab -e

# Add line (runs at 9:30 AM daily):
30 9 * * 1-5 cd /path/to/stock_screener && python console_scanner.py --sector Technology --export csv > /path/to/logs/scan_$(date +\%Y\%m\%d).log

# Email results
30 9 * * 1-5 cd /path/to/stock_screener && python console_scanner.py --sector Technology --export text | mail -s "Daily Scan Results" your@email.com
```

## Configuration

### API Keys (Optional)

For enhanced features with Financial Modeling Prep:

```bash
# Create .env file
cp .env.example .env

# Edit .env
nano .env

# Add your key:
FMP_API_KEY=your_key_here
```

Get free key: https://financialmodelingprep.com/developer/docs/

**Note:** Screener works 100% FREE without this!

### Settings Customization

Edit `config/settings.py` to customize:

```python
# Trading parameters
CAPITAL_PER_TRADE = 1000  # Change trade size
PRIMARY_RETURN_TARGET = 15.0  # Adjust target
MAX_LOSS_PERCENT = 10.0  # Adjust stop loss

# Screening filters
MIN_PRICE = 5.0  # Minimum stock price
MAX_PRICE = 200.0  # Maximum stock price
MIN_VOLUME = 500000  # Minimum daily volume
```

### Custom Watchlists

Add your own stocks to `watchlists/custom.txt`:

```
AAPL,MSFT,GOOGL
TSLA,NVDA,AMD
# Comments are ignored
```

Or create new sector files in `watchlists/`:

```bash
# Create custom sector
nano watchlists/my_sector.txt

# Add symbols
STOCK1,STOCK2,STOCK3
```

## Backup and Data

### Important Files
- `data/positions/*.json` - Active positions (backup daily)
- `data/trades/*.json` - Trade history
- `watchlists/*.txt` - Your custom watchlists

### Backup Script

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/screener_$DATE"

mkdir -p $BACKUP_DIR
cp -r data/positions $BACKUP_DIR/
cp -r data/trades $BACKUP_DIR/
cp -r watchlists $BACKUP_DIR/
cp .env $BACKUP_DIR/ 2>/dev/null || true

echo "Backup completed: $BACKUP_DIR"
```

## Performance Optimization

### Caching

The screener automatically caches data for 4 hours. To adjust:

Edit `config/settings.py`:
```python
CACHE_DURATION_HOURS = 4  # Increase for faster scans
```

Clear cache manually:
```python
from utils.cache import Cache
cache = Cache()
cache.clear()  # Clear all cache
```

### Parallel Scanning

For scanning multiple sectors:

```bash
# Run in parallel (requires GNU parallel)
parallel python console_scanner.py --sector {} --export csv ::: Technology Healthcare Energy
```

## Monitoring and Logs

### View Logs

```bash
# Real-time logs
tail -f screener.log

# Filter errors
grep ERROR screener.log

# Today's activity
grep $(date +%Y-%m-%d) screener.log
```

### Health Check Script

```bash
#!/bin/bash
# health_check.sh

# Check if process is running
if pgrep -f "streamlit run main.py" > /dev/null; then
    echo "✅ Screener is running"
else
    echo "❌ Screener is down"
    # Restart
    cd /path/to/stock_screener
    streamlit run main.py &
fi
```

## Security Considerations

### API Key Protection
- ✅ Never commit `.env` to git (already in .gitignore)
- ✅ Use environment variables in production
- ✅ Rotate keys periodically

### Data Privacy
- ✅ Position data stored locally only
- ✅ No external data transmission (except API calls)
- ✅ No user tracking or analytics

### Access Control
For public deployments:
- Add authentication (Streamlit supports this)
- Use firewall rules
- Enable HTTPS
- Implement rate limiting

## Troubleshooting

### "Module not found"
```bash
pip install --upgrade -r requirements.txt
```

### "No data fetched"
- Check internet connection
- Verify yfinance is working: `python -c "import yfinance; print(yfinance.__version__)"`
- Try different symbols

### "Streamlit not starting"
```bash
# Check port 8501 is free
lsof -i :8501

# Use different port
streamlit run main.py --server.port 8502
```

### "Permission denied"
```bash
chmod +x console_scanner.py
chmod +x main.py
```

## Scaling

### For Multiple Users

Use proper web framework:
- FastAPI backend
- React frontend
- Database for results
- Queue for scan jobs

### For High Frequency

- Use Redis for caching
- Implement connection pooling
- Cache indicator calculations
- Use async/await for API calls

## Maintenance

### Weekly Tasks
- [ ] Review active positions
- [ ] Check log files
- [ ] Verify API keys valid
- [ ] Backup position data

### Monthly Tasks
- [ ] Update dependencies: `pip install --upgrade -r requirements.txt`
- [ ] Review and update watchlists
- [ ] Analyze performance metrics
- [ ] Archive old trade data

### Updates

```bash
# Pull latest changes
git pull origin main

# Reinstall dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart screener
```

## Support

For issues or questions:
1. Check QUICK_START.md
2. Review EXAMPLES.md
3. Read troubleshooting section above
4. Create GitHub issue

## License

MIT License - See LICENSE file

---

**Remember:** This is a tool for informed decision-making, not financial advice. Always do your own research and trade responsibly!
