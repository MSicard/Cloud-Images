import dynamostorage as Dynamo
import keyvalue.parsetriples as ParseTripe
import keyvalue.stemmer as Stemmer

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

def saveTags(readSize, filename, imagesList):
    parse = ParseTripe.ParseTriples(filename)
    lastSort = ' '
    i = 0
    triple = parse.getNext()
    while i < readSize and triple != None:
        sort = triple[0].split('/')
        sort = sort[-1]
        if sort != lastSort : 
            if  triple[0] in imagesList:
                labels = Stemmer.stem(triple[2]).split(' ')
                for label in labels:
                    dynamo_labels.putItem({
                        'keyword': label,
                        'inx': int(sort.replace('Q', '')),
                        'value': triple[0]
                    })
                i += 1 
                print(Stemmer.stem(triple[2]) + sort.replace('Q', '') + triple[0])
            lastSort = sort
        triple = parse.getNext()

# Make connections to Dynamo
dynamo_labels = Dynamo.dynamoStorage('Labels', sortKey=True)
dynamo_images = Dynamo.dynamoStorage('Images')

## codigo
categories = saveImages(5, './images.ttl')
saveTags(5, './labels_en.ttl', categories)

