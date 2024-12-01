

# Chatbot para Solicitação e Validação de Horas Complementares

Este projeto desenvolve um chatbot que visa otimizar o processo de solicitação e validação de horas complementares, um requisito essencial para a conclusão do curso de Bacharelado em Ciência da Computação da UFRJ. A solução foi criada para ajudar a Comissão de Atividades Complementares (COAC), aliviando a sobrecarga da equipe, reduzindo erros e simplificando a interação dos alunos com o sistema. O chatbot automatiza a verificação de matrícula, organização de documentos e preenchimento do formulário de solicitação, proporcionando mais agilidade e eficiência no processo.

A implementação foi realizada em Python, utilizando a biblioteca python-telegram-bot para integração com o Telegram, e outras bibliotecas como py_pdf_parser e PyPDFForm para manipulação de documentos. O sistema está hospedado em um Raspberry Pi, com possibilidade de migração futura para a nuvem. O projeto visa melhorar a experiência dos alunos e a eficiência da COAC, oferecendo uma interface simples e acessível.

### Estrutura do Projeto

* **`main.py`** : Arquivo principal para iniciar o bot.
* **`boa_parser.py`** : Contém lógica relacionada ao parsing de documentos.
* **`business_logic.py`** : Implementa a lógica de negócios do chatbot.
* **`database.py`** : Gerencia interações com o banco de dados.
* **`telegram_handlers.py`** : Define as funções de manipulação para interações no Telegram.
* **`requirements.txt`** : Lista de bibliotecas necessárias para execução do projeto.
* **`dtos/`** : Pasta contendo objetos de transferência de dados (provavelmente define estruturas de dados).
* **`files/`** : Contém arquivos necessários para a execução, como PDFs ou dados auxiliares.
* **`FORMULARIO_ANTERIOR.pdf` e `FORMULARIO_ATUAL.pdf`** : Formulários em PDF usados no processo.
* **`anterior_preview.pdf` e `atual_preview.pdf`** : Pré-visualizações ou exemplos de formulários processados.

### Requisitos

1. **Dependências de Python** :
   O projeto utiliza as seguintes bibliotecas:

* `python-telegram-bot==21.6`: Integração com o Telegram.
* `py-pdf-parser==0.13.0` e `PyPDFForm==1.4.37`: Para manipulação de PDFs.
* `peewee==3.17.6`: Gerenciamento do banco de dados.
* `reportlab==4.2.5`: Geração de PDFs.
* `python-dotenv==1.0.1`: Gerenciamento de variáveis de ambiente.
* Outras bibliotecas gerais: `anyio`, `cryptography`, `httpx`, `idna`, etc.

1. **Ambiente** :

* **Python 3.8+** : Recomendado para garantir compatibilidade com as bibliotecas.
* **Raspberry Pi** (opcional): O sistema pode ser hospedado localmente ou migrado para um servidor de nuvem.

### Execução

1. **Instalar as dependências** :
   Execute o seguinte comando no terminal:

   ```
   pip install -r requirements.txt
   ```
2. **Configurar variáveis de ambiente** :

* O projeto parece usar `python-dotenv`, então as variáveis sensíveis, como a chave da API do Telegram, devem ser configuradas em um arquivo `.env`.

3. **Executar o bot** :

* O arquivo principal é `main.py`. Para iniciar o bot, use:
  ```
  python main.py
  ```

4. **Testar no Telegram** :

* Certifique-se de configurar o bot corretamente no BotFather para integrá-lo ao Telegram.

### Configurando um Ambiente Virtual com `venv`

1) **Criar um ambiente virtual**:

```
python3 -m venv venv
```

**2. Ativar o ambiente virtual** :

* Em Linux/macOS:

  ```
  source venv/bin/activate
  ```

Em Windows:

``venv\Scripts\activate``

1. **Instalar as dependências dentro do ambiente** :

pip install -r requirements.txt

### **Funcionamento do bot**

1. **Configuração do Ambiente** :

* Usa a biblioteca `dotenv` para carregar variáveis de ambiente, como o token do bot (`TELEGRAM_BOT_TOKEN`).
* Cria o diretório `files` automaticamente, se não existir, para armazenar arquivos enviados pelos usuários.

