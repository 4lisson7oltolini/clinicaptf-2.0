"""
Validações puras (sem dependência de banco ou UI) — fáceis de testar com pytest.
"""


def validar_cpf(cpf: str) -> bool:
    """Valida CPF pelo algoritmo oficial de dígitos verificadores."""
    cpf = "".join(filter(str.isdigit, cpf))

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(0, i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf[i]):
            return False

    return True


def validar_cep(cep: str) -> bool:
    """Valida formato de CEP brasileiro (8 dígitos numéricos)."""
    cep = "".join(filter(str.isdigit, cep))
    return len(cep) == 8


def formatar_cpf(cpf: str) -> str:
    cpf = "".join(filter(str.isdigit, cpf))
    return f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}" if len(cpf) == 11 else cpf