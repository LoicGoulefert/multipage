import click
import vpype as vp


@click.command()
@vp.generator
def multipage():
    """
    Insert documentation here...
    """
    lc = vp.LineCollection()
    return lc


multipage.help_group = "Plugins"
