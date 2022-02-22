from library_system.models import User
from django.contrib.auth.models import User, auth
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Book
from pymongo import MongoClient
import datetime

from library_system.forms import UserForm
from library_system.models import User

import mysql.connector as mcdb

# Establish a connection with mongo instance.
myclient = MongoClient("mongodb://127.0.0.1:27017/")
books_collection = myclient["Library"]["Books"]

# Connecting with MySQL instance
mysqldb = mcdb.connect(
    host='localhost', user='root', passwd='password', db='Library')
mycursor = mysqldb.cursor()

current_userid = None
current_username = None
account_type = None

# Create your views here.


def home(request):
    return render(request, 'home.html', {'name': current_username})


def register(request):
    if request.method == "POST":
        user_name = request.POST["user_username"]
        user_id = request.POST["login_username"]
        user_password = request.POST["login_password"]
        mycursor.execute(
            f"SELECT * FROM LibraryUser u WHERE u.LibraryUserID = '{user_id}'")
        if len(mycursor.fetchall()) > 0:
            message = 'Unable to create account with that username. Please try again.'
            return render(request, 'sign_up.html', {'message': message})
        try:
            mycursor.execute(
                f"INSERT INTO LibraryUser (LibraryUserID, LibraryUserName, Password) VALUES ('{user_id}', '{user_name}', '{user_password}')")
            mysqldb.commit()
            message = 'Account successfully registered! Please sign in.'
        except:
            mysqldb.rollback()
        return render(request, 'home.html', {'message': message})
    else:
        return render(request, 'sign_up.html')


def login(request):
    if request.method == "POST":
        account_username = request.POST["login_username"]
        account_password = request.POST["login_password"]
        global current_userid
        global current_username
        global account_type
        current_userid = account_username
        account_type = "library user"
        mycursor.execute(
            f"SELECT * FROM LibraryUser lu WHERE lu.LibraryUserID = '{account_username}' AND lu.Password = '{account_password}'")
        if len(mycursor.fetchall()) == 0:
            mycursor.execute(
                f"SELECT * FROM AdminUser au WHERE au.AdminUserID = '{account_username}' AND au.Password = '{account_password}'")
            account_type = "admin user"
            if len(mycursor.fetchall()) == 0:
                message = "Incorrect login credentials"
                return render(request, 'home.html', {'message': message})
            else:
                mycursor.execute(
                    f"SELECT * FROM AdminUser au WHERE au.AdminUserID = '{account_username}' AND au.Password = '{account_password}'")
                current_username = mycursor.fetchall()[0][1]
        else:
            mycursor.execute(
                f"SELECT * FROM LibraryUser lu WHERE lu.LibraryUserID = '{account_username}' AND lu.Password = '{account_password}'")
            current_username = mycursor.fetchall()[0][1]
        return render(request, 'welcome.html', {'current_user': current_username})


def sign_up(request):
    message = "Create an account with us!"
    return render(request, 'sign_up.html', {'message': message})


def index(request):
    results = books_collection
    return render(request, "search_result.html", {'results': results})


def main(request):
    return render(request, 'main.html', {'current_user': current_username})


def borrow_book(request):
    return render(request, 'borrow.html')


def return_book(request):
    return render(request, 'return.html')


def reserve_book(request):
    return render(request, 'reserve.html')


def search(request):
    return render(request, 'search.html')


def advanced_search(request):
    return render(request, 'advanced_search.html')


def fines_and_payments(request):
    if account_type == "admin user":
        return render(request, 'admin_fines_and_payments.html')
    return render(request, 'fines_and_payments.html')


def admin_fines_and_payments(request):
    return render(request, 'admin_fines_and_payments.html')


def admin_borrow_and_return(request):
    return render(request, 'admin_borrow_and_return.html')

# -------------- View all borrowed books -------------


def admin_borrowing(request):
    try:
        mycursor.execute(
            f"SELECT bb.BookID, bb.LibraryUserID, bk.title, bb.DueDate FROM Library.Borrow bb INNER JOIN Library.Book bk USING (BookID)")
        result = mycursor.fetchall()
    except:
        mysqldb.rollback()
    return render(request, 'admin_borrowing.html', {'result': result})


