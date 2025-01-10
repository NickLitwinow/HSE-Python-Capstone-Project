def get_connection_uri(conn):
    """
    Создает валидный URI из параметров хука.

    Args:
        conn: Соединение, полученное из хука (например, PostgresHook или MySqlHook).

    Returns:
        str: Строка URI для подключения к системе управления базами данных (СУБД).
    """
    # Словарь для сопоставления типов соединений с префиксами JDBC
    conn_type_jdbc_mapping = {
        "postgres": "postgresql",  # PostgreSQL использует префикс 'postgresql'
        "mysql": "mysql"           # MySQL использует префикс 'mysql'
    }

    # Определение типа соединения на основе типа соединения из хука
    conn_type = conn_type_jdbc_mapping[conn.conn_type]

    # Извлечение информации о пользователе из соединения
    login = conn.login            # Имя пользователя для подключения
    password = conn.password      # Пароль для подключения

    # Извлечение информации о хосте и порте из соединения
    host = conn.host              # Адрес хоста СУБД
    port = conn.port              # Порт, на котором СУБД прослушивает подключения

    # Извлечение имени базы данных из соединения
    db = conn.schema              # Имя базы данных (schema) для подключения

    # Обработка дополнительных параметров из поля 'extra' соединения
    # 'extra_dejson' преобразует JSON-строку в словарь
    extras_list = [f"{k}={v}" for k, v in conn.extra_dejson.items()]
    # Преобразование списка дополнительных параметров в строку формата 'ключ=значение&ключ=значение'
    extras = f"&{'&'.join(extras_list)}" if extras_list else ''

    # Формирование окончательной строки URI для подключения
    # Формат: jdbc:<тип_субд>://<хост>:<порт>/<база_данных>?user=<пользователь>&password=<пароль>&<доп.параметры>
    return f"jdbc:{conn_type}://{host}:{port}/{db}?user={login}&password={password}{extras}"