import sys
import os

# Adiciona o diretório onde o pacote 'resellercontrol' está ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from resellercontrol import original_app, database
from resellercontrol.routes import pipeline_digest

# Criar o contexto da aplicação Flask real
with original_app.app_context():
    pipeline_digest()
