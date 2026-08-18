# SeguraMente

## Ferramenta inteligente para comunicação proativa com o segurado

MVP desenvolvido para o **Desafio 5 — InsurMinds**. A solução monitora uma fonte pública de dados meteorológicos, classifica eventos relevantes, aplica regras de elegibilidade a uma base sintética, gera mensagens preventivas com um modelo de linguagem e registra uma simulação de envio.

> O MVP não envia SMS, e-mail, WhatsApp ou notificações push. Todos os perfis são sintéticos e toda comunicação passa por revisão humana antes do registro da simulação.

## Atendimento ao Desafio 5

| Requisito do edital | Implementação neste repositório |
|---|---|
| Consumir API pública meteorológica | `seguramente/weather.py` integra a Open-Meteo Geocoding API e Forecast API. |
| Identificar eventos automaticamente | `seguramente/rules.py` classifica chuva intensa, granizo, ventos fortes e alagamento com limiares documentados. |
| Aplicar regras de decisão | `seguramente/rules.py` verifica relevância, produto, canal, contato e consentimento. |
| Gerar mensagens com IA/modelo de linguagem | `seguramente/llm.py` usa uma API OpenAI ou compatível, com prompt e guardrails explícitos. |
| Simular envio | `seguramente/pipeline.py` cria registros locais com status de simulação e não chama canais externos. |
| Demonstrar fluxo completo | `app.py` apresenta as etapas na interface Streamlit; `scripts/run_demo.py` gera evidência JSON reproduzível. |
| Relatório técnico | `docs/Documentacao_Tecnica_Desafio_5_SeguraMente.pdf`. |
| Código-fonte e instruções | Todo o código, testes, dados sintéticos e instruções estão neste repositório. |
| README e licença MIT | Este arquivo e `LICENSE`. |

## Arquitetura

O fluxo é organizado em etapas independentes:

```text
Open-Meteo Geocoding/Forecast
            |
            v
Normalização de WeatherObservation
            |
            v
Classificação por limiares meteorológicos
            |
            v
Cruzamento com insured_profiles.csv
            |
            v
Regras de elegibilidade e consentimento
            |
            v
Geração por modelo de linguagem
            |
            v
Revisão humana na interface
            |
            v
Registro de envio simulado
```

| Componente | Responsabilidade | Arquivo |
|---|---|---|
| Coletor meteorológico | Geocodificar a localidade e consultar dados atuais | `seguramente/weather.py` |
| Analista de eventos | Normalizar indicadores e classificar o risco | `seguramente/rules.py` |
| Regras de negócio | Decidir elegibilidade e registrar motivos | `seguramente/rules.py` |
| Gerador de mensagens | Produzir e validar comunicação preventiva | `seguramente/llm.py` |
| Simulador de envio | Registrar histórico sem comunicação real | `seguramente/pipeline.py` |
| Interface e revisão | Exibir etapas, permitir revisão e confirmar simulação | `app.py` |

## Requisitos

