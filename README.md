**Análise exploratória dos dados de vendas dos EUA**

*Ultilize este código para fazer o clone do repositório:*

#importando modulos
import os
from getpass import getpass

class autent_git(object):

  def __init__(self, username: str, usermail: str, token: str):
    self.username = username
    self.usermail = usermail
    self.token = token
    self.cofig_user = self._config_user()
    self.cofig_mail = self._config_mail()
    self.cofig_token = self._config_token()
    
  def _config_user(self):
    try:
      os.environ['GITHUB_USER'] = self.username
      !git config --global user.name "${GITHUB_USER}"
    except Exception as exc:
      print(exc)
    else:
      print("Autenticação de usuário realizada com sucesso.")

  def _config_mail(self):
    try:
      os.environ['GITHUB_MAIL'] = self.usermail
      !git config --global user.email $'{GITHUB_MAIL}'
    except Exception as exc:
      print(exc)
    else:
      print("Autenticação de email realizada com sucesso.")


  def _config_token(self):
    try:
      os.environ['GITHUB_TOKEN'] = self.token
    except Exception as exc:
      print(exc)
    else:
      print("Autenticação de token realizada com sucesso.")

- Depois de criar a classe, instancie seus dados:

#instanciando autenticação
user_git = autent_git('', "", '')