from typing import List
from financeiro.lancamento import (
    ContaRecorrente,
    Despesa,
    GastoFixo,
    Investimento,
    Lancamento,
    Receita,
)


class Fechamento:
    """Consolida as movimentações financeiras de um mês e ano específicos."""

    def __init__(self, mes: int, ano: int) -> None:
        if not (1 <= mes <= 12):
            raise ValueError("O mês do fechamento deve estar entre 1 e 12.")
        if ano < 2000:
            raise ValueError("O ano do fechamento deve ser igual ou superior a 2000.")

        self.mes = mes
        self.ano = ano
        self._lancamentos: List[Lancamento] = []

    def adicionar_lancamento(self, lancamento: Lancamento) -> None:
        if not isinstance(lancamento, Lancamento):
            raise TypeError("O item adicionado deve ser uma instância válida de Lancamento.")

        if lancamento.data.month != self.mes or lancamento.data.year != self.ano:
            periodo_lanc = f"{lancamento.data.month:02d}/{lancamento.data.year}"
            periodo_fech = f"{self.mes:02d}/{self.ano}"
            raise ValueError(
                f"Data incompatível: lançamento de {periodo_lanc} não pertence ao fechamento {periodo_fech}."
            )

        self._lancamentos.append(lancamento)

    @property
    def total_receitas(self) -> float:
        return sum(l.valor for l in self._lancamentos if isinstance(l, Receita))

    @property
    def total_despesas(self) -> float:
        return sum(l.valor for l in self._lancamentos if isinstance(l, Despesa))

    @property
    def total_investimentos_aportados(self) -> float:
        return sum(l.valor for l in self._lancamentos if isinstance(l, Investimento))

    @property
    def patrimonio_investido_total(self) -> float:
        return sum(l.saldo_atualizado for l in self._lancamentos if isinstance(l, Investimento))

    @property
    def rendimento_total_acumulado(self) -> float:
        return round(self.patrimonio_investido_total - self.total_investimentos_aportados, 2)

    @property
    def resultado_liquido(self) -> float:
        return self.total_receitas - self.total_despesas

    @property
    def taxa_poupanca_percentual(self) -> float:
        if self.total_receitas <= 0:
            return 0.0
        return round((self.resultado_liquido / self.total_receitas) * 100, 2)

    @property
    def gastos_fixos(self) -> List[GastoFixo]:
        return [l for l in self._lancamentos if isinstance(l, GastoFixo)]

    @property
    def total_encargos_gastos_fixos(self) -> float:
        return round(sum(g.diferenca_encargos for g in self.gastos_fixos), 2)

    @property
    def contas_recorrentes(self) -> List[ContaRecorrente]:
        return [l for l in self._lancamentos if isinstance(l, ContaRecorrente)]

    @property
    def total_contas_atrasadas(self) -> int:
        return sum(1 for c in self.contas_recorrentes if c.pago_com_atraso)

    @property
    def investimentos(self) -> List[Investimento]:
        return [l for l in self._lancamentos if isinstance(l, Investimento)]

    def _formatar_moeda(self, valor: float) -> str:
        sinal = "-" if valor < 0 else ""
        valor_abs = abs(valor)
        texto = f"{valor_abs:,.2f}"
        texto_br = texto.replace(",", "X").replace(".", ",").replace("X", ".")
        prefixo = f"{sinal} R$ " if sinal else "R$ "
        return f"{prefixo}{texto_br}"

    @property
    def total_receitas_formatado(self) -> str:
        return self._formatar_moeda(self.total_receitas)

    @property
    def total_despesas_formatado(self) -> str:
        return self._formatar_moeda(self.total_despesas)

    @property
    def resultado_liquido_formatado(self) -> str:
        return self._formatar_moeda(self.resultado_liquido)