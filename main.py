#!/usr/bin/env python3
"""
Amul Product Stock Checker with Cron Job Integration
Checks if Amul Chocolate Whey Protein is in stock for pincode 641014
Can be run as a one-time check or scheduled with cron
"""

import argparse
from checker import AmulStockChecker
import sys
import os
import json
from cron import setup_cron_job, remove_cron_job

def show_status():
    """Show the current stock status from the saved file"""
    status_file = "amul_stock_status.json"
    
    try:
        if os.path.exists(status_file):
            with open(status_file, "r") as f:
                data = json.load(f)
            
            print("📊 Current Stock Status:")
            print(f"  Status: {data['status']}")
            print(f"  Pincode: {data['pincode']}")
            print(f"  Last Checked: {data['timestamp']}")
            print(f"  Product URL: {data['product_url']}")
        else:
            print("❌ No status file found. Run a stock check first.")
            
    except Exception as e:
        print(f"❌ Error reading status: {e}")

def main():
    """Main function to run the stock checker"""
    parser = argparse.ArgumentParser(description='Amul Product Stock Checker with Cron Integration')
    parser.add_argument('--cron', action='store_true', help='Run in cron mode (headless, minimal output)')
    parser.add_argument('--setup-cron', action='store_true', help='Setup cron job to run every 5 minutes')
    parser.add_argument('--remove-cron', action='store_true', help='Remove the cron job')
    parser.add_argument('--status', action='store_true', help='Show current stock status')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--log-file', type=str, help='Custom log file path')
    
    args = parser.parse_args()
    
    if args.setup_cron:
        setup_cron_job(os.path.abspath(__file__))
        return
    
    if args.remove_cron:
        remove_cron_job(os.path.abspath(__file__))
        return
    
    if args.status:
        show_status()
        return
    
    # Determine if running in headless mode
    headless = args.headless or args.cron
    
    if not args.cron:
        print("Amul Chocolate Whey Protein Stock Checker")
        print("Checking stock for pincode: 641014")
        print("-" * 50)
    
    # Run the stock checker
    checker = AmulStockChecker(headless=headless, log_file=args.log_file)
    
    success = checker.run_stock_check()
    
    if not success:
        if not args.cron:
            print("\n❌ Stock check failed due to errors")
        sys.exit(1)
    else:
        if not args.cron:
            print("\n✅ Stock check completed successfully")

if __name__ == "__main__":
    main()