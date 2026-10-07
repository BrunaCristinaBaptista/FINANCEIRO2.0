from abc import ABC, abstractmethod
from datetime import date
from typing import Optional
from financeiro.categoria import Categoria
from financeiro.conta import Conta
from financeiro.estabelecimento import Estabelecimento
from financeiro.forma_pagamento import FormaPagamento


class Lancamento(ABC):
    """Classe base abstrata para qualquer movimentação financeira."""

    def __init__(
        self,
        valor: float,
        data: date,
        conta: Conta,
        categoria: Categoria,
        observacao: Optional[str] = None,) -> None:
        if valor <= 0:
            raise ValueError("O valor do lançamento deve ser maior que zero.")

        if not isinstance(data, date):
            raise ValueError("A data deve ser uma instância válida de date.")

        if not isinstance(conta, Conta):
            raise TypeError("O lançamento exige uma instância válida de Conta.")

        if not isinstance(categoria, Categoria):
            raise TypeError("O lançamento exige uma instância válida de Categoria.")

        self.valor = float(valor)
        self.data = data
        self.conta = conta
        self.categoria = categoria
        self.observacao = observacao.strip() if observacao and observacao.strip() else None

        self._processar_saldo()

    @abstractmethod
    def _processar_saldo(self) -> None:
        pass

    @property
    @abstractmethod
    def sinal(self) -> str:
        pass

    @property
    def valor_formatado(self) -> str:
        texto = f"{self.valor:,.2f}"
        texto_br = texto.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{self.sinal} R$ {texto_br}"


class Receita(Lancamento):
    """Representa entrada de recursos operacionais."""

    def __init__(
        self,
        valor: float,
        data: date,
        conta: Conta,
        categoria: Categoria,
        observacao: Optional[str] = None,) -> None:
        super().__init__(
            valor=valor,
            data=data,
            conta=conta,
            categoria=categoria,
            observacao=observacao,
        )

    def _processar_saldo(self) -> None:
        self.conta.creditar(self.valor)

    @property
    def sinal(self) -> str:
        return "+"


class Despesa(Lancamento):
    """Representa saída de recursos operacionais."""

    def __init__(
        self,
        valor: float,
        data: date,
        conta: Conta,
        forma_pagamento: FormaPagamento,
        categoria: Optional[Categoria] = None,
        estabelecimento: Optional[Estabelecimento] = None,
        observacao: Optional[str] = None,) -> None:
        if not isinstance(forma_pagamento, FormaPagamento):
            raise TypeError("Despesa exige uma instância válida de FormaPagamento.")

        forma_pagamento.validar_conta(conta)

        categoria_final = categoria
        if categoria_final is None and estabelecimento is not None:
            categoria_final = estabelecimento.categoria_padrao

        if categoria_final is None:
            raise ValueError(
                "A despesa exige uma categoria ou um estabelecimento com categoria padrão."
            )

        self.forma_pagamento = forma_pagamento
        self.estabelecimento = estabelecimento

        super().__init__(
            valor=valor,
            data=data,
            conta=conta,
            categoria=categoria_final,
            observacao=observacao,
        )

    def _processar_saldo(self) -> None:
        self.conta.debitar(self.valor)

    @property
    def sinal(self) -> str:
        return "-"


class GastoFixo(Despesa):
    """Representa despesas parceladas ou financiamentos contratuais com valor esperado."""

    def __init__(
        self,
        valor_pago: float,
        valor_esperado: float,
        numero_parcela: int,
        total_parcelas: int,
        data: date,
        conta: Conta,
        forma_pagamento: FormaPagamento,
        categoria: Optional[Categoria] = None,
        estabelecimento: Optional[Estabelecimento] = None,
        observacao: Optional[str] = None,) -> None:
        if valor_esperado <= 0:
            raise ValueError("O valor esperado deve ser maior que zero.")
        if numero_parcela <= 0 or total_parcelas <= 0:
            raise ValueError("As parcelas devem ser inteiros positivos.")
        if numero_parcela > total_parcelas:
            raise ValueError("O número da parcela não pode ser maior que o total de parcelas.")

        self.valor_esperado = float(valor_esperado)
        self.numero_parcela = numero_parcela
        self.total_parcelas = total_parcelas

        super().__init__(
            valor=valor_pago,
            data=data,
            conta=conta,
            forma_pagamento=forma_pagamento,
            categoria=categoria,
            estabelecimento=estabelecimento,
            observacao=observacao,
        )

    @property
    def diferenca_encargos(self) -> float:
        """Variação monetária (positivo = encargos/juros, negativo = desconto)."""
        return round(self.valor - self.valor_esperado, 2)

    @property
    def indicador_parcela(self) -> str:
        return f"{self.numero_parcela:02d}/{self.total_parcelas:02d}"


class ContaRecorrente(Despesa):
    """Representa contas de consumo mensal contínuo cujo valor varia a cada fatura."""

    def __init__(
        self,
        valor_pago: float,
        data_vencimento: date,
        mes_competencia: int,
        ano_competencia: int,
        data_pagamento: date,
        conta: Conta,
        forma_pagamento: FormaPagamento,
        categoria: Optional[Categoria] = None,
        estabelecimento: Optional[Estabelecimento] = None,
        observacao: Optional[str] = None,) -> None:
        if not (1 <= mes_competencia <= 12):
            raise ValueError("Mês de competência inválido (deve ser entre 1 e 12).")
        if not isinstance(data_vencimento, date):
            raise ValueError("Data de vencimento inválida.")

        self.data_vencimento = data_vencimento
        self.mes_competencia = mes_competencia
        self.ano_competencia = ano_competencia

        super().__init__(
            valor=valor_pago,
            data=data_pagamento,
            conta=conta,
            forma_pagamento=forma_pagamento,
            categoria=categoria,
            estabelecimento=estabelecimento,
            observacao=observacao,
        )

    @property
    def pago_com_atraso(self) -> bool:
        return self.data > self.data_vencimento

    @property
    def competencia_formatada(self) -> str:
        return f"{self.mes_competencia:02d}/{self.ano_competencia}"


class Investimento(Lancamento):
    """Representa aplicação de capital em títulos/fundos com acompanhamento de rendimento."""

    def __init__(
        self,
        valor_aplicado: float,
        data_aplicacao: date,
        conta: Conta,
        categoria: Categoria,
        produto: str,
        indexador: str = "100% CDI",
        data_vencimento: Optional[date] = None,
        observacao: Optional[str] = None,) -> None:
        if not produto or not produto.strip():
            raise ValueError("O nome do produto de investimento é obrigatório.")

        self.produto = produto.strip()
        self.indexador = indexador.strip()
        self.data_vencimento = data_vencimento
        self.saldo_atualizado = float(valor_aplicado)

        super().__init__(
            valor=valor_aplicado,
            data=data_aplicacao,
            conta=conta,
            categoria=categoria,
            observacao=observacao,
        )

    def _processar_saldo(self) -> None:
        self.conta.debitar(self.valor)

    def atualizar_rendimento(self, novo_saldo: float) -> None:
        if novo_saldo < 0:
            raise ValueError("O saldo atualizado não pode ser negativo.")
        self.saldo_atualizado = float(novo_saldo)

    @property
    def rendimento_total(self) -> float:
        return round(self.saldo_atualizado - self.valor, 2)

    @property
    def rentabilidade_percentual(self) -> float:
        if self.valor == 0:
            return 0.0
        return round((self.rendimento_total / self.valor) * 100, 2)

    @property
    def sinal(self) -> str:
        return "-"