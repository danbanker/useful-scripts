import teradata_tools
session = teradata_tools.TeradataSession(keyring_name='tdprod', system='tdprod', username='user_here', logmech='LDAP') # remove logmech arg for standard up_ production user
result = session.query('select current_date as today_dt;')
first_event_id = result[0].values[result[0].columns['today_dt']]
print('pause')