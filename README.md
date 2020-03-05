# Cloud-Images
Practica 1 de Cloud

## Parte 1:
La primera parte consiste en agregar imáges y tags a la base de datos de SQL. Las modificaciones que se hicieron para desarrollarlo fueron los siguientes:

### sqlitekeyvalue.py

En este archivo fue necesario incluir una función que nos permitiera obtener más de un valor. Esta función se creó porque tenemos valores donde la clave primeria son dos valores. Tenemos el partition key que representa la palabra a ser buscada, y el sort key que tiene una categoría con el formato `Q`+ {Number}.

En otras palabras, podríamos tener en la base de datos algo así:

| label     | sort | value             |
|---------|------|-------------------|
| america | 18   | category_america       |
| america | 19   | category_north_america |
| golf    | 21   | category_golf          |

Se puede notar que tenemos dos valores para el tag de américa. Con la función obtendríamos ambos valores. Se limitó el número de valores recibidos a 5, pero este valor puede ser modificado. 

```python
def getSort(self,key):
        if not isinstance(key, basestring):
            raise TypeError('key must be of str type!')
        self._cur.execute('SELECT value FROM  {0} WHERE skey=?'.format(self._table), (key,))
        rows = self._cur.fetchmany(5)
        if rows is None:
           return None
        return rows
```

### loadImages.py

Este archivo funciona para insertar datos en la base de datos de sql. Para esto se crearon dos funciones, ya que las tablas son diferentes al igual que los valores.

#### saveImages

saveImages guarda la url de las imágenes y su respectiva categoría. Esta función va leyendo el archivo ttl hasta que sucedan dos cosas; la primera es que llegue al límite de valores que se desean insertar, la segunda es que ya no encuentre más datos en el ttl.

Cada vez que se lee un `triple`se toma la categoría y se compara con la última categoría agregada para no almacenar la misma. Esto fue necesario porque había categorías que tenían múltiples urls. Si la categoría es nueva, se agrega a la base de datos y se guarda esa categoría como la última almacenada. Este ciclo continua hasta terminar con alguna de las dos condiciones mencionadas. 

```python
def saveImages(readSize, filename):
    parse = ParseTripe.ParseTriples(filename)
    i = 0
    lastCategory = ' '
    triple = parse.getNext()
    while i < readSize and triple != None:
        category = triple[0].split('/')
        category = category[-1]
        if category != lastCategory : 
            kv_images.put(triple[0], triple[2]) 
            lastCategory = category
            i += 1
        triple = parse.getNext()
```
#### saveTags
Esta función almacena las palabras con la respectiva categoría. Consiste en un ciclo donde si el valor de datos ingresados es mayor a lo que se pide en la función o si ya no se encuentra más datos en el ttl, termina. Al igual que saveImages, revisa que el último valor del sort no sea el mismo que el actual, se hace para evitar que las palabras con la misma categoría que tengan múltiples imágenes se agreguen. Al encontrar un nuevo sort se toma la palabra y se hace un stemmer. También fue necesario separar la palabra por espacios, y por cada una de ellas se guarda en la base de datos con el mismo valor de la categoría. Antes de almacenar un valor, fue necesario hacer una búsqueda de la categoría dentro de la tabla de images, y con esto impedir que se agregara información que no tiene una categoría con url. 

```python
def saveTags(readSize, filename):
    parse = ParseTripe.ParseTriples(filename)
    lastSort = ' '
    i = 0
    triple = parse.getNext()
    while i < readSize and triple != None:
        sort = triple[0].split('/')
        sort = sort[-1]
        if sort != lastSort : 
            if kv_images.get(triple[0]) != None :
                labels = Stemmer.stem(triple[2]).split(' ')
                for label in labels:
                    kv_labels.putSort(label, sort, triple[0])
                    print(label + " - " + sort + ": " + triple[0])
                i += 1 
            lastSort = sort
        triple = parse.getNext()
```
### queryImages.py
Este documento nos ayuda a obtener los valores de la url de una imagen a través de palabras expuestas en la línea de comandos. Se tiene una función donde por cada argumento de la línea de comandos busca en la tabla de labels la palabra, y por cada una de las respuestas, busca la imagen de la categoría.

