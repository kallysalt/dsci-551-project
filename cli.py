import cmd
import glob
import os
from MyRDB import MyRDB

from myNoSQL.MyJSONQLParser import MyJSONQLParser
from myNoSQL.MyNoSQL import MyNoSQL

class MyCLI(cmd.Cmd):
    prompt = '(mycli) '
    intro = "Welcome to MyDB! Type ? to list commands."
    
    def __init__(self):
        super().__init__()
        self.current_db = None
        
    def _delete_tmp_files(self):
        pattern = f'rdb/*/*.tmp'
        files = glob.glob(pattern)
        for file in files:
            os.remove(file)

    def preloop(self):
        self.select_database()

    def select_database(self):
        self.db_type = input("Which database would you like to use? (relational/json): ").lower()
        if self.db_type == 'relational':
            self.prompt = '(relational) '
            self.db = MyRDB()
        elif self.db_type == 'json':
            self.prompt = '(json) '
            self.db = MyNoSQL()
            self.parser = MyJSONQLParser(self.db)
        else:
            print("Invalid choice. Please enter 'relational' or 'json'.")
            self.select_database()

    def __execute__(self, command):
        """Execute a command on the selected database."""
        if self.db_type == 'json':
            self.parser.execute(command)
        if self.db_type == 'relational':
            self.db.query(command)

    def do_switch(self, args):
        self.select_database()
        
    def do_query(self, args):
        try:
            if self.current_db:
                self.current_db.query(args)
            else:
                print("Please select a database first.")
        except Exception as e:
            # delete all tmp files
            for file in glob.glob('rdb/*.tmp'):
                os.remove(file)
            # delete all json files
            for file in glob.glob('rdb/*.json'):
                os.remove(file)

    def do_exit(self, args):
        print("Goodbye!")
        return True
    
    def default(self, line):
        """Handle commands using the __execute__ logic."""
        try:
            self.__execute__(line)
        except Exception as e:
            self._delete_tmp_files()
            print(f"Error: {e}")

if __name__ == '__main__':
    cli = MyCLI()
    import pdb; pdb.set_trace()
    cli.cmdloop()
