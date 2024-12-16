from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///printfarm.db'
db = SQLAlchemy(app)

class Printer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(100))
    location = db.Column(db.String(100))
    prints = db.relationship('Print', backref='printer', lazy=True)
    maintenance_logs = db.relationship('MaintenanceLog', backref='printer', lazy=True)

class PrintedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    prints = db.relationship('Print', backref='item', lazy=True)

class Print(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    printer_id = db.Column(db.Integer, db.ForeignKey('printer.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('printed_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)

class MaintenanceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    printer_id = db.Column(db.Integer, db.ForeignKey('printer.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/printers', methods=['GET', 'POST'])
def printers():
    if request.method == 'POST':
        name = request.form.get('name')
        model = request.form.get('model')
        location = request.form.get('location')
        
        printer = Printer(name=name, model=model, location=location)
        db.session.add(printer)
        db.session.commit()
        return redirect(url_for('printers'))
    
    printers = Printer.query.all()
    return render_template('printers.html', printers=printers)

@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'POST':
        sku = request.form.get('sku')
        name = request.form.get('name')
        description = request.form.get('description')
        
        item = PrintedItem(sku=sku, name=name, description=description)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('items'))
    
    items = PrintedItem.query.all()
    return render_template('items.html', items=items)

@app.route('/log_print', methods=['GET', 'POST'])
def log_print():
    if request.method == 'POST':
        printer_id = request.form.get('printer_id')
        item_id = request.form.get('item_id')
        quantity = request.form.get('quantity')
        notes = request.form.get('notes')
        
        print_log = Print(printer_id=printer_id, item_id=item_id, 
                         quantity=quantity, notes=notes)
        db.session.add(print_log)
        db.session.commit()
        return redirect(url_for('log_print'))
    
    printers = Printer.query.all()
    items = PrintedItem.query.all()
    recent_prints = Print.query.order_by(Print.timestamp.desc()).limit(10).all()
    return render_template('log_print.html', printers=printers, items=items, 
                         recent_prints=recent_prints)

@app.route('/maintenance', methods=['GET', 'POST'])
def maintenance():
    if request.method == 'POST':
        printer_id = request.form.get('printer_id')
        description = request.form.get('description')
        
        maintenance = MaintenanceLog(printer_id=printer_id, description=description)
        db.session.add(maintenance)
        db.session.commit()
        return redirect(url_for('maintenance'))
    
    printers = Printer.query.all()
    recent_maintenance = MaintenanceLog.query.order_by(
        MaintenanceLog.timestamp.desc()).limit(10).all()
    return render_template('maintenance.html', printers=printers, 
                         recent_maintenance=recent_maintenance)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)