# -------------- View all reserved books -------------


def admin_reservation(request):
    try:
        mycursor.execute(
            f"SELECT br.BookID, br.LibraryUserID, bk.title FROM Library.Reserve br INNER JOIN Library.Book bk USING (BookID)")
        result = mycursor.fetchall()
    except:
        mysqldb.rollback()
    return render(request, 'admin_reservation.html', {'result': result})


# -------------- View all payments ------------


def admin_payments(request):
    try:
        mycursor.execute(
            f"SELECT * FROM Library.payment")
        result = mycursor.fetchall()
    except:
        mysqldb.rollback()
    return render(request, 'admin_payments.html', {'result': result})

# -------------- View all outstanding fines ------------


def admin_fines(request):
    try:
        mycursor.execute(
            f"SELECT * FROM Library.Fine")
        result = mycursor.fetchall()
    except:
        mysqldb.rollback()
    return render(request, 'admin_fines.html', {'result': result})


def search_result(request):
    search_words = request.GET["keywords"]
    search_results = books_collection.find(
        {"title": {"$regex": ".*" + search_words + ".*", "$options": 'i'}})
    results = list(map(lambda x: ([x["_id"], x["title"], str(x["authors"])[
        1:-1], str(x["categories"])[1:-1], x.get("publishedDate").year if x.get("publishedDate") != None else None]), search_results))
    return render(request, 'search_result.html', {'words': search_words, 'results': results})


def advanced_search_result(request):
    search_words = request.GET["keywords"]
    search_author = request.GET["author"]
    search_category = request.GET["category"]
    search_publisher = request.GET["publisher"]
    search_publication_year = request.GET["publication_year"]
    if search_words != None:
        search_results = books_collection.find(
            {"title": {"$regex": ".*" + search_words + ".*", "$options": 'i'}})
    else:
        search_results = books_collection.find()
    if search_author != None:
        search_results = filter(lambda x: substring_present(
            search_author, x["authors"]), search_results)
    if search_category != None:
        search_results = filter(lambda x: substring_present(
            search_category, x["categories"]), search_results)
    if search_publisher != None:
        search_results = filter(lambda x: substring_present(
            search_publisher, x["status"]), search_results)
    if search_publication_year != None and search_publication_year != "":
        search_results = filter(lambda x: int(x.get("publishedDate").year) == int(
            search_publication_year) if x.get("publishedDate") != None else False, search_results)
    results = list(map(lambda x: ([x["_id"], x["title"], str(x["authors"])[
        1:-1], str(x["categories"])[1:-1], x.get("publishedDate").year if x.get("publishedDate") != None else None]), search_results))
    return render(request, 'advanced_search_result.html', {'search_words': search_words, 'search_author': search_author, 'search_category': search_category, 'search_publisher': search_publisher, 'search_publication_year': search_publication_year, 'results': results})


def fines(request):
    try:
        result = "You have no existing fines"
        mycursor.execute(
            f"SELECT fn.AmountCharged FROM Library.Fine fn WHERE fn.LibraryUserID = '{current_userid}'")
        if len(mycursor.fetchall()) != 0:
            mycursor.execute(
                f"SELECT fn.AmountCharged FROM Library.Fine fn WHERE fn.LibraryUserID = '{current_userid}'")
            result = "$" + str(mycursor.fetchall()[0][0]) + str(0)
    except:
        mysqldb.rollback()
    return render(request, 'fines.html', {'outstanding_fines': result})


def payments(request):
    try:
        mycursor.execute(
            f"SELECT pm.PaymentID, pm.AmountPaid, pm.DateOfPayment, pm.PaymentType FROM Library.Payment pm WHERE pm.LibraryUserID = '{current_userid}'")
        result = mycursor.fetchall()
    except:
        mysqldb.rollback()
    return render(request, 'payments.html', {'previous_payments': result})


