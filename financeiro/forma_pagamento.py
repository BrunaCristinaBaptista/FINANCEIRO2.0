from abc import ABC, abstractmethod
from financeiro.conta import CarteiraFisica, Conta, ContaBancaria


class FormaPagamento(ABC):
    @property
    @abstractmethod
    def descricao(self) -> str:
        pass

    @abstractmethod
    def validar_conta(self, conta: Conta) -> None:
        pass

    def __eq__(self, outro: object) -> bool:
        if not isinstance(outro, FormaPagamento):
            return False
        return self.__class__ is outro.__class__

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class Dinheiro(FormaPagamento):
    @property
    def descricao(self) -> str:
        return "Dinheiro"

    def validar_conta(self, conta: Conta) -> None:
        if not isinstance(conta, CarteiraFisica):
            raise ValueError(
                f"Pagamentos em dinheiro vivo exigem uma Carteira Física como origem, "
                f"mas foi informada a conta '{conta.nome}'."
            )


class Pix(FormaPagamento):
    @property
    def descricao(self) -> str:
        return "Pix"

    def validar_conta(self, conta: Conta) -> None:
        if not conta.permite_pagamento_eletronico:
            raise ValueError(
                f"A conta '{conta.nome}' não suporta transações via Pix por não ser eletrônica."
            )


class CartaoDebito(FormaPagamento):
    @property
    def descricao(self) -> str:
        return "Cartão de Débito"

    def validar_conta(self, conta: Conta) -> None:
        if not isinstance(conta, ContaBancaria):
            raise ValueError(
                f"Cartão de Débito exige vínculo com Conta Bancária, "
                f"mas foi informada a conta '{conta.nome}'."
            )


class Transferencia(FormaPagamento):
    @property
    def descricao(self) -> str:
        return "Transferência"

    def validar_conta(self, conta: Conta) -> None:
        if not conta.permite_pagamento_eletronico:
            raise ValueError(
                f"A conta '{conta.nome}' não permite transferências eletrônicas bancárias."
            )