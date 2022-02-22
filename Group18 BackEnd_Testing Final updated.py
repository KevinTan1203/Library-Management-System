import mysql.connector
import datetime
import sys
import re
import collections
import pymongo
import pandas as pd
import pprint
from pymongo import MongoClient
#from datetime import datetime
import datetime
import time
from tabulate import tabulate
#############################################################################################################################
######################## Connecting to the MongoDB and MysqlServer ##########################################################
myclient = MongoClient("mongodb://127.0.0.1:27017/")
mysqldb = mysql.connector.connect(
    host='localhost', user='root', passwd='KevSQL@1203', db='Library')
mycursor = mysqldb.cursor()

#############################################################################################################################
########################### Collections and Databases #######################################################################
# LibraryUser::Book Collection (Open to Library Admin and Regular User)
mydb_LU = myclient["LibraryUser"]
# This is where users can view the book library and borrow books
myBooks_col = mydb_LU["Books"]

#############################################################################################################################
########################################## Mass Control function ############################################################


def massDelete(table):  # Do note that this mass delete removes everything from a table, but it does not reset the auto-increment value (drop table to reset it)
    mycursor.execute("DELETE FROM " + table)
    mysqldb.commit()
    print('Records updated successfully! Your table is now empty')

#############################################################################################################################
######################## Library and Admin User Creation ####################################################################


# --- Library User ---
LibUser1 = ('test1', 'zifeng', 'a0222369a')
LibUser2 = ('test2', 'yuxian', 'a0217968l')
LibUser3 = ('test3', 'jiaming', 'a0226563a')
LibUser4 = ('test4', 'joel', 'a0218183e')
LibUser5 = ('test5', 'kevin', 'a0218074h')
LibUser6 = ('test6', 'brian', 'a0214272n')

# --- Administrative User ---
adminUser1 = ('Atest1','susan', 'susu123')
adminUser2 = ('Atest2','karen', 'manager1')
adminUser3 = ('Atest3','danielle', 'winnie3')
adminUser4 = ('Atest4','jennie', 'girl123')
adminUser5 = ('Atest5','angela', 'immaxmm')

listOfTuplesLibUsers = [LibUser1, LibUser2, LibUser3, LibUser4, LibUser5]
listOfTuplesAdminUsers = [adminUser1, adminUser2,
                          adminUser3, adminUser4, adminUser5]


def addAdminName(listOfTuples):  # List of tuples containing the admin users name and password
    strg = ""
    count = 0
    for tup in listOfTuples:
        userID, username, pw = tup[0], tup[1], tup[2]
        newTup = (userID,) +  ("ADMIN_" + username,) + (pw,)
        if count == len(listOfTuples) - 1:
            strg += str(newTup)
        else:
            strg += str(newTup) + ", "
        count += 1
    return strg


# List of tuples containing the admin users name and password
def addLibUserName(listOfTuples):
    strg = ""
    count = 0
    for tup in listOfTuples:
        userID, username, pw = tup[0], tup[1], tup[2]
        newTup = (userID,) + (username,) + (pw,)
        if count == len(listOfTuples) - 1:
            strg += str(newTup)
        else:
            strg += str(newTup) + ", "
        count += 1
    return strg


def creatingLibUsers(listOfTuples):
    try:
        mycursor.execute(
            "INSERT into Library.LibraryUser (LibraryUserID, LibraryUserName, Password) VALUES " + addLibUserName(listOfTuples))
        mysqldb.commit()
        print('Records inserted successfully!')
    except:
        mysqldb.rollback()
    mysqldb.close()


def createAdminUsers(listOfTuples):
    try:
        mycursor.execute(
            "INSERT into Library.AdminUser (AdminUserID, AdminUserName, Password) VALUES " + addAdminName(listOfTuples))
        mysqldb.commit()
        print('Records inserted successfully!')
    except:
        mysqldb.rollback()
    mysqldb.close()


def displayLibaryUserRecords():
    try:
        mycursor.execute("SELECT * from Library.LibraryUser")
        result = mycursor.fetchall()
        print(tabulate(result, headers=[
              "LibraryUserID", "LibraryUserName", "Password"]))
    except:
        print('Error: Unable to fetch data.')
    mysqldb.close()


def displayAdminUserRecords():
    try:
        mycursor.execute("SELECT * from Library.AdminUser")
        result = mycursor.fetchall()
        print(tabulate(result, headers=[
              "AdminUserID", "AdminUserName", "Password"]))
    except:
        print('Error: Unable to fetch data.')
    mysqldb.close()

