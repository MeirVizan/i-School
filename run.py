"""from folder app we import the variable app from '__init__' """
from iSchoolApp import create_app

app = create_app()

"""from hare we execute our app """
if __name__ == '__main__':
    app.run(debug=True)


