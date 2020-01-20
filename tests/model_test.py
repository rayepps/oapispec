
import swaggerf as swag

def test_model_validate_succeedes():

    user_model = swag.model.Model('User', {
        'user_id': swag.fields.String,
        'username': swag.fields.String(required=True),
    })

    result = user_model.validate({
        'user_id': 'yolo',
        'username': 'yolo',
    })

    assert result is None

def test_model_returns_error():

    user_model = swag.model.Model('User', {
        'user_id': swag.fields.String,
        'username': swag.fields.String(required=True),
    })

    result = user_model.validate({
        'user_id': 'yolo'
    })

    assert result == {
        'username': "'username' is a required property"
    }
