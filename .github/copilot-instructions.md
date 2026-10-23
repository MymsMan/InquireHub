# InquireHub AI Coding Agent Instructions

## Project Overview
- **Purpose:** Automate monitoring and control of the Greenpacket Y5-210MU 4G/5G router supplied by 3 (Three) UK.
- **Main script:** `InquireHub.py` (single-file utility)
- **Outputs:** Data is displayed, saved as CSV, and returned as JSON. Log and config files can be downloaded.

## Key Workflows
- **Run the script:**
  - `python InquireHub.py [function] [options]`
  - Example: `python InquireHub.py -p <password> -f`
- **Functions:**
  - Query hub status and save to CSV: `-f` or `--CSVfile [CSVFILE]`
  - Download logs: `-l [LOGPATH]`
  - Download config: `-c [CONFIGPATH]`
  - Ping website: `-pi [PINGURL]`
  - Reset traffic stats: `-rs`
  - Reboot hub: `--reboot`
- **Options:**
  - Credentials: `-u [USERID]` (default: admin), `-p [PASSWORD]`
  - Router URL: `-url [URL]` (default: https://192.168.0.1)
  - Output control: `-hdr`, `-nohdr`, `-v`, `-q`

## Customization Patterns
- **User credentials and output paths** can be set by editing constants at the top of `InquireHub.py`:
  - `USERNAME`, `PASSWORD`, `DEFAULT_PATH`, `CSVFILE`, `LOGPATH`, `CONFIGPATH`
- **Data selection:**
  - Edit the `query_list` structure in `InquireHub.py` to change which fields are queried and output.
  - Array fields require explicit indexes (looping not supported).

## Integration Points
- **External dependencies:** Only `requests` (install via `pip install requests`).
- **Scheduling:** Use Windows Task Scheduler or Linux `cron` for automation.
- **Spreadsheet integration:** Output CSV is designed for Google Sheets (see linked template in README).

## Project-Specific Quirks
- Hub login and data retrieval may intermittently fail; retry if needed.
- Date/time and numeric formats may be inconsistent.
- Daylight Saving option on hub can affect uptime reporting.
- Host info query is positioned last due to reliability issues.

## Example Usage
```shell
python InquireHub.py -p <password> -f -v
python InquireHub.py -p <password> -l
python InquireHub.py -p <password> --reboot
python InquireHub.py -p <password> -pi microsoft.com
```

## References
- See `ReadMe.md` for full documentation, usage examples, and links to Google Sheets templates.
- Master repository: https://github.com/MymsMan/InquireHub

---
**Feedback:** If any section is unclear or missing, please specify so it can be improved for future AI agents.