```python
def getImages(argv):
    for x in argv:
        categories = kv_labels.getSort(Stemmer.stem(x))
        print(categories)
        if (categories != None):
            for category in categories:
                url = kv_images.get(category[0])
                print(str(x) + ' Category: ' , category[0])
                if (url != None):
                    print('URL: ', url)
                else:
                    print('Not Found')
```

## Parte 2:

La segunda parte consiste en usar DynamoDb de AWS. Para esto fue necesario crear tres archivos principales que coinciden con las mismas características que los de sql. Se tiene el `dynamostorage.py`que es la similitud de `sqlitekeyvalue.py`donde se tiene un objeto que representa la tabla y que interactua con ella. Otro documento es para hacer la carga de datos `loadDynamo.py`y otro para obtener los datos `queryDynamo.py`.

### dynamostorage.py

Este documento usa el sdk de python de AWS. Cuenta con una función de inicialización, donde, se revisa que la tabla pedida exista, y en caso de que no, la crea. Para esto fue necesario hacer dos funciones, una para la creación de tablas con solo un partition key y otra para las tablas que cuenten con partition key y sort key.

También se crearon funciones para agregar los datos y obtenerlos. Para esto se usaron las funciones de `putItem`y `getItem`de DynamoDb. Se agregró una función de `queryItem`para usar el query que nos presenta DynamoDb. Ésta función fue utilizada sobre todo para obtener los datos de la tabla de labels.

### loadDynamo.py

Al igual que `loadImages.py`este documento almacena información, pero en este caso será en DynamoDb. Utiliza dos funciones, donde cada una de ellas almacena dependiendo de la tabla.

#### saveImages

Guarda las imágenes de la misma forma que se hace en `loadImages.py`. La diferencia radica en que se almacena en un diccionario de datos cada uno de estas. Este es para ser usada en el futuro y regresa esta lista.
```python
def saveImages(readSize, filename):
    parse = ParseTripe.ParseTriples(filename)
    i = 0
    lastCategory = ' '
    imagesList = []
    categoriesList = []
    triple = parse.getNext()

    while i < readSize and triple != None:
        category = triple[0].split('/')
        category = category[-1]

        if category != lastCategory : 
            imagesList.append(
              {
                "keyword": triple[0], 
                "value": triple[2]
            })
            categoriesList.append(triple[0])
            lastCategory = category
            i += 1
        triple = parse.getNext()
    
    dynamo_images.batchWriteItem(imagesList) 
    return categoriesList
```
#### saveTags

Usa la misma lógica que en `loadImages.py`, la diferencia radica en que antes de almacenar revisa en una lista que pide si existe la imagen. Esta es la misma lista que regresa la función de saveImages. Se creó de está forma para verificar que efectivamente existe en Images pero sin usar los recursos de DynamoDb y así ahorrar peticiones. 

```python
def saveTags(readSize, filename):
    parse = ParseTripe.ParseTriples(filename)
    lastSort = ' '
    i = 0
    triple = parse.getNext()
    while i < readSize and triple != None:
        sort = triple[0].split('/')
        sort = sort[-1]
        if sort != lastSort : 
            if kv_images.get(triple[0]) != None :
                labels = Stemmer.stem(triple[2]).split(' ')
                for label in labels:
                    kv_labels.putSort(label, sort, triple[0])
                    print(label + " - " + sort + ": " + triple[0])
                i += 1 
            lastSort = sort
        triple = parse.getNext()
```

### queryDynamo.py
Usa la misma lógica que queryImages.py. La diferencia radica en que utiliza `dynamostorage`para hacer las peticiones. Como el otro caso, revisa los argumentos introducidos en la línea de comando y hace una búsqueda del label con la función de query. Cuando encuentra más de un resultado, busca cada una de las urls de las imágenes que corresponde. 

```python
def getImages(argv):
    for x in argv:
        response = dynamo_labels.queryItem(Stemmer.stem(x))
        if ('Items' in response):
            items = response['Items']
            for item in items:
                url = dynamo_images.getItem(
                    { 
                        'keyword': item['value'] 
                    })
                print(str(x) + ' Category: ' , item['value'])
                if ('Item' in url):
                    print('URL: ', url['Item']['value'])
                else:
                    print('Not Found')
```
