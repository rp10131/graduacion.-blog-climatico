# Importar
from flask import Flask, render_template, request, redirect, session
# Conectando a la biblioteca de bases de datos
from flask_sqlalchemy import SQLAlchemy
# Importar datetime
from datetime import datetime
# Secrets es un módulo que generar cadenas difíciles de adivinar
import secrets, random


app = Flask(__name__)

# Conectando SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.token_hex(15)
# Creando una base de datos
db = SQLAlchemy(app)

ADMINISTRADOR = secrets.token_hex(10)
# Contraseña para el administrador
# Lo pongo aquí porque tal vez uno desee ir publicando cosas manualmente

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<User {self.id}>'
    
class Entrada(db.Model):
    # Creación de columnas
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)
    idea = db.Column(db.Text, nullable=True)

    # Relación con usuario
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    autor = db.relationship('User', backref=db.backref('entradas', lazy=True))

    # Salida del objeto y del id
    def __repr__(self):
        return f'<Entrada {self.id}>'

class PromptDiario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, unique=True, nullable=False)
    numero_random = db.Column(db.Integer, nullable=False)
    texto_prompt = db.Column(db.String(300), nullable=False)
    titulo_prompt = db.Column(db.String(100), nullable=False)
    saludito = db.Column(db.String(20), nullable=False) # Feliz __ !

    def __repr__(self):
        return f"<Prompt {self.fecha}: {self.texto_prompt}>"

# Ejecutar la página de contenidos
@app.route('/')
def index():

    mensaje = {
        'lunes' : {'top': '¡Feliz Lunes!', 'Opciones': ['Describe el clima de hoy en tu localidad. Quizás, ¿hace calor, frío, llueve, hay viento?','¿Hay señales de sequía, inundaciones o erosión en tu comunidad?'], 'Titulo': ['¿Cómo es el Clima Hoy?','Sequía, inundaciones y Erosión']},
        'martes' : {'top': '¡Feliz Martes!', 'Opciones': ['¿Qué cambios has notado en las estaciones en los últimos 5-10 años?','Imagina un titular de periódico sobre el clima de tu localidad hoy'], 'Titulo': ['Estaciones del Año en estos Años','Noticia Ficticia del Clima']},
        'miercoles' : {'top': '¡Feliz Miércoles!', 'Opciones': ['¿Qué efectos del cambio climático notas más en tu entorno?','¿Qué esperas que ocurra con el clima en tu localidad en el futuro cercano?'], 'Titulo': ['Cambio Climático Local','El Futuro del Clima']},
        'jueves' : {'top': '¡Feliz Jueves!', 'Opciones': ['¿Cómo se prepara tu comunidad para enfrentar el clima extremo?','¿El clima de esta semana se parece al de años anteriores en la misma época?'], 'Titulo': ['Preparaciones','¿Clima Habitual?']},
        'viernes' : {'top': '¡Feliz Viernes!', 'Opciones': ['Si tuvieras que describir el clima de hoy con una metáfora, ¿cuál sería?','¿Qué medidas locales se están implementando para mitigar los efectos del cambio climático?'], 'Titulo': ['Metáfora','Acciones Tomadas']},
        'sabado' : {'top': '¡Feliz Sábado!', 'Opciones': ['¿Qué tradiciones o costumbres locales se ven afectadas por el clima?','¿Has notado algún fenómeno inusual en el clima hoy? (ej. lluvias fuera de temporada, temperaturas extremas).'], 'Titulo': ['Costumbres Locales Afectadas','Clima Inusual de Hace Poco']},
        'domingo' : {'top': '¡Feliz Domingo!', 'Opciones': ['¿Cómo afecta el clima de hoy tus actividades cotidianas?','¿Has visto cambios en la vegetación o fauna locales relacionados con el clima reciente?'], 'Titulo': ['El Clima y Tus Actividades','Vegetación y Fauna']}
        }
    
    hoy = datetime.now()
    # Obtener el día de la semana (0 = lunes, 6 = domingo)
    dia_semana = hoy.weekday()
    lista = list(mensaje.keys())
    dia_semana = lista[dia_semana]

    # Buscar si ya existe un prompt para hoy
    prompt = PromptDiario.query.filter_by(fecha=hoy.date()).first()
    if not prompt:
        numero = random.randint(0, 1)
        texto = mensaje[dia_semana]['Opciones'][numero]
        titulo = mensaje[dia_semana]['Titulo'][numero]
        
        prompt = PromptDiario(fecha=hoy.date(), numero_random=numero, texto_prompt=texto, titulo_prompt=titulo, saludito=mensaje[dia_semana]['top'])
        db.session.add(prompt)
        db.session.commit()
    
    # Visualización de las entradas de la base de datos
    entradas = Entrada.query.order_by(Entrada.id).all()
    return render_template('index.html', entradas=entradas, prompt=prompt)

