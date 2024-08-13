from myapp import create_app

app = create_app()

def list_routes(app):
    print("Available routes:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        print(f"{rule.endpoint:50s} {methods:20s} {rule}")

# Run the server and display routes
if __name__ == '__main__':
    list_routes(app)
    app.run(debug=True)