A execução local requer Python 3.11 ou superior. A consulta meteorológica usa a [Open-Meteo](https://open-meteo.com/en/docs), fonte pública que não exige chave para o fluxo demonstrativo. A geração com IA exige uma chave de uma API OpenAI ou compatível.

## Instalação

```bash
git clone <URL_DO_REPOSITORIO>
cd seguramente-desafio5
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` e configure `OPENAI_API_KEY`. O arquivo `.env` está no `.gitignore` e não deve ser publicado. Se o provedor for compatível com a API OpenAI, configure também `OPENAI_API_BASE` e `SEGURAMENTE_LLM_MODEL`.

## Execução da interface

```bash
streamlit run app.py
```

A interface oferece duas formas de demonstração:

| Modo | Uso |
|---|---|
| Demonstração reproduzível | Usa fixtures sintéticas para apresentar chuva intensa, granizo, ventos fortes ou alagamento sem depender da rede. |
| API ao vivo | Consulta uma localidade na Open-Meteo e executa o mesmo fluxo com dados meteorológicos atuais. |

O provider `openai` é o modo de produção demonstrável com modelo de linguagem. O provider `template` existe somente para testes e execução offline, mantendo a lógica de guardrails e simulação verificável quando não há credencial disponível.

## Demonstração reproduzível pela linha de comando

Para gerar uma evidência local sem chamada de modelo, use o provider determinístico de teste:

```bash
python scripts/run_demo.py \
  --scenario chuva_intensa \
  --provider template \
  --simulate \
  --output evidence/demo_run_offline.json
```

Para demonstrar a integração com modelo de linguagem, configure `.env` no ambiente e execute:

```bash
python scripts/run_demo.py \
  --scenario chuva_intensa \
  --provider openai \
  --simulate \
  --output evidence/demo_run_openai.json
```

O arquivo JSON registra fonte, coordenadas, indicadores, evento, justificativas, decisões, provider, modelo, mensagens e status da simulação. Ele não contém chaves de API.

## Regras e limiares do MVP

| Evento | Regra | Severidade |
|---|---|---|
| Granizo | Código meteorológico WMO 96 ou 99 | Alta |
| Alagamento | Precipitação atual igual ou superior a 30 mm | Crítica |
| Ventos fortes | Rajada igual ou superior a 60 km/h | Alta |
| Chuva intensa | Precipitação atual igual ou superior a 10 mm ou probabilidade igual ou superior a 70% | Moderada |
| Sem evento relevante | Nenhum limiar foi atingido | Baixa, sem comunicação |

O produto deve possuir relação com o evento. Chuva intensa e alagamento são relacionados a produtos residencial e empresarial; granizo, a automóvel e residencial; ventos fortes, a residencial, empresarial e automóvel. Perfis sem consentimento ativo, sem contato ou com canal incompatível são bloqueados com justificativa explícita.

## Uso de IA e guardrails

O prompt do sistema está em `seguramente/llm.py` e estabelece que a comunicação deve ser curta, preventiva, clara e não alarmista. O modelo não pode prometer cobertura, indenização ou aprovação de sinistro, nem solicitar senha, token, documento, código de segurança ou credencial.

A função `validate_message` rejeita respostas vazias, excessivamente longas ou que contenham padrões proibidos. A mensagem só é enviada ao simulador depois de ser exibida para revisão humana na interface.

## Testes

```bash
pytest -q
```

Os testes verificam a classificação de chuva, granizo e ventos; bloqueio por consentimento inativo e produto incompatível; rejeição de conteúdo proibido; aceitação de mensagem preventiva; geração de mensagem; e criação de registros sem comunicação real.

## Estrutura do projeto

```text
.
├── app.py
├── data/insured_profiles.csv
├── docs/
│   └── Documentacao_Tecnica_Desafio_5_SeguraMente.pdf
├── evidence/
│   └── demo_run.json
├── fixtures.py
├── LICENSE
├── README.md
├── requirements.txt
├── scripts/run_demo.py
├── seguramente/
│   ├── llm.py
│   ├── models.py
│   ├── pipeline.py
│   ├── profiles.py
│   ├── rules.py
│   └── weather.py
└── tests/test_seguramente.py
```

## Dados e limites

A base `data/insured_profiles.csv` contém somente perfis sintéticos e contatos fictícios. O sistema não acessa sistemas de seguradoras, não processa dados reais, não decide cobertura, não calcula indenização e não realiza disparos externos. Esses limites são intencionais para preservar o escopo didático do Desafio 5.

## Entrega e repositório

O edital determina que o README contenha instruções de instalação e execução e informe a licença MIT. Quando um repositório GitHub for utilizado na entrega, ele deve estar com acesso público. Antes do envio, confira também o PDF, o código-fonte compactado e as evidências de execução.

## Licença

Este projeto está licenciado sob a **MIT License**. Consulte `LICENSE`.
