"""
Validações utilizadas pela aplicação.

Este módulo centraliza regras de validação de dados
para evitar duplicação de lógica entre as páginas
e os serviços da aplicação.
"""
import re
# ---------------------------------------------------------
# CPF
# ---------------------------------------------------------

def limpar_cpf(cpf: str) -> str:
    """
    Remove pontos, traços e outros caracteres do CPF.

    Exemplo:
        529.982.247-25
        -> 52998224725
    """

    return re.sub(
        r"\D",
        "",
        cpf or "",
    )


def validar_cpf(cpf: str) -> bool:
    """
    Valida estruturalmente um CPF.

    Verifica:
    - quantidade de dígitos;
    - CPFs com todos os números iguais;
    - primeiro dígito verificador;
    - segundo dígito verificador.
    """

    cpf = limpar_cpf(cpf)

    # -----------------------------------------------------
    # Quantidade de dígitos
    # -----------------------------------------------------

    if len(cpf) != 11:
        return False


    # -----------------------------------------------------
    # Impedir números repetidos
    # -----------------------------------------------------

    if cpf == cpf[0] * 11:
        return False


    # -----------------------------------------------------
    # Primeiro dígito verificador
    # -----------------------------------------------------

    soma = sum(
        int(cpf[i]) * (10 - i)
        for i in range(9)
    )

    resto = soma % 11

    primeiro_digito = (
        0
        if resto < 2
        else 11 - resto
    )

    if primeiro_digito != int(cpf[9]):
        return False


    # -----------------------------------------------------
    # Segundo dígito verificador
    # -----------------------------------------------------

    soma = sum(
        int(cpf[i]) * (11 - i)
        for i in range(10)
    )

    resto = soma % 11

    segundo_digito = (
        0
        if resto < 2
        else 11 - resto
    )

    if segundo_digito != int(cpf[10]):
        return False


    return True


def formatar_cpf(cpf: str) -> str:
    """
    Formata um CPF no padrão:

        529.982.247-25
    """

    cpf = limpar_cpf(cpf)

    if len(cpf) != 11:
        return cpf

    return (
        f"{cpf[:3]}."
        f"{cpf[3:6]}."
        f"{cpf[6:9]}-"
        f"{cpf[9:]}"
    )


# ---------------------------------------------------------
# CEP
# ---------------------------------------------------------

def limpar_cep(cep: str) -> str:
    """
    Remove caracteres não numéricos do CEP.
    """

    return re.sub(
        r"\D",
        "",
        cep or "",
    )


def validar_cep(cep: str) -> bool:
    """
    Valida o formato de um CEP brasileiro.

    Aceita:

        88330-000
        88330000
    """

    cep = limpar_cep(cep)

    return len(cep) == 8


def formatar_cep(cep: str) -> str:
    """
    Formata um CEP no padrão:

        88330-000
    """

    cep = limpar_cep(cep)

    if len(cep) != 8:
        return cep

    return f"{cep[:5]}-{cep[5:]}"


# ---------------------------------------------------------
# Telefone
# ---------------------------------------------------------

def limpar_telefone(telefone: str) -> str:
    """
    Remove caracteres não numéricos do telefone.
    """

    return re.sub(
        r"\D",
        "",
        telefone or "",
    )


def validar_telefone(telefone: str) -> bool:
    """
    Valida telefone brasileiro.

    Aceita números com:
    - 10 dígitos: telefone fixo;
    - 11 dígitos: telefone celular.
    """

    telefone = limpar_telefone(
        telefone
    )

    return len(telefone) in {
        10,
        11,
    }


def formatar_telefone(telefone: str) -> str:
    """
    Formata telefones brasileiros.

    Exemplos:

        4733334444
        -> (47) 3333-4444

        47999990000
        -> (47) 99999-0000
    """

    telefone = limpar_telefone(
        telefone
    )


    # -----------------------------------------------------
    # Telefone fixo
    # -----------------------------------------------------

    if len(telefone) == 10:

        return (
            f"({telefone[:2]}) "
            f"{telefone[2:6]}-"
            f"{telefone[6:]}"
        )


    # -----------------------------------------------------
    # Telefone celular
    # -----------------------------------------------------

    if len(telefone) == 11:

        return (
            f"({telefone[:2]}) "
            f"{telefone[2:7]}-"
            f"{telefone[7:]}"
        )


    return telefone


# ---------------------------------------------------------
# Nome
# ---------------------------------------------------------

def validar_nome(nome: str) -> bool:
    """
    Valida o nome de uma pessoa.

    Regras:
    - não pode estar vazio;
    - mínimo de 3 caracteres;
    - deve possuir pelo menos duas partes;
    - permite letras, espaços, acentos e hífen.
    """

    nome = (
        nome or ""
    ).strip()

    if len(nome) < 3:
        return False

    partes = nome.split()

    if len(partes) < 2:
        return False

    return bool(
        re.fullmatch(
            r"[A-Za-zÀ-ÖØ-öø-ÿ\s\-]+",
            nome,
        )
    )


# ---------------------------------------------------------
# Texto obrigatório
# ---------------------------------------------------------

def validar_texto_obrigatorio(
    texto: str,
    minimo: int = 1,
) -> bool:
    """
    Verifica se um texto foi preenchido
    e possui a quantidade mínima de caracteres.
    """

    texto = (
        texto or ""
    ).strip()

    return len(texto) >= minimo
