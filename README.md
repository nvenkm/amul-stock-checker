# 📦 Amul Product Stock Checker

A Python CLI tool that checks if **Amul Chocolate Whey Protein** is in stock for a specific pincode (`641014`).  
It can be run as a one-time script or scheduled automatically using **cron jobs**.

---

## 🚀 Usage

```bash
python main.py [OPTIONS]
```

| Argument        | Type   | Description                                                                |
| --------------- | ------ | -------------------------------------------------------------------------- |
| `--cron`        | Flag   | Runs in **cron mode** (headless, minimal output). Intended for automation. |
| `--setup-cron`  | Flag   | Sets up a **cron job** to run the checker every 5 minutes.                 |
| `--remove-cron` | Flag   | Removes the previously configured **cron job**.                            |
| `--status`      | Flag   | Displays the **last saved stock status** from `amul_stock_status.json`.    |
| `--headless`    | Flag   | Runs the scraper in **headless mode** (no browser window opens).           |
| `--log-file`    | String | Path to a **custom log file** where logs will be saved.                    |

## 📊 Example Commands

### Setup cron job (every 5 minutes):

```bash
python main.py --setup-cron
```

### Check stock once (normal mode):

```bash
python main.py
```

### Run in headless mode::

```bash
python main.py --headless
```

### Show last saved stock status:

```bash
python main.py --status
```

### Remove cron job:

```bash
python main.py --remove-cron
```

## 🔧 Integration with Cron

Once `--setup-cron` is used, the script will automatically run every 5 minutes in headless mode.
Logs and stock status updates will be handled automatically.

---
