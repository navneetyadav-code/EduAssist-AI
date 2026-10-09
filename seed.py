from app import app
from extensions import db
from models import Admin, Setting, Knowledge, Subject
from werkzeug.security import generate_password_hash

with app.app_context():
    # 1. Create tables
    db.create_all()

    # 2. Add default Admin if not exists
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', password_hash=generate_password_hash('ChangeMe123!'))
        db.session.add(admin)

    # 3. Add default settings
    default_settings = {
        'institute_name': 'EduAssist AI',
        'welcome_message': 'Welcome to EduAssist AI! I am the AI Student Assistant developed by Navneet Kumar Yadav. How can I help you today?',
        'fallback_message': 'I could not find that information in my knowledge base. Please contact the EduAssist AI office directly.',
        'out_of_scope_message': 'Sorry, I can only help with information related to EduAssist AI and the subjects taught here.'
    }
    for key, value in default_settings.items():
        s = db.session.get(Setting, key)
        if not s:
            db.session.add(Setting(setting_key=key, setting_value=value))
        else:
            # Force update the name to EduAssist AI if they already ran the seed script previously
            if key == 'institute_name' and s.setting_value in ['Your Coaching Institute', 'Aadi Shree Classes']:
                s.setting_value = 'EduAssist AI'

    # 4. Add default subjects
    default_subjects = [
        ('Mathematics', '9-12', 'Mathematics taught at the institute'),
        ('Physics', '11-12', 'Physics taught at the institute'),
        ('Chemistry', '11-12', 'Chemistry taught at the institute'),
        ('Biology', '11-12', 'Biology taught at the institute'),
        ('English', '9-12', 'English taught at the institute')
    ]
    for name, class_level, desc in default_subjects:
        if not Subject.query.filter_by(name=name).first():
            db.session.add(Subject(name=name, class_level=class_level, description=desc))

    # 5. Add default knowledge (25 Templates)
    default_knowledge = [
        ('About Institute', 'general', 'EduAssist AI is a premier educational platform dedicated to providing top-quality coaching for students. We focus on conceptual clarity and overall academic excellence.', 'about,institute,who are you'),
        ('Developer Information', 'general', 'This AI Chatbot was developed by Navneet Kumar Yadav to assist students with their academic queries using modern AI technology.', 'developer,who made this,creator,navneet,yadav'),
        ('Contact Information', 'contact', 'You can reach our support desk at +91-9876543210 or email us at support@eduassistai.com for any inquiries between 9 AM and 6 PM.', 'phone,number,contact,call,email'),
        ('Address', 'contact', 'EduAssist AI is a digital-first platform, with our primary administrative office located in New Delhi, India.', 'address,location,where,map'),
        ('Courses Offered', 'academic', 'We offer coaching for Classes 9 and 10 (All Subjects) and Classes 11 and 12 (Science Stream). We also provide specialized preparation for competitive exams.', 'courses,classes,what do you teach'),
        ('Fee Structure', 'fees', 'Our annual fee structure is highly competitive and varies by class level. Fees can be paid in flexible installments. Please contact the front desk for exact pricing for your specific grade.', 'fees,cost,price'),
        ('Scholarship Programs', 'admission', 'We offer merit-based scholarships based on our Annual Talent Search Examination held in March every year.', 'scholarship,discount,free'),
        ('Admission Process', 'admission', 'To take admission, students can register online via our website or visit our administrative office to fill out the application form.', 'admission,apply,join,register'),
        ('Entrance Test', 'admission', 'Direct admission is available for students who scored above 80% in their previous class. Other students will need to take a basic entrance evaluation.', 'entrance,test,exam for admission'),
        ('Refund Policy', 'rules', 'Registration fees are non-refundable. Tuition fees can be refunded pro-rata if a student withdraws within the first 15 days of enrollment.', 'refund,cancel,money back'),
        ('Batch Timings', 'timetable', 'We offer both Morning batches (8:00 AM to 12:00 PM) for dropper students and Evening batches (4:00 PM to 8:00 PM) for regular school-going students.', 'morning,evening,timing,schedule'),
        ('Study Materials', 'academic', 'Digital modules, daily practice papers (DPPs), and comprehensive revision notes are provided free of cost to all registered students.', 'books,modules,material,dpp'),
        ('Doubt Clearing Sessions', 'academic', 'Dedicated doubt-clearing sessions are held every Saturday. Students can also book 1-on-1 online slots with our expert teachers.', 'doubt,help,questions'),
        ('Parent-Teacher Meetings', 'general', 'PTMs are conducted monthly to discuss the student\'s progress, test scores, and overall performance.', 'ptm,parents,meeting'),
        ('Test Schedule', 'academic', 'Part-syllabus tests are conducted every 15 days, and full-syllabus mock tests are conducted once a month to track progress.', 'test,exam schedule,mock test'),
        ('Past Results', 'general', 'Our students consistently secure top ranks in competitive exams and board examinations across the country.', 'results,achievements,toppers'),
        ('Holidays', 'rules', 'We observe all major national holidays and provide a standard summer break in June.', 'holiday,vacation,diwali,summer'),
        ('Attendance Policy', 'rules', 'Regular attendance is highly encouraged for optimal results. For continuous absences, our academic counselors will reach out to parents.', 'attendance,absent,leave'),
        ('Dress Code', 'rules', 'For offline events and classes, students are expected to wear decent casual wear. No formal uniforms are required.', 'dress,uniform,wear')
    ]
    for title, cat, content, kw in default_knowledge:
        if not Knowledge.query.filter_by(title=title).first():
            db.session.add(Knowledge(title=title, category=cat, content=content, keywords=kw))

    db.session.commit()
    print("Database successfully created and seeded!")
