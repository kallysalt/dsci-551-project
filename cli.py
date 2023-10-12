import cmd

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
        else:
            print("Invalid choice. Please enter 'relational' or 'json'.")
            self.select_database()

    def do_switch(self, args):
        """Switch between databases."""
        self.select_database()

    def do_exit(self, args):
        """Exit the CLI."""
        print("Goodbye!")
        return True

if __name__ == '__main__':
    cli = MyCLI()
    cli.cmdloop()
