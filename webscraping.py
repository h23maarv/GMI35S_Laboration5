"""
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import json
import time


try:
    current_datetime = datetime.now().strftime("%Y%m%d")
    book_file = f"books_{current_datetime}.json"

    with open(book_file, 'r') as file:
        books = json.load(file)
except FileNotFoundError:
    books = []
except json.decoder.JSONDecodeError:
    books = []


def get_books_page1():
    response_obj = requests.get("https://books.toscrape.com/")
    response = response_obj.text

    if response_obj.status_code == 200:
        print("Request successful")

        soup = BeautifulSoup(response, 'html.parser')
        title = soup.find('title')
        print(title.text)

        books_data = []
        books = soup.find_all("article", class_="product_pod")

        for book in books:
            title = book.h3.a["title"]
            price = book.find("p", class_="price_color").get_text().strip()
            rating = book.p["class"][1]
            stock = book.find("p", class_="instock availability").get_text().strip()

            book_info = {
            "Title": title,
            "Price": price,
            "Rating": rating,
            "availability": stock
            }

            books_data.append(book_info)

        with open(book_file, 'w') as file:
            json.dump(books_data, file, indent=2)

        for book in books_data:
            print(f"Title: {book['Title']}")
            print(f"Price: {book['Price']}")
            print(f"Rating: {book['Rating']}")
            print(f"availability: {book['availability']}\n")

    else:
        print("Request failed")

    return books_data
#get_books_page1()

def get_all_books():

    books_data = []
    total_time = 0

    for page_num in range(1, 51):
        response_obj = requests.get(f"https://books.toscrape.com/catalogue/page-{page_num}.html")
        response = response_obj.text

        if response_obj.status_code == 200:
            print("Request successful for page", page_num)
            
            soup = BeautifulSoup(response, 'html.parser')
            books = soup.find_all('h3')
            start_time = time.time()
            books_extracted = 0

            for book in books:
                book_url = book.find('a')['href']
                book_response = requests.get('https://books.toscrape.com/catalogue/' + book_url)
                book_soup = BeautifulSoup(book_response.content, 'html.parser')

                title = book_soup.find('h1').text
                category = book_soup.find('ul', class_="breadcrumb").find_all('a')[2].text.strip()
                rating = book_soup.find('p', class_='star-rating')['class'][1]
                price = book_soup.find('p', class_='price_color').text.strip()
                availability = book_soup.find('p', class_='availability').text.strip()

                end_time = time.time()
                total_time += (end_time-start_time)/60.0

                book_info = {
                "Title": title,
                "category": category,
                "Price": price,
                "Rating": rating,
                "Available": availability
                }

                books_data.append(book_info)
                books_extracted += 1

        else:
            print("Request failed for page", page_num)
            continue

        with open(book_file, 'w') as file:
            json.dump(books_data, file, indent=2)

        print(books_data)
        print('*******')
        print(f'Total time taken: {total_time:.2f} secounds')
        print('*******')
        print(f'{page_num * len(books)} books extracted so far...')

    all_books = get_all_books()
    print("Total number of books extracted:", len(all_books))

    return books_data
#get_all_books()


def get_book_category():

    response = requests.get("http://books.toscrape.com/index.html")
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', href=True)
    print(links)

    books = fetch_books()
    category_books = [book for book in books if book['category'] == category]
    today_date = datetime.datetime.now().strftime("%Y%m%d")
    new_filename = f"{category}_{today_date}.json"
    with open(new_filename, 'w') as file:
        json.dump(category_books, file, indent=4)
    return jsonify(category_books)

#get_book_category()
"""

from flask import Blueprint, jsonify, request
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import json
import time

RuffelBok_app = Blueprint("RuffelBok_app", __name__)

try:
    current_datetime = datetime.now().strftime("%Y%m%d")
    book_file = f"books_{current_datetime}.json"

    with open(book_file, 'r') as file:
        books = json.load(file)
