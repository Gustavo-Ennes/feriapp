# FERIAPP

Sistema escrito em Python e Django que visa automatizar a rotina de diferentes tipos de férias e folgas para trabalhadores públicos.

## O que ele faz

- Principais funções agrupadas na página principal de forma intuitiva

- Banner informativo via Web Scrapping: banners informativos oficiais são buscados utilizando o Google Cloud Functions, copiados e rearranjados na página principal todos os dias, rotina que é mantida utilizando Google Cloud Scheduler. 

- Cadastro de trabalhadores e secretarias

- Formulários:
    1. Requisição de Abonada
    2. Requisição e requisição de Cancelamento de Férias
    3. Requisição e requisição de Cancelamento de Licença-Prêmio
    4. Requisição de Materiais
    5. Atestado de Trabalho
    6. Sexta-Parte
    7. Justificativas de Horas Extras

    
- Automação de Relatórios de Horas Extras:
    1. Transferência de servidor entre Relatórios
    2. Divisão de horas de servidor entre Relatórios
    
- Geração de PDF's:
    1. Pdf gerado automaticamente após agendamento de qualquer tipo de requerimento: folgas(férias, abonadas, etc), justificativas, relatório de H.E, atestado, etc.
    2. Botão de geração de pdf em todas as páginas listas ou tabelas
    3. Pesquisa detalhada


    
- Monitor de folgas: te lembra quem folgará nos próximos dias, quem está folgando agora, e quem logo retornará ao trabalho e quando.
    
- Lembretes: ao logar, caso lembretes precisem ser exibidos, eles são jogados na tela em um modal, garatindo que o usuário visualize o conteúdo do lembrete.


