from utils.validators import (
    limpar_cpf,
    validar_cpf,
    formatar_cpf,
    limpar_cep,
    validar_cep,
    formatar_cep,
    limpar_telefone,
    validar_telefone,
    formatar_telefone,
    validar_nome,
    validar_texto_obrigatorio,
)

# =========================================================
# CPF
# =========================================================

def test_limpar_cpf():
    assert limpar_cpf(
        "529.982.247-25"
    ) == "52998224725"


def test_validar_cpf_valido():
    assert validar_cpf(
        "529.982.247-25"
    ) is True


def test_validar_cpf_sem_formatacao():
    assert validar_cpf(
        "52998224725"
    ) is True


def test_validar_cpf_invalido():
    assert validar_cpf(
        "529.982.247-26"
    ) is False


def test_validar_cpf_com_tamanho_invalido():
    assert validar_cpf(
        "123456789"
    ) is False


def test_validar_cpf_com_numeros_repetidos():
    assert validar_cpf(
        "111.111.111-11"
    ) is False


def test_formatar_cpf():
    assert formatar_cpf(
        "52998224725"
    ) == "529.982.247-25"


# =========================================================
# CEP
# =========================================================

def test_limpar_cep():
    assert limpar_cep(
        "88330-000"
    ) == "88330000"


def test_validar_cep_valido():
    assert validar_cep(
        "88330-000"
    ) is True


def test_validar_cep_sem_formatacao():
    assert validar_cep(
        "88330000"
    ) is True


def test_validar_cep_invalido():
    assert validar_cep(
        "88330"
    ) is False


def test_formatar_cep():
    assert formatar_cep(
        "88330000"
    ) == "88330-000"


# =========================================================
# Telefone
# =========================================================

def test_limpar_telefone():
    assert limpar_telefone(
        "(47) 99999-0000"
    ) == "47999990000"


def test_validar_telefone_celular():
    assert validar_telefone(
        "(47) 99999-0000"
    ) is True


def test_validar_telefone_fixo():
    assert validar_telefone(
        "(47) 3333-4444"
    ) is True


def test_validar_telefone_invalido():
    assert validar_telefone(
        "99999"
    ) is False


def test_formatar_telefone_celular():
    assert formatar_telefone(
        "47999990000"
    ) == "(47) 99999-0000"


def test_formatar_telefone_fixo():
    assert formatar_telefone(
        "4733334444"
    ) == "(47) 3333-4444"


# =========================================================
# Nome
# =========================================================

def test_validar_nome_completo():
    assert validar_nome(
        "Maria da Silva"
    ) is True


def test_validar_nome_com_apenas_um_nome():
    assert validar_nome(
        "Maria"
    ) is False


def test_validar_nome_vazio():
    assert validar_nome(
        ""
    ) is False


def test_validar_nome_com_numeros():
    assert validar_nome(
        "Maria 123"
    ) is False


def test_validar_nome_com_acento():
    assert validar_nome(
        "João da Silva"
    ) is True


# =========================================================
# Texto obrigatório
# =========================================================

def test_validar_texto_obrigatorio():
    assert validar_texto_obrigatorio(
        "Paciente"
    ) is True


def test_validar_texto_obrigatorio_vazio():
    assert validar_texto_obrigatorio(
        ""
    ) is False


def test_validar_texto_obrigatorio_com_minimo():
    assert validar_texto_obrigatorio(
        "ABC",
        minimo=3,
    ) is True


def test_validar_texto_obrigatorio_abaixo_do_minimo():
    assert validar_texto_obrigatorio(
        "AB",
        minimo=3,
    ) is False
