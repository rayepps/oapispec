
import swaggerf as swag


def test_doc_adds_function_name():

    @swag.doc.doc(params={})
    class handler():
        pass

    assert hasattr(handler, '__apidoc__')
    assert handler.__apidoc__['name'] == 'handler'

def test_doc_decorator():

    params = {'q': {'description': 'some description'}}

    @swag.doc.doc(params=params)
    class handler():
        pass

    assert hasattr(handler, '__apidoc__')
    assert handler.__apidoc__ == {'name': 'handler', 'params': params}
