import cmd
from relational_db import RelationalDB
from json_db import JsonDB

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
            self.current_db = RelationalDB()
        elif self.db_type == 'json':
            self.prompt = '(json) '
            self.current_db = JsonDB()
        else:
            print("Invalid choice. Please enter 'relational' or 'json'.")
            self.select_database()

    def do_switch(self, args):
        self.select_database()
        
    def do_query(self, args):
        try:
            if self.current_db:
                self.current_db.query(args)
            else:
                print("Please select a database first.")
        except ValueError as e:
            print(e)

    def do_exit(self, args):
        print("Goodbye!")
        return True

if __name__ == '__main__':
    cli = MyCLI()
    cli.cmdloop()