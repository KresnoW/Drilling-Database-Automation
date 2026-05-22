import subprocess
import time

# List your scripts in the exact order they need to run
scripts = [
    "main.py",          # Step 1: Cleans raw data & builds the master database
    "coal_summary.py",  # Step 2: Creates the seam thickness logs
    "coal_rank.py",     # Step 3: Generates the quality reports (CVAR, TM, TS, ASH)
    "lith_summary.py",  # Step 4: Runs lithology percentage distribution
    "rig_drilled.py",   # Step 5: Summarizes total depths per rig
    "daily_report.py"   # Step 6: Generates the daily PDF report
]

print("🚀 Starting Data Update Automation...\n" + "="*40)
start_time = time.time()

for script in scripts:
    print(f"⏳ Running: {script}...")
    try:
        result = subprocess.run(["python", script], check=True, text=True, capture_output=True)
        print(f"✅ Success: {script} finished perfectly.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {script}:")
        print(e.stderr)
        print("🛑 Automation stopped due to script error.")
        break
    print("-"*40)

end_time = time.time()
print(f"\n🎉 All databases updated and PDF report generated in {round(end_time - start_time, 2)} seconds!")