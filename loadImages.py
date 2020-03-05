import keyvalue.sqlitekeyvalue as KeyValue
import keyvalue.parsetriples as ParseTripe
import keyvalue.stemmer as Stemmer

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
        
# Make connections to KeyValue
kv_labels = KeyValue.SqliteKeyValue("sqlite_labels.db","labels",sortKey=True)
kv_images = KeyValue.SqliteKeyValue("sqlite_images.db","images")

# Process Logic.
# Open all files
saveImages(200, './images.ttl')
saveTags(200, './labels_en.ttl')



# Close KeyValues Storages
kv_labels.close()
kv_images.close()








