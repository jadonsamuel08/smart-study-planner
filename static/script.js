function createRow(subject="", difficulty=3, urgency=3){
const wrapper = document.createElement("div");
wrapper.className = "row g-2 align-items-end subject-row mb-2";

wrapper.innerHTML = `
    <div class="col-md-5">
    <label class="form-label visually-hidden">Subject</label>
    <input type="text" name="subject[]" class="form-control" placeholder="Enter subject name" value="${subject}" required>
    </div>
    <div class="col-md-2">
    <label class="form-label small">Difficulty</label>
    <select name="difficulty[]" class="form-select" data-indicator="difficulty">
        <option value="1" ${difficulty==1 ? "selected":""}>1 - Easy</option>
        <option value="2" ${difficulty==2 ? "selected":""}>2 - Light</option>
        <option value="3" ${difficulty==3 ? "selected":""}>3 - Moderate</option>
        <option value="4" ${difficulty==4 ? "selected":""}>4 - Hard</option>
        <option value="5" ${difficulty==5 ? "selected":""}>5 - Very Hard</option>
    </select>
    </div>
    <div class="col-md-2">
    <label class="form-label small">Urgency</label>
    <select name="urgency[]" class="form-select" data-indicator="urgency">
        <option value="1" ${urgency==1 ? "selected":""}>1 - Low</option>
        <option value="2" ${urgency==2 ? "selected":""}>2 - Medium</option>
        <option value="3" ${urgency==3 ? "selected":""}>3 - High</option>
        <option value="4" ${urgency==4 ? "selected":""}>4 - Very High</option>
        <option value="5" ${urgency==5 ? "selected":""}>5 - Critical</option>
    </select>
    </div>
    <div class="col-md-2">
    <label class="form-label small">Weight</label>
    <div class="form-control-plaintext text-center fw-bold" data-weight-display>
        ${difficulty + urgency}
    </div>
    </div>
    <div class="col-md-1">
    <button type="button" class="btn btn-outline-danger btn-sm remove-row w-100" title="Remove subject">
        <i class="fas fa-trash"></i>
    </button>
    </div>
`;

// Add event listeners for dynamic weight calculation
const difficultySelect = wrapper.querySelector('select[name="difficulty[]"]');
const urgencySelect = wrapper.querySelector('select[name="urgency[]"]');
const weightDisplay = wrapper.querySelector('[data-weight-display]');

function updateWeight() {
    const diff = parseInt(difficultySelect.value);
    const urg = parseInt(urgencySelect.value);
    const weight = diff + urg;
    weightDisplay.textContent = weight;
    
    // Add visual indicator based on weight
    weightDisplay.className = 'form-control-plaintext text-center fw-bold';
    if (weight <= 3) weightDisplay.classList.add('text-success');
    else if (weight <= 6) weightDisplay.classList.add('text-warning');
    else weightDisplay.classList.add('text-danger');
}

difficultySelect.addEventListener('change', updateWeight);
urgencySelect.addEventListener('change', updateWeight);

return wrapper;
}

function addRowTo(wrapper, subject="", difficulty=3, urgency=3){
const row = createRow(subject, difficulty, urgency);
wrapper.appendChild(row);
row.querySelector(".remove-row").addEventListener("click", function(){
    row.remove();
    updateSubjectCount();
});
updateSubjectCount();
}

function updateSubjectCount() {
const subjectCount = document.querySelectorAll('.subject-row').length;
const countElement = document.getElementById('subject-count');
if (countElement) {
    countElement.textContent = `${subjectCount} subject${subjectCount !== 1 ? 's' : ''}`;
}
}

function validateForm() {
const subjects = document.querySelectorAll('input[name="subject[]"]');
const totalHours = document.getElementById('total-hours').value;
let hasError = false;

// Clear previous error states
document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

// Validate subjects
subjects.forEach((input, index) => {
    if (!input.value.trim()) {
        input.classList.add('is-invalid');
        hasError = true;
    }
});

// Validate total hours
if (!totalHours || parseFloat(totalHours) < 0.5) {
    document.getElementById('total-hours').classList.add('is-invalid');
    hasError = true;
}

if (subjects.length === 0) {
    alert('Please add at least one subject!');
    hasError = true;
}

return !hasError;
}