@app.route('/login', methods=['GET','POST'])
def login():
        error = ''
        if request.method == 'POST':
            form_login = request.form['username']
            form_password = request.form['password']
            
            #Asignación #4. Aplicar la autorización
            users_db = User.query.all()
            for user in users_db:
                if form_login == user.login and form_password == user.password:
                    session['user_id'] = user.id
                    return redirect('/')
            else:
                error = 'Nombre de usuario o contraseña incorrectos'
                return render_template('login.html', error=error)
        else:
            return render_template('login.html')

@app.route('/logout')
def logout():
    # Eliminar el usuario de la sesión
    session.pop('user_id', None)
    return redirect('/')

@app.route('/register', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        login= request.form['username']
        password = request.form['password']

        user = User.query.filter_by(login=login).first()

        if user:
            error = 'Este nombre de usuario ya existe'
            return render_template('registration.html', error=error)
        
        user = User(login=login, password=password)
        db.session.add(user)
        db.session.commit() 
        
        return redirect('/')
    
    else:    
        return render_template('registration.html')

# Ejecutar la página con la entrada
@app.route('/card/<int:id>')
def card(id):
    entrada = Entrada.query.get(id)

    return render_template('card.html', entrada=entrada)

# Ejecutar la página de creación de entradas
@app.route('/create')
def create():
    if 'user_id' not in session:
        return redirect('/login')  # Redirigir a login si no está autenticado
    
    return render_template('create_card.html')

# El formulario de inscripción
@app.route('/form_create', methods=['GET','POST'])
def form_create():
    
    if request.method == 'POST':
        title =  request.form['title']
        subtitle =  request.form['subtitle']
        text =  request.form['text']
        idea = request.form.get('prompt')

        # Creación de un objeto que se enviará a la base de datos
        user_id = session['user_id']
        card = Entrada(title=title, subtitle=subtitle, text=text, idea=idea, user_id=user_id)

        db.session.add(card)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('create_card.html')

# Página del contenido del usuario
@app.route('/my')
def user_content():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = session['user_id']
    entradas = Entrada.query.order_by(Entrada.id).all()
    entradas = [entrada for entrada in entradas if entrada.autor.id == user]
    user = User.query.filter_by(id=user).first()
    return render_template('my.html',entradas=entradas,user=user,conteo=len(entradas))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", url=request.path), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Crear usuario por defecto si no existe
        if not User.query.first():
            default_user = User(login="Administrador", password=ADMINISTRADOR)
            db.session.add(default_user)
            db.session.commit()
        else:
            default_user = User.query.first()

        # Crear entrada inicial si la base está vacía
        if not Entrada.query.first():
            ejemplo = Entrada(
                title="Bienvenida al Blog Climático",
                subtitle="Entrada por Defecto",
                text="Hola! Gracias por visitar el Blog Climático. Este es un sitio web que proporciona ideas de investigación personal del clima y medio ambiente de la localidad de uno! Cheque las ideas diarias en el Index y publique sus reflexiones!",
                idea="Parte de: Principal",
                user_id=default_user.id
            )
            db.session.add(ejemplo)
            db.session.commit()

    app.run(debug=True)

