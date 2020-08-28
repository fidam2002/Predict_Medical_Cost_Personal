from flask import Flask, render_template, request
import plotly
import plotly.graph_objs as go
import pandas as pd
import json
from sqlalchemy import create_engine

import joblib

app = Flask(__name__)

###################
## CATEGORY PLOT ##
###################

## IMPORT DATA USING pd.read_csv
insurance = pd.read_csv('./static/insurance without region.csv')

# IMPORT DATA USING pd.read_sql
sqlengine = create_engine('mysql+pymysql://fidam:mamaOzy1966@127.0.0.1/final_project', pool_recycle=3605)
dbConnection = sqlengine.connect()
engine = sqlengine.raw_connection()
cursor = engine.cursor()
insurance = pd.read_sql("select * from insurance", dbConnection)

# category plot function
def category_plot(
    cat_plot = 'histplot',
    cat_x = 'sex', cat_y = 'charges',
    estimator = 'count', hue = 'smoker'):

    # generate dataframe insurance.csv
    insurance = pd.read_csv('./static/insurance without region.csv')



    # jika menu yang dipilih adalah histogram
    if cat_plot == 'histplot':
        # siapkan list kosong untuk menampung konfigurasi hist
        data = []
        # generate config histogram dengan mengatur sumbu x dan sumbu y
        for val in insurance[hue].unique():
            hist = go.Histogram(
                x=insurance[insurance[hue]==val][cat_x],
                y=insurance[insurance[hue]==val][cat_y],
                histfunc=estimator,
                name=str(val)
                )
            #masukkan ke dalam array
            data.append(hist)
        #tentukan title dari plot yang akan ditampilkan
        title='Histogram'
    elif cat_plot == 'boxplot':
        data = []

        for val in insurance[hue].unique():
            box = go.Box(
                x=insurance[insurance[hue] == val][cat_x], #series
                y=insurance[insurance[hue] == val][cat_y],
                name=str(val)
            )
            data.append(box)
        title='Box'
    # menyiapkan config layout tempat plot akan ditampilkan
    # menentukan nama sumbu x dan sumbu y
    if cat_plot == 'histplot':
        layout = go.Layout(
            title=title,
            xaxis=dict(title=cat_x),
            yaxis=dict(title='frequency'),
            # boxmode group digunakan berfungsi untuk mengelompokkan box berdasarkan hue
            boxmode = 'group'
        )
    else:
        layout = go.Layout(
            title=title,
            xaxis=dict(title=cat_x),
            yaxis=dict(title=cat_y),
            # boxmode group digunakan berfungsi untuk mengelompokkan box berdasarkan hue
            boxmode = 'group'
        )
    #simpan config plot dan layout pada dictionary
    result = {'data': data, 'layout': layout}

    #json.dumps akan mengenerate plot dan menyimpan hasilnya pada graphjson
    graphJSON = json.dumps(result, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

# akses halaman menuju route '/' untuk men-test
# apakah API sudah running atau belum
@app.route('/')
def index():
    plot = category_plot()
    # dropdown menu
    # kita lihat pada halaman dashboard terdapat menu dropdown
    # terdapat lima menu dropdown, sehingga kita mengirimkan kelima variable di bawah ini
    # kita mengirimnya dalam bentuk list agar mudah mengolahnya di halaman html menggunakan looping
    list_plot = [('histplot', 'Histogram'), ('boxplot', 'Box')]
    list_x = [('sex', 'Sex'), ('smoker', 'Smoker')]
    list_y = [('age', 'Age'), ('bmi', 'BMI'), ('children', 'Children'), ('charges', 'Charges')]
    list_est = [('count', 'Count'), ('avg', 'Average'), ('max', 'Max'), ('min', 'Min')]
    list_hue = [('sex', 'Sex'), ('smoker', 'Smoker')]

    return render_template(
        # file yang akan menjadi response dari API
        'category.html',
        # plot yang akan ditampilkan
        plot=plot,
        # menu yang akan tampil di dropdown 'Jenis Plot'
        focus_plot='histplot',
        # menu yang akan muncul di dropdown 'sumbu X'
        focus_x='sex',

        # untuk sumbu Y tidak ada, nantinya menu dropdown Y akan di disable
        # karena pada histogram, sumbu Y akan menunjukkan kuantitas data

        # menu yang akan muncul di dropdown 'Estimator'
        focus_estimator='count',
        # menu yang akan tampil di dropdown 'Hue'
        focus_hue='smoker',
        # list yang akan digunakan looping untuk membuat dropdown 'Jenis Plot'
        drop_plot= list_plot,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu X'
        drop_x= list_x,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu Y'
        drop_y= list_y,
        # list yang akan digunakan looping untuk membuat dropdown 'Estimator'
        drop_estimator= list_est,
        # list yang akan digunakan looping untuk membuat dropdown 'Hue'
        drop_hue= list_hue)

# ada dua kondisi di mana kita akan melakukan request terhadap route ini
# pertama saat klik menu tab (Histogram & Box)
# kedua saat mengirim form (saat merubah salah satu dropdown) 
@app.route('/cat_fn/<nav>')
def cat_fn(nav):

    # saat klik menu navigasi
    if nav == 'True':
        cat_plot = 'histplot'
        cat_x = 'sex'
        cat_y = 'charges'
        estimator = 'count'
        hue = 'smoker'
    
    # saat memilih value dari form
    else:
        cat_plot = request.args.get('cat_plot')
        cat_x = request.args.get('cat_x')
        cat_y = request.args.get('cat_y')
        estimator = request.args.get('estimator')
        hue = request.args.get('hue')

    # Dari boxplot ke histogram akan None
    if estimator == None:
        estimator = 'count'
    
    # Saat estimator == 'count', dropdown menu sumbu Y menjadi disabled dan memberikan nilai None
    if cat_y == None:
        cat_y = 'charges'

    # Dropdown menu
    list_plot = [('histplot', 'Histogram'), ('boxplot', 'Box')]
    list_x = [('sex', 'Sex'), ('smoker', 'Smoker')]
    list_y = [('age', 'Age'), ('bmi', 'BMI'), ('children', 'Children'), ('charges', 'Charges')]
    list_est = [('count', 'Count'), ('avg', 'Average'), ('max', 'Max'), ('min', 'Min')]
    list_hue = [('sex', 'Sex'), ('smoker', 'Smoker')]

    plot = category_plot(cat_plot, cat_x, cat_y, estimator, hue)
    return render_template(
        # file yang akan menjadi response dari API
        'category.html',
        # plot yang akan ditampilkan
        plot=plot,
        # menu yang akan tampil di dropdown 'Jenis Plot'
        focus_plot=cat_plot,
        # menu yang akan muncul di dropdown 'sumbu X'
        focus_x=cat_x,
        focus_y=cat_y,

        # menu yang akan muncul di dropdown 'Estimator'
        focus_estimator=estimator,
        # menu yang akan tampil di dropdown 'Hue'
        focus_hue=hue,
        # list yang akan digunakan looping untuk membuat dropdown 'Jenis Plot'
        drop_plot= list_plot,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu X'
        drop_x= list_x,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu Y'
        drop_y= list_y,
        # list yang akan digunakan looping untuk membuat dropdown 'Estimator'
        drop_estimator= list_est,
        # list yang akan digunakan looping untuk membuat dropdown 'Hue'
        drop_hue= list_hue
    )

##################
## SCATTER PLOT ##
##################

# scatter plot function
def scatter_plot(cat_x, cat_y, hue):


    data = []

    for val in insurance[hue].unique():
        scatt = go.Scatter(
            x = insurance[insurance[hue] == val][cat_x],
            y = insurance[insurance[hue] == val][cat_y],
            mode = 'markers',
            name = str(val)
        )
        data.append(scatt)

    layout = go.Layout(
        title= 'Scatter',
        title_x= 0.5,
        xaxis=dict(title=cat_x),
        yaxis=dict(title=cat_y)
    )

    result = {"data": data, "layout": layout}

    graphJSON = json.dumps(result,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/scatt_fn')
def scatt_fn():
    cat_x = request.args.get('cat_x')
    cat_y = request.args.get('cat_y')
    hue = request.args.get('hue')

    # WAJIB! default value ketika scatter pertama kali dipanggil
    if cat_x == None and cat_y == None and hue == None:
        cat_x = 'charges'
        cat_y = 'age'
        hue = 'smoker'

    # Dropdown menu
    list_x = [('age', 'Age'), ('bmi', 'BMI'), ('children', 'Children'), ('charges', 'Charges')]
    list_y = [('age', 'Age'), ('bmi', 'BMI'), ('children', 'Children'), ('charges', 'Charges')]
    list_hue = [('sex', 'Sex'), ('smoker', 'Smoker')]

    plot = scatter_plot(cat_x, cat_y, hue)

    return render_template(
        'scatter.html',
        plot=plot,
        focus_x=cat_x,
        focus_y=cat_y,
        focus_hue=hue,
        drop_x= list_x,
        drop_y= list_y,
        drop_hue= list_hue
    )

##############
## PIE PLOT ##
##############

def pie_plot(hue = 'smoker'):
    


    vcounts = insurance[hue].value_counts()

    labels = []
    values = []

    for item in vcounts.iteritems():
        labels.append(item[0])
        values.append(item[1])
    
    data = [
        go.Pie(
            labels=labels,
            values=values
        )
    ]

    layout = go.Layout(title='Pie', title_x= 0.48)

    result = {'data': data, 'layout': layout}

    graphJSON = json.dumps(result,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/pie_fn')
def pie_fn():
    hue = request.args.get('hue')

    if hue == None:
        hue = 'smoker'

    list_hue = [('sex', 'Sex'), ('smoker', 'Smoker')]

    plot = pie_plot(hue)
    return render_template('pie.html', plot=plot, focus_hue=hue, drop_hue= list_hue)

###############
## UPDATE DB ##
###############

@app.route('/db_fn')
def db_fn():
    sqlengine = create_engine('mysql+pymysql://fidam:mamaOzy1966@127.0.0.1/final_project', pool_recycle=3605)
    engine = sqlengine.raw_connection()
    cursor = engine.cursor()
    cursor.execute("SELECT * FROM insurance")
    data = cursor.fetchall()
    return render_template('update.html', data=data)

@app.route('/update_fn', methods=['POST', 'GET'])
def update_fn():

    if request.method == 'POST':
        input = request.form
        
        age = abs(int(input["age"]))

        sex = ''
        if input['sex'] == 'male':
            sex = 'Male'
        else:
            sex = 'Female'

        height = abs(float(input["height"]))
        weight = abs(float(input["weight"]))
        bmi = round(float(weight/((height/100)**2)),2)
        children = abs(int(input['children']))

        smoker = ''
        if input['smoker'] == 'Yes':
            smoker = 'Yes'
        else:
            smoker = 'No'

        charges = abs(float(input['charges']))


        ## Memasukkan data ke Tabel SQL
        data = { "age" : [age], "sex" : [sex], "bmi" : [bmi], "children" : [children], "smoker" : [smoker], 
                 "charges" : [charges]
               }

        new_df = pd.DataFrame.from_dict(data)

        new_df.to_sql('insurance', con=dbConnection, if_exists='append', index=False)

        return render_template('success.html',
            age=abs(int(input['age'])),
            sex=input['sex'],
            height = abs(float(input["height"])),
            weight = abs(float(input["weight"])),
            bmi = round(float(weight/((height/100)**2)),2),
            children=abs(int(input['children'])),
            smoker=input['smoker'],
            charges=abs(float(input['charges'])),
            )
            


@app.route('/pred_lr')
def pred_lr():
    sqlengine = create_engine('mysql+pymysql://fidam:mamaOzy1966@127.0.0.1/final_project', pool_recycle=3605)
    engine = sqlengine.raw_connection()
    cursor = engine.cursor()
    cursor.execute("SELECT * FROM insurance")
    data = cursor.fetchall()
    return render_template('predict.html', data=data)

@app.route('/pred_result', methods=['POST', 'GET'])
def pred_result():

    if request.method == 'POST':
    ## Untuk Predict
        input = request.form
        
        age = abs(int(input["age"]))

        if input["sex"] == "Male":
            sex = 1
        else:
            sex = 0

        height = abs(float(input["height"]))
        weight = abs(float(input["weight"]))
        bmi = round(float(weight/((height/100)**2)),2)
        children = abs(int(input['children']))

        if input["smoker"] == "Yes":
            smoker = 1
        else:
            smoker = 0

        pred = model.predict([[age, sex, bmi, children, smoker]])[0].round(2)

        ## Untuk Isi Data
        sex_dt = ''
        if input['sex'] == 'male':
            sex_dt = 'Male'
        else:
            sex_dt = 'Female'

        smoker_dt = ''
        if input['smoker'] == 'Yes':
            smoker_dt = 'Yes'
        else:
            smoker_dt = 'No'



        return render_template('result.html',
            age=abs(int(input['age'])),
            sex=input['sex'],
            height = abs(float(input["height"])),
            weight = abs(float(input["weight"])),
            bmi = round(float(weight/((height/100)**2)),2),
            children=abs(int(input['children'])),
            smoker=input['smoker'],
            insurance_pred = pred
            )

@app.route("/visualization", methods = ["POST", "GET"])
def visualization():

    return render_template("visualization.html")

if __name__ == '__main__':
    ## Me-Load data dari Database
    sqlengine = create_engine('mysql+pymysql://fidam:mamaOzy1966@127.0.0.1/final_project', pool_recycle=3605)
    dbConnection = sqlengine.connect()
    engine = sqlengine.raw_connection()
    cursor = engine.cursor()
    insurance = pd.read_sql("select * from insurance", dbConnection)
    ## Load Model
    model = joblib.load('ModelJoblib')
    app.run(debug=True, port=5000)