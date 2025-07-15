import click

@click.argument('config',type=click.File('r'))
@click.option('--const',type=click.File('r'),default=None)
@click.command()
def importer(config,const=None):
    content=config.read()
    output="user_configuration.py"
    f=open(output, 'w',encoding='utf-8')
    f.write(content)
    f.close()
    if(const!=None):
        content=const.read()
        output="const.py"
        f=open(output, 'w',encoding='utf-8')
        f.write(content)
        f.close()
    import runner
    
if __name__ == '__main__':
    importer()
    
# python click_application.py sample_config.py