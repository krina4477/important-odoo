from . import models

def _pre_init_query_run(cr):
    """ Allow change the type of studio field
    """
    cr.execute("""UPDATE ir_model
                     SET state='base' where model='x_radio';""")
