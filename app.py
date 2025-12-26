from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_strong_secret_key'

# Имитация базы данных
db_students = {
    "ivanov": {"name": "Иван Иванов", "group": "ИТ-21", "grades": {"Математика": 5, "Программирование": 5}},
    "petrov": {"name": "Петр Петров", "group": "ИТ-21", "grades": {"Математика": 4, "Программирование": 4}}
}

db_teachers = {
    "petrova": {"name": "Мария Петрова", "subject": "Программирование"}
}

db_schedule = {
    "ИТ-21": ["Пн (9:00): Программирование", "Ср (11:00): Математика"]
}

db_assignments = [
    {"id": 1, "title": "Лаб. работа 1", "group": "ИТ-21", "description": "Сделать API на Flask"}
]

def is_student():
    return session.get('role') == 'student'

def is_teacher():
    return session.get('role') == 'teacher'

@app.route('/')
def index():
    if is_student():
        return redirect(url_for('student_dashboard'))
    if is_teacher():
        return redirect(url_for('teacher_dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if username in db_students:
        session['user'] = username
        session['role'] = 'student'
        return redirect(url_for('student_dashboard'))
    elif username in db_teachers:
        session['user'] = username
        session['role'] = 'teacher'
        return redirect(url_for('teacher_dashboard'))
    flash("Пользователь не найден")
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect(url_for('index'))

# --- СТУДЕНТ ---

@app.route('/student/dashboard')
def student_dashboard():
    if not is_student(): return redirect(url_for('index'))
    student_data = db_students[session['user']]
    return render_template('student_dashboard.html', student=student_data)

# Посмотреть расписание
@app.route('/student/schedule')
def view_schedule():
    if not is_student(): return redirect(url_for('index'))
    user_group = db_students[session['user']]['group']
    group_schedule = db_schedule.get(user_group, ["Расписание пока не добавлено."])
    return render_template('schedule.html', schedule=group_schedule, role='student')

# Посмотреть оценки (использует dashboard)
@app.route('/student/grades')
def view_grades():
    if not is_student(): return redirect(url_for('index'))
    student_data = db_students[session['user']]
    return render_template('grades.html', student=student_data, role='student')

# Загрузить задание
@app.route('/student/upload', methods=['GET', 'POST'])
def upload_assignment_student():
    if not is_student(): return redirect(url_for('index'))
    if request.method == 'POST':
        # Здесь должна быть логика загрузки файла, сейчас это имитация
        flash(f"Задание '{request.form.get('title')}' успешно загружено.")
        return redirect(url_for('student_dashboard'))
    return render_template('publish_assignment.html', role='student', assignments=db_assignments)

# Редактировать профиль
@app.route('/student/edit_profile', methods=['GET', 'POST'])
def edit_profile_student():
    if not is_student(): return redirect(url_for('index'))
    if request.method == 'POST':
        # Логика обновления данных профиля в db_students
        db_students[session['user']]['name'] = request.form.get('name')
        flash("Профиль успешно обновлен.")
        return redirect(url_for('student_dashboard'))
    return render_template('edit_profile.html', student=db_students[session['user']])


# --- ПРЕПОДАВАТЕЛЬ ---

@app.route('/teacher/dashboard')
def teacher_dashboard():
    if not is_teacher(): return redirect(url_for('index'))
    return render_template('teacher_dashboard.html', teacher=db_teachers[session['user']])

# Посмотреть расписание (использует тот же шаблон)
@app.route('/teacher/schedule')
def view_schedule_teacher():
    if not is_teacher(): return redirect(url_for('index'))
    # Преподаватель может видеть все расписание
    all_schedule = [f"Группа {g}: {s}" for g, s_list in db_schedule.items() for s in s_list]
    return render_template('schedule.html', schedule=all_schedule, role='teacher')

# Выставить оценки (упрощенно)
@app.route('/teacher/grade', methods=['GET', 'POST'])
def grade_student():
    if not is_teacher(): return redirect(url_for('index'))
    if request.method == 'POST':
        student_user = request.form.get('username')
        subject = db_teachers[session['user']]['subject']
        grade = request.form.get('grade')
        if student_user in db_students and subject:
            db_students[student_user]['grades'][subject] = int(grade)
            flash(f"Оценка {grade} для {student_user} по {subject} выставлена.")
        return redirect(url_for('grade_student'))
    return render_template('grades.html', students=db_students, teacher_subject=db_teachers[session['user']]['subject'], role='teacher')

# Опубликовать задание
@app.route('/teacher/publish_assignment', methods=['GET', 'POST'])
def publish_assignment():
    if not is_teacher(): return redirect(url_for('index'))
    if request.method == 'POST':
        new_assignment = {
            "id": len(db_assignments) + 1,
            "title": request.form.get('title'),
            "group": request.form.get('group'),
            "description": request.form.get('description')
        }
        db_assignments.append(new_assignment)
        flash("Задание успешно опубликовано.")
        return redirect(url_for('teacher_dashboard'))
    # Передаем список групп, чтобы выбрать, для кого задание
    groups = list(db_schedule.keys())
    return render_template('publish_assignment.html', role='teacher', groups=groups)

# Посмотреть список студентов
@app.route('/teacher/students_list')
def students_list():
    if not is_teacher(): return redirect(url_for('index'))
    list_of_students = [(user, data['name'], data['group']) for user, data in db_students.items()]
    return render_template('students_list.html', students=list_of_students, role='teacher')

if __name__ == '__main__':
    app.run(debug=True)
