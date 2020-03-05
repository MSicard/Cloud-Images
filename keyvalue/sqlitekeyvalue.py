import sqlite3

try:
    basestring
except NameError:
    basestring = str

class SqliteKeyValue():
    
    def __init__(self,dbFile,tableName="KeyValue",sortKey=False):
        super().__init__()
        print("Archivo de BaseDeDatos: "+dbFile)
        self._table = tableName
        self._con = sqlite3.connect(dbFile,timeout=10)
        self._cur = self._con.cursor()
        self._cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?', (self._table,))
        if self._cur.fetchone() is None:
            if(not sortKey):
                self._cur.execute('CREATE TABLE {0} (skey TEXT PRIMARY KEY, value TEXT)'.format(self._table))
            else:
                self._cur.execute('CREATE TABLE {0} (skey TEXT, sort TEXT, value TEXT, PRIMARY KEY(skey,sort))'.format(self._table))

    def put(self,key,value):
        if not isinstance(key, basestring):
            raise TypeError('key must be of str type!')
        self._cur.execute('INSERT OR REPLACE INTO {0} VALUES (?,?)'.format(self._table), (key, value))
    
    def putSort(self,key,sort,value):
        if not isinstance(key, basestring) or not isinstance(sort, basestring):
            raise TypeError('keys must be of str type!')
        self._cur.execute('INSERT OR REPLACE INTO {0} VALUES (?,?,?)'.format(self._table), (key, sort, value))

    def get(self,key):
        if not isinstance(key, basestring):
            raise TypeError('key must be of str type!')
        self._cur.execute('SELECT value FROM  {0} WHERE skey=?'.format(self._table), (key,))
        row = self._cur.fetchone()
        if row is None:
           return None
        return row[0]

    def getSort(self,key):
        if not isinstance(key, basestring):
            raise TypeError('key must be of str type!')
        self._cur.execute('SELECT value FROM  {0} WHERE skey=?'.format(self._table), (key,))
        rows = self._cur.fetchmany(5)
        if rows is None:
           return None
        return rows

    def getAll(self):
        self._cur.execute('SELECT * FROM  {0} '.format(self._table))
        rows = self._cur.fetchall()
        if rows is None:
           return None
        return rows

    def close(self):
        self._con.commit()
        self._con.close()
    
    