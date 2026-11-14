# File Automator — Automated File Operating & Text-Parsing Script

A background automation utility that organizes a messy directory and mines flat log files for structured data (emails, transaction IDs, IP addresses), writing everything to a single clean CSV.

Built entirely on Python's standard library — no external dependencies.

## Features

- **Auto-sorts files by extension** into category subfolders (`Documents/`, `Images/`, `Logs/`, `Spreadsheets/`, `Scripts/`, `Archives/`, `Videos/`, `Other/`)
- **Extracts structured data** from `.log`/`.txt` files using regex: email addresses, transaction IDs, IP addresses
- **Writes a master CSV** with full traceability — every row records the source file and exact line number it came from
- **Persistent activity log** for every run, so it's safe to schedule unattended (cron / Task Scheduler)
- **Dry-run mode** to preview every action before anything is moved or written
- **Collision-safe** — never silently overwrites a file; auto-renames with a timestamp on conflict

## Requirements

- Python 3.9+
- No third-party packages — uses only `os`, `shutil`, `re`, `pathlib`, `csv`, `logging`, `argparse`

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Check your Python version

Requires Python 3.9+. No installation of packages needed — everything used is standard library.

```bash
python --version
```

> On Windows, use `python`. On macOS/Linux, this is usually `python3`.

### 3. Create a source folder with files to organize

If you don't already have a folder of files to test with, make one:

**macOS/Linux:**
```bash
mkdir unsorted_data
echo "Contact us at test@example.com or txn TXN-12345AB" > unsorted_data/sample.log
```

**Windows (PowerShell):**
```powershell
mkdir unsorted_data
Set-Content -Path unsorted_data\sample.log -Value "Contact us at test@example.com or txn TXN-12345AB" -Encoding utf8
```

> ⚠️ On Windows PowerShell specifically, always use `Set-Content -Encoding utf8` rather than `echo >` when creating log files — see the [Notes on Windows / PowerShell](#notes-on-windows--powershell) section below for why.

### 4. Preview with a dry run (recommended first step)

This shows exactly what the script *would* do — no files are moved, nothing is written.

```bash
python file_automator.py --source ./unsorted_data --dest ./organized --dry-run
```

### 5. Run it for real

```bash
python file_automator.py --source ./unsorted_data --dest ./organized
```

### 6. Check the results

```bash
# macOS/Linux
ls -R organized
cat organized/master_extracted_data.csv

# Windows PowerShell
Get-ChildItem organized -Recurse
type organized\master_extracted_data.csv
```

You should see your files sorted into category subfolders, plus `master_extracted_data.csv` containing every extracted email, transaction ID, and IP address, along with `file_automator_activity.log` recording every action taken.

## Usage

```bash
# Basic run
python file_automator.py --source ./unsorted_data --dest ./organized

# Preview only — nothing is moved or written
python file_automator.py --source ./unsorted_data --dest ./organized --dry-run

# Parse logs only, skip sorting
python file_automator.py --source ./unsorted_data --no-sort

# Suppress console output (activity log still written)
python file_automator.py --source ./unsorted_data --quiet
```

### CLI options

| Flag | Description |
|---|---|
| `--source` | **(required)** Path to the unorganized source directory |
| `--dest` | Destination root directory (default: `./organized`) |
| `--no-sort` | Skip file sorting, only parse logs |
| `--dry-run` | Preview actions without moving/writing anything |
| `--quiet` | Suppress console output |

## Output

Running the script produces:

```
organized/
├── Documents/
├── Images/
├── Logs/
├── Scripts/
├── Spreadsheets/
├── Archives/
├── Videos/
├── Other/
├── file_automator_activity.log
└── master_extracted_data.csv
```

**`master_extracted_data.csv`** columns:

| Column | Description |
|---|---|
| `source_file` | Name of the log/text file the match came from |
| `line_number` | Line in that file where the match was found |
| `match_type` | `email`, `transaction_id`, or `ip_address` |
| `match_value` | The matched text |
| `extracted_at` | Timestamp of extraction |

## Example

```bash
$ python file_automator.py --source ./unsorted_data --dest ./organized
INFO | Found 8 file(s) in source directory: unsorted_data
INFO | Moved access.log -> Logs/access.log
INFO | Moved report.pdf -> Documents/report.pdf
INFO | Parsed access.log: 4 match(es) found
INFO | Wrote 4 row(s) to master CSV: organized/master_extracted_data.csv
INFO | Run complete.
```

## Configuration

Extension-to-folder mapping and regex patterns are defined at the top of `file_automator.py` (`EXTENSION_MAP` and `PATTERNS`), so both can be extended without touching the core logic.

## Real-world use cases

- Scheduled cleanup of shared drives or download folders
- Reconciling transaction IDs and customer emails from payment/gateway logs
- First-pass security monitoring — flagging IPs/emails in auth logs before a full SIEM review
- Support-ticket log triage
- Pre-migration cleanup of a messy legacy file share

## Notes on Windows / PowerShell

If you're testing on Windows using PowerShell, be aware that `echo "text" > file.log` writes **UTF-16** by default, while this script reads files as **UTF-8** — mismatched encoding will cause regex matches to silently fail. Use:

```powershell
Set-Content -Path file.log -Value "your text" -Encoding utf8
```

to guarantee UTF-8 output when creating test log files.

## License

For academic/project use.
