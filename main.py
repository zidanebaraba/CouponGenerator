import pymysql
from app import app
from config import mysql
from flask import jsonify
from flask import flash, request, render_template
from GenerateVoucher import create_coupon
import pandas as pd


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def create():
    num = request.form['generate']
    print(num)
    create_coupon(num)
    return "Success"


@app.route('/refresh')
def refresh():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("UPDATE tbl_voucher v  "
                       "SET     v.status =  CASE  "
                       "WHEN v.status = 2 AND v.expiration >= CURDATE()  THEN 2 "
                       "WHEN v.status = 2 AND v.expiration < CURDATE()  THEN 4 "
                       "WHEN v.status = 3 THEN 3 WHEN v.status = 4 THEN 4 END")
        conn.commit()
        return "Success Update Status"
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/coupon', methods=['GET'])
def coupon():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * from tbl_voucher')
        c_rows = cursor.fetchall()
        response = jsonify(c_rows)
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/status', methods=['GET', 'POST'])
def status():
    df = pd.DataFrame()
    try:
        coupon = request.form['coupon']
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "SELECT v.coupon, v.expiration, s.status from tbl_voucher v inner join tbl_status s on v.status = s.id where coupon =%s limit 1",
            coupon)
        c_rows = cursor.fetchone()
        df = df.append(c_rows, ignore_index=True)
        return render_template('redeem.html', exp=str(df['expiration'][0]), status=str(df['status'][0]))
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/redeem', methods=['POST', 'PUT', 'GET'])
def redeem():
    df = pd.DataFrame()
    try:
        coupon = request.form['coupon']
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT coupon, status from tbl_voucher where coupon =%s limit 1", coupon)
        c_rows = cursor.fetchone()
        df = df.append(c_rows, ignore_index=True)
        if df['status'][0] == 2:
            cursor.execute("update tbl_voucher set status = 3 where coupon = %s", coupon)
            conn.commit()
            print(df)
            return render_template('result.html', hasil="Reedem Sukses!")
        elif df['status'][0] == 4:
            return render_template('result.html', hasil="Voucher is expired!")
        else:
            return render_template('result.html', hasil="Voucher is already redeemed!")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run()
