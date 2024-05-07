# import json
from flask import Flask, jsonify, request
import pyodbc, requests

app = Flask(__name__)
# # Configuración de la conexión a la base de datos
# server = 'DESKTOP-RKAJ\\AJRP'
# database = 'munimaynas_sistemaconsulta'
# username = 'sa'
# password = 'Kurama69.'

# Configuración de la conexión a la base de datos PRUEBA
server = '192.168.100.33'
# database = 'BDSGTM01'
database = 'BDSGTM01'
username = 'ApiSGTM'
password = '29y^w!F^Z&30dp#'

@app.route('/getcontribydni', methods=['POST'])
def getcontribydni():
    try:
        conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        conn = pyodbc.connect(conn_str)

        data = request.json
        dni = data.get('dni')

        cursor = conn.cursor()
        query = f'''SELECT CodContribuyente, dbo.fn_NombreContribuyente(CodContribuyente) AS nombre,
        dbo.fn_GetDomicioContribuyente(CodContribuyente) AS Direccion FROM T100ContribDocumentos f
        WHERE NumDocumento = '{dni}' '''
        try:
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows:
                col_names = [column[0] for column in cursor.description]
                personas = []
                for row in rows:
                    persona = dict(zip(col_names, row))
                    personas.append(persona)

                return jsonify({'datos': personas}), 200
            else:
                return jsonify({'datos': "Por favor acérquese a la municipalidad para regularizar sus datos."}), 400
        except Exception as e:
            return jsonify({'message': 'Ocurrió un error en el servidor', 'error': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return jsonify({'message': 'Ocurrió un error en el servidor', 'error': str(e)}), 501


# Ruta para consultar los datos de la tabla "munimaynas_sistemaconsulta.contribuyente"
@app.route('/checkcontribuyente', methods=['POST'])
def check_contribuyente():
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)

    data = request.json
    contribuyente = data.get('contribuyente')
    dni = data.get('dni')
    
    # query = f"SELECT * FROM dbo.ContribuyenteLlevarGabriel WHERE CodContribuyente = '{contribuyente}' AND DNI = '{dni}'"
    # query = f"SELECT * FROM dbo.ContribuyenteLlevarGabriel WHERE CodContribuyente = '{contribuyente}'"
    query = f"select validar=count(a.CodContribuyente) From T100ContribDocumentos as a where a.CodContribuyente='{contribuyente}' and a.NumDocumento='{dni}'"

    cursor = conn.cursor()
    try:
        cursor.execute(query)
        row = cursor.fetchone()

        if row.validar > 0:
            return jsonify({'message': 'Contribuyente verificado'}), 200
        else:
            return jsonify({'message': 'No se encontraron coincidencias'}), 400
    except Exception as e:
        return jsonify({'message': 'Ocurrió un error en el servidor', 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/paydeudas', methods=['POST'])
def update_deuda():
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)

    data = request.json
    clavedeu = data.get('clavedeuda')
    cuota = data.get('cuota')
    year = data.get('year')
    
    query = f"SELECT validar=count(d.Clavedeu) FROM dbo.vT700DeudaDatos as d WHERE d.ClaveDeu = '{clavedeu}' AND d.Cuota = '{cuota}' AND d.AnoDeu = '{year}'"
    
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        row = cursor.fetchone()

        if row.validar > 0:
            update_query = f"UPDATE dbo.vT700DeudaDatos SET Estado = 'C' WHERE ClaveDeu = '{clavedeu}' AND Cuota = '{cuota}' AND AnoDeu = '{year}'"
            cursor.execute(update_query)
            conn.commit()
            return jsonify({'message': 'Se actualizó el registro correctamente'}), 200
        else:
            return jsonify({'message': "No se encontraron coincidencias con los datos proveídos"}), 400
    except Exception as e:
        # return jsonify({'message': 'No se pudo procesar la solicitud de actualización de registro', 'error': str(e)}), 500
        return jsonify({'message': 'No se pudo procesar la solicitud de actualización de registro'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/getcontribuyente', methods=['POST'])
def get_contribuyente(contribuyente):
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)

    query = f'''SELECT CodContribuyente AS codcontribuyente, dbo.fn_NombreContribuyente(CodContribuyente) AS nombre,
        dbo.fn_GetDomicioContribuyente(CodContribuyente) AS Direccion FROM T100ContribDocumentos f
        WHERE CodContribuyente = '{contribuyente}' '''
    # query = "EXEC ObtenerContribuyenteMunipay @CodContribuyente = ?"

    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()

        if len(rows) > 0:
            col_names = [column[0] for column in cursor.description]
            registro_contribuyente = [dict(zip(col_names, row)) for row in rows]
            return registro_contribuyente
        else:
            return jsonify({'message': 'No se encontraron coincidencias'}), 400
            # return None
    except Exception as e:
        return jsonify({'message': 'No se ha podido procesar la solicitud', 'error': str(e)}), 500
        # return None
    finally:
        cursor.close()
        conn.close()


@app.route('/getcontribuyenteapi', methods=['POST'])
def get_contribuyenteapi():
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)

    data = request.json
    contribuyente = data.get("contribuyente")

    query = f'''SELECT CodContribuyente AS codcontribuyente, dbo.fn_NombreContribuyente(CodContribuyente) AS nombre,
        dbo.fn_GetDomicioContribuyente(CodContribuyente) AS Direccion FROM T100ContribDocumentos f
        WHERE CodContribuyente = '{contribuyente}' '''
    # query = "EXEC ObtenerContribuyenteMunipay @CodContribuyente = ?"

    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()

        if len(rows) > 0:
            col_names = [column[0] for column in cursor.description]
            registro_contribuyente = [dict(zip(col_names, row)) for row in rows]
            return registro_contribuyente
        else:
            return jsonify({'message': 'No se encontraron coincidencias'}), 400
            # return None
    except Exception as e:
        return jsonify({'message': 'No se ha podido procesar la solicitud', 'error': str(e)}), 500
        # return None
    finally:
        cursor.close()
        conn.close()


@app.route('/getdeudas', methods=['POST'])
def get_deuda():
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)

    data = request.json
    contribuyente_request = data.get('contribuyente')

    contribuyente = get_contribuyente(contribuyente_request)

    cursor = conn.cursor()
    try:
        query = f"EXEC ObtenerDeudasContribuyente @CodContribuyente = ?"
        cursor.execute(query, contribuyente_request)
        result = cursor.fetchall()

        if len(result) > 0:
            col_names = [column[0] for column in cursor.description]
            deudas = [dict(zip(col_names, row)) for row in result]
            
            
            years = list(set([deuda['anodeu'] for deuda in deudas]))
            years.sort(reverse=True)

            tributos = sorted(list(set([deuda['nomtributo'] for deuda in deudas if deuda['nomtributo']])))

            context = {
                "contri": contribuyente,
                "years": years,
                "tributos": tributos,
            }
            return jsonify({'context': context}), 200
        else:
            context = {
                "contri": contribuyente,
                "years": [],
                "tributos": [],
            }
            message = "Este contribuyente no tiene deudas"
            return jsonify({'context': context, 'message': message}), 200
    except Exception as e:
        return jsonify({'message': 'Ocurrió un error en el servidor', 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/buscar', methods=['POST'])
def filter_deuda():
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)

    data = request.json
    contribuyente = data.get('contribuyente')
    cuota = data.get('cuota')
    year = data.get('year')
    tributo = data.get('tributo')
    coactiva = data.get('coactiva')


    cursor = conn.cursor()
    try:
        query = "EXEC ObtenerDeudasContribuyenteF @CodContribuyente = ?"
        params = [contribuyente]
     
        if cuota:
            query += ", @Cuota = ?"
            params.append(cuota)
        if year:
            query += ", @AnoDeu = ?"
            params.append(year)
        if tributo:
            query += ", @NomTributo = ?"
            params.append(tributo)
        if coactiva:
            query += ", @Coactiva = ?"
            params.append(coactiva)

        cursor.execute(query, params)
        result = cursor.fetchall()
        
        if len(result) > 0:
            col_names = [column[0] for column in cursor.description]
            deudas = [dict(zip(col_names, row)) for row in result]
            formatos(deudas)

            # context = {
            #     "deudas": deudas
            # }
            # Aquí puedes hacer algo con los registros encontrados, como construir una respuesta JSON
            # ...
            return jsonify({'deudas': deudas}), 200
        else:
            return jsonify({'context': {}}), 200
    except Exception as e:
        return jsonify({'message': 'Ocurrió un error en el servidor', 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/guardarpago', methods=['POST'])
def agregar_pago():
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)
    
    data = request.json
    transaccion_id = data['transaccion_id']
    clavedeu = data['clavedeu']
    montopagado = data['montopagado']
    divisa = data['divisa']
    anodeu = data['anodeu']
    cuota = data['cuota']
    nombtributo = data['nombtributo']
    canal = data['canal']
    order_id = data['order_id']
    tipo_transaccion = data['tipo_transaccion']
    metodo_pago = data['metodo_pago']
    fecha_creacion = data['fecha_creacion']
    fecha_operacion = data['fecha_operacion']
        
    cursor = conn.cursor()
    
    try:
        insert_query = f"INSERT INTO munipay_pagos (transaccion_id, clavedeu, divisa, tipo_transaccion, anodeu, cuota, nombtributo, order_id, montopagado, metodo_pago, canal, fecha_creacion, fecha_operacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(insert_query, transaccion_id, clavedeu, divisa, tipo_transaccion, anodeu, cuota, nombtributo, order_id, montopagado, metodo_pago, canal, fecha_creacion, fecha_operacion)
        conn.commit()
        
        update_query = f"EXEC mpay_update_prepago @p_canalpago=?, @p_clavedeu=?"
        cursor.execute(update_query, canal, clavedeu)
        conn.commit()
        return jsonify({'message': 'Se procedió correctamente'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'message': 'Ocurrió un error en el servidor 2', 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/guardarprepago', methods=['POST'])
def agregar_prepago():
    try:
        conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        conn = pyodbc.connect(conn_str)

        data = request.json
        clavedeu = data['clavedeu']
        insoluto = data['insoluto']
        interes = data['interes']
        gastos = data['gastos']

        cursor = conn.cursor()
        check_query = f"SELECT validar=count(p.clavedeu) FROM munipay_pre_pagos as p WHERE p.clavedeu = '{clavedeu}'"
        try:
            cursor.execute(check_query)
            row = cursor.fetchone()
            
            if(row.validar > 0):
                update_query = f"UPDATE munipay_pre_pagos SET interes = ?, gastos = ? WHERE clavedeu = ?"
                cursor.execute(update_query, interes, gastos, clavedeu)
                conn.commit()

                return jsonify({'message': 'Se encontró la orden de pago registrada previamente'}), 200
            else:
                insert_query = f"INSERT INTO dbo.munipay_pre_pagos (clavedeu,interes,gastos,insoluto) VALUES (?, ?, ?, ?)"
                cursor.execute(insert_query,clavedeu,interes,gastos,insoluto)
                conn.commit()
                
                return jsonify({'message': "Se guardó correctamente la orden de pago"}), 200  
        except Exception as e:
            return jsonify({'message': 'Ocurrió un error en el servidor', 'error': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return jsonify({'message': 'Ocurrió un error en el servidor', 'error': str(e)}), 500

########################### ACTUALIZAR PAGO ################################
# ACTUALIZAR PAGO - API DE PRUEBA ############################################
@app.route('/updateprepago', methods=['POST'])
def update_prepagoapi():
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)

    data = request.json
    clavedeu = data.get('clavedeu')
    canal = data.get('canal')

    try:
        cursor = conn.cursor()
        check_query = f"EXEC mpay_update_prepago @p_canalpago=?, @p_clavedeu=?"
        
        try:
            cursor.execute(check_query, canal, clavedeu)
            conn.commit()
        except Exception as e:
            return jsonify({'message': 'Ocurrió un error en el servidor', 'error': str(e)}), 500
        finally:
            cursor.close()
    except Exception as e:
        return jsonify({'message': 'Ocurrió un error en el servidor', 'error': str(e)}), 500



@app.route('/reportedeuda', methods=['POST'])
def reporte_deudas():
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)
    data = request.json
    # cod_contribuyente = data['cod_contribuyente']
    # ano_deu = data['ano_deu']
    # cuota1 = data['cuota1']
    # cuota2 = data['cuota2']
    cod_contribuyente = data.get('cod_contribuyente')
    ano_deu = data.get('ano_deu')
    cuota1 = data.get('cuota1')
    cuota2 = data.get('cuota2')
    cursor = conn.cursor()

    try:

        query = "EXEC ObtenerReporteDeudasFiltro @codContribuyente=?"
        params = [cod_contribuyente]

        if ano_deu:
            query += ", @anoDeu=?"
            params.append(ano_deu)

        if cuota1:
            query += ", @cuota1=?"
            params.append(cuota1)

        if cuota2:
            query += ", @cuota2=?"
            params.append(cuota2)

        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        result = [dict(zip(columns, row)) for row in rows]    

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

def formatos(deudas):
    for deuda in deudas:
        #deuda['total'] = round(float(deuda['total']), 2)
        deuda['total'] = "%.2f" % float(deuda['total'])
        deuda['gastos'] = "%.2f" % float(deuda['gastos'])
        deuda['insoluto'] = "%.2f" % float(deuda['insoluto'])
        deuda['interes'] = "%.2f" % float(deuda['interes'])

@app.route('/test', methods=['POST'])
def getTestValue():   
    # conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    # conn = pyodbc.connect(conn_str)

    # data = request.json
    # canal = data.get("canal")
    # clavedeu = data.get("clavedeu")

    # update_prepago(clavedeu, canal, conn)

    # codigo = data.get('contribuyente')
    # print(codigo)
    # response = get_contribuyente(codigo)

    return "ejecutado"




if __name__ == '__main__':
    app.run(debug=False, port=4343)
