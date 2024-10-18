
# Proxy Checker

A Python script to check and validate HTTP, SOCKS4, and SOCKS5 proxies from various sources.

## Features

- Supports HTTP, SOCKS4, and SOCKS5 proxies
- Checks proxies from multiple sources (URLs or local files)
- Concurrent checking for faster results
- Measures proxy speed
- Saves working proxies to separate files based on type
- Color-coded console output for better readability

## Requirements

- Python 3.6+
- requests
- PySocks
- colorama

## Installation Instructions

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/ZoniBoy00/proxy-checker.git
cd proxy-checker
```

### 2. Install Dependencies

Install the required Python dependencies by running the following command:

```bash
pip install requests PySocks colorama
```

## Usage Instructions

1. Run the script:

```bash
python proxy_checker.py
```

2. When prompted, enter the proxy sources. You can use comma-separated URLs or file paths. For example:

```
Enter proxy sources (comma-separated URLs or file paths): https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt, https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt, https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt
```

3. The script will start checking the proxies and display the results in real-time.

4. Once finished, the script will save the working proxies to separate files:
   - `http_working_proxies.txt`
   - `socks4_working_proxies.txt`
   - `socks5_working_proxies.txt`

## Output

The script will display:
- Working proxies with their type and speed
- Total number of working proxies for each type
- Total number of proxies checked
- Total time taken for the operation

## Notes

- The script uses a timeout of 5 seconds for each proxy check. You can adjust this in the `check_proxy` function if needed.
- The maximum number of concurrent threads is set to 100. You can modify this in the `ThreadPoolExecutor` initialization if you want to change it.

## License

This project is open-source and available under the [MIT License](https://github.com/ZoniBoy00/proxy-checker/blob/main/LICENSE).

## Contributing

Feel free to submit issues or pull requests if you have any improvements or bug fixes to suggest.
