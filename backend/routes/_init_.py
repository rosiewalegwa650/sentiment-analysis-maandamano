def register_routes(app):
    from .collect import collect_bp
    from .dashboard import dashboard_bp

    app.register_blueprint(collect_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
