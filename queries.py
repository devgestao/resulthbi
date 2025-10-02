VENDAS_QUERY = """select
  w.TEXTO_FILIAL,
  round(w.VALOR_TOTALVENDAS, 2) as VALOR_TOTALVENDAS,
  w.DATA_DATAINICIAL,
  w.DATA_DATAFINAL,
  w.TEXTO_QUANTIDADEVENDAS - w.TEXTO_QUANTTRANSFERENCIA as TEXTO_QUANTIDADEVENDAS,
  w.VALOR_TRANSFERENCIA,
  w.TEXTO_QUANTTRANSFERENCIA,
  round(w.VALOR_TOTALVENDAS - w.VALOR_TRANSFERENCIA, 2) as VALOR_VENDASFILIAL,
  round((w.VALOR_TOTALVENDAS - w.VALOR_TRANSFERENCIA) / (w.TEXTO_QUANTIDADEVENDAS - w.TEXTO_QUANTTRANSFERENCIA),2) as VALOR_TICKETMEDIO,
  round(w.VALOR_VENDADINHEIRO, 2) as VALOR_VENDADINHEIRO,
  round(w.VALOR_VENDACHEQUE, 2) as VALOR_VENDACHEQUE,
  round(w.VALOR_VENDARECEBER, 2) as VALOR_VENDARECEBER,
  round(w.VALOR_VENDATEF, 2) as VALOR_VENDATEF,
  round(w.VALOR_VENDAPOS, 2) as VALOR_VENDAPOS,
  round(w.VALOR_CREDITOAPROVEITADO, 2) as VALOR_CREDITOAPROVEITADO
	FROM (
select
	filiais.nomeempresa as TEXTO_FILIAL,
	min(encefat.dt_movimento) as DATA_DATAINICIAL,
	max(encefat.dt_movimento) as DATA_DATAFINAL,
	sum(case when cdoperc.devvenda = 'S' THEN round(PedidoC.TotalPedido * -1,2) else round(PedidoC.TotalPedido,2) end) as VALOR_TOTALVENDAS,
	sum(case when cdoperc.transfentrefiliais = '1' THEN round(PedidoC.TotalPedido,2) else 0 end) as VALOR_TRANSFERENCIA,
	sum(case when cdoperc.transfentrefiliais = '1' THEN 1 else 0 end) as TEXTO_QUANTTRANSFERENCIA,
	sum(case when cdoperc.devvenda = 'S' THEN -1 else 1 end) as TEXTO_QUANTIDADEVENDAS,
	sum (encefat.vlrdinheiro - encefat.vlrtroco) as VALOR_VENDADINHEIRO,
	sum (encefat.vlrcheque + encefat.vlrchpredatado) as VALOR_VENDACHEQUE,
	sum (encefat.vlrreceber) as VALOR_VENDARECEBER,
	sum (encefat.vlrcartao) as VALOR_VENDATEF,
	sum (encefat.vlrconvenio) as VALOR_VENDAPOS,
	sum (coalesce(w.vcred,0)) as VALOR_CREDITOAPROVEITADO
from
	pedidoc
	INNER JOIN filiais on pedidoc.codempresa = filiais.codempresa
	INNER JOIN encefat on pedidoc.codempresa = encefat.codempresa and
						  pedidoc.tipopedido = encefat.tipopedido and
						  pedidoc.codpedido = encefat.codpedido and
						  pedidoc.codcliente = encefat.codcliente -- and
						 -- coalesce(pedidoc.codpedidoimportado,'') = ''
	INNER JOIN cdoperc ON pedidoc.codoper = cdoperc.codoper
	LEFT JOIN pedidoc pedc ON pedc.codempresa = pedidoc.codempresa AND
							  pedc.codpedido  = pedidoc.codpedidodevolucao and
							  pedc.tipopedido = pedidoc.tipopedidodevolucao AND
							  pedc.codcliente = pedidoc.codcliente
	LEFT JOIN (select c.documentobaixa, c.datamovimento, c.tipodocumentobaixa, c.codcliente, c.codempresa, sum(c.valormovimento) as vcred from creditos 
                           c where c.tiporegistro = 'M' group by 1,2,3,4,5) as w
                 on w.documentobaixa = encefat.codpedido and
                      w.datamovimento = encefat.dt_movimento and
                      w.codcliente = encefat.codcliente and
                     case when w.tipodocumentobaixa = 'OS' then '65' else w.tipodocumentobaixa end  = encefat.tipopedido
where
	pedidoc.datafatura between '[DATA_INICIAL]' and '[DATA_FINAL]'
	AND filiais.CGC = '[CNPJ_FILIAL]'  and
	pedidoc.faturado = 'S' and  (cdoperc.MapaVenda = 'S' Or  Cdoperc.DevVenda  = 'S')
	group by 1
 ) as w"""

