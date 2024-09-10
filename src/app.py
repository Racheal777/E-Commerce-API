from crypt import methods

from . import create_app

app = create_app()

@app.route('/order', methods = ['POST'])
def order():
    return 'hello'


if __name__ == '__main__':
    app.run()

