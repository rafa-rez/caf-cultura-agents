# RAG-Café: Sistema Distribuído de Suporte à Decisão na Cafeicultura

Este projeto é um sistema distribuído focado em resolver uma dor central da cafeicultura moderna, utilizando Agentes de Inteligência Artificial para fornecer conhecimento técnico-científico acessível.

## 1. A "Dor" do Problema (1,5 pts)

A cafeicultura brasileira é uma das mais avançadas do mundo, mas enfrenta desafios complexos: mudanças climáticas, manejo de pragas e doenças resistentes, volatilidade do mercado e a necessidade constante de otimização de recursos (água, fertilizantes).

Os produtores e agrônomos precisam tomar decisões rápidas baseadas em informações técnicas, mas o conhecimento científico relevante está disperso em artigos, boletins técnicos (EMBRAPA, UFLA, etc.) e manuais.

**A "Dor" principal é:** A dificuldade do produtor em **obter respostas rápidas, confiáveis e contextualizadas** para problemas específicos (ex: "Qual o tratamento recomendado para mancha-de-olho-pardo em lavoura de 2 anos?") sem ter que consultar manualmente múltiplas fontes ou depender da disponibilidade imediata de um especialista.

## 2. Validação da Relevância (2,5 pts)

A necessidade de informação técnica rápida e de qualidade na cafeicultura é amplamente documentada por instituições de pesquisa e órgãos governamentais. A complexidade do setor justifica a necessidade de ferramentas de apoio à decisão.

**Referências de Validação:**

1.  **EMBRAPA (Empresa Brasileira de Pesquisa Agropecuária):** A EMBRAPA publica constantemente boletins técnicos sobre o manejo de pragas, doenças e safras, indicando a necessidade de disseminação de conhecimento.
    * *Referência:* [EMBRAPA - Café: Doenças](https://www.embrapa.br/cafe/doencas)
2.  **UFLA (Universidade Federal de Lavras):** Sendo um polo de excelência em agronomia e cafeicultura (PRPG UFLA), a universidade gera um vasto volume de pesquisas sobre o tema, muitas das quais poderiam ser mais acessíveis aos produtores.
    * *Referência:* [Repositório UFLA - Teses sobre Cafeicultura](http://repositorio.ufla.br/jspui/handle/1/13)
3.  **Ministério da Agricultura, Pecuária e Abastecimento (MAPA):** O MAPA frequentemente lança planos de safra e diretrizes que dependem da adoção de tecnologia e boas práticas, reforçando a necessidade de acesso à informação.
    * *Referáecia:* [MAPA - Programas e Ações - Café](https://www.gov.br/agricultura/pt-br/assuntos/camaras-setoriais-tematicas/composicao/agricola/cafe)
4.  **Consórcio Pesquisa Café (CBP&D/Café):** A existência de um consórcio focado exclusivamente em pesquisa demonstra a complexidade e a demanda por soluções inovadoras e disseminação de informação no setor.
    * *Referência:* [Consórcio Pesquisa Café](https://www.consorciopesquisacafe.com.br/)

## 3. A Solução: RAG-Café

Nosso sistema propõe o uso de dois Agentes de IA (via arquitetura RAG - Retrieval-Augmented Generation) para "ler" essa base de conhecimento (artigos, boletins) e fornecer respostas precisas, agindo como um "agrônomo assistente virtual" baseado em fatos.

---