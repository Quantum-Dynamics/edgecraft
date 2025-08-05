import click


@click.argument('config', type=click.File('r'))
@click.option('--const', type=click.File('r'), default=None)
@click.option('--energy_graphs', type=bool, default=True)
@click.option('--anim', type=bool, default=True)
@click.option('--scale_factor', type=bool, default=True)
@click.option('--dynamics', type=bool, default=True)
@click.option('--pulse', type=bool, default=True)
@click.command()
def importer(
    config,
    const=None,
    energy_graphs=True,
    anim=True,
    scale_factor=True,
    dynamics=True,
    pulse=True,
):
    content = config.read()
    output = "user_configuration.py"
    f = open(output, 'w', encoding='utf-8')
    f.write(content)
    f.close()
    if const is not None:
        content = const.read()
        output = "const.py"
        f = open(output, 'w', encoding='utf-8')
        f.write(content)
        f.close()
    import runner
    runner.run(energy_graphs, anim, scale_factor, dynamics, pulse)


if __name__ == '__main__':
    importer()

# To run this script, use the command line:
# python click_application.py sample_config.py
