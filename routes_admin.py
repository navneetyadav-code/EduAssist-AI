import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from models import Admin, Knowledge, Subject, Setting

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def require_admin():
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))
    return None

@admin_bp.before_request
def before_request():
    if request.endpoint and request.endpoint != 'admin.login' and 'static' not in request.endpoint:
        return require_admin()

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if 'admin_id' in session:
            return redirect(url_for('admin.index'))
        
        error = None
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            admin_user = Admin.query.filter_by(username=username).first()
            
            if admin_user and check_password_hash(admin_user.password_hash, password):
                session.clear()
                session['admin_id'] = admin_user.id
                session['admin_username'] = admin_user.username
                return redirect(url_for('admin.index'))
                
            error = 'Invalid username or password.'
            
        return render_template('admin/login.html', error=error)
    except Exception as e:
        import traceback
        return f"<h1>Login Error!</h1><pre>{traceback.format_exc()}</pre>", 500

@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))

@admin_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'knowledge_save':
            kid = request.form.get('id', type=int)
            title = request.form.get('title', '').strip()
            cat = request.form.get('category', 'general').strip()
            content = request.form.get('content', '').strip()
            keywords = request.form.get('keywords', '').strip()
            
            if title and content:
                if kid:
                    k = db.session.get(Knowledge, kid)
                    if k:
                        k.title = title
                        k.category = cat
                        k.content = content
                        k.keywords = keywords
                else:
                    k = Knowledge(title=title, category=cat, content=content, keywords=keywords)
                    db.session.add(k)
                db.session.commit()
                flash('Knowledge base article saved.', 'success')
                
        elif action == 'knowledge_delete':
            kid = request.form.get('id', type=int)
            k = db.session.get(Knowledge, kid)
            if k:
                db.session.delete(k)
                db.session.commit()
                flash('Article deleted.', 'success')
                
        elif action == 'subject_save':
            sid = request.form.get('id', type=int)
            name = request.form.get('name', '').strip()
            class_level = request.form.get('class_level', '').strip()
            desc = request.form.get('description', '').strip()
            
            if name:
                if sid:
                    s = db.session.get(Subject, sid)
                    if s:
                        s.name = name
                        s.class_level = class_level
                        s.description = desc
                else:
                    s = Subject(name=name, class_level=class_level, description=desc)
                    db.session.add(s)
                db.session.commit()
                flash('Subject saved.', 'success')
                
        elif action == 'subject_delete':
            sid = request.form.get('id', type=int)
            s = db.session.get(Subject, sid)
            if s:
                db.session.delete(s)
                db.session.commit()
                flash('Subject deleted.', 'success')
                
        elif action == 'setting_save':
            key = request.form.get('key', '')
            val = request.form.get('value', '').strip()
            if key:
                s = db.session.get(Setting, key)
                if s:
                    s.setting_value = val
                else:
                    s = Setting(setting_key=key, setting_value=val)
                    db.session.add(s)
                db.session.commit()
                flash(f'Setting "{key}" updated.', 'success')
                
        elif action == 'password_save':
            old_pass = request.form.get('old_password', '')
            new_pass = request.form.get('new_password', '')
            admin_user = db.session.get(Admin, session["admin_id"])
            if admin_user and check_password_hash(admin_user.password_hash, old_pass):
                admin_user.password_hash = generate_password_hash(new_pass)
                db.session.commit()
                flash('Password changed successfully.', 'success')
            else:
                flash('Incorrect current password.', 'error')
                
        tab_redirect = request.args.get('tab', 'chats')
        return redirect(url_for('admin.index', tab=tab_redirect))

    # GET request data
    tab = request.args.get('tab', 'chats')
    
    chats = []
    knowledge = []
    subjects = []
    settings = []
    
    if tab == 'chats':
        from models import Chat
        chats = Chat.query.order_by(Chat.id.desc()).limit(200).all()
    elif tab == 'knowledge':
        knowledge = Knowledge.query.order_by(Knowledge.updated_at.desc()).all()
    elif tab == 'subjects':
        subjects = Subject.query.order_by(Subject.name).all()
    elif tab == 'settings':
        settings = Setting.query.order_by(Setting.setting_key).all()
    
    edit_id = request.args.get('edit', type=int)
    edit_knowledge = db.session.get(Knowledge, edit_id) if edit_id else None

    return render_template('admin/index.html', 
                           tab=tab,
                           chats=chats,
                           knowledge=knowledge, 
                           subjects=subjects, 
                           settings=settings, 
                           edit=edit_knowledge)
