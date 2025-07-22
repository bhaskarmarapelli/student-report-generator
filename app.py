from flask import Flask, request, render_template
import pandas as pd
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Expected column names from the CSV
required_columns = [
    'Roll No', 'Name', 'Hostel status', 'cgpa', 'Total Registerd credits',
    'Result Declared Credits', 'Result Awaiting Credits', 'Obtained Credits',
    'Cumulative Grade Points', 'Missing Courses', 'Not Declared Courses',
    'Error', 'Credit Requirements', 'Attained', 'Not Attained',
    'Requirements Error', 'Backlog Count', 'Backlog Details'
]

# Load student data from CSV
try:
    df = pd.read_csv('studentcgpa_data.csv', dtype={'Roll No': str})
    # Normalize column names (strip spaces, ensure consistent case)
    df.columns = [col.strip() for col in df.columns]
    app.logger.debug(f"CSV loaded successfully with {len(df)} records")
    app.logger.debug(f"CSV columns: {df.columns.tolist()}")
    app.logger.debug(f"First row: {df.iloc[0].to_dict()}")
    # Check for missing columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        app.logger.error(f"Missing columns in CSV: {missing_columns}")
        df = pd.DataFrame()
except FileNotFoundError:
    df = pd.DataFrame()
    app.logger.error("Error: studentcgpa_data.csv not found in the current directory")
except pd.errors.EmptyDataError:
    df = pd.DataFrame()
    app.logger.error("Error: studentcgpa_data.csv is empty")
except Exception as e:
    df = pd.DataFrame()
    app.logger.error(f"Error loading CSV: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def index():
    student = None
    error_message = None
    if request.method == 'POST':
        roll_no = request.form.get('roll_no').strip()
        app.logger.debug(f"Searching for Roll No: '{roll_no}'")
        if df.empty:
            error_message = "Error: studentcgpa_data.csv file is missing, empty, or has missing columns."
        else:
            student_data = df[df['Roll No'].astype(str) == roll_no].to_dict('records')
            if student_data:
                student = student_data[0]
                # Split Not Declared Courses and Backlog Details into lists
                student['Not Declared Courses'] = (
                    student['Not Declared Courses'].split('||')
                    if 'Not Declared Courses' in student and pd.notna(student['Not Declared Courses'])
                    else []
                )
                student['Backlog Details'] = (
                    student['Backlog Details'].split('||')
                    if 'Backlog Details' in student and pd.notna(student['Backlog Details'])
                    else []
                )
                app.logger.debug(f"Found student: {student['Name']}")
            else:
                error_message = f"No student found with Roll No: {roll_no}. Available Roll Nos: {', '.join(df['Roll No'].tolist())}"
                app.logger.debug(f"No match for Roll No: {roll_no}")
    return render_template('index.html', student=student, error_message=error_message)

if __name__ == '__main__':
    app.run()