import random
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages   # for user feedback

# In‑memory data storage
students = {}
questions = []
responses = []
next_student_id = 1
next_question_id = 1   # will be set after init
topics = ["Math", "Science", "History", "Language"]

def init_questions():
    """Populate the questions list with initial questions and set next_question_id."""
    global questions, next_question_id
    questions.clear()
    questions.extend([
        {
            'id': 1,
            'topic': 'Math',
            'difficulty': 0.4,
            'text': 'What is 5 + 7?',
            'options': ['10', '11', '12', '13'],
            'correct': '12',
            'explanation': '5 + 7 = 12'
        },
        {
            'id': 2,
            'topic': 'Science',
            'difficulty': 0.5,
            'text': 'Which planet is known as the Red Planet?',
            'options': ['Earth', 'Mars', 'Jupiter', 'Venus'],
            'correct': 'Mars',
            'explanation': 'Mars is called the Red Planet because of its reddish appearance.'
        },
        {
            'id': 3,
            'topic': 'History',
            'difficulty': 0.5,
            'text': 'Who was the first President of the United States?',
            'options': ['Abraham Lincoln', 'George Washington', 'Thomas Jefferson', 'John Adams'],
            'correct': 'George Washington',
            'explanation': 'George Washington served as the first U.S. president from 1789 to 1797.'
        },
        {
            'id': 4,
            'topic': 'Math',
            'difficulty': 0.6,
            'text': 'What is the square root of 64?',
            'options': ['6', '7', '8', '9'],
            'correct': '8',
            'explanation': 'The square root of 64 is 8.'
        },
        {
            'id': 5,
            'topic': 'Science',
            'difficulty': 0.7,
            'text': 'What gas do plants absorb from the atmosphere?',
            'options': ['Oxygen', 'Nitrogen', 'Carbon Dioxide', 'Hydrogen'],
            'correct': 'Carbon Dioxide',
            'explanation': 'Plants absorb carbon dioxide for photosynthesis.'
        }
    ])
    next_question_id = max(q['id'] for q in questions) + 1

# Initialize questions at module load
init_questions()

# Helper functions (identical to before)
def update_student_performance(student_id, topic, is_correct):
    student = students[student_id]
    if topic not in student['performance']['topics']:
        student['performance']['topics'][topic] = {'correct': 0, 'total': 0}
    student['performance']['topics'][topic]['total'] += 1
    if is_correct:
        student['performance']['topics'][topic]['correct'] += 1

def get_next_topic(student_id):
    student = students[student_id]
    topics_data = student['performance']['topics']
    if not topics_data:
        return random.choice(topics)
    weakest_topic = None
    min_accuracy = 101
    for topic, data in topics_data.items():
        accuracy = (data['correct'] / data['total']) * 100
        if accuracy < min_accuracy:
            min_accuracy = accuracy
            weakest_topic = topic
    return weakest_topic or random.choice(topics)

def get_question(topic, asked_questions):
    topic_questions = [q for q in questions if q['topic'] == topic and q['id'] not in asked_questions]
    if topic_questions:
        return random.choice(topic_questions)
    all_questions = [q for q in questions if q['id'] not in asked_questions]
    if all_questions:
        return random.choice(all_questions)
    return None

# Views
def home(request):
    return render(request, 'index.html', {'students': students.values()})

def register_student(request):
    global next_student_id
    if request.method == 'POST':
        name = request.POST['name']
        student_id = next_student_id
        students[student_id] = {
            'id': student_id,
            'name': name,
            'performance': {'topics': {}},
            'last_updated': datetime.now().isoformat()
        }
        next_student_id += 1
    return redirect('home')

def student_dashboard(request, student_id):
    student = students.get(student_id)
    if not student:
        return redirect('home')
    # Compute accuracy for each topic
    for topic, data in student['performance']['topics'].items():
        if data['total'] > 0:
            data['accuracy'] = (data['correct'] / data['total']) * 100
        else:
            data['accuracy'] = 0.0
    student_responses = [r.copy() for r in responses if r['student_id'] == student_id]
    for resp in student_responses:
        q = next((q for q in questions if q['id'] == resp['question_id']), None)
        if q:
            resp['question_text'] = q['text']
            resp['topic'] = q['topic']
    return render(request, 'dashboard.html', {
        'student': student,
        'responses': student_responses,
        'performance': student['performance']
    })

