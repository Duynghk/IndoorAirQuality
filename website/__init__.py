from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ajsfdkhaskjdhsajk'

    # from .views import views
    from .views import views
    # from .views_SB2 import views

    app.register_blueprint(views,url_prefix='/')
    return app