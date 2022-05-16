'''
The initial table is created with peewee (initInstanceDB).
All further adjustments should be made with yoyo-migrations.
For a new adjustment, a new file is needed, stored next to this one.
Yoyo stores already applied migrations in the db:

gis=# select * from _yoyo_migration ;
migration_hash                          |     migration_id     |
 applied_at_utc
------------------------------------------------------------------+----------------------+----------------------------
b9faf3aa8fe158938471e8275bf6f7dc6d49bd4c5e7a89953de4b790b711eba8 |
 0001.add-status_info | 2020-06-10 15:13:45.250212

gis=# select * from _yoyo_log ;
id                  |
 migration_hash                          |     migration_id     | operation |
 username | hostname | comment |      created_at_utc
--------------------------------------+------------------------------------------------------------------+----------------------+-----------+----------+----------+---------+---------------------------
fa2e5dd8-ab2c-11ea-9e24-6057186705c0 |
 b9faf3aa8fe158938471e8275bf6f7dc6d49bd4c5e7a89953de4b790b711eba8 |
 0001.add-status_info | apply     | default  | carmen   |         | 2020-06-10
 15:13:45.24777
(1 row)

Rollbacks are also possible but currently not integrated in our code. We should
use them, if we have more comlex migration scripts which should not be applied
only partwise.
Pure SQL scripts are also possible but cannot replace variables as needed here.

For more information, see https://ollycope.com/software/yoyo/latest/

'''

from yoyo import step
from actinia_parallel_plugin.resources.config import JOBTABLE

# dummy migration to test functionality
steps = [
  step(
      "select * from %s limit 1" % JOBTABLE.table
  )
]