def start_quiz(request, student_id):
    if student_id not in students:
        return redirect('home')
    request.session.flush()
    request.session['student_id'] = student_id
    request.session['question_count'] = 0
    request.session['correct_count'] = 0
    request.session['asked_questions'] = []
    request.session['quiz_results'] = []
    return redirect('show_question')

def show_question(request):
    if 'student_id' not in request.session:
        return redirect('home')
    topic = get_next_topic(request.session['student_id'])
    question = get_question(topic, request.session.get('asked_questions', []))
    if not question:
        return render(request, 'no_questions.html')
    request.session['current_question'] = question
    request.session['question_count'] = request.session.get('question_count', 0) + 1
    request.session['asked_questions'] = request.session.get('asked_questions', []) + [question['id']]
    return render(request, 'question.html', {
        'question': question,
        'question_count': request.session['question_count']
    })

def process_answer(request):
    if 'student_id' not in request.session or 'current_question' not in request.session:
        return redirect('home')
    student_id = request.session['student_id']
    question = request.session['current_question']
    user_answer = request.POST['response']
    is_correct = (user_answer == question['correct'])
    update_student_performance(student_id, question['topic'], is_correct)
    if is_correct:
        request.session['correct_count'] = request.session.get('correct_count', 0) + 1
    responses.append({
        'student_id': student_id,
        'question_id': question['id'],
        'response': user_answer,
        'timestamp': datetime.now().isoformat(),
        'correct': is_correct
    })
    results = request.session.get('quiz_results', [])
    results.append({
        'question': question,
        'response': user_answer,
        'is_correct': is_correct,
        'correct_answer': question['correct'],
        'explanation': question['explanation']
    })
    request.session['quiz_results'] = results
    students[student_id]['last_updated'] = datetime.now().isoformat()
    if request.session['question_count'] >= 5:
        return redirect('quiz_results')
    return redirect('show_question')

def quiz_results(request):
    if 'quiz_results' not in request.session:
        return redirect('home')
    quiz_results = request.session['quiz_results']
    student_id = request.session['student_id']
    student = students[student_id]
    question_count = request.session['question_count']
    correct_count = request.session['correct_count']
    if question_count > 0:
        accuracy = (correct_count / question_count) * 100
    else:
        accuracy = 0.0
    request.session.flush()
    return render(request, 'results.html', {
        'quiz_results': quiz_results,
        'student_name': student['name'],
        'student_id': student_id,
        'question_count': question_count,
        'correct_count': correct_count,
        'accuracy': accuracy,
    })

# ---------- NEW: Add Question ----------
def add_question(request):
    global next_question_id
    if request.method == 'POST':
        # Extract form data
        topic = request.POST.get('topic')
        difficulty = float(request.POST.get('difficulty', 0.5))
        text = request.POST.get('text')
        options = [
            request.POST.get('option1'),
            request.POST.get('option2'),
            request.POST.get('option3'),
            request.POST.get('option4'),
        ]
        correct = request.POST.get('correct')
        explanation = request.POST.get('explanation')

        # Basic validation
        if topic and text and all(options) and correct and explanation:
            new_question = {
                'id': next_question_id,
                'topic': topic,
                'difficulty': difficulty,
                'text': text,
                'options': options,
                'correct': correct,
                'explanation': explanation,
            }
            questions.append(new_question)
            next_question_id += 1
            messages.success(request, 'Question added successfully!')
        else:
            messages.error(request, 'All fields are required.')
        return redirect('add_question')

    # GET request – show form
    # Pass existing topics for suggestions (optional)
    existing_topics = sorted(set(q['topic'] for q in questions))
    return render(request, 'add_question.html', {'topics': existing_topics})