import click, pytest, sys
from flask.cli import with_appcontext, AppGroup

from App.database import db, get_migrate
from App.models import User
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize )
from App.controllers.staff import *
from App.controllers.shift import *
from click import DateTime



# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")


def init():
    initialize()
    print('database intialized')

'''

Admin Commands
'''

admin_cli = AppGroup('admin', help='Admin object commands')

@admin_cli.command("create", help="Creates a staff user")
@click.argument("staffname", type=str)
  

def createStaff(staffname):
    new_staff=create_staff(staffname=staffname)
    staffid=new_staff.id
    print(f'{staffname} created!, Your ID is {staffid}')
    return new_staff

@admin_cli.command("c_shift", help="Creates a shift")
@click.argument("day", type=DateTime(formats=["%Y-%m-%d"]))

def createShift( day):
    
    new_shift = create_shift(shift_day=day.date())
    
    day=new_shift.Day
    print(f'Shift created for {day}')
    return new_shift


app.cli.add_command(admin_cli)  


