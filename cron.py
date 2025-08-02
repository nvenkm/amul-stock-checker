import os

def setup_cron_job(script_path):
    """Setup cron job to run every 5 minutes"""
    import subprocess
    
    # Find where Python is installed
    python_path = subprocess.run(['which', 'python3'], capture_output=True, text=True).stdout.strip()

    # Current working directory
    current_dir = subprocess.run(['pwd'], capture_output=True, text=True).stdout.strip()
    print(f"🔍 Current working directory: {current_dir}")

    if not python_path:
        print("❌ Python3 not found. Please install Python3 and try again.")
        return False
    print(f"🔍 Using Python at: {python_path}")

    cron_command = f"* * * * * {python_path} {script_path} --cron >> {current_dir}/log/amul-log.log 2>&1"
    
    try:
        # Get current crontab
        current_cron = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        
        print("Current cron le bhai tu pehle:",current_cron.stdout)

        # Check if our job already exists
        if cron_command in current_cron.stdout:
            print("✓ Cron job already exists")
            return True
        
        # Add our job to crontab
        new_cron = current_cron.stdout + f"\n{cron_command}\n"
        
        # Write new crontab
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_cron)

        # Check if log directory exists, if not create it
        log_dir = os.path.join(current_dir, 'log')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"✅ Created log directory: {log_dir}")
        
        if process.returncode == 0:
            print("✅ Cron job added successfully!")
            print(f"📅 Script will run every 1 minute")
            print(f"📁 Logs will be saved in: {current_dir}/log/amul-log.log")
            return True
        else:
            print("❌ Failed to add cron job")
            return False
            
    except FileNotFoundError:
        print("❌ Crontab not found. Make sure you're on a Unix-like system")
        return False
    except Exception as e:
        print(f"❌ Error setting up cron job: {e}")
        return False

def remove_cron_job(script_path):
    """Remove the cron job"""
    import subprocess
    
    cron_command = f"*/1 * * * * /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 {script_path} --cron >> /Users/naveen/Desktop/Timepass/amul-stock/cron/cron.log 2>&1"

    
    try:
        # Get current crontab
        current_cron = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        
        # Remove our job from crontab
        new_cron = current_cron.stdout.replace(cron_command + "\n", "")
        
        # Write new crontab
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_cron)
        
        if process.returncode == 0:
            print("✅ Cron job removed successfully!")
            return True
        else:
            print("❌ Failed to remove cron job")
            return False
            
    except Exception as e:
        print(f"❌ Error removing cron job: {e}")
        return False
