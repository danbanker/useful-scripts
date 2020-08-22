import pymssql
import os
import argparse
import datetime_tools

t = datetime_tools.DateTimeTools()
tms = t.current_yyyymmddhhmmss
t2 = datetime_tools.DateTimeTools()
tms2 = t2.current_yyyymmddhhmmss
td = t.current_date
tmd = t.format_dashed_yyyymmdd(td)

cwd = os.path.dirname(os.path.realpath(__file__))
print('CWD: ' + cwd)
os.chdir(cwd)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', dest='server', default='localhost')
    parser.add_argument('--user', dest='user', default='test')
    parser.add_argument('--password', dest='password', default='test')
    parser.add_argument('--database', dest='database', default='test')
    parser.add_argument('--port', dest='port', default=1433)
    args = parser.parse_args()

    session = SQLSession(server=args.server, user=args.user, password=args.password, database=args.database, port=args.port)

    test_delete = "delete from tbl_test"
    test_delete_result = session.dml(test_delete, debug=True)

    test_insert = "insert into tbl_test(col_1, col_2) values('%s', '%s')" % (tms, tms)
    test_insert_result = session.dml(test_insert, debug=True)

    test_insert_2 = "insert into tbl_test(col_1, col_2) values('%s', '%s')" % (tms2, tms2)
    test_insert_result_2 = session.dml(test_insert_2, debug=True)

    test_update = "update tbl_test set col_1 = col_1+'!'"
    test_update_result = session.dml(test_update, debug=True)

    test_query = 'select * from tbl_test'
    test_query_result = session.query(test_query, debug=True)

    result_dict = {'test_delete':test_delete, 'test_delete_result':test_delete_result,
                   'test_insert':test_insert, 'test_insert_result':test_insert_result,
                   'test_insert_2':test_insert_2, 'test_insert_result_2':test_insert_result_2,
                   'test_update':test_update, 'test_update_result':test_update_result,
                   'test_query':test_query, 'test_query_result':test_query_result}
    return result_dict

class SQLSession:
    def __init__(self, server, user, password, database, port, as_dict=True, autocommit=True):
        self.conn = pymssql.connect(server=server, user=user, password=password, database=database, port=port, as_dict=as_dict, autocommit=autocommit)
        #conn = pyodbc.connect(driver='{ODBC Driver 13 for SQL Server}',server='tcp:localhost,1433',database=database, uid=user, pwd=password)

    def statement(self, query_string, result_data=False, debug=False, many_list=None):
        cursor = self.conn.cursor()

        if debug:
            print('query_string: '+ query_string)

        if many_list:
            cursor.executemany(query_string, many_list)
        else:
            cursor.execute(query_string)

        if result_data:
            result = cursor.fetchall()
        else:
            result = cursor._source._conn.rows_affected

        if debug:
            print('result: '+ str(result))

        cursor.close()
        return result

    def query(self, query_string, debug=False):
        return self.statement(query_string, result_data=True, debug=debug)

    def dml(self, query_string, debug=False, many_list=None):
        return self.statement(query_string, result_data=False, debug=debug, many_list=many_list)

if __name__ == "__main__":
    test_result = main()
    print('TEST COMPLETE!')