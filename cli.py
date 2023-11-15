import cmd

from myNoSQL.MyJSONQLParser import MyJSONQLParser
from myNoSQL.MyNoSQL import MyNoSQL

class MyCLI(cmd.Cmd):
    prompt = '(mycli) '
    intro = "Welcome to MyDB! Type ? to list commands."

    def preloop(self):
        self.select_database()

    def select_database(self):
        self.db_type = input("Which database would you like to use? (relational/json): ").lower()
        if self.db_type == 'relational':
            self.prompt = '(relational) '
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

    def do_switch(self, args):
        """Switch between databases."""
        self.select_database()

    def do_exit(self, args):
        """Exit the CLI."""
        print("Goodbye!")
        return True
    
    def default(self, line):
        """Handle commands using the __execute__ logic."""
        try:
            self.__execute__(line)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    cli = MyCLI()
    cli.cmdloop()