1. **Handlers Principais** :
   Os handlers são responsáveis por lidar com comandos e mensagens enviadas ao bot:

* **Comandos** :
  * `/start`: Inicia ou retoma um processo baseado no `chat_id` do usuário.
  * `/attach`: Permite anexar comprovantes de horas complementares.
  * `/delete`: Deleta o processo atual.
  * `/finish`: Finaliza o processo se os critérios forem atendidos.
  * `/help`: Exibe informações de ajuda.
* **Mensagens** :
  * **PDFs** : Processa arquivos PDF enviados.
  * **Texto** : Interpreta mensagens de texto de acordo com o estado atual do processo.
* **Callback Query** :
  * Processa interações de botões inline para fluxo de anexos e seleção de categorias.

1. **Fluxo Lógico** :

* O fluxo de interação é gerenciado com base no status do processo (`ProcessStatusEnum`) e no status dos anexos (`CurrentFillingAttachmentStatusEnum`).
* A lógica garante que as ações sejam realizadas na ordem correta. Por exemplo, o comando `/attach` só funciona quando o status do processo é `WAITING_ATTACH_START`.

1. **Interações com o Banco de Dados** :

* Os dados do processo, como informações do aluno e anexos, são carregados, salvos e deletados usando funções no arquivo `database.py`.

1. **Execução** :

* A aplicação é iniciada usando `ApplicationBuilder().run_polling()`.

### Banco de dados

O `database.py` gerencia a persistência dos dados do bot. Ele utiliza a biblioteca **Peewee** para manipular um banco de dados SQLite.

* **Configuração do Banco de Dados** :
  * Define o arquivo SQLite (`database.db`) como a fonte de dados.
  * Configura a tabela com suporte a *foreign keys* para gerenciar relacionamentos entre tabelas.
* **Modelos de Dados** :
  * **ProcessModel** :
    * Representa o processo de um usuário.
    * Armazena informações do aluno, como nome, DRE, e-mail, e status do processo.
  * **HoursAttachmentModel** :
    * Representa os anexos enviados pelo usuário.
    * Cada anexo é vinculado a um processo e contém informações como categoria, horas complementares, data, e descrição.
  * **CurrentFillingAttachmentModel** :
    * Representa o estado atual do anexo sendo preenchido.
    * Inclui informações parciais que o usuário forneceu até o momento.
* **Funções Importantes** :
  * **`init()`** :
    * Cria as tabelas no banco de dados, se ainda não existirem.
  * **`create_process()` e `save_process()`** :
    * Criam ou salvam os dados de um processo no banco de dados.
    * Incluem informações detalhadas, como anexos associados.
  * **`load_process()`** :
    * Carrega um processo com base no `chat_id`.
    * Converte os dados armazenados no banco em um objeto `ProcessDto`.
  * **`delete_process()`** :
    * Remove o processo associado a um `chat_id`, incluindo seus anexos.
  * **`create_current_filling_attachment()` e `save_current_filling_attachment()`** :
    * Criam ou atualizam o estado atual de um anexo.
  * **`load_current_filling_attachment()`** :
    * Retorna o estado atual do anexo em preenchimento.
  * **`delete_current_filling_attachment()`** :
    * Remove o estado atual de preenchimento do anexo.

### Handlers de interação com o Telegram

Implementados em telegram_handlers.py para gerenciar as interações com a API do Telegram. Segue abaixo principais funções:

* **Função `get_process_info`** : Gera uma mensagem com as informações detalhadas sobre o processo em andamento, como nome, DRE, currículo, horas registradas e comandos disponíveis (como `/delete`, `/attach`, `/finish`).
* **Funções de Processos e Interações** :
  * **`handle_start_new_process`** : Envia mensagem inicial pedindo o envio de um arquivo PDF para iniciar um processo.
  * **`handle_start_process_already_exists`** : Exibe detalhes do processo se um já estiver em andamento para o chat.
  * **`handle_process_creation`** : Faz o download do arquivo BOA, valida e cria o processo, solicitando mais informações do usuário (ano e período de ingresso).
  * **`validate_boa_info`** : Valida informações extraídas do BOA, como a situação ativa e o curso de Ciência da Computação.