except FileNotFoundError:
    books = []
except json.decoder.JSONDecodeError:
    books = []

@RuffelBok_app.route('/', methods=['GET'])
def get_all_books():

    books_data = []
    total_time = 0

    for page_num in range(1, 51):
        response_obj = requests.get(f"https://books.toscrape.com/catalogue/page-{page_num}.html")
        response = response_obj.text

        if response_obj.status_code == 200:
            print("Request successful for page", page_num)

            soup = BeautifulSoup(response, 'html.parser')
            books = soup.find_all('h3')
            start_time = time.time()
            books_extracted = 0

            for book in books:
                book_url = book.find('a')['href']
                book_response = requests.get('https://books.toscrape.com/catalogue/' + book_url)
                book_soup = BeautifulSoup(book_response.content, 'html.parser')

                title = book_soup.find('h1').text
                category = book_soup.find('ul', class_="breadcrumb").find_all('a')[2].text.strip()
                rating = book_soup.find('p', class_='star-rating')['class'][1]
                price = book_soup.find('p', class_='price_color').text.strip()
                availability = book_soup.find('p', class_='availability').text.strip()

                end_time = time.time()
                total_time += (end_time-start_time)/60.0

                book_info = {
                "Title": title,
                "Category": category,
                "Price": price,
                "Rating": rating,
                "Available": availability
                }

                books_data.append(book_info)
                books_extracted += 1
                break

        else:
            print("Request failed for page", page_num)
            continue

        with open(book_file, 'w') as file:
            json.dump(books_data, file, indent=2)

        print(books_data)
        print('*******')
        print(f'Total time taken: {total_time:.2f} secounds')
        print('*******')
        print(f'{page_num * len(books)} books extracted so far...')

    all_books = get_all_books()
    print("Total number of books extracted:", len(all_books))

    return books_data

get_all_books()



@RuffelBok_app.route('/<category>', methods=['GET'])
def get_book_category(category):
    books = get_all_books()
    category_books = [book for book in books if book['category'] == category]
    try:
        file_category = f"{category}_{current_datetime}.json"
        with open(book_file, 'r') as file:
            books = json.load(file)
    except FileNotFoundError:
        books = []
    except json.decoder.JSONDecodeError:
        books = []
    with open(file_category, 'w') as file:
            json.dump(category_books, file, indent=2)
    return jsonify(category_books)


@RuffelBok_app.route('/<title>', methods=['DELETE'])
def delete_book(title):

    for book in books:
        if book['title'] == title:
            books.remove(book)
            with open(book_file, 'w') as file:
                json.dump(books, file, indent=2)
            return jsonify({'message': 'Book deleted successfully!'})

    return jsonify({'error': 'Book not found!'}), 404


@RuffelBok_app.route('/<title>', methods=['PUT'])
def update_book(title):
    title = request.json['title']
    category = request.json['category']
    rating = request.json['rating']
    price = request.json['price']
    availability = request.json['availability']

    for book in books:
        if book['title'] == title:
            book['category'] = category
            book['rating'] = rating
            book['price'] = price
            book['availability'] = availability
            with open(book_file, 'w') as file:
                json.dump(books, file, indent=2)
            return jsonify({'message': 'Book updated successfully!'})

    return jsonify({'error': 'Book not found!'}), 404


@RuffelBok_app.route('/', methods=['POST'])
def add_book():
    title = request.json['title']
    category = request.json['category']
    rating = request.json['rating']
    price = request.json['price']
    availability = request.json['availability']
    
    for book in books:
        if book['title'] == title:
            return jsonify({'error': 'Book already exists!'}), 400

    new_book = {'title': title, 'category': category, 'rating': rating, 'price': price, 'availability': availability}
    books.append(new_book)

    with open(book_file, 'w') as file:
        json.dump(books, file,indent=2)

    return jsonify({'message': 'Book added successfully!'}), 201

if __name__ == '__main__':
    RuffelBok_app.run(debug=True)