def borrow_and_return(request):
    if account_type == "admin user":
        return render(request, 'admin_borrow_and_return.html')
    return render(request, 'borrow_and_return.html')


def borrowing(request):
    try:
        mycursor.execute(
            f"SELECT bb.BookID, bk.title, bb.DueDate FROM Library.Borrow bb INNER JOIN Library.Book bk USING (BookID) WHERE bb.LibraryUserID = '{current_userid}'")
        result1 = mycursor.fetchall()
        mycursor.execute(
            f"SELECT br.BookID, bk.Title, bb.libraryUserID AS borrower FROM Library.Reserve br  LEFT JOIN Library.borrow bb  USING (BookID) INNER JOIN Library.Book bk  USING (BookID)  WHERE br.LibraryUserID = '{current_userid}' AND bb.libraryUserID IS NULL;")
        result2 = mycursor.fetchall()
        mycursor.execute(
            f"SELECT br.BookID, bk.Title FROM Library.Reserve br RIGHT JOIN Library.borrow bb USING (BookID) INNER JOIN Library.Book bk  USING (BookID)  WHERE br.LibraryUserID = '{current_userid}'")
        result3 = mycursor.fetchall()
    except:
        mysqldb.rollback()
    return render(request, 'borrowing.html', {'current_borrowing': result1, 'available_reservation': result2, 'unavailable_reservation': result3})


def returning(request):
    try:
        mycursor.execute(
            f"SELECT bb.BookID, bk.title, bb.DueDate FROM Library.Borrow bb INNER JOIN Library.Book bk USING (BookID) WHERE bb.LibraryUserID = '{current_userid}'")
        result1 = mycursor.fetchall()
        mycursor.execute(
            f"SELECT br.BookID, bk.title FROM Library.Reserve br INNER JOIN Library.Book bk USING (BookID) WHERE br.LibraryUserID = '{current_userid}'")
        result2 = mycursor.fetchall()
    except:
        mysqldb.rollback()
    return render(request, 'returning.html', {'current_borrowing': result1, 'current_reservation': result2})


# -------------- Borrowing / Reserving book --------------


def borrowed(request):
    book_id = request.GET["book_id"]
    current_dt = datetime.datetime.now()
    due_date = extendingDateTime(current_dt)
    message = ""
    try:
        if reachMaxLoan(current_userid):
            message = "You have reached the maximum number of books borrowed"
            return render(request, 'transaction.html', {'current_user': current_username, 'message': message})
        elif gotFines(current_userid):
            message = "You have outstanding fines unpaid, so you cannot borrow any books!"
            return render(request, 'transaction.html', {'current_user': current_username, 'message': message})
        mycursor.execute(
            f"SELECT * FROM Library.Borrow bb WHERE bb.BookID = '{book_id}' AND bb.LibraryUserID = '{current_userid}'")
        if len(mycursor.fetchall()) != 0:
            message = "You are already borrowing this book."
            return render(request, 'transaction.html', {'current_user': current_username, 'message': message})
        mycursor.execute(
            f"SELECT * FROM Library.Reserve br WHERE br.BookID = '{book_id}' AND br.LibraryUserID = '{current_userid}'")
        if len(mycursor.fetchall()) != 0:
            message = "You have already reserved this book."
            return render(request, 'transaction.html', {'current_user': current_username, 'message': message})
        mycursor.execute(
            f"SELECT * FROM Library.Book bk WHERE bk.BookID = '{book_id}'")
        if len(mycursor.fetchall()) == 0:
            message = "Unfortunately, there is no such book."
        else:
            mycursor.execute(
                f"SELECT * FROM Library.Borrow bb WHERE bb.BookID = '{book_id}'")
            if len(mycursor.fetchall()) == 0:
                mycursor.execute(
                    f"INSERT INTO Library.Borrow VALUES ('{book_id}', '{current_userid}', '{due_date}')")
                message = "You have succesfully borrowed the book!"
            else:
                mycursor.execute(
                    f"SELECT * FROM Library.Reserve br WHERE br.BookID = '{book_id}'")
                if len(mycursor.fetchall()) == 0:
                    mycursor.execute(
                        f"INSERT INTO Library.Reserve VALUES ('{book_id}', '{current_userid}')")
                    message = "Unfortunately, the book has already been borrowed. We have reserved the book for you."
                else:
                    message = "Unfortunately, the book is currently borrowed and reserved by someone else!"
        mysqldb.commit()
    except:
        mysqldb.rollback()
    return render(request, 'transaction.html', {'current_user': current_username, 'message': message})


