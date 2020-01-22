
import oapispec as oapi

def test_model_validate_succeedes():

    user_model = oapi.model.Model('User', {
        'user_id': oapi.fields.String,
        'username': oapi.fields.String(required=True),
    })

    result = user_model.validate({
        'user_id': 'yolo',
        'username': 'yolo',
    })

    assert result is None

def test_model_returns_error():

    user_model = oapi.model.Model('User', {
        'user_id': oapi.fields.String,
        'username': oapi.fields.String(required=True),
    })

    result = user_model.validate({
        'user_id': 'yolo'
    })

    assert result == {
        'username': "'username' is a required property"
    }
