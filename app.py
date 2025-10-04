from flask import Flask, render_template, request, send_file, redirect, url_for
import pandas as pd
import io
import math
from datetime import datetime, timedelta

app = Flask(__name__)

def compute_allocation(subjects, difficulties, urgencies, total_hours):
    # Clean and convert
    entries = []
    for s, d, u in zip(subjects, difficulties, urgencies):
        name = s.strip()
        if name == "":
            continue
        try:
            d = float(d)
        except:
            d = 3.0
        try:
            u = float(u)
        except:
            u = 3.0
        weight = max(0.1, d + u)  # avoid zero
        entries.append({"subject": name, "difficulty": d, "urgency": u, "weight": weight})

    if not entries:
        return pd.DataFrame(columns=["subject", "difficulty", "urgency", "weight", "allocated_hours", "share_pct"])

    df = pd.DataFrame(entries)
    total_weight = df["weight"].sum()
    if total_weight == 0:
        df["allocated_hours"] = 0.0
        df["share_pct"] = 0.0
    else:
        df["share"] = df["weight"] / total_weight
        df["allocated_hours"] = (df["share"] * total_hours).round(2)
        # Ensure rounding does not exceed total_hours
        diff = round(total_hours - df["allocated_hours"].sum(), 2)
        if abs(diff) >= 0.01:
            # adjust largest weight entry
            idx = df["weight"].idxmax()
            df.loc[idx, "allocated_hours"] = round(df.loc[idx, "allocated_hours"] + diff, 2)
        df["share_pct"] = (df["share"] * 100).round(1)

    df = df[["subject", "difficulty", "urgency", "weight", "allocated_hours", "share_pct"]]
    df = df.sort_values(by="allocated_hours", ascending=False).reset_index(drop=True)
    return df

