from utils.validators import validar_cpf, validar_cep, formatar_cpf


def test_cpf_valido():
    assert validar_cpf("11144477735") is True


def test_cpf_invalido_todos_digitos_iguais():
    assert validar_cpf("11111111111") is False


def test_cpf_invalido_digito_verificador_errado():
    assert validar_cpf("11144477736") is False


def test_cep_valido():
    assert validar_cep("01311000") is True


def test_cep_invalido_tamanho():
    assert validar_cep("123") is False


def test_formatar_cpf():
    assert formatar_cpf("11144477735") == "111.444.777-35"