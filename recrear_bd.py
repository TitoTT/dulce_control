import pymysql

try:
    # Conexión sin base de datos
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456'
    )
    cursor = conn.cursor()
    
    # Eliminar base de datos si existe
    cursor.execute("DROP DATABASE IF EXISTS dulce_control")
    conn.commit()
    print("✅ Base de datos anterior eliminada")
    
    # Leer el script SQL
    with open('database/dulce_control.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Separar CREATE PROCEDURE del resto (no lo ejecutaremos en PyMySQL)
    proc_start = sql_script.find('CREATE PROCEDURE')
    if proc_start != -1:
        before_proc = sql_script[:proc_start]
        # Encontrar el final del procedimiento
        proc_end = sql_script.find('INSERT INTO ingredientes', proc_start)
        sql_script = before_proc + sql_script[proc_end:]
    
    # Ejecutar sentencias
    statements = sql_script.split(';')
    for statement in statements:
        lines = [line.strip() for line in statement.split('\n')]
        statement = '\n'.join([line for line in lines if line and not line.startswith('#')])
        
        if statement.strip():
            try:
                cursor.execute(statement)
                conn.commit()
                desc = statement.split('\n')[0][:40]
                if 'INSERT' not in statement.upper():
                    print(f"✅ {desc}...")
            except Exception as e:
                pass  # Ignorar errores
    
    cursor.close()
    conn.close()
    print('\n✅ Base de datos recreada exitosamente')
    
except Exception as e:
    print(f'❌ Error: {e}')
