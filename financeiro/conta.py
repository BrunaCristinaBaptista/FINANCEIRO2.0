from abc import ABC, abstractmethod
from typing import Optional


class Conta(ABC):
    def __init__(self, nome: str, saldo_inicial: float = 0.0) -> None:
        if not nome or not nome.strip():
            raise ValueError("O nome da conta não pode ser vazio.")

        self.nome = nome.strip()
        self.saldo_atual = float(saldo_inicial)

    def creditar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("O valor para crédito deve ser maior que zero.")
        self.saldo_atual += float(valor)

    def debitar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("O valor para débito deve ser maior que zero.")
        if valor > self.saldo_atual:
            raise ValueError(
                f"Saldo insuficiente na conta '{self.nome}'. Saldo disponível: {self.saldo_formatado}."
            )
        self.saldo_atual -= float(valor)

    def transferir(self, valor: float, destino: "Conta") -> None:
        if not isinstance(destino, Conta):
            raise TypeError("A conta de destino deve ser uma instância válida de Conta.")
        if destino is self:
            raise ValueError("Não é possível realizar transferências para a mesma conta.")

        self.debitar(valor)
        destino.creditar(valor)

    @property
    @abstractmethod
    def permite_pagamento_eletronico(self) -> bool:
        pass

    @property
    def saldo_formatado(self) -> str:
        texto = f"{self.saldo_atual:,.2f}"
        texto_br = texto.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {texto_br}"


class CarteiraFisica(Conta):
    @property
    def permite_pagamento_eletronico(self) -> bool:
        return False


class ContaBancaria(Conta):
    def __init__(
        self,
        nome: str,
        instituicao: str,
        saldo_inicial: float = 0.0,
        agencia: Optional[str] = None,
        numero_conta: Optional[str] = None,) -> None:
        super().__init__(nome=nome, saldo_inicial=saldo_inicial)

        if not instituicao or not instituicao.strip():
            raise ValueError("A instituição bancária não pode ser vazia.")

        self.instituicao = instituicao.strip()
        self.agencia = agencia.strip() if agencia and agencia.strip() else None
        self.numero_conta = numero_conta.strip() if numero_conta and numero_conta.strip() else None

    @property
    def permite_pagamento_eletronico(self) -> bool:
        return True