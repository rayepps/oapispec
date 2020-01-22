
import oapispec as oapi


def test_doc_adds_function_name():

    @oapi.doc.doc(params={})
    class handler():
        pass

    assert hasattr(handler, '__apidoc__')
    assert handler.__apidoc__['name'] == 'handler'

def test_doc_decorator():

    params = {'q': {'description': 'some description'}}

    @oapi.doc.doc(params=params)
    class handler():
        pass

    assert hasattr(handler, '__apidoc__')
    assert handler.__apidoc__ == {'name': 'handler', 'params': params}