#creatingLibUsers(listOfTuplesLibUsers)
#createAdminUsers(listOfTuplesAdminUsers)
# displayLibaryUserRecords()
# displayAdminUserRecords()


#############################################################################################################################
################################################### Populate the sql books ##################################################
def addBookStrg(listOfTuples):  # List of tuples containing the admin users name and password
    strg, count = "", 0
    for tup in listOfTuples:
        if count == len(listOfTuples) - 1:
            strg += str(tup)
        else:
            strg += str(tup) + ", "
        count += 1
    return strg


def get_cursor_of_book_id(id):
    cursor = myBooks_col.find({"_id": id}, {"_id": 1, "title": 1, "isbn": 1, "pageCount": 1, "publishedDate": 1,
                                            "status": 1, "authors": 1, "categories": 1})
    return cursor


def singleImportImproved(id):
    try:
        cursor = get_cursor_of_book_id(id)
        for cur in cursor:
            colNames = "(BookID, Title, ISBN, PageCount, PublishedDate, Status, Authors, Categories)"
            values = "(%(BookID)s, %(Title)s, %(ISBN)s, %(PageCount)s, %(PublishedDate)s, %(Status)s, %(Authors)s, %(Categories)s)"
            dict_values = {
                'BookID': cur['_id'], 'Title': cur['title'], 'ISBN': cur['isbn'], 'PageCount': cur['pageCount'], 'PublishedDate': cur['publishedDate'],
                'Status': cur['status'], 'Authors': str(cur['authors']), 'Categories': str(cur['categories'])
            }
            sqlQuery = "INSERT INTO Library.Book " + colNames + " VALUES " + values
            mycursor.execute(sqlQuery, dict_values)
            mysqldb.commit()
            print("Successfully imported!")
    except:
        mysqldb.rollback()
        print("Import unsuccessful!")
    mysqldb.close()

# Import the first 10 books
# singleImportImproved(1)
# singleImportImproved(2)
# singleImportImproved(3)
# singleImportImproved(4)
# singleImportImproved(5)
# singleImportImproved(6)
# singleImportImproved(7)
# singleImportImproved(8)
# singleImportImproved(9)
# singleImportImproved(10)


def checkImportableBooks():  # This code is purely for checking purposes. Run to see which books can be imported
    listImportableBooks, listFailedBooks = [], []
    cursor = myBooks_col.find({}, {"_id": 1, "title": 1, "isbn": 1, "pageCount": 1, "publishedDate": 1,
                                   "status": 1, "authors": 1, "categories": 1})
    for cur in cursor:
        try:
            dict_values = {
                'BookID': cur['_id'], 'Title': cur['title'], 'ISBN': cur['isbn'], 'PageCount': cur['pageCount'], 'PublishedDate': cur['publishedDate'],
                'Status': cur['status'], 'Authors': str(cur['authors']), 'Categories': str(cur['categories'])
            }
            listImportableBooks.append(cur['_id'])
        except:
            listFailedBooks.append(cur['_id'])
    print("Importable Books: \n", listImportableBooks)
    print("Unimportable Books: \n", listFailedBooks)
    mysqldb.close()


