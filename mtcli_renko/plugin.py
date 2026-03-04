"""
Plugin de integração do comando Renko com o mtcli.

Este módulo é o ponto de entrada do plugin `mtcli-renko`.
Ele expõe a função `register()` que é utilizada pelo
plugin loader do mtcli para registrar comandos CLI.

Quando o plugin é carregado, o mtcli executa `register(cli)`
e os comandos definidos aqui passam a fazer parte da CLI
principal.

Comandos registrados
--------------------

rk
    Gera blocos Renko a partir de dados de mercado obtidos
    via MT5 ou banco local de ticks.

Exemplo de uso:

    mt rk

ou

    mt rk --symbol WIN$N --brick 60

Arquitetura
-----------

O plugin segue a estrutura MVC utilizada no ecossistema mtcli:

    commands/
        renko.py        → interface CLI (Click)

    controllers/
        renko_controller.py

    models/
        renko_model.py

Este arquivo apenas conecta o comando CLI ao loader
de plugins do mtcli.
"""

from .commands.renko import renko


def register(cli):
    """
    Registra os comandos do plugin no CLI principal.

    Esta função é chamada automaticamente pelo
    plugin loader do mtcli durante a inicialização.

    Parameters
    ----------
    cli : click.Group
        Grupo principal de comandos da aplicação `mt`.

    Notes
    -----
    O comando `renko` é registrado com o nome curto `rk`
    para facilitar o uso na linha de comando.
    """

    cli.add_command(renko, name="rk")