# -------------- Returning book --------------
def returned(request):
    book_id = request.GET["book_id"]
    current_dt = datetime.datetime.now()
    message = ""
    try:
        mycursor.execute(
            f"SELECT * FROM Library.Borrow bb WHERE bb.LibraryUserID = '{current_userid}' AND bb.BookID = '{book_id}'")
        if len(mycursor.fetchall()) == 0:
            message = "You did not borrow that book."
        else:
            mycursor.execute(
                f"SELECT * FROM Library.Borrow bb WHERE bb.LibraryUserID = '{current_userid}' AND bb.BookID = '{book_id}'")
            date = mycursor.fetchall()[0][2]
            if current_dt > date:
                datediff = (current_dt - date)
                amtcharged = datediff.days * 1.00
                message = "You've incurred a $" + \
                    str(amtcharged) + " fine for late return. Please refer to fines and payments management for total fines incurred. All book reservations are cancelled."
                mycursor.execute(
                    f"SELECT AmountCharged FROM Library.Fine bb WHERE bb.LibraryUserID = '{current_userid}'")
                if len(mycursor.fetchall()) != 0:
                    amount = mycursor.fetchall()[0][1]
                    mycursor.execute(
                        f"UPDATE Library.Fine fn SET AmountCharged = '{amtcharged + amount}' WHERE LibraryUserID = '{current_userid}'")
                else:
                    mycursor.execute(
                        f"INSERT INTO Library.Fine VALUES ('{current_userid}', '{amtcharged}')")
                mycursor.execute(
                    f"DELETE FROM Library.Reserve br WHERE br.LibraryUserID = '{current_userid}'")
            mycursor.execute(
                f"DELETE FROM Library.Borrow bb WHERE bb.BookID = '{book_id}'")
            message = "Your book was succesfully returned!"
        mysqldb.commit()
    except:
        mysqldb.rollback()
    return render(request, 'transaction.html', {'current_user': current_username, 'message': message})

# -------------- Pay fines --------------


def payfine_credit(request):
    message = ""
    try:
        mycursor.execute(
            f"SELECT * FROM Library.Fine fn WHERE fn.LibraryUserID = '{current_userid}'")
        cursor = mycursor.fetchall()
        if len(cursor) == 0:
            message = "You do not any existing fines."
        else:
            try:
                amt = cursor[0][1]
                date = datetime.datetime.now()
                mycursor.execute(
                    f"INSERT INTO Library.Payment(LibraryUserID, AmountPaid, DateofPayment, PaymentType) VALUES ('{current_userid}', '{amt}', '{date}', 'Credit')")
                mycursor.execute(
                    f"DELETE FROM Library.Fine fn WHERE fn.LibraryUserID = '{current_userid}'")
                message = "You have succesfully paid your fine by credit"
            except:
                message = "Error. Payment was unsuccessful."
            mysqldb.commit()
    except:
        mysqldb.rollback()
    return render(request, 'transaction.html', {'current_user': current_username, 'message': message})


