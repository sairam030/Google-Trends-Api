# Google Trends CSV Downloader & API

Automated script to download CSV files from Google Trends for multiple categories in parallel, add category labels, and merge them into a single file.

**NEW:** 🚀 **REST API available!** Get real-time JSON responses instead of CSV files. [See API documentation](API_README.md)

## Features

✅ **Download all 20 Google Trends categories** automatically  
✅ **Parallel processing** - Use multiple workers to download faster  
✅ **Auto-categorization** - Adds a "Category" column to each CSV  
✅ **Smart merging** - Combines all CSVs into one master file  
✅ **Headless browser** - Runs in background without opening windows  
✅ **Progress tracking** - See real-time status for each category  

## Categories Supported

The script downloads data for these 20 categories:
- All Categories (0)
- Autos and vehicles (1)
- Beauty and fashion (2)
- Business and finance (3)
- Climate (4)
- Entertainment (5)
- Food and drink (6)
- Games (7)
- Health (8)
- Hobbies and leisure (9)
- Jobs and education (10)
- Law and government (11)
- Other (12)
- Pets and animals (13)
- Politics (14)
- Science (15)
- Shopping (16)
- Sports (17)
- Technology (18)
- Travel and transportation (19)

## Installation

```bash
# Activate your virtual environment
source venv/bin/activate

# Dependencies should already be installed:
# - selenium
# - webdriver-manager
```

## Usage

### Download ALL Categories (Recommended)

```bash
# Default: Download all categories for India with 3 workers
python google.py all

# Specify country and workers
python google.py all IN 5        # India with 5 workers
python google.py all US 4        # USA with 4 workers
python google.py all GB 3        # UK with 3 workers
```

### Download Single URL

```bash
python google.py "https://trends.google.com/trending?geo=IN&category=3"
```

### Run Demo (3 categories only)

```bash
python demo.py
```

## How It Works

1. **Parallel Download**: Uses ThreadPoolExecutor to download multiple categories simultaneously
2. **Browser Automation**: Selenium clicks the "Export" button and "Download CSV" option
3. **Category Tagging**: Adds a "Category" column as the first column in each CSV
4. **Merging**: Combines all individual CSVs into one master file with timestamp

## Output

### Individual Files
Each category creates a file like:
```
downloads/trending_IN_1d_20251022-2301.csv
```

### Merged File
Final merged file with all categories:
```
downloads/merged_trends_20251022_230145.csv
```

### CSV Structure
```csv
Category,Trends,Search volume,Started,Ended,Trend breakdown,Explore link
Business and finance,gold rate today,500K+,October 22 2025...
Entertainment,movies,100K+,October 22 2025...
Technology,AI,50K+,October 22 2025...
```

## Performance

- **Sequential**: ~2-3 minutes per category = 40-60 minutes total
- **Parallel (5 workers)**: ~10-15 minutes total (4-6x faster!)

## Tips for Faster Downloads

1. **Increase workers**: Use 5-8 workers for maximum speed
   ```bash
   python google.py all IN 8
   ```

2. **Good internet connection**: Faster downloads = better performance

3. **Run during off-peak hours**: Less likely to hit rate limits

## Troubleshooting

**No CSV file detected**: Some categories might be empty for certain regions

**ChromeDriver version mismatch**: The script auto-updates ChromeDriver using webdriver-manager

**Rate limiting**: Reduce the number of workers or add more delay between requests

## Examples

### Download for Multiple Countries
```bash
# India
python google.py all IN 5

# United States  
python google.py all US 5

# United Kingdom
python google.py all GB 5
```

### Check Merged Results
```bash
# List merged files
ls -lh downloads/merged_*.csv

# View first 10 lines
head -10 downloads/merged_trends_*.csv

# Count total rows
wc -l downloads/merged_trends_*.csv
```

## Author

Created for automated Google Trends data collection with category labeling and merging.
# Google-Trends-CSV-Downloader