document.addEventListener("DOMContentLoaded", function(){
const wrapper = document.getElementById("subjects-wrapper");
const addBtn = document.getElementById("add-row");
const resetBtn = document.getElementById("reset-sample");
const form = document.getElementById("planner-form");
const generateBtn = document.getElementById("generate-btn");

// Initialize with sample data if available
if (typeof sample !== "undefined" && Array.isArray(sample) && sample.length > 0){
    sample.forEach(s => addRowTo(wrapper, s.subject, s.difficulty, s.urgency));
} else {
    // default single empty row
    addRowTo(wrapper, "", 3, 3);
}

addBtn.addEventListener("click", function(){
    addRowTo(wrapper, "", 3, 3);
    // Scroll to the new row
    wrapper.lastElementChild.scrollIntoView({ behavior: 'smooth' });
});

resetBtn.addEventListener("click", function(){
    wrapper.innerHTML = "";
    if (typeof sample !== "undefined" && Array.isArray(sample) && sample.length > 0){
        sample.forEach(s => addRowTo(wrapper, s.subject, s.difficulty, s.urgency));
    } else {
        addRowTo(wrapper, "", 3, 3);
    }
});

// Form submission with validation and loading state
form.addEventListener("submit", function(e){
    if (!validateForm()) {
        e.preventDefault();
        return false;
    }
    
    // Show loading state
    generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating Plan...';
    generateBtn.disabled = true;
    
    // Add a small delay for better UX
    setTimeout(() => {
        form.submit();
    }, 500);
});

// Real-time validation feedback
wrapper.addEventListener('input', function(e) {
    if (e.target.name === 'subject[]') {
        e.target.classList.remove('is-invalid');
    }
});

document.getElementById('total-hours').addEventListener('input', function(e) {
    e.target.classList.remove('is-invalid');
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        form.dispatchEvent(new Event('submit'));
    }
    
    // Ctrl/Cmd + Plus to add new row
    if ((e.ctrlKey || e.metaKey) && (e.key === '+' || e.key === '=')) {
        e.preventDefault();
        addBtn.click();
    }
});

// Add tooltips for better UX
const tooltipTriggerList = [].slice.call(document.querySelectorAll('[title]'));
tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

// Break preferences interaction
const breakFrequencySelect = document.querySelector('select[name="break_frequency"]');
const maxBreaksInput = document.querySelector('input[name="max_breaks"]');
const totalBreakTimeInput = document.querySelector('input[name="total_break_time"]');
const breakDurationInput = document.querySelector('input[name="break_duration"]');

function updateBreakSuggestions() {
    const frequency = breakFrequencySelect.value;
    const duration = parseInt(breakDurationInput.value) || 15;
    
    // Clear current suggestions
    maxBreaksInput.placeholder = "Auto";
    totalBreakTimeInput.placeholder = "Auto";
    
    // Update suggestions based on frequency
    switch(frequency) {
        case 'frequent':
            maxBreaksInput.placeholder = "6-10 (suggested)";
            totalBreakTimeInput.placeholder = `${duration * 6}-${duration * 10} min`;
            break;
        case 'minimal':
            maxBreaksInput.placeholder = "2-4 (suggested)";
            totalBreakTimeInput.placeholder = `${duration * 2}-${duration * 4} min`;
            break;
        default: // auto
            maxBreaksInput.placeholder = "Auto";
            totalBreakTimeInput.placeholder = "Auto";
    }
}

// Add event listeners for break preferences
if (breakFrequencySelect) {
    breakFrequencySelect.addEventListener('change', updateBreakSuggestions);
}

if (breakDurationInput) {
    breakDurationInput.addEventListener('input', updateBreakSuggestions);
}

// Initialize break suggestions
updateBreakSuggestions();

// Time validation
const totalHoursInput = document.getElementById('total-hours');
const startTimeInput = document.querySelector('input[name="study_start_time"]');
const endTimeInput = document.querySelector('input[name="study_end_time"]');

function calculateAvailableTime() {
    if (!startTimeInput.value || !endTimeInput.value) return null;
    
    const startTime = new Date(`2000-01-01T${startTimeInput.value}:00`);
    const endTime = new Date(`2000-01-01T${endTimeInput.value}:00`);
    
    // Handle case where end time is next day
    if (endTime <= startTime) {
        endTime.setDate(endTime.getDate() + 1);
    }
    
    const diffMs = endTime - startTime;
    const diffHours = diffMs / (1000 * 60 * 60);
    return diffHours;
}

function validateTimeConstraints() {
    const totalHours = parseFloat(totalHoursInput.value) || 0;
    const availableTime = calculateAvailableTime();
    
    if (availableTime && totalHours > availableTime) {
        // Show warning
        let warningDiv = document.getElementById('time-warning');
        if (!warningDiv) {
            warningDiv = document.createElement('div');
            warningDiv.id = 'time-warning';
            warningDiv.className = 'alert alert-warning mt-2';
            totalHoursInput.parentNode.appendChild(warningDiv);
        }
        warningDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-1"></i>
            <strong>Time Constraint:</strong> You've requested ${totalHours} hours of study, 
            but your time window (${startTimeInput.value} - ${endTimeInput.value}) only allows 
            ${availableTime.toFixed(1)} hours. The system will automatically adjust your schedule.
        `;
        warningDiv.style.display = 'block';
    } else {
        // Hide warning
        const warningDiv = document.getElementById('time-warning');
        if (warningDiv) {
            warningDiv.style.display = 'none';
        }
    }
}

// Add event listeners for time validation
if (totalHoursInput) {
    totalHoursInput.addEventListener('input', validateTimeConstraints);
}

if (startTimeInput) {
    startTimeInput.addEventListener('change', validateTimeConstraints);
}

if (endTimeInput) {
    endTimeInput.addEventListener('change', validateTimeConstraints);
}

// Initial validation
setTimeout(validateTimeConstraints, 100);
});