def payfine_debit(request):
    message = ""
    try:
        mycursor.execute(
            f"SELECT * FROM Library.Fine fn WHERE fn.LibraryUserID = '{current_userid}'")
        cursor = mycursor.fetchall()
        if len(cursor) == 0:
            message = "You do not any existing fines."
        else:
            try:
                amt = cursor[0][1]
                date = datetime.datetime.now()
                mycursor.execute(
                    f"INSERT INTO Library.Payment(LibraryUserID, AmountPaid, DateOfPayment, PaymentType) VALUES ('{current_userid}', '{amt}', '{date}', 'Debit')")
                mycursor.execute(
                    f"DELETE FROM Library.Fine fn WHERE fn.LibraryUserID = '{current_userid}'")
                message = "You have succesfully paid your fine by debit"
            except:
                message = "Error. Payment was unsuccessful."
            mysqldb.commit()
    except:
        mysqldb.rollback()
    return render(request, 'transaction.html', {'current_user': current_username, 'message': message})

# -------------- Extend due date --------------


def extended(request):
    book_id = request.GET["book_id"]
    message = ""
    try:
        if gotFines(current_userid):
            message = "You have outstanding fines unpaid, so you cannot extend any borrowings!"
            return render(request, 'transaction.html', {'current_user': current_username, 'message': message})
        mycursor.execute(
            f"SELECT * FROM Library.Borrow bb WHERE bb.BookID = '{book_id}' AND bb.LibraryUserID = '{current_userid}'")
        if len(mycursor.fetchall()) == 0:
            message = "You did not borrow this book"
        else:
            mycursor.execute(
                f"SELECT * FROM Library.Reserve br WHERE br.BookID = '{book_id}'")
            if len(mycursor.fetchall()) != 0:
                message = "A user has currently reserved this book. You may not extend borrowing of this book."
            else:
                mycursor.execute(
                    f"SELECT * FROM Library.Borrow bb WHERE bb.BookID = '{book_id}' AND bb.LibraryUserID = '{current_userid}'")
                duedate = mycursor.fetchall()[0][2]
                newDate = extendingDateTime(duedate)
                mycursor.execute(
                    f"UPDATE Library.Borrow bb SET bb.DueDate = '{newDate.date()}' WHERE bb.BookID = '{book_id}'")
                message = "Book borrowing was succesfully extended!"
        mysqldb.commit()
    except:
        mysqldb.rollback()
    return render(request, 'transaction.html', {'current_user': current_username, 'message': message})

# -------------- Cancel Reservation ------------


def cancelled(request):
    book_id = request.GET["book_id"]
    message = ""
    try:
        mycursor.execute(
            f"SELECT * FROM Library.Reserve br WHERE br.LibraryUserID = '{current_userid}' AND br.BookID = '{book_id}'")
        if len(mycursor.fetchall()) == 0:
            message = "You did not reserve this book!"
        else:
            mycursor.execute(
                f"DELETE FROM Library.Reserve br WHERE br.BookID = '{book_id}'")
            message = "Book reservation has been successfully cancelled!"
        mysqldb.commit()
    except:
        mysqldb.rollback()
    return render(request, 'transaction.html', {'current_user': current_username, 'message': message})


def reachMaxLoan(userID):
    mycursor.execute(
        f"SELECT * FROM Library.Borrow bb WHERE bb.LibraryUserID = '{userID}'")
    return len(mycursor.fetchall()) >= 4


def gotFines(userID):
    mycursor.execute(
        f"SELECT * FROM Library.Fine fn WHERE fn.LibraryUserID = '{userID}'")
    cursor = mycursor.fetchall()
    return len(cursor) >= 1


def retrieveUserID(username):
    mycursor.execute(
        f"SELECT * FROM Library.LibraryUser LU WHERE LU.LibraryUserName = '{username}'")
    cursor = mycursor.fetchall()
    return cursor[0][0]


def substring_present(word, lst):
    for i in lst:
        if word.lower() in i.lower():
            return True
    return False


def extendingDateTime(datetimeObj):  # this extends the datetime by 1 month
    try:
        dt_obj = datetime.datetime.strptime(
            str(datetimeObj), '%Y-%m-%d %H:%M:%S.%f')
    except:
        dt_obj = datetime.datetime.strptime(
            str(datetimeObj), '%Y-%m-%d %H:%M:%S')
    d = datetime.timedelta(days=28)
    t = dt_obj + d
    return t
