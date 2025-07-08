import click

@click.argument('config',type=click.File('r'))
@click.command()
def importer(config):
    content=config.read()
    output="config.py"
    f=open(output, 'w',encoding='utf-8')
    f.write(content)
    f.close()
    import runner
    
if __name__ == '__main__':
    importer()
    
# python click_application.py sample_config.py