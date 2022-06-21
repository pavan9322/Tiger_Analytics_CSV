from flask import Flask, redirect, url_for, render_template, request, flash, jsonify
from src.models import db
from src.forms import RetailForm
from src import retail_csv_services
from io import TextIOWrapper
import csv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect

# Flask
app = Flask(__name__)
app.config['DEBUG'] = True
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test11.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)
db = SQLAlchemy(app)
app.secret_key = "Dev Testing"


class Serializer(object):
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


class Retail(db.Model, Serializer):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sku = db.Column(db.String(80), nullable=False)
    product_name = db.Column(db.String(100), nullable=True)
    price = db.Column(db.String(200), nullable=True, unique=False)
    date = db.Column(db.String(20), nullable=True, unique=False)

    def __repr__(self):
        return '<Retail %r>' % self.product_name


@app.route("/products")
def retail():
    '''
    Show alls records
    '''
    records = Retail.query.order_by(Retail.id).all()
    # records = db.session.query(Retail.id, Retail.sku,
    #                            Retail.product_name, Retail.price,
    #                            Retail.date).distinct().all()
    print("Records:", records)
    return render_template('web/products.html', records=records)


@app.route('/', methods=['GET', 'POST'])
def upload_csv():
    status = False
    if request.method == 'POST':
        csv_file = request.files['file']
        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            status = True
            print(row[0], row[1], row[2], row[3])
            user = Retail(sku=row[0], product_name=row[1], price=row[2], date=row[3])
            db.session.add(user)
            db.session.commit()
        if status:
            flash('Your file was successfully uploaded', 'success')
        else:
            flash("No file to upload", "danger")
        return redirect(url_for('upload_csv'))
    return render_template('web/csv_upload.html')


@app.route("/search")
def search():
    '''
    Search
    '''
    name_search = request.args.get('name')
    key, val = name_search.split(":")[0], name_search.split(":")[1]
    column_dict = {"sku":Retail.sku,
                   "id":Retail.id,
                   "product":Retail.product_name,
                   "price":Retail.price,
                   "date": Retail.date}
    all_records = Retail.query\
        .filter(column_dict[key].contains(val)
        ).distinct().all()
    return render_template('web/products.html', records=all_records)


@app.route("/product/delete", methods=('POST',))
def product_delete():
    '''
    Delete record
    '''
    try:
        mi_contacto = Retail.query.filter_by(id=request.form['id']).first()
        db.session.delete(mi_contacto)
        db.session.commit()
        flash('Delete successfully.', 'danger')
    except:
        db.session.rollback()
        flash('Error delete  record.', 'danger')
    return redirect(url_for('retail'))


@app.route("/edit_product/<id>", methods=('GET', 'POST'))
def edit_product(id):
    '''
    Edit contact
    :param id: Id from Retail
    '''
    prod = Retail.query.filter_by(id=id).first()
    form = RetailForm(obj=prod)
    if form.validate_on_submit():
        try:
            form.populate_obj(prod)
            db.session.add(prod)
            db.session.commit()
            flash('Saved successfully', 'success')
        except:
            db.session.rollback()
            flash('Error update record.', 'danger')
    return render_template(
        'web/edit_product.html',
        form=form)


@app.route("/new_product", methods=('GET', 'POST'))
def new_product():
    '''
    Create new product
    '''
    form = RetailForm()
    if form.validate_on_submit():
        record = Retail()
        form.populate_obj(record)
        db.session.add(record)
        try:
            db.session.commit()
            flash('Product created successfully', 'success')
            return redirect(url_for('retail'))
        except:
            db.session.rollback()
            flash('Error generating record.', 'danger')

    return render_template('web/new_product.html', form=form)


@app.route("/api/", methods=('GET', 'POST'))
def get_api_list():
    return {"All Products": "http://127.0.0.1:8888/api/all/",
            "Filter_By_name":"http://127.0.0.1:8888/api/name/<name>/",
            "Filter_By id": "http://127.0.0.1:8888/api/id/<id>/",
            "Filter_By Price":"http://127.0.0.1:8888/api/price/<price>/"
            }


@app.route("/api/all/", endpoint='all', methods=['GET'])
@app.route("/api/price/<string:price>", methods=['GET'])
@app.route("/api/id/<int:id>/", methods=['GET'])
@app.route("/api/name/<string:name>", methods=['GET'])
def fetch_data(price=None, id=None, name=None):
    if request.endpoint == 'all':
        return retail_csv_services.get_all_user()
    if id is not None:
        return retail_csv_services.get_user_by_id(id)
    if name is not None:
        return retail_csv_services.get_user_by_name(name)
    if price is not None:
        return retail_csv_services.get_user_by_price(price)




if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", port="8888")