import sqlite3
import os
import itertools

cwd = os.path.dirname(os.path.realpath(__file__))
print(cwd)
os.chdir(cwd)

def main():
    session = ProcessedSession(sandbox=True)

class ProcessedSession:
    def __init__(self, database_file, sandbox=False):
        self.database_file = database_file
        self.sandbox = sandbox
        self.create_processed_table()

    def close(self):
        self.conn.close()

    def create_processed_table(self):
        self.conn = sqlite3.connect(self.database_file)
        self.c = self.conn.cursor()
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tbl_processed';")
        if self.c.fetchone() is None:
            self.c.execute("CREATE TABLE tbl_processed (operation_number INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT, transaction_id text, bulk_file text, skipped integer, sandbox integer, action_type text, effectiveDate date, request_body text, header_result text, errors text, subscriptionId text, attempt_time DATETIME DEFAULT CURRENT_TIMESTAMP, result_detail text, success integer, actual_row text, sf_accounts text, zu_subs text, other_metadata text);")

    def check_trans_id_processed(self, transaction_id):
        sandbox_flag = 1 if self.sandbox is True else 0
        self.c.execute("select transaction_id from tbl_processed where transaction_id = ? and sandbox = ? and success = 1;", (transaction_id, sandbox_flag))
        if self.c.fetchone() is None:
            return False
        else:
            return True

    def get_trans_id_processed(self):
        sandbox_flag = 1 if self.sandbox is True else 0
        self.c.execute("select transaction_id from tbl_processed where sandbox = ? and success = 1;", (sandbox_flag,))
        r = self.c.fetchall()
        processed = list(itertools.chain(*r))
        return processed

    def get_unprocessed(self, job_list, transaction_id_field='transaction_id'):
        already_processed = self.get_trans_id_processed()
        new_list = []
        for r in job_list:
            if type(r) is str:
                if r not in already_processed:
                    new_list.append(r)
            elif r[transaction_id_field] not in already_processed:
                new_list.append(r)

        return new_list

    def get_file_results(self):
        self.c.execute("select * from tbl_processed;")
        return self.c.fetchall()

    def get_trans_id_result(self, transaction_id):
        self.c.execute("select * from tbl_processed where transaction_id = ?;", (transaction_id,))
        return self.c.fetchall()

    def log_result(self, transaction_id, sandbox, bulk_file=None, skipped=None, action_type=None, effectiveDate=None, request_body=None, header_result=None, errors=None, subscriptionId=None, attempt_time=None, result_detail=None, success=None, actual_row=None, sf_accounts=None, zu_subs=None, other_metadata=None):
        self.c.execute("INSERT INTO tbl_processed (transaction_id, bulk_file, sandbox, skipped, action_type, effectiveDate, request_body, header_result, errors, subscriptionId, attempt_time, result_detail, success, actual_row, sf_accounts, zu_subs, other_metadata) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (str(transaction_id), str(bulk_file), sandbox, skipped, str(action_type), effectiveDate, str(request_body), str(header_result), str(errors), str(subscriptionId), attempt_time, str(result_detail), success, str(actual_row), str(sf_accounts), str(zu_subs), str(other_metadata)))
        self.conn.commit()


if __name__ == "__main__":
    main()
