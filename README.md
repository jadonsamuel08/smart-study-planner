# 🎓 Smart Study Planner

<div align="center">

![Smart Study Planner](https://img.shields.io/badge/Study-Planner-blue?style=for-the-badge&logo=graduation-cap)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0+-red?style=for-the-badge&logo=flask)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3+-purple?style=for-the-badge&logo=bootstrap)

**An intelligent study scheduling web application that optimizes your study time based on subject difficulty, urgency, and your available time slots.**

[🚀 Features](#-features) • [📦 Installation](#-installation) • [🎯 Usage](#-usage) • [📊 Screenshots](#-screenshots) • [🔧 API](#-api) • [🤝 Contributing](#-contributing)

</div>

---

## ✨ Features

### 🧠 **Intelligent Study Allocation**
- **Smart Weight Calculation**: Combines difficulty and urgency to prioritize subjects
- **Proportional Time Distribution**: Allocates study hours based on subject importance
- **Visual Progress Indicators**: Real-time feedback on study time distribution

### 📅 **Advanced Scheduling System**
- **Customizable Time Windows**: Set your available study hours (supports overnight schedules)
- **Flexible Break Management**: 
  - Auto, Frequent, or Minimal break patterns
  - Custom break duration (5-60 minutes)
  - Optional max breaks and total break time limits
- **Time Constraint Handling**: Automatically adjusts schedules when study time exceeds available time
- **Priority-Based Ordering**: Most urgent and difficult subjects scheduled first

### 🎨 **Modern User Interface**
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Interactive Charts**: Beautiful Chart.js visualizations
- **Real-time Validation**: Instant feedback on form inputs
- **Dynamic Subject Management**: Add/remove subjects with ease
- **Keyboard Shortcuts**: Power user features for efficiency

### 📊 **Comprehensive Analytics**
- **Study Statistics**: Track study blocks, breaks, and efficiency
- **Export Options**: Download CSV files for study plans and schedules
- **Print Support**: Clean print layouts for physical copies
- **Progress Tracking**: Visual indicators for study progress

### 🔧 **Smart Features**
- **Auto-Save**: Form data persists during session
- **Study Tips**: Built-in productivity guidance
- **Error Handling**: Graceful handling of edge cases
- **Cross-browser Support**: Works on all modern browsers

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smart-study-planner.git
   cd smart-study-planner
   ```

2. **Install dependencies**
   ```bash
   pip install Flask pandas
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

### Alternative Installation (with virtual environment)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install Flask pandas

# Run the application
python app.py
```

---

## 🎯 Usage

### 1. **Create Your Study Plan**

1. **Add Subjects**: Enter your study subjects with difficulty (1-5) and urgency (1-5) ratings
2. **Set Total Hours**: Specify how many hours you want to study
3. **Choose Time Window**: Set your available study start and end times
4. **Customize Breaks**: 
   - Select break frequency (Auto, Frequent, Minimal)
   - Set break duration
   - Optionally specify max breaks or total break time

### 2. **Review Your Schedule**

- **Study Plan Overview**: See how time is allocated across subjects
- **Visual Charts**: Interactive bar charts showing time distribution
- **Detailed Schedule**: Hour-by-hour breakdown with breaks included
- **Statistics**: Study blocks, breaks, and efficiency metrics

### 3. **Export and Save**

- **Download CSV**: Get your study plan as a spreadsheet
- **Print Schedule**: Clean print layout for physical copies
- **Save for Later**: Bookmark or screenshot your schedule

### 4. **Time Constraint Handling**

The system intelligently handles scenarios where your requested study time exceeds your available time window:

- **Automatic Scaling**: Proportionally reduces all subjects to fit your time
- **Clear Warnings**: Explains what adjustments were made
- **Smart Suggestions**: Real-time feedback on time constraints

---

## 📊 Screenshots

<div align="center">

### Main Interface
![Main Interface](docs/screenshots/main-interface.png)

### Study Plan Results
![Study Plan Results](docs/screenshots/study-plan.png)

### Schedule View
![Schedule View](docs/screenshots/schedule-view.png)

### Break Customization
![Break Customization](docs/screenshots/break-settings.png)

</div>

---

## 🔧 API

### Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Main study planner interface |
| `/plan` | POST | Generate study plan and schedule |
| `/download_csv` | POST | Download study plan as CSV |
| `/download_schedule` | POST | Download schedule as CSV |
| `/tips` | GET | Study tips and guidance |

### Request Parameters

#### POST `/plan`

```json
{
  "subject[]": ["Mathematics", "Physics", "Chemistry"],
  "difficulty[]": [5, 4, 3],
  "urgency[]": [4, 5, 2],
  "total_hours": "8",
  "study_start_time": "08:00",
  "study_end_time": "22:00",
  "break_duration": "15",
  "max_breaks": "6",
  "total_break_time": "90",
  "break_frequency": "auto",
  "note": "Final exam preparation"
}
```

#### Response

```json
{
  "schedule": [
    {
      "subject": "Mathematics",
      "start_time": "08:00",
      "end_time": "09:30",
      "duration": "90 min",
      "type": "study",
      "difficulty": 5.0,
      "urgency": 4.0
    }
  ],
  "schedule_stats": {
    "total_study_blocks": 6,
    "total_break_blocks": 3,
    "total_study_minutes": 480.0,
    "total_break_minutes": 45.0,
    "efficiency_percentage": 91.4
  },
  "warnings": []
}
```

---

## 🏗️ Architecture

```
smart_study_planner/
├── app.py                 # Main Flask application
├── templates/
│   ├── index.html        # Main study planner interface
│   ├── result.html       # Study plan results page
│   └── tips.html         # Study tips page
├── static/
│   ├── style.css         # Custom styling
│   └── script.js         # Frontend JavaScript
├── docs/
│   └── screenshots/      # Documentation images
└── README.md             # This file
```

### Key Components

- **`app.py`**: Flask backend with study allocation algorithms
- **`generate_study_schedule()`**: Core scheduling logic with break management
- **`compute_allocation()`**: Subject weight calculation and time distribution
- **Frontend**: Bootstrap 5 + Chart.js for modern UI/UX
- **Real-time validation**: JavaScript for instant user feedback

---

## 🎨 Customization

### Break Patterns

| Pattern | Description | Block Duration | Break Duration |
|---------|-------------|----------------|----------------|
| **Auto** | Balanced approach | 50 minutes | 15 minutes |
| **Frequent** | More breaks for focus | 25 minutes | 5-10 minutes |
| **Minimal** | Deep work sessions | 90 minutes | 15-20 minutes |

### Time Constraints

The system handles various time constraint scenarios:

- **Over-allocated**: Study time > Available time → Proportional scaling
- **Overnight schedules**: Start time after end time → Next-day handling
- **Minimal time**: < 30 minutes available → Efficient micro-scheduling

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 Bug Reports
1. Check existing issues first
2. Provide detailed reproduction steps
3. Include browser/OS information

### ✨ Feature Requests
1. Describe the feature clearly
2. Explain the use case
3. Consider implementation complexity

### 💻 Code Contributions
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 🧪 Testing
```bash
# Run the application
python app.py

# Test various scenarios
# - Different time windows
# - Various break patterns
# - Edge cases (overnight, minimal time)
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Bootstrap** for the responsive UI framework
- **Chart.js** for beautiful data visualizations
- **Font Awesome** for the comprehensive icon library
- **Flask** for the lightweight web framework

---


---

<div align="center">

**Made with ❤️ for students everywhere**

[⬆️ Back to top](#-smart-study-planner)

</div>
