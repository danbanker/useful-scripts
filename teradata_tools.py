import teradata
import base64
import keyring.backend
import pandas as pd

def main():
    test_class = TeradataSession('tdprod', 'up_edwetl_fin')
    # query_result = test_class.query("SELECT current_date as currdt")
    query_result = test_class.query("SELECT top 100 * from dp_vedw_biz_xm.bill_line")
    test_class.output(query_result, filepath='D:/Data/E_Drive/DataFile/GL_Summary/Output_Drop/output.xlsx')
    radioid_esn__c = '8V7BRAM3'
    sub_num = 'Z-S00168438'
    dc_name = 'Fix_Missing_ESN-2019-05-27-15-11-31'
    td_update_query = "update dp_tedw_fin.zu_subscription set RadioID_ESN__c = '{}', Notes = '{}' where Name = '{}';".format(radioid_esn__c, dc_name, sub_num)
    update_result = test_class.execute(td_update_query)
    print(str(query_result))
    print(str(update_result))
    print('Done')


class TeradataSession():
    def __init__(self, keyring_name, username, system='tdprod', driver='Teradata', sessionName='td_session', version="1.0", logConsole=True, method='odbc', charset='UTF8', logmech='TD2', port=1025):
        password = base64.b64decode(keyring.get_password(keyring_name, username)).decode("utf-8")
        udaExec = teradata.UdaExec(appName=sessionName, version=version, logConsole=logConsole)
        self.session = udaExec.connect(method=method, system=system, username=username, password=password, driver=driver, charset=charset, authentication=logmech, port=port)

        ###
        # OTHER POSSIBLE CONFIG OPTIONS
        ###
        # params = general_tools.get_dict_from_file(parameter_file)
        # odbcLibPath = params['odbcLibPath']
        # os.environ['ODBCINI'] = "C:\\Windows\\ODBC.INI"
        # udaExec = teradata.UdaExec(odbcLibPath=odbcLibPath, appName="tdsession", version="1.0", logConsole=True, configFiles=['C:\\Windows\\ODBC.INI'])
        # self.session = udaExec.connect(externalDSN="tdprod_fin")
        ###


    # def query(self, query_str):
    #     result_list = []
    #     for row in self.session.execute(query_str):
    #         result_list.append(row)
    #     return result_list

    # arraysize plays a big role in how long the fetch will take
    # its default was 1, which made pulling millions of rows very slow
    def query(self, query_str, arraysize=500000):
        result_list = []
        with self.session.cursor() as cursor:
            cursor.arraysize = arraysize
            for r, row in enumerate(cursor.execute(query_str)):
                if r % 10000 == 0:
                    print('Fetched: {} of {}'.format(r, cursor.rowcount))
                result_list.append(row)
        return result_list

    def execute(self, dml_str):
        result_list = []
        result = self.session.execute(dml_str)
        return result

    def to_dataframe(self, result_set):
        return pd.DataFrame(result_set, columns=list(result_set[0].columns.keys()))

    # takes query result format and outputs file
    def output(self, query_result=None, df = None, filepath='output', sheet_name='Output_1', xlsx=True, expand=True, index=False):
        if query_result:
            df = self.to_dataframe(query_result)
        if xlsx:
            writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
            df.to_excel(writer, sheet_name=sheet_name, index=index)
            if expand:
                workbook = writer.book
                worksheet = writer.sheets[sheet_name]
                for i, col in enumerate(df.columns):
                    # find length of column i
                    column_len = df[col].astype(str).str.len().max()
                    # Setting the length if the column header is larger
                    # than the max column value length
                    column_len = max(column_len, len(col)) + 2
                    # set the column length
                    worksheet.set_column(i, i, column_len)
                writer.save()

    def close(self):
        result = self.session.close()
        return result


if __name__ == "__main__":
    main()