def generate_study_schedule(df, study_start_time="08:00", study_end_time="22:00", break_duration=15, 
                          max_breaks=None, total_break_time=None, break_frequency="auto"):
    """
    Generate a detailed study schedule with specific time blocks and customizable breaks
    
    Args:
        df: DataFrame with subjects and allocated hours
        study_start_time: Start time for study session
        study_end_time: End time for study session
        break_duration: Duration of each break in minutes
        max_breaks: Maximum number of breaks (optional)
        total_break_time: Total break time in minutes (optional)
        break_frequency: "auto", "frequent", "minimal" - controls break placement
    
    Returns:
        tuple: (schedule, warnings) where warnings is a list of any time constraint issues
    """
    if df.empty:
        return [], []
    
    # Parse start and end times
    start_hour, start_min = map(int, study_start_time.split(':'))
    end_hour, end_min = map(int, study_end_time.split(':'))
    
    start_time = datetime.now().replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
    end_time = datetime.now().replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
    
    # Handle case where end time is before start time (next day)
    if end_time <= start_time:
        end_time = end_time + timedelta(days=1)
    
    schedule = []
    warnings = []
    current_time = start_time
    
    # Sort subjects by urgency first, then difficulty (highest priority first)
    sorted_subjects = df.sort_values(['urgency', 'difficulty'], ascending=[False, False])
    
    # Calculate total study time needed
    total_study_minutes = int(df['allocated_hours'].sum() * 60)
    available_time_minutes = (end_time - start_time).total_seconds() / 60
    
    # Check if study time exceeds available time
    if total_study_minutes > available_time_minutes:
        warnings.append(f"Requested study time ({total_study_minutes/60:.1f}h) exceeds available time window ({available_time_minutes/60:.1f}h). Schedule will be truncated.")
        # Adjust study time to fit available window (leave some buffer for breaks)
        max_study_time = available_time_minutes * 0.9  # Use 90% of available time for study
        if total_study_minutes > max_study_time:
            # Scale down all subjects proportionally
            scale_factor = max_study_time / total_study_minutes
            df = df.copy()
            df['allocated_hours'] = df['allocated_hours'] * scale_factor
            total_study_minutes = int(df['allocated_hours'].sum() * 60)
            warnings.append(f"Study time scaled down to {total_study_minutes/60:.1f}h to fit your time window.")
    
    # Determine break strategy
    if break_frequency == "minimal":
        block_duration = min(90, total_study_minutes)  # Longer blocks, fewer breaks
    elif break_frequency == "frequent":
        block_duration = 25  # Shorter blocks, more breaks
    else:  # auto
        block_duration = 50  # Standard blocks
    
    # Adjust break duration based on user preferences
    if total_break_time is not None:
        # Calculate how many breaks we can fit
        remaining_time = available_time_minutes - total_study_minutes
        if remaining_time > 0:
            estimated_breaks = max(1, int(remaining_time / break_duration))
            if max_breaks:
                estimated_breaks = min(estimated_breaks, max_breaks)
            break_duration = min(break_duration, total_break_time / estimated_breaks) if estimated_breaks > 0 else break_duration
    
    break_count = 0
    max_break_count = max_breaks if max_breaks else float('inf')
    
    for _, subject in sorted_subjects.iterrows():
        subject_name = subject['subject']
        hours = subject['allocated_hours']
        
        # Convert hours to minutes for easier calculation
        total_minutes = int(hours * 60)
        remaining_minutes = total_minutes
        
        while remaining_minutes > 0 and current_time < end_time:
            # Calculate block duration (don't exceed remaining time or end time)
            if remaining_minutes >= block_duration:
                block_minutes = block_duration
            else:
                block_minutes = remaining_minutes
            
            # Check if we have enough time before end time
            block_end = current_time + timedelta(minutes=block_minutes)
            if block_end > end_time:
                # Adjust block to fit within available time
                available_minutes = (end_time - current_time).total_seconds() / 60
                if available_minutes < 15:  # Less than 15 minutes, skip
                    break
                block_minutes = min(block_minutes, available_minutes)
                block_end = current_time + timedelta(minutes=block_minutes)
            
            # Add study block
            schedule.append({
                'subject': subject_name,
                'start_time': current_time.strftime('%H:%M'),
                'end_time': block_end.strftime('%H:%M'),
                'duration': f"{block_minutes} min",
                'type': 'study',
                'difficulty': subject['difficulty'],
                'urgency': subject['urgency'],
                'hours_allocated': hours
            })
            
            current_time = block_end
            remaining_minutes -= block_minutes
            
            # Add break based on user preferences
            should_add_break = (
                remaining_minutes > 0 and 
                current_time < end_time and 
                break_count < max_break_count
            )
            
            # Additional break logic based on frequency
            if break_frequency == "minimal":
                # Only add breaks after longer study periods
                should_add_break = should_add_break and remaining_minutes >= block_duration
            elif break_frequency == "frequent":
                # Add breaks more often
                should_add_break = should_add_break and remaining_minutes >= 15
            
            if should_add_break:
                break_end = current_time + timedelta(minutes=break_duration)
                if break_end <= end_time:
                    schedule.append({
                        'subject': 'Break',
                        'start_time': current_time.strftime('%H:%M'),
                        'end_time': break_end.strftime('%H:%M'),
                        'duration': f"{break_duration} min",
                        'type': 'break',
                        'difficulty': 0,
                        'urgency': 0,
                        'hours_allocated': 0
                    })
                    current_time = break_end
                    break_count += 1
    
    return schedule, warnings

def calculate_schedule_stats(schedule):
    """Calculate statistics for the generated schedule"""
    study_blocks = [block for block in schedule if block['type'] == 'study']
    break_blocks = [block for block in schedule if block['type'] == 'break']
    
    total_study_time = sum(float(block['duration'].split()[0]) for block in study_blocks)
    total_break_time = sum(float(block['duration'].split()[0]) for block in break_blocks)
    
    return {
        'total_study_blocks': len(study_blocks),
        'total_break_blocks': len(break_blocks),
        'total_study_minutes': total_study_time,
        'total_break_minutes': total_break_time,
        'total_study_hours': round(total_study_time / 60, 1),
        'efficiency': round(total_study_time / (total_study_time + total_break_time) * 100, 1) if (total_study_time + total_break_time) > 0 else 0
    }

@app.route("/", methods=["GET"])
def index():
    # sample prefilled rows for convenience
    sample = [
        {"subject": "Calculus", "difficulty": 4, "urgency": 3},
        {"subject": "English Essay", "difficulty": 3, "urgency": 5},
        {"subject": "Physics", "difficulty": 5, "urgency": 2},
    ]
    return render_template("index.html", sample=sample)

