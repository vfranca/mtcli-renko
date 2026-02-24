from .commands.renko import renko


def register(cli):
    cli.add_command(renko, name="renko")
    cli.add_command(renko, name="rk")
