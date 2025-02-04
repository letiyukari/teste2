import os
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, request, make_response, abort, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, RadioField, TextAreaField, DateTimeField, DateTimeLocalField
from wtforms.validators import DataRequired, InputRequired 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    semester = db.Column(db.String(64))
    users = db.relationship('User', backref='role', lazy='dynamic')
    students = db.relationship('Student', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username
    
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username
    
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    coursename = db.Column(db.String(64), unique=True, index=True)
    coursedescription = db.Column(db.String(250))

    def __repr__(self):
        return '<Course %r>' % self.coursename    

class NameForm(FlaskForm):
    name = StringField('Cadastre o novo Professor:', validators=[DataRequired()])
    role = SelectField(u'Disciplina associada:', choices=[('DSWA5'), ('GPSA5'), ('IHCA5'), ('SODA5'), ('PJIA5'), ('TCOA5')])
    submit = SubmitField('Cadastrar')

class DisciplineForm(FlaskForm):
    name = StringField('Cadastre a nova disciplina e o semestre associado:', validators=[DataRequired()])
    semester = RadioField('Semestre associado:', choices=[('1º semestre'), ('2º semestre'), ('3º semestre'), ('4º semestre'), ('5º semestre'), ('6º semestre')])
    submit = SubmitField('Cadastrar')

class StudentsForm(FlaskForm):
    name = StringField('Cadastre o novo Aluno:', validators=[DataRequired()])
    role = SelectField(u'Disciplina associada:', choices=[('DSWA5'), ('GPSA5'), ('IHCA5'), ('SODA5'), ('PJIA5'), ('TCOA5')])
    submit = SubmitField('Cadastrar')

class CourseForm(FlaskForm):
    coursename = StringField('Qual é o nome do curso?', validators=[DataRequired()])
    coursedescription = TextAreaField('Descrição (250 caracteres)', validators=[DataRequired()])    
    submit = SubmitField('Cadastrar')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/')
def index():
     return render_template('index.html', current_time=datetime.utcnow())

@app.route('/professores', methods=['GET', 'POST'])
def professores():
    form = NameForm()
    user_all = User.query.all();
    print(user_all);
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()                
        if user is None:
            
            # Cadastrar disciplina
            search_role = Role.query.filter_by(name=form.role.data).first()
            if not (search_role):
                search_role = Role(name=form.role.data, semester="5º semestre")
                db.session.add(search_role)
                db.session.commit()

            #user_role = Role.query.filter_by(name='User').first();

            user = User(username=form.name.data, role=search_role);
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            flash('Professor cadastrado com sucesso!')
        else:
            session['known'] = True
            flash('Professor já existe na base de dados!')
        session['name'] = form.name.data
        return redirect(url_for('professores'))
    return render_template('professores.html', form=form, name=session.get('name'),
                           known=session.get('known', False),
                           user_all=user_all);

@app.route('/disciplinas', methods=['GET', 'POST'])
def disciplinas():
    form = DisciplineForm()
    discipline_all = Role.query.all();
    print(discipline_all, flush=True);
    if form.validate_on_submit():
        role = Role.query.filter_by(name=form.name.data).first()                
        if role is None:
            role = Role(name=form.name.data, semester=form.semester.data);
            db.session.add(role)
            db.session.commit()
            session['known'] = False
            flash('Disciplina cadastrada com sucesso!')
        else:
            flash('Disciplina já existe na base de dados!')
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('disciplinas'))
    return render_template('disciplinas.html', form=form, name=session.get('name'),
                           known=session.get('known', False),
                           discipline_all=discipline_all);

@app.route('/alunos', methods=['GET', 'POST'])
def alunos():
    form = StudentsForm()
    students_all = Student.query.all();
    print(students_all, flush=True);
    if form.validate_on_submit():
        user = Student.query.filter_by(username=form.name.data).first()                
        if user is None:
            
            # Cadastrar disciplina
            search_role = Role.query.filter_by(name=form.role.data).first()
            if not (search_role):
                search_role = Role(name=form.role.data, semester="5º semestre")
                db.session.add(search_role)
                db.session.commit()

            #user_role = Role.query.filter_by(name='User').first();

            user = Student(username=form.name.data, role=search_role);
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            flash('Estudante cadastrado com sucesso!')
        else:
            session['known'] = True
            flash('Estudante já existe na base de dados!')
        session['name'] = form.name.data
        return redirect(url_for('alunos'))
    return render_template('alunos.html', form=form, name=session.get('name'),
                           known=session.get('known', False),
                           students_all=students_all);

@app.route('/cursos', methods=['GET', 'POST'])
def cursos():
    form = CourseForm()
    course_all = Course.query.all();
    print(course_all, flush=True);
    if form.validate_on_submit():
        coursename = Course.query.filter_by(coursename=form.coursename.data).first()                
        if coursename is None:
            course = Course(coursename=form.coursename.data, coursedescription=form.coursedescription.data);
            db.session.add(course)
            db.session.commit()
            session['known'] = False
            flash('Curso cadastrado com sucesso!')
        else:
            flash('Curso já existe na base de dados!')
            session['known'] = True
        session['curso'] = form.coursename.data
        return redirect(url_for('cursos'))
    return render_template('cursos.html', form=form, name=session.get('curso'),
                           known=session.get('known', False),
                           course_all=course_all);

@app.route('/ocorrencias', methods=['GET', 'POST'])
def ocorrencias():
     return render_template('naodisponivel.html', current_time=datetime.utcnow())