from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email, Length


class RetailForm(FlaskForm):
    sku = StringField('Sku', validators=[DataRequired(), Length(min=-1, max=80, message='You cannot have more than 80 characters')])
    product_name= StringField('Product Name', validators=[Length(min=-1, max=100, message='You cannot have more than 100 characters')])
    price = StringField('Price', validators=[Length(min=-1, max=50, message='You cannot have more than 200 characters')])
    date = StringField('Date', validators=[Length(min=-1, max=20, message='You cannot have more than 20 characters')])