VENDAS_GRUPO_QUERY = """select filial as TEXTO_FILIAL, '[DATA_INICIAL]' as DATA_DATAINICIAL, '[DATA_FINAL]' as DATA_DATAFINAL,  grupo as TEXTO_GRUPO, quantidade as QUANTIDADE_GRUPO,  valor as VALOR_GRUPO from (
   select f.nomeempresa as Filial, coalesce(g.descricao,'SEM GRUPO') as Grupo,
                round(sum(pi.quantidade),2) as Quantidade, round(sum(pi.totalrateado),2) as Valor from  pedidoc pc
             inner join pedidoi pi on pc.codempresa = pi.codempresa and pc.tipopedido = pi.tipopedido and pc.codpedido = pi.codpedido and pc.codcliente =  pi.codcliente
             inner join produto p on p.codprod = pi.codprod
            inner join filiais f on pc.codempresa = f.codempresa
            left join gruprod g on g.codgrupo = p.codgrupo
            INNER JOIN cdoperc ON pc.codoper = cdoperc.codoper
            where (cdoperc.MapaVenda = 'S' Or  Cdoperc.DevVenda  = 'S') and pc.datapedido between '[DATA_INICIAL]' and '[DATA_FINAL]'
            and pc.faturado = 'S' and f.CGC = '[CNPJ_FILIAL]'
            group by 1,2
union all
              select f.nomeempresa as Filial, 'Total' as Grupo,
                round(sum(pi.quantidade),2) as Quantidade, round(sum(pi.totalrateado),2) as Valor from  pedidoc pc
             inner join pedidoi pi on pc.codempresa = pi.codempresa and pc.tipopedido = pi.tipopedido and pc.codpedido = pi.codpedido and pc.codcliente =  pi.codcliente
             inner join produto p on p.codprod = pi.codprod
            inner join filiais f on pc.codempresa = f.codempresa
            left join gruprod g on g.codgrupo = p.codgrupo
            INNER JOIN cdoperc ON pc.codoper = cdoperc.codoper
            where (cdoperc.MapaVenda = 'S' Or  Cdoperc.DevVenda  = 'S') and pc.datapedido between '[DATA_INICIAL]' and '[DATA_FINAL]'
            and pc.faturado = 'S' and f.CGC = '[CNPJ_FILIAL]'
            group by 1,2
   ) as xx"""

PRODUTOS_MAIS_VENDIDOS_QUERY = """SELECT
    filiais.nomeempresa AS TEXTO_NOMEEMPRESA,
    produto.codprod || ' - ' || produto.descricao AS TEXTO_PRODUTO,
    ROUND(SUM(pedidoi.quantidade),2) AS QUANTIDADE_VENDIDA,
    ROUND(SUM(pedidoi.totalrateado),2) AS VALOR_VENDA
FROM
    produto
JOIN
    pedidoi ON produto.codprod = pedidoi.codprod
JOIN
    filiais ON pedidoi.codempresa = filiais.codempresa
JOIN
    pedidoc on  pedidoi.codempresa = pedidoc.codempresa
    and pedidoi.tipopedido = pedidoc.tipopedido
    and pedidoi.codcliente = pedidoc.codcliente
    and pedidoi.codpedido = pedidoc.codpedido
JOIN
    cdoperc ON pedidoc.codoper = cdoperc.codoper
WHERE
    filiais.CGC = '[CNPJ_FILIAL]'
    AND pedidoc.datapedido between '[DATA_INICIAL]' and '[DATA_FINAL]'
    and pedidoc.faturado = 'S'
    and  cdoperc.MapaVenda = 'S'
    AND PRODUTO.ativo = 'S'
GROUP BY
    filiais.nomeempresa,
    produto.codprod,
    produto.descricao
ORDER BY
    QUANTIDADE_VENDIDA DESC
ROWS 15"""

DESPESAS_CAIXA_QUERY = """
 select  Filial, Contacx, Descricao, sum(total) as Total from (
SELECT  f1.nomeempresa as FILIAL,  p.contacx as CONTACX, p.descricao as DESCRICAO,  sum(m.valormov) as TOTAL
 FROM movimen m
INNER JOIN pcontas p on p.contacx = m.contacx  AND p.dc = 'D' AND p.confrelgeralsaldo =  'S'
inner join filiais f1 on f1.codempresa = m.codempresa
WHERE  m.lancavulso =  'S' and m.dt_movimento between '[DATA_INICIAL]' and '[DATA_FINAL]' and f1.CGC = '[CNPJ_FILIAL]'
group by 1,2 ,3
union all
 select f.nomeempresa, p.contacx, p.descricao, sum(coalesce(d.valordesc,0)) as total
 from docurec d
  inner join filiais f on f.codempresa = d.codempresa
  inner join cartcon c on c.codigo = d.codvinculo
  INNER JOIN pcontas p on p.contacx = c.contacxaretencao
  where d.codvinculo is not null and  d.dt_emissao between '[DATA_INICIAL]' and '[DATA_FINAL]' 
	and f.CGC = '[CNPJ_FILIAL]'
   group by 1,2, 3 having sum(coalesce(d.valordesc,0)) > 0
   union all
    select f.nomeempresa, p.contacx, p.descricao, sum(e.valormov) as total
  from moviban e
   inner join filiais f on f.codempresa = e.codempresaorigem
   INNER JOIN pcontas p on p.contacx = e.cc
   where e.cc NOT IN ('0205004','0205005') and e.lancavulso = 'S'
    and p.dc = 'D' and p.confrelgeralsaldo =  'S' and e.datamov between '[DATA_INICIAL]' and '[DATA_FINAL]'  
	and coalesce(f.CGC ,'') = '[CNPJ_FILIAL]'
    group by 1,2, 3
    ) as x group by 1,2,3
"""
