from http.server import BaseHTTPRequestHandler,HTTPServer, SimpleHTTPRequestHandler
import re
import mysql.connector
import json

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="admin",
  database='books'
)

def create_book(row):
    if 'isbn' in row.keys():
        return Book(str(row['title']), str(row['author']), float(row['price']), row['isbn'])
    return Book(str(row['title']), str(row['author']), float(row['price']))


class Book:
    def __init__(self, title, author, price, isbn=None):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.price = price

class GetHandler(SimpleHTTPRequestHandler):

        def do_GET(self):
            if self.path == '/books':
                mycursor = mydb.cursor(dictionary=True)
                mycursor.execute("SELECT * FROM books")
                rows = mycursor.fetchall()
                result = json.dumps(list(map(lambda row: create_book(row).__dict__, rows)))

            if re.search("/books/[0-9]+", self.path):
                mycursor = mydb.cursor(dictionary=True)
                sql = "SELECT * FROM books WHERE isbn = %s"
                mycursor.execute(sql, (self.path.split('/')[-1], ))
                row = mycursor.fetchone()
                if (row):
                    result = json.dumps(create_book(row).__dict__)
                else: 
                    self.send_response(404)
                    self.end_headers()
                    return
                

                print('getting book with id ' + self.path.split('/')[-1])

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(result)

        def do_POST(self):
            if self.path == '/books':
                print('creating book')
                book = create_book(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
                mycursor = mydb.cursor()

                sql = "INSERT INTO books (title, author, price) VALUES (%s, %s, %s)"
                val = (book.title, book.author, book.price)
                mycursor.execute(sql, val)
                mydb.commit()
                self.send_response(201)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

        def do_DELETE(self):
            if re.search("/books/[0-9]+", self.path):
                sql = "DELETE FROM books where isbn = %s"
                mycursor = mydb.cursor()
                mycursor.execute(sql, (self.path.split('/')[-1], ))
                mydb.commit()
                print('deleting book with id ' + self.path.split('/')[-1])
                self.send_response(204)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                return

        def do_PUT(self):
            if re.search("/books/[0-9]+", self.path):
                book = create_book(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
                mycursor = mydb.cursor()
                sql = "UPDATE books SET title = %s, author = %s, price = %s WHERE isbn = %s"
                val = (book.title, book.author, book.price, self.path.split('/')[-1]) 
                mycursor.execute(sql, val)
                mydb.commit()
                self.send_response(204)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                print('replacing book with id ' + self.path.split('/')[-1])        
                
        def do_PATCH(self):
            if re.search("/books/[0-9]+", self.path):
                print('updating book with id ' + self.path.split('/')[-1])


Handler=GetHandler
try:
    httpd=HTTPServer(("localhost", 8080), Handler)
    httpd.serve_forever()
except KeyboardInterrupt:
    print("exiting")
    exit()