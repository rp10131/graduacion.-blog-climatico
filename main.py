# Importar
from flask import Flask, render_template, request, redirect
# Conectando a la biblioteca de bases de datos
from flask_sqlalchemy import SQLAlchemy
# Importar datetime
from datetime import datetime


app = Flask(__name__)

# Conectando SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Creando una base de datos
db = SQLAlchemy(app)
# Creación de una tabla

class Entrada(db.Model):
    # Creación de columnas
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)

    # Salida del objeto y del id
    def __repr__(self):
        return f'<Entrada {self.id}>'

#Asignación #2. Crear la tabla Usuario

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<User {self.id}>'

# Ejecutar la página de contenidos
@app.route('/')
def index():
    # Visualización de las entradas de la base de datos
    entradas = Entrada.query.order_by(Entrada.id).all()
    return render_template('index.html', entradas=entradas)

@app.route('/log', methods=['GET','POST'])
def login():
        error = ''
        if request.method == 'POST':
            form_login = request.form['email']
            form_password = request.form['password']
            
            #Asignación #4. Aplicar la autorización
            users_db = User.query.all()
            for user in users_db:
                if form_login == user.login and form_password == user.password:
                    return redirect('/index')
            else:
                error = 'Nombre de usuario o contraseña incorrectos'
                return render_template('login.html', error=error)

            
        else:
            return render_template('login.html')



@app.route('/reg', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        login= request.form['username']
        password = request.form['password']

        
        #Asignación #3. Hacer que los datos del usuario se registren en la base de datos.
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
    return render_template('create_card.html')

# El formulario de inscripción
@app.route('/form_create', methods=['GET','POST'])
def form_create():
    if request.method == 'POST':
        title =  request.form['title']
        subtitle =  request.form['subtitle']
        text =  request.form['text']

        # Creación de un objeto que se enviará a la base de datos
        card = Entrada(title=title, subtitle=subtitle, text=text)

        db.session.add(card)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('create_card.html')




@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", url=request.path), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Crear entrada inicial si la base está vacía
        if not Entrada.query.first():
            ejemplo = Entrada(
                title="Bienvenida al Blog Climático",
                subtitle="Prueba de Entrada",
                text="Este es tu primer post automático 🌍✨"
            )
            db.session.add(ejemplo)
            db.session.commit()
    app.run(debug=True)