* **Funções de Anexos e Validação de Documentos** :
  * **`handle_process_attach_document`** : Permite anexar documentos ao processo quando o estado for adequado, salva o arquivo e atualiza o status do processo.
  * **`handle_attachment_text_message`** : Processa mensagens de texto relacionadas ao preenchimento de campos de anexos (quantidade, data, descrição).
  * **`handle_fill_amount`, `handle_fill_date`, `handle_fill_description`** : Auxiliam na coleta de dados específicos para os anexos, como quantidade de horas, data e descrição do evento.
* **Funções de Acompanhamento do Processo** :
  * **`handle_ingress`** : Recebe e valida o ano e período de ingresso do usuário.
  * **`handle_email`** : Coleta o email institucional do usuário.
  * **`handle_phone`** : Solicita o telefone de contato e finaliza a coleta de dados pessoais.
* **Funções de Confirmação e Finalização** :
  * **`handle_finish_confirm_query_response`** : Lida com a confirmação do usuário sobre a correção dos dados, com opções para confirmar ou reiniciar o processo.
  * **`handle_process_finish`** : Envia o formulário de horas complementares preenchido para o usuário e solicita confirmação final.
* **Função de Consulta de Respostas** :
  * **`handle_query_response`** : Processa respostas em momentos inesperados e redireciona o fluxo conforme o status atual do processo (por exemplo, aguardando anexos, categoria de horas, etc.).

Essas funções em conjunto permitem a interação com o bot para criação, atualização e finalização de processos relacionados ao registro de horas complementares, validando documentos e informações fornecidas pelos usuários e gerenciando o progresso do processo.

### Regras de negócio

Implementadas em business_logic.py para o gerenciamento de processos relacionados a atividades acadêmicas, com foco na validação, cálculo e geração de dados associados às horas complementares. Ele é estruturado em várias funções que lidam com os seguintes aspectos:

#### Funções principais

1. **Validação de Horas** :

* `can_still_add_hours`: Verifica se ainda é possível adicionar mais horas para uma categoria específica dentro de um processo.
* `sum_hours_for_category`: Calcula o total de horas para uma categoria específica, garantindo que não exceda o limite permitido.

1. **Cálculos Gerais** :

* `total_process_hours`: Retorna a soma total de horas para todas as categorias de um processo.
* `get_process_target_hours`: Determina o total de horas alvo de um processo, com base no currículo associado.

1. **Limites por Categoria** :

* `max_hours_for_category`: Obtém o limite máximo de horas para uma categoria específica, dependendo do currículo.
* `max_hours_for_category_old_curriculum` e `max_hours_for_category_new_curriculum`: Definem os limites específicos para currículos antigos e novos.

1. **Multiplicadores e Valores Baseados em Currículo**:

* `get_hours_for_category_and_amount`: Calcula o total de horas com base em um valor arbitrário e na categoria.
* `get_old_curriculum_amount_multiplier` e `get_new_curriculum_amount_multiplier`: Determinam multiplicadores específicos para currículos antigos e novos.

1. **Geração de Formulários em PDF**:

* `generate_pdf_form_for_process`: Preenche automaticamente um formulário em PDF com as informações de um processo, gerando um arquivo pronto para submissão.

1. **Utilidades** :

* `get_category_map`: Agrupa os anexos do processo por categoria.
* `get_form_keys_for_category`: Mapeia as chaves dos campos do formulário PDF para cada categoria.
* `is_old_curriculum`: Identifica se o processo segue um currículo antigo.


## Conclusão

O chatbot desenvolvido para a Comissão de Atividades Complementares trouxe melhorias significativas na eficiência e organização do processo de solicitação e validação de horas complementares. Ao automatizar a verificação da matrícula dos alunos e a organização dos documentos, o sistema reduz a sobrecarga de trabalho da Comissão e facilita a comunicação com os alunos. Embora o chatbot não elimine totalmente as etapas manuais, ele otimiza o fluxo de trabalho, tornando o processo mais ágil e menos propenso a erros. A escolha do Telegram como plataforma garantiu acessibilidade e usabilidade, oferecendo uma experiência mais fluida para os alunos. Em resumo, a solução é uma melhoria prática e eficaz para um processo administrativo essencial.
