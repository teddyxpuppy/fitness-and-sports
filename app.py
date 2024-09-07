from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="25315",
    database="hari"
)

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        cursor = db.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for('signup'))
        
        # Insert user details into the database
        cursor.execute("INSERT INTO users (name, username, password, role) VALUES (%s, %s, %s, %s)", 
                       (name, username, password, role))
        db.commit()
        cursor.close()
        
        flash("Sign-up successful!")
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = db.cursor()
        
        # Check user credentials and fetch role from the database
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        
        if user:
            session['username'] = username
            role = user[4]  # Assuming the 'role' is the 5th column (index 4) in the 'users' table
            
            session['role'] = role
            flash("Login successful!")
            
            if role == 'athlete':
                return redirect(url_for('athlete_dashboard'))
            elif role == 'academy':
                return redirect(url_for('academy_dashboard'))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for('login'))
    
    return render_template('index.html')

# Athlete Dashboard Route
@app.route('/athlete')
def athlete_dashboard():
    if 'username' in session and session['role'] == 'athlete':
        return render_template('athlete.html')
    else:
        flash("Unauthorized access!")
        return redirect(url_for('login'))
@app.route('/academy')
def academy_dashboard():
    if 'username' in session and session['role'] == 'academy':
        return render_template('aca.html')
    else:
        flash("Unauthorized access!")
        return redirect(url_for('login'))

# Redirection Route for Calorie, Exercise, and Sports
@app.route('/redirect', methods=['POST'])
def handle_redirection():
    if 'username' in session:
        option = request.form.get('option')
        if option == 'calorie':
            return redirect(url_for('calorie_intake'))
        elif option == 'exercise':
            return redirect(url_for('exercise_page'))
        elif option == 'sports':
            return redirect(url_for('sports_selection'))
    else:
        flash("Unauthorized access!")
        return redirect(url_for('login'))

# Calorie Intake Page
@app.route('/calorie')
def calorie_intake():
    return render_template('calorie.html')

# Exercise Page
@app.route('/exercise')
def exercise_page():
    return render_template('exercise.html')

# Sports Selection Page
@app.route('/sports')
def sports_selection():
    return render_template('spa.html')
@app.route('/search_sport', methods=['POST'])
def search_sport():
    sport = request.form.get('sport')
    
    cursor = db.cursor(dictionary=True)

    # Query to find coaches with the selected sport as their specialization
    cursor.execute("""
        SELECT a.name AS academy_name, a.address, a.phone AS academy_phone, a.email AS academy_email,
               c.name AS coach_name, c.specialization, c.phone AS coach_phone, c.email AS coach_email, c.achievements, c.certifications
        FROM academies a
        JOIN coaches c ON a.id = c.academy_id
        WHERE c.specialization = %s
    """, (sport,))
    
    result = cursor.fetchall()
    cursor.close()

    if result:
        return render_template('sport_results.html', sport=sport, data=result)
    else:
        flash(f"No academy or coach found specializing in {sport}")
        return redirect(url_for('sports_selection'))

# Result page to show matching academies and coaches
@app.route('/sport_results')
def sport_results():
    return render_template('sport_results.html')
@app.route('/submit_academy', methods=['POST'])
def submit_academy():
    academy_name = request.form.get('academyName')
    academy_address = request.form.get('academyAddress')
    academy_phone = request.form.get('academyPhone')
    academy_email = request.form.get('academyEmail')
    num_coaches = int(request.form.get('numCoaches'))
    
    cursor = db.cursor()
    
    # Insert academy details into the database
    cursor.execute("INSERT INTO academies (name, address, phone, email) VALUES (%s, %s, %s, %s)",
                   (academy_name, academy_address, academy_phone, academy_email))
    academy_id = cursor.lastrowid
    
    # Insert coach details into the database
    for i in range(1, num_coaches + 1):
        coach_name = request.form.get(f'coachName{i}')
        coach_specialization = request.form.get(f'coachSpecialization{i}')
        coach_achievements = request.form.get(f'coachAchievements{i}')
        coach_phone = request.form.get(f'coachPhone{i}')
        coach_email = request.form.get(f'coachEmail{i}')
        coach_certifications = request.form.get(f'coachCertifications{i}')
        coach_gender = request.form.get(f'coachGender{i}')
        
        cursor.execute("INSERT INTO coaches (academy_id, name, specialization, achievements, phone, email, certifications, gender) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (academy_id, coach_name, coach_specialization, coach_achievements, coach_phone, coach_email, coach_certifications, coach_gender))
    
    db.commit()
    cursor.close()

    # Redirect to the submit.html page after successful registration
    return redirect(url_for('submit_page'))

# Submit Page Route
@app.route('/submit')
def submit_page():
    return render_template('submit.html')

if __name__ == '__main__':
    app.run(debug=True)
