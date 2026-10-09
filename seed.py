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
        ('About Institute', 'general', 'EduAssist AI is a premier educational institute dedicated to providing top-quality coaching for students from classes 9 to 12. We focus on conceptual clarity and board/competitive exam preparation.', 'about,institute,who are you'),
        ('Developer Information', 'general', 'This AI Chatbot was proudly developed by Navneet Kumar Yadav, a B.Tech CSE (First Year) student. It uses a modern Decoupled Architecture and Retrieval-Augmented Generation (RAG) to assist students.', 'developer,who made this,creator,navneet,yadav'),
        ('Contact Number', 'contact', 'You can reach the administration desk at +91-9876543210 for any inquiries between 9 AM and 6 PM.', 'phone,number,contact,call'),
        ('Address', 'contact', 'EduAssist AI is located at [Insert Full Address Here]. We are easily accessible by public transport.', 'address,location,where,map'),
        ('Email Address', 'contact', 'For official queries, you can email us at contact@eduassistai.com', 'email,mail,id'),
        ('Courses Offered', 'academic', 'We offer coaching for Classes 9 and 10 (All Subjects) and Classes 11 and 12 (Science Stream: PCM & PCB). We also prepare students for JEE and NEET.', 'courses,classes,what do you teach'),
        ('Fee Structure (Class 9 & 10)', 'fees', 'The annual fee for Class 9 and 10 is Rs. [Insert Amount] covering all core subjects. Fees can be paid in 3 installments.', 'fees class 9,fees class 10,cost'),
        ('Fee Structure (Class 11 & 12 PCM)', 'fees', 'The annual fee for Class 11 and 12 (Physics, Chemistry, Math) is Rs. [Insert Amount].', 'fees class 11,fees class 12,pcm fees'),
        ('Fee Structure (Class 11 & 12 PCB)', 'fees', 'The annual fee for Class 11 and 12 (Physics, Chemistry, Biology) is Rs. [Insert Amount].', 'pcb fees,biology fees'),
        ('Scholarship Programs', 'admission', 'We offer up to 100% scholarships based on our Annual Talent Search Examination (ATSE) held in March every year.', 'scholarship,discount,free'),
        ('Admission Process', 'admission', 'To take admission, students must visit the branch, fill out the physical application form, submit 2 passport photos, and pay the registration fee of Rs. 1000.', 'admission,apply,join,register'),
        ('Entrance Test', 'admission', 'Direct admission is available for students who scored above 80% in their previous class. Others must take a basic entrance test.', 'entrance,test,exam for admission'),
        ('Refund Policy', 'rules', 'Registration fees are strictly non-refundable. Tuition fees can be refunded pro-rata if a student withdraws within the first 15 days of batch commencement.', 'refund,cancel,money back'),
        ('Morning Batch Timings', 'timetable', 'Morning batches run from 8:00 AM to 12:00 PM and are designed for dropper students.', 'morning,timing'),
        ('Evening Batch Timings', 'timetable', 'Evening batches are for regular school-going students and run from 4:00 PM to 8:00 PM.', 'evening,timing'),
        ('Study Materials', 'academic', 'Printed modules, daily practice papers (DPPs), and revision notes are provided free of cost to all registered students.', 'books,modules,material,dpp'),
        ('Doubt Clearing Sessions', 'academic', 'Special doubt-clearing counters are open every Saturday from 2 PM to 5 PM. Students can book a 1-on-1 slot with teachers.', 'doubt,help,questions'),
        ('Parent-Teacher Meetings', 'general', 'PTMs are conducted on the second Sunday of every month to discuss the student\'s progress, test scores, and attendance.', 'ptm,parents,meeting'),
        ('Test Schedule', 'academic', 'Part-syllabus tests are conducted every 15 days (Sunday), and full-syllabus mock tests are conducted once a month.', 'test,exam schedule,mock test'),
        ('Hostel / PG Facilities', 'facilities', 'We do not have an in-house hostel, but we have partnered with highly secure and hygienic PGs nearby. Contact the front desk for the PG list.', 'hostel,pg,stay,accommodation'),
        ('Transportation / Bus', 'facilities', 'Institute bus facility is available for selected routes within a 10 km radius. Transport fees are charged separately.', 'bus,transport,van'),
        ('Past Results', 'general', 'Last year, over 50 of our students cleared JEE Mains, and 20 cleared NEET with top ranks. We consistently produce district toppers in board exams.', 'results,achievements,toppers'),
        ('Vacation / Holidays', 'rules', 'The institute remains closed on all national holidays and during the Diwali week. A 15-day summer break is given in June.', 'holiday,vacation,diwali,summer'),
        ('Attendance Policy', 'rules', '75% attendance is compulsory. If a student is absent for 3 consecutive days without prior notice, parents will be called.', 'attendance,absent,leave'),
        ('Dress Code', 'rules', 'Students must wear the EduAssist AI ID card at all times. Decent casual wear is allowed; no uniforms are required.', 'dress,uniform,wear')
    ]
    for title, cat, content, kw in default_knowledge:
        if not Knowledge.query.filter_by(title=title).first():
            db.session.add(Knowledge(title=title, category=cat, content=content, keywords=kw))

    db.session.commit()
    print("Database successfully created and seeded!")