def multipleImports():
    lst_importable = []
    cursor = myBooks_col.find({}, {"_id": 1, "title": 1, "isbn": 1, "pageCount": 1, "publishedDate": 1,
                                   "status": 1, "authors": 1, "categories": 1})
    for cur in cursor:
        try:
            data = (cur['_id'], cur['title'], cur['isbn'], cur['pageCount'],
                    cur['publishedDate'], cur['status'], str(cur['authors']), str(cur['categories']))
            lst_importable.append(data)
        except:
            continue
    query = '''INSERT INTO Library.Book (BookID, Title, ISBN, PageCount, PublishedDate, Status, Authors, Categories) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
    mycursor.executemany(query, lst_importable)
    mysqldb.commit()
    print("Successfully imported " + str(len(lst_importable)) + " books!")
    mysqldb.close()


#multipleImports()
# checkImportableBooks()


def viewBooks():
    try:
        mycursor.execute(f"SELECT * FROM Library.Book")
        result = mycursor.fetchall()
        print(tabulate(result, headers=[
              "BookID", "Title", "ISBN", "PageCount", "PublishedDate", "Status", "Authors", "Categories"]))
    except:
        mysqldb.rollback()
    mysqldb.close()

# viewBooks()

#############################################################################################################################
################################################### Search Functions ########################################################


def extendingDateTime(datetimeObj):  # this extends the datetime by 1 month
    try:
        dt_obj = datetime.datetime.strptime(str(datetimeObj), '%Y-%m-%d %H:%M:%S.%f')
    except:
        dt_obj = datetime.datetime.strptime(str(datetimeObj), '%Y-%m-%d %H:%M:%S')
    d = datetime.timedelta(days = 28)
    t = dt_obj + d
    return t

def reachMaxLoan(userID):
    mycursor.execute(
        f"SELECT * FROM Library.Reserve br WHERE br.LibraryUserID = '{userID}'")
    return len(mycursor.fetchall()) >= 4


def gotFines(userID):
    mycursor.execute(
        f"SELECT * FROM Library.Fine fn WHERE fn.LibraryUserID = '{userID}'")
    return len(mycursor.fetchall()) >= 1


def get_id(cursor):
    lst_id = []
    for cur in cursor:
        for key, value in cur.items():
            lst_id.append(value)
            break
    return lst_id


def simple_search_id(id):
    cursor = myBooks_col.find({"_id": id}, {"_id": 1, "title": 1, "isbn": 1, "pageCount": 1, "publishedDate": 1,
                                            "status": 1, "authors": 1, "categories": 1})
    return cursor


def simple_search_tuple(keyword):
    cursor = myBooks_col.find({"title": {"$regex": ".*" + keyword + ".*", "$options": 'i'}
                               }, {"_id": 1, "title": 1, "publishedDate": 1})
    return cursor


def emptyCursor(mycursor):
    return len(mycursor.fetchall()) == 0


def retrieveUserID(username):
    mycursor.execute(
        f"SELECT * FROM Library.LibraryUser LU WHERE LU.LibraryUserName = '{username}'")
    cursor = mycursor.fetchall()
    return cursor[0][0]

def removeReserve(username, BookID):
    try:
        mycursor.execute(
            f"SELECT * FROM {booksReservedTable} br WHERE br.LibraryUserID = '{retrieveUserID(username)}' AND br.BookID = '{BookID}'")
        if emptyCursor(mycursor):
            return
        else:
            mycursor.execute(
                f"DELETE FROM Library.Reserve re WHERE re.LibraryUserID = '{retrieveUserID(username)}'")
        mysqldb.commit()
    except:
        mysqldb.rollback()
    mysqldb.close()



def borrowBookImproved(username, keyword):
    # Tables
    booksTable = "Library.Book"
    booksBorrowedTable = "Library.Borrow"
    booksReservedTable = "Library.Reserve"
    libraryUserTable = "Library.LibraryUser"
    # Messages
    notRegisteredMsg = "You are not registered!"
    alreadyReservedMsg = "You have already reserved this book!"
    alreadyBorrowedMsg = "You have already borrowed this book!"
    bookReservedMsg = "Book was already reserved!"
    reservedSuccessMsg = "You have succesfully reserved the book"
    borrowedSuccessMsg = "Book was succesfully borrowed!"
    maxBookMsg = "Maximum number of books reached!!!!"
    existingFinesMsg = "You got existing fines, so you cannot borrow any books!"

    # Datetime values
    timing = datetime.datetime.now()
    # print(timing)

    duedate = extendingDateTime(timing)
    try:
        mycursor.execute(
            f"SELECT * FROM {libraryUserTable} LU WHERE LU.LibraryUserName = '{username}'")
        if emptyCursor(mycursor):
            print(notRegisteredMsg)
        else:
            id = retrieveUserID(username)
            if reachMaxLoan(id):
                print(maxBookMsg)
            elif gotFines(id):
                print(existingFinesMsg)
            else:
                print("Book id list that match your search;\n",
                      get_id(simple_search_tuple(keyword)))
                if len(get_id(simple_search_tuple(keyword))) == 0:
                    print("There are no books that match your search :(")
                else:
                    num = int(input("Select a book ID: "))
                    mycursor.execute(
                        f"SELECT * FROM {booksBorrowedTable} bb WHERE bb.BookID = '{num}'")
                    if emptyCursor(mycursor):
                        dict = list(simple_search_id(num))[0]
                        valueBook = list(dict.values())
                        colNames = "(BookID, LibraryUserID, DueDate)"
                        values = "(%(BookID)s, %(LibraryUserID)s, %(DueDate)s)"
                        dict_values = {
                            'BookID': valueBook[0],
                            'LibraryUserID': retrieveUserID(username),
                            'DueDate': duedate
                        }
                        sqlQuery = "INSERT INTO Library.Borrow " + colNames + " VALUES " + values
                        mycursor.execute(sqlQuery, dict_values)
                        print(borrowedSuccessMsg)
                    else:
                        mycursor.execute(
                            f"SELECT * FROM {booksBorrowedTable} bb WHERE bb.LibraryUserID = '{retrieveUserID(username)}'")
                        if emptyCursor(mycursor) == False:
                            print(alreadyBorrowedMsg)
                        else:
                            mycursor.execute(
                                f"SELECT * FROM {booksReservedTable} br WHERE br.BookID = '{num}'")
                            if emptyCursor(mycursor):
                                colNames = "(BookID, LibraryUserID)"
                                values = "(%(BookID)s, %(LibraryUserID)s)"
                                dict_values = {
                                    'BookID': num,
                                    'LibraryUserID': retrieveUserID(username),
                                }
                                sqlQuery = "INSERT INTO Library.Reserve " + colNames + " VALUES " + values
                                mycursor.execute(sqlQuery, dict_values)
                                print(reservedSuccessMsg)

                            else:
                                mycursor.execute(
                                    f"SELECT * FROM {booksReservedTable} br WHERE br.LibraryUserID = '{retrieveUserID(username)}'")
                                if emptyCursor(mycursor) == False:


                                    mycursor.execute(
                                        f"SELECT * FROM {booksBorrowedTable} br WHERE br.BookID = '{num}'")
                                    if emptyCursor(mycursor):
                                        dict = list(simple_search_id(num))[0]
                                        valueBook = list(dict.values())
                                        colNames = "(BookID, LibraryUserID, DueDate)"
                                        values = "(%(BookID)s, %(LibraryUserID)s, %(DueDate)s)"
                                        dict_values = {
                                            'BookID': valueBook[0],
                                            'LibraryUserID': retrieveUserID(username),
                                            'DueDate': duedate
                                        }
                                        sqlQuery = "INSERT INTO Library.Borrow " + colNames + " VALUES " + values
                                        mycursor.execute(sqlQuery, dict_values)

                                        removeReserve(username, num)
                                        print(borrowedSuccessMsg)
                                    else:
                                        print(alreadyReservedMsg)
                                else:
                                    print(bookReservedMsg)
        mysqldb.commit()
    except:
        mysqldb.rollback()
    mysqldb.close()


#borrowBookImproved('zifeng', 'call')
#borrowBookImproved('yuxian', 'java')
borrowBookImproved('zifeng', 'java')
#borrowBookImproved('kevin', 'java')


def bookSearchImproved(userID, keyword):  # Simple Search
    notRegisteredMsg = "You are not registered!"
    try:
        mycursor.execute(
            f"SELECT * FROM Library.LibraryUser LU WHERE LU.LibraryUserName LIKE '{userID}'")
        if emptyCursor(mycursor):
            print(notRegisteredMsg)
        else:
            cursor = simple_search_tuple(keyword)
            for cur in cursor:
                print(cur)
        mysqldb.commit()
    except:
        mysqldb.rollback()
    mysqldb.close()

#bookSearchImproved("33HRHWONCW19EFSID", 'java')

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Missing Advanced Search!!!!!!
# Verify Please!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#############################################################################################################################
######################################### View Fines, Payment, Borrowed, Reserved ###########################################

# -------------- View borrowed books ------------


def viewAllBorrowed():  # This function is meant for admin users
    try:
        mycursor.execute(f"SELECT * FROM Library.Borrow")
        result = mycursor.fetchall()
        print(tabulate(result, headers=["BookID", "LibraryUserID", "DueDate"]))
    except:
        mysqldb.rollback()
    mysqldb.close()

def viewUserBorrowed(username):  # This function is meant for library users
    try:
        mycursor.execute(
            f"SELECT * FROM Library.Borrow bb WHERE bb.LibraryUserID = '{retrieveUserID(username)}'")
        result = mycursor.fetchall()
        print(tabulate(result, headers=["BookID", "LibraryUserID", "DueDate"]))
    except:
        mysqldb.rollback()
    mysqldb.close()

# -------------- View reserved books ------------


def viewAllReserved():  # This function is meant for admin users
    try:
        mycursor.execute(f"SELECT * FROM Library.Reserve")
        result = mycursor.fetchall()
        print(tabulate(result, headers=["BookID", "LibraryUserID"]))
    except:
        mysqldb.rollback()
    mysqldb.close()


def viewUserReserved(username):  # This function is meant for library users
    try:
        mycursor.execute(
            f"SELECT * FROM Library.Reserve br WHERE br.LibraryUserID = '{retrieveUserID(username)}'")
        result = mycursor.fetchall()
        print(tabulate(result, headers=["BookID", "LibraryUserID"]))
    except:
        mysqldb.rollback()
    mysqldb.close()

# -------------- View users payments ------------


def viewPayments():  # This function is meant for admin users
    try:
        mycursor.execute(f"SELECT * FROM Library.Payment")
        result = mycursor.fetchall()
        print(tabulate(result, headers=[
              "PaymentID", "LibraryUserID", "AmountPaid"]))
    except:
        mysqldb.rollback()
    mysqldb.close()

# -------------- View users fines ------------


def viewFines():  # This function is meant for admin users
    try:
        mycursor.execute(f"SELECT * FROM Library.Fine")
        result = mycursor.fetchall()
        print(tabulate(result, headers=[
              "FineID", "LibraryUserID", "AmountCharged"]))
    except:
        mysqldb.rollback()
    mysqldb.close()


def viewUserFines(username):  # This function is meant for library users
    noFineMsg = "You did not incur any fines"
    try:
        mycursor.execute(
            f"SELECT * FROM Library.Fine fn WHERE fn.LibraryUserID = '{retrieveUserID(username)}'")
        if len(mycursor.fetchall()) == 0:
            print(noFineMsg)
        else:
            mycursor.execute(
                f"SELECT fn.AmountPaid FROM Library.Fine fn WHERE fn.LibraryUserID = '{retrieveUserID(username)}'")
            print("\nYou're currently incurring a fine of $" +
                  str(mycursor.fetchall()[0][0]) + "0")
            print("\n")
            mycursor.execute(
                f"SELECT * FROM Library.Fine fn WHERE fn.LibraryUserID = '{retrieveUserID(username)}'")
            result = mycursor.fetchall()
            print(tabulate(result, headers=["LibraryUserID", "AmountCharged"]))
    except:
        mysqldb.rollback()
    mysqldb.close()


#############################################################################################################################
############################################# Extend, Return a book #########################################################
def extendBook(username, bookID):
    noBookMsg = "You did not borrow this book!"
    notRegisteredMsg = "You are not registered!"
    try:
        mycursor.execute(
            f"SELECT * FROM Library.LibraryUser LU WHERE LU.LibraryUserName LIKE '{username}'")
        if emptyCursor(mycursor):
            print(notRegisteredMsg)
        else:
            mycursor.execute(
                f"SELECT * FROM Library.Borrow bb WHERE bb.BookID = '{bookID}' AND bb.LibraryUserID = '{retrieveUserID(username)}'")
            if len(mycursor.fetchall()) == 0:
                print(noBookMsg)
            else:

                mycursor.execute(
                    f"SELECT * FROM Library.Borrow bb WHERE bb.BookID = '{bookID}' AND bb.LibraryUserID = '{retrieveUserID(username)}'")
                duedate = mycursor.fetchall()[0][2]

                newDate = extendingDateTime(duedate)
                mycursor.execute(
                    f"UPDATE Library.Borrow bb SET bb.DueDate = '{newDate.date()}' WHERE bb.BookID = '{bookID}'")
                print("Book was succesfully extended!")
        mysqldb.commit()
    except:
        mysqldb.rollback()
    mysqldb.close()

#extendBook('zifeng', 8)
#extendBook('zifeng', 255)


def returnBook(username, bookID):
    currentTime = datetime.datetime.now()
    noBookMsg = "You did not borrow that book!"
    notRegisteredMsg = "You are not registered!"
    try:
        mycursor.execute(
            f"SELECT * FROM Library.LibraryUser LU WHERE LU.LibraryUserName LIKE '{username}'")
        if emptyCursor(mycursor):
            print(notRegisteredMsg)
        else:
            mycursor.execute(
                f"SELECT * FROM Library.Borrow bb WHERE bb.LibraryUserID = '{retrieveUserID(username)}' AND bb.BookID = '{bookID}'")
            if len(mycursor.fetchall()) == 0:
                print(noBookMsg)
            else:
                mycursor.execute(
                    f"SELECT * FROM Library.Borrow bb WHERE bb.LibraryUserID = '{retrieveUserID(username)}'")
                date = mycursor.fetchall()[0][2]
                if currentTime > date:
                    datediff = (currentTime - date)
                    amtcharged = datediff.days * 1.00
                    print("You've incurred a fine for late return")
                    mycursor.execute(
                        f"INSERT INTO Library.Fine (LibraryUserID, AmountCharged) VALUES ('{retrieveUserID(username)}', '{amtcharged}')")
                mycursor.execute(
                    f"DELETE FROM Library.Borrow bb WHERE bb.BookID = '{bookID}'")
                print("Book was succesfully returned!")
        mysqldb.commit()
    except:
        mysqldb.rollback()
    mysqldb.close()


#returnBook("yuxian", 8)
#returnBook("zifeng", 8)
#returnBook("10PWPIEFRN75OTENV", 700)
