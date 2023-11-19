import cmd
import glob
import os
from MyRQL import RelationalDB

from myNoSQL.MyJSONQLParser import MyJSONQLParser
from myNoSQL.MyNoSQL import MyNoSQL

class MyCLI(cmd.Cmd):
    prompt = '(mycli) '
    intro = "Welcome to MyDB! Type ? to list commands."
    
    def __init__(self):
        super().__init__()
        self.current_db = None

    def preloop(self):
        self.select_database()

    def select_database(self):
        self.db_type = input("Which database would you like to use? (relational/json): ").lower()
        if self.db_type == 'relational':
            self.prompt = '(relational) '
            self.db = RelationalDB()
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
        except ValueError as e:
            # delete all tmp files
            tmp_files = glob.glob('rdb/*.tmp')
            for file in tmp_files:
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
    cli.cmdloop()