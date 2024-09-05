import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://Leonel:Leonel@PC-DEV14/Gestion_Inventario_Vehiculos?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Vehiculo(db.Model):
    __tablename__ = 'Vehiculos'
    ID_Vehiculo = db.Column(db.Integer, primary_key=True)
    Marca = db.Column(db.String(50), nullable=False)
    Modelo = db.Column(db.String(50), nullable=False)
    Año = db.Column(db.Integer, nullable=False)
    Precio = db.Column(db.Float, nullable=False)
    Disponibilidad = db.Column(db.Boolean, default=True, nullable=False)
    ventas = db.relationship('Venta', backref='vehiculo', lazy=True)

class Cliente(db.Model):
    __tablename__ = 'Clientes'
    ID_Cliente = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100), nullable=False)
    NumeroIdentificacion = db.Column(db.String(50), unique=True, nullable=False)
    Correo = db.Column(db.String(100), unique=True, nullable=False)
    Telefono = db.Column(db.String(20), nullable=False)
    ventas = db.relationship('Venta', backref='cliente', lazy=True)

class Venta(db.Model):
    __tablename__ = 'Ventas'
    ID_Venta = db.Column(db.Integer, primary_key=True)
    ID_Vehiculo = db.Column(db.Integer, db.ForeignKey('Vehiculos.ID_Vehiculo'), nullable=False)
    ID_Cliente = db.Column(db.Integer, db.ForeignKey('Clientes.ID_Cliente'), nullable=False)
    Fecha_venta = db.Column(db.DateTime, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

# Leer todos los vehículos
@app.route("/vehiculos/lista")
def listar_vehiculos():
    vehiculos = Vehiculo.query.all()
    return render_template('ListaVehiculos.html', vehiculos=vehiculos)

@app.route('/vehiculos', methods=['GET', 'POST'])
def crear_vehiculo():
    if request.method == 'POST':
        # Crear nuevo vehículo
        new_vehiculo = Vehiculo(
            Marca=request.form['Marca'],
            Modelo=request.form['Modelo'],
            Año=request.form['Año'],
            Precio=request.form['Precio'],
            Disponibilidad=True
        )
        db.session.add(new_vehiculo)
        db.session.commit()
        return redirect(url_for('listar_vehiculos'))
    
    vehiculos = Vehiculo.query.all()
    return render_template('Vehiculos.html', vehiculos=vehiculos)


@app.route('/clientes', methods=['GET', 'POST'])
def manage_clientes():
    if request.method == 'POST':
        # Crear nuevo cliente
        new_cliente = Cliente(
            Nombre=request.form['Nombre'],
            NumeroIdentificacion=request.form['NumeroIdentificacion'],
            Correo=request.form['Correo'],
            Telefono=request.form['Telefono']
        )
        db.session.add(new_cliente)
        db.session.commit()
        return redirect(url_for('manage_clientes'))
    
    # Leer todos los clientes
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

@app.route('/ventas', methods=['GET', 'POST'])
def manage_ventas():
    if request.method == 'POST':
        vehiculo_id = request.form['ID_Vehiculo']
        cliente_id = request.form['ID_Cliente']
        vehiculo = Vehiculo.query.get(vehiculo_id)
        if vehiculo and vehiculo.Disponibilidad:
            new_venta = Venta(
                ID_Vehiculo=vehiculo_id,
                ID_Cliente=cliente_id,
                Fecha_venta=datetime.now()
            )
            vehiculo.Disponibilidad = False
            db.session.add(new_venta)
            db.session.commit()
        return redirect(url_for('manage_ventas'))
    vehiculos = Vehiculo.query.filter_by(Disponibilidad=True).all()
    clientes = Cliente.query.all()

    # Leer todas las ventas
    ventas = Venta.query.all()
    return render_template('Ventas.html', vehiculos=vehiculos, clientes = clientes)


if __name__ == '__main__':
    app.run(debug=True)