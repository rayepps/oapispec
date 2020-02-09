import os


def generate_swagger_ui(
    spec_url,
    title='Swagger UI',
    asset_source='https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.25.0'):

    ui_template = load_ui_template()

    config = {
        'title': title,
        'asset_source': asset_source,
        'spec_url': spec_url
    }

    for key, value in config.items():
        ui_template = ui_template.replace('{{%s}}' % key, value)

    return ui_template

def load_ui_template():
    rel_path = '../templates/swagger-ui.html'
    path = os.path.join(os.path.dirname(__file__), rel_path)
    with open(path) as f:
        return f.read()
