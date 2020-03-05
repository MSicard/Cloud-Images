import keyvalue.sqlitekeyvalue as KeyValue
import keyvalue.parsetriples as ParseTripe
import keyvalue.stemmer as Stemmer
import sys

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

# Make connections to KeyValue
kv_labels = KeyValue.SqliteKeyValue("sqlite_labels.db","labels",sortKey=True)
kv_images = KeyValue.SqliteKeyValue("sqlite_images.db","images")

# Process Logic.
argv = sys.argv
argv.remove('queryImages.py')
getImages(argv)

# Close KeyValues Storages
kv_labels.close()
kv_images.close()







