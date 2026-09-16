

def init_blueprints(app) -> None:

    from data5580_hw.routes.user_routes import user_blueprint
    app.register_blueprint(user_blueprint)
