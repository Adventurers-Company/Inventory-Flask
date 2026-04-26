# Inventory

Aplicação Flask para modelar e gerenciar inventário e equipamentos de um jogador (bags, slots, itens, serviços de inventário/equipamento).

**Status:** Protótipo / demo

## Recursos

- Modelos para `Player`, `Item`, `Bag`, `BagSlot` e `EquipSlot`.
- Blueprints para inventário, equipamento e API.
- Serviço de cálculo/negócio para movimentação e equipagem de itens.
- Banco SQLite por padrão e seed de dados iniciais.

## Estrutura principal do projeto

- [run.py](run.py) — ponto de entrada da aplicação.
- [config.py](config.py) — configurações por ambiente.
- [requirements.txt](requirements.txt) — dependências do projeto.
- [test_models.py](test_models.py) — script simples para verificar modelos e serviços.
- [app/__init__.py](app/__init__.py) — fábrica da aplicação e registro de blueprints.
- `app/blueprints/` — rotas da aplicação.
- `app/models/` — modelos SQLAlchemy.
- `app/services/` — lógica de negócio (inventory / equipment / calculation).

## Pré-requisitos

- Python 3.10+ recomendado
- Recomenda-se criar um ambiente virtual

## Instalação

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No Linux / macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Executando a aplicação

Por padrão a aplicação usa SQLite (arquivo `inventory.db`). Para rodar em ambiente de desenvolvimento:

```powershell
# Windows PowerShell
$env:FLASK_ENV = 'development'
python run.py
```

Ou no Linux/macOS:

```bash
export FLASK_ENV=development
python run.py
```

A aplicação irá subir em `http://0.0.0.0:5000` por padrão.

Para produção, defina `FLASK_ENV=production` e configure `SECRET_KEY` e outras variáveis de ambiente conforme necessário.

## Testes rápidos

Há um script simples que valida importações e campos básicos dos modelos:

```bash
python test_models.py
```

## Notas de desenvolvimento

- A fábrica `create_app` em [app/__init__.py](app/__init__.py) cria as tabelas e popula dados iniciais quando o app inicia.
- As configurações estão em [config.py](config.py): `development`, `production` e `testing`.