@app.route("/tips", methods=["GET"])
def tips():
    study_tips = {
        "time_management": [
            "Use the Pomodoro Technique: 25 minutes focused study, 5-minute break",
            "Schedule your hardest subjects when you're most alert (usually morning)",
            "Take regular breaks every 45-60 minutes to maintain focus",
            "Use active recall: test yourself instead of just re-reading notes"
        ],
        "study_methods": [
            "Spaced repetition: review material at increasing intervals",
            "Interleaving: mix different subjects/topics in one study session",
            "Elaboration: explain concepts in your own words",
            "Dual coding: combine verbal and visual information"
        ],
        "motivation": [
            "Set specific, achievable goals for each study session",
            "Reward yourself after completing study blocks",
            "Study with friends or join study groups for accountability",
            "Track your progress to see improvement over time"
        ]
    }
    return render_template("tips.html", tips=study_tips)

@app.route("/plan", methods=["POST"])
def plan():
    # gather repeated form fields
    subjects = request.form.getlist("subject[]")
    difficulties = request.form.getlist("difficulty[]")
    urgencies = request.form.getlist("urgency[]")
    total_hours_raw = request.form.get("total_hours", "0")
    note = request.form.get("note", "")
    study_start_time = request.form.get("study_start_time", "08:00")
    study_end_time = request.form.get("study_end_time", "22:00")
    
    # Break preferences
    break_duration = int(request.form.get("break_duration", "15"))
    max_breaks_raw = request.form.get("max_breaks", "")
    total_break_time_raw = request.form.get("total_break_time", "")
    break_frequency = request.form.get("break_frequency", "auto")
    
    # Parse optional break parameters
    max_breaks = None
    if max_breaks_raw and max_breaks_raw.strip():
        try:
            max_breaks = int(max_breaks_raw)
        except:
            max_breaks = None
    
    total_break_time = None
    if total_break_time_raw and total_break_time_raw.strip():
        try:
            total_break_time = int(total_break_time_raw)
        except:
            total_break_time = None

    try:
        total_hours = float(total_hours_raw)
        if total_hours < 0:
            total_hours = 0.0
    except:
        total_hours = 0.0

    df = compute_allocation(subjects, difficulties, urgencies, total_hours)
    
    # Generate study schedule with custom break preferences
    schedule, schedule_warnings = generate_study_schedule(
        df, 
        study_start_time, 
        study_end_time, 
        break_duration,
        max_breaks,
        total_break_time,
        break_frequency
    )
    schedule_stats = calculate_schedule_stats(schedule)
    
    # prepare data for chart and table
    labels = list(df["subject"])
    hours = list(df["allocated_hours"])
    
    # store the dataframe CSV in memory for download
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    
    # Create schedule CSV
    schedule_df = pd.DataFrame(schedule)
    schedule_csv_buf = io.StringIO()
    schedule_df.to_csv(schedule_csv_buf, index=False)
    
    table_html = df.to_dict(orient="records")
    total_allocated = df["allocated_hours"].sum() if not df.empty else 0.0
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    return render_template("result.html",
                        table=table_html,
                        labels=labels,
                        hours=hours,
                        total_hours=total_hours,
                        total_allocated=round(total_allocated,2),
                        note=note,
                        timestamp=timestamp,
                        csv_text=csv_buf.getvalue(),
                        schedule=schedule,
                        schedule_stats=schedule_stats,
                        schedule_csv=schedule_csv_buf.getvalue(),
                        study_start_time=study_start_time,
                        study_end_time=study_end_time,
                        break_duration=break_duration,
                        max_breaks=max_breaks,
                        total_break_time=total_break_time,
                        break_frequency=break_frequency,
                        schedule_warnings=schedule_warnings)

@app.route("/download_csv", methods=["POST"])
def download_csv():
    # Expects csv_text and filename in form
    csv_text = request.form.get("csv_text", "")
    filename = request.form.get("filename", "study_plan.csv")
    if csv_text == "":
        return redirect(url_for("index"))
    bytes_io = io.BytesIO(csv_text.encode("utf-8"))
    bytes_io.seek(0)
    return send_file(bytes_io,
                    as_attachment=True,
                    download_name=filename,
                    mimetype="text/csv")

@app.route("/download_schedule", methods=["POST"])
def download_schedule():
    # Download schedule CSV
    schedule_csv = request.form.get("schedule_csv", "")
    filename = request.form.get("filename", "study_schedule.csv")
    if schedule_csv == "":
        return redirect(url_for("index"))
    bytes_io = io.BytesIO(schedule_csv.encode("utf-8"))
    bytes_io.seek(0)
    return send_file(bytes_io,
                    as_attachment=True,
                    download_name=filename,
                    mimetype="text/csv")

if __name__ == "__main__":
    app.run(debug=True)
