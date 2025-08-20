# Painel de Gestão interna
Me foi demandado um painel para que a equipe de gestão conseguisse acompanhar os processos de tarefas e necessidades diárias da empresa com a ferramenta que utilizamos, o Gestta, seguindo algumas regras de negócio, como:
- Menor custo possível;
- Taxa de atualização praticamente instantânea;
- Gestão de times e pessoas em específico, com visuais temporais e quantitativos.
Nesse projeto utilizei as seguintes ferramentas e técnicas:
- Python (com suas bibliotecas, como, Pandas, SQLAlchemy, OS, Requests);
- PostgreSQL;
- Python + Selenium (para uma RPA);
- Excel online;
- PowerBI;
- Uso e criação de API;
- Criação de views e joins no banco de dados;
- Criação de medidas e colunas DAX, tooltips, relacionamento dentro do PowerBI.
  
O painel foi separado em 3 partes, focalizando em cada necessidade em específico:
1º Operacional: dentro dele conseguimos fazer uma gestão das tarefas que são distribuídas entre os setores e as pessoas, para assim, fazer um acompanhamento direto a quantidade de tarefas, como estão seus status, como está o desenvolvimento das equipes e pessoal e diversos outros insights;
Alguns desafios que encontrei dentro desse projeto foram, o Gestta não disponibiliza uma API pública para conseguir puxar os dados, então, desenvolvi um meio por um get ao endpoint que conseguisse me trazer as informações que precisava, tudo isso utilizando Python com suas bibliotecas, essa informação tem alta volatidade então precisava de alta taxa de atualização, a empresa por optar por menor gasto preferiu não assinar plano premium, então, desenvolvi uma RPA que atualiza o meu conjunto de dados a cada 5 minutos e usando o agendador de tarefas faço para chamar todo bloco de código necessário para rodar todo esse fluxo;
2º Atendimento: dentro desse painel conseguimos acompanhar a criação das tarefas, com visualizações temporais e quantitativas, para gerir o time de criação para tirar uma base de como seguir com novas técnicas para otimizar o contato com o cliente e garantir que as demandas sejam resolvidas no menor tempo, somando os painéis de atendimento e operacional;
Alguns desafios que encontrei dentro desse projeto foram, como já dito o Gestta não disponibiliza API pública, e nesse caso o endpoint é variável a cada tarefa, pois cada tarefa tem seu ID, criei um for para primeiro ler todas tarefas que existiam no meu conjunto de dados, e com os ID puxado desse conjunto criei um for para rodar em relação a todo o período, conseguindo pegar todos os ID e fazer esse chamado get para trazer todas tarefas pelo seu ID, colocando para rodar a cada começo do dia puxando os ID somente do dia anterior;
3º Apuração: dentro desse é possível acompanhar como o time de Fiscal está, analisando as empresas e os passos que ainda faltam dar continuidade para que todo o processo contábil funcione;
Como desafio dentro desse projeto foi o seguinte, as informações são dadas manualmente, então vinculei o painel a um conjunto de dados Excel que está no Drive da empresa, então o gestor alimenta a fonte de dados nesse arquivo direto da nuvem e no momento em que é salvo o painel é atualizado